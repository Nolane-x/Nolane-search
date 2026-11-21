import { htmlEscape, sha256Hex, isSafePublicUrl, normalizeUrl } from "./security";
import { sendArchiveDocument, sendTelegram, sendToArchive, telegramApi } from "./telegram";
import { saveArchiveSnapshot } from "./archive";
import type { Env } from "./types";

export interface RobotsRule {
  allow: boolean;
  pattern: string;
  specificity: number;
  regex: RegExp;
}

interface RobotsGroup {
  agents: string[];
  rules: Array<{ allow: boolean; pattern: string }>;
}

function compileRobotsPattern(pattern: string): RegExp {
  const anchored = pattern.endsWith("$");
  const sourcePattern = anchored ? pattern.slice(0, -1) : pattern;
  const regexMeta = new Set([".", "+", "?", "^", "$", "{", "}", "(", ")", "|", "[", "]", String.fromCharCode(92)]);
  let source = "^";
  for (const character of sourcePattern) {
    if (character === "*") source += ".*";
    else source += regexMeta.has(character) ? String.fromCharCode(92) + character : character;
  }
  if (anchored) source += "$";
  return new RegExp(source);
}

/** Parse the core RFC 9309 Allow/Disallow groups for NolaneSearchBot. */
export function parseRobotsRules(content: string, userAgent = "NolaneSearchBot"): RobotsRule[] {
  const groups: RobotsGroup[] = [];
  let current: RobotsGroup | null = null;
  let hasRules = false;

  for (const rawLine of content.split("\n")) {
    const withoutCarriageReturn = rawLine.endsWith("\r") ? rawLine.slice(0, -1) : rawLine;
    const commentAt = withoutCarriageReturn.indexOf("#");
    const line = (commentAt >= 0 ? withoutCarriageReturn.slice(0, commentAt) : withoutCarriageReturn).trim();
    if (!line) continue;
    const separator = line.indexOf(":");
    if (separator < 0) continue;
    const directive = line.slice(0, separator).trim().toLowerCase();
    const value = line.slice(separator + 1).trim();

    if (directive === "user-agent") {
      if (current && hasRules) {
        groups.push(current);
        current = null;
        hasRules = false;
      }
      current ??= { agents: [], rules: [] };
      if (value) current.agents.push(value.toLowerCase());
      continue;
    }
    if (!current?.agents.length || (directive !== "allow" && directive !== "disallow")) continue;
    hasRules = true;
    // An empty Disallow means no restriction; empty rules are ignored.
    if (!value.startsWith("/")) continue;
    current.rules.push({ allow: directive === "allow", pattern: value });
  }

  if (current?.agents.length) groups.push(current);
  const token = userAgent.toLowerCase();
  const matching = groups.filter(group => group.agents.some(agent => agent !== "*" && token.includes(agent)));
  const selected = matching.length ? matching : groups.filter(group => group.agents.includes("*"));

  return selected.flatMap(group => group.rules).map(rule => {
    const withoutEndAnchor = rule.pattern.endsWith("$") ? rule.pattern.slice(0, -1) : rule.pattern;
    return {
      ...rule,
      specificity: new TextEncoder().encode(withoutEndAnchor.replaceAll("*", "")).length,
      regex: compileRobotsPattern(rule.pattern),
    };
  });
}

/** Longest matching rule wins; Allow wins an equal-length tie. */
export function isAllowedByRobots(urlInput: string | URL, rules: RobotsRule[]): boolean {
  const url = typeof urlInput === "string" ? new URL(urlInput) : urlInput;
  const pathAndQuery = url.pathname + url.search;
  let best: RobotsRule | null = null;
  for (const rule of rules) {
    if (!rule.regex.test(pathAndQuery)) continue;
    if (!best || rule.specificity > best.specificity ||
      (rule.specificity === best.specificity && rule.allow && !best.allow)) best = rule;
  }
  return best?.allow ?? true;
}

interface WatchRow {
  id: number;
  chat_id: string;
  user_id: string;
  url: string;
  normalized_url: string;
  interval_minutes: number;
  etag: string | null;
  last_modified: string | null;
  content_hash: string | null;
  last_status: number | null;
}

