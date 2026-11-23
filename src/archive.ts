import { htmlEscape } from "./security";
import type { Env } from "./types";

export interface ArchiveSnapshot {
  id: number;
  watchId: number;
  userId: string;
  chatId: string;
  archiveChatId: string;
  archiveMessageId: number;
  telegramFileId: string;
  telegramFileUniqueId: string | null;
  fileName: string;
  fileSize: number | null;
  url: string;
  normalizedUrl: string;
  title: string;
  contentHash: string;
  captureKind: "initial" | "change";
  capturedAt: string;
  createdAt: number;
}


export interface ArchiveBackupEntry {
  watchId: number;
  archiveMessageId: number;
  telegramFileId: string;
  telegramFileUniqueId: string | null;
  fileName: string;
  fileSize: number | null;
  url: string;
  normalizedUrl: string;
  title: string;
  contentHash: string;
  captureKind: "initial" | "change";
  capturedAt: string;
  createdAt: number;
}

export interface ArchiveBackupPayload {
  format: "nolane-telegram-archive-index";
  version: 1;
  exportedAt: string;
  ownerUserId: string;
  archiveChatId: string;
  count: number;
  snapshots: ArchiveBackupEntry[];
}

export const MAX_ARCHIVE_BACKUP_ROWS = 2000;
export const MAX_ARCHIVE_BACKUP_BYTES = 5 * 1024 * 1024;
const ARCHIVE_BACKUP_PAGE_SIZE = 200;

function validPublicHttpsUrl(value: unknown, label: string): string {
  if (typeof value !== "string" || !value.trim() || value.length > 2048) {
    throw new Error("Archive backup " + label + " is invalid.");
  }
  let parsed: URL;
  try { parsed = new URL(value); }
  catch { throw new Error("Archive backup " + label + " is invalid."); }
  if (parsed.protocol !== "https:" || parsed.username || parsed.password || !parsed.hostname) {
    throw new Error("Archive backup " + label + " must be a public HTTPS URL without credentials.");
  }
  return value;
}

function validateArchiveBackupEntry(value: unknown): ArchiveBackupEntry {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("Archive backup contains an invalid snapshot record.");
  }
  const item = value as Record<string, unknown>;
  const text = (field: string, max: number): string => {
    const candidate = item[field];
    if (typeof candidate !== "string" || !candidate.trim() || candidate.length > max) {
      throw new Error("Archive backup snapshot field " + field + " is invalid.");
    }
    return candidate;
  };
  const positiveInt = (field: string): number => {
    const candidate = item[field];
    if (typeof candidate !== "number" || !Number.isSafeInteger(candidate) || candidate <= 0) {
      throw new Error("Archive backup snapshot field " + field + " is invalid.");
    }
    return candidate;
  };
  const watchId = positiveInt("watchId");
  const archiveMessageId = positiveInt("archiveMessageId");
  const telegramFileId = text("telegramFileId", 2048);
  const fileName = text("fileName", 255);
  if (/[\\/\u0000-\u001f\u007f]/.test(fileName) || fileName === "." || fileName === "..") {
    throw new Error("Archive backup file name is invalid.");
  }
  const telegramFileUniqueId = item.telegramFileUniqueId;
  if (telegramFileUniqueId !== null &&
      (typeof telegramFileUniqueId !== "string" || !telegramFileUniqueId.trim() || telegramFileUniqueId.length > 256)) {
    throw new Error("Archive backup Telegram unique file reference is invalid.");
  }
  const fileSize = item.fileSize;
  if (fileSize !== null && (typeof fileSize !== "number" || !Number.isSafeInteger(fileSize) || fileSize < 0)) {
    throw new Error("Archive backup file size is invalid.");
  }
  const title = text("title", 240);
  const contentHash = text("contentHash", 64);
  if (!/^[a-f0-9]{64}$/i.test(contentHash)) throw new Error("Archive backup SHA-256 hash is invalid.");
  const captureKind = item.captureKind;
  if (captureKind !== "initial" && captureKind !== "change") {
    throw new Error("Archive backup capture kind is invalid.");
  }
  const capturedAt = text("capturedAt", 64);
  if (!Number.isFinite(Date.parse(capturedAt))) throw new Error("Archive backup capture time is invalid.");
  const createdAt = item.createdAt;
  if (typeof createdAt !== "number" || !Number.isSafeInteger(createdAt) || createdAt <= 0) {
    throw new Error("Archive backup creation time is invalid.");
  }
  return {
    watchId,
    archiveMessageId,
    telegramFileId,
    telegramFileUniqueId: telegramFileUniqueId as string | null,
    fileName,
    fileSize: fileSize as number | null,
    url: validPublicHttpsUrl(item.url, "URL"),
    normalizedUrl: validPublicHttpsUrl(item.normalizedUrl, "normalized URL"),
    title,
    contentHash: contentHash.toLowerCase(),
    captureKind,
    capturedAt,
    createdAt,
  };
}

