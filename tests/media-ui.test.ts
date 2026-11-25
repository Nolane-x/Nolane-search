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
    expect(html).toContain("safeMediaEmbedUrl(item)");
    expect(html).toContain("Nhúng player '+item.provider");
    expect(html).toContain("u.origin===location.origin");
    expect(html).toContain("frameUrl.searchParams.set('p2p','0')");
    expect(html).toContain("frameUrl.searchParams.set('dnt','1')");
    expect(html).toContain("strict-origin-when-cross-origin");
    expect(html).toContain("frame.sandbox.add('allow-scripts','allow-same-origin','allow-popups','allow-forms','allow-presentation')");
    expect(html).toContain("/api/media/resolve?url='+encodeURIComponent(q)");
    expect(html).toContain("var isUrl=q.indexOf('https://')===0||q.indexOf('http://')===0");
    expect(html).toContain('maxlength="2048"');
  });

  it("serves syntactically valid inline browser JavaScript", async () => {
    const html = await (await mediaAppResponse()).text();
    const start = html.indexOf("<script>");
    const end = html.indexOf("</script>", start);
    expect(start).toBeGreaterThanOrEqual(0);
    expect(end).toBeGreaterThan(start);
    const script = html.slice(start + "<script>".length, end);
    expect(() => new Function(script)).not.toThrow();
  });

  it("serves HLS and DASH players lazily with request and CSP restrictions", async () => {
    const response = mediaAppResponse();
    const html = await response.text();
    const csp = response.headers.get("content-security-policy") || "";
    expect(csp).toContain("https://cdn.jsdelivr.net");
    expect(csp).toContain("connect-src 'self' https:");
    expect(csp).toContain("media-src 'self' blob:");
    expect(csp).toContain("worker-src 'self' blob:");
    expect(html).toContain("hls.js@1.7.4/dist/hls.min.js");
    expect(html).toContain("dashjs@5.3.0/dist/legacy/umd/dash.all.min.js");
    expect(html).toContain("function startPlayer()");
    expect(html).toContain("function cleanUp()");
    expect(html).toContain("var attempt=++generation");
    expect(html).toContain("if(cancelled||attempt!==generation)return");
    expect(html).toContain("destroyCurrent=function(){hls.destroy()}");
    expect(html).toContain("destroyCurrent=function(){player.destroy()}");
    expect(html).toContain("retry.addEventListener('click',function(){startPlayer()})");
    expect(html).toContain("Thử phát lại");
    expect(html).toContain("function makeQualityControl()");
    expect(html).toContain("function populateQualityControl(control,representations)");
    expect(html).toContain("hls.currentLevel=selected");
    expect(html).toContain("Hls.Events.LEVELS_UPDATED");
    expect(html).toContain("Hls.Events.LEVEL_SWITCHED");
    expect(html).toContain("player.getRepresentationsByType('video')");
    expect(html).toContain("var dashRepresentations=[]");
    expect(html).toContain("dashRepresentations[event.newQuality]");
    expect(html).toContain("bitrateInKbit");
    expect(html).toContain("autoSwitchBitrate:{video:false}");
    expect(html).toContain("autoSwitchBitrate:{video:true}");
    expect(html).toContain("player.setRepresentationForTypeByIndex('video',selected,true)");
    expect(html).toContain("Chất lượng");
    expect(html).toContain("function safeMediaStreamUrl(item)");
    expect(html).toContain("function isSafePublicMediaRequest(value)");
    expect(html).toContain("xhr.withCredentials=false");
    expect(html).toContain("initParams.credentials='omit'");
    expect(html).toContain("player.addRequestInterceptor");
    expect(html).toContain("dashjs.MediaPlayer.events.LICENSE_REQUEST_SENDING");
    expect(html).toContain("player.destroy()");
    expect(html).toContain("request.credentials='omit'");
    expect(html).toContain("item.streamType?null:anchor");
    expect(html).toContain("clearStreamPlayers()");
    expect(html).toContain("Phát '+(item.streamType==='hls'?'HLS':'DASH')");
  });

  it("renders Twitch VOD and Clip embeds only with the official host and current-page parent", async () => {
    const html = await (await mediaAppResponse()).text();
    expect(html).toContain("item.provider==='Twitch'?['player.twitch.tv','clips.twitch.tv']:[]");
    expect(html).toContain("u.hostname==='player.twitch.tv'");
    expect(html).toContain("u.hostname==='clips.twitch.tv'");
    expect(html).toContain("frameUrl.searchParams.set('parent',parent)");
    expect(html).toContain("var parent=location.hostname.toLowerCase()");
    expect(html).toContain("item.provider==='Twitch'?'Mở trên Twitch'");
    expect(html).toContain("strict-origin-when-cross-origin");
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
    expect(html).toContain("item.provider==='PeerTube'?'Xem trên PeerTube':item.provider==='YouTube'?'Mở trên YouTube'");
    expect(html).toContain("Mở trang PeerTube gốc để xem video");
    expect(html).toContain("PeerTube dùng chỉ mục liên mạng SepiaSearch");
  });
});
