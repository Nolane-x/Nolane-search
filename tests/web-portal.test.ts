import { describe, expect, it } from "vitest";
import worker from "../src/index";
import type { Env, ExecutionContext } from "../src/types";

const env = {} as Env;
const context = { waitUntil() {} } as ExecutionContext;

describe("private browser search portal", () => {
  it("serves a responsive search and chat interface with no-store security headers", async () => {
    const response = await worker.fetch(new Request("https://nolane-search.example/"), env, context);
    const html = await response.text();
    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toContain("text/html");
    expect(response.headers.get("cache-control")).toContain("no-store");
    expect(response.headers.get("content-security-policy")).toContain("frame-ancestors 'none'");
    expect(html).toContain("Nolane Search");
    expect(html).toContain('id="mediaBtn"');
    expect(html).toContain("AI Overview");
    expect(html).toContain("Nolane Chat");
    expect(html).toContain("Personal Web Index");
    expect(html).toContain("indexFilter");
    expect(html).toContain("indexMore");
    expect(html).toContain("Gỡ domain");
    expect(html).toContain("feedback-btn");
    expect(html).toContain("data-mode=\"research\"");
    expect(html).toContain('id="chatFile"');
    expect(html).toContain('id="clearChatFile"');
    expect(html).toContain("/api/ai/upload");
    expect(html).toContain("Tối đa 20 MB");
  });

  it("serves the Telegram Mini App shell without exposing private data before authentication", async () => {
    const response = await worker.fetch(new Request("https://nolane-search.example/telegram"), env, context);
    const html = await response.text();
    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toContain("no-store");
    expect(response.headers.get("content-security-policy")).toContain("frame-ancestors 'none'");
    expect(html).toContain("NOLANE");
    expect(html).toContain('data-tab="tools"');
    expect(html).toContain("/api/auth/me");
  });

  it("keeps Mini App job retry owner-session protected and rejects cross-origin requests", async () => {
    const anonymous = await worker.fetch(new Request("https://nolane-search.example/api/tools/jobs/retry", {
      method: "POST",
      headers: { origin: "https://nolane-search.example", "content-type": "application/json" },
      body: JSON.stringify({ jobId: "12345678-1234-1234-1234-123456789abc" }),
    }), env, context);
    expect(anonymous.status).toBe(401);

    const crossOrigin = await worker.fetch(new Request("https://nolane-search.example/api/tools/jobs/retry", {
      method: "POST",
      headers: { origin: "https://attacker.example", "content-type": "application/json" },
      body: JSON.stringify({ jobId: "12345678-1234-1234-1234-123456789abc" }),
    }), env, context);
    expect(crossOrigin.status).toBe(403);
  });

  it("does not expose search results to anonymous browser requests", async () => {
    const response = await worker.fetch(new Request("https://nolane-search.example/api/search?q=hello"), env, context);
    expect(response.status).toBe(401);
    expect(await response.json()).toMatchObject({ error: expect.stringContaining("Phiên đăng nhập") });
  });

  it("keeps site crawl and feedback APIs private", async () => {
    const crawl = await worker.fetch(new Request("https://nolane-search.example/api/crawl", {
      method: "POST",
      headers: { "content-type": "application/json", origin: "https://nolane-search.example" },
      body: JSON.stringify({ url: "https://example.com", maxPages: 5 }),
    }), env, context);
    expect(crawl.status).toBe(401);

    const crawls = await worker.fetch(new Request("https://nolane-search.example/api/crawls"), env, context);
    expect(crawls.status).toBe(401);

    const index = await worker.fetch(new Request("https://nolane-search.example/api/index"), env, context);
    expect(index.status).toBe(401);

    const deleteIndex = await worker.fetch(new Request("https://nolane-search.example/api/index/delete", {
      method: "POST",
      headers: { "content-type": "application/json", origin: "https://nolane-search.example" },
      body: JSON.stringify({ domain: "example.com" }),
    }), env, context);
    expect(deleteIndex.status).toBe(401);

    const aiUpload = await worker.fetch(new Request("https://nolane-search.example/api/ai/upload", {
      method: "POST",
      headers: { origin: "https://nolane-search.example", "content-type": "multipart/form-data; boundary=test" },
      body: "--test--\\r\\n",
    }), env, context);
    expect(aiUpload.status).toBe(401);

    const feedback = await worker.fetch(new Request("https://nolane-search.example/api/feedback", {
      method: "POST",
      headers: { "content-type": "application/json", origin: "https://nolane-search.example" },
      body: JSON.stringify({ eventId: "12345678-1234-1234-1234-123456789abc", url: "https://example.com", rating: 1 }),
    }), env, context);
    expect(feedback.status).toBe(401);
  });

  it("rejects cross-origin AI file uploads before authentication or file parsing", async () => {
    const response = await worker.fetch(new Request("https://nolane-search.example/api/ai/upload", {
      method: "POST",
      headers: { origin: "https://attacker.example", "content-type": "multipart/form-data; boundary=test" },
      body: "--test--\\r\\n",
    }), env, context);
    expect(response.status).toBe(403);
  });

  it("rejects cross-origin ticket exchanges before accessing D1", async () => {
    const response = await worker.fetch(new Request("https://nolane-search.example/api/auth/exchange", {
      method: "POST",
      headers: { "content-type": "application/json", origin: "https://attacker.example" },
      body: JSON.stringify({ ticket: "a".repeat(64) }),
    }), env, context);
    expect(response.status).toBe(403);
  });
  it("serves the private Media Portal and keeps media discovery API session-protected", async () => {
    const page = await worker.fetch(new Request("https://nolane-search.example/media"), env, context);
    expect(page.status).toBe(302);
    expect(page.headers.get("location")).toBe("https://nolane-search.example/");

    const search = await worker.fetch(new Request("https://nolane-search.example/api/media/search?q=nebula"), env, context);
    expect(search.status).toBe(401);
    expect(await search.json()).toMatchObject({ error: expect.stringContaining("Phiên đăng nhập") });

    const audioSearch = await worker.fetch(new Request("https://nolane-search.example/api/media/search?q=public+lecture&kind=audio"), env, context);
    expect(audioSearch.status).toBe(401);
    expect(await audioSearch.json()).toMatchObject({ error: expect.stringContaining("Phiên đăng nhập") });
  });
});
