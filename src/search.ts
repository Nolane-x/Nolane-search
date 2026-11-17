import { normalizeUrl, sha256Hex } from "./security";
import type { Env, SearchMode, SearchResult } from "./types";
import { searchBrave, searchExa, searchGitHub, searchTavily } from "./providers";

function queryTerms(query: string): string[] {
  return query.toLowerCase().split(/[^\p{L}\p{N}]+/u).filter((term) => term.length > 2).slice(0, 20);
}

function rankAndDeduplicate(query: string, items: SearchResult[], mode: SearchMode): SearchResult[] {
  const terms = queryTerms(query);
  const byUrl = new Map<string, SearchResult>();
  for (const item of items) {
    let key: string;
    try { key = normalizeUrl(item.url); } catch { continue; }
    const title = item.title.toLowerCase();
    const snippet = item.snippet.toLowerCase();
    const overlap = terms.length ? terms.filter((term) => title.includes(term) || snippet.includes(term)).length / terms.length : 0;
    const domainBoost = /(^|\.)((gov|edu)(\.[a-z]{2,})?|docs\.[a-z]{2,})$/i.test(item.domain) ? 0.08 : 0;
    const age = item.publishedAt ? Date.parse(item.publishedAt) : NaN;
    const freshness = Number.isFinite(age) ? Math.max(0, 1 - (Date.now() - age) / (1000 * 60 * 60 * 24 * 365)) : 0;
    const score = Math.max(0, Math.min(1.5,
      item.score * 0.58 + overlap * 0.30 + domainBoost + (mode === "news" ? freshness * 0.12 : freshness * 0.035),
    ));
    const normalized = { ...item, score };
    const previous = byUrl.get(key);
    if (!previous || normalized.score > previous.score) byUrl.set(key, normalized);
  }
  const results = [...byUrl.values()].sort((a, b) => b.score - a.score);
  const domains = new Set<string>();
  const diversified: SearchResult[] = [];
  for (const item of results) {
    if (!domains.has(item.domain) || diversified.length < 3) {
      diversified.push(item);
      domains.add(item.domain);
    }
  }
  for (const item of results) {
    if (diversified.length >= 8) break;
    if (!diversified.some((existing) => existing.url === item.url)) diversified.push(item);
  }
  return diversified.slice(0, 8);
}

async function localSearch(env: Env, query: string): Promise<SearchResult[]> {
  const safeQuery = query.replace(/[^\p{L}\p{N}\s_-]/gu, " ").trim().split(/\s+/).filter(Boolean).join(" ");
  if (!safeQuery) return [];
  const result = await env.DB.prepare(
    \`SELECT p.title, p.url, p.domain,
            snippet(indexed_pages_fts, 1, '', '', ' … ', 18) AS snippet
       FROM indexed_pages_fts
       JOIN indexed_pages p ON p.id = indexed_pages_fts.rowid
      WHERE indexed_pages_fts MATCH ?
      ORDER BY bm25(indexed_pages_fts)
      LIMIT 8\`,
  ).bind(safeQuery).all<{ title: string; url: string; domain: string; snippet: string }>();
  return result.results.map((item) => ({
    title: item.title, url: item.url, domain: item.domain, snippet: item.snippet,
    provider: "Nolane Index", score: 0.7,
  }));
}

async function cachedSearch(env: Env, query: string, mode: SearchMode): Promise<SearchResult[]> {
  const cacheKey = await sha256Hex(\`\${mode}\\n\${query.trim().toLowerCase()}\`);
  const now = Date.now();
  const cached = await env.DB.prepare(
    "SELECT payload FROM search_cache WHERE cache_key = ? AND expires_at > ?",
  ).bind(cacheKey, now).first<{ payload: string }>();
  if (cached?.payload) {
    try { return JSON.parse(cached.payload) as SearchResult[]; } catch { /* discard malformed cache row */ }
  }

  let results: SearchResult[] = [];
  if (mode === "github") {
    results = await searchGitHub(env, query);
  } else if (mode === "local") {
    results = await localSearch(env, query);
  } else if (mode === "research") {
    const calls = await Promise.allSettled([
      ...(env.TAVILY_API_KEY ? [searchTavily(env, query)] : []),
      ...(env.EXA_API_KEY ? [searchExa(env, query)] : []),
    ]);
    for (const call of calls) if (call.status === "fulfilled") results.push(...call.value);
    if (!results.length) throw new Error("Research providers unavailable. Configure TAVILY_API_KEY or EXA_API_KEY.");
  } else if (mode === "tech") {
    const calls = await Promise.allSettled([
      ...(env.TAVILY_API_KEY ? [searchTavily(env, query)] : []),
      searchGitHub(env, query),
    ]);
    for (const call of calls) if (call.status === "fulfilled") results.push(...call.value);
    if (!results.length) throw new Error("Technology search providers unavailable.");
  } else if (mode === "news") {
    if (env.TAVILY_API_KEY) {
      try { results = await searchTavily(env, query, "news"); } catch { /* use fallback */ }
    }
    if (!results.length && env.BRAVE_SEARCH_API_KEY) results = await searchBrave(env, query, true);
    if (!results.length) throw new Error("News search providers unavailable.");
  } else {
    if (env.TAVILY_API_KEY) {
      try { results = await searchTavily(env, query); } catch { /* use fallback */ }
    }
    if (!results.length && env.BRAVE_SEARCH_API_KEY) results = await searchBrave(env, query);
    if (!results.length) throw new Error("Web search providers unavailable.");
  }

  const ranked = rankAndDeduplicate(query, results, mode);
  if (ranked.length) {
    await env.DB.prepare(
      \`INSERT INTO search_cache (cache_key, payload, expires_at, created_at)
       VALUES (?, ?, ?, ?)
       ON CONFLICT(cache_key) DO UPDATE SET
         payload = excluded.payload, expires_at = excluded.expires_at, created_at = excluded.created_at\`,
    ).bind(cacheKey, JSON.stringify(ranked), now + 2 * 60 * 1000, now).run();
  }
  return ranked;
}

export async function performSearch(env: Env, query: string, mode: SearchMode = "web"): Promise<SearchResult[]> {
  return cachedSearch(env, query, mode);
}

export async function performDeepSearch(env: Env, query: string): Promise<SearchResult[]> {
  const variations = [
    query,
    \`\${query} official documentation\`,
    \`\${query} research benchmarks evidence\`,
    \`\${query} open source projects\`,
  ];
  const calls = await Promise.allSettled([
    ...(env.TAVILY_API_KEY ? variations.map((item) => searchTavily(env, item)) : []),
    ...(env.EXA_API_KEY ? [searchExa(env, query)] : []),
    ...(env.BRAVE_SEARCH_API_KEY ? [searchBrave(env, query)] : []),
  ]);
  const combined: SearchResult[] = [];
  for (const call of calls) if (call.status === "fulfilled") combined.push(...call.value);
  if (!combined.length) throw new Error("No configured search provider returned results.");
  return rankAndDeduplicate(query, combined, "research");
}
