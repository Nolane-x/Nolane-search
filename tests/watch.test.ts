import { afterEach, describe, expect, it, vi } from "vitest";
import { crawlAndIndexSite } from "../src/watch";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());

function makeEnv() {
  const batch = vi.fn(async () => []);
  const statement = {
    bind() { return this; },
    first: async () => null,
    run: async () => ({ meta: { changes: 1 } }),
    all: async () => ({ results: [] }),
  };
  return {
    env: { DB: { prepare: () => statement, batch } } as unknown as Env,
    batch,
  };
}

describe("bounded same-origin site crawler", () => {
  it("seeds from sitemap, indexes only same-origin HTML pages and respects the page cap", async () => {
    const requested: string[] = [];
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      requested.push(url.toString());
      if (url.pathname === "/robots.txt") {
        return new Response("User-agent: *\nAllow: /\nSitemap: https://example.com/sitemap.xml", {
          status: 200, headers: { "content-type": "text/plain" },
        });
      }
      if (url.pathname === "/sitemap.xml") {
        return new Response(
          "<urlset><url><loc>https://example.com/docs</loc></url><url><loc>https://evil.example/steal</loc></url><url><loc>https://example.com/blog</loc></url></urlset>",
          { status: 200, headers: { "content-type": "application/xml" } },
        );
      }
      if (url.pathname === "/") {
        return new Response(
          "<html><title>Home</title><body><main>Welcome to the example public website with enough indexable text for our private search index.</main><a href='/docs'>Docs</a><a href='https://evil.example/steal'>External</a></body></html>",
          { status: 200, headers: { "content-type": "text/html; charset=utf-8" } },
        );
      }
      if (url.pathname === "/docs") {
        return new Response(
          "<html><title>Documentation</title><body><main>Documentation for the public example website. This page contains useful searchable text and instructions.</main></body></html>",
          { status: 200, headers: { "content-type": "text/html; charset=utf-8" } },
        );
      }
      throw new Error("Unexpected fetch " + url.toString());
    }));
    const { env, batch } = makeEnv();

    const result = await crawlAndIndexSite(env, "https://example.com/", 2);

    expect(result.indexed).toBe(2);
    expect(result.pages.map(page => page.title)).toEqual(["Home", "Documentation"]);
    expect(result.discovered).toBeGreaterThanOrEqual(3);
    expect(requested.some(url => url.includes("evil.example"))).toBe(false);
    expect(batch).toHaveBeenCalledTimes(2);
  });

  it("does not fetch paths disallowed by robots.txt", async () => {
    const requested: string[] = [];
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      requested.push(url.toString());
      if (url.pathname === "/robots.txt") {
        return new Response("User-agent: *\nDisallow: /private", {
          status: 200, headers: { "content-type": "text/plain" },
        });
      }
      if (url.pathname === "/sitemap.xml") {
        return new Response("<urlset></urlset>", { status: 200, headers: { "content-type": "application/xml" } });
      }
      throw new Error("A robots-disallowed page must not be fetched.");
    }));
    const { env, batch } = makeEnv();

    const result = await crawlAndIndexSite(env, "https://example.com/private", 5);

    expect(result.indexed).toBe(0);
    expect(result.skipped).toBe(1);
    expect(requested.some(url => url.includes("/private"))).toBe(false);
    expect(batch).not.toHaveBeenCalled();
  });
});
