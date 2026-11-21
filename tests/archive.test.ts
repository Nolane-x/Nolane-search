import { describe, expect, it, vi } from "vitest";
import {
  formatArchiveSnapshotList,
  getArchiveSnapshot,
  listArchiveSnapshots,
  parseArchivePageArguments,
  saveArchiveSnapshot,
} from "../src/archive";
import type { ArchiveSnapshot } from "../src/archive";
import type { Env } from "../src/types";

const row = {
  id: 17,
  watch_id: 4,
  user_id: "42",
  chat_id: "42",
  archive_chat_id: "-1001234567890",
  archive_message_id: 91,
  telegram_file_id: "telegram-file-reference",
  telegram_file_unique_id: "unique-file-reference",
  file_name: "nolane-4-snapshot.txt",
  file_size: 2048,
  url: "https://example.com/docs",
  normalized_url: "https://example.com/docs",
  title: "Nolane <Research> & Search",
  content_hash: "a".repeat(64),
  capture_kind: "change" as const,
  captured_at: "2026-11-21T08:00:00.000Z",
  created_at: 1795267200000,
};

const input = {
  watchId: 4,
  userId: "42",
  chatId: "42",
  archiveChatId: "-1001234567890",
  archiveMessageId: 91,
  telegramFileId: "telegram-file-reference",
  telegramFileUniqueId: "unique-file-reference",
  fileName: "nolane-4-snapshot.txt",
  fileSize: 2048,
  url: "https://example.com/docs",
  normalizedUrl: "https://example.com/docs",
  title: "Nolane Research & Search",
  contentHash: "a".repeat(64),
  captureKind: "change" as const,
  capturedAt: "2026-11-21T08:00:00.000Z",
};

function archiveSnapshot(overrides: Partial<ArchiveSnapshot> = {}): ArchiveSnapshot {
  return {
    id: row.id,
    watchId: row.watch_id,
    userId: row.user_id,
    chatId: row.chat_id,
    archiveChatId: row.archive_chat_id,
    archiveMessageId: row.archive_message_id,
    telegramFileId: row.telegram_file_id,
    telegramFileUniqueId: row.telegram_file_unique_id,
    fileName: row.file_name,
    fileSize: row.file_size,
    url: row.url,
    normalizedUrl: row.normalized_url,
    title: row.title,
    contentHash: row.content_hash,
    captureKind: row.capture_kind,
    capturedAt: row.captured_at,
    createdAt: row.created_at,
    ...overrides,
  };
}

function envWithStatement(statement: Record<string, unknown>): Env {
  return { DB: { prepare: () => statement } } as unknown as Env;
}

