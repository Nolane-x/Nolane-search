import { isSafePublicUrl } from "./security";
import type { Env } from "./types";

export type AiTask = "chat" | "fast" | "reasoning" | "coding" | "creative" | "translation" | "research" | "summary" | "classification";
export type AiProtocol = "openai-compatible" | "anthropic-messages" | "gemini-interactions";
export type AiStrategy = "balanced" | "priority" | "cheapest";
export interface AiToolCall {
  id: string;
  type: "function";
  function: { name: string; arguments: string };
}
export interface AiFunctionTool {
  type: "function";
  function: { name: string; description: string; parameters: Record<string, unknown>; strict?: boolean };
}
export interface AiMessage {
  role: "system" | "user" | "assistant" | "tool";
  content: string;
  tool_calls?: AiToolCall[];
  tool_call_id?: string;
  name?: string;
}
export interface AiCompletionInput {
  task: AiTask;
  messages: AiMessage[];
  temperature?: number;
  maxTokens?: number;
  tools?: AiFunctionTool[];
  toolChoice?: "auto" | "none" | "required";
}
export interface AiCompletionResult {
  text: string; providerId: string; protocol: AiProtocol; model: string; latencyMs: number;
  inputTokens?: number; outputTokens?: number; estimatedCostUsd?: number;
  toolCalls?: AiToolCall[];
}
interface AiModelConfig {
  id: string; tasks: AiTask[] | "all"; priority: number;
  inputCostUsdPerMillion?: number; outputCostUsdPerMillion?: number; maxOutputTokens?: number;
}
interface AiProviderConfig {
  id: string; protocol: AiProtocol; baseUrl: string; apiKey: string; priority: number;
  timeoutMs: number; models: AiModelConfig[];
}
interface AiRouterConfig { strategy: AiStrategy; maxAttempts: number; providers: AiProviderConfig[]; invalidEntries: number; }
export interface AiRouterStatus {
  configured: boolean; strategy: AiStrategy; maxAttempts: number; providerKeys: number; models: number; invalidEntries: number;
  providers: Array<{ id: string; protocol: AiProtocol; models: Array<{ id: string; tasks: AiTask[] | "all" }> }>;
}

const VALID_TASKS = new Set<AiTask>(["chat","fast","reasoning","coding","creative","translation","research","summary","classification"]);
const VALID_PROTOCOLS = new Set<AiProtocol>(["openai-compatible","anthropic-messages","gemini-interactions"]);
let routeCursor = 0;
const routeCooldowns = new Map<string, number>();

function routeKey(candidate: Candidate): string {
  return candidate.provider.id + ":" + candidate.model.id;
}

function isRouteCoolingDown(candidate: Candidate, now = Date.now()): boolean {
  const key = routeKey(candidate);
  const until = routeCooldowns.get(key) || 0;
  if (until <= now) {
    routeCooldowns.delete(key);
    return false;
  }
  return true;
}

function markRouteCoolingDown(candidate: Candidate, error: unknown): void {
  const message = error instanceof Error ? error.message : "";
  const status = Number(message.match(/HTTP (\d{3})/)?.[1] || 0);
  const duration = status === 429 ? 60_000
    : status === 401 || status === 403 ? 5 * 60_000
    : status >= 500 ? 30_000
    : /timeout|abort/i.test(message) ? 15_000
    : 10_000;
  routeCooldowns.set(routeKey(candidate), Date.now() + duration);
  if (routeCooldowns.size > 256) {
    const now = Date.now();
    for (const [key, until] of routeCooldowns) if (until <= now) routeCooldowns.delete(key);
    while (routeCooldowns.size > 256) routeCooldowns.delete(routeCooldowns.keys().next().value as string);
  }
}

function numberInRange(value: unknown, fallback: number, min: number, max: number): number {
  return typeof value === "number" && Number.isFinite(value) ? Math.max(min, Math.min(max, value)) : fallback;
}

function parseModels(value: unknown): AiModelConfig[] {
  if (!Array.isArray(value)) return [];
  const output: AiModelConfig[] = [];
  for (const item of value.slice(0, 32)) {
    const raw = typeof item === "string" ? { id: item } : item;
    if (!raw || typeof raw !== "object") continue;
    const model = raw as Record<string, unknown>;
    const id = typeof model.id === "string" ? model.id.trim() : "";
    if (!/^[A-Za-z0-9._:/+-]{1,180}$/.test(id)) continue;
    const tasks = Array.isArray(model.tasks)
      ? [...new Set(model.tasks.filter((task): task is AiTask => typeof task === "string" && VALID_TASKS.has(task as AiTask)))]
      : [];
    output.push({
      id, tasks: tasks.length ? tasks : "all",
      priority: numberInRange(model.priority, 0, -1000, 1000),
      inputCostUsdPerMillion: typeof model.inputCostUsdPerMillion === "number" ? numberInRange(model.inputCostUsdPerMillion, 0, 0, 1_000_000) : undefined,
      outputCostUsdPerMillion: typeof model.outputCostUsdPerMillion === "number" ? numberInRange(model.outputCostUsdPerMillion, 0, 0, 1_000_000) : undefined,
      maxOutputTokens: typeof model.maxOutputTokens === "number" ? Math.round(numberInRange(model.maxOutputTokens, 2048, 1, 8192)) : undefined,
    });
  }
  return output;
}

