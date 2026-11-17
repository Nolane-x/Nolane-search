import { describe, expect, it } from "vitest";
import { formatDeepReport, formatSearchResults } from "../src/telegram";
import type { SearchResult } from "../src/types";

const result: SearchResult = {
  title: "A <title> & quoted",
  url: "https://example.com/docs?a=1&b=2",
  snippet: "An excerpt with <script>alert(1)</script> & other markup.",
  domain: "example.com",
  provider: "Tavily",
  score: 0.9,
};

function countTag(text: string, tag: string, closing = false): number {
  const pattern = closing
    ? new RegExp("</" + tag + ">", "g")
    : new RegExp("<" + tag + "(?:\\s[^>]*)?>", "g");
  return [...text.matchAll(pattern)].length;
}

describe("Telegram HTML formatting", () => {
  it("escapes untrusted search result text and URLs", () => {
    const output = formatSearchResults("<img src=x onerror=1>", "web", [result]);
    expect(output).toContain("&lt;img");
    expect(output).toContain("&lt;script&gt;");
    expect(output).not.toContain("<script>");
    expect(output).toContain("a=1&amp;b=2");
  });

  it("does not cut HTML tags when input is very long", () => {
    const huge: SearchResult = {
      ...result, title: "&".repeat(5000), snippet: "<".repeat(8000), domain: "&".repeat(500),
    };
    const output = formatSearchResults("x".repeat(5000), "web", Array.from({ length: 8 }, () => huge));
    expect(output.length).toBeLessThanOrEqual(3600);
    for (const tag of ["b", "i", "a", "code"]) {
      expect(countTag(output, tag)).toBe(countTag(output, tag, true));
    }
  });

  it("bounds long Deep Search summaries without breaking markup", () => {
    const output = formatDeepReport("topic", Array.from({ length: 8 }, () => result), "<".repeat(20_000));
    expect(output.length).toBeLessThanOrEqual(3600);
    for (const tag of ["b", "i", "a", "code"]) {
      expect(countTag(output, tag)).toBe(countTag(output, tag, true));
    }
    expect(output).toContain("&lt;");
  });
});
