import { afterEach, describe, expect, it, vi } from "vitest";
import { processUpdate } from "../src/index";
import { downloadTelegramFile, sendArchiveDocument, sendTelegramDocument } from "../src/telegram";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());

describe("Telegram archive document delivery", () => {
  it("returns the channel message and document references after a successful upload", async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL) => new Response(JSON.stringify({
      ok: true,
      result: {
        message_id: 91,
        document: {
          file_id: "telegram-file-reference",
          file_unique_id: "unique-file-reference",
          file_name: "snapshot.txt",
          file_size: 2048,
        },
      },
    }), { status: 200, headers: { "content-type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);
    const env = {
      TELEGRAM_BOT_TOKEN: "test-token",
      TELEGRAM_ARCHIVE_CHAT_ID: "-1001234567890",
    } as Env;

    const result = await sendArchiveDocument(env, "snapshot.txt", "snapshot body", "snapshot caption");

    expect(result).toEqual({
      messageId: 91,
      fileId: "telegram-file-reference",
      fileUniqueId: "unique-file-reference",
      fileName: "snapshot.txt",
      fileSize: 2048,
    });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(String(fetchMock.mock.calls[0]?.[0])).toContain("/sendDocument");
  });

  it("does not send when the archive channel is not configured", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const result = await sendArchiveDocument({} as Env, "snapshot.txt", "body", "caption");
    expect(result).toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("fails closed when Telegram confirms delivery without a document reference", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({
      ok: true, result: { message_id: 91 },
    }), { status: 200, headers: { "content-type": "application/json" } })));
    const env = { TELEGRAM_BOT_TOKEN: "test-token", TELEGRAM_ARCHIVE_CHAT_ID: "-100123" } as Env;
    await expect(sendArchiveDocument(env, "snapshot.txt", "body", "caption")).rejects.toThrow("document reference");
  });


  it("sends a JSON backup to the owner's private chat", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      expect(String(input)).toContain("/sendDocument");
      return new Response(JSON.stringify({
        ok: true,
        result: { message_id: 123, document: { file_id: "private-file-ref", file_name: "backup.json", file_size: 100 } },
      }), { status: 200, headers: { "content-type": "application/json" } });
    });
    vi.stubGlobal("fetch", fetchMock);
    const result = await sendTelegramDocument(
      { TELEGRAM_BOT_TOKEN: "test-token" } as Env,
      42,
      "backup.json",
      '{"format":"nolane-telegram-archive-index"}',
      "Private archive backup",
    );
    expect(result.messageId).toBe(123);
    expect(result.fileName).toBe("backup.json");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("downloads a Telegram file only after validating getFile metadata and caps the stream", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/getFile")) {
        return new Response(JSON.stringify({ ok: true, result: { file_path: "documents/archive-backup.json", file_size: 5 } }), {
          status: 200, headers: { "content-type": "application/json" },
        });
      }
      expect(url).toBe("https://api.telegram.org/file/bottest-token/documents/archive-backup.json");
      return new Response(new Uint8Array([1, 2, 3, 4, 5]), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    const bytes = await downloadTelegramFile({ TELEGRAM_BOT_TOKEN: "test-token" } as Env, "telegram-file-ref", 10);
    expect([...bytes]).toEqual([1, 2, 3, 4, 5]);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("rejects unsafe Telegram file paths before making a download request", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({
      ok: true, result: { file_path: "../secrets.json", file_size: 2 },
    }), { status: 200, headers: { "content-type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(downloadTelegramFile({ TELEGRAM_BOT_TOKEN: "test-token" } as Env, "file", 10))
      .rejects.toThrow("invalid file path");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("enforces the download cap while streaming when Telegram omits file_size", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      if (String(input).endsWith("/getFile")) {
        return new Response(JSON.stringify({ ok: true, result: { file_path: "documents/stream.json" } }), {
          status: 200, headers: { "content-type": "application/json" },
        });
      }
      return new Response(new Uint8Array(11), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    await expect(downloadTelegramFile({ TELEGRAM_BOT_TOKEN: "test-token" } as Env, "file", 10))
      .rejects.toThrow("exceeds the download size limit");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("rejects a Telegram file whose declared or streamed size exceeds the cap", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      if (String(input).endsWith("/getFile")) {
        return new Response(JSON.stringify({ ok: true, result: { file_path: "documents/large.json", file_size: 11 } }), {
          status: 200, headers: { "content-type": "application/json" },
        });
      }
      return new Response(new Uint8Array(11), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    await expect(downloadTelegramFile({ TELEGRAM_BOT_TOKEN: "test-token" } as Env, "file", 10))
      .rejects.toThrow("exceeds the download size limit");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});


describe("Telegram archive import update integration", () => {
  const payload = {
    format: "nolane-telegram-archive-index",
    version: 1,
    exportedAt: "2026-11-23T05:00:00.000Z",
    ownerUserId: "42",
    archiveChatId: "-1001234567890",
    count: 1,
    snapshots: [{
      watchId: 12,
      archiveMessageId: 991,
      telegramFileId: "archive-document-file-ref",
      telegramFileUniqueId: "archive-document-unique-ref",
      fileName: "snapshot.txt",
      fileSize: 120,
      url: "https://example.com/article",
      normalizedUrl: "https://example.com/article",
      title: "Example archive snapshot",
      contentHash: "a".repeat(64),
      captureKind: "initial",
      capturedAt: "2026-11-22T10:00:00.000Z",
      createdAt: 1795341600000,
    }],
  };

  function uploadUpdate(chatId = 42, chatType = "private", userId = 42) {
    return {
      update_id: 9001,
      message: {
        message_id: 9002,
        chat: { id: chatId, type: chatType },
        from: { id: userId, is_bot: false, first_name: "Owner" },
        caption: "/archive_import",
        document: {
          file_id: "private-backup-file-ref",
          file_unique_id: "private-backup-unique-ref",
          file_name: "nolane-archive-index.json",
          mime_type: "application/json",
          file_size: new TextEncoder().encode(JSON.stringify(payload)).byteLength,
        },
      },
    };
  }

  it("imports a private owner backup through processUpdate without creating a Tool Center job", async () => {
    const backupBytes = new TextEncoder().encode(JSON.stringify(payload));
    const prepared: Array<{ sql: string; values: unknown[] }> = [];
    const batches: Array<Array<{ sql: string; values: unknown[] }>> = [];
    const prepare = vi.fn((sql: string) => ({
      sql,
      values: [] as unknown[],
      bind(...values: unknown[]) {
        this.values = values;
        return this;
      },
      run: async () => {
        prepared.push({ sql, values: this.values });
        return { meta: { changes: 1 } };
      },
    }));
    const batch = vi.fn(async (statements: Array<{ sql: string; values: unknown[] }>) => {
      batches.push(statements);
      return statements.map(() => ({ meta: { changes: 1 } }));
    });
    const telegramMessages: Array<Record<string, unknown>> = [];
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/getFile")) {
        expect(JSON.parse(String(init?.body || "{}"))).toMatchObject({ file_id: "private-backup-file-ref" });
        return new Response(JSON.stringify({
          ok: true,
          result: { file_path: "documents/nolane-archive-index.json", file_size: backupBytes.byteLength },
        }), { status: 200, headers: { "content-type": "application/json" } });
      }
      if (url === "https://api.telegram.org/file/bottest-token/documents/nolane-archive-index.json") {
        return new Response(backupBytes, { status: 200 });
      }
      if (url.endsWith("/sendMessage")) {
        const body = JSON.parse(String(init?.body || "{}")) as Record<string, unknown>;
        telegramMessages.push(body);
        return new Response(JSON.stringify({ ok: true, result: { message_id: 9003 } }), {
          status: 200, headers: { "content-type": "application/json" },
        });
      }
      throw new Error("Unexpected request " + url);
    });
    vi.stubGlobal("fetch", fetchMock);

    const env = {
      TELEGRAM_BOT_TOKEN: "test-token",
      TELEGRAM_ARCHIVE_CHAT_ID: "-1001234567890",
      ALLOWED_TELEGRAM_USER_IDS: "42",
      DB: { prepare, batch },
    } as unknown as Env;

    await processUpdate(env, uploadUpdate() as never);

    expect(prepare.mock.calls.map(call => call[0])).toContain(
      "INSERT OR IGNORE INTO telegram_updates (update_id) VALUES (?)",
    );
    expect(batches).toHaveLength(1);
    expect(batches[0]).toHaveLength(1);
    expect(batches[0]?.[0]?.sql).toContain("INSERT OR IGNORE INTO archive_snapshots");
    expect(batches[0]?.[0]?.values).toEqual([
      12, "42", "42", "-1001234567890", 991, "archive-document-file-ref",
      "archive-document-unique-ref", "snapshot.txt", 120,
      "https://example.com/article", "https://example.com/article",
      "Example archive snapshot", "a".repeat(64), "initial",
      "2026-11-22T10:00:00.000Z", 1795341600000,
    ]);
    expect(telegramMessages).toHaveLength(1);
    expect(String(telegramMessages[0]?.text)).toContain("Nhập mới: <b>1</b>");
    expect(String(telegramMessages[0]?.text)).toContain("Bỏ qua trùng lặp: <b>0</b>");
    expect(fetchMock.mock.calls.some(call => String(call[0]).includes("/createToolJob"))).toBe(false);
    expect(batches.flat().some(statement => statement.sql.includes("tool_jobs"))).toBe(false);
  });

  it("does not download or import an archive backup sent outside the owner's private chat", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/sendMessage")) {
        return new Response(JSON.stringify({ ok: true, result: { message_id: 9004 } }), {
          status: 200, headers: { "content-type": "application/json" },
        });
      }
      throw new Error("Unexpected request " + url);
    });
    vi.stubGlobal("fetch", fetchMock);
    const batch = vi.fn();
    const env = {
      TELEGRAM_BOT_TOKEN: "test-token",
      TELEGRAM_ARCHIVE_CHAT_ID: "-1001234567890",
      ALLOWED_TELEGRAM_USER_IDS: "42",
      DB: {
        prepare: () => ({
          bind: () => ({ run: async () => ({ meta: { changes: 1 } }) }),
        }),
        batch,
      },
    } as unknown as Env;

    await processUpdate(env, uploadUpdate(-100123, "supergroup") as never);

    expect(fetchMock.mock.calls.some(call => String(call[0]).endsWith("/getFile"))).toBe(false);
    expect(batch).not.toHaveBeenCalled();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("does not download or import an archive backup from a non-allowlisted Telegram user", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/sendMessage")) {
        return new Response(JSON.stringify({ ok: true, result: { message_id: 9005 } }), {
          status: 200, headers: { "content-type": "application/json" },
        });
      }
      throw new Error("Unexpected request " + url);
    });
    vi.stubGlobal("fetch", fetchMock);
    const batch = vi.fn();
    const env = {
      TELEGRAM_BOT_TOKEN: "test-token",
      TELEGRAM_ARCHIVE_CHAT_ID: "-1001234567890",
      ALLOWED_TELEGRAM_USER_IDS: "99",
      DB: {
        prepare: () => ({
          bind: () => ({ run: async () => ({ meta: { changes: 1 } }) }),
        }),
        batch,
      },
    } as unknown as Env;

    await processUpdate(env, uploadUpdate() as never);

    expect(fetchMock.mock.calls.some(call => String(call[0]).endsWith("/getFile"))).toBe(false);
    expect(batch).not.toHaveBeenCalled();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
