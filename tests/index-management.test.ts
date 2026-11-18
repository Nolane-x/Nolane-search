import { describe, expect, it, vi } from "vitest";
import {
  deleteIndexedContent, listIndexedPages, normalizeIndexDomain, normalizeIndexPageUrl,
} from "../src/index-management";
import type { Env } from "../src/types";

describe("personal index target validation", () => {
  it("normalizes a public domain and rejects unsafe or malformed targets", () => {
    expect(normalizeIndexDomain("WWW.Example.com.")).toBe("example.com");
    expect(normalizeIndexDomain("sub.example.com")).toBe("sub.example.com");
    for (const value of ["", "localhost", "example.com/path", "example..com", "-bad.example", "bad-.example", "127.0.0.1", "example.com:8443"]) {
      expect(normalizeIndexDomain(value)).toBeNull();
    }
  });

  it("accepts only public HTTPS page URLs and removes tracking fragments", () => {
    expect(normalizeIndexPageUrl("https://Example.com/docs?utm_source=test&id=7#section"))
      .toBe("https://example.com/docs?id=7");
    expect(normalizeIndexPageUrl("http://example.com/docs")).toBeNull();
    expect(normalizeIndexPageUrl("https://user:pass@example.com/docs")).toBeNull();
    expect(normalizeIndexPageUrl("https://127.0.0.1/admin")).toBeNull();
  });
});

describe("personal index listing", () => {
  it("maps compact page metadata and clamps pagination", async () => {
    const statements: Array<{ sql: string; values: unknown[] }> = [];
    const env = {
      DB: {
        prepare(sql: string) {
          const call = {
            sql, values: [] as unknown[],
            bind(...values: unknown[]) { this.values = values; return this; },
            first: async () => { statements.push({ sql, values: call.values }); return { total: 42 }; },
            all: async () => {
              statements.push({ sql, values: call.values });
              return { results: [{ id: 9, url: "https://example.com/a", domain: "example.com", title: "Guide", updated_at: "2026-11-18T00:00:00.000Z", content_chars: 840 }] };
            },
            run: async () => ({ meta: { changes: 1 } }),
          };
          return call;
        },
      },
    } as unknown as Env;

    const result = await listIndexedPages(env, { query: " GUIDE ", limit: 100, offset: 9000 });
    expect(result).toEqual({
      total: 42,
      pages: [{ id: 9, url: "https://example.com/a", domain: "example.com", title: "Guide", updatedAt: "2026-11-18T00:00:00.000Z", contentChars: 840 }],
    });
    expect(statements[0]?.values).toEqual(["guide", "%guide%", "%guide%", "%guide%"]);
    expect(statements[1]?.values).toEqual(["guide", "%guide%", "%guide%", "%guide%", 40, 5000]);
  });
});

describe("personal index deletion", () => {
  function makeEnv() {
    const statements: Array<{ sql: string; values: unknown[] }> = [];
    const db = {
      prepare(sql: string) {
        const call = {
          sql, values: [] as unknown[],
          bind(...values: unknown[]) { this.values = values; return this; },
          first: async () => null,
          all: async () => ({ results: [] }),
          run: async () => ({ meta: { changes: 1 } }),
        };
        statements.push(call);
        return call;
      },
      batch: vi.fn(async (batch: Array<{ sql: string; values: unknown[] }>) => {
        expect(batch).toHaveLength(3);
        return [
          { meta: { changes: 1 } },
          { meta: { changes: 2 } },
          { meta: { changes: 1 } },
        ];
      }),
    };
    return { env: { DB: db } as unknown as Env, db, statements };
  }

  it("deletes a page from FTS and base index and disables its watch", async () => {
    const { env, db, statements } = makeEnv();
    const result = await deleteIndexedContent(env, {
      kind: "url", value: "https://example.com/docs?utm_source=old#top",
    });
    expect(result).toEqual({
      pagesDeleted: 1, watchesDisabled: 2,
      target: { kind: "url", value: "https://example.com/docs" },
    });
    expect(db.batch).toHaveBeenCalledTimes(1);
    expect(statements[0]?.sql).toContain("DELETE FROM indexed_pages_fts");
    expect(statements[1]?.sql).toContain("UPDATE watches SET active = 0");
    expect(statements[2]?.sql).toContain("DELETE FROM indexed_pages WHERE normalized_url = ?");
    for (const statement of statements) expect(statement.values).toEqual(["https://example.com/docs"]);
  });

  it("removes the root domain, www and its subdomains using safe bound parameters", async () => {
    const { env, statements } = makeEnv();
    const result = await deleteIndexedContent(env, { kind: "domain", value: "WWW.Example.com" });
    expect(result.target).toEqual({ kind: "domain", value: "example.com" });
    expect(result.pagesDeleted).toBe(1);
    expect(statements[2]?.sql).toContain("lower(domain) LIKE ?");
    expect(statements[2]?.values).toEqual(["example.com", "www.example.com", "%.example.com"]);
  });

  it("rejects unsafe deletion targets before issuing database statements", async () => {
    const { env, db } = makeEnv();
    await expect(deleteIndexedContent(env, { kind: "url", value: "http://127.0.0.1/admin" })).rejects.toThrow();
    await expect(deleteIndexedContent(env, { kind: "domain", value: "localhost" })).rejects.toThrow();
    expect(db.batch).not.toHaveBeenCalled();
  });
});
