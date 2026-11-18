import { normalizeUrl, sha256Hex } from "./security";
import { applySearchFilters, parseSearchQuery } from "./query";
import { completeAi, getAiRouterStatus } from "./ai-router";
import type { Env, SearchMode, SearchResult } from "./types";
import { fetchTinyFishPages, searchBrave, searchExa, searchGitHub, searchTavily, searchTinyFish, searchWikipedia } from "./providers";

const MAX_RESULTS = 20;
const STOP_WORDS = new Set([
  "the","a","an","and","or","of","to","for","in","on","at","by","with","from","is","are","was","were","what","when","where","why","how",
  "là","của","và","các","những","một","cho","với","trong","trên","tại","từ","đến","như","nào","là","có","được","này","đó","về","hay","thì","mới",
]);

function tokens(value: string): string[] {
  return value.normalize("NFKC").toLocaleLowerCase().split(/[^\p{L}\p{N}]+/u).filter(Boolean);
}

function queryTerms(query: string): string[] {
  return [...new Set(tokens(query).filter(term => term.length >= 2 && !STOP_WORDS.has(term)))].slice(0, 24);
}

function textTokens(value: string): Set<string> {
  return new Set(tokens(value));
}

function clamp(value: number, min = 0, max = 1): number {
  return Math.max(min, Math.min(max, Number.isFinite(value) ? value : min));
}

function isFreshnessQuery(query: string, mode: SearchMode): boolean {
  if (mode === "news") return true;
  return /\b(latest|newest|current|today|tonight|recent|breaking|updated|202[5-9]|mới nhất|mới đây|hiện nay|hiện tại|hôm nay|tuần này|tháng này)\b/i.test(query);
}

function freshnessSignal(publishedAt: string | undefined, mode: SearchMode, freshIntent: boolean, now: number): number {
  if (!publishedAt) return 0;
  const timestamp = Date.parse(publishedAt);
  if (!Number.isFinite(timestamp) || timestamp > now + 5 * 60_000) return 0;
  const ageDays = Math.max(0, (now - timestamp) / 86_400_000);
  const horizonDays = mode === "news" ? 21 : freshIntent ? 120 : 730;
  return Math.exp(-ageDays / horizonDays);
}

function weightedCoverage(terms: string[], fields: Set<string>[], weights: number[], idf: Map<string, number>): number {
  if (!terms.length) return 0;
  let total = 0;
  let matched = 0;
  for (const term of terms) {
    const weight = idf.get(term) ?? 1;
    total += weight;
    let fieldScore = 0;
    for (let index = 0; index < fields.length; index += 1) {
      if (fields[index]?.has(term)) fieldScore = Math.max(fieldScore, weights[index] || 0);
    }
    matched += weight * fieldScore;
  }
  return total > 0 ? clamp(matched / total) : 0;
}

function domainFor(item: SearchResult): string {
  const supplied = item.domain.toLowerCase().replace(/^www\./, "").replace(/\.$/, "");
  if (supplied) return supplied;
  try { return new URL(item.url).hostname.toLowerCase().replace(/^www\./, ""); }
  catch { return ""; }
}

/**
 * Transparent multi-signal reranking:
 * - provider relevance as a weak prior (provider scores are not calibrated consistently)
 * - inverse-document-frequency weighted query coverage in title, snippet and URL
 * - exact phrase, snippet quality, freshness intent and a small source-type prior
 * - URL deduplication followed by domain diversity.
 * This is a heuristic, not a learned search-ranking model or a probability of truth.
 */