/** Parse and validate a private, versioned metadata-only archive backup. */
export function parseArchiveBackup(
  content: string,
  ownerUserId: string,
  archiveChatId: string,
): ArchiveBackupPayload {
  requireText(ownerUserId, "owner user ID", 64);
  requireText(archiveChatId, "archive chat ID", 64);
  if (typeof content !== "string" || new TextEncoder().encode(content).byteLength > MAX_ARCHIVE_BACKUP_BYTES) {
    throw new Error("Archive backup exceeds the 5 MiB import limit.");
  }
  let value: unknown;
  try { value = JSON.parse(content); }
  catch { throw new Error("Archive backup is not valid JSON."); }
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("Archive backup root must be a JSON object.");
  }
  const backup = value as Record<string, unknown>;
  if (backup.format !== "nolane-telegram-archive-index" || backup.version !== 1) {
    throw new Error("Unsupported archive backup format or version.");
  }
  if (backup.ownerUserId !== ownerUserId) {
    throw new Error("Archive backup belongs to a different Telegram owner.");
  }
  if (backup.archiveChatId !== archiveChatId) {
    throw new Error("Archive backup belongs to a different Telegram archive channel.");
  }
  if (typeof backup.exportedAt !== "string" || !Number.isFinite(Date.parse(backup.exportedAt))) {
    throw new Error("Archive backup export timestamp is invalid.");
  }
  if (!Array.isArray(backup.snapshots) || backup.snapshots.length > MAX_ARCHIVE_BACKUP_ROWS) {
    throw new Error("Archive backup record count is invalid or exceeds the safety limit.");
  }
  if (backup.count !== backup.snapshots.length) {
    throw new Error("Archive backup record count does not match its contents.");
  }
  const snapshots = backup.snapshots.map(validateArchiveBackupEntry);
  const messageIds = new Set<number>();
  for (const snapshot of snapshots) {
    if (messageIds.has(snapshot.archiveMessageId)) {
      throw new Error("Archive backup contains duplicate Telegram message IDs.");
    }
    messageIds.add(snapshot.archiveMessageId);
  }
  return {
    format: "nolane-telegram-archive-index",
    version: 1,
    exportedAt: backup.exportedAt,
    ownerUserId,
    archiveChatId,
    count: snapshots.length,
    snapshots,
  };
}

