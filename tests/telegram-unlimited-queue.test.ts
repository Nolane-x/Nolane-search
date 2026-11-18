import { afterEach, describe, expect, it, vi } from "vitest";
import { processUpdate } from "../src/index";
import type { D1Database, D1Result, D1Statement, Env, DeepSearchJob } from "../src/types";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("single-owner Telegram usage", () => {
  it("allows five Deep Search jobs within the same minute", async () => {
    const queued: DeepSearchJob[] = [];
    const insertedJobs: string[] = [];

    const DB = {
      prepare(sql: string): D1Statement {
        let values: unknown[] = [];
        const statement = {
          bind(...bindings: unknown[]) { values = bindings; return statement; },
          async run(): Promise<D1Result> {
            if (sql.includes("INSERT INTO deep_search_jobs")) insertedJobs.push(String(values[0]));
            return { results: [], meta: { changes: 1 } };
          },
          async first<T>(): Promise<T | null> { return null; },
          async all<T>(): Promise<D1Result<T>> { return { results: [] }; },
        };
        return statement as D1Statement;
      },
      async batch<T>(): Promise<D1Result<T>[]> { return []; },
    } satisfies D1Database;

    const env = {
      TELEGRAM_BOT_TOKEN: "test-token",
      ALLOWED_TELEGRAM_USER_IDS: "42",
      DB,
      SEARCH_JOBS: { async send(job: DeepSearchJob) { queued.push(job); } },
    } as unknown as Env;

    vi.stubGlobal("fetch", vi.fn(async () =>
      Response.json({ ok: true, result: { message_id: 1 } }),
    ));

    for (let updateId = 1; updateId <= 5; updateId += 1) {
      await processUpdate(env, {
        update_id: updateId,
        message: {
          message_id: updateId,
          chat: { id: 42, type: "private" },
          from: { id: 42 },
          text: "/deep unrestricted owner request " + updateId,
        },
      });
    }

    expect(insertedJobs).toHaveLength(5);
    expect(queued).toHaveLength(5);
  });
});
