import type { Env } from "./types";
import { getTool, validateToolPipeline } from "./tools";
import type { ToolPipelineStep } from "./tools";

export interface ToolStepTrace {
  step: number;
  total: number;
  toolId: string;
  status: "completed" | "failed";
  durationMs: number;
  inputBytes: number;
  outputBytes: number | null;
  summary: string;
  error?: string;
}

export interface ToolJob {
  id: string;
  userId: number;
  chatId: number;
  toolId: string;
  fileId: string;
  fileName: string;
  mimeType: string;
  fileSize: number;
  status: "queued" | "running" | "completed" | "failed";
  createdAt: number;
  updatedAt: number;
  finishedAt?: number;
  notifiedAt?: number;
  resultSummary?: string;
  error?: string;
  /** Temporary request context used only to synthesize an AI-assisted file job. */
  agentPrompt?: string;
  agentTask?: string;
  agentToolReason?: string;
  pipeline?: ToolPipelineStep[];
  /** Saved workflow identity, kept for per-run history and summaries. */
  workflowId?: string;
  workflowName?: string;
  /** One-based attempt number within a manual retry chain. */
  attempt?: number;
  retryOf?: string;
  trace?: ToolStepTrace[];
}

const PREFIX = "tool-job:";
const TTL_MS = 30 * 24 * 60 * 60 * 1000;

export async function getToolJob(env: Env, id: string): Promise<ToolJob | null> {
  const row = await env.DB.prepare("SELECT payload FROM search_cache WHERE cache_key = ? AND expires_at > ?")
    .bind(PREFIX + id, Date.now()).first<{ payload: string }>();
  if (!row?.payload) return null;
  try { return JSON.parse(row.payload) as ToolJob; } catch { return null; }
}

async function saveToolJob(env: Env, job: ToolJob): Promise<void> {
  const now = Date.now();
  await env.DB.prepare(
    "INSERT INTO search_cache (cache_key, payload, expires_at, created_at) VALUES (?, ?, ?, ?) " +
    "ON CONFLICT(cache_key) DO UPDATE SET payload = excluded.payload, expires_at = excluded.expires_at, created_at = excluded.created_at",
  ).bind(PREFIX + job.id, JSON.stringify(job), now + TTL_MS, now).run();
}

export async function updateToolJob(
  env: Env,
  id: string,
  patch: Partial<Pick<ToolJob, "status" | "updatedAt" | "finishedAt" | "resultSummary" | "error" | "fileId" | "notifiedAt" | "agentPrompt" | "agentTask" | "agentToolReason" | "trace" | "attempt" | "retryOf">>,
): Promise<ToolJob | null> {
  const previous = await getToolJob(env, id);
  if (!previous) return null;
  const next = { ...previous, ...patch, updatedAt: Date.now() };
  await saveToolJob(env, next);
  return next;
}

export async function listToolJobs(env: Env, userId: number, limit = 20): Promise<ToolJob[]> {
  const rows = await env.DB.prepare(
    "SELECT payload FROM search_cache WHERE cache_key LIKE 'tool-job:%' AND expires_at > ? ORDER BY created_at DESC LIMIT ?",
  ).bind(Date.now(), Math.max(1, Math.min(50, limit))).all<{ payload: string }>();
  const jobs: ToolJob[] = [];
  for (const row of rows.results) {
    try {
      const job = JSON.parse(row.payload) as ToolJob;
      if (job.userId === userId) jobs.push(job);
    } catch { /* Skip malformed tool history entries. */ }
  }
  return jobs.slice(0, limit);
}

export function validateToolStepTrace(
  raw: unknown,
  pipeline: ToolPipelineStep[],
  finalStatus: "completed" | "failed",
): { ok: true; trace: ToolStepTrace[] } | { ok: false; error: string } {
  if (!Array.isArray(raw) || raw.length > pipeline.length) return { ok: false, error: "Tool trace has an invalid number of steps." };
  const trace: ToolStepTrace[] = [];
  for (let index = 0; index < raw.length; index++) {
    const value = raw[index];
    if (!value || typeof value !== "object" || Array.isArray(value)) return { ok: false, error: "Tool trace contains an invalid step." };
    const item = value as Record<string, unknown>;
    const expected = pipeline[index]?.toolId;
    if (item.step !== index + 1 || item.total !== pipeline.length ||
        typeof expected !== "string" || item.toolId !== expected ||
        (item.status !== "completed" && item.status !== "failed") ||
        !Number.isSafeInteger(item.durationMs) || Number(item.durationMs) < 0 || Number(item.durationMs) > 45 * 60 * 1000 ||
        !Number.isSafeInteger(item.inputBytes) || Number(item.inputBytes) < 0 || Number(item.inputBytes) > 45 * 1024 * 1024 ||
        (item.outputBytes !== null && (!Number.isSafeInteger(item.outputBytes) || Number(item.outputBytes) < 0 || Number(item.outputBytes) > 45 * 1024 * 1024)) ||
        typeof item.summary !== "string" || item.summary.length > 800 ||
        (item.error !== undefined && (typeof item.error !== "string" || item.error.length > 500))) {
      return { ok: false, error: "Tool trace step does not match the stored pipeline." };
    }
    if (item.status === "failed" && index !== raw.length - 1) return { ok: false, error: "A failed trace step must be the final recorded step." };
    trace.push({
      step: index + 1, total: pipeline.length, toolId: expected, status: item.status,
      durationMs: Number(item.durationMs), inputBytes: Number(item.inputBytes),
      outputBytes: item.outputBytes === null ? null : Number(item.outputBytes), summary: item.summary,
      ...(typeof item.error === "string" ? { error: item.error } : {}),
    });
  }
  if (finalStatus === "completed" && (trace.length !== pipeline.length || trace.some(item => item.status !== "completed"))) {
    return { ok: false, error: "A completed job must contain a successful trace for every pipeline step." };
  }
  return { ok: true, trace };
}

