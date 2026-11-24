import { afterEach, describe, expect, it, vi } from "vitest";
import { runOpenKnowledgeTool } from "../src/open-knowledge-tools";

afterEach(() => vi.unstubAllGlobals());
function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), { status, headers: { "content-type": "application/json" } });
}
function apiResponse(value: unknown) {
  return { query: { pages: [value] } };
}

describe("Wave 55 open knowledge discovery", () => {
  it("searches Wikipedia in Vietnamese and normalizes safe article references", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("vi.wikipedia.org");
      expect(url.searchParams.get("list")).toBe("search");
      expect(url.searchParams.get("srsearch")).toBe("địa lý Việt Nam");
      expect(url.searchParams.get("srlimit")).toBe("5");
      expect(url.searchParams.get("maxlag")).toBe("5");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return json({ query: { search: [
        { pageid: 123, title: "Địa lý Việt Nam", snippet: "Vị trí <b>địa lý</b>...", wordcount: 5000, timestamp: "2026-11-22T00:00:00Z" },
        { pageid: "invalid", title: "Invalid" }
      ] } });
    }));
    const result = JSON.parse(await runOpenKnowledgeTool("search_wikipedia_articles", { query: "địa lý Việt Nam", language: "vi", limit: 5 }));
    expect(result.results).toHaveLength(1);
    expect(result.results[0].title).toBe("Địa lý Việt Nam");
    expect(result.results[0].snippet).toBe("Vị trí địa lý ...");
    expect(result.results[0].url).toBe("https://vi.wikipedia.org/wiki/Địa_lý_Việt_Nam");
  });

  it("retrieves a bounded article extract, original page link, categories and thumbnail", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("en.wikipedia.org");
      expect(url.searchParams.get("prop")).toContain("extracts");
      expect(url.searchParams.get("explaintext")).toBe("1");
      expect(url.searchParams.get("exchars")).toBe("8000");
      return json(apiResponse({
        pageid: 42, title: "Douglas Adams", fullurl: "https://en.wikipedia.org/wiki/Douglas_Adams",
        extract: "Douglas Adams was an English author and humorist.",
        thumbnail: { source: "https://upload.wikimedia.org/wikipedia/commons/1/1a/Douglas_Adams.jpg" },
        categories: [{ title: "Category:English humorists" }, { title: "Category:Science fiction writers" }]
      }));
    }));
    const result = JSON.parse(await runOpenKnowledgeTool("get_wikipedia_article", { title: "Douglas Adams" }));
    expect(result.status).toBe("ok");
    expect(result.url).toBe("https://en.wikipedia.org/wiki/Douglas_Adams");
    expect(result.text).toContain("English author");
    expect(result.categories).toEqual(["English humorists", "Science fiction writers"]);
    expect(result.thumbnail_url).toContain("upload.wikimedia.org");
  });

  it("searches Wikivoyage separately from encyclopedia results", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("vi.wikivoyage.org");
      expect(url.searchParams.get("srsearch")).toBe("Hải Phòng");
      return json({ query: { search: [{ pageid: 77, title: "Hải Phòng", snippet: "A port city", wordcount: 900 }] } });
    }));
    const result = JSON.parse(await runOpenKnowledgeTool("search_wikivoyage_guides", { query: "Hải Phòng", language: "vi" }));
    expect(result.results[0].url).toContain("vi.wikivoyage.org/wiki/H%E1%BA%A3i_Ph%C3%B2ng");
    expect(result.note).toContain("travel guide");
  });

  it("retrieves the travel guide text and warns that prices and hours change", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("en.wikivoyage.org");
      return json(apiResponse({
        pageid: 9, title: "Hanoi", fullurl: "https://en.wikivoyage.org/wiki/Hanoi",
        extract: "Hanoi is the capital of Vietnam. See: Old Quarter.",
        categories: [{ title: "Category:Cities" }]
      }));
    }));
    const result = JSON.parse(await runOpenKnowledgeTool("get_wikivoyage_guide", { title: "Hanoi" }));
    expect(result.text).toContain("capital of Vietnam");
    expect(result.note).toContain("opening hours");
  });

  it("looks up a Vietnamese Wiktionary entry without pretending to translate or certify usage", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("vi.wiktionary.org");
      expect(url.searchParams.get("titles")).toBe("an lạc");
      return json(apiResponse({
        pageid: 12, title: "an lạc", fullurl: "https://vi.wiktionary.org/wiki/an_l%E1%BA%A1c",
        extract: "an lạc\nTừ Hán Việt, nghĩa là bình an và vui vẻ."
      }));
    }));
    const result = JSON.parse(await runOpenKnowledgeTool("lookup_wiktionary_entry", { title: "an lạc", language: "vi" }));
    expect(result.source).toBe("Wiktionary");
    expect(result.text).toContain("bình an");
  });

  it("rejects unsupported languages and malformed queries before making requests", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(runOpenKnowledgeTool("search_wikipedia_articles", { query: "test", language: "ru" })).rejects.toThrow("en, vi, ja, fr, es, de");
    await expect(runOpenKnowledgeTool("search_wikivoyage_guides", { query: "x" })).rejects.toThrow("2 to 120");
    expect(mock).not.toHaveBeenCalled();
  });

  it("returns a clear provider rate-limit error and does not retry aggressively", async () => {
    const mock = vi.fn(async () => json({}, 429));
    vi.stubGlobal("fetch", mock);
    await expect(runOpenKnowledgeTool("search_wikipedia_articles", { query: "Mount Fuji" })).rejects.toThrow("rate-limiting");
    expect(mock).toHaveBeenCalledTimes(1);
  });

  it("returns not-found when the selected language has no readable page", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ query: { pages: [{ ns: 0, title: "Unknown", missing: true }] } })));
    const result = JSON.parse(await runOpenKnowledgeTool("get_wikipedia_article", { title: "Unknown" }));
    expect(result.status).toBe("not_found");
  });
});