async function fetchSafe(urlInput: string, etag?: string | null, lastModified?: string | null): Promise<Response> {
  let current = urlInput;
  for (let redirects = 0; redirects <= 3; redirects += 1) {
    const safe = isSafePublicUrl(current);
    const originalOrigin = new URL(urlInput).origin;
    if (!safe || safe.origin !== originalOrigin) {
      throw new Error("Watch URL or redirect must remain on the original public HTTPS origin.");
    }
    const headers = new Headers({
      "user-agent": "NolaneSearchBot/0.1 (+https://github.com/Nolane-x/Nolane-search)",
      "accept": "text/html,application/xhtml+xml,text/plain,application/xml;q=0.9,*/*;q=0.2",
    });
    if (etag) headers.set("if-none-match", etag);
    if (lastModified) headers.set("if-modified-since", lastModified);
    const response = await fetch(safe, {
      method: "GET",
      headers,
      redirect: "manual",
      signal: AbortSignal.timeout(12_000),
    });
    if ([301, 302, 303, 307, 308].includes(response.status)) {
      const location = response.headers.get("location");
      if (!location) return response;
      let next: URL;
      try { next = new URL(location, safe); }
      catch {
        await response.body?.cancel().catch(() => undefined);
        throw new Error("Watch returned an invalid redirect location.");
      }
      await response.body?.cancel().catch(() => undefined);
      if (next.origin !== originalOrigin) {
        throw new Error("Watch redirect left the original origin.");
      }
      current = next.toString();
      continue;
    }
    return response;
  }
  throw new Error("Too many redirects.");
}

interface RobotsDocument {
  rules: RobotsRule[];
  sitemaps: string[];
}

async function loadRobotsDocument(origin: string): Promise<RobotsDocument | null> {
  try {
    const response = await fetchSafe(origin + "/robots.txt");
    if (response.status === 404 || response.status === 410) return { rules: [], sitemaps: [] };
    // Conservatively defer when policy access is blocked, rate-limited or unavailable.
    if ([401, 403, 429].includes(response.status) || response.status >= 500 || response.status === 304) return null;
    if (response.status >= 400) return { rules: [], sitemaps: [] };
    if (!response.ok) return null;

    const body = await readLimited(response, 64_000);
    const sitemaps = new Set<string>();
    for (const rawLine of body.split(/\r?\n/)) {
      const line = rawLine.replace(/#.*$/, "").trim();
      const match = line.match(/^sitemap\s*:\s*(\S+)\s*$/i);
      if (!match?.[1]) continue;
      try {
        const sitemap = isSafePublicUrl(new URL(match[1], origin).toString());
        if (sitemap && sitemap.origin === origin) sitemaps.add(normalizeUrl(sitemap.toString()));
      } catch { /* Ignore malformed or cross-origin Sitemap declarations. */ }
    }
    return { rules: parseRobotsRules(body), sitemaps: [...sitemaps] };
  } catch (error) {
    console.warn("Robots policy could not be loaded; deferring crawl:", error instanceof Error ? error.message : "unknown");
    return null;
  }
}

export async function loadRobotsPolicy(origin: string): Promise<RobotsRule[] | null> {
  const document = await loadRobotsDocument(origin);
  return document?.rules ?? null;
}

export async function readLimited(response: Response, maxBytes = 500_000): Promise<string> {
  if (!response.body) return "";
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > maxBytes) {
        await reader.cancel();
        throw new Error("Website content exceeded the 500 KB check limit.");
      }
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }
  const bytes = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return new TextDecoder("utf-8", { fatal: false }).decode(bytes);
}

function decodeHtmlText(value: string): string {
  return value.replace(/&(#x[0-9a-f]{1,6}|#\d{1,7}|amp|lt|gt|quot|apos|nbsp);/gi, (entity, token: string) => {
    const named: Record<string, string> = {
      amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ",
    };
    const key = token.toLowerCase();
    if (key in named) return named[key]!;
    const numeric = key.startsWith("#x")
      ? Number.parseInt(key.slice(2), 16)
      : Number.parseInt(key.slice(1), 10);
    if (!Number.isInteger(numeric) || numeric <= 0 || numeric > 0x10ffff) return entity;
    try { return String.fromCodePoint(numeric); } catch { return entity; }
  });
}