export async function retryToolJob(env: Env, userId: number, chatId: number, sourceJobId: string): Promise<ToolJob> {
  const previous = await getToolJob(env, sourceJobId);
  if (!previous || previous.userId !== userId || previous.chatId !== chatId) {
    throw new Error("Không tìm thấy tool job thuộc cuộc trò chuyện của bạn.");
  }
  if (previous.status !== "failed") throw new Error("Chỉ có thể retry job đã thất bại.");
  if (!previous.fileId || previous.fileId.length < 8) {
    throw new Error("Job cũ không còn Telegram file reference. Hãy gửi lại tệp gốc để chạy lại.");
  }
  return createToolJob(env, {
    userId: previous.userId, chatId: previous.chatId, toolId: previous.toolId, fileId: previous.fileId,
    fileName: previous.fileName, mimeType: previous.mimeType, fileSize: previous.fileSize,
    pipeline: previous.pipeline || [{ toolId: previous.toolId }],
    workflowId: previous.workflowId, workflowName: previous.workflowName,
    agentPrompt: previous.agentPrompt, agentTask: previous.agentTask, agentToolReason: previous.agentToolReason,
    retryOf: previous.id, attempt: (previous.attempt || 1) + 1,
  });
}

export async function createToolJob(env: Env, input: Omit<ToolJob, "id" | "status" | "createdAt" | "updatedAt">): Promise<ToolJob> {
  const tool = getTool(input.toolId);
  if (!tool?.ready) throw new Error("Công cụ này chưa được kích hoạt.");
  const pipeline = validateToolPipeline(
    { mimeType: input.mimeType, fileName: input.fileName },
    input.pipeline || [{ toolId: input.toolId }],
  );
  if (!pipeline.ok) throw new Error("Tool pipeline không hợp lệ: " + pipeline.error);
  if (pipeline.steps[0]?.toolId !== input.toolId) {
    throw new Error("Tool ID phải trùng với bước đầu tiên trong pipeline.");
  }
  if (!env.NOLANE_GH_ACTIONS_TOKEN) {
    throw new Error("Thiếu GitHub Actions token. Hãy thêm GitHub Secret NOLANE_GH_ACTIONS_TOKEN với quyền Actions: write cho repository Nolane-x/Nolane-search.");
  }
  if (typeof input.fileId !== "string" || input.fileId.length < 8 || input.fileId.length > 1024 || /[\u0000-\u001f\u007f]/.test(input.fileId)) {
    throw new Error("Telegram file_id không hợp lệ.");
  }
  if (input.fileSize > 20 * 1024 * 1024) throw new Error("Telegram Bot API chỉ tải được tệp tối đa 20 MB qua getFile.");
  const now = Date.now();
  const job: ToolJob = { ...input, pipeline: pipeline.steps, trace: undefined, attempt: input.attempt || 1, id: crypto.randomUUID(), status: "queued", createdAt: now, updatedAt: now };
  await saveToolJob(env, job);
  try {
    const response = await fetch(
      "https://api.github.com/repos/Nolane-x/Nolane-search/actions/workflows/tool-runner.yml/dispatches",
      {
        method: "POST",
        headers: {
          authorization: "Bearer " + env.NOLANE_GH_ACTIONS_TOKEN,
          accept: "application/vnd.github+json",
          "content-type": "application/json",
          "x-github-api-version": "2022-11-28",
        },
        body: JSON.stringify({ ref: "main", inputs: { job_id: job.id } }),
        signal: AbortSignal.timeout(15_000),
      },
    );
    if (response.status !== 204) {
      const detail = (await response.text().catch(() => "")).slice(0, 700);
      throw new Error("GitHub Actions dispatch thất bại (" + response.status + "). " + detail);
    }
  } catch (error) {
    await updateToolJob(env, job.id, {
      status: "failed",
      finishedAt: Date.now(),
      fileId: "",
      error: error instanceof Error ? error.message.slice(0, 500) : "Không thể kích hoạt GitHub Actions.",
    });
    throw error;
  }
  return job;
}
