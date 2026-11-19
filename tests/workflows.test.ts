import { describe, expect, it } from "vitest";
import {
  clearPendingToolWorkflow, deleteToolWorkflow, getPendingToolWorkflow,
  getToolWorkflow, listToolWorkflows,
  saveToolWorkflow, setPendingToolWorkflow,
} from "../src/workflows";
import type { D1Database, D1Result, D1Statement, Env } from "../src/types";

function fakeDb() {
  const rows = new Map<string, { payload: string; expiresAt: number; createdAt: number }>();
  const db = {
    prepare(sql: string): D1Statement {
      let values: unknown[] = [];
      const statement = {
        bind(...bindings: unknown[]) { values = bindings; return statement; },
        async run(): Promise<D1Result> {
          if (sql.startsWith("INSERT INTO search_cache")) {
            rows.set(String(values[0]), { payload: String(values[1]), expiresAt: Number(values[2]), createdAt: Number(values[3]) });
          } else if (sql.startsWith("DELETE FROM search_cache WHERE cache_key = ?")) {
            rows.delete(String(values[0]));
          }
          return { results: [], meta: { changes: 1 } };
        },
        async first<T>(): Promise<T | null> {
          if (sql.includes("SELECT payload FROM search_cache WHERE cache_key = ?")) {
            const row = rows.get(String(values[0]));
            if (!row || (values.length > 1 && row.expiresAt <= Number(values[1]))) return null;
            return { payload: row.payload } as T;
          }
          return null;
        },
        async all<T>(): Promise<D1Result<T>> {
          if (!sql.includes("SELECT payload FROM search_cache WHERE cache_key LIKE ?")) return { results: [] };
          const prefix = String(values[0]).replace(/%$/, "");
          const now = Number(values[1]);
          const results = [...rows.entries()]
            .filter(([key, row]) => key.startsWith(prefix) && row.expiresAt > now)
            .sort((a,b) => b[1].createdAt-a[1].createdAt)
            .map(([,row]) => ({ payload: row.payload }) as T);
          return { results };
        },
      };
      return statement as D1Statement;
    },
    async batch<T>(): Promise<D1Result<T>[]> { return []; },
  } satisfies D1Database;
  return { db, rows };
}

const envFor = (db: D1Database) => ({ DB: db } as unknown as Env);

describe("Saved Nolane Tool Workflows", () => {
  it("saves, retrieves and lists an owner-bound validated workflow", async () => {
    const { db } = fakeDb();
    const env=envFor(db);
    const workflow=await saveToolWorkflow(env,42,42,"  Video   transcript  ",[
      {toolId:"video-audio"},{toolId:"audio-convert"},{toolId:"audio-transcribe"},
    ]);
    expect(workflow.id).toMatch(/^[a-f0-9]{12}$/);
    expect(workflow.name).toBe("Video transcript");
    expect((await getToolWorkflow(env,42,workflow.id))?.steps.map(step=>step.toolId))
      .toEqual(["video-audio","audio-convert","audio-transcribe"]);
    expect(await getToolWorkflow(env,43,workflow.id)).toBeNull();
    expect((await listToolWorkflows(env,42)).map(item=>item.id)).toEqual([workflow.id]);
    expect(await listToolWorkflows(env,43)).toEqual([]);
  });

  it("rejects invalid pipeline transitions and duplicate names before saving", async () => {
    const { db, rows }=fakeDb();
    const env=envFor(db);
    await expect(saveToolWorkflow(env,42,42,"Broken chain",[
      {toolId:"video-info"},{toolId:"audio-transcribe"},
    ])).rejects.toThrow("luồng dữ liệu");
    expect(rows.size).toBe(0);
    await saveToolWorkflow(env,42,42,"My workflow",[{toolId:"image-ocr"},{toolId:"text-clean"}]);
    await expect(saveToolWorkflow(env,42,42,"MY WORKFLOW",[{toolId:"image-ocr"}]))
      .rejects.toThrow("trùng tên");
    expect(rows.size).toBe(1);
  });

  it("accepts long workflows and rejects repeated processors", async () => {
    const {db,rows}=fakeDb();
    const env=envFor(db);
    await expect(saveToolWorkflow(env,42,42,"x",[{toolId:"image-ocr"}])).rejects.toThrow("3–40");
    const long=await saveToolWorkflow(env,42,42,"Long pipeline",[
      "video-audio","audio-convert","audio-transcribe","text-clean","text-deduplicate","text-stats",
    ].map(toolId=>({toolId})));
    expect(long.steps).toHaveLength(6);
    await expect(saveToolWorkflow(env,42,42,"Repeated",[{toolId:"file-hash"},{toolId:"file-hash"}]))
      .rejects.toThrow("lặp lại");
    expect(rows.size).toBe(1);
  });

  it("does not impose a workflow-count quota or expiry", async () => {
    const {db,rows}=fakeDb();
    const env=envFor(db);
    for(let index=0;index<25;index++){
      await saveToolWorkflow(env,42,42,"Workflow "+String(index+1).padStart(2,"0"),[{toolId:"file-hash"}]);
    }
    expect((await listToolWorkflows(env,42))).toHaveLength(25);
    expect(rows.size).toBe(25);
    expect([...rows.values()].every(row=>row.expiresAt>1_000_000_000_000_000)).toBe(true);
  });

  it("arms, resolves and clears a pending run without exposing another user's workflow", async () => {
    const {db,rows}=fakeDb();
    const env=envFor(db);
    const workflow=await saveToolWorkflow(env,42,42,"JSON to Excel",[
      {toolId:"json-to-csv"},{toolId:"csv-clean"},{toolId:"csv-to-xlsx"},
    ]);
    await setPendingToolWorkflow(env,42,42,workflow.id);
    const pending=await getPendingToolWorkflow(env,42,42);
    expect(pending?.pending.workflowId).toBe(workflow.id);
    expect(pending?.workflow.name).toBe("JSON to Excel");
    expect(await getPendingToolWorkflow(env,43,42)).toBeNull();
    await clearPendingToolWorkflow(env,42,42);
    expect(await getPendingToolWorkflow(env,42,42)).toBeNull();
    expect([...rows.keys()].some(key=>key.startsWith("tool-workflow-pending:"))).toBe(false);
  });

  it("deletes only a workflow owned by the requesting user", async () => {
    const {db}=fakeDb();
    const env=envFor(db);
    const workflow=await saveToolWorkflow(env,42,42,"Image cleanup",[{toolId:"image-clean-exif"}]);
    expect(await deleteToolWorkflow(env,43,workflow.id)).toBe(false);
    expect(await getToolWorkflow(env,42,workflow.id)).not.toBeNull();
    expect(await deleteToolWorkflow(env,42,workflow.id)).toBe(true);
    expect(await getToolWorkflow(env,42,workflow.id)).toBeNull();
  });
});