export function extractPage(html: string): { title: string; text: string } {
  const titleRaw = html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i)?.[1]
    ?? html.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i)?.[1]
    ?? "Untitled page";
  const title = decodeHtmlText(titleRaw.replace(/<[^>]+>/g, " "))
    .replace(/\s+/g, " ").trim().slice(0, 240) || "Untitled page";

  // Prefer the semantic article/main region when present; otherwise clean the
  // whole document. Remove high-noise regions before converting markup to text.
  const article = html.match(/<article\b[^>]*>([\s\S]*?)<\/article\s*>/i)?.[1];
  const main = html.match(/<main\b[^>]*>([\s\S]*?)<\/main\s*>/i)?.[1];
  const source = article && article.replace(/<[^>]+>/g, " ").trim().length >= 80
    ? article
    : main && main.replace(/<[^>]+>/g, " ").trim().length >= 80
      ? main
      : html;
  const text = decodeHtmlText(source
    .replace(/<(script|style|noscript|svg|iframe|template|nav|footer|aside|form)\b[^>]*>[\s\S]*?<\/\1\s*>/gi, " ")
    .replace(/<!--[\s\S]*?-->/g, " ")
    .replace(/<(br|\/p|\/div|\/li|\/h[1-6]|\/section|\/article)[^>]*>/gi, "\n")
    .replace(/<[^>]+>/g, " "))
    .replace(/[ \t]+/g, " ")
    .replace(/\s+/g, " ").trim().slice(0, 100_000);
  return { title, text };
}