/** Export only the current owner's metadata references; page bodies remain in Telegram. */
export async function createArchiveBackup(
  env: Env,
  ownerUserId: string,
  archiveChatId: string,
): Promise<{ fileName: string; content: string; count: number }> {
  requireText(ownerUserId, "owner user ID", 64);
  requireText(archiveChatId, "archive chat ID", 64);
  const countRow = await env.DB.prepare(
    "SELECT COUNT(*) AS total FROM archive_snapshots WHERE user_id = ? AND archive_chat_id = ?",
  ).bind(ownerUserId, archiveChatId).first<{ total: number }>();
  const total = Math.max(0, Number(countRow?.total) || 0);
  if (total > MAX_ARCHIVE_BACKUP_ROWS) {
    throw new Error("Archive contains more than 2,000 records. Export paging is required before a full backup can be created.");
  }
  const snapshots: ArchiveBackupEntry[] = [];
  for (let offset = 0; offset < total; offset += ARCHIVE_BACKUP_PAGE_SIZE) {
    const result = await env.DB.prepare(
      "SELECT watch_id, archive_message_id, telegram_file_id, telegram_file_unique_id, " +
        "file_name, file_size, url, normalized_url, title, content_hash, capture_kind, captured_at, created_at " +
        "FROM archive_snapshots WHERE user_id = ? AND archive_chat_id = ? " +
        "ORDER BY captured_at ASC, id ASC LIMIT ? OFFSET ?",
    ).bind(ownerUserId, archiveChatId, ARCHIVE_BACKUP_PAGE_SIZE, offset).all<ArchiveSnapshotRow>();
    for (const row of result.results || []) {
      snapshots.push({
        watchId: Number(row.watch_id),
        archiveMessageId: Number(row.archive_message_id),
        telegramFileId: String(row.telegram_file_id),
        telegramFileUniqueId: row.telegram_file_unique_id === null ? null : String(row.telegram_file_unique_id),
        fileName: String(row.file_name),
        fileSize: row.file_size === null ? null : Number(row.file_size),
        url: String(row.url),
        normalizedUrl: String(row.normalized_url),
        title: String(row.title),
        contentHash: String(row.content_hash),
        captureKind: row.capture_kind,
        capturedAt: String(row.captured_at),
        createdAt: Number(row.created_at),
      });
    }
  }
  if (snapshots.length !== total) throw new Error("Archive changed while the backup was being created. Retry the export.");
  const payload: ArchiveBackupPayload = {
    format: "nolane-telegram-archive-index",
    version: 1,
    exportedAt: new Date().toISOString(),
    ownerUserId,
    archiveChatId,
    count: snapshots.length,
    snapshots,
  };
  const content = JSON.stringify(payload, null, 2) + "\n";
  if (new TextEncoder().encode(content).byteLength > MAX_ARCHIVE_BACKUP_BYTES) {
    throw new Error("Archive metadata backup exceeds the 5 MiB file limit.");
  }
  const date = payload.exportedAt.replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
  return {
    fileName: "nolane-archive-index-" + date + ".json",
    content,
    count: snapshots.length,
  };
}

/** Restore only owner-scoped index rows; duplicate Telegram channel/message pairs are skipped. */
export async function importArchiveBackup(
  env: Env,
  content: string,
  ownerUserId: string,
  archiveChatId: string,
): Promise<{ imported: number; skipped: number; total: number }> {
  const backup = parseArchiveBackup(content, ownerUserId, archiveChatId);
  let imported = 0;
  for (let offset = 0; offset < backup.snapshots.length; offset += 100) {
    const batch = backup.snapshots.slice(offset, offset + 100).map(snapshot =>
      env.DB.prepare(
        "INSERT OR IGNORE INTO archive_snapshots (" +
          "watch_id, user_id, chat_id, archive_chat_id, archive_message_id, telegram_file_id, " +
          "telegram_file_unique_id, file_name, file_size, url, normalized_url, title, content_hash, " +
          "capture_kind, captured_at, created_at" +
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ).bind(
        snapshot.watchId,
        ownerUserId,
        ownerUserId,
        archiveChatId,
        snapshot.archiveMessageId,
        snapshot.telegramFileId,
        snapshot.telegramFileUniqueId,
        snapshot.fileName,
        snapshot.fileSize,
        snapshot.url,
        snapshot.normalizedUrl,
        snapshot.title,
        snapshot.contentHash,
        snapshot.captureKind,
        snapshot.capturedAt,
        snapshot.createdAt,
      ),
    );
    const results = await env.DB.batch(batch);
    imported += results.reduce((sum, result) => sum + Math.max(0, Number(result.meta?.changes) || 0), 0);
  }
  return { imported, skipped: backup.count - imported, total: backup.count };
}

