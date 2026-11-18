import { describe, expect, it, vi } from "vitest";
import { parseJsonObjectBody, readJsonResponse } from "../src/http";

describe("bounded JSON request reader", () => {
  it("parses a JSON object from a bounded request stream", async () => {
    const request = new Request("https://example.test/api", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ q: "Cloudflare Workers", mode: "web" }),
    });
    await expect(parseJsonObjectBody(request)).resolves.toEqual({ q: "Cloudflare Workers", mode: "web" });
  });

  it("rejects malformed JSON, arrays and empty request bodies", async () => {
    const malformed = new Request("https://example.test/api", { method: "POST", body: "{" });
    const array = new Request("https://example.test/api", { method: "POST", body: "[]" });
    const empty = new Request("https://example.test/api", { method: "POST" });
    await expect(parseJsonObjectBody(malformed)).resolves.toBeNull();
    await expect(parseJsonObjectBody(array)).resolves.toBeNull();
    await expect(parseJsonObjectBody(empty)).resolves.toBeNull();
  });

  it("cancels and rejects a body when it exceeds the byte budget", async () => {
    let cancelled = false;
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('{"value":"' + "x".repeat(100) + '"}'));
      },
      cancel() { cancelled = true; },
    });
    const request = new Request("https://example.test/api", { method: "POST", body: stream, duplex: "half" } as RequestInit);
    await expect(parseJsonObjectBody(request, 32)).resolves.toBeNull();
    expect(cancelled).toBe(true);
  });
});

describe("bounded JSON response reader", () => {
  it("parses a valid JSON response", async () => {
    const response = new Response(JSON.stringify({ ok: true, rows: [1, 2] }), {
      headers: { "content-type": "application/json" },
    });
    await expect(readJsonResponse<{ ok: boolean; rows: number[] }>(response)).resolves.toEqual({ ok: true, rows: [1, 2] });
  });

  it("rejects a response whose declared content length exceeds the limit", async () => {
    const response = new Response('{"oversized":true}', {
      headers: { "content-length": "1000" },
    });
    await expect(readJsonResponse(response, 32)).rejects.toThrow("exceeded the configured size limit");
  });

  it("cancels a streaming response once it exceeds the byte budget", async () => {
    let cancelled = false;
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('{"data":"' + "x".repeat(100) + '"}'));
      },
      cancel() { cancelled = true; },
    });
    const response = new Response(stream);
    await expect(readJsonResponse(response, 32)).rejects.toThrow("exceeded the configured size limit");
    expect(cancelled).toBe(true);
  });

  it("rejects malformed JSON and empty responses", async () => {
    await expect(readJsonResponse(new Response("{"))).rejects.toThrow("invalid JSON");
    await expect(readJsonResponse(new Response(null))).rejects.toThrow("empty JSON response");
  });
});