describe("Telegram archive index", () => {
  it("stores Telegram message references and metadata, not snapshot bytes", async () => {
    const statement = {
      bind: vi.fn().mockReturnThis(),
      first: vi.fn().mockResolvedValue({ id: 23 }),
    };
    const env = envWithStatement(statement);
    const id = await saveArchiveSnapshot(env, input);

    expect(id).toBe(23);
    expect(statement.bind).toHaveBeenCalledWith(
      4, "42", "42", "-1001234567890", 91, "telegram-file-reference",
      "unique-file-reference", "nolane-4-snapshot.txt", 2048,
      "https://example.com/docs", "https://example.com/docs", "Nolane Research & Search",
      "a".repeat(64), "change", "2026-11-21T08:00:00.000Z", expect.any(Number),
    );
    expect(String(statement.bind.mock.calls[0]?.join(" "))).not.toContain("snapshot page body");
  });

  it("rejects invalid hashes and message IDs before writing", async () => {
    const prepare = vi.fn();
    const env = { DB: { prepare } } as unknown as Env;
    await expect(saveArchiveSnapshot(env, { ...input, contentHash: "not-a-hash" })).rejects.toThrow("content hash");
    await expect(saveArchiveSnapshot(env, { ...input, archiveMessageId: 0 })).rejects.toThrow("IDs");
    expect(prepare).not.toHaveBeenCalled();
  });

  it("searches only the owner's snapshots and escapes SQL LIKE wildcards", async () => {
    const countStatement = {
      bind: vi.fn().mockReturnThis(),
      first: vi.fn().mockResolvedValue({ total: 1 }),
    };
    const rowsStatement = {
      bind: vi.fn().mockReturnThis(),
      all: vi.fn().mockResolvedValue({ results: [row] }),
    };
    const prepare = vi.fn((sql: string) => sql.includes("COUNT(*)") ? countStatement : rowsStatement);
    const env = { DB: { prepare } } as unknown as Env;
    const result = await listArchiveSnapshots(env, "42", "Nolane_%", 50, -10);

    expect(result.total).toBe(1);
    expect(result.snapshots[0]?.id).toBe(17);
    expect(result.snapshots[0]?.archiveMessageId).toBe(91);
    expect(countStatement.bind).toHaveBeenCalledWith("42", "%Nolane\\_\\%%", "%Nolane\\_\\%%");
    expect(rowsStatement.bind).toHaveBeenCalledWith("42", "%Nolane\\_\\%%", "%Nolane\\_\\%%", 20, 0);
    expect(prepare.mock.calls[0]?.[0]).toContain("user_id = ?");
  });

  it("never returns a snapshot belonging to another Telegram user", async () => {
    const statement = {
      bind: vi.fn().mockReturnThis(),
      first: vi.fn().mockResolvedValue(null),
    };
    const env = envWithStatement(statement);
    await expect(getArchiveSnapshot(env, 17, "99")).resolves.toBeNull();
    expect(statement.bind).toHaveBeenCalledWith(17, "99");
  });

  it("parses safe archive page arguments and normalizes query whitespace", () => {
    expect(parseArchivePageArguments("2   climate   policy")).toEqual({ page: 2, query: "climate policy" });
    expect(parseArchivePageArguments("1")).toEqual({ page: 1, query: "" });
    expect(parseArchivePageArguments("0")).toBeNull();
    expect(parseArchivePageArguments("1002")).toBeNull();
    expect(parseArchivePageArguments("page 2")).toBeNull();
    expect(parseArchivePageArguments("2 " + "x".repeat(121))).toBeNull();
  });

  it("includes safe previous/next page commands and carries the search query forward", () => {
    const snapshots = Array.from({ length: 5 }, (_, index) =>
      archiveSnapshot({ id: 20 + index, title: "Archive item " + (index + 1) }),
    );
    const output = formatArchiveSnapshotList(snapshots, 12, "<climate>", 2, 5);
    expect(output).toContain("Trang 2 / 3");
    expect(output).toContain("Hiển thị 6–10 / 12 mục.");
    expect(output).toContain("/archive_page 1 &lt;climate&gt;");
    expect(output).toContain("/archive_page 3 &lt;climate&gt;");
    expect(output).not.toContain("<climate>");
  });

  it("shows only the forward command on the first page", () => {
    const snapshots = Array.from({ length: 5 }, (_, index) =>
      archiveSnapshot({ id: 30 + index }),
    );
    const output = formatArchiveSnapshotList(snapshots, 8, "", 1, 5);
    expect(output).toContain("/archive_page 2");
    expect(output).not.toContain("/archive_page 0");
  });

  it("escapes titles, URLs and user queries in Telegram HTML", () => {
    const snapshot: ArchiveSnapshot = {
      id: 17, watchId: 4, userId: "42", chatId: "42", archiveChatId: "-1001234567890",
      archiveMessageId: 91, telegramFileId: "file-ref", telegramFileUniqueId: null,
      fileName: "snapshot.txt", fileSize: 2048, url: "https://example.com/?a=1&b=<x>",
      normalizedUrl: "https://example.com/", title: "Title <script> & text",
      contentHash: "a".repeat(64), captureKind: "initial", capturedAt: "2026-11-21T08:00:00.000Z",
      createdAt: 1,
    };
    const output = formatArchiveSnapshotList([snapshot], 1, "<archive>");
    expect(output).toContain("&lt;script&gt;");
    expect(output).toContain("&amp;");
    expect(output).toContain("&lt;archive&gt;");
    expect(output).not.toContain("<script>");
    expect(output).toContain("/archive_restore 17");
    expect(output).toContain("snapshot.txt");
    expect(output).toContain("2.0 KB");
    expect(output).toContain("SHA-256");
    expect(output).toContain("aaaaaaaaaaaaaaaa…");
  });
});