export interface SaveArchiveSnapshotInput {
  watchId: number;
  userId: string;
  chatId: string;
  archiveChatId: string;
  archiveMessageId: number;
  telegramFileId: string;
  telegramFileUniqueId?: string | null;
  fileName: string;
  fileSize?: number | null;
  url: string;
  normalizedUrl: string;
  title: string;
  contentHash: string;
  captureKind: "initial" | "change";
  capturedAt: string;
}

/** Telegram message size remains bounded by keeping archive pages compact. */
export const ARCHIVE_PAGE_SIZE = 5;
export const MAX_ARCHIVE_PAGE = 1001; // listArchiveSnapshots deliberately caps offset at 5,000.

/** Parse: /archive_page PAGE [query]. Invalid or out-of-range input returns null. */
export function parseArchivePageArguments(input: string): { page: number; query: string } | null {
  const match = input.trim().match(/^(\d{1,4})(?:\s+([\s\S]*))?$/);
  if (!match) return null;
  const page = Number(match[1]);
  const query = (match[2] || "").trim().replace(/\s+/g, " ");
  if (!Number.isSafeInteger(page) || page < 1 || page > MAX_ARCHIVE_PAGE || query.length > 120) return null;
  return { page, query };
}

interface ArchiveSnapshotRow {
  id: number;
  watch_id: number;
  user_id: string;
  chat_id: string;
  archive_chat_id: string;
  archive_message_id: number;
  telegram_file_id: string;
  telegram_file_unique_id: string | null;
  file_name: string;
  file_size: number | null;
  url: string;
  normalized_url: string;
  title: string;
  content_hash: string;
  capture_kind: "initial" | "change";
  captured_at: string;
  created_at: number;
}

function requireText(value: string, label: string, maxLength: number): void {
  if (typeof value !== "string" || !value.trim() || value.length > maxLength) {
    throw new Error("Archive snapshot " + label + " is invalid.");
  }
}

function mapSnapshot(row: ArchiveSnapshotRow): ArchiveSnapshot {
  return {
    id: Number(row.id),
    watchId: Number(row.watch_id),
    userId: String(row.user_id),
    chatId: String(row.chat_id),
    archiveChatId: String(row.archive_chat_id),
    archiveMessageId: Number(row.archive_message_id),
    telegramFileId: String(row.telegram_file_id),
    telegramFileUniqueId: row.telegram_file_unique_id === null ? null : String(row.telegram_file_unique_id),
    fileName: String(row.file_name),
    fileSize: row.file_size === null ? null : Number(row.file_size),
    url: String(row.url),
    normalizedUrl: String(row.normalized_url),
    title: String(row.title),
    contentHash: String(row.content_hash),
    captureKind: row.capture_kind,
    capturedAt: String(row.captured_at),
    createdAt: Number(row.created_at),
  };
}

