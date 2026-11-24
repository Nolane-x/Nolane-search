import { describe, expect, it } from "vitest";
import { mediaAppResponse } from "../src/media-ui";

describe("Media Portal audio experience", () => {
  it("serves an audio filter and native player under the archive media CSP", async () => {
    const response = mediaAppResponse();
    const html = await response.text();
    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toContain("no-store");
    expect(response.headers.get("content-security-policy")).toContain("media-src 'self'");
    expect(response.headers.get("content-security-policy")).toContain("https://archive.org");
    expect(html).toContain('<option value="audio">Chỉ audio</option>');
    expect(html).toContain('data-kind="audio"');
    expect(html).toContain("document.createElement('audio')");
    expect(html).toContain("Mở audio gốc");
  });

  it("disables image/video-only providers for incompatible media filters", async () => {
    const html = await (await mediaAppResponse()).text();
    expect(html).toContain("kind==='audio'?['commons','nasa','openverse']");
    expect(html).toContain("kind==='video'?['commons','openverse']");
    expect(html).toContain("kind==='image'?['archive']");
  });
});
