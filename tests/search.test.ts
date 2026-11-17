import { afterEach, describe, expect, it, vi } from "vitest";
import { normalizeUrl } from "../src/security";
import { performSearch } from "../src/search";

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
    expect(results.every(item => item.provider === "Exa")).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
