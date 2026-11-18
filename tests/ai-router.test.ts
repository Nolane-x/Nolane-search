import { afterEach, describe, expect, it, vi } from "vitest";
import { completeAi, getAiRouterStatus } from "../src/ai-router";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());

function env(config: unknown): Env {
  return { DB: {} as never, SEARCH_JOBS: {} as never, AI_ROUTER_CONFIG: JSON.stringify(config) };
}
function route(id: string, protocol: string, baseUrl: string, apiKey: string, models: unknown[]) {
  return { id, protocol, baseUrl, apiKey, models };
}

describe("AI Router configuration", () => {
  it("counts separate API keys and models without exposing key values", () => {
    const status = getAiRouterStatus(env({
      strategy: "balanced",
      providers: [
        route("groq-key-1", "openai-compatible", "https://api.groq.com/openai/v1", "secret-groq-key-one", ["llama-3.3-70b"]),
        route("groq-key-2", "openai-compatible", "https://api.groq.com/openai/v1", "secret-groq-key-two", ["llama-3.3-70b"]),
        route("claude-main", "anthropic-messages", "https://api.anthropic.com", "secret-anthropic-key", ["claude-sonnet"]),
      ],
    }));
    expect(status).toMatchObject({ configured: true, providerKeys: 3, models: 3, strategy: "balanced" });
    expect(JSON.stringify(status)).not.toContain("secret-");
    expect(status.providers.map(provider => provider.id)).toEqual(["groq-key-1", "groq-key-2", "claude-main"]);
  });

  it("rejects insecure or private custom endpoints", () => {
    const status = getAiRouterStatus(env({
      providers: [
        route("insecure", "openai-compatible", "http://api.example.com/v1", "secret-key-123", ["model-a"]),
        route("local", "openai-compatible", "https://127.0.0.1/v1", "secret-key-456", ["model-b"]),
      ],
    }));
    expect(status.configured).toBe(false);
    expect(status.invalidEntries).toBe(2);
  });

  it("keeps legacy OpenRouter credentials as a fallback route", () => {
    const legacy = {
      DB: {} as never, SEARCH_JOBS: {} as never,
      OPENROUTER_API_KEY: "legacy-openrouter-key",
      OPENROUTER_MODELS: "provider/model-a,provider/model-b",
    } as Env;
    expect(getAiRouterStatus(legacy)).toMatchObject({ configured: true, providerKeys: 1, models: 2 });
  });
});

