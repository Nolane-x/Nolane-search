const HTML = String.raw`<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#101827"><meta name="robots" content="noindex,nofollow">
<title>Nolane Search · Media</title>
<style>
:root{color-scheme:dark;--bg:#0b1220;--panel:#121d2f;--panel2:#18253a;--line:#26354d;--ink:#edf3ff;--muted:#9aabc4;--accent:#84a8ff;--blue:#456ff0;--radius:17px}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top,#172641 0,#0b1220 48rem);color:var(--ink);font:15px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}button,input,select{font:inherit}button,a{cursor:pointer}a{color:inherit}.shell{max-width:1280px;margin:0 auto;padding:0 24px}.top{height:72px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);background:#0b1220cc;backdrop-filter:blur(15px);position:sticky;top:0;z-index:4}.brand{text-decoration:none;font-size:19px;font-weight:800;letter-spacing:-.04em;display:flex;align-items:center;gap:10px}.mark{width:34px;height:34px;display:grid;place-items:center;background:linear-gradient(140deg,#416df0,#789cff);border-radius:12px;box-shadow:0 6px 20px #406df044}.toplinks{display:flex;gap:9px;align-items:center}.toplinks a,.toplinks button{border:1px solid var(--line);background:#172339;color:#cfdbf1;text-decoration:none;padding:8px 13px;border-radius:999px;font-size:13px}.toplinks a:hover,.toplinks button:hover{border-color:#688ce8}.hero{text-align:center;padding:58px 0 30px}.eyebrow{display:inline-block;color:#a8c0ff;border:1px solid #334a77;background:#172846;border-radius:999px;padding:5px 11px;font-size:12px;font-weight:700}.hero h1{font-size:clamp(32px,4.7vw,53px);letter-spacing:-.055em;line-height:1.1;margin:15px 0 12px}.hero p{max-width:680px;margin:0 auto;color:var(--muted);font-size:15px}.search{max-width:860px;margin:25px auto 0;display:grid;grid-template-columns:1fr auto auto;gap:9px}.search input,.search select{min-width:0;border:1px solid #2d3d58;background:#111e31;color:var(--ink);padding:13px 15px;border-radius:13px;outline:none}.search input:focus,.search select:focus{border-color:#789cff;box-shadow:0 0 0 3px #638aff22}.btn{border:0;background:#557df5;color:white;font-weight:700;padding:0 19px;border-radius:13px}.btn:disabled{opacity:.6;cursor:wait}.tabs{display:flex;justify-content:center;flex-wrap:wrap;gap:8px;margin:21px auto 0}.tab{border:1px solid var(--line);background:#111e31;color:#aebed7;padding:8px 17px;border-radius:999px}.tab.active{background:#263f70;color:white;border-color:#527ddc}
.playback-lab{max-width:1040px;margin:24px auto 4px;text-align:left;border:1px solid #2b3c59;border-radius:20px;padding:17px;background:linear-gradient(140deg,#172944,#101a2b 68%,#151d32);box-shadow:0 16px 42px #0002}
.lab-heading{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin:0 0 13px}.lab-kicker{font-size:10px;font-weight:850;letter-spacing:.14em;color:#91adff}.lab-heading h2{font-size:20px;letter-spacing:-.035em;margin:4px 0}.lab-heading p{font-size:12px;color:var(--muted);margin:0;max-width:650px}.lab-badge{flex:0 0 auto;padding:5px 8px;border:1px solid #38517c;border-radius:999px;background:#1a2c49;color:#b8caff;font-size:10px;font-weight:800}
.lab-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.lab-sample{display:flex;flex-direction:column;align-items:flex-start;gap:4px;text-align:left;min-width:0;border:1px solid #2c405e;border-radius:14px;padding:11px 12px;background:#111e31;color:var(--ink);transition:border-color .15s,transform .15s}.lab-sample:hover{border-color:#789cff;transform:translateY(-1px)}.lab-type{color:#9eb7ff;font-size:9px;font-weight:850;letter-spacing:.1em}.lab-sample strong{font-size:12px}.lab-sample>span:nth-last-child(2){color:var(--muted);font-size:10px;line-height:1.45}.lab-action{width:100%;display:flex;justify-content:space-between;align-items:center;margin-top:4px;color:#c7d7ff;font-size:10px;font-weight:800}.lab-action b{font-size:15px}
.lab-footnote{color:#8495af;font-size:10px;line-height:1.55;margin:12px 2px 0}
@media(max-width:640px){.playback-lab{padding:13px;margin-top:18px}.lab-grid{grid-template-columns:1fr}.lab-heading{gap:8px}.lab-badge{font-size:9px}}.meta{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:26px 0 14px;color:var(--muted);font-size:13px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:17px;padding-bottom:70px}.card{background:linear-gradient(160deg,#152239,#111a2a);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;min-width:0;box-shadow:0 12px 32px #0002}.preview{aspect-ratio:16/10;background:#080e18;display:grid;place-items:center;overflow:hidden}.preview img,.preview video{width:100%;height:100%;object-fit:contain}.preview iframe{width:100%;height:100%;min-height:220px;border:0;background:#080e18}.stream-video{display:block;width:100%;max-height:70vh;min-height:230px;background:#000}.stream-status{padding:10px 12px;color:#aebed5;font-size:12px;overflow-wrap:anywhere}.stream-controls{display:flex;align-items:center;gap:9px;padding:4px 12px 12px;color:#aebed5;font-size:12px}.stream-quality,.stream-rate,.stream-track{max-width:min(100%,250px);padding:6px 9px;border:1px solid var(--line);border-radius:9px;background:#142238;color:var(--ink)}.stream-controls[hidden]{display:none}.stream-card{grid-column:span 2}.stream-card .preview{display:flex;flex-direction:column;align-items:stretch;aspect-ratio:auto}.stream-card .preview .stream-video{height:auto;max-height:70vh;min-height:230px}.card.twitch-card{grid-column:span 2}.preview audio{width:min(100%,560px);max-width:100%}.embed-load{border:1px solid #536c9a;background:#172a49;color:#e5edff;padding:10px 14px;border-radius:10px;font-weight:700}.embed-load:hover{border-color:#86a9ff;background:#203b66}.no-preview{color:#8da2c4;font-size:13px;padding:25px;text-align:center}.body{padding:14px 15px 15px}.body h2{font-size:15px;line-height:1.35;margin:0 0 7px}.description{color:#9fb0c9;font-size:12px;line-height:1.55;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;min-height:55px}.badges{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}.badge{font-size:10px;border-radius:999px;background:#203453;color:#aec6ff;padding:3px 8px}.credit{font-size:11px;color:#8195b3;overflow-wrap:anywhere}.actions{display:flex;gap:8px;margin-top:12px}.actions a{display:inline-flex;align-items:center;justify-content:center;min-height:34px;text-decoration:none;padding:6px 11px;border-radius:9px;background:#20375c;color:#d8e5ff;font-size:12px;font-weight:650}.actions a.primary{background:#416cdd;color:white}.notice,.empty{margin:16px 0;background:#142238;border:1px solid #2b3e5c;color:#aebed5;padding:18px;border-radius:14px}.notice strong,.empty strong{color:#e8f0ff}.adult-toggle{display:flex;align-items:center;justify-content:center;gap:8px;max-width:860px;margin:12px auto 0;padding:11px 14px;border:1px solid #785c36;background:#33281b;color:#ffe0ad;border-radius:12px;font-size:12px}.adult-toggle input{accent-color:#e5a54c;width:17px;height:17px}.small{font-size:11px;color:#7186a4;margin-top:6px}.footer{padding:16px 0 34px;color:#7285a2;font-size:11px;border-top:1px solid var(--line)}.hidden{display:none!important}
@media(max-width:900px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:620px){.card.twitch-card,.card.stream-card{grid-column:auto}.shell{padding:0 15px}.hero{padding:38px 0 24px}.search{grid-template-columns:1fr 1fr}.search input{grid-column:1/-1}.search .btn{min-height:44px}.grid{grid-template-columns:1fr}.toplinks a,.toplinks button{padding:7px 10px}.meta{align-items:flex-start;flex-direction:column}}
</style>
</head>
<body data-nsfw-enabled="__NSFW_ENABLED__">
<header class="top"><div class="shell" style="width:100%;display:flex;align-items:center;justify-content:space-between"><a class="brand" href="/"><span class="mark">N</span><span>Nolane <span style="color:#91afff">Search</span></span></a><nav class="toplinks"><a href="/">Tìm kiếm</a><button id="logout" type="button">Đăng xuất</button></nav></div></header>
<main class="shell">
<section class="hero">
<span class="eyebrow">MEDIA DISCOVERY · IMAGE · VIDEO · AUDIO</span>
<h1>Khám phá ảnh, video và âm thanh.</h1>
<p>Tìm ảnh có giấy phép từ Commons, Openverse và iNaturalist; xem tư liệu công khai từ NASA, Internet Archive và PeerTube ngay trong trình duyệt.</p>
<form id="search" class="search"><input id="q" autocomplete="off" minlength="2" maxlength="2048" placeholder="Ví dụ: aurora, Hubble telescope, coral reef…" required><select id="kind" aria-label="Loại media"><option value="all">Ảnh, video và audio</option><option value="image">Chỉ hình ảnh</option><option value="video">Chỉ video</option><option value="audio">Chỉ audio</option></select><select id="provider" aria-label="Nguồn media"><option value="all">Tất cả nguồn</option><option value="commons">Wikimedia Commons</option><option value="nasa">NASA</option><option value="openverse">Openverse · ảnh có giấy phép mở</option><option value="archive">Internet Archive · video/audio công cộng</option><option value="peertube">PeerTube · video liên mạng</option><option value="inaturalist">iNaturalist · ảnh thiên nhiên</option></select><button id="go" class="btn" type="submit">Tìm media</button></form>
<label id="nsfw-control" class="adult-toggle hidden"><input id="includeNsfw" type="checkbox"> <strong>Hiển thị video PeerTube gắn nhãn NSFW (18+)</strong> · Tôi xác nhận mình đã đủ 18 tuổi. Nhãn nhạy cảm phụ thuộc dữ liệu của máy chủ nguồn.</label>
<section class="playback-lab" aria-labelledby="playback-lab-title">
 <div class="lab-heading"><div><span class="lab-kicker">BROWSER COMPATIBILITY BENCH</span><h2 id="playback-lab-title">Playback Lab</h2><p>Chạy thử các nguồn công khai để kiểm tra CORS, codec, chất lượng, audio và phụ đề ngay trong player của Nolane.</p></div><span class="lab-badge">HLS · DASH</span></div>
 <div class="lab-grid">
  <button type="button" class="lab-sample" data-stream-url="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8">
   <span class="lab-type">HLS · ADAPTIVE</span><strong>Mux · Big Buck Bunny</strong><span>Master playlist nhiều bitrate và độ phân giải, phù hợp kiểm tra Auto / Manual quality</span><span class="lab-action">Dùng mẫu <b>→</b></span>
  </button>
  <button type="button" class="lab-sample" data-stream-url="https://storage.googleapis.com/shaka-demo-assets/angel-one-hls/hls.m3u8">
   <span class="lab-type">HLS · MULTI-AUDIO</span><strong>Shaka · Angel One</strong><span>Nhiều ngôn ngữ audio, kiểm tra khả năng tải và chuyển track</span><span class="lab-action">Dùng mẫu <b>→</b></span>
  </button>
  <button type="button" class="lab-sample" data-stream-url="https://mtoczko.github.io/hls-test-streams/test-vtt-ts-segments/playlist.m3u8">
   <span class="lab-type">HLS · WEBVTT</span><strong>HLS Test Streams · WebVTT</strong><span>Nguồn HLS công khai có WebVTT, kiểm tra chọn track và tắt phụ đề</span><span class="lab-action">Dùng mẫu <b>→</b></span>
  </button>
  <button type="button" class="lab-sample" data-stream-url="https://storage.googleapis.com/shaka-demo-assets/angel-one/dash.mpd">
   <span class="lab-type">DASH · MULTI-TRACK</span><strong>Shaka · Angel One</strong><span>DASH đa codec, nhiều ngôn ngữ và subtitle; bản clear, không dùng DRM</span><span class="lab-action">Dùng mẫu <b>→</b></span>
  </button>
  <button type="button" class="lab-sample" data-stream-url="https://storage.googleapis.com/shaka-demo-assets/sintel/dash.mpd">
   <span class="lab-type">DASH · SUBTITLES</span><strong>Shaka · Sintel</strong><span>DASH nhiều representation, audio và subtitle WebVTT</span><span class="lab-action">Dùng mẫu <b>→</b></span>
  </button>
 </div>
 <p class="lab-footnote">Nguồn thử do bên thứ ba lưu trữ; tình trạng online, CORS, codec và track có thể thay đổi. Nolane phát trực tiếp từ máy chủ nguồn, không proxy, lưu cache hay chuyển tiếp dữ liệu đăng nhập.</p>
</section>
<div class="tabs"><button class="tab active" data-kind="all">Tất cả</button><button class="tab" data-kind="image">Hình ảnh</button><button class="tab" data-kind="video">Video</button><button class="tab" data-kind="audio">Audio</button></div>
</section>
<div class="meta"><span id="status">Đang kiểm tra phiên đăng nhập…</span><span id="count"></span></div>
<div id="notice" class="notice hidden"></div>
<section id="results" class="grid"></section>
<div class="footer">Wikimedia Commons, Openverse và iNaturalist cung cấp ảnh kèm nguồn/tác giả/giấy phép theo từng mục. NASA và Internet Archive có thể phát hoặc mở/tải tệp gốc khi hồ sơ công khai liệt kê URL phù hợp; quyền sử dụng khác nhau theo từng mục. PeerTube dùng chỉ mục liên mạng SepiaSearch, không bao phủ mọi instance; video mở tại máy chủ gốc. <strong>Hiện chưa có downloader đa website hoặc kho chia sẻ file riêng tư.</strong> Luồng xử lý tệp qua Telegram vẫn chịu giới hạn tải 20 MB của Bot API. Tính năng tải từ nhiều website, lưu vào private storage và chia sẻ bằng link có hạn dùng cần R2 được kích hoạt trước. Hãy xem trang nguồn và điều khoản trước khi tải hoặc tái sử dụng.</div>
</main>
<script>
(function(){
'use strict';
var $=function(id){return document.getElementById(id)};
var nsfwEnabled=document.body.dataset.nsfwEnabled==='true';
if(nsfwEnabled)$('nsfw-control').classList.remove('hidden');
var last=[];
var streamPlayerCleanups=[];
var streamScriptPromises={};
function safeUrl(value,hosts){
 try{var u=new URL(value);if(u.protocol!=='https:'||u.username||u.password||u.port||(hosts&&hosts.indexOf(u.hostname)<0))return null;return u.href}catch(e){return null}
}
function safePeerTubeEmbedUrl(value,instanceHost){
 if(typeof instanceHost!=='string'||!instanceHost)return null;
 var safe=safeUrl(value,[instanceHost]);if(!safe)return null;
 try{
  var u=new URL(safe);var parts=u.pathname.split('/');
  if(u.origin===location.origin||parts.length!==4||parts[0]!==''||parts[1]!=='videos'||parts[2]!=='embed'||!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(parts[3])||u.search||u.hash)return null;
  return u.href;
 }catch(e){return null}
}
function safeMediaEmbedUrl(item){
 if(!item||typeof item!=='object'||typeof item.embedUrl!=='string')return null;
 if(item.provider==='PeerTube')return safePeerTubeEmbedUrl(item.embedUrl,item.instanceHost);
 var hosts=item.provider==='YouTube'?['www.youtube-nocookie.com']:item.provider==='Vimeo'?['player.vimeo.com']:item.provider==='Dailymotion'?['geo.dailymotion.com']:item.provider==='Twitch'?['player.twitch.tv','clips.twitch.tv']:[];
 var safe=safeUrl(item.embedUrl,hosts);if(!safe)return null;
 try{
  var u=new URL(safe);if(u.origin===location.origin||u.hash)return null;
  if(item.provider==='YouTube'){
   if(!/^\/embed\/[A-Za-z0-9_-]{11}$/.test(u.pathname))return null;
   var ytKeys=Array.from(u.searchParams.keys());
   if(ytKeys.some(function(k){return k!=='playsinline'&&k!=='rel'}))return null;
   if(u.searchParams.get('playsinline')!=='1'||u.searchParams.get('rel')!=='0')return null;
  }else if(item.provider==='Vimeo'){
   if(!/^\/video\/[0-9]{5,15}$/.test(u.pathname))return null;
   var vmKeys=Array.from(u.searchParams.keys());
   if(vmKeys.some(function(k){return k!=='h'&&k!=='dnt'}))return null;
   if(u.searchParams.get('dnt')!=='1')return null;
   var h=u.searchParams.get('h');if(h&&!/^[A-Za-z0-9_-]{4,80}$/.test(h))return null;
  }else if(item.provider==='Dailymotion'){
   if(!/^\/player\/[A-Za-z0-9_-]{3,32}\.html$/.test(u.pathname))return null;
   var dmKeys=Array.from(u.searchParams.keys());
   if(dmKeys.length!==1||dmKeys[0]!=='video'||!/^[A-Za-z0-9]{4,20}$/.test(u.searchParams.get('video')||''))return null;
  }else if(item.provider==='Twitch'){
   var twitchKeys=Array.from(u.searchParams.keys());
   if(u.hostname==='player.twitch.tv'){
    if(u.pathname!=='/'||twitchKeys.length!==2||twitchKeys.indexOf('video')<0||twitchKeys.indexOf('autoplay')<0||!/^v[0-9]{5,15}$/.test(u.searchParams.get('video')||'')||u.searchParams.get('autoplay')!=='false')return null;
   }else if(u.hostname==='clips.twitch.tv'){
    if(u.pathname!=='/embed'||twitchKeys.length!==2||twitchKeys.indexOf('clip')<0||twitchKeys.indexOf('autoplay')<0||!/^[A-Za-z0-9_-]{4,80}$/.test(u.searchParams.get('clip')||'')||u.searchParams.get('autoplay')!=='false')return null;
   }else return null;
  }else return null;
  return u.href;
 }catch(e){return null}
}
function isSafePublicMediaRequest(value){
 try{
  var u=new URL(value);
  var host=u.hostname.toLowerCase().replace(/\.$/,'');
  if(u.protocol!=='https:'||u.username||u.password||u.port||u.hash)return false;
  if(!host||!host.includes('.')||host==='localhost'||host.endsWith('.localhost')||host.endsWith('.local')||host.endsWith('.internal')||host.endsWith('.test')||host.endsWith('.example')||host.endsWith('.invalid'))return false;
  if(/^(?:\d{1,3}\.){3}\d{1,3}$/.test(host)||host.indexOf(':')>=0)return false;
  var labels=host.split('.');
  if(labels.some(function(label){return !/^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(label)}))return false;
  return true;
 }catch(e){return false}
}
function safeMediaStreamUrl(item){
 if(!item||!item.streamType||(item.provider!=='HLS'&&item.provider!=='DASH')||typeof item.mediaUrl!=='string')return null;
 if((item.streamType==='hls'&&item.provider!=='HLS')||(item.streamType==='dash'&&item.provider!=='DASH'))return null;
 var safe=safeUrl(item.mediaUrl,null);if(!safe||!isSafePublicMediaRequest(safe))return null;
 try{
  var u=new URL(safe);
  if(item.streamType==='hls'&&!u.pathname.toLowerCase().endsWith('.m3u8'))return null;
  if(item.streamType==='dash'&&!u.pathname.toLowerCase().endsWith('.mpd'))return null;
  return u.href;
 }catch(e){return null}
}
function loadPinnedMediaScript(key,url,globalName){
 if(window[globalName])return Promise.resolve(window[globalName]);
 if(streamScriptPromises[key])return streamScriptPromises[key];
 streamScriptPromises[key]=new Promise(function(resolve,reject){
  var script=document.createElement('script');
  script.async=true;script.crossOrigin='anonymous';script.referrerPolicy='no-referrer';script.src=url;
  script.onload=function(){if(window[globalName])resolve(window[globalName]);else{delete streamScriptPromises[key];reject(new Error('Thư viện player không khởi tạo đúng.'))}};
  script.onerror=function(){delete streamScriptPromises[key];reject(new Error('Không tải được thư viện phát video. Kiểm tra kết nối tới CDN rồi thử lại.'))};
  document.head.appendChild(script);
 });
 return streamScriptPromises[key];
}
function clearStreamPlayers(){
 streamPlayerCleanups.splice(0).forEach(function(cleanup){try{cleanup()}catch(e){}});
}
function qualityLabel(level){
 var height=Number(level&&level.height);
 var width=Number(level&&level.width);
 var bitrate=Number(level&&(level.bitrate||level.bandwidth||(Number(level.bitrateInKbit)>0?Number(level.bitrateInKbit)*1000:0)));
 var name=height>0?Math.round(height)+'p':(width>0?Math.round(width)+'w':'');
 var kbps=bitrate>0?Math.round(bitrate/1000)+' kbps':'';
 return [name,kbps].filter(Boolean).join(' · ')||'Chất lượng '+String(level&&level.id||'');
}
function makeQualityControl(){
 var row=document.createElement('label');row.className='stream-controls';row.hidden=true;
 var caption=document.createElement('span');caption.textContent='Chất lượng';
 var select=document.createElement('select');select.className='stream-quality';select.setAttribute('aria-label','Chất lượng video');
 var auto=document.createElement('option');auto.value='-1';auto.textContent='Tự động';select.appendChild(auto);
 row.append(caption,select);
 return {row:row,select:select};
}
function makePlaybackRateControl(video){
 var row=document.createElement('label');row.className='stream-controls';
 var caption=document.createElement('span');caption.textContent='Tốc độ phát';
 var select=document.createElement('select');select.className='stream-rate';select.setAttribute('aria-label','Tốc độ phát video');
 [[0.5,'0.5×'],[0.75,'0.75×'],[1,'1×'],[1.25,'1.25×'],[1.5,'1.5×'],[2,'2×']].forEach(function(rate){
  var option=document.createElement('option');option.value=String(rate[0]);option.textContent=rate[1];select.appendChild(option);
 });
 select.value='1';
 select.addEventListener('change',function(){var rate=Number(select.value);if([0.5,0.75,1,1.25,1.5,2].indexOf(rate)>=0)video.playbackRate=rate});
 row.append(caption,select);
 return {row:row,select:select};
}
function makeTrackControl(label,ariaLabel){
 var row=document.createElement('label');row.className='stream-controls';row.hidden=true;
 var caption=document.createElement('span');caption.textContent=label;
 var select=document.createElement('select');select.className='stream-track';select.setAttribute('aria-label',ariaLabel);
 row.append(caption,select);
 return {row:row,select:select};
}
function streamTrackLabel(track,index){
 var name=String(track&&(track.name||track.label)||'').trim();
 var lang=String(track&&(track.lang||track.language)||'').trim();
 var channels=String(track&&track.channels||'').trim();
 var label=name||lang||('Track '+String(index+1));
 if(name&&lang&&name.toLowerCase()!==lang.toLowerCase())label+=' · '+lang;
 if(channels)label+=' · '+channels;
 return label;
}
function populateTrackControl(control,tracks,includeOff,selectedValue,valueKey,minimum){
 var list=Array.isArray(tracks)?tracks:[];
 control.select.replaceChildren();
 if(includeOff){
  var off=document.createElement('option');off.value='-1';off.textContent='Tắt phụ đề';control.select.appendChild(off);
 }
 list.forEach(function(track,index){
  var raw=track&&valueKey&&track[valueKey]!==undefined&&track[valueKey]!==null?track[valueKey]:index;
  var option=document.createElement('option');option.value=String(raw);option.textContent=streamTrackLabel(track,index);control.select.appendChild(option);
 });
 control.row.hidden=list.length<(minimum||1);
 var desired=selectedValue===undefined||selectedValue===null?(includeOff?'-1':String(list.length?control.select.options[includeOff?1:0].value:'')):String(selectedValue);
 var hasValue=Array.from(control.select.options).some(function(option){return option.value===desired});
 control.select.value=hasValue?desired:(includeOff?'-1':(control.select.options[0]?control.select.options[0].value:''));
}
function populateQualityControl(control,representations){
 var previous=control.select.value||'-1';
 var list=Array.isArray(representations)?representations:[];
 control.select.replaceChildren();
 var automatic=document.createElement('option');automatic.value='-1';automatic.textContent='Tự động';control.select.appendChild(automatic);
 list.forEach(function(level,index){
  var option=document.createElement('option');option.value=String(index);option.textContent=qualityLabel(level);control.select.appendChild(option);
 });
 control.row.hidden=list.length<2;
 control.select.value=list.length>1&&Array.from(control.select.options).some(function(option){return option.value===previous})?previous:'-1';
}
function showStreamPlayer(preview,item,streamUrl){
 var video=document.createElement('video');video.className='stream-video';video.controls=true;video.playsInline=true;video.preload='none';video.crossOrigin='anonymous';video.referrerPolicy='no-referrer';
 var status=document.createElement('div');status.className='stream-status';status.setAttribute('role','status');
 var quality=makeQualityControl();
 var audioTrack=makeTrackControl('Âm thanh','Ngôn ngữ âm thanh');
 var subtitleTrack=makeTrackControl('Phụ đề','Ngôn ngữ phụ đề');
 var playbackRate=makePlaybackRateControl(video);
 var retry=document.createElement('button');retry.type='button';retry.className='embed-load';retry.textContent='Thử phát lại';retry.hidden=true;
 var cancelled=false;var generation=0;var destroyCurrent=function(){};
 function stopCurrent(){
  var stop=destroyCurrent;destroyCurrent=function(){};
  try{stop()}catch(e){}
 }
 function cleanUp(){
  if(cancelled)return;
  cancelled=true;generation++;stopCurrent();video.pause();video.removeAttribute('src');video.load();
 }
 function fail(message,retryable){
  stopCurrent();video.pause();video.removeAttribute('src');video.load();
  status.textContent=message;retry.hidden=!retryable;
 }
 retry.addEventListener('click',function(){startPlayer()});
 streamPlayerCleanups.push(cleanUp);
 preview.replaceChildren(video,status,quality.row,audioTrack.row,subtitleTrack.row,playbackRate.row,retry);
 function startPlayer(){
  if(cancelled)return;
  var attempt=++generation;
  stopCurrent();video.pause();video.removeAttribute('src');video.load();
  quality.row.hidden=true;quality.select.replaceChildren();
  audioTrack.row.hidden=true;audioTrack.select.replaceChildren();subtitleTrack.row.hidden=true;subtitleTrack.select.replaceChildren();retry.hidden=true;
  status.textContent='Đang khởi tạo player…';
  if(item.streamType==='hls'){
   function canUseAppleNativeHls(){
    var ua=navigator.userAgent||'';var vendor=navigator.vendor||'';
    var appleWebKit=/AppleWebKit/i.test(ua)&&/Apple Computer, Inc\./i.test(vendor);
    var blinkOrGecko=/(Chrome|Chromium|Edg\/|OPR\/|Firefox\/|SamsungBrowser)/i.test(ua);
    return appleWebKit&&!blinkOrGecko&&Boolean(video.canPlayType('application/vnd.apple.mpegurl'));
   }
   function startNativeHls(){
    video.src=streamUrl;status.textContent='Đang dùng HLS native của trình duyệt. Máy chủ nguồn vẫn cần CORS.';
    video.addEventListener('error',function(){if(!cancelled&&attempt===generation)fail('Không phát được HLS native. Kiểm tra CORS, playlist và codec của nguồn.',true)},{once:true});
   }
   if(canUseAppleNativeHls()){startNativeHls();return}
   loadPinnedMediaScript('hls','https://cdn.jsdelivr.net/npm/hls.js@1.7.4/dist/hls.min.js','Hls').then(function(Hls){
    if(cancelled||attempt!==generation)return;
    if(!Hls.isSupported()){
     if(canUseAppleNativeHls()){startNativeHls();return}
     fail('Trình duyệt này không hỗ trợ Media Source Extensions hoặc HLS native.',false);
     return;
    }
    var hls=new Hls({
     enableWorker:true,
     lowLatencyMode:false,
     xhrSetup:function(xhr,url){
      if(!isSafePublicMediaRequest(url))throw new Error('HLS chứa URL segment không an toàn.');
      xhr.withCredentials=false;
     },
     fetchSetup:function(context,initParams){
      if(!isSafePublicMediaRequest(context.url))throw new Error('HLS chứa URL resource không an toàn.');
      initParams.credentials='omit';initParams.mode='cors';
      return new Request(context.url,initParams);
     }
    });
    destroyCurrent=function(){hls.destroy()};
    function refreshHlsQualities(){
     if(cancelled||attempt!==generation)return;
     var levels=Array.isArray(hls.levels)?hls.levels:[];
     populateQualityControl(quality,levels);
    }
    quality.select.onchange=function(){
     if(cancelled||attempt!==generation)return;
     var selected=Number(quality.select.value);
     if(!Number.isInteger(selected)||selected < -1 || selected >= hls.levels.length)return;
     hls.currentLevel=selected;
     status.textContent=selected===-1?'Đang để HLS tự chọn chất lượng.':'Đã yêu cầu chất lượng '+qualityLabel(hls.levels[selected])+'.';
    };
    hls.on(Hls.Events.MANIFEST_PARSED,refreshHlsQualities);
    hls.on(Hls.Events.LEVELS_UPDATED,refreshHlsQualities);
    function refreshHlsTracks(){
     if(cancelled||attempt!==generation)return;
     var audioTracks=Array.isArray(hls.audioTracks)?hls.audioTracks:[];
     var subtitles=Array.isArray(hls.subtitleTracks)?hls.subtitleTracks:[];
     populateTrackControl(audioTrack,audioTracks,false,hls.audioTrack,'id',2);
     populateTrackControl(subtitleTrack,subtitles,true,hls.subtitleTrack,'id',1);
    }
    audioTrack.select.onchange=function(){
     if(cancelled||attempt!==generation)return;
     var selected=Number(audioTrack.select.value);
     if(Number.isInteger(selected)&&selected>=0&&selected<hls.audioTracks.length)hls.audioTrack=selected;
    };
    subtitleTrack.select.onchange=function(){
     if(cancelled||attempt!==generation)return;
     var selected=Number(subtitleTrack.select.value);
     if(!Number.isInteger(selected)||selected < -1 || selected >= hls.subtitleTracks.length)return;
     if(selected===-1){hls.subtitleTrack=-1;hls.subtitleDisplay=false}
     else{hls.subtitleDisplay=true;hls.subtitleTrack=selected}
    };
    hls.on(Hls.Events.MANIFEST_PARSED,refreshHlsTracks);
    hls.on(Hls.Events.AUDIO_TRACKS_UPDATED,refreshHlsTracks);
    hls.on(Hls.Events.SUBTITLE_TRACKS_UPDATED,refreshHlsTracks);

    hls.on(Hls.Events.LEVEL_SWITCHED,function(_event,data){
     if(cancelled||attempt!==generation||quality.select.value!=='-1')return;
     var current=hls.levels[data.level];
     if(current)status.textContent='HLS tự động · '+qualityLabel(current);
    });
    hls.on(Hls.Events.ERROR,function(_event,data){
     if(data&&data.fatal&&!cancelled&&attempt===generation)fail('HLS lỗi khi tải manifest/segment. Cần HTTPS, CORS GET và codec tương thích; nội dung DRM không được hỗ trợ.',true);
    });
    status.textContent='Đang tải HLS manifest…';
    hls.loadSource(streamUrl);hls.attachMedia(video);
   }).catch(function(error){
    if(cancelled||attempt!==generation)return;
    if(canUseAppleNativeHls()){startNativeHls();return}
    fail(error.message||'Không thể tải HLS player.',true);
   });
   return;
  }
  loadPinnedMediaScript('dash','https://cdn.jsdelivr.net/npm/dashjs@5.3.0/dist/legacy/umd/dash.all.min.js','dashjs').then(function(dashjs){
   if(cancelled||attempt!==generation)return;
   var player=dashjs.MediaPlayer().create();
   destroyCurrent=function(){player.destroy()};
   player.addRequestInterceptor(function(request){
    if(!request||!isSafePublicMediaRequest(request.url))return Promise.reject(new Error('DASH chứa URL manifest/segment không an toàn.'));
    var method=String(request.method||'GET').toUpperCase();
    if(method!=='GET'&&method!=='HEAD')return Promise.reject(new Error('DASH chỉ được phép gửi GET/HEAD; yêu cầu license hoặc POST bị chặn.'));
    request.credentials='omit';request.mode='cors';
    return Promise.resolve(request);
   });
   var dashRepresentations=[];
   function refreshDashQualities(){
    if(cancelled||attempt!==generation)return;
    try{dashRepresentations=player.getRepresentationsByType('video')||[]}catch(e){dashRepresentations=[]}
    populateQualityControl(quality,dashRepresentations);
   }
   quality.select.onchange=function(){
    if(cancelled||attempt!==generation)return;
    var selected=Number(quality.select.value);
    try{dashRepresentations=player.getRepresentationsByType('video')||[]}catch(e){dashRepresentations=[]}
    if(!Number.isInteger(selected)||selected < -1 || selected >= dashRepresentations.length)return;
    if(selected===-1){
     player.updateSettings({streaming:{abr:{autoSwitchBitrate:{video:true}}}});
     status.textContent='Đang để DASH tự chọn chất lượng.';
    }else{
     player.updateSettings({streaming:{abr:{autoSwitchBitrate:{video:false}}}});
     player.setRepresentationForTypeByIndex('video',selected,true);
     status.textContent='Đã yêu cầu chất lượng '+qualityLabel(dashRepresentations[selected])+'.';
    }
   };
   player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED,refreshDashQualities);
   var dashAudioTracks=[];
   var dashTextTracks=[];
   function refreshDashTracks(){
    if(cancelled||attempt!==generation)return;
    try{dashAudioTracks=player.getTracksFor('audio')||[]}catch(e){dashAudioTracks=[]}
    var currentAudio=null;
    try{currentAudio=player.getCurrentTrackFor('audio')}catch(e){}
    populateTrackControl(audioTrack,dashAudioTracks,false,currentAudio&&currentAudio.index,'index',2);
    populateTrackControl(subtitleTrack,dashTextTracks,true,-1,'index',1);
   }
   function addDashTextTracks(event){
    if(cancelled||attempt!==generation)return;
    var incoming=event&&Array.isArray(event.tracks)?event.tracks:(event&&event.track?[event.track]:[]);
    incoming.forEach(function(track){
     if(!track)return;
     var key=track.index!==undefined?String(track.index):String(track.id||'');
     if(!dashTextTracks.some(function(existing){return (existing.index!==undefined?String(existing.index):String(existing.id||''))===key}))dashTextTracks.push(track);
    });
    refreshDashTracks();
   }
   audioTrack.select.onchange=function(){
    if(cancelled||attempt!==generation)return;
    var selected=String(audioTrack.select.value);
    var track=dashAudioTracks.find(function(candidate,index){return String(candidate&&candidate.index!==undefined?candidate.index:index)===selected});
    if(track)player.setCurrentTrack(track);
   };
   subtitleTrack.select.onchange=function(){
    if(cancelled||attempt!==generation)return;
    var selected=Number(subtitleTrack.select.value);
    if(Number.isInteger(selected)&&selected>=-1)player.setTextTrack(selected);
   };
   player.on(dashjs.MediaPlayer.events.TEXT_TRACKS_ADDED,addDashTextTracks);
   player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED,refreshDashTracks);
   player.on(dashjs.MediaPlayer.events.TRACK_CHANGE_RENDERED,refreshDashTracks);
   player.on(dashjs.MediaPlayer.events.TEXT_TRACK_ADDED,addDashTextTracks);

   player.on(dashjs.MediaPlayer.events.QUALITY_CHANGE_RENDERED,function(event){
    if(cancelled||attempt!==generation||quality.select.value!=='-1')return;
    var active=event&&Number.isFinite(event.newQuality)?dashRepresentations[event.newQuality]:null;
    status.textContent=active?'DASH tự động · '+qualityLabel(active):'DASH tự động · chất lượng vừa đổi.';
   });
   player.on(dashjs.MediaPlayer.events.ERROR,function(){
    if(!cancelled&&attempt===generation)fail('DASH lỗi khi tải MPD/segment. Cần HTTPS, CORS GET và codec tương thích; DRM không được hỗ trợ.',true);
   });
   player.on(dashjs.Protection.events.LICENSE_REQUEST_SENDING,function(){
    if(cancelled||attempt!==generation)return;
    stopCurrent();fail('Nguồn DASH yêu cầu DRM/license server; Media Portal chỉ hỗ trợ stream không DRM.',false);
   });
   status.textContent='Đang tải DASH manifest…';
   player.updateSettings({streaming:{text:{defaultEnabled:false}}});
   player.initialize(video,streamUrl,false);
  }).catch(function(error){if(!cancelled&&attempt===generation)fail(error.message||'Không thể tải DASH player.',true)});
 }
 startPlayer();
}
async function api(path,options){
 var response=await fetch(path,Object.assign({credentials:'same-origin',cache:'no-store'},options||{}));
 var data;try{data=await response.json()}catch(e){throw new Error('Máy chủ trả về phản hồi không hợp lệ.')}
 if(!response.ok)throw new Error(data.error||('HTTP '+response.status));
 return data;
}
function anchor(label,url,primary){
 if(!url)return null;var a=document.createElement('a');a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=label;if(primary)a.className='primary';return a;
}
function card(item){
 var card=document.createElement('article');card.className='card';if(item.provider==='Twitch')card.className+=' twitch-card';
 var preview=document.createElement('div');preview.className='preview';
 var imageHosts=['upload.wikimedia.org','images-assets.nasa.gov'];
 var imageUrl=item.provider==='Openverse'?safeUrl(item.previewUrl,['api.openverse.org']):item.provider==='Internet Archive'?safeUrl(item.previewUrl,['archive.org']):safeUrl(item.previewUrl,imageHosts);
 var mediaUrl=item.provider==='Openverse'?safeUrl(item.mediaUrl,null):item.provider==='Internet Archive'?safeUrl(item.mediaUrl,['archive.org']):safeUrl(item.mediaUrl,imageHosts);
 var embedUrl=item.mediaType==='video'?safeMediaEmbedUrl(item):null;
 var streamUrl=item.streamType?safeMediaStreamUrl(item):null;
 if(item.mediaType==='video'&&streamUrl){
  card.className+=' stream-card';
  var loadStream=document.createElement('button');loadStream.type='button';loadStream.className='embed-load';loadStream.textContent='Phát '+(item.streamType==='hls'?'HLS':'DASH');
  loadStream.addEventListener('click',function(){loadStream.disabled=true;loadStream.textContent='Đang khởi tạo…';showStreamPlayer(preview,item,streamUrl)});
  preview.appendChild(loadStream);
 }else if(item.mediaType==='video'&&item.streamType){
  var blocked=document.createElement('div');blocked.className='no-preview';blocked.textContent='Manifest không hợp lệ hoặc URL nguồn không an toàn; chỉ có thể mở trang nguồn.';preview.appendChild(blocked);
 }else if(item.mediaType==='video'&&mediaUrl){
  var video=document.createElement('video');video.controls=true;video.preload='metadata';video.playsInline=true;video.src=mediaUrl;preview.appendChild(video);
 }else if(item.mediaType==='audio'&&mediaUrl){
  var audio=document.createElement('audio');audio.controls=true;audio.preload='metadata';audio.src=mediaUrl;preview.appendChild(audio);
 }else if(item.mediaType==='video'&&embedUrl){
  var loadEmbed=document.createElement('button');loadEmbed.type='button';loadEmbed.className='embed-load';loadEmbed.textContent='Nhúng player '+item.provider;
  loadEmbed.addEventListener('click',function(){
   var frameUrl=new URL(embedUrl);
   if(item.provider==='Twitch'){
    var parent=location.hostname.toLowerCase().replace(/\.$/,'');
    if(location.protocol!=='https:'||!parent.includes('.')||parent==='localhost'||parent.endsWith('.localhost')||parent.endsWith('.local')||parent.endsWith('.internal')||parent.endsWith('.invalid')||parent.endsWith('.example')||parent.endsWith('.test')||/^(?:\d{1,3}\.){3}\d{1,3}$/.test(parent)){
     preview.textContent='Twitch player cần một tên miền HTTPS công khai để xác định tham số parent.';
     return;
    }
    frameUrl.searchParams.set('parent',parent);
    if(preview.clientWidth<400){preview.textContent='Twitch yêu cầu khung phát tối thiểu 400 × 300 px; hãy mở trang nguồn hoặc dùng màn hình rộng hơn.';return;}
    preview.style.minHeight='300px';
   }
   if(item.provider==='PeerTube')frameUrl.searchParams.set('p2p','0');
   if(item.provider==='Vimeo')frameUrl.searchParams.set('dnt','1');
   var frame=document.createElement('iframe');frame.src=frameUrl.href;frame.title='Trình phát '+item.provider+': '+(item.title||'video');frame.loading='lazy';frame.referrerPolicy=item.referrerPolicy==='strict-origin-when-cross-origin'?'strict-origin-when-cross-origin':'no-referrer';frame.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';frame.allowFullscreen=true;if(item.provider==='Twitch')frame.style.minHeight='300px';frame.sandbox.add('allow-scripts','allow-same-origin','allow-popups','allow-forms','allow-presentation');preview.replaceChildren(frame);
  });
  preview.appendChild(loadEmbed);
 }else if(imageUrl){
  var img=document.createElement('img');img.loading='lazy';img.alt=item.title||'';img.src=imageUrl;preview.appendChild(img);
 }else{var empty=document.createElement('div');empty.className='no-preview';empty.textContent=item.provider==='PeerTube'?'Mở trang PeerTube gốc để xem video':item.mediaType==='video'?'Nguồn chưa cung cấp MP4 phát trực tiếp':item.mediaType==='audio'?'Không có audio phát trực tiếp':'Không có ảnh xem trước';preview.appendChild(empty)}
 card.appendChild(preview);
 var body=document.createElement('div');body.className='body';
 var title=document.createElement('h2');title.textContent=item.title||'Media không có tiêu đề';body.appendChild(title);
 if(item.description){var d=document.createElement('p');d.className='description';d.textContent=item.description;body.appendChild(d)}
 var badges=document.createElement('div');badges.className='badges';
 [item.provider,item.mediaType==='video'?'VIDEO':item.mediaType==='audio'?'AUDIO':'IMAGE',item.nsfw?'NSFW · 18+':null,item.license].filter(Boolean).forEach(function(value){var b=document.createElement('span');b.className='badge';b.textContent=value;badges.appendChild(b)});
 body.appendChild(badges);
 if(item.credit){var credit=document.createElement('div');credit.className='credit';credit.textContent='Ghi công: '+item.credit;body.appendChild(credit)}
 var actions=document.createElement('div');actions.className='actions';
 var source=item.provider==='PeerTube'?safeUrl(item.sourceUrl,[item.instanceHost]):item.provider==='YouTube'?safeUrl(item.sourceUrl,['youtube.com','www.youtube.com','m.youtube.com','youtu.be']):item.provider==='Vimeo'?safeUrl(item.sourceUrl,['vimeo.com','www.vimeo.com']):item.provider==='Dailymotion'?safeUrl(item.sourceUrl,['dailymotion.com','www.dailymotion.com','dai.ly']):item.provider==='Twitch'?safeUrl(item.sourceUrl,['twitch.tv','www.twitch.tv','m.twitch.tv','clips.twitch.tv']):(item.provider==='HLS'||item.provider==='DASH')?safeUrl(item.sourceUrl,null):item.provider==='Openverse'?safeUrl(item.sourceUrl,null):item.provider==='Internet Archive'?safeUrl(item.sourceUrl,['archive.org']):item.provider==='iNaturalist'?safeUrl(item.sourceUrl,['www.inaturalist.org']):safeUrl(item.sourceUrl,['commons.wikimedia.org','images.nasa.gov','www.nasa.gov']);
 var sourceLabel=item.provider==='PeerTube'?'Xem trên PeerTube':item.provider==='YouTube'?'Mở trên YouTube':item.provider==='Vimeo'?'Mở trên Vimeo':item.provider==='Dailymotion'?'Mở trên Dailymotion':item.provider==='Twitch'?'Mở trên Twitch':item.provider==='HLS'?'Mở manifest HLS':item.provider==='DASH'?'Mở manifest DASH':'Trang nguồn';
 var sourceLink=anchor(sourceLabel,source,item.mediaType==='video');if(sourceLink)actions.appendChild(sourceLink);
 var file=item.streamType?null:anchor(item.mediaType==='video'?'Mở / tải video gốc':item.mediaType==='audio'?'Mở / tải audio gốc':'Mở / tải ảnh gốc',mediaUrl,true);if(file)actions.appendChild(file);
 if(item.licenseUrl){var license=safeUrl(item.licenseUrl,['creativecommons.org','rightsstatements.org','www.nasa.gov']);var licenseLink=anchor('Giấy phép',license,false);if(licenseLink)actions.appendChild(licenseLink)}
 body.appendChild(actions);card.appendChild(body);return card;
}
function render(items){
 clearStreamPlayers();$('results').replaceChildren();last=items||[];
 $('count').textContent=last.length?last.length+' kết quả':'';
 if(!last.length){var empty=document.createElement('div');empty.className='empty';var h=document.createElement('strong');h.textContent='Chưa tìm thấy media';empty.appendChild(h);empty.appendChild(document.createTextNode(' Thử từ khóa khác hoặc đổi nguồn tìm kiếm.'));$('results').appendChild(empty);return}
 last.forEach(function(item){$('results').appendChild(card(item))});
}
async function search(){
 var q=$('q').value.trim();if(q.length<2)return;
 var isUrl=q.indexOf('https://')===0||q.indexOf('http://')===0;
 if(q.length>(isUrl?2048:160)){ $('notice').classList.remove('hidden');$('notice').textContent=isUrl?'URL video không được vượt quá 2048 ký tự.':'Từ khóa tìm kiếm không được vượt quá 160 ký tự.';return; }
 $('go').disabled=true;$('status').textContent=isUrl?'Đang nhận diện URL video…':'Đang tìm kiếm trên các nguồn media…';$('notice').classList.add('hidden');
 clearStreamPlayers();$('results').replaceChildren();
 try{
  if(isUrl){
   var resolved=await api('/api/media/resolve?url='+encodeURIComponent(q));
   if(!resolved.item)throw new Error('Không nhận được thông tin video từ nguồn.');
   render([resolved.item]);$('status').textContent='Đã nhận diện '+resolved.item.provider+' · có thể nhúng player hoặc mở trang nguồn';
  }else{
   var query=new URLSearchParams({q:q,kind:$('kind').value,provider:$('provider').value});
   if(nsfwEnabled && $('includeNsfw').checked)query.set('include_nsfw','true');
   var data=await api('/api/media/search?'+query.toString());
   render(data.items||[]);$('status').textContent='Tìm xong · nguồn: '+(data.providers||[]).join(', ');if(data.warnings&&data.warnings.length){$('notice').classList.remove('hidden');$('notice').textContent='Một số nguồn tạm thời không phản hồi: '+data.warnings.join(' · ')}
  }
 }catch(error){$('results').replaceChildren();$('notice').classList.remove('hidden');$('notice').textContent=error.message;$('status').textContent=isUrl?'Không thể nhận diện URL video':'Không thể tìm media'}
 finally{$('go').disabled=false}
}
function syncProviderOptions(){
 var kind=$('kind').value;
 var unsupported=kind==='audio'?['commons','nasa','openverse','peertube','inaturalist']:kind==='video'?['commons','openverse','inaturalist']:kind==='image'?['archive','peertube']:[];
 var provider=$('provider');
 for(var i=0;i<provider.options.length;i++){provider.options[i].disabled=unsupported.indexOf(provider.options[i].value)>=0}
 if(provider.options[provider.selectedIndex]&&provider.options[provider.selectedIndex].disabled)provider.value='all';
}
$('kind').addEventListener('change',syncProviderOptions);
syncProviderOptions();
document.querySelectorAll('[data-stream-url]').forEach(function(button){
 button.addEventListener('click',function(){
  var url=button.dataset.streamUrl||'';
  if(!url)return;
  $('q').value=url;
  $('kind').value='video';syncProviderOptions();
  search();
 });
});
$('search').addEventListener('submit',function(e){e.preventDefault();search()});
document.querySelectorAll('[data-kind]').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('[data-kind]').forEach(x=>x.classList.toggle('active',x===b));$('kind').value=b.dataset.kind;syncProviderOptions()})});
$('logout').addEventListener('click',async function(){try{await api('/api/auth/logout',{method:'POST',headers:{'content-type':'application/json','origin':location.origin},body:'{}'})}catch(e){}location.href='/'});
(async function boot(){try{await api('/api/auth/me');$('status').textContent='Đã đăng nhập · sẵn sàng tìm media'}catch(e){$('status').textContent='Hãy đăng nhập từ bot Telegram bằng /web';$('notice').classList.remove('hidden');$('notice').textContent='Bạn cần mở Nolane Search từ liên kết đăng nhập trong cuộc trò chuyện riêng với bot.'}})();
})();
</script>
</body></html>`;
export function mediaAppResponse(nsfwFeatureEnabled = false): Response {
  const html = HTML.replace('__NSFW_ENABLED__', nsfwFeatureEnabled ? 'true' : 'false');
  return new Response(html, {
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store, max-age=0",
      "x-content-type-options": "nosniff",
      "referrer-policy": "no-referrer",
      "content-security-policy": "default-src 'self'; script-src 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'unsafe-inline'; connect-src 'self' https:; img-src 'self' data: https://upload.wikimedia.org https://images-assets.nasa.gov https://api.openverse.org https://archive.org; media-src 'self' blob: data: https://images-assets.nasa.gov https://archive.org https://*.archive.org https:; worker-src 'self' blob:; frame-src https:; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
    },
  });
}
