import { describe, expect, it } from "vitest";
import {
  deletePersonalMemory, getRelevantPersonalMemoryContext, listPersonalMemories, savePersonalMemory,
} from "../src/memory";
import type { Env } from "../src/types";

function createDb() {
  const rows = new Map<string, { payload: string; expires_at: number; created_at: number }>();
  const db = {
    prepare(sql: string) {
      let values: unknown[] = [];
      return {
        bind(...input: unknown[]) { values = input; return this; },
        async all<T>() {
          if (!sql.includes("SELECT cache_key, payload, created_at")) return { results: [] as T[] };
          const [like, now, limit] = values as [string, number, number];
          const prefix = like.slice(0, -1);
          const results = [...rows.entries()]
            .filter(([key, value]) => key.startsWith(prefix) && value.expires_at > now)
            .sort((a, b) => b[1].created_at - a[1].created_at)
            .slice(0, limit)
            .map(([cache_key, value]) => ({ cache_key, payload: value.payload, created_at: value.created_at })) as T[];
          return { results };
        },
        async run() {
          if (sql.startsWith("INSERT INTO search_cache")) {
            const [key, payload, expires_at, created_at] = values as [string, string, number, number];
            rows.set(key, { payload, expires_at, created_at });
            return { meta: { changes: 1 } };
          }
          if (sql.startsWith("DELETE FROM search_cache")) {
            const [key] = values as [string];
            const changed = rows.delete(key);
            return { meta: { changes: changed ? 1 : 0 } };
          }
          return { meta: { changes: 0 } };
        },
        async first<T>() { return null as T | null; },
      };
    },
  };
  return { db, rows };
}

function envWithDb(db: ReturnType<typeof createDb>["db"]): Env {
  return { DB: db as never, SEARCH_JOBS: {} as never };
}

describe("personal memory", () => {
  it("saves, lists and deletes a memory without exposing another user's records", async () => {
    const { db } = createDb();
    const env = envWithDb(db);
    const saved = await savePersonalMemory(env, 101, "preference", "Ưu tiên câu trả lời bằng tiếng Việt.");
    await savePersonalMemory(env, 202, "note", "Private note belonging to another user.");
    expect((await listPersonalMemories(env, 101)).map(item => item.id)).toEqual([saved.id]);
    expect(await deletePersonalMemory(env, 101, saved.id.slice(0, 8))).toMatchObject({ status: "deleted" });
    expect(await listPersonalMemories(env, 101)).toHaveLength(0);
    expect(await listPersonalMemories(env, 202)).toHaveLength(1);
  });

  it("recalls baseline preferences and only project memories relevant to the query", async () => {
    const { db } = createDb();
    const env = envWithDb(db);
    await savePersonalMemory(env, 101, "preference", "Ưu tiên câu trả lời ngắn gọn, có kiểm chứng.");
    await savePersonalMemory(env, 101, "project", "Nolane Search chạy trên Cloudflare Worker và D1.");
    await savePersonalMemory(env, 101, "note", "Đang học hình học không gian.");
    const context = await getRelevantPersonalMemoryContext(env, 101, "Nolane Search Cloudflare Worker");
    expect(context).toContain("câu trả lời ngắn gọn");
    expect(context).toContain("Cloudflare Worker");
    expect(context).not.toContain("hình học không gian");
  });

  it("rejects too-short or oversized memories", async () => {
    const { db } = createDb();
    const env = envWithDb(db);
    await expect(savePersonalMemory(env, 101, "note", "x")).rejects.toThrow("between 3 and 500");
    await expect(savePersonalMemory(env, 101, "note", "x".repeat(501))).rejects.toThrow("between 3 and 500");
  });
});
