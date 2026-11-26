import { describe, expect, it } from "vitest";
import { createMediaNodeRequest, isMediaNodeConfigured } from "../src/media-downloader";

const TOKEN = "a".repeat(64);
const ENV = {
  MEDIA_NODE_URL: "https://node.personal-tailnet.ts.net",
  MEDIA_NODE_TOKEN: TOKEN,
};

describe("zero-cost self-hosted Media Node connector", () => {
  it("enables only an HTTPS Tailscale Funnel origin with a strong token", () => {
    expect(isMediaNodeConfigured(ENV)).toBe(true);
    expect(isMediaNodeConfigured({ ...ENV, MEDIA_NODE_TOKEN: "" })).toBe(false);
    expect(isMediaNodeConfigured({ ...ENV, MEDIA_NODE_TOKEN: "short" })).toBe(false);
    expect(isMediaNodeConfigured({ ...ENV, MEDIA_NODE_URL: "http://node.personal-tailnet.ts.net" })).toBe(false);
    expect(isMediaNodeConfigured({ ...ENV, MEDIA_NODE_URL: "https://node.example.com" })).toBe(false);
    expect(isMediaNodeConfigured({ ...ENV, MEDIA_NODE_URL: "https://node.personal-tailnet.ts.net:8443" })).toBe(false);
    expect(isMediaNodeConfigured({ ...ENV, MEDIA_NODE_URL: "https://node.personal-tailnet.ts.net/api" })).toBe(false);
    expect(isMediaNodeConfigured({ ...ENV, MEDIA_NODE_URL: "https://127.0.0.1" })).toBe(false);
  });

  it("builds an authenticated internal request", async () => {
    const request = createMediaNodeRequest(
      ENV, 123456, "/internal/start",
      { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ format: "video" }) },
    );
    expect(request).not.toBeNull();
    expect(request!.url).toBe("https://node.personal-tailnet.ts.net/internal/start");
    expect(request!.headers.get("x-nolane-internal")).toBe(TOKEN);
    expect(request!.headers.get("x-nolane-owner-id")).toBe("123456");
    expect(request!.redirect).toBe("error");
    expect(await request!.text()).toContain('"video"');
  });

  it("preserves Range and rejects path escape and other origins", () => {
    const request = createMediaNodeRequest(
      ENV, 123456, "/internal/share-file/7f3dd2d7-4d41-4ef9-9e18-b4f56a510c21",
      { method: "GET", headers: { range: "bytes=0-99" } }, 0,
    );
    expect(request?.headers.get("range")).toBe("bytes=0-99");
    expect(createMediaNodeRequest(ENV, 123456, "/internal/../health")).toBeNull();
    expect(createMediaNodeRequest(ENV, 123456, "https://example.org/internal/start")).toBeNull();
    expect(createMediaNodeRequest(ENV, 0, "/internal/status/id")).toBeNull();
  });
});


describe("Media Node streaming cancellation", () => {
  it("preserves the caller AbortSignal when the stream has no fixed timeout", () => {
    const controller = new AbortController();
    const request = createMediaNodeRequest(
      ENV, 123456,
      "/internal/share-file/7f3dd2d7-4d41-4ef9-9e18-b4f56a510c21",
      { method: "GET", signal: controller.signal },
      0,
    );
    expect(request).not.toBeNull();
    controller.abort();
    expect(request!.signal.aborted).toBe(true);
  });
});
