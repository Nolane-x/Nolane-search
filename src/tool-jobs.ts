import type { Env } from "./types";
import { getTool, isToolCompatible } from "./tools";

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
  resultSummary?: string;
  error?: string;
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
  patch: Partial<Pick<ToolJob, "status" | "updatedAt" | "finishedAt" | "resultSummary" | "error">>,
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

export async function createToolJob(env: Env, input: Omit<ToolJob, "id" | "status" | "createdAt" | "updatedAt">): Promise<ToolJob> {
  const tool = getTool(input.toolId);
  if (!tool?.ready) throw new Error("Công cụ này chưa được kích hoạt.");
  if (!isToolCompatible(tool, input.mimeType, input.fileName)) {
    throw new Error("Định dạng tệp không phù hợp với công cụ " + tool.name + ".");
  }
  if (!env.GITHUB_ACTIONS_TOKEN) {
    throw new Error("Thiếu GitHub Actions token. Hãy thêm GitHub Secret GITHUB_ACTIONS_TOKEN với quyền Actions: write cho repository Nolane-x/Nolane-search.");
  }
  if (typeof input.fileId !== "string" || input.fileId.length < 8 || input.fileId.length > 1024 || /[\u0000-\u001f\u007f]/.test(input.fileId)) {
    throw new Error("Telegram file_id không hợp lệ.");
  }
  if (input.fileSize > 20 * 1024 * 1024) throw new Error("Telegram Bot API chỉ tải được tệp tối đa 20 MB qua getFile.");
  const now = Date.now();
  const job: ToolJob = { ...input, id: crypto.randomUUID(), status: "queued", createdAt: now, updatedAt: now };
  await saveToolJob(env, job);
  try {
    const response = await fetch(
      "https://api.github.com/repos/Nolane-x/Nolane-search/actions/workflows/tool-runner.yml/dispatches",
      {
        method: "POST",
        headers: {
          authorization: "Bearer " + env.GITHUB_ACTIONS_TOKEN,
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
      error: error instanceof Error ? error.message.slice(0, 500) : "Không thể kích hoạt GitHub Actions.",
    });
    throw error;
  }
  return job;
}
