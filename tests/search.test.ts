import { afterEach, describe, expect, it, vi } from "vitest";
import { normalizeUrl } from "../src/security";
import { buildLocalFtsQuery, feedbackWeight, performSearch, rankAndDeduplicate } from "../src/search";

afterEach(() => vi.unstubAllGlobals());

describe("search URL normalization", () => {
  it("treats tracking-parameter variants as the same URL", () => {
    expect(normalizeUrl("https://example.com/a?utm_source=x&id=2"))
      .toBe(normalizeUrl("https://example.com/a?id=2"));
  });
  it("preserves meaningful query parameters", () => {
    expect(normalizeUrl("https://example.com/search?q=workers")).toContain("q=workers");
  });
});

describe("personal index hybrid retrieval", () => {
  it("builds a parameter-safe broad FTS5 query from meaningful terms", () => {
    expect(buildLocalFtsQuery("the Cloudflare Workers durable objects"))
      .toBe('"cloudflare" OR "workers" OR "durable" OR "objects"');
    expect(buildLocalFtsQuery('"" -- !!!')).toBe("");
  });

  it("federates private indexed pages into ordinary Web search results", async () => {
    const sqlCalls: string[] = [];
    const indexedRows = [{
      title: "Cloudflare Workers Durable Objects — personal notes",
      url: "https://my-docs.example/workers/durable-objects",
      domain: "my-docs.example",
      snippet: "Personal notes about Durable Objects, storage, alarms and Cloudflare Workers.",
      bm25_score: -0.12,
    }];
    const db = {
      prepare(sql: string) {
        sqlCalls.push(sql);
        return {
          bind() { return this; },
          first: async () => null,
          run: async () => ({ results: [], meta: { changes: 1 } }),
          all: async () => ({ results: sql.includes("indexed_pages_fts MATCH") ? indexedRows : [] }),
        };
      },
    };
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.hostname === "en.wikipedia.org") {
        return new Response(JSON.stringify({ query: { search: [{
          title: "Cloudflare Workers reference",
          snippet: "Background reference information about Cloudflare Workers.",
          timestamp: "2026-10-01T00:00:00Z",
        }] } }), { status: 200 });
      }
      throw new Error("Unexpected provider: " + url.hostname);
    }));

    const results = await performSearch({
      DB: db,
    } as never, "Cloudflare Workers Durable Objects", "web");

    expect(sqlCalls.some(sql => sql.includes("indexed_pages_fts MATCH"))).toBe(true);
    expect(results.some(item =>
      item.url === "https://my-docs.example/workers/durable-objects" &&
      item.provider === "Nolane Index · BM25",
    )).toBe(true);
  });

  it("keeps dedicated Wikipedia lookups isolated from the personal index", async () => {
    const sqlCalls: string[] = [];
    const db = {
      prepare(sql: string) {
        sqlCalls.push(sql);
        return {
          bind() { return this; },
          first: async () => null,
          run: async () => ({ results: [], meta: { changes: 1 } }),
          all: async () => ({ results: [] }),
        };
      },
    };
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.hostname === "en.wikipedia.org") {
        return new Response(JSON.stringify({ query: { search: [] } }), { status: 200 });
      }
      throw new Error("Unexpected provider: " + url.hostname);
    }));

    await performSearch({ DB: db } as never, "Cloudflare Workers", "wiki");
    expect(sqlCalls.some(sql => sql.includes("indexed_pages_fts MATCH"))).toBe(false);
  });

  it("uses title-weighted BM25 candidates before the shared relevance reranker", async () => {
    const sqlCalls: Array<{ sql: string; values: unknown[] }> = [];
    const rows = [
      {
        title: "Cloudflare Workers Durable Objects",
        url: "https://docs.example/workers/durable-objects",
        domain: "docs.example",
        snippet: "A guide to Durable Objects on Cloudflare Workers.",
        bm25_score: -0.08,
      },
      {
        title: "Workers overview",
        url: "https://other.example/workers",
        domain: "other.example",
        snippet: "An overview that only briefly mentions Workers.",
        bm25_score: -0.01,
      },
    ];
    const db = {
      prepare(sql: string) {
        let values: unknown[] = [];
        const call = {
          bind(...input: unknown[]) { values = input; return this; },
          first: async () => null,
          all: async () => {
            sqlCalls.push({ sql, values });
            return { results: sql.includes("indexed_pages_fts MATCH") ? rows : [] };
          },
          run: async () => ({ meta: { changes: 1 } }),
        };
        return call;
      },
    };
    const results = await performSearch({
      DB: db,
    } as never, "Cloudflare Workers Durable Objects", "local");

    const retrieval = sqlCalls.find(call => call.sql.includes("indexed_pages_fts MATCH"));
    expect(retrieval).toBeDefined();
    expect(retrieval?.sql).toContain("bm25(indexed_pages_fts, 8.0, 1.0, 0.0, 0.0)");
    expect(retrieval?.values[0]).toBe('"cloudflare" OR "workers" OR "durable" OR "objects"');
    expect(retrieval?.values[1]).toBe(60);
    expect(results[0]?.title).toBe("Cloudflare Workers Durable Objects");
    expect(results[0]?.provider).toBe("Nolane Index · BM25");
  });
});

