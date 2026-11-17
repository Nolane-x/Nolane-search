import type { SearchResult } from "./types";

export interface SearchFilters {
  sites: string[];
  filetypes: string[];
  titleTerms: string[];
  after: number | null;
  beforeExclusive: number | null;
}

export interface ParsedSearchQuery {
  /** Original query including supported operators, sent to external providers. */
  providerQuery: string;
  /** Terms with valid recognized operators removed, used by ranking. */
  rankingQuery: string;
  /** Plain terms with filters removed, used by the local FTS index. */
  localQuery: string;
  filters: SearchFilters;
}

function validDateStart(value: string): number | null {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
  const timestamp = Date.parse(value + "T00:00:00.000Z");
  if (!Number.isFinite(timestamp) || new Date(timestamp).toISOString().slice(0, 10) !== value) return null;
  return timestamp;
}

/** Parse a safe, intentionally small Google-style operator set. Unknown or invalid syntax stays in the query. */
export function parseSearchQuery(query: string): ParsedSearchQuery {
  const filters: SearchFilters = {
    sites: [],
    filetypes: [],
    titleTerms: [],
    after: null,
    beforeExclusive: null,
  };
  const removable: Array<[number, number]> = [];
  const pattern = /(?:^|\s)(site|filetype|intitle|after|before):([^\s]+)/gi;

  for (const match of query.matchAll(pattern)) {
    const full = match[0];
    const operator = (match[1] || "").toLowerCase();
    const value = (match[2] || "").trim();
    const index = match.index ?? 0;
    let valid = false;

    if (operator === "site") {
      const domain = value.toLowerCase().replace(/^https?:\/\//, "").replace(/^www\./, "").replace(/\/.*$/, "");
      if (domain.length <= 253 && /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\.[a-z]{2,}$/i.test(domain) &&
          !domain.includes("..")) {
        filters.sites.push(domain);
        valid = true;
      }
    } else if (operator === "filetype") {
      if (/^[a-z0-9]{1,12}$/i.test(value)) {
        filters.filetypes.push(value.toLowerCase());
        valid = true;
      }
    } else if (operator === "intitle") {
      if (value.length >= 2 && value.length <= 80) {
        filters.titleTerms.push(value.toLowerCase());
        valid = true;
      }
    } else if (operator === "after") {
      const date = validDateStart(value);
      if (date !== null) {
        filters.after = filters.after === null ? date : Math.max(filters.after, date);
        valid = true;
      }
    } else if (operator === "before") {
      const date = validDateStart(value);
      if (date !== null) {
        const exclusive = date + 86_400_000;
        filters.beforeExclusive = filters.beforeExclusive === null
          ? exclusive
          : Math.min(filters.beforeExclusive, exclusive);
        valid = true;
      }
    }

    if (valid) removable.push([index, index + full.length]);
  }

  let rankingQuery = query;
  for (const [start, end] of removable.sort((a, b) => b[0] - a[0])) {
    rankingQuery = rankingQuery.slice(0, start) + " " + rankingQuery.slice(end);
  }
  rankingQuery = rankingQuery.replace(/\s+/g, " ").trim();
  return {
    providerQuery: query,
    rankingQuery,
    localQuery: rankingQuery,
    filters,
  };
}

function matchesDomain(domain: string, requested: string): boolean {
  const normalized = domain.toLowerCase().replace(/^www\./, "").replace(/\.$/, "");
  return normalized === requested || normalized.endsWith("." + requested);
}

function tokens(value: string): string[] {
  return value.toLowerCase().split(/[^\p{L}\p{N}]+/u).filter(Boolean);
}

/** Apply parsed operators locally as a second guard, even if a provider ignores them. */
export function applySearchFilters(parsed: ParsedSearchQuery, results: SearchResult[]): SearchResult[] {
  const { sites, filetypes, titleTerms, after, beforeExclusive } = parsed.filters;
  if (!sites.length && !filetypes.length && !titleTerms.length && after === null && beforeExclusive === null) {
    return results;
  }

  return results.filter(item => {
    if (sites.length && !sites.some(site => matchesDomain(item.domain, site))) return false;

    if (filetypes.length) {
      let pathname = "";
      try { pathname = new URL(item.url).pathname.toLowerCase(); } catch { return false; }
      if (!filetypes.some(type => pathname.endsWith("." + type))) return false;
    }

    if (titleTerms.length) {
      const titleTokens = new Set(tokens(item.title));
      if (!titleTerms.every(term => tokens(term).every(token => titleTokens.has(token)))) return false;
    }

    if (after !== null || beforeExclusive !== null) {
      const published = item.publishedAt ? Date.parse(item.publishedAt) : NaN;
      // Date filtering is strict: unknown publication dates cannot prove the requested range.
      if (!Number.isFinite(published)) return false;
      if (after !== null && published < after) return false;
      if (beforeExclusive !== null && published >= beforeExclusive) return false;
    }
    return true;
  });
}
