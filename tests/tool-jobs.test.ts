import { afterEach, describe, expect, it, vi } from "vitest";
import { createToolJob } from "../src/tool-jobs";
import type { D1Database, D1Result, D1Statement, Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());

function fakeDb() {
  const rows = new Map<string, string>();
  const db = {
    prepare(sql: string): D1Statement {
      let values: unknown[] = [];
      const statement = {
        bind(...bindings: unknown[]) { values = bindings; return statement; },
        async run(): Promise<D1Result> {
          if (sql.startsWith("INSERT INTO search_cache")) {
            rows.set(String(values[0]), String(values[1]));
          } else if (sql.startsWith("UPDATE search_cache")) {
            rows.set(String(values[3]), String(values[0]));
          }
          return { results: [], meta: { changes: 1 } };
        },
        async first<T>(): Promise<T | null> {
          if (sql.includes("SELECT payload FROM search_cache WHERE cache_key = ?")) {
            const payload = rows.get(String(values[0]));
            return payload ? ({ payload } as T) : null;
          }
          return null;
        },
        async all<T>(): Promise<D1Result<T>> { return { results: [] }; },
      };
      return statement as D1Statement;
    },
    async batch<T>(): Promise<D1Result<T>[]> { return []; },
  } satisfies D1Database;
  return { db, rows };
}

describe("GitHub Actions tool dispatch", () => {
  it("persists metadata and dispatches only an opaque job ID", async () => {
    const { db, rows } = fakeDb();
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const body = JSON.parse(String(init?.body || "{}")) as { ref?: string; inputs?: { job_id?: string } };
      expect(String(input)).toContain("/actions/workflows/tool-runner.yml/dispatches");
      expect(init?.method).toBe("POST");
      expect(body.ref).toBe("main");
      expect(body.inputs?.job_id).toBeTruthy();
      expect(JSON.stringify(body)).not.toContain("telegram-file-id-123456");
      return new Response(null, { status: 204 });
    });
    vi.stubGlobal("fetch", fetchMock);

    const env = { DB: db, NOLANE_GH_ACTIONS_TOKEN: "test-actions-token" } as unknown as Env;
    const job = await createToolJob(env, {
      userId: 42, chatId: 42, toolId: "image-ocr", fileId: "telegram-file-id-123456",
      fileName: "homework.jpg", mimeType: "image/jpeg", fileSize: 1234,
    });

    expect(job.status).toBe("queued");
    expect(rows.has("tool-job:" + job.id)).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("persists a validated multi-step pipeline while still dispatching only the opaque job ID", async () => {
    const { db, rows } = fakeDb();
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      const body = JSON.parse(String(init?.body || "{}")) as { inputs?: { job_id?: string } };
      expect(body.inputs?.job_id).toBeTruthy();
      expect(JSON.stringify(body)).not.toContain("telegram-file-id-123456");
      return new Response(null, { status: 204 });
    });
    vi.stubGlobal("fetch", fetchMock);
    const env = { DB: db, NOLANE_GH_ACTIONS_TOKEN: "test-actions-token" } as unknown as Env;
    const job = await createToolJob(env, {
      userId:42,chatId:42,toolId:"video-audio",fileId:"telegram-file-id-123456",
      fileName:"clip.mp4",mimeType:"video/mp4",fileSize:1234,
      pipeline:[{toolId:"video-audio"},{toolId:"audio-convert"},{toolId:"audio-transcribe"}],
      agentPrompt:"Transcribe the clip",
    });
    expect(job.pipeline?.map(step=>step.toolId)).toEqual(["video-audio","audio-convert","audio-transcribe"]);
    const stored=JSON.parse(rows.get("tool-job:"+job.id)||"{}");
    expect(stored.pipeline).toHaveLength(3);
  });

  it("rejects an unsupported pipeline before any D1 write or dispatch", async () => {
    const DB = { prepare: () => { throw new Error("D1 should not be used"); } } as unknown as D1Database;
    const fetchMock=vi.fn();
    vi.stubGlobal("fetch",fetchMock);
    await expect(createToolJob({DB,NOLANE_GH_ACTIONS_TOKEN:"test-actions-token"} as unknown as Env,{
      userId:42,chatId:42,toolId:"video-info",fileId:"telegram-file-id-123456",
      fileName:"clip.mp4",mimeType:"video/mp4",fileSize:1234,
      pipeline:[{toolId:"video-info"},{toolId:"audio-transcribe"}],
    })).rejects.toThrow("pipeline");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("rejects unsupported formats before dispatch", async () => {
    const { db } = fakeDb();
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const env = { DB: db, NOLANE_GH_ACTIONS_TOKEN: "test-actions-token" } as unknown as Env;

    await expect(createToolJob(env, {
      userId: 42, chatId: 42, toolId: "pdf-text", fileId: "telegram-file-id-123456",
      fileName: "photo.jpg", mimeType: "image/jpeg", fileSize: 100,
    })).rejects.toThrow("không tương thích");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("explains a missing Actions write token before persisting work", async () => {
    const DB = { prepare: () => { throw new Error("D1 should not be used"); } } as unknown as D1Database;
    await expect(createToolJob({ DB } as unknown as Env, {
      userId: 42, chatId: 42, toolId: "image-ocr", fileId: "telegram-file-id-123456",
      fileName: "photo.png", mimeType: "image/png", fileSize: 100,
    })).rejects.toThrow("NOLANE_GH_ACTIONS_TOKEN");
  });
});
