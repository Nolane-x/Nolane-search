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
    expect(response.headers.get("content-security-policy")).toContain("https://inaturalist-open-data.s3.amazonaws.com");
    expect(response.headers.get("content-security-policy")).toContain("frame-src https:");
    expect(html).toContain('<option value="audio">Chỉ audio</option>');
    expect(html).toContain('data-kind="audio"');
    expect(html).toContain("document.createElement('audio')");
    expect(html).toContain("Mở / tải audio gốc");
    expect(html).toContain("Mở / tải video gốc");
    expect(html).toContain("Tải media dung lượng lớn và chia sẻ link riêng tư chưa được bật trên production");
    expect(html).toContain("phương án Media Node miễn phí chạy trên máy cá nhân đang được review tại PR #149");
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
    expect(html).toContain("BROWSER COMPATIBILITY BENCH");
    expect(html).toContain("Playback Lab");
    expect(html).toContain("data-stream-url=\"https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8\"");
    expect(html).toContain("data-stream-url=\"https://storage.googleapis.com/shaka-demo-assets/angel-one-hls/hls.m3u8\"");
    expect(html).toContain("data-stream-url=\"https://mtoczko.github.io/hls-test-streams/test-vtt-ts-segments/playlist.m3u8\"");
    expect(html).toContain("data-stream-url=\"https://storage.googleapis.com/shaka-demo-assets/angel-one/dash.mpd\"");
    expect(html).toContain("data-stream-url=\"https://storage.googleapis.com/shaka-demo-assets/sintel/dash.mpd\"");
    expect(html).toContain("document.querySelectorAll('[data-stream-url]')");
    expect(html).toContain("row.append(caption,select);");
    expect(html).toContain("select.className='stream-rate'");
    expect(html).toContain("video.playbackRate=rate");
    expect(html).toContain("Nguồn thử do bên thứ ba lưu trữ");
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
    expect(csp).toContain("media-src 'self' blob: data:");
    expect(csp).toContain("worker-src 'self' blob:");
    expect(html).toContain("video.canPlayType('application/vnd.apple.mpegurl')");
    expect(html).toContain("function canUseAppleNativeHls()");
    expect(html).toContain("AppleWebKit");
    expect(html).toContain("Apple Computer, Inc");
    expect(html).toContain("blinkOrGecko");
    expect(html).toContain("if(canUseAppleNativeHls()){startNativeHls();return}");
    expect(html).toContain("Đang dùng HLS native của trình duyệt");
    expect(html).toContain("hls.js@1.7.4/dist/hls.min.js");
    expect(html).toContain("dashjs@5.3.0/dist/legacy/umd/dash.all.min.js");
    expect(html).toContain("function startPlayer()");
    expect(html).toContain("function cleanUp()");
    expect(html).toContain("var attempt=++generation");
    expect(html).toContain("if(cancelled||attempt!==generation)return");
    expect(html).toContain("destroyCurrent=function(){hls.destroy()}");
    expect(html).toContain("destroyCurrent=function(){player.destroy()}");
    expect(html).toContain("retry.addEventListener('click',function(){startPlayer()})");
    expect(html).toContain("quality.select.onchange=function()");
    expect(html).not.toContain("quality.select.addEventListener('change'");
    expect(html).toContain("retry.hidden=!retryable");
    expect(html).toContain("stopCurrent();video.pause();video.removeAttribute('src');video.load();");
    expect(html).toContain("Thử phát lại");
    expect(html).toContain("function makeTrackControl(label,ariaLabel)");
    expect(html).toContain("hls.audioTracks");
    expect(html).toContain("hls.audioTrack=selected");
    expect(html).toContain("hls.subtitleTracks");
    expect(html).toContain("hls.subtitleDisplay=true");
    expect(html).toContain("player.getTracksFor('audio')");
    expect(html).toContain("player.setCurrentTrack(track)");
    expect(html).toContain("dashjs.MediaPlayer.events.TEXT_TRACKS_ADDED");
    expect(html).toContain("dashjs.MediaPlayer.events.TEXT_TRACK_ADDED");
    expect(html).toContain("player.setTextTrack(selected)");
    expect(html).toContain("stream-track");
    expect(html).toContain("function makePlaybackRateControl(video)");
    expect(html).toContain("Tốc độ phát");
    expect(html).toContain("[0.5,'0.5×'],[0.75,'0.75×'],[1,'1×'],[1.25,'1.25×'],[1.5,'1.5×'],[2,'2×']");
    expect(html).toContain("video.playbackRate=rate");
    expect(html).toContain("stream-rate");
    expect(html).toContain(".stream-card .preview{display:flex;flex-direction:column;align-items:stretch;aspect-ratio:auto}");
    expect(html).toContain(".stream-card .preview .stream-video{height:auto;max-height:70vh;min-height:230px}");
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
    expect(html).toContain("else{delete streamScriptPromises[key];reject(new Error('Thư viện player không khởi tạo đúng.'))}");
    expect(html).toContain("script.onerror=function(){delete streamScriptPromises[key]");
    expect(html).toContain("function safeMediaStreamUrl(item)");
    expect(html).toContain("function isSafePublicMediaRequest(value)");
    expect(html).toContain("xhr.withCredentials=false");
    expect(html).toContain("initParams.credentials='omit'");
    expect(html).toContain("player.addRequestInterceptor");
    expect(html).toContain("dashjs.Protection.events.LICENSE_REQUEST_SENDING");
    expect(html).not.toContain("dashjs.MediaPlayer.events.LICENSE_REQUEST_SENDING");
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
    expect(html).toContain("kind==='audio'?['commons','nasa','openverse','peertube','inaturalist','met','aic','cleveland']");
    expect(html).toContain("kind==='video'?['commons','openverse','inaturalist','met','aic','cleveland']");
    expect(html).toContain("kind==='image'?['archive','peertube']");
  });

  it("offers The Met Open Access as a trusted image-only source", async () => {
    const response = mediaAppResponse();
    const html = await response.text();
    expect(html).toContain('<option value="met">The Met · ảnh bảo tàng CC0</option>');
    expect(html).toContain("images.metmuseum.org");
    expect(html).toContain("item.provider==='The Met'?safeUrl(item.sourceUrl,['www.metmuseum.org'])");
    expect(html).toContain("The Met Open Access");
    expect(html).toContain("CC0");
  });

  it("offers Art Institute of Chicago as a trusted public-domain image source", async () => {
    const html = await (await mediaAppResponse()).text();
    expect(html).toContain('<option value="aic">Art Institute of Chicago · ảnh public domain</option>');
    expect(html).toContain("www.artic.edu");
    expect(html).toContain("item.provider==='Art Institute of Chicago'?safeUrl(item.sourceUrl,['www.artic.edu'])");
    expect(html).toContain("Art Institute of Chicago và Cleveland Museum of Art bổ sung các tác phẩm có trạng thái public domain/CC0");
  });


  it("offers Cleveland Museum Open Access as a trusted CC0 image-only source", async () => {
    const response = mediaAppResponse();
    const html = await response.text();
    expect(html).toContain('<option value="cleveland">Cleveland Museum of Art · ảnh CC0</option>');
    expect(response.headers.get("content-security-policy")).toContain("https://openaccess-cdn.clevelandart.org");
    expect(html).toContain("item.provider==='Cleveland Museum of Art'?safeUrl(item.sourceUrl,['clevelandart.org','www.clevelandart.org'])");
    expect(html).toContain("Cleveland Museum of Art bổ sung các tác phẩm có trạng thái public domain/CC0");
  });


  it("offers Library of Congress as an image-only source with exact image and item origins", async () => {
    const response = mediaAppResponse();
    const html = await response.text();
    expect(html).toContain('<option value="loc">Library of Congress · ảnh tư liệu</option>');
    expect(response.headers.get("content-security-policy")).toContain("https://tile.loc.gov");
    expect(response.headers.get("content-security-policy")).toContain("https://cdn.loc.gov");
    expect(html).toContain("item.provider==='Library of Congress'?safeUrl(item.sourceUrl,['www.loc.gov'])");
    expect(html).toContain("Library of Congress bổ sung ảnh tư liệu cùng rights advisory theo từng mục");
    expect(html).toContain("không tự động đồng nghĩa ảnh được tự do tái sử dụng");
    expect(html).toContain("kind==='audio'?['commons','nasa','openverse','peertube','inaturalist','met','aic','cleveland','loc']");
    expect(html).toContain("kind==='video'?['commons','openverse','inaturalist','met','aic','cleveland','loc']");
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
