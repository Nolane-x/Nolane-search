import { afterEach, describe, expect, it, vi } from "vitest";
import { fetchTinyFishPages, parseOpenRouterModels, searchBrave, searchTinyFish, searchWikipedia, wikipediaLanguageForQuery } from "../src/providers";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("OpenRouter model routing", () => {
  it("parses ordered model lists and removes duplicates", () => {
    expect(parseOpenRouterModels({
      OPENROUTER_MODELS: "openai/gpt-4.1-mini, deepseek/deepseek-chat\nqwen/qwen3.5-32b",
      OPENROUTER_MODEL: "openai/gpt-4.1-mini",
    })).toEqual([
      "openai/gpt-4.1-mini",
      "deepseek/deepseek-chat",
      "qwen/qwen3.5-32b",
    ]);
  });

  it("keeps the legacy single-model secret working", () => {
    expect(parseOpenRouterModels({ OPENROUTER_MODEL: "openai/gpt-4.1-mini" }))
      .toEqual(["openai/gpt-4.1-mini"]);
  });

  it("limits routing to eight model candidates", () => {
    const models = Array.from({ length: 12 }, (_, index) => `provider/model-${index}`).join(",");
    expect(parseOpenRouterModels({ OPENROUTER_MODELS: models })).toHaveLength(8);
  });
});

describe("TinyFish Search adapter", () => {
  it("sends the API key and normalizes structured results", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.search.tinyfish.ai");
      expect(url.searchParams.get("query")).toContain("Cloudflare Workers");
      expect(url.searchParams.get("query")).toContain("academic papers");
      expect(url.searchParams.has("domain_type")).toBe(false);
      expect(url.searchParams.has("purpose")).toBe(false);
      expect(url.searchParams.get("location")).toBe("VN");
      expect(url.searchParams.get("language")).toBe("vi");
      expect(new Headers(init?.headers).get("X-API-Key")).toBe("tinyfish-test-key");
      return new Response(JSON.stringify({
        results: [{
          position: 1,
          site_name: "arxiv.org",
          title: "A Research Paper",
          snippet: "An abstract excerpt",
          url: "https://arxiv.org/abs/1234.5678",
        }, {
          position: 2,
          title: "Credential URL must be rejected",
          url: "https://user:password@example.com/private",
          snippet: "untrusted result",
        }],
      }), { status: 200, headers: { "content-type": "application/json" } });
    });
    vi.stubGlobal("fetch", fetchMock);

    const results = await searchTinyFish(
      { TINYFISH_API_KEY: "tinyfish-test-key" } as never,
      "Cloudflare Workers",
      { domainType: "research_paper", location: "VN", language: "vi" },
    );

    expect(results).toHaveLength(1);
    expect(results[0]).toMatchObject({
      title: "A Research Paper",
      url: "https://arxiv.org/abs/1234.5678",
      domain: "arxiv.org",
      provider: "TinyFish",
      snippet: "An abstract excerpt",
    });
  });
});

describe("TinyFish Fetch adapter", () => {
  it("maps extracted content to both original and final URLs", async () => {
    vi.stubGlobal("fetch", vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => new Response(JSON.stringify({
      results: [{
        url: "https://example.com/article",
        final_url: "https://www.example.com/article",
        title: "Example article",
        text: "# Extracted content",
      }],
    }), { status: 200, headers: { "content-type": "application/json" } })));

    const pages = await fetchTinyFishPages(
      { TINYFISH_API_KEY: "tinyfish-test-key" } as never,
      ["https://example.com/article"],
    );

    expect(pages.get("https://example.com/article")?.text).toBe("# Extracted content");
    expect(pages.get("https://www.example.com/article")?.title).toBe("Example article");
  });

  it("does not send private or unsafe URLs to TinyFish", async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => new Response(JSON.stringify({ results: [{ url: "https://example.com/valid", title: "Valid", text: "safe content" }] }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    const pages = await fetchTinyFishPages(
      { TINYFISH_API_KEY: "tinyfish-test-key" } as never,
      ["http://127.0.0.1/admin", "https://example.com/valid"],
    );
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const request = fetchMock.mock.calls[0]?.[1];
    expect(JSON.parse(String(request?.body)).urls).toEqual(["https://example.com/valid"]);
    expect(pages.has("https://example.com/valid")).toBe(true);
  });
});

describe("publication date normalization", () => {
  it("converts Brave relative ages into comparable timestamps", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify({
      web: { results: [{ title: "Recent result", url: "https://example.com/recent", description: "Fresh information", age: "2 days ago" }] },
    }), { status: 200, headers: { "content-type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);
    const results = await searchBrave({ BRAVE_SEARCH_API_KEY: "brave-test-key" } as never, "latest news");
    expect(results).toHaveLength(1);
    const timestamp = Date.parse(results[0]!.publishedAt || "");
    expect(Number.isFinite(timestamp)).toBe(true);
    expect(Date.now() - timestamp).toBeGreaterThanOrEqual(2 * 86_400_000 - 3000);
    expect(Date.now() - timestamp).toBeLessThan(2 * 86_400_000 + 3000);
  });
});

describe("Wikipedia reference search", () => {
  it("selects Vietnamese Wikipedia for Vietnamese queries and English otherwise", () => {
    expect(wikipediaLanguageForQuery("trí tuệ nhân tạo")).toBe("vi");
    expect(wikipediaLanguageForQuery("artificial intelligence")).toBe("en");
  });

  it("uses the public MediaWiki search API and sanitizes result snippets", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("vi.wikipedia.org");
      expect(url.pathname).toBe("/w/api.php");
      expect(url.searchParams.get("action")).toBe("query");
      expect(url.searchParams.get("list")).toBe("search");
      expect(url.searchParams.get("srsearch")).toBe("trí tuệ nhân tạo");
      expect(url.searchParams.get("srlimit")).toBe("6");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return new Response(JSON.stringify({
        query: {
          search: [{
            title: "Trí tuệ nhân tạo",
            snippet: "Đây là <span class=\"searchmatch\">trí tuệ</span> nhân tạo &amp; học máy.",
            timestamp: "2026-11-01T10:00:00Z",
          }],
        },
      }), { status: 200, headers: { "content-type": "application/json" } });
    });
    vi.stubGlobal("fetch", fetchMock);

    const results = await searchWikipedia("trí tuệ nhân tạo");
    expect(results).toHaveLength(1);
    expect(results[0]).toMatchObject({
      title: "Trí tuệ nhân tạo",
      url: "https://vi.wikipedia.org/wiki/Tr%C3%AD_tu%E1%BB%87_nh%C3%A2n_t%E1%BA%A1o",
      snippet: "Đây là trí tuệ nhân tạo & học máy.",
      domain: "vi.wikipedia.org",
      provider: "Wikipedia (vi)",
    });
  });
});
