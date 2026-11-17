import { normalizeUrl, sha256Hex } from "./security";
import type { Env, SearchMode, SearchResult } from "./types";
import { fetchTinyFishPages, searchBrave, searchExa, searchGitHub, searchTavily, searchTinyFish } from "./providers";

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
    `SELECT p.title, p.url, p.domain,
            snippet(indexed_pages_fts, 1, '', '', ' … ', 18) AS snippet
       FROM indexed_pages_fts
       JOIN indexed_pages p ON p.id = indexed_pages_fts.rowid
      WHERE indexed_pages_fts MATCH ?
      ORDER BY bm25(indexed_pages_fts)
      LIMIT 8`,
  ).bind(safeQuery).all<{ title: string; url: string; domain: string; snippet: string }>();
  return result.results.map((item) => ({
    title: item.title, url: item.url, domain: item.domain, snippet: item.snippet,
    provider: "Nolane Index", score: 0.7,
  }));
}

async function settledResults(calls: Promise<SearchResult[]>[]): Promise<SearchResult[]> {
  const settled = await Promise.allSettled(calls);
  const results: SearchResult[] = [];
  for (const call of settled) {
    if (call.status === "fulfilled") results.push(...call.value);
    else console.warn("A federated search provider failed:", call.reason instanceof Error ? call.reason.message : "unknown error");
  }
  return results;
}

async function cachedSearch(env: Env, query: string, mode: SearchMode): Promise<SearchResult[]> {
  const cacheKey = await sha256Hex(`${mode}\n${query.trim().toLowerCase()}`);
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
    results = await settledResults([
      ...(env.TAVILY_API_KEY ? [searchTavily(env, query)] : []),
      ...(env.EXA_API_KEY ? [searchExa(env, query)] : []),
      ...(env.TINYFISH_API_KEY ? [searchTinyFish(env, query, { domainType: "research_paper", purpose: "Find academic papers and evidence relevant to this research question." })] : []),
    ]);
    if (!results.length) throw new Error("Research providers unavailable. Configure TAVILY_API_KEY, EXA_API_KEY or TINYFISH_API_KEY.");
  } else if (mode === "tech") {
    results = await settledResults([
      ...(env.TAVILY_API_KEY ? [searchTavily(env, query)] : []),
      ...(env.TINYFISH_API_KEY ? [searchTinyFish(env, query, { purpose: "Find technical documentation, tools and reliable engineering resources." })] : []),
      searchGitHub(env, query),
    ]);
    if (!results.length) throw new Error("Technology search providers unavailable.");
  } else if (mode === "news") {
    results = await settledResults([
      ...(env.TAVILY_API_KEY ? [searchTavily(env, query, "news")] : []),
      ...(env.BRAVE_SEARCH_API_KEY ? [searchBrave(env, query, true)] : []),
      ...(env.TINYFISH_API_KEY ? [searchTinyFish(env, query, { domainType: "news", purpose: "Find recent news coverage about this topic." })] : []),
    ]);
    if (!results.length) throw new Error("News search providers unavailable.");
  } else {
    // Keep ordinary searches economical: Tavily alone is enough when it returns a useful set.
    // If it fails or returns fewer than four results, query configured fallbacks in parallel.
    let primary: SearchResult[] = [];
    if (env.TAVILY_API_KEY) {
      try { primary = await searchTavily(env, query); }
      catch (error) {
        console.warn("Tavily primary search failed:", error instanceof Error ? error.message : "unknown error");
      }
    }

    if (primary.length >= 4) {
      results = primary;
    } else {
      const fallback = await settledResults([
        ...(env.EXA_API_KEY ? [searchExa(env, query)] : []),
        ...(env.TINYFISH_API_KEY ? [searchTinyFish(env, query)] : []),
        ...(env.BRAVE_SEARCH_API_KEY ? [searchBrave(env, query)] : []),
      ]);
      results = [...primary, ...fallback];
    }
    if (!results.length) {
      throw new Error("Web search providers unavailable. Configure Tavily, Exa, TinyFish or Brave.");
    }
  }

  const ranked = rankAndDeduplicate(query, results, mode);
  if (ranked.length) {
    await env.DB.prepare(
      `INSERT INTO search_cache (cache_key, payload, expires_at, created_at)
       VALUES (?, ?, ?, ?)
       ON CONFLICT(cache_key) DO UPDATE SET
         payload = excluded.payload, expires_at = excluded.expires_at, created_at = excluded.created_at`,
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
    `${query} official documentation`,
    `${query} research benchmarks evidence`,
    `${query} open source projects`,
  ];
  const calls = await Promise.allSettled([
    ...(env.TAVILY_API_KEY ? variations.map((item) => searchTavily(env, item)) : []),
    ...(env.EXA_API_KEY ? [searchExa(env, query)] : []),
    ...(env.BRAVE_SEARCH_API_KEY ? [searchBrave(env, query)] : []),
    ...(env.TINYFISH_API_KEY ? [
      searchTinyFish(env, query, { purpose: "Conduct broad research; find primary sources, technical documentation, and credible evidence." }),
      searchTinyFish(env, query, { domainType: "research_paper", purpose: "Find relevant academic papers, benchmarks and primary research." }),
    ] : []),
  ]);
  const combined: SearchResult[] = [];
  for (const call of calls) if (call.status === "fulfilled") combined.push(...call.value);
  if (!combined.length) throw new Error("No configured search provider returned results.");

  let ranked = rankAndDeduplicate(query, combined, "research");
  if (env.TINYFISH_API_KEY && ranked.length) {
    try {
      const pages = await fetchTinyFishPages(env, ranked.slice(0, 5).map((item) => item.url));
      ranked = ranked.map((item) => {
        const page = pages.get(item.url);
        return page ? { ...item, title: page.title || item.title, snippet: page.text.slice(0, 1100), provider: `${item.provider} + TinyFish Fetch` } : item;
      });
    } catch (error) {
      console.error("TinyFish deep fetch enrichment failed:", error instanceof Error ? error.message : "unknown");
    }
  }
  return ranked;
}