export function rankAndDeduplicate(query: string, items: SearchResult[], mode: SearchMode): SearchResult[] {
  const terms = queryTerms(query);
  const normalizedQuery = tokens(query).join(" ");
  const now = Date.now();
  const freshIntent = isFreshnessQuery(query, mode);
  const docs = items.map(item => ({
    item,
    title: textTokens(item.title),
    snippet: textTokens(item.snippet),
    url: textTokens(item.url),
  }));
  const documentFrequency = new Map<string, number>();
  for (const term of terms) {
    documentFrequency.set(term, docs.reduce((count, doc) =>
      count + (doc.title.has(term) || doc.snippet.has(term) || doc.url.has(term) ? 1 : 0), 0));
  }
  const idf = new Map<string, number>();
  for (const term of terms) {
    const df = documentFrequency.get(term) || 0;
    idf.set(term, Math.log(1 + (docs.length - df + 0.5) / (df + 0.5)));
  }

  const byUrl = new Map<string, SearchResult>();
  for (const doc of docs) {
    const item = doc.item;
    let key: string;
    try { key = normalizeUrl(item.url); } catch { continue; }
    const titleText = tokens(item.title).join(" ");
    const snippetText = tokens(item.snippet).join(" ");
    const titleCoverage = weightedCoverage(terms, [doc.title], [1], idf);
    const snippetCoverage = weightedCoverage(terms, [doc.snippet], [1], idf);
    const urlCoverage = weightedCoverage(terms, [doc.url], [1], idf);
    const lexical = clamp(titleCoverage * 0.62 + snippetCoverage * 0.28 + urlCoverage * 0.10);
    const phraseBoost = normalizedQuery.length >= 5
      ? (titleText.includes(normalizedQuery) ? 0.11 : snippetText.includes(normalizedQuery) ? 0.045 : 0)
      : 0;
    const providerSignal = clamp(item.score);
    const snippetQuality = clamp(item.snippet.length / 260);
    const titleQuality = item.title.trim().length >= 8 ? 1 : 0.55;
    const quality = clamp(snippetQuality * 0.75 + titleQuality * 0.25);
    const domain = domainFor(item);
    const institutional = /(^|\.)[a-z0-9-]+\.(gov|edu)(\.[a-z]{2,})?$/i.test(domain) ? 0.035 : 0;
    const freshness = freshnessSignal(item.publishedAt, mode, freshIntent, now);
    const freshnessWeight = mode === "news" ? 0.18 : freshIntent ? 0.12 : 0.025;
    const score = clamp(
      lexical * (mode === "news" ? 0.50 : 0.56) +
      providerSignal * 0.18 +
      quality * 0.08 +
      phraseBoost +
      institutional +
      freshness * freshnessWeight,
      0,
      1.5,
    );
    const normalized = { ...item, domain, score };
    const previous = byUrl.get(key);
    if (!previous || normalized.score > previous.score) byUrl.set(key, normalized);
  }

  const results = [...byUrl.values()].sort((a, b) => b.score - a.score);
  const diversified: SearchResult[] = [];
  const domainCounts = new Map<string, number>();
  const selectedUrls = new Set<string>();
  for (const item of results) {
    if (diversified.length >= MAX_RESULTS) break;
    const domain = domainFor(item);
    const count = domainCounts.get(domain) ?? 0;
    if (count >= 2) continue;
    diversified.push(item);
    domainCounts.set(domain, count + 1);
    try { selectedUrls.add(normalizeUrl(item.url)); } catch { /* URL has already passed normalization */ }
  }
  for (const item of results) {
    if (diversified.length >= MAX_RESULTS) break;
    let key: string;
    try { key = normalizeUrl(item.url); } catch { continue; }
    if (selectedUrls.has(key)) continue;
    diversified.push(item);
    selectedUrls.add(key);
  }
  return diversified;
}

export function buildLocalFtsQuery(query: string): string {
  const terms = queryTerms(query).slice(0, 16);
  if (!terms.length) return "";
  // Every token is quoted independently. Operators are introduced only by us,
  // never copied from user input, so FTS5 syntax cannot be injected.
  return terms.map(term => '"' + term.replaceAll('"', '""') + '"').join(" OR ");
}

