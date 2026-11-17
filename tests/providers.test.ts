import { afterEach, describe, expect, it, vi } from "vitest";
import { parseOpenRouterModels, searchTinyFish } from "../src/providers";

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
      expect(new Headers(init?.headers).get("X-API-Key")).toBe("tinyfish-test-key");
      return new Response(JSON.stringify({
        results: [{
          position: 1,
          site_name: "arxiv.org",
          title: "A Research Paper",
          snippet: "An abstract excerpt",
          url: "https://arxiv.org/abs/1234.5678",
        }],
      }), { status: 200, headers: { "content-type": "application/json" } });
    });
    vi.stubGlobal("fetch", fetchMock);

    const results = await searchTinyFish(
      { TINYFISH_API_KEY: "tinyfish-test-key" } as never,
      "Cloudflare Workers",
      { domainType: "research_paper" },
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