/** Store only a Telegram message reference and searchable metadata; never store snapshot bytes in D1. */
export async function saveArchiveSnapshot(env: Env, input: SaveArchiveSnapshotInput): Promise<number> {
  if (!Number.isSafeInteger(input.watchId) || input.watchId <= 0 ||
      !Number.isSafeInteger(input.archiveMessageId) || input.archiveMessageId <= 0) {
    throw new Error("Archive snapshot IDs are invalid.");
  }
  requireText(input.userId, "user ID", 64);
  requireText(input.chatId, "chat ID", 64);
  requireText(input.archiveChatId, "archive chat ID", 64);
  requireText(input.telegramFileId, "Telegram file reference", 2048);
  requireText(input.fileName, "file name", 255);
  requireText(input.url, "URL", 2048);
  requireText(input.normalizedUrl, "normalized URL", 2048);
  requireText(input.title, "title", 240);
  if (!/^[a-f0-9]{64}$/i.test(input.contentHash)) throw new Error("Archive snapshot content hash is invalid.");
  if (input.captureKind !== "initial" && input.captureKind !== "change") {
    throw new Error("Archive snapshot capture kind is invalid.");
  }
  if (!Number.isFinite(Date.parse(input.capturedAt))) throw new Error("Archive snapshot capture time is invalid.");
  if (input.fileSize !== undefined && input.fileSize !== null &&
      (!Number.isSafeInteger(input.fileSize) || input.fileSize < 0)) {
    throw new Error("Archive snapshot file size is invalid.");
  }

  const row = await env.DB.prepare(
    "INSERT INTO archive_snapshots (" +
      "watch_id, user_id, chat_id, archive_chat_id, archive_message_id, telegram_file_id, " +
      "telegram_file_unique_id, file_name, file_size, url, normalized_url, title, content_hash, " +
      "capture_kind, captured_at, created_at" +
    ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id",
  ).bind(
    input.watchId,
    input.userId,
    input.chatId,
    input.archiveChatId,
    input.archiveMessageId,
    input.telegramFileId,
    input.telegramFileUniqueId || null,
    input.fileName,
    input.fileSize ?? null,
    input.url,
    input.normalizedUrl,
    input.title,
    input.contentHash.toLowerCase(),
    input.captureKind,
    input.capturedAt,
    Date.now(),
  ).first<{ id: number }>();

  if (!row || !Number.isSafeInteger(Number(row.id)) || Number(row.id) <= 0) {
    throw new Error("Archive snapshot index insert did not return an ID.");
  }
  return Number(row.id);
}

function escapeLike(value: string): string {
  return value.replace(/[\\%_]/g, (character) => "\\" + character);
}

export async function listArchiveSnapshots(
  env: Env,
  userId: string,
  query = "",
  limit = 10,
  offset = 0,
): Promise<{ snapshots: ArchiveSnapshot[]; total: number }> {
  requireText(userId, "user ID", 64);
  const boundedLimit = Math.max(1, Math.min(20, Math.floor(limit) || 10));
  const boundedOffset = Math.max(0, Math.min(5000, Math.floor(offset) || 0));
  const normalizedQuery = query.trim().slice(0, 120);
  const where = normalizedQuery
    ? " AND (LOWER(title) LIKE LOWER(?) ESCAPE '\\' OR LOWER(url) LIKE LOWER(?) ESCAPE '\\')"
    : "";
  const pattern = normalizedQuery ? "%" + escapeLike(normalizedQuery) + "%" : "";
  const baseBindings: unknown[] = [userId];
  if (normalizedQuery) baseBindings.push(pattern, pattern);

  const [count, rows] = await Promise.all([
    env.DB.prepare("SELECT COUNT(*) AS total FROM archive_snapshots WHERE user_id = ?" + where)
      .bind(...baseBindings).first<{ total: number }>(),
    env.DB.prepare(
      "SELECT id, watch_id, user_id, chat_id, archive_chat_id, archive_message_id, " +
        "telegram_file_id, telegram_file_unique_id, file_name, file_size, url, normalized_url, " +
        "title, content_hash, capture_kind, captured_at, created_at " +
        "FROM archive_snapshots WHERE user_id = ?" + where +
        " ORDER BY captured_at DESC, id DESC LIMIT ? OFFSET ?",
    ).bind(...baseBindings, boundedLimit, boundedOffset).all<ArchiveSnapshotRow>(),
  ]);

  return {
    snapshots: (rows.results || []).map(mapSnapshot),
    total: Math.max(0, Number(count?.total) || 0),
  };
}

export async function getArchiveSnapshot(
  env: Env,
  snapshotId: number,
  userId: string,
): Promise<ArchiveSnapshot | null> {
  if (!Number.isSafeInteger(snapshotId) || snapshotId <= 0) return null;
  requireText(userId, "user ID", 64);
  const row = await env.DB.prepare(
    "SELECT id, watch_id, user_id, chat_id, archive_chat_id, archive_message_id, " +
      "telegram_file_id, telegram_file_unique_id, file_name, file_size, url, normalized_url, " +
      "title, content_hash, capture_kind, captured_at, created_at " +
      "FROM archive_snapshots WHERE id = ? AND user_id = ? LIMIT 1",
  ).bind(snapshotId, userId).first<ArchiveSnapshotRow>();
  return row ? mapSnapshot(row) : null;
}