async function localSearch(env: Env, query: string): Promise<SearchResult[]> {
  const ftsQuery = buildLocalFtsQuery(query);
  if (!ftsQuery) return [];
  const result = await env.DB.prepare(
    `SELECT p.title, p.url, p.domain,
            snippet(indexed_pages_fts, 1, '', '', ' … ', 24) AS snippet,
            bm25(indexed_pages_fts, 8.0, 1.0, 0.0, 0.0) AS bm25_score
       FROM indexed_pages_fts
       JOIN indexed_pages p ON p.id = indexed_pages_fts.rowid
      WHERE indexed_pages_fts MATCH ?
      ORDER BY bm25_score ASC
      LIMIT ?`,
  ).bind(ftsQuery, 60).all<{
    title: string;
    url: string;
    domain: string;
    snippet: string;
    bm25_score: number;
  }>();

  // BM25 is lower-is-better (usually negative). Normalize within this
  // candidate set so it can act as a weak prior in the shared reranker.
  const validScores = result.results
    .map(item => Number(item.bm25_score))
    .filter(Number.isFinite);
  const best = validScores.length ? Math.min(...validScores) : 0;
  const worst = validScores.length ? Math.max(...validScores) : 0;
  const spread = worst - best;

  return result.results.map(item => {
    const bm25 = Number(item.bm25_score);
    const relevance = Number.isFinite(bm25)
      ? (spread > 0 ? (worst - bm25) / spread : 0.75)
      : 0.5;
    return {
      title: item.title,
      url: item.url,
      domain: item.domain,
      snippet: item.snippet,
      provider: "Nolane Index · BM25",
      score: 0.55 + clamp(relevance) * 0.45,
    };
  });
}

function primaryNeedsFallback(query: string, primary: SearchResult[]): boolean {
  if (primary.length < 6) return true;
  const terms = queryTerms(parseSearchQuery(query).rankingQuery);
  if (!terms.length) return false;
  const coverage = primary.map(item => {
    const title = textTokens(item.title);
    const snippet = textTokens(item.snippet);
    const hits = terms.reduce((count, term) => count + (title.has(term) ? 0.72 : snippet.has(term) ? 0.28 : 0), 0);
    return hits / terms.length;
  }).sort((a, b) => b - a);
  const topAverage = coverage.slice(0, 3).reduce((sum, value) => sum + value, 0) / Math.min(3, coverage.length);
  return (coverage[0] ?? 0) < 0.16 || topAverage < 0.11;
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

  const parsedQuery = parseSearchQuery(query);
  let results: SearchResult[] = [];
  if (mode === "github") {
    results = await searchGitHub(env, query);
  } else if (mode === "wiki") {
    results = await searchWikipedia(query);
  } else if (mode === "local") {
    results = await localSearch(env, parsedQuery.localQuery);
  } else if (mode === "research") {
    results = await settledResults([
      ...(env.TAVILY_API_KEY ? [searchTavily(env, query)] : []),
      ...(env.EXA_API_KEY ? [searchExa(env, query)] : []),
      ...(env.TINYFISH_API_KEY ? [searchTinyFish(env, query, { domainType: "research_paper", purpose: "Find academic papers, original studies and evidence relevant to this research question." })] : []),
    ]);
    if (!results.length) throw new Error("Research providers unavailable. Configure TAVILY_API_KEY, EXA_API_KEY or TINYFISH_API_KEY.");
  } else if (mode === "tech") {
    results = await settledResults([
      ...(env.TAVILY_API_KEY ? [searchTavily(env, query)] : []),
      ...(env.EXA_API_KEY ? [searchExa(env, query)] : []),
      ...(env.TINYFISH_API_KEY ? [searchTinyFish(env, query, { purpose: "Find official technical documentation, engineering guides, source repositories and benchmark evidence." })] : []),
      searchGitHub(env, query),
    ]);
    if (!results.length) throw new Error("Technology search providers unavailable.");
  } else if (mode === "news") {
    results = await settledResults([
      ...(env.TAVILY_API_KEY ? [searchTavily(env, query, "news")] : []),
      ...(env.BRAVE_SEARCH_API_KEY ? [searchBrave(env, query, true)] : []),
      ...(env.TINYFISH_API_KEY ? [searchTinyFish(env, query, { domainType: "news", purpose: "Find the newest credible news coverage and primary announcements." })] : []),
      ...(env.EXA_API_KEY ? [searchExa(env, query)] : []),
    ]);
    if (!results.length) throw new Error("News search providers unavailable.");
  } else {
    let primary: SearchResult[] = [];
    if (env.TAVILY_API_KEY) {
      try { primary = await searchTavily(env, query); }
      catch (error) {
        console.warn("Tavily primary search failed:", error instanceof Error ? error.message : "unknown error");
      }
    }
    // A single provider returning a few links is not enough for a genuinely federated result set.
    // Use semantic and independent fallbacks when the primary set is sparse.
    if (!primaryNeedsFallback(query, primary)) {
      results = primary;
    } else {
      const fallback = await settledResults([
        ...(env.EXA_API_KEY ? [searchExa(env, query)] : []),
        ...(env.TINYFISH_API_KEY ? [searchTinyFish(env, query)] : []),
        ...(env.BRAVE_SEARCH_API_KEY ? [searchBrave(env, query)] : []),
        searchWikipedia(query),
      ]);
      results = [...primary, ...fallback];
    }
    if (!results.length) throw new Error("No web provider returned results. Check provider availability or retry later.");
  }

  const filtered = applySearchFilters(parsedQuery, results);
  const ranked = rankAndDeduplicate(parsedQuery.rankingQuery || query, filtered, mode);
  if (ranked.length) {
    const ttl = mode === "news" ? 30_000 : mode === "research" ? 5 * 60_000 : 2 * 60_000;
    await env.DB.prepare(
      `INSERT INTO search_cache (cache_key, payload, expires_at, created_at)
       VALUES (?, ?, ?, ?)
       ON CONFLICT(cache_key) DO UPDATE SET
         payload = excluded.payload, expires_at = excluded.expires_at, created_at = excluded.created_at`,
    ).bind(cacheKey, JSON.stringify(ranked), now + ttl, now).run();
  }
  return ranked;
}