describe("AI Router protocol adapters and failover", () => {
  it("uses the next key after a rate-limit response", async () => {
    const calls: string[] = [];
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      const authorization = new Headers(init?.headers).get("authorization") || "";
      calls.push(authorization);
      if (authorization === "Bearer first-secret-key") return new Response("limited", { status: 429 });
      return new Response(JSON.stringify({
        choices: [{message:{content:"The second key succeeded."}}],
        usage: {prompt_tokens:10,completion_tokens:5},
      }), {status:200,headers:{"content-type":"application/json"}});
    });
    vi.stubGlobal("fetch",fetchMock);
    const result = await completeAi(env({strategy:"priority",providers:[
      route("groq-one","openai-compatible","https://api.groq.com/openai/v1","first-secret-key",["llama-3.3-70b"]),
      route("groq-two","openai-compatible","https://api.groq.com/openai/v1","second-secret-key",["llama-3.3-70b"]),
    ]}),{task:"chat",messages:[{role:"user",content:"Hello"}]});
    expect(result.text).toBe("The second key succeeded.");
    expect(result.providerId).toBe("groq-two");
    expect(result.inputTokens).toBe(10);
    expect(calls).toHaveLength(2);
  });

  it("uses Anthropic Messages request shape", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      expect(String(input)).toBe("https://api.anthropic.com/v1/messages");
      expect(new Headers(init?.headers).get("anthropic-version")).toBe("2026-10-21");
      expect(new Headers(init?.headers).get("x-api-key")).toBe("anthropic-secret-key");
      const body=JSON.parse(String(init?.body));
      expect(body.system).toBe("System prompt");
      expect(body.messages).toEqual([{role:"user",content:"Question"}]);
      return new Response(JSON.stringify({content:[{type:"text",text:"Claude response"}],usage:{input_tokens:20,output_tokens:8}}),{status:200});
    });
    vi.stubGlobal("fetch",fetchMock);
    const result=await completeAi(env({providers:[
      route("claude","anthropic-messages","https://api.anthropic.com","anthropic-secret-key",["claude-model"]),
    ]}),{task:"reasoning",messages:[{role:"system",content:"System prompt"},{role:"user",content:"Question"}]});
    expect(result.text).toBe("Claude response");
    expect(result.outputTokens).toBe(8);
  });

  it("uses Gemini Interactions request shape and extracts output steps", async () => {
    const fetchMock=vi.fn(async(input:RequestInfo|URL,init?:RequestInit)=>{
      expect(String(input)).toBe("https://generativelanguage.googleapis.com/v1beta/interactions");
      expect(new Headers(init?.headers).get("x-goog-api-key")).toBe("gemini-secret-key");
      const body=JSON.parse(String(init?.body));
      expect(body.model).toBe("gemini-flash");
      expect(body.system_instruction).toBe("Be helpful");
      expect(body.input).toContain("User:");
      return new Response(JSON.stringify({steps:[{type:"model_output",content:[{type:"text",text:"Gemini response"}]}],usage:{total_input_tokens:12,total_output_tokens:9}}),{status:200});
    });
    vi.stubGlobal("fetch",fetchMock);
    const result=await completeAi(env({providers:[
      route("gemini","gemini-interactions","https://generativelanguage.googleapis.com/v1beta","gemini-secret-key",["gemini-flash"]),
    ]}),{task:"summary",messages:[{role:"system",content:"Be helpful"},{role:"user",content:"Summarize this"}]});
    expect(result.text).toBe("Gemini response");
    expect(result.inputTokens).toBe(12);
  });

  it("routes only to models declaring the requested task", async () => {
    const fetchMock=vi.fn(async(_input:RequestInfo|URL,init?:RequestInit)=>{
      const body=JSON.parse(String(init?.body));
      expect(body.model).toBe("coding-model");
      return new Response(JSON.stringify({choices:[{message:{content:"done"}}]}),{status:200});
    });
    vi.stubGlobal("fetch",fetchMock);
    const result=await completeAi(env({strategy:"priority",providers:[
      route("multi-task","openai-compatible","https://api.example.ai/v1","api-key-value-123",[
        {id:"cheap-model",tasks:["fast"],priority:100},
        {id:"coding-model",tasks:["coding"],priority:1},
      ]),
    ]}),{task:"coding",messages:[{role:"user",content:"Write code"}]});
    expect(result.model).toBe("coding-model");
  });

  it("uses a small default failover budget and caps configured attempts", () => {
    const defaultStatus = getAiRouterStatus(env({ providers: [
      route("attempt-primary", "openai-compatible", "https://api.example.ai/v1", "primary-key-123", ["model-a"]),
    ] }));
    const cappedStatus = getAiRouterStatus(env({ maxAttempts: 24, providers: [
      route("attempt-cap", "openai-compatible", "https://api.example.ai/v1", "primary-key-123", ["model-a"]),
    ] }));
    expect(defaultStatus.maxAttempts).toBe(3);
    expect(cappedStatus.maxAttempts).toBe(6);
  });

  it("temporarily skips a route after an upstream failure on the next request", async () => {
    const calls: string[] = [];
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      calls.push(url);
      if (url.includes("primary-cooldown.example.ai")) return new Response("unavailable", { status: 503 });
      return new Response(JSON.stringify({ choices: [{ message: { content: "backup ok" } }] }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    const configuration = env({ strategy: "priority", providers: [
      route("primary-cooldown-test", "openai-compatible", "https://primary-cooldown.example.ai/v1", "primary-secret-123", ["model-a"]),
      route("backup-cooldown-test", "openai-compatible", "https://backup-cooldown.example.ai/v1", "backup-secret-123", ["model-b"]),
    ] });
    const input = { task: "chat" as const, messages: [{ role: "user" as const, content: "hello" }] };
    expect((await completeAi(configuration, input)).text).toBe("backup ok");
    const afterFirstRequest = calls.length;
    expect((await completeAi(configuration, input)).text).toBe("backup ok");
    expect(calls).toHaveLength(afterFirstRequest + 1);
    expect(calls.slice(-1)[0]).toContain("backup-cooldown.example.ai");
  });
});
