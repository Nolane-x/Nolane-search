import { describe, expect, it } from "vitest";
import { consumeRateLimit } from "../src/rate-limit";
import type { D1Database, D1Result, D1Statement } from "../src/types";

function createRateLimitDb() {
  const counts = new Map<string, number>();
  const db = {
    prepare(sql: string): D1Statement {
      let values: unknown[] = [];
      const statement = {
        bind(...bindings: unknown[]) {
          values = bindings;
          return statement;
        },
        async run(): Promise<D1Result> {
          if (!sql.includes("INSERT INTO web_rate_limits")) {
            throw new Error("Unexpected SQL in rate-limit test: " + sql);
          }
          const [userId, action, windowStart, limit] = values as [string, string, number, number];
          const key = [userId, action, windowStart].join(":");
          const current = counts.get(key) || 0;
          if (current >= limit) return { meta: { changes: 0 } };
          counts.set(key, current + 1);
          return { meta: { changes: 1 } };
        },
        async first<T>(): Promise<T | null> { return null; },
        async all<T>(): Promise<D1Result<T>> { return { results: [] }; },
      };
      return statement as D1Statement;
    },
    async batch<T>(): Promise<D1Result<T>[]> { return []; },
  } satisfies D1Database;
  return { db, counts };
}

describe("atomic D1 rate limiting", () => {
  it("allows exactly the configured number of requests in one minute", async () => {
    const { db, counts } = createRateLimitDb();
    const now = 1_800_000_000_000;

    expect(await consumeRateLimit(db, 42, "telegram:deep", 2, now)).toBe(true);
    expect(await consumeRateLimit(db, 42, "telegram:deep", 2, now + 1)).toBe(true);
    expect(await consumeRateLimit(db, 42, "telegram:deep", 2, now + 2)).toBe(false);
    expect(counts.get("42:telegram:deep:1800000000000")).toBe(2);
  });

  it("isolates users and actions, then resets at the next minute boundary", async () => {
    const { db } = createRateLimitDb();
    const now = 1_800_000_000_000;

    expect(await consumeRateLimit(db, 42, "telegram:search", 1, now)).toBe(true);
    expect(await consumeRateLimit(db, 42, "telegram:search", 1, now + 1)).toBe(false);
    expect(await consumeRateLimit(db, 43, "telegram:search", 1, now + 1)).toBe(true);
    expect(await consumeRateLimit(db, 42, "telegram:ai", 1, now + 1)).toBe(true);
    expect(await consumeRateLimit(db, 42, "telegram:search", 1, now + 60_000)).toBe(true);
  });

  it("fails closed for invalid identities, action keys and limits", async () => {
    const { db, counts } = createRateLimitDb();

    expect(await consumeRateLimit(db, -1, "telegram:ai", 1)).toBe(false);
    expect(await consumeRateLimit(db, 42, "unsafe action", 1)).toBe(false);
    expect(await consumeRateLimit(db, 42, "telegram:ai", 0)).toBe(false);
    expect(counts.size).toBe(0);
  });
});
