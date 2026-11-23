import { afterEach, describe, expect, it, vi } from "vitest";
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
