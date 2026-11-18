import { afterEach, describe, expect, it, vi } from "vitest";
import { processUpdate } from "../src/index";
import type { D1Database, D1Result, D1Statement, Env, DeepSearchJob } from "../src/types";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("Telegram command rate limits", () => {
  it("prevents a third Deep Search job in the same minute", async () => {
    const counts = new Map<string, number>();
    const queued: DeepSearchJob[] = [];
    const insertedJobs: string[] = [];
    const sentMessages: Array<Record<string, unknown>> = [];

    const DB = {
      prepare(sql: string): D1Statement {
        let values: unknown[] = [];
        const statement = {
          bind(...bindings: unknown[]) { values = bindings; return statement; },
          async run(): Promise<D1Result> {
            if (sql.includes("INSERT INTO web_rate_limits")) {
              const [userId, action, windowStart, limit] = values as [string, string, number, number];
              const key = [userId, action, windowStart].join(":");
              const current = counts.get(key) || 0;
              if (current >= limit) return { results: [], meta: { changes: 0 } };
              counts.set(key, current + 1);
              return { results: [], meta: { changes: 1 } };
            }
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

    vi.stubGlobal("fetch", vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      const body = JSON.parse(String(init?.body || "{}")) as Record<string, unknown>;
      sentMessages.push(body);
      return Response.json({ ok: true, result: { message_id: sentMessages.length } });
    }));

    for (let updateId = 1; updateId <= 3; updateId += 1) {
      await processUpdate(env, {
        update_id: updateId,
        message: {
          message_id: updateId,
          chat: { id: 42, type: "private" },
          from: { id: 42 },
          text: "/deep research rate-limit test",
        },
      });
    }

    expect(insertedJobs).toHaveLength(2);
    expect(queued).toHaveLength(2);
    expect(sentMessages.some(message => String(message.text || "").includes("tối đa 2 job/phút"))).toBe(true);
  });
});