export async function checkWatchTargets(env: Env): Promise<{ checked: number; changed: number }> {
  const rows = await env.DB.prepare(
    `SELECT id, chat_id, user_id, url, normalized_url, interval_minutes, etag, last_modified, content_hash, last_status
       FROM watches
      WHERE active = 1
        AND (last_checked_at IS NULL OR datetime(last_checked_at, '+' || interval_minutes || ' minutes') <= datetime('now'))
      ORDER BY last_checked_at IS NULL DESC, last_checked_at ASC
      LIMIT 12`,
  ).all<WatchRow>();
  let checked = 0;
  let changed = 0;
  const archiveConfigured = Boolean(env.TELEGRAM_ARCHIVE_CHAT_ID);
  // Fetch robots.txt once per origin for this scheduled invocation.
  const robotsPolicies = new Map<string, Promise<RobotsRule[] | null>>();

  for (const watch of rows.results) {
    const wasArchivePending = watch.last_status === -4;
    try {
      const origin = new URL(watch.url).origin;
      let policyPromise = robotsPolicies.get(origin);
      if (!policyPromise) {
        policyPromise = loadRobotsPolicy(origin);
        robotsPolicies.set(origin, policyPromise);
      }
      const robotsRules = await policyPromise;
      if (robotsRules === null || !isAllowedByRobots(watch.url, robotsRules)) {
        // Preserve archive-pending state while access is deferred. Validators were
        // cleared before the failed archive attempt, so a later allowed fetch is full.
        const status = wasArchivePending ? -4 : robotsRules === null ? -3 : -2;
        await env.DB.prepare("UPDATE watches SET last_checked_at = ?, last_status = ? WHERE id = ?")
          .bind(new Date().toISOString(), status, watch.id).run();
        checked += 1;
        continue;
      }

      // A failed capture clears validators and keeps the previous content hash.
      // On retry, force a full body fetch instead of accepting a 304 without a snapshot.
      const response = await fetchSafe(
        watch.url,
        wasArchivePending ? null : watch.etag,
        wasArchivePending ? null : watch.last_modified,
      );
      const now = new Date().toISOString();
      if (response.status === 304) {
        await env.DB.prepare("UPDATE watches SET last_checked_at = ?, last_status = ? WHERE id = ?")
          .bind(now, wasArchivePending ? -4 : 304, watch.id).run();
        checked += 1;
        continue;
      }
      if (!response.ok) {
        await env.DB.prepare("UPDATE watches SET last_checked_at = ?, last_status = ? WHERE id = ?")
          .bind(now, wasArchivePending ? -4 : response.status, watch.id).run();
        checked += 1;
        continue;
      }
      const contentType = response.headers.get("content-type") || "";
      if (!/(text\/html|text\/plain|application\/xhtml\+xml|application\/xml)/i.test(contentType)) {
        await env.DB.prepare("UPDATE watches SET last_checked_at = ?, last_status = ? WHERE id = ?")
          .bind(now, wasArchivePending ? -4 : response.status, watch.id).run();
        checked += 1;
        continue;
      }

      const body = await readLimited(response);
      const page = extractPage(body);
      const hash = await sha256Hex(page.text);
      const etag = response.headers.get("etag");
      const lastModified = response.headers.get("last-modified");
      const hostname = new URL(watch.url).hostname;
      const isFirstSnapshot = watch.content_hash === null;
      const isChanged = !isFirstSnapshot && watch.content_hash !== hash;
      const shouldArchive = archiveConfigured && (isFirstSnapshot || isChanged || wasArchivePending);
      const existing = await env.DB.prepare("SELECT id FROM indexed_pages WHERE normalized_url = ?")
        .bind(watch.normalized_url).first<{ id: number }>();

      // Arm retry state before Telegram. If upload/indexing fails, the old content
      // hash remains authoritative and validators stay empty for the next full fetch.
      const statements = [
        shouldArchive
          ? env.DB.prepare(
              "UPDATE watches SET last_checked_at = ?, last_status = -4, etag = NULL, last_modified = NULL WHERE id = ?",
            ).bind(now, watch.id)
          : env.DB.prepare(
              "UPDATE watches SET last_checked_at = ?, last_status = ?, etag = ?, last_modified = ?, content_hash = ? WHERE id = ?",
            ).bind(now, response.status, etag, lastModified, hash, watch.id),
        env.DB.prepare(
          `INSERT INTO indexed_pages (url, normalized_url, domain, title, content, content_hash, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(normalized_url) DO UPDATE SET
             url = excluded.url, domain = excluded.domain, title = excluded.title,
             content = excluded.content, content_hash = excluded.content_hash, updated_at = excluded.updated_at`,
        ).bind(watch.url, watch.normalized_url, hostname, page.title, page.text.slice(0, 5000), hash, now),
      ];
      if (existing) statements.push(env.DB.prepare("DELETE FROM indexed_pages_fts WHERE rowid = ?").bind(existing.id));
      statements.push(env.DB.prepare(
        `INSERT INTO indexed_pages_fts (rowid, title, content, url, domain)
         SELECT id, title, content, url, domain FROM indexed_pages WHERE normalized_url = ?`,
      ).bind(watch.normalized_url));
      await env.DB.batch(statements);

      let archiveIndexed = !shouldArchive;
      let recoveryNotified = false;
      if (shouldArchive) {
        const captureKind = isFirstSnapshot ? "initial" : "change";
        const caption = `Nolane Search snapshot · ${captureKind === "initial" ? "initial capture" : "detected change"} · ${hostname} · ${now}`;
        let archived: Awaited<ReturnType<typeof sendArchiveDocument>> = null;
        try {
          archived = await sendArchiveDocument(
            env,
            "nolane-" + watch.id + "-" + Date.now() + ".txt",
            "TITLE: " + page.title + "\nURL: " + watch.url + "\nCAPTURED: " + now +
              "\nCONTENT HASH: " + hash + "\n\n" + page.text,
            caption,
          );
          if (!archived) throw new Error("Telegram archive is configured but no document was uploaded.");
          await saveArchiveSnapshot(env, {
            watchId: watch.id, userId: watch.user_id, chatId: watch.chat_id,
            archiveChatId: env.TELEGRAM_ARCHIVE_CHAT_ID!, archiveMessageId: archived.messageId,
            telegramFileId: archived.fileId, telegramFileUniqueId: archived.fileUniqueId || null,
            fileName: archived.fileName, fileSize: archived.fileSize ?? null,
            url: watch.url, normalizedUrl: watch.normalized_url, title: page.title,
            contentHash: hash, captureKind, capturedAt: now,
          });
          archiveIndexed = true;
        } catch (error) {
          console.error("Snapshot archive/index failed; retaining pending retry:", error instanceof Error ? error.message : "unknown error");
          if (archived) {
            // Upload succeeded but metadata indexing failed. Return the file directly
            // to the owner while retaining the pending marker for a later index retry.
            let copiedToOwner = false;
            try {
              await telegramApi(env, "copyMessage", {
                chat_id: watch.chat_id,
                from_chat_id: env.TELEGRAM_ARCHIVE_CHAT_ID,
                message_id: archived.messageId,
              });
              copiedToOwner = true;
            } catch (recoveryError) {
              console.error("Snapshot direct recovery failed:", recoveryError instanceof Error ? recoveryError.message : "unknown error");
            }
            try {
              const recoveryMessage = copiedToOwner
                ? "<b>Đã cứu hộ snapshot nhưng chưa lập chỉ mục được.</b>\n" +
                  "Tệp đã được sao chép trực tiếp vào chat này. Snapshot sẽ được thử lập chỉ mục lại ở lần kiểm tra tiếp theo.\n" +
                  "<code>" + htmlEscape(archived.fileName) + "</code>"
                : "<b>Cảnh báo: snapshot chưa được lập chỉ mục.</b>\n" +
                  "Tệp vẫn nằm trong kênh archive; hãy giữ nguyên tin gốc để có thể xử lý lại.\n" +
                  "<code>" + htmlEscape(archived.fileName) + "</code> · message <code>" + archived.messageId + "</code>";
              await sendTelegram(env, watch.chat_id, recoveryMessage);
              recoveryNotified = true;
            } catch (notifyError) {
              console.error("Snapshot recovery notification failed:", notifyError instanceof Error ? notifyError.message : "unknown error");
            }
          }
        }

        if (archiveIndexed) {
          await env.DB.prepare(
            "UPDATE watches SET content_hash = ?, etag = ?, last_modified = ?, last_status = ? WHERE id = ?",
          ).bind(hash, etag, lastModified, response.status, watch.id).run();
        } else if (!wasArchivePending && !recoveryNotified) {
          try {
            await sendTelegram(env, watch.chat_id,
              "<b>Snapshot đang chờ lưu vào archive.</b>\n" +
              "Lần gửi hoặc lập chỉ mục vừa thất bại. Nolane Search giữ hash cũ, tạm bỏ HTTP validators và sẽ tự thử lại ở lần kiểm tra tiếp theo.\n" +
              "<a href=\"" + htmlEscape(watch.url) + "\">" + htmlEscape(page.title) + "</a>");
          } catch (notifyError) {
            console.error("Snapshot retry notification failed:", notifyError instanceof Error ? notifyError.message : "unknown error");
          }
        }
      }

      if (isChanged && archiveIndexed) {
        const message =
          `<b>Website changed · Nolane Search</b>\n` +
          `<a href="${htmlEscape(watch.url)}">${htmlEscape(page.title)}</a>\n` +
          `Domain: <code>${htmlEscape(hostname)}</code>\n` +
          `Watch ID: <code>${watch.id}</code>\n` +
          `Detected: ${now}\n\n` +
          `Trang đã thay đổi so với lần kiểm tra trước. Bản snapshot mới đã được lưu trong archive.`;
        try {
          await sendTelegram(env, watch.chat_id, message);
        } catch (notificationError) {
          // A failed alert must not roll back a snapshot that is already archived
          // and indexed. Keep notification delivery separate from capture state.
          console.error("Watch change notification failed:", notificationError instanceof Error ? notificationError.message : "unknown error");
        }
        await sendToArchive(env, message);
        changed += 1;
      }
      checked += 1;
    } catch (error) {
      console.error("Watch check failed", watch.id, error instanceof Error ? error.message : "unknown");
      await env.DB.prepare("UPDATE watches SET last_checked_at = ?, last_status = ? WHERE id = ?")
        .bind(new Date().toISOString(), wasArchivePending ? -4 : -1, watch.id).run();
      checked += 1;
    }
  }
  return { checked, changed };
}