describe("explicit relevance feedback", () => {
  it("uses a small smoothed boost for positive feedback and penalty for negative feedback", () => {
    expect(feedbackWeight(1, 0)).toBeGreaterThan(0);
    expect(feedbackWeight(0, 1)).toBeLessThan(0);
    expect(feedbackWeight(0, 0)).toBe(0);
    expect(feedbackWeight(1000, 0)).toBeCloseTo(0.1, 3);
    expect(feedbackWeight(0, 1000)).toBeCloseTo(-0.1, 3);
  });
});

describe("multi-signal search ranking", () => {
  it("prefers strong title and snippet matches over a weak provider-only match", () => {
    const base = {
      url: "https://example.com/a",
      domain: "example.com",
      provider: "Test",
      score: 0.95,
    };
    const ranked = rankAndDeduplicate("cloudflare workers durable objects", [
      { ...base, title: "Unrelated product", snippet: "A generic introduction.", url: "https://weak.example/a", domain: "weak.example" },
      { ...base, title: "Cloudflare Workers Durable Objects", snippet: "Official guide to durable objects on Cloudflare Workers.", url: "https://developers.cloudflare.com/workers/durable-objects/", domain: "developers.cloudflare.com" },
    ], "web");
    expect(ranked[0]?.domain).toBe("developers.cloudflare.com");
  });

  it("uses freshness more strongly when the query asks for current information", () => {
    const now = Date.now();
    const recent = new Date(now - 2 * 86_400_000).toISOString();
    const old = new Date(now - 500 * 86_400_000).toISOString();
    const common = { title: "AI model release", snippet: "AI model release and technical details", domain: "example.com", provider: "Test", score: 0.8 };
    const ranked = rankAndDeduplicate("latest AI model release", [
      { ...common, url: "https://old.example/a", domain: "old.example", publishedAt: old },
      { ...common, url: "https://new.example/a", domain: "new.example", publishedAt: recent },
    ], "web");
    expect(ranked[0]?.domain).toBe("new.example");
  });

  it("queries independent fallbacks when a full primary result set is lexically weak", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.hostname === "api.tavily.com") {
        return new Response(JSON.stringify({
          results: Array.from({ length: 8 }, (_, index) => ({
            title: "Unrelated generic page " + index,
            url: "https://generic" + index + ".example/page",
            content: "A general overview with no matching terms.",
            score: 0.9,
          })),
        }), { status: 200, headers: { "content-type": "application/json" } });
      }
      if (url.hostname === "api.exa.ai") {
        return new Response(JSON.stringify({
          results: [{
            title: "Cloudflare Workers Durable Objects guide",
            url: "https://docs.example/cloudflare-workers-durable-objects",
            text: "Technical documentation about Cloudflare Workers and Durable Objects.",
            score: 0.95,
          }],
        }), { status: 200, headers: { "content-type": "application/json" } });
      }
      if (url.hostname === "en.wikipedia.org") {
        return new Response(JSON.stringify({ query: { search: [] } }), { status: 200 });
      }
      throw new Error("Unexpected provider: " + url.hostname);
    });
    vi.stubGlobal("fetch", fetchMock);
    const statement = {
      bind() { return this; },
      first: async () => null,
      run: async () => ({ meta: { changes: 1 } }),
      all: async () => ({ results: [] }),
    };
    const results = await performSearch({
      TAVILY_API_KEY: "test-tavily-key",
      EXA_API_KEY: "test-exa-key",
      DB: { prepare: () => statement },
    } as never, "Cloudflare Workers Durable Objects", "web");
    expect(results[0]?.title).toContain("Cloudflare Workers");
    expect(results.some(item => item.provider === "Exa")).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("returns up to twenty unique results with domain diversification", () => {
    const items = Array.from({ length: 28 }, (_, index) => ({
      title: "Search engine result " + index,
      url: "https://site" + Math.floor(index / 4) + ".example/page-" + index,
      snippet: "Search engine implementation and documentation",
      domain: "site" + Math.floor(index / 4) + ".example",
      provider: "Test",
      score: 0.8,
    }));
    const ranked = rankAndDeduplicate("search engine implementation", items, "web");
    expect(ranked).toHaveLength(20);
    expect(new Set(ranked.map(item => item.url)).size).toBe(20);
    const counts = new Map<string, number>();
    for (const item of ranked.slice(0, 12)) counts.set(item.domain, (counts.get(item.domain) || 0) + 1);
    expect([...counts.values()].every(count => count <= 2)).toBe(true);
  });
});