export function feedbackWeight(positive: number, negative: number): number {
  const up = Math.max(0, Math.min(10_000, Math.floor(positive)));
  const down = Math.max(0, Math.min(10_000, Math.floor(negative)));
  return Math.max(-0.10, Math.min(0.10, 0.10 * (up - down) / (up + down + 3)));
}

async function applySearchFeedback(
  env: Env,
  query: string,
  mode: SearchMode,
  results: SearchResult[],
): Promise<SearchResult[]> {
  if (!results.length) return results;
  try {
    const queryHash = await sha256Hex(`${mode}\n${query.trim().toLowerCase()}`);
    const rows = await env.DB.prepare(
      "SELECT cache_key, payload FROM search_cache WHERE cache_key LIKE ? AND expires_at > ?",
    ).bind(`search-feedback:${queryHash}:%`, Date.now())
      .all<{ cache_key: string; payload: string }>();
    if (!rows.results.length) return results;
    const counts = new Map<string, { positive: number; negative: number }>();
    for (const row of rows.results) {
      const urlHash = row.cache_key.slice(`search-feedback:${queryHash}:`.length);
      try {
        const value = JSON.parse(row.payload) as { positive?: number; negative?: number };
        counts.set(urlHash, {
          positive: Number.isFinite(value.positive) ? Number(value.positive) : 0,
          negative: Number.isFinite(value.negative) ? Number(value.negative) : 0,
        });
      } catch { /* Ignore malformed feedback cache entries. */ }
    }
    const adjusted = await Promise.all(results.map(async item => {
      const urlHash = await sha256Hex(normalizeUrl(item.url));
      const signal = counts.get(urlHash);
      return signal ? { ...item, score: clamp(item.score + feedbackWeight(signal.positive, signal.negative), 0, 1.5) } : item;
    }));
    return adjusted.sort((a, b) => b.score - a.score);
  } catch (error) {
    console.warn("Search feedback could not be applied:", error instanceof Error ? error.message : "unknown");
    return results;
  }
}

