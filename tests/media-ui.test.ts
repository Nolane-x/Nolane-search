import { describe, expect, it } from "vitest";
import { mediaAppResponse } from "../src/media-ui";

describe("Media Portal media discovery experience", () => {
  it("serves an audio filter and native player under the archive media CSP", async () => {
    const response = mediaAppResponse();
    const html = await response.text();
    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toContain("no-store");
    expect(response.headers.get("content-security-policy")).toContain("media-src 'self'");
    expect(response.headers.get("content-security-policy")).toContain("https://archive.org");
    expect(response.headers.get("content-security-policy")).toContain("frame-src https:");
    expect(html).toContain('<option value="audio">Chỉ audio</option>');
    expect(html).toContain('data-kind="audio"');
    expect(html).toContain("document.createElement('audio')");
    expect(html).toContain("Mở / tải audio gốc");
    expect(html).toContain("Mở / tải video gốc");
    expect(html).toContain("Hiện chưa có downloader đa website hoặc kho chia sẻ file riêng tư.");
    expect(html).toContain("R2 được kích hoạt trước");
    expect(html).toContain("document.createElement('iframe')");
    expect(html).toContain("Nhúng player PeerTube");
    expect(html).toContain("frame.sandbox.add('allow-scripts')");
  });

  it("keeps the adult-only search control hidden unless the deployment explicitly enables it", async () => {
    const disabledHtml = await (await mediaAppResponse()).text();
    expect(disabledHtml).toContain('data-nsfw-enabled="false"');
    expect(disabledHtml).toContain('id="nsfw-control" class="adult-toggle hidden"');
    const enabledHtml = await (await mediaAppResponse(true)).text();
    expect(enabledHtml).toContain('data-nsfw-enabled="true"');
    expect(enabledHtml).toContain("Tôi xác nhận mình đã đủ 18 tuổi");
    expect(enabledHtml).toContain("query.set('include_nsfw','true')");
  });

  it("disables incompatible providers for image, video and audio filters", async () => {
    const html = await (await mediaAppResponse()).text();
    expect(html).toContain("kind==='audio'?['commons','nasa','openverse','peertube']");
    expect(html).toContain("kind==='video'?['commons','openverse']");
    expect(html).toContain("kind==='image'?['archive','peertube']");
  });

  it("offers PeerTube as a video-only provider and links to the exact origin host", async () => {
    const html = await (await mediaAppResponse()).text();
    expect(html).toContain('<option value="peertube">PeerTube · video liên mạng</option>');
    expect(html).toContain("item.provider==='PeerTube'?safeUrl(item.sourceUrl,[item.instanceHost])");
    expect(html).toContain("item.provider==='PeerTube'?'Xem trên PeerTube':'Trang nguồn'");
    expect(html).toContain("Mở trang PeerTube gốc để xem video");
    expect(html).toContain("PeerTube dùng chỉ mục liên mạng SepiaSearch");
  });
});