function formatArchiveFileSize(size: number | null): string {
  if (size === null || !Number.isSafeInteger(size) || size < 0) return "không rõ dung lượng";
  if (size < 1024) return size + " B";
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + " KB";
  return (size / (1024 * 1024)).toFixed(2) + " MB";
}

export function formatArchiveSnapshotList(
  snapshots: ArchiveSnapshot[],
  total: number,
  query = "",
  page = 1,
  pageSize = ARCHIVE_PAGE_SIZE,
): string {
  const safePage = Math.max(1, Math.floor(page) || 1);
  const safePageSize = Math.max(1, Math.min(20, Math.floor(pageSize) || ARCHIVE_PAGE_SIZE));
  const safeTotal = Math.max(0, Math.floor(total) || 0);
  const pageCount = Math.max(1, Math.ceil(safeTotal / safePageSize));
  if (!snapshots.length) {
    return query
      ? "<b>Nolane Archive</b>\nKhông tìm thấy snapshot khớp với <code>" + htmlEscape(query.slice(0, 120)) + "</code>."
      : "<b>Nolane Archive</b>\nChưa có snapshot website nào được lưu. Hãy cấu hình <code>TELEGRAM_ARCHIVE_CHAT_ID</code> và tạo một watch bằng <code>/watch URL</code>.";
  }
  const lines = [
    "<b>Nolane Archive</b> · " + safeTotal + " snapshot" + (query ? " phù hợp" : ""),
    query ? "Từ khóa: <code>" + htmlEscape(query.slice(0, 120)) + "</code>" : "Các snapshot mới nhất",
    "Trang " + safePage + " / " + pageCount,
    "",
  ];
  for (const snapshot of snapshots) {
    const title = htmlEscape(snapshot.title.slice(0, 100));
    const url = htmlEscape(snapshot.url.slice(0, 180));
    const captured = htmlEscape(snapshot.capturedAt.replace("T", " ").replace(/\.\d{3}Z$/, " UTC"));
    const fileName = htmlEscape(snapshot.fileName.slice(0, 90));
    const fileSize = formatArchiveFileSize(snapshot.fileSize);
    const hashPrefix = htmlEscape(snapshot.contentHash.slice(0, 16));
    const kind = snapshot.captureKind === "initial" ? "bản đầu tiên" : "phát hiện thay đổi";
    lines.push(
      "<b>" + snapshot.id + ". <a href=\"" + url + "\">" + title + "</a></b>",
      "<code>Watch " + snapshot.watchId + "</code> · " + captured + " · " + kind,
      "<code>" + fileName + "</code> · " + fileSize + " · SHA-256 <code>" + hashPrefix + "…</code>",
      "<code>/archive_restore " + snapshot.id + "</code>",
      "",
    );
  }
  if (safeTotal > snapshots.length) {
    const first = (safePage - 1) * safePageSize + 1;
    lines.push("Hiển thị " + first + "–" + (first + snapshots.length - 1) + " / " + safeTotal + " mục.");
  }
  if (pageCount > 1) {
    const querySuffix = query ? " " + htmlEscape(query.slice(0, 120)) : "";
    const navigation: string[] = [];
    if (safePage > 1) navigation.push("← Trước: <code>/archive_page " + (safePage - 1) + querySuffix + "</code>");
    if (safePage < pageCount) navigation.push("Tiếp: <code>/archive_page " + (safePage + 1) + querySuffix + "</code> →");
    if (navigation.length) lines.push(navigation.join("  ·  "));
  }
  lines.push("Tệp gốc nằm trong Telegram archive channel; D1 chỉ giữ chỉ mục và tham chiếu khôi phục.");
  return lines.join("\n");
}
