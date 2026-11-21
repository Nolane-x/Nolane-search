import { afterEach, describe, expect, it, vi } from "vitest";
import { checkWatchTargets } from "../src/watch";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());

describe("watch snapshot archive indexing", () => {
  it("indexes the Telegram channel message only after document upload succeeds", async () => {
    const watch = {
      id: 12,
      chat_id: "42",
      user_id: "42",
      url: "https://example.com/docs",
      normalized_url: "https://example.com/docs",
      interval_minutes: 30,
      etag: null,
      last_modified: null,
      content_hash: null,
    };
    const prepared: Array<{ sql: string; values: unknown[] }> = [];
    const prepare = vi.fn((sql: string) => {
      const statement = {
        values: [] as unknown[],
        bind(...values: unknown[]) {
          this.values = values;
          return this;
        },
        all: async () => ({ results: sql.includes("FROM watches") ? [watch] : [] }),
        first: async () => {
          if (sql.includes("SELECT id FROM indexed_pages")) return null;
          if (sql.includes("INSERT INTO archive_snapshots")) return { id: 77 };
          return null;
        },
        run: async () => ({ meta: { changes: 1 } }),
      };
      const originalBind = statement.bind.bind(statement);
      statement.bind = (...values: unknown[]) => {
        originalBind(...values);
        prepared.push({ sql, values });
        return statement;
      };
      return statement;
    });
    const batch = vi.fn(async () => []);
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/robots.txt")) {
        return new Response("User-agent: *\nAllow: /", {
          status: 200,
          headers: { "content-type": "text/plain" },
        });
      }
      if (url === "https://example.com/docs") {
        return new Response(
          "<html><head><title>Archive test page</title></head><body><main>Body from the monitored site that should be uploaded to the Telegram archive as a text document.</main></body></html>",
          { status: 200, headers: { "content-type": "text/html; charset=utf-8" } },
        );
      }
      if (url.includes("/sendDocument")) {
        return new Response(JSON.stringify({
          ok: true,
          result: {
            message_id: 991,
            document: {
              file_id: "telegram-file-id-991",
              file_unique_id: "telegram-file-unique-id-991",
              file_name: "nolane-12-snapshot.txt",
              file_size: 300,
            },
          },
        }), { status: 200, headers: { "content-type": "application/json" } });
      }
      throw new Error("Unexpected request " + url);
    });
    vi.stubGlobal("fetch", fetchMock);

    const env = {
      DB: { prepare, batch },
      TELEGRAM_BOT_TOKEN: "test-token",
      TELEGRAM_ARCHIVE_CHAT_ID: "-1001234567890",
    } as unknown as Env;

    const result = await checkWatchTargets(env);

    expect(result).toEqual({ checked: 1, changed: 0 });
    expect(fetchMock.mock.calls.some(call => String(call[0]).includes("/sendDocument"))).toBe(true);
    const archiveInsert = prepared.find(entry => entry.sql.includes("INSERT INTO archive_snapshots"));
    expect(archiveInsert).toBeDefined();
    expect(archiveInsert?.values).toContain("-1001234567890");
    expect(archiveInsert?.values).toContain(991);
    expect(archiveInsert?.values).toContain("telegram-file-id-991");
    expect(archiveInsert?.values).toContain("Archive test page");
    expect(archiveInsert?.values).not.toContain("Body from the monitored site");
  });
});