function parseConfig(env: Env): AiRouterConfig {
  let strategy: AiStrategy = "balanced";
  let maxAttempts = 3;
  const providers: AiProviderConfig[] = [];
  let invalidEntries = 0;

  if (env.AI_ROUTER_CONFIG) {
    if (env.AI_ROUTER_CONFIG.length > 100_000) invalidEntries += 1;
    else try {
      const parsed = JSON.parse(env.AI_ROUTER_CONFIG) as Record<string, unknown>;
      if (parsed.strategy === "priority" || parsed.strategy === "cheapest" || parsed.strategy === "balanced") strategy = parsed.strategy;
      maxAttempts = Math.round(numberInRange(parsed.maxAttempts, 3, 1, 6));
      const list = Array.isArray(parsed.providers) ? parsed.providers : [];
      for (const raw of list.slice(0, 64)) {
        if (!raw || typeof raw !== "object") { invalidEntries += 1; continue; }
        const item = raw as Record<string, unknown>;
        const id = typeof item.id === "string" ? item.id.trim() : "";
        const protocol = item.protocol as AiProtocol;
        const apiKey = typeof item.apiKey === "string" ? item.apiKey.trim() : "";
        const defaultUrl = protocol === "anthropic-messages" ? "https://api.anthropic.com"
          : protocol === "gemini-interactions" ? "https://generativelanguage.googleapis.com/v1beta" : "";
        const baseUrl = typeof item.baseUrl === "string" ? item.baseUrl.trim() : defaultUrl;
        const safeUrl = baseUrl ? isSafePublicUrl(baseUrl) : null;
        const models = parseModels(item.models);
        if (!/^[A-Za-z0-9._-]{1,50}$/.test(id) || !VALID_PROTOCOLS.has(protocol) ||
            apiKey.length < 8 || apiKey.length > 4096 || !safeUrl || safeUrl.search || safeUrl.hash || !models.length) {
          invalidEntries += 1; continue;
        }
        providers.push({
          id, protocol, baseUrl: safeUrl.toString().replace(/\/+$/, ""), apiKey,
          priority: numberInRange(item.priority, 0, -1000, 1000),
          timeoutMs: Math.round(numberInRange(item.timeoutMs, 45_000, 5_000, 90_000)),
          models,
        });
      }
    } catch { invalidEntries += 1; }
  }

  // Legacy OpenRouter credentials remain available as a final fallback.
  if (env.OPENROUTER_API_KEY) {
    const models = [...new Set([env.OPENROUTER_MODELS || "", env.OPENROUTER_MODEL || ""]
      .join("\n").split(/[\s,;]+/).map(x => x.trim()).filter(x => /^[A-Za-z0-9._:/+-]{1,180}$/.test(x)))].slice(0, 8)
      .map(id => ({ id, tasks: "all" as const, priority: -100 }));
    if (models.length) providers.push({
      id: "openrouter-legacy", protocol: "openai-compatible", baseUrl: "https://openrouter.ai/api/v1",
      apiKey: env.OPENROUTER_API_KEY, priority: -100, timeoutMs: 45_000, models,
    });
  }
  return { strategy, maxAttempts, providers, invalidEntries };
}

interface Candidate { provider: AiProviderConfig; model: AiModelConfig; priority: number; cost: number; }
function candidatesFor(config: AiRouterConfig, task: AiTask): Candidate[] {
  const candidates: Candidate[] = [];
  for (const provider of config.providers) for (const model of provider.models) {
    if (model.tasks !== "all" && !model.tasks.includes(task)) continue;
    const priced = model.inputCostUsdPerMillion !== undefined && model.outputCostUsdPerMillion !== undefined;
    candidates.push({
      provider, model, priority: provider.priority + model.priority,
      cost: priced ? (model.inputCostUsdPerMillion || 0) + (model.outputCostUsdPerMillion || 0) * 2 : Number.POSITIVE_INFINITY,
    });
  }
  if (config.strategy === "cheapest") candidates.sort((a,b) => a.cost - b.cost || b.priority - a.priority);
  else candidates.sort((a,b) => b.priority - a.priority);
  if (config.strategy === "balanced" && candidates.length > 1) {
    const offset = routeCursor++ % candidates.length;
    return [...candidates.slice(offset), ...candidates.slice(0, offset)];
  }
  return candidates;
}

