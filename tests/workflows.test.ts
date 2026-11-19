import { describe, expect, it } from "vitest";
import {
  clearPendingToolWorkflow, deleteToolWorkflow, getPendingToolWorkflow,
  getToolWorkflow, listToolWorkflows,
  saveToolWorkflow, saveDagToolWorkflow, setPendingToolWorkflow,
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


  it("saves and reloads a branching DAG with parallel siblings", async () => {
    const {db,rows}=fakeDb();
    const env=envFor(db);
    const graph={nodes:[
      {id:"extract",toolId:"video-audio",dependsOn:[]},
      {id:"inspect",toolId:"audio-info",dependsOn:["extract"],input:"parent"},
      {id:"transcribe",toolId:"audio-transcribe",dependsOn:["extract"],input:"parent"},
    ]};
    const saved=await saveDagToolWorkflow(env,42,42,"Parallel video analysis",graph);
    expect(saved.graph?.nodes.map(node=>node.id)).toEqual(["extract","inspect","transcribe"]);
    expect(saved.steps.map(step=>step.toolId)).toEqual(["video-audio","audio-info","audio-transcribe"]);
    const loaded=await getToolWorkflow(env,42,saved.id);
    expect(loaded?.graph?.nodes[1]?.dependsOn).toEqual(["extract"]);
    expect(loaded?.graph?.nodes[2]?.toolId).toBe("audio-transcribe");
    expect(await getToolWorkflow(env,43,saved.id)).toBeNull();
    expect(rows.size).toBe(1);
  });

  it("rejects cycles, missing dependencies and unsupported parent data edges", async () => {
    const {db,rows}=fakeDb();
    const env=envFor(db);
    await expect(saveDagToolWorkflow(env,42,42,"Cycle graph",{nodes:[
      {id:"a",toolId:"video-audio",dependsOn:["b"],input:"parent"},
      {id:"b",toolId:"audio-info",dependsOn:["a"],input:"parent"},
    ]})).rejects.toThrow("chu trình");
    await expect(saveDagToolWorkflow(env,42,42,"Missing parent",{nodes:[
      {id:"a",toolId:"video-audio",dependsOn:["missing"],input:"parent"},
    ]})).rejects.toThrow("không tồn tại");
    await expect(saveDagToolWorkflow(env,42,42,"Bad edge",{nodes:[
      {id:"extract",toolId:"video-audio",dependsOn:[]},
      {id:"bad",toolId:"text-clean",dependsOn:["extract"],input:"parent"},
    ]})).rejects.toThrow("luồng dữ liệu");
    expect(rows.size).toBe(0);
  });

  it("validates conditional failure branches and multi-dependency barriers", async () => {
    const {db}=fakeDb();
    const env=envFor(db);
    const workflow=await saveDagToolWorkflow(env,42,42,"Failure branch",{nodes:[
      {id:"extract",toolId:"video-audio",dependsOn:[]},
      {id:"transcribe",toolId:"audio-transcribe",dependsOn:["extract"],input:"parent"},
      {id:"fallback",toolId:"video-info",dependsOn:["transcribe"],input:"source",when:"any-failure"},
    ]});
    expect(workflow.graph?.nodes[2]).toMatchObject({id:"fallback",when:"any-failure",input:"source"});
    await expect(saveDagToolWorkflow(env,42,42,"Bad branch",{nodes:[
      {id:"extract",toolId:"video-audio",dependsOn:[]},
      {id:"fallback",toolId:"video-info",dependsOn:["extract"],input:"source",when:"all-success"},
    ]})).rejects.toThrow("input=source");
    const barrier=await saveDagToolWorkflow(env,42,42,"Barrier",{nodes:[
      {id:"left",toolId:"video-audio",dependsOn:[]},
      {id:"right",toolId:"video-info",dependsOn:[]},
      {id:"after-both",toolId:"video-thumbnail",dependsOn:["left","right"],input:"source",when:"all-success"},
    ]});
    expect(barrier.graph?.nodes.at(-1)?.dependsOn).toEqual(["left","right"]);
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
