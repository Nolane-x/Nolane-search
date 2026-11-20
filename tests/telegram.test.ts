import { describe, expect, it } from "vitest";
import { buildBackHomeKeyboard, buildHomeKeyboard, buildModePromptKeyboard, buildSearchKeyboard, buildToolCenterKeyboard, buildToolCategoryKeyboard, buildToolDetailKeyboard, buildToolSearchKeyboard, formatDeepReport, formatHomeMenu, formatModePrompt, formatSearchResults, formatToolCenterHome, formatToolCategoryPage, formatToolDetail, formatToolSearchResults, SEARCH_PAGE_SIZE } from "../src/telegram";
import { TOOL_CATALOG, getTool } from "../src/tools";
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

describe("Telegram interactive workspace UI", () => {
  it("builds a menu with all search/AI modes and a web workspace URL", () => {
    const menu = buildHomeKeyboard();
    const buttons = menu.inline_keyboard.flat();
    expect(buttons.some(button => button.callback_data === "ui:mode:web")).toBe(true);
    expect(buttons.some(button => button.callback_data === "ui:mode:ask")).toBe(true);
    expect(buttons.some(button => button.callback_data === "ui:mode:deep")).toBe(true);
    expect(buttons.some(button => button.callback_data === "ui:mode:local")).toBe(true);
    expect(buttons.some(button => button.callback_data === "tc:home")).toBe(true);
    expect(buttons.some(button => button.url?.startsWith("https://"))).toBe(true);
    expect(buttons.every(button => new TextEncoder().encode(button.callback_data || "").length <= 64)).toBe(true);
  });

  it("shows an explicit next-message prompt and cancel/home navigation", () => {
    expect(formatHomeMenu("<admin>")).toContain("&lt;admin&gt;");
    expect(formatModePrompt("ask")).toContain("AI trả lời có nguồn");
    expect(buildModePromptKeyboard().inline_keyboard[0]?.map(button => button.callback_data)).toEqual(["ui:cancel", "ui:home"]);
    expect(buildBackHomeKeyboard().inline_keyboard[0]?.[0]?.callback_data).toBe("ui:home");
  });
});


describe("Telegram Tool Center UI", () => {
  it("shows every active category and navigates into paginated tool listings", () => {
    const home = formatToolCenterHome(TOOL_CATALOG, true);
    expect(home).toContain("94 processor");
    expect(home).toContain("Lập trình &amp; văn bản");
    const keyboard = buildToolCenterKeyboard(TOOL_CATALOG);
    const callbacks = keyboard.inline_keyboard.flat().map(button => button.callback_data).filter(Boolean) as string[];
    expect(callbacks).toContain("tc:developer");
    expect(callbacks).toContain("tc:jobs");
    expect(callbacks).toContain("tc:workflows");
    const page = formatToolCategoryPage(TOOL_CATALOG, "developer", 0);
    expect(page).toContain("markdown-outline");
    const pageKeyboard = buildToolCategoryKeyboard(TOOL_CATALOG, "developer", 0);
    expect(pageKeyboard.inline_keyboard.flat().some(button => button.callback_data === "td:markdown-outline")).toBe(true);
    expect(pageKeyboard.inline_keyboard.flat().every(button => new TextEncoder().encode(button.callback_data || "").length <= 64)).toBe(true);
  });

  it("shows tool details and use action with compact callbacks", () => {
    const tool = getTool("code-secret-scan")!;
    expect(formatToolDetail(tool)).toContain("giá trị bí mật");
    const buttons = buildToolDetailKeyboard(tool).inline_keyboard.flat();
    expect(buttons.some(button => button.callback_data === "tu:code-secret-scan")).toBe(true);
    expect(buttons.every(button => new TextEncoder().encode(button.callback_data || "").length <= 64)).toBe(true);
  });

  it("renders search results and buttons only for the bounded shortlist", () => {
    const matches = TOOL_CATALOG.filter(tool => tool.id.includes("markdown"));
    expect(formatToolSearchResults(matches, "markdown")).toContain("2 kết quả");
    const buttons = buildToolSearchKeyboard(matches).inline_keyboard.flat();
    expect(buttons.map(button => button.callback_data)).toContain("td:markdown-links");
  });
});

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

  it("paginates search results with stable numbering", () => {
    const results = Array.from({ length: 20 }, (_, index) => ({
      ...result, title: `Result ${index + 1}`, url: `https://example.com/${index + 1}`,
    }));
    const first = formatSearchResults("topic", "web", results, 0, SEARCH_PAGE_SIZE);
    const second = formatSearchResults("topic", "web", results, 1, SEARCH_PAGE_SIZE);
    const third = formatSearchResults("topic", "web", results, 2, SEARCH_PAGE_SIZE);
    expect(first).toContain("Kết quả 1–5 / 20");
    expect(first).toContain("1. <a");
    expect(first).toContain("5. <a");
    expect(first).not.toContain("6. <a");
    expect(second).toContain("Kết quả 6–10 / 20");
    expect(second).toContain("6. <a");
    expect(third).toContain("Kết quả 11–15 / 20");
    expect(third).toContain("15. <a");
    const fourth = formatSearchResults("topic", "web", results, 3, SEARCH_PAGE_SIZE);
    expect(fourth).toContain("Kết quả 16–20 / 20");
    expect(fourth).toContain("20. <a");
  });

  it("creates owner-session pagination and contextual follow-up actions", () => {
    const keyboard = buildSearchKeyboard("12345678-1234-1234-1234-123456789abc", 1, 12);
    expect(keyboard?.inline_keyboard[0]?.map(button => button.text)).toEqual(["⬅️ Trước", "2/3", "Tiếp ➡️"]);
    expect(keyboard?.inline_keyboard[0]?.[0]?.callback_data).toBe("ns:12345678-1234-1234-1234-123456789abc:0");
    const singlePage = buildSearchKeyboard("12345678-1234-1234-1234-123456789abc", 0, 5);
    expect(singlePage.inline_keyboard[0]?.map(button => button.text)).toEqual(["🤖 Hỏi AI có nguồn", "📚 Deep Search"]);
    expect(singlePage.inline_keyboard[1]?.[0]?.callback_data).toBe("ui:home");
    expect(singlePage.inline_keyboard[0]?.[0]?.callback_data).toBe("na:ask:12345678-1234-1234-1234-123456789abc");
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