function textContent(value: unknown): string {
  if (typeof value === "string") return value;
  if (!Array.isArray(value)) return "";
  return value.map(part => part && typeof part === "object" && typeof (part as Record<string,unknown>).text === "string"
    ? (part as Record<string,string>).text : "").filter(Boolean).join("\n");
}
function responseText(protocol: AiProtocol, data: Record<string,unknown>): string {
  if (protocol === "openai-compatible") {
    const choices = Array.isArray(data.choices) ? data.choices : [];
    const message = choices[0] && typeof choices[0] === "object" ? (choices[0] as Record<string,unknown>).message as Record<string,unknown> : undefined;
    return textContent(message?.content).trim();
  }
  if (protocol === "anthropic-messages") return textContent(data.content).trim();
  if (typeof data.output_text === "string") return data.output_text.trim();
  const steps = Array.isArray(data.steps) ? data.steps : [];
  return steps.map(step => {
    if (!step || typeof step !== "object") return "";
    const item = step as Record<string,unknown>;
    return (typeof item.text === "string" ? item.text : "") + textContent(item.content);
  }).filter(Boolean).join("\n").trim();
}
function responseUsage(protocol: AiProtocol, data: Record<string,unknown>): { input?: number; output?: number } {
  const usage = data.usage && typeof data.usage === "object" ? data.usage as Record<string,unknown> : {};
  if (protocol === "anthropic-messages") return {
    input: typeof usage.input_tokens === "number" ? usage.input_tokens : undefined,
    output: typeof usage.output_tokens === "number" ? usage.output_tokens : undefined,
  };
  if (protocol === "gemini-interactions") return {
    input: typeof usage.total_input_tokens === "number" ? usage.total_input_tokens : undefined,
    output: typeof usage.total_output_tokens === "number" ? usage.total_output_tokens : undefined,
  };
  return {
    input: typeof usage.prompt_tokens === "number" ? usage.prompt_tokens : undefined,
    output: typeof usage.completion_tokens === "number" ? usage.completion_tokens : undefined,
  };
}

function responseToolCalls(data: Record<string, unknown>): AiToolCall[] {
  const choices = Array.isArray(data.choices) ? data.choices : [];
  const first = choices[0] && typeof choices[0] === "object" ? choices[0] as Record<string, unknown> : {};
  const message = first.message && typeof first.message === "object" ? first.message as Record<string, unknown> : {};
  const raw = Array.isArray(message.tool_calls) ? message.tool_calls : [];
  const calls: AiToolCall[] = [];
  for (const value of raw.slice(0, 8)) {
    if (!value || typeof value !== "object") continue;
    const item = value as Record<string, unknown>;
    const fn = item.function && typeof item.function === "object" ? item.function as Record<string, unknown> : {};
    const name = typeof fn.name === "string" ? fn.name : "";
    const args = typeof fn.arguments === "string" ? fn.arguments : "";
    if (!/^[A-Za-z0-9_-]{1,64}$/.test(name) || args.length > 12_000) continue;
    calls.push({
      id: typeof item.id === "string" && item.id.length <= 128 ? item.id : "call_" + crypto.randomUUID(),
      type: "function",
      function: { name, arguments: args },
    });
  }
  return calls;
}

