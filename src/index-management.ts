import { isSafePublicUrl, normalizeUrl } from "./security";
import type { Env } from "./types";

export interface IndexedPageSummary { id: number; url: string; domain: string; title: string; updatedAt: string; contentChars: number; }
export interface IndexedPageList { total: number; pages: IndexedPageSummary[]; }
export type IndexDeleteTarget = { kind: "url"; value: string } | { kind: "domain"; value: string };
export interface IndexDeleteResult { pagesDeleted: number; watchesDisabled: number; target: IndexDeleteTarget; }

export function normalizeIndexDomain(input: string): string | null {
  const raw = input.trim().toLowerCase().replace(/^www\./, "").replace(/\.$/, "");
  if (!raw || raw.length > 253 || /[\s/:?#@]/.test(raw)) return null;
  const safe = isSafePublicUrl("https://" + raw + "/");
  if (!safe || safe.hostname !== raw) return null;
  return safe.hostname;
}

export function normalizeIndexPageUrl(input: string): string | null {
  const safe = isSafePublicUrl(input.trim());
  return safe ? normalizeUrl(safe.toString()) : null;
}

export async function listIndexedPages(env: Env, options: { query?: string; limit?: number; offset?: number } = {}): Promise<IndexedPageList> {
  const query = String(options.query || "").trim().slice(0, 100).toLocaleLowerCase();
  const pattern = query ? "%" + query + "%" : "%";
  const limit = Math.max(1, Math.min(40, Math.floor(options.limit || 20)));
  const offset = Math.max(0, Math.min(5000, Math.floor(options.offset || 0)));
  const [count, rows] = await Promise.all([
    env.DB.prepare("SELECT COUNT(*) AS total FROM indexed_pages WHERE (? = '' OR lower(title) LIKE ? OR lower(domain) LIKE ? OR lower(url) LIKE ?)")
      .bind(query, pattern, pattern, pattern).first<{ total: number }>(),
    env.DB.prepare("SELECT id, url, domain, title, updated_at, length(content) AS content_chars FROM indexed_pages WHERE (? = '' OR lower(title) LIKE ? OR lower(domain) LIKE ? OR lower(url) LIKE ?) ORDER BY updated_at DESC, id DESC LIMIT ? OFFSET ?")
      .bind(query, pattern, pattern, pattern, limit, offset).all<{ id: number; url: string; domain: string; title: string; updated_at: string; content_chars: number }>(),
  ]);
  return {
    total: Math.max(0, Number(count?.total) || 0),
    pages: rows.results.map(row => ({ id: row.id, url: row.url, domain: row.domain, title: row.title, updatedAt: row.updated_at, contentChars: Math.max(0, Number(row.content_chars) || 0) })),
  };
}

/** Remove matching FTS/base rows and deactivate matching watches in one D1 batch. */
export async function deleteIndexedContent(env: Env, target: IndexDeleteTarget): Promise<IndexDeleteResult> {
  let predicate: string;
  let values: unknown[];
  if (target.kind === "url") {
    const normalized = normalizeIndexPageUrl(target.value);
    if (!normalized) throw new Error("Only a valid public HTTPS page URL can be removed.");
    predicate = "normalized_url = ?";
    values = [normalized];
    target = { kind: "url", value: normalized };
  } else {
    const domain = normalizeIndexDomain(target.value);
    if (!domain) throw new Error("Enter a valid public domain such as example.com.");
    predicate = "lower(domain) IN (?, ?)";
    values = [domain, "www." + domain];
    target = { kind: "domain", value: domain };
  }
  const result = await env.DB.batch([
    env.DB.prepare("DELETE FROM indexed_pages_fts WHERE rowid IN (SELECT id FROM indexed_pages WHERE " + predicate + ")").bind(...values),
    env.DB.prepare("UPDATE watches SET active = 0 WHERE normalized_url IN (SELECT normalized_url FROM indexed_pages WHERE " + predicate + ")").bind(...values),
    env.DB.prepare("DELETE FROM indexed_pages WHERE " + predicate).bind(...values),
  ]);
  return { pagesDeleted: Math.max(0, Number(result[2]?.meta?.changes) || 0), watchesDisabled: Math.max(0, Number(result[1]?.meta?.changes) || 0), target };
}
