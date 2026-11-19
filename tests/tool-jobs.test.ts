import { afterEach, describe, expect, it, vi } from "vitest";
import { createToolJob, retryToolJob, updateToolJob, validateToolStepTrace } from "../src/tool-jobs";
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

  it("persists saved workflow identity without sending it or file identifiers to GitHub Actions", async () => {
    const { db, rows } = fakeDb();
    const fetchMock=vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      const body=JSON.parse(String(init?.body||"{}")) as {inputs?:{job_id?:string}};
      expect(body.inputs?.job_id).toBeTruthy();
      expect(JSON.stringify(body)).not.toContain("private-file-id-abcdefghijkl");
      expect(JSON.stringify(body)).not.toContain("workflow-name-private");
      return new Response(null,{status:204});
    });
    vi.stubGlobal("fetch",fetchMock);
    const env={DB:db,NOLANE_GH_ACTIONS_TOKEN:"test-actions-token"} as unknown as Env;
    const job=await createToolJob(env,{
      userId:42,chatId:42,toolId:"json-to-csv",fileId:"private-file-id-abcdefghijkl",
      fileName:"records.json",mimeType:"application/json",fileSize:100,
      pipeline:[{toolId:"json-to-csv"},{toolId:"csv-clean"},{toolId:"csv-to-xlsx"}],
      workflowId:"abcdef123456",workflowName:"workflow-name-private",
      agentPrompt:"Run a saved workflow",
    });
    const stored=JSON.parse(rows.get("tool-job:"+job.id)||"{}");
    expect(stored.workflowId).toBe("abcdef123456");
    expect(stored.workflowName).toBe("workflow-name-private");
    expect(fetchMock).toHaveBeenCalledTimes(1);
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


  it("validates trace entries against the stored pipeline and bounds untrusted fields", () => {
    const pipeline=[{toolId:"video-audio"},{toolId:"audio-transcribe"}];
    const trace=[
      {step:1,total:2,toolId:"video-audio",status:"completed",durationMs:1200,inputBytes:1000,outputBytes:900,summary:"Audio extracted"},
      {step:2,total:2,toolId:"audio-transcribe",status:"completed",durationMs:3400,inputBytes:900,outputBytes:null,summary:"Transcript ready"},
    ];
    expect(validateToolStepTrace(trace,pipeline,"completed")).toEqual({ok:true,trace});
    expect(validateToolStepTrace(trace.slice(0,1),pipeline,"completed").ok).toBe(false);
    expect(validateToolStepTrace([{...trace[0],toolId:"file-hash"},trace[1]],pipeline,"completed").ok).toBe(false);
    expect(validateToolStepTrace([{...trace[0],summary:"x".repeat(900)},trace[1]],pipeline,"completed").ok).toBe(false);
    expect(validateToolStepTrace([{...trace[0],status:"failed",error:"codec error"}],pipeline,"failed").ok).toBe(true);
    expect(validateToolStepTrace(undefined,pipeline,"failed")).toEqual({ok:true,trace:[]});
    expect(validateToolStepTrace(undefined,pipeline,"completed").ok).toBe(false);
  });

  it("retries only an owner's failed job using its private source reference", async () => {
    const {db,rows}=fakeDb();
    const dispatches: string[]=[];
    const fetchMock=vi.fn(async (_input:RequestInfo|URL,init?:RequestInit)=>{
      const body=JSON.parse(String(init?.body||"{}")) as {inputs?:{job_id?:string}};
      dispatches.push(body.inputs?.job_id||"");
      expect(JSON.stringify(body)).not.toContain("telegram-file-id-123456");
      return new Response(null,{status:204});
    });
    vi.stubGlobal("fetch",fetchMock);
    const env={DB:db,NOLANE_GH_ACTIONS_TOKEN:"test-actions-token"} as unknown as Env;
    const original=await createToolJob(env,{
      userId:42,chatId:42,toolId:"video-audio",fileId:"telegram-file-id-123456",
      fileName:"clip.mp4",mimeType:"video/mp4",fileSize:1234,
      pipeline:[{toolId:"video-audio"},{toolId:"audio-convert"}],
      agentPrompt:"Convert this clip",workflowId:"abcdef123456",workflowName:"Media workflow",
    });
    await updateToolJob(env,original.id,{status:"failed",finishedAt:Date.now(),fileId:"telegram-file-id-123456",error:"FFmpeg failed"});
    await expect(retryToolJob(env,99,99,original.id)).rejects.toThrow("Không tìm thấy");
    await expect(retryToolJob(env,42,42,original.id)).resolves.toMatchObject({
      status:"queued",attempt:2,retryOf:original.id,workflowName:"Media workflow",
      pipeline:[{toolId:"video-audio"},{toolId:"audio-convert"}],
    });
    expect(dispatches).toHaveLength(2);
    expect(dispatches[0]).not.toBe(dispatches[1]);
    const retryId=dispatches[1]!;
    const retry=JSON.parse(rows.get("tool-job:"+retryId)||"{}");
    expect(retry.fileId).toBe("telegram-file-id-123456");
    expect(retry.retryOf).toBe(original.id);
  });

  it("does not retry active or successful jobs", async () => {
    const {db}=fakeDb();
    const fetchMock=vi.fn(async ()=>new Response(null,{status:204}));
    vi.stubGlobal("fetch",fetchMock);
    const env={DB:db,NOLANE_GH_ACTIONS_TOKEN:"test-actions-token"} as unknown as Env;
    const active=await createToolJob(env,{
      userId:42,chatId:42,toolId:"image-ocr",fileId:"telegram-file-id-123456",
      fileName:"photo.png",mimeType:"image/png",fileSize:100,
    });
    await expect(retryToolJob(env,42,42,active.id)).rejects.toThrow("đã thất bại");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });


  it("retains the source reference when Actions dispatch itself fails", async () => {
    const {db,rows}=fakeDb();
    vi.stubGlobal("fetch",vi.fn(async()=>new Response("dispatch unavailable",{status:503})));
    const env={DB:db,NOLANE_GH_ACTIONS_TOKEN:"test-actions-token"} as unknown as Env;
    await expect(createToolJob(env,{
      userId:42,chatId:42,toolId:"image-ocr",fileId:"telegram-file-id-123456",
      fileName:"photo.png",mimeType:"image/png",fileSize:100,
    })).rejects.toThrow("dispatch thất bại");
    const saved=[...rows.entries()].find(([key])=>key.startsWith("tool-job:"));
    expect(saved).toBeTruthy();
    const job=JSON.parse(saved![1]);
    expect(job.status).toBe("failed");
    expect(job.fileId).toBe("telegram-file-id-123456");
  });

  it("explains a missing Actions write token before persisting work", async () => {
    const DB = { prepare: () => { throw new Error("D1 should not be used"); } } as unknown as D1Database;
    await expect(createToolJob({ DB } as unknown as Env, {
      userId: 42, chatId: 42, toolId: "image-ocr", fileId: "telegram-file-id-123456",
      fileName: "photo.png", mimeType: "image/png", fileSize: 100,
    })).rejects.toThrow("NOLANE_GH_ACTIONS_TOKEN");
  });
});