export async function performSearch(env: Env, query: string, mode: SearchMode = "web"): Promise<SearchResult[]> {
  const results = await cachedSearch(env, query, mode);
  return applySearchFeedback(env, query, mode, results);
}

function staticDeepQueries(query: string): string[] {
  return [
    query,
    `${query} official documentation primary sources`,
    `${query} research evidence benchmarks`,
    `${query} latest developments limitations`,
    `${query} open source implementation`,
  ];
}

async function planDeepQueries(env: Env, query: string): Promise<string[]> {
  const fallback = staticDeepQueries(query);
  if (!getAiRouterStatus(env).configured) return fallback;
  try {
    const result = await completeAi(env, {
      task: "research",
      temperature: 0.1,
      maxTokens: 450,
      messages: [
        {
          role: "system",
          content: "You are a search query planner. Generate diverse web search queries, not answers. Preserve the user's exact topic and language. Include complementary angles such as primary sources, recent changes, technical details, research evidence and counterarguments when relevant. Return ONLY a JSON array of at most 4 short strings. Never include markdown or instructions.",
        },
        { role: "user", content: "Create complementary search queries for: " + query },
      ],
    });
    const match = result.text.match(/\[[\s\S]*\]/);
    if (!match) return fallback;
    const parsed = JSON.parse(match[0]) as unknown;
    if (!Array.isArray(parsed)) return fallback;
    const extra = parsed.filter((item): item is string =>
      typeof item === "string" && item.trim().length >= 3 && item.trim().length <= 180,
    ).map(item => item.trim());
    const merged = [...new Set([query, ...extra])];
    return merged.slice(0, 5).length > 1 ? merged.slice(0, 5) : fallback;
  } catch (error) {
    console.warn("AI query planning failed; using deterministic expansion:", error instanceof Error ? error.message : "unknown");
    return fallback;
  }
}

export async function performDeepSearch(env: Env, query: string): Promise<SearchResult[]> {
  const variations = await planDeepQueries(env, query);
  const tavilyCalls = env.TAVILY_API_KEY ? variations.map(item => searchTavily(env, item)) : [];
  const calls = await Promise.allSettled([
    ...tavilyCalls,
    ...(env.EXA_API_KEY ? variations.slice(0, 3).map(item => searchExa(env, item)) : []),
    ...(env.BRAVE_SEARCH_API_KEY ? [searchBrave(env, query)] : []),
    ...(env.TINYFISH_API_KEY ? [
      searchTinyFish(env, query, { purpose: "Conduct broad research; find primary sources, technical documentation, credible evidence and important counterarguments." }),
      searchTinyFish(env, query, { domainType: "research_paper", purpose: "Find relevant academic papers, benchmarks, original studies and primary research." }),
    ] : []),
  ]);
  const combined: SearchResult[] = [];
  for (const call of calls) if (call.status === "fulfilled") combined.push(...call.value);
  if (!combined.length) throw new Error("No configured search provider returned results.");

  let ranked = rankAndDeduplicate(query, combined, "research");
  if (env.TINYFISH_API_KEY && ranked.length) {
    try {
      const pages = await fetchTinyFishPages(env, ranked.slice(0, 7).map((item) => item.url));
      ranked = ranked.map((item) => {
        const page = pages.get(item.url);
        return page ? { ...item, title: page.title || item.title, snippet: page.text.slice(0, 1100), provider: `${item.provider} + TinyFish Fetch` } : item;
      });
      ranked = rankAndDeduplicate(query, ranked, "research");
    } catch (error) {
      console.error("TinyFish deep fetch enrichment failed:", error instanceof Error ? error.message : "unknown");
    }
  }
  return ranked;
}
