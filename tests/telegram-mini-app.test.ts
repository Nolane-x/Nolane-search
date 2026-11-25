import { describe, expect, it } from "vitest";
import { telegramMiniAppResponse } from "../src/telegram-mini-app-ui";

describe("Telegram Mini App workspace", () => {
  it("serves a private, theme-aware Telegram Web App without introducing a new origin", async () => {
    const response = telegramMiniAppResponse();
    const html = await response.text();
    const csp = response.headers.get("content-security-policy") || "";
    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toContain("no-store");
    expect(response.headers.get("x-content-type-options")).toBe("nosniff");
    expect(csp).toContain("https://telegram.org");
    expect(csp).toContain("connect-src 'self'");
    expect(csp).toContain("frame-ancestors 'none'");
    expect(html).toContain("Telegram.WebApp");
    expect(html).toContain("themeParams");
    expect(html).toContain("tg-content-safe-area-inset-bottom");
    expect(html).toContain("BackButton");
    expect(html).toContain('data-tab="home"');
    expect(html).toContain('data-tab="search"');
    expect(html).toContain('data-tab="ai"');
    expect(html).toContain('data-tab="tools"');
    expect(html).toContain('data-tab="library"');
    expect(html).toContain("/api/auth/exchange");
    expect(html).toContain("/api/auth/me");
    expect(html).toContain("/api/search?");
    expect(html).toContain("/api/ask");
    expect(html).toContain("/api/chat");
    expect(html).toContain("/api/ai/upload");
    expect(html).toContain("/api/tools/catalog");
    expect(html).toContain("/api/tools/jobs");
    expect(html).toContain("/api/index?");
    expect(html).toContain("/api/crawl");
    expect(html).toContain("/api/crawls");
  });

  it("serves syntactically valid inline Mini App JavaScript", async () => {
    const html = await (await telegramMiniAppResponse()).text();
    const start = html.indexOf("<script>\n");
    const end = html.indexOf("</script>", start);
    expect(start).toBeGreaterThanOrEqual(0);
    expect(end).toBeGreaterThan(start);
    const script = html.slice(start + "<script>\n".length, end);
    expect(() => new Function(script)).not.toThrow();
  });

  it("uses only same-origin application APIs and the Telegram SDK", async () => {
    const html = await (await telegramMiniAppResponse()).text();
    expect(html).toContain('src="https://telegram.org/js/telegram-web-app.js"');
    expect(html).toContain("credentials:'same-origin'");
    expect(html).toContain("history.replaceState({},'',location.pathname+location.hash)");
    expect(html).toContain("var initialTab=(location.hash||'').slice(1)");
    expect(html).toContain("localStorage");
    expect(html).not.toContain("api.openai.com");
    expect(html).not.toContain("api.telegram.org/bot");
  });
});