export interface SiteCrawlSummary {
  seedUrl: string;
  origin: string;
  discovered: number;
  indexed: number;
  skipped: number;
  pages: Array<{ url: string; title: string }>;
}

function decodeHtmlAttribute(value: string): string {
  return value
    .replace(/&amp;/gi, "&")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">");
}

function crawlCandidate(input: string, origin: string): string | null {
  try {
    const url = new URL(input, origin);
    if (url.origin !== origin || url.protocol !== "https:" || url.username || url.password) return null;
    if (/\.(?:7z|avi|css|csv|docx?|eot|gif|gz|ico|jpe?g|js|json|m4v|mov|mp[34]|pdf|png|pptx?|rar|rss|svg|tar|tif|ttf|webm|webp|woff2?|xlsx?|xml\.gz|zip)$/i.test(url.pathname)) return null;
    url.hash = "";
    if (url.search) return null;
    return normalizeUrl(url.toString());
  } catch { return null; }
}

function extractCrawlLinks(html: string, currentUrl: string, origin: string, limit: number): string[] {
  const found = new Set<string>();
  const pattern = /<a\b[^>]*\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/gi;
  for (const match of html.matchAll(pattern)) {
    const raw = decodeHtmlAttribute((match[1] ?? match[2] ?? match[3] ?? "").trim());
    if (!raw || /^(?:#|mailto:|tel:|javascript:|data:)/i.test(raw)) continue;
    const candidate = crawlCandidate(raw, origin);
    if (!candidate || candidate === currentUrl) continue;
    found.add(candidate);
    if (found.size >= limit) break;
  }
  return [...found];
}

async function fetchCrawlResponse(
  input: string,
  origin: string,
): Promise<{ response: Response; finalUrl: URL }> {
  let current = input;
  for (let redirects = 0; redirects <= 3; redirects += 1) {
    const safe = isSafePublicUrl(current);
    if (!safe || safe.origin !== origin) throw new Error("Crawl redirect left the allowed HTTPS origin.");
    const response = await fetch(safe, {
      method: "GET",
      headers: {
        "user-agent": "NolaneSearchBot/0.2 (+https://github.com/Nolane-x/Nolane-search)",
        "accept": "text/html,application/xhtml+xml,text/plain,application/xml;q=0.9,*/*;q=0.2",
      },
      redirect: "manual",
      signal: AbortSignal.timeout(10_000),
    });
    if ([301, 302, 303, 307, 308].includes(response.status)) {
      const location = response.headers.get("location");
      if (!location) return { response, finalUrl: safe };
      let next: URL;
      try { next = new URL(location, safe); }
      catch {
        await response.body?.cancel().catch(() => undefined);
        throw new Error("Crawl returned an invalid redirect location.");
      }
      await response.body?.cancel().catch(() => undefined);
      if (next.origin !== origin) throw new Error("Crawl redirect left the allowed HTTPS origin.");
      current = next.toString();
      continue;
    }
    return { response, finalUrl: safe };
  }
  throw new Error("Crawl exceeded the redirect limit.");
}

function sitemapLocation(block: string): string | null {
  const value = block.match(/<loc\b[^>]*>([\s\S]*?)<\/loc\s*>/i)?.[1];
  return value ? decodeHtmlAttribute(value.trim()) : null;
}

async function discoverSitemapUrls(
  origin: string,
  rules: RobotsRule[],
  limit: number,
  declaredSitemaps: string[] = [],
): Promise<string[]> {
  const maxPageUrls = Math.max(1, Math.min(100, Math.floor(limit)));
  const sitemapQueue = [...new Set([...declaredSitemaps, origin + "/sitemap.xml"])];
  const visitedSitemaps = new Set<string>();
  const pageUrls = new Set<string>();

  // Bound sitemap recursion separately from the page cap. A sitemap index
  // can reference hundreds of child files; only a small same-origin subset is read.
  while (sitemapQueue.length && visitedSitemaps.size < 5 && pageUrls.size < maxPageUrls) {
    const sitemapInput = sitemapQueue.shift()!;
    const sitemap = crawlCandidate(sitemapInput, origin);
    if (!sitemap || visitedSitemaps.has(sitemap) || !isAllowedByRobots(sitemap, rules)) continue;
    visitedSitemaps.add(sitemap);

    try {
      const { response } = await fetchCrawlResponse(sitemap, origin);
      if (!response.ok || !/(xml|text\/plain)/i.test(response.headers.get("content-type") || "")) continue;
      const xml = await readLimited(response, 300_000);
      if (/<sitemapindex\b/i.test(xml)) {
        const blocks = [...xml.matchAll(/<sitemap\b[^>]*>([\s\S]*?)<\/sitemap\s*>/gi)];
        for (const block of blocks) {
          const location = sitemapLocation(block[1] || "");
          if (!location) continue;
          const nested = crawlCandidate(location, origin);
          if (nested && !visitedSitemaps.has(nested) && !sitemapQueue.includes(nested) && sitemapQueue.length < 12) {
            sitemapQueue.push(nested);
          }
        }
        continue;
      }

      const blocks = [...xml.matchAll(/<url\b[^>]*>([\s\S]*?)<\/url\s*>/gi)];
      const locations = blocks.length
        ? blocks.map(block => sitemapLocation(block[1] || "")).filter((item): item is string => Boolean(item))
        : [...xml.matchAll(/<loc\b[^>]*>([\s\S]*?)<\/loc\s*>/gi)]
          .map(match => decodeHtmlAttribute((match[1] || "").trim()));
      for (const location of locations) {
        const candidate = crawlCandidate(location, origin);
        if (!candidate || candidate === sitemap || pageUrls.has(candidate)) continue;
        pageUrls.add(candidate);
        if (pageUrls.size >= maxPageUrls) break;
      }
    } catch (error) {
      console.warn("Sitemap discovery was skipped:", error instanceof Error ? error.message : "unknown");
    }
  }
  return [...pageUrls];
}

async function storeIndexedPage(
  env: Env,
  url: string,
  title: string,
  content: string,
  contentHash: string,
): Promise<void> {
  const now = new Date().toISOString();
  const domain = new URL(url).hostname;
  await env.DB.batch([
    env.DB.prepare(
      "DELETE FROM indexed_pages_fts WHERE rowid = (SELECT id FROM indexed_pages WHERE normalized_url = ?)",
    ).bind(url),
    env.DB.prepare(
      `INSERT INTO indexed_pages (url, normalized_url, domain, title, content, content_hash, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(normalized_url) DO UPDATE SET
         url = excluded.url, domain = excluded.domain, title = excluded.title,
         content = excluded.content, content_hash = excluded.content_hash, updated_at = excluded.updated_at`,
    ).bind(url, url, domain, title.slice(0, 240), content.slice(0, 5000), contentHash, now),
    env.DB.prepare(
      `INSERT INTO indexed_pages_fts (rowid, title, content, url, domain)
       SELECT id, title, content, url, domain FROM indexed_pages WHERE normalized_url = ?`,
    ).bind(url),
  ]);
}

/**
 * Bounded, same-origin public-site crawl for the owner's private FTS index.
 * It follows robots.txt, optionally seeds from sitemap.xml and indexes a capped
 * number of HTML/text pages. It is deliberately not a general Internet crawler.
 */
export async function crawlAndIndexSite(
  env: Env,
  seedInput: string,
  requestedMaxPages = 10,
): Promise<SiteCrawlSummary> {
  const seed = validateWatchUrl(seedInput);
  if (!seed) throw new Error("Only public HTTPS website URLs are allowed.");
  const origin = seed.url.origin;
  const maxPages = Math.max(1, Math.min(20, Math.floor(requestedMaxPages)));
  const robots = await loadRobotsDocument(origin);
  if (robots === null) throw new Error("The site's robots.txt could not be checked; crawl deferred for safety.");
  const rules = robots.rules;

  const queued = new Set<string>([seed.normalized]);
  for (const sitemapUrl of await discoverSitemapUrls(origin, rules, maxPages * 5, robots.sitemaps)) {
    if (queued.size >= maxPages * 5 + 1) break;
    queued.add(sitemapUrl);
  }
  const pending = [...queued];
  const visited = new Set<string>();
  const pages: Array<{ url: string; title: string }> = [];
  let indexed = 0;
  let skipped = 0;

  while (pending.length && indexed < maxPages) {
    const current = pending.shift()!;
    if (visited.has(current)) continue;
    visited.add(current);
    if (!isAllowedByRobots(current, rules)) { skipped += 1; continue; }

    try {
      const { response, finalUrl } = await fetchCrawlResponse(current, origin);
      if (!response.ok) { skipped += 1; continue; }
      const contentType = response.headers.get("content-type") || "";
      if (!/(text\/html|text\/plain|application\/xhtml\+xml)/i.test(contentType)) {
        skipped += 1;
        continue;
      }
      const body = await readLimited(response, 350_000);
      const page = extractPage(body);
      if (page.text.length < 40) { skipped += 1; continue; }
      const finalNormalized = normalizeUrl(finalUrl.toString());
      const hash = await sha256Hex(page.text);
      await storeIndexedPage(env, finalNormalized, page.title, page.text, hash);
      indexed += 1;
      pages.push({ url: finalNormalized, title: page.title });

      for (const link of extractCrawlLinks(body, finalNormalized, origin, maxPages * 6)) {
        if (!visited.has(link) && !queued.has(link) && pending.length < maxPages * 6) {
          queued.add(link);
          pending.push(link);
        }
      }
    } catch (error) {
      skipped += 1;
      console.warn("Site crawl page skipped:", current, error instanceof Error ? error.message : "unknown");
    }
  }

  return {
    seedUrl: seed.normalized,
    origin,
    discovered: queued.size,
    indexed,
    skipped,
    pages,
  };
}

export function validateWatchUrl(input: string): { url: URL; normalized: string } | null {
  const url = isSafePublicUrl(input);
  if (!url) return null;
  return { url, normalized: normalizeUrl(url.toString()) };
}