describe("web search fallback", () => {
  it("uses Exa when Tavily fails instead of reporting no providers", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.hostname === "api.tavily.com") return new Response("upstream unavailable", { status: 503 });
      if (url.hostname === "api.exa.ai") return new Response(JSON.stringify({
        results: [
          { title: "Workers architecture guide", url: "https://exa.example/one", text: "Cloudflare Workers architecture" },
          { title: "Workers deployment reference", url: "https://exa.example/two", text: "Deploy Workers with CI" },
          { title: "Workers runtime overview", url: "https://exa.example/three", text: "Workers runtime documentation" },
        ],
      }), { status: 200, headers: { "content-type": "application/json" } });
      if (url.hostname === "en.wikipedia.org") return new Response(JSON.stringify({
        query: {
          search: [{
            title: "Cloudflare Workers",
            snippet: "Cloudflare Workers is a serverless platform for application execution.",
            timestamp: "2026-10-01T00:00:00Z",
          }],
        },
      }), { status: 200, headers: { "content-type": "application/json" } });
      throw new Error(`Unexpected provider: ${url.hostname}`);
    });
    vi.stubGlobal("fetch", fetchMock);
    const statement = {
      bind() { return this; },
      first: async () => null,
      run: async () => ({ meta: { changes: 1 } }),
      all: async () => ({ results: [] }),
    };
    const env = {
      TAVILY_API_KEY: "test-tavily-key",
      EXA_API_KEY: "test-exa-key",
      DB: { prepare: () => statement },
    };
    const results = await performSearch(env as never, "Cloudflare Workers", "web");
    expect(results.length).toBeGreaterThan(0);
    expect(results.some(item => item.provider === "Exa")).toBe(true);
    expect(results.some(item => item.provider === "Wikipedia (en)")).toBe(true);
    expect(results.length).toBeLessThanOrEqual(20);
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });
});

describe("Wikipedia search mode", () => {
  it("can search the encyclopedia without any paid provider key", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("en.wikipedia.org");
      return new Response(JSON.stringify({
        query: { search: [{ title: "Artificial intelligence", snippet: "A field of computer science.", timestamp: "2026-10-01T00:00:00Z" }] },
      }), { status: 200, headers: { "content-type": "application/json" } });
    }));
    const statement = {
      bind() { return this; },
      first: async () => null,
      run: async () => ({ meta: { changes: 1 } }),
      all: async () => ({ results: [] }),
    };
    const env = { DB: { prepare: () => statement } };
    const results = await performSearch(env as never, "artificial intelligence", "wiki");
    expect(results[0]?.provider).toBe("Wikipedia (en)");
  });
});
