import { describe, expect, it } from "vitest";
import { applySearchFilters, parseSearchQuery } from "../src/query";
import type { SearchResult } from "../src/types";

function result(overrides: Partial<SearchResult> = {}): SearchResult {
  return {
    title: "Cloudflare Workers documentation",
    url: "https://developers.cloudflare.com/workers/guide.pdf",
    snippet: "A guide to Cloudflare Workers.",
    domain: "developers.cloudflare.com",
    provider: "Tavily",
    score: 0.9,
    publishedAt: "2026-01-15T12:00:00Z",
    ...overrides,
  };
}

describe("Google-style search operators", () => {
  it("removes recognized operators from the ranking and local query", () => {
    const parsed = parseSearchQuery("cloudflare workers site:github.com filetype:pdf intitle:workers after:2026-01-01 before:2026-02-01");
    expect(parsed.providerQuery).toContain("site:github.com");
    expect(parsed.rankingQuery).toBe("cloudflare workers");
    expect(parsed.localQuery).toBe("cloudflare workers");
    expect(parsed.filters.sites).toEqual(["github.com"]);
    expect(parsed.filters.filetypes).toEqual(["pdf"]);
    expect(parsed.filters.titleTerms).toEqual(["workers"]);
    expect(parsed.filters.after).toBe(Date.parse("2026-01-01T00:00:00.000Z"));
    expect(parsed.filters.beforeExclusive).toBe(Date.parse("2026-02-02T00:00:00.000Z"));
  });

  it("preserves invalid operator values as ordinary query text", () => {
    const parsed = parseSearchQuery("workers after:2026-02-30 filetype:pdfx!");
    expect(parsed.rankingQuery).toBe("workers after:2026-02-30 filetype:pdfx!");
    expect(parsed.filters.after).toBeNull();
    expect(parsed.filters.filetypes).toEqual([]);
  });

  it("filters exact domains and their subdomains without accepting lookalike suffixes", () => {
    const parsed = parseSearchQuery("workers site:github.com");
    const results = applySearchFilters(parsed, [
      result({ domain: "github.com" }),
      result({ domain: "docs.github.com" }),
      result({ domain: "github.com.evil.test" }),
    ]);
    expect(results.map(item => item.domain)).toEqual(["github.com", "docs.github.com"]);
  });

  it("filters file extensions and title tokens", () => {
    const parsed = parseSearchQuery("workers filetype:pdf intitle:Cloudflare");
    const results = applySearchFilters(parsed, [
      result(),
      result({ url: "https://example.com/guide.html", domain: "example.com" }),
      result({ title: "Workers manual", url: "https://example.com/file.pdf", domain: "example.com" }),
    ]);
    expect(results).toHaveLength(1);
    expect(results[0]?.url).toContain(".pdf");
  });

  it("uses inclusive after/before calendar dates and excludes unknown dates", () => {
    const parsed = parseSearchQuery("workers after:2026-01-10 before:2026-01-20");
    const results = applySearchFilters(parsed, [
      result({ publishedAt: "2026-01-10T00:00:00Z" }),
      result({ publishedAt: "2026-01-20T00:00:00Z" }),
      result({ publishedAt: undefined }),
      result({ publishedAt: "2026-01-15T12:00:00Z" }),
    ]);
    expect(results).toHaveLength(2);
    expect(results.map(item => item.publishedAt)).toEqual([
      "2026-01-10T00:00:00Z", "2026-01-15T12:00:00Z",
    ]);
  });
});
