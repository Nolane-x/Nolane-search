import { afterEach, describe, expect, it, vi } from "vitest";
import { sendArchiveDocument } from "../src/telegram";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());

describe("Telegram archive document delivery", () => {
  it("returns the channel message and document references after a successful upload", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({
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
});