async function invoke(candidate: Candidate, input: AiCompletionInput): Promise<{text:string; inputTokens?:number; outputTokens?:number; toolCalls?:AiToolCall[]}> {
  const {provider, model} = candidate;
  const maxTokens = Math.round(numberInRange(input.maxTokens, model.maxOutputTokens || 1800, 1, model.maxOutputTokens || 8192));
  const temperature = numberInRange(input.temperature, 0.2, 0, 2);
  let url: string;
  let headers: Record<string,string>;
  let body: Record<string,unknown>;

  if (provider.protocol === "openai-compatible") {
    url = provider.baseUrl + "/chat/completions";
    headers = { authorization: "Bearer " + provider.apiKey };
    body = {
      model: model.id, messages: input.messages, max_tokens: maxTokens, temperature, stream: false,
      ...(input.tools?.length ? { tools: input.tools, tool_choice: input.toolChoice || "auto" } : {}),
    };
    if (provider.id === "openrouter-legacy") {
      headers["HTTP-Referer"] = "https://github.com/Nolane-x/Nolane-search";
      headers["X-Title"] = "Nolane Search";
    }
  } else if (provider.protocol === "anthropic-messages") {
    url = provider.baseUrl + "/v1/messages";
    headers = { "x-api-key": provider.apiKey, "anthropic-version": "2026-10-21" };
    const system = input.messages.filter(m => m.role === "system").map(m => m.content).join("\n\n");
    body = {
      model: model.id, max_tokens: maxTokens, temperature,
      ...(system ? {system} : {}),
      messages: input.messages.filter(m => m.role !== "system"),
    };
  } else {
    url = provider.baseUrl + "/interactions";
    headers = {"x-goog-api-key": provider.apiKey};
    const system = input.messages.filter(m => m.role === "system").map(m => m.content).join("\n\n");
    const conversation = input.messages.filter(m => m.role !== "system")
      .map(m => (m.role === "assistant" ? "Assistant:\n" : "User:\n") + m.content).join("\n\n");
    body = {
      model: model.id, input: conversation, store: false,
      generation_config: {max_output_tokens: maxTokens, temperature},
      ...(system ? {system_instruction: system} : {}),
    };
  }

  const response = await fetch(url, {
    method: "POST",
    headers: {"content-type": "application/json", accept: "application/json", ...headers},
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(provider.timeoutMs),
  });
  if (!response.ok) throw new Error("HTTP " + response.status);
  const data = await response.json() as Record<string,unknown>;
  const text = responseText(provider.protocol, data);
  const toolCalls = provider.protocol === "openai-compatible" ? responseToolCalls(data) : [];
  if (!text && !toolCalls.length) throw new Error("empty model response");
  const usage = responseUsage(provider.protocol, data);
  return {text, inputTokens: usage.input, outputTokens: usage.output, ...(toolCalls.length ? {toolCalls} : {})};
}

export function getAiRouterStatus(env: Env): AiRouterStatus {
  const config = parseConfig(env);
  return {
    configured: config.providers.length > 0, strategy: config.strategy, maxAttempts: config.maxAttempts,
    providerKeys: config.providers.length,
    models: config.providers.reduce((n,p) => n + p.models.length, 0),
    invalidEntries: config.invalidEntries,
    providers: config.providers.map(p => ({id:p.id, protocol:p.protocol, models:p.models.map(m => ({id:m.id,tasks:m.tasks}))})),
  };
}

export async function completeAi(env: Env, input: AiCompletionInput): Promise<AiCompletionResult> {
  const config = parseConfig(env);
  const allCandidates = candidatesFor(config, input.task);
  const candidates = input.tools?.length
    ? allCandidates.filter(candidate => candidate.provider.protocol === "openai-compatible")
    : allCandidates;
  if (!candidates.length) {
    if (input.tools?.length && allCandidates.length) {
      throw new Error("No OpenAI-compatible AI route is available for native function calling.");
    }
    if (config.invalidEntries) throw new Error("AI router configuration is invalid or has no usable routes.");
    throw new Error("No AI route is configured for task '" + input.task + "'. Add AI_ROUTER_CONFIG in GitHub Actions Secrets.");
  }
  const available = candidates.filter(candidate => !isRouteCoolingDown(candidate));
  // If every route is cooling down, make a bounded recovery attempt instead
  // of leaving the assistant unavailable for the entire cooldown window.
  const selected = (available.length ? available : candidates).slice(0, config.maxAttempts);
  const maxAttempts = selected.length;
  let lastFailure = "unknown provider error";
  for (const candidate of selected) {
    const started = Date.now();
    const key = routeKey(candidate);
    try {
      const result = await invoke(candidate,input);
      routeCooldowns.delete(key);
      const model = candidate.model;
      const estimatedCostUsd = result.inputTokens !== undefined && result.outputTokens !== undefined &&
        model.inputCostUsdPerMillion !== undefined && model.outputCostUsdPerMillion !== undefined
        ? result.inputTokens * model.inputCostUsdPerMillion / 1_000_000 +
          result.outputTokens * model.outputCostUsdPerMillion / 1_000_000
        : undefined;
      return {
        text: result.text, providerId: candidate.provider.id, protocol: candidate.provider.protocol,
        model: model.id, latencyMs: Date.now()-started, inputTokens: result.inputTokens,
        outputTokens: result.outputTokens, estimatedCostUsd,
        ...(result.toolCalls?.length ? {toolCalls: result.toolCalls} : {}),
      };
    } catch (error) {
      lastFailure = error instanceof Error ? error.message : "unknown provider error";
      markRouteCoolingDown(candidate, error);
      console.warn("AI route failed; trying the next route:",candidate.provider.id,candidate.model.id,lastFailure);
    }
  }
  throw new Error("All AI routes failed ("+maxAttempts+" attempt(s)). Last failure: "+lastFailure+". Check provider key validity, model access and quota.");
}
