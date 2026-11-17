import { htmlEscape, sha256Hex, isSafePublicUrl, normalizeUrl } from "./security";
import { sendArchiveDocument, sendTelegram, sendToArchive } from "./telegram";
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
}

async function fetchSafe(urlInput: string, etag?: string | null, lastModified?: string | null): Promise<Response> {
  let current = urlInput;
  for (let redirects = 0; redirects <= 3; redirects += 1) {
    const safe = isSafePublicUrl(current);
    if (!safe) throw new Error("URL or redirect is not an allowed public HTTPS address.");
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
      current = new URL(location, safe).toString();
      continue;
    }
    return response;
  }
  throw new Error("Too many redirects.");
}

async function loadRobotsPolicy(origin: string): Promise<RobotsRule[] | null> {
  try {
    const response = await fetchSafe(origin + "/robots.txt");
    if (response.status === 404 || response.status === 410) return [];
    // Conservative handling for auth blocks, rate limits, server failures and unreadable policies.
    if ([401, 403, 429].includes(response.status) || response.status >= 500 || response.status === 304) return null;
    // Other 4xx responses mean the robots resource is unavailable under RFC 9309.
    if (response.status >= 400) return [];
    if (!response.ok) return null;
    return parseRobotsRules(await readLimited(response, 64_000));
  } catch (error) {
    console.warn("Robots policy could not be loaded; deferring watch:", error instanceof Error ? error.message : "unknown");
    return null;
  }
}

async function readLimited(response: Response, maxBytes = 500_000): Promise<string> {
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

function extractPage(html: string): { title: string; text: string } {
  const title = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1]
    ?.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim().slice(0, 240) || "Untitled page";
  const text = html
    .replace(/<(script|style|noscript|svg|iframe)[^>]*>[\s\S]*?<\/\1>/gi, " ")
    .replace(/<!--[\s\S]*?-->/g, " ")
    .replace(/<(br|\/p|\/div|\/li|\/h[1-6])[^>]*>/gi, "\n")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/gi, " ").replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<").replace(/&gt;/gi, ">")
    .replace(/&#39;/gi, "'").replace(/&quot;/gi, '"')
    .replace(/\s+/g, " ").trim().slice(0, 100_000);
  return { title, text };
}

export async function checkWatchTargets(env: Env): Promise<{ checked: number; changed: number }> {
  const rows = await env.DB.prepare(
    `SELECT id, chat_id, user_id, url, normalized_url, interval_minutes, etag, last_modified, content_hash
       FROM watches
      WHERE active = 1
        AND (last_checked_at IS NULL OR datetime(last_checked_at, '+' || interval_minutes || ' minutes') <= datetime('now'))
      ORDER BY last_checked_at IS NULL DESC, last_checked_at ASC
      LIMIT 12`,
  ).all<WatchRow>();
  let checked = 0;
  let changed = 0;
  // Fetch robots.txt once per origin for this scheduled invocation.
  const robotsPolicies = new Map<string, Promise<RobotsRule[] | null>>();
  for (const watch of rows.results) {
    try {
      const origin = new URL(watch.url).origin;
      let policyPromise = robotsPolicies.get(origin);
      if (!policyPromise) {
        policyPromise = loadRobotsPolicy(origin);
        robotsPolicies.set(origin, policyPromise);
      }
      const robotsRules = await policyPromise;
      if (robotsRules === null || !isAllowedByRobots(watch.url, robotsRules)) {
        // -2 = disallowed by robots.txt; -3 = policy unavailable, so the check is deferred.
        await env.DB.prepare("UPDATE watches SET last_checked_at = ?, last_status = ? WHERE id = ?")
          .bind(new Date().toISOString(), robotsRules === null ? -3 : -2, watch.id).run();
        checked += 1;
        continue;
      }
      const response = await fetchSafe(watch.url, watch.etag, watch.last_modified);
      const now = new Date().toISOString();
      if (response.status === 304) {
        await env.DB.prepare("UPDATE watches SET last_checked_at = ?, last_status = 304 WHERE id = ?")
          .bind(now, watch.id).run();
        checked += 1;
        continue;
      }
      if (!response.ok) {
        await env.DB.prepare("UPDATE watches SET last_checked_at = ?, last_status = ? WHERE id = ?")
          .bind(now, response.status, watch.id).run();
        checked += 1;
        continue;
      }
      const contentType = response.headers.get("content-type") || "";
      if (!/(text\/html|text\/plain|application\/xhtml\+xml|application\/xml)/i.test(contentType)) {
        await env.DB.prepare("UPDATE watches SET last_checked_at = ?, last_status = ? WHERE id = ?")
          .bind(now, response.status, watch.id).run();
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

      const existing = await env.DB.prepare("SELECT id FROM indexed_pages WHERE normalized_url = ?")
        .bind(watch.normalized_url).first<{ id: number }>();
      const statements = [
        env.DB.prepare(
          `UPDATE watches SET last_checked_at = ?, last_status = ?, etag = ?, last_modified = ?, content_hash = ?
            WHERE id = ?`,
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

      if (isFirstSnapshot || isChanged) {
        const caption = `Nolane Search snapshot · ${isFirstSnapshot ? "initial capture" : "detected change"} · ${hostname} · ${now}`;
        try {
          await sendArchiveDocument(
            env,
            `nolane-${watch.id}-${Date.now()}.txt`,
            `TITLE: ${page.title}\nURL: ${watch.url}\nCAPTURED: ${now}\nCONTENT HASH: ${hash}\n\n${page.text}`,
            caption,
          );
        } catch (error) {
          console.error("Snapshot archive failed:", error instanceof Error ? error.message : "unknown");
        }
      }
      if (isChanged) {
        const message =
          `<b>Website changed · Nolane Search</b>\n` +
          `<a href="${htmlEscape(watch.url)}">${htmlEscape(page.title)}</a>\n` +
          `Domain: <code>${htmlEscape(hostname)}</code>\n` +
          `Watch ID: <code>${watch.id}</code>\n` +
          `Detected: ${now}\n\n` +
          `Trang đã thay đổi so với lần kiểm tra trước. Bản snapshot mới đã được gửi vào kênh lưu trữ nếu bạn đã cấu hình.`;
        await sendTelegram(env, watch.chat_id, message);
        await sendToArchive(env, message);
        changed += 1;
      }
      checked += 1;
    } catch (error) {
      console.error("Watch check failed", watch.id, error instanceof Error ? error.message : "unknown");
      await env.DB.prepare("UPDATE watches SET last_checked_at = ?, last_status = -1 WHERE id = ?")
        .bind(new Date().toISOString(), watch.id).run();
      checked += 1;
    }
  }
  return { checked, changed };
}

export function validateWatchUrl(input: string): { url: URL; normalized: string } | null {
  const url = isSafePublicUrl(input);
  if (!url) return null;
  return { url, normalized: normalizeUrl(url.toString()) };
}
