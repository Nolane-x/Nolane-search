const HTML = String.raw`<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#101827"><meta name="robots" content="noindex,nofollow">
<title>Nolane Search · Media</title>
<style>
:root{color-scheme:dark;--bg:#0b1220;--panel:#121d2f;--panel2:#18253a;--line:#26354d;--ink:#edf3ff;--muted:#9aabc4;--accent:#84a8ff;--blue:#456ff0;--radius:17px}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top,#172641 0,#0b1220 48rem);color:var(--ink);font:15px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}button,input,select{font:inherit}button,a{cursor:pointer}a{color:inherit}.shell{max-width:1280px;margin:0 auto;padding:0 24px}.top{height:72px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);background:#0b1220cc;backdrop-filter:blur(15px);position:sticky;top:0;z-index:4}.brand{text-decoration:none;font-size:19px;font-weight:800;letter-spacing:-.04em;display:flex;align-items:center;gap:10px}.mark{width:34px;height:34px;display:grid;place-items:center;background:linear-gradient(140deg,#416df0,#789cff);border-radius:12px;box-shadow:0 6px 20px #406df044}.toplinks{display:flex;gap:9px;align-items:center}.toplinks a,.toplinks button{border:1px solid var(--line);background:#172339;color:#cfdbf1;text-decoration:none;padding:8px 13px;border-radius:999px;font-size:13px}.toplinks a:hover,.toplinks button:hover{border-color:#688ce8}.hero{text-align:center;padding:58px 0 30px}.eyebrow{display:inline-block;color:#a8c0ff;border:1px solid #334a77;background:#172846;border-radius:999px;padding:5px 11px;font-size:12px;font-weight:700}.hero h1{font-size:clamp(32px,4.7vw,53px);letter-spacing:-.055em;line-height:1.1;margin:15px 0 12px}.hero p{max-width:680px;margin:0 auto;color:var(--muted);font-size:15px}.search{max-width:860px;margin:25px auto 0;display:grid;grid-template-columns:1fr auto auto;gap:9px}.search input,.search select{min-width:0;border:1px solid #2d3d58;background:#111e31;color:var(--ink);padding:13px 15px;border-radius:13px;outline:none}.search input:focus,.search select:focus{border-color:#789cff;box-shadow:0 0 0 3px #638aff22}.btn{border:0;background:#557df5;color:white;font-weight:700;padding:0 19px;border-radius:13px}.btn:disabled{opacity:.6;cursor:wait}.tabs{display:flex;justify-content:center;flex-wrap:wrap;gap:8px;margin:21px auto 0}.tab{border:1px solid var(--line);background:#111e31;color:#aebed7;padding:8px 17px;border-radius:999px}.tab.active{background:#263f70;color:white;border-color:#527ddc}.meta{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:26px 0 14px;color:var(--muted);font-size:13px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:17px;padding-bottom:70px}.card{background:linear-gradient(160deg,#152239,#111a2a);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;min-width:0;box-shadow:0 12px 32px #0002}.preview{aspect-ratio:16/10;background:#080e18;display:grid;place-items:center;overflow:hidden}.preview img,.preview video{width:100%;height:100%;object-fit:contain}.preview audio{width:min(100%,560px);max-width:100%}.no-preview{color:#8da2c4;font-size:13px;padding:25px;text-align:center}.body{padding:14px 15px 15px}.body h2{font-size:15px;line-height:1.35;margin:0 0 7px}.description{color:#9fb0c9;font-size:12px;line-height:1.55;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;min-height:55px}.badges{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}.badge{font-size:10px;border-radius:999px;background:#203453;color:#aec6ff;padding:3px 8px}.credit{font-size:11px;color:#8195b3;overflow-wrap:anywhere}.actions{display:flex;gap:8px;margin-top:12px}.actions a{display:inline-flex;align-items:center;justify-content:center;min-height:34px;text-decoration:none;padding:6px 11px;border-radius:9px;background:#20375c;color:#d8e5ff;font-size:12px;font-weight:650}.actions a.primary{background:#416cdd;color:white}.notice,.empty{margin:16px 0;background:#142238;border:1px solid #2b3e5c;color:#aebed5;padding:18px;border-radius:14px}.notice strong,.empty strong{color:#e8f0ff}.adult-toggle{display:flex;align-items:center;justify-content:center;gap:8px;max-width:860px;margin:12px auto 0;padding:11px 14px;border:1px solid #785c36;background:#33281b;color:#ffe0ad;border-radius:12px;font-size:12px}.adult-toggle input{accent-color:#e5a54c;width:17px;height:17px}.small{font-size:11px;color:#7186a4;margin-top:6px}.footer{padding:16px 0 34px;color:#7285a2;font-size:11px;border-top:1px solid var(--line)}.hidden{display:none!important}
@media(max-width:900px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:620px){.shell{padding:0 15px}.hero{padding:38px 0 24px}.search{grid-template-columns:1fr 1fr}.search input{grid-column:1/-1}.search .btn{min-height:44px}.grid{grid-template-columns:1fr}.toplinks a,.toplinks button{padding:7px 10px}.meta{align-items:flex-start;flex-direction:column}}
</style>
</head>
<body data-nsfw-enabled="__NSFW_ENABLED__">
<header class="top"><div class="shell" style="width:100%;display:flex;align-items:center;justify-content:space-between"><a class="brand" href="/"><span class="mark">N</span><span>Nolane <span style="color:#91afff">Search</span></span></a><nav class="toplinks"><a href="/">Tìm kiếm</a><button id="logout" type="button">Đăng xuất</button></nav></div></header>
<main class="shell">
<section class="hero">
<span class="eyebrow">MEDIA DISCOVERY · IMAGE · VIDEO · AUDIO</span>
<h1>Khám phá ảnh, video và âm thanh.</h1>
<p>Tìm ảnh kèm tác giả và giấy phép, xem tư liệu công khai từ NASA và Internet Archive, hoặc nghe các bản ghi âm có tệp gốc công khai ngay trong trình duyệt.</p>
<form id="search" class="search"><input id="q" autocomplete="off" minlength="2" maxlength="160" placeholder="Ví dụ: aurora, Hubble telescope, coral reef…" required><select id="kind" aria-label="Loại media"><option value="all">Ảnh, video và audio</option><option value="image">Chỉ hình ảnh</option><option value="video">Chỉ video</option><option value="audio">Chỉ audio</option></select><select id="provider" aria-label="Nguồn media"><option value="all">Tất cả nguồn</option><option value="commons">Wikimedia Commons</option><option value="nasa">NASA</option><option value="openverse">Openverse · ảnh có giấy phép mở</option><option value="archive">Internet Archive · video/audio công cộng</option><option value="peertube">PeerTube · video liên mạng</option></select><button id="go" class="btn" type="submit">Tìm media</button></form>
<label id="nsfw-control" class="adult-toggle hidden"><input id="includeNsfw" type="checkbox"> <strong>Hiển thị video PeerTube gắn nhãn NSFW (18+)</strong> · Tôi xác nhận mình đã đủ 18 tuổi. Nhãn nhạy cảm phụ thuộc dữ liệu của máy chủ nguồn.</label>
<div class="tabs"><button class="tab active" data-kind="all">Tất cả</button><button class="tab" data-kind="image">Hình ảnh</button><button class="tab" data-kind="video">Video</button><button class="tab" data-kind="audio">Audio</button></div>
</section>
<div class="meta"><span id="status">Đang kiểm tra phiên đăng nhập…</span><span id="count"></span></div>
<div id="notice" class="notice hidden"></div>
<section id="results" class="grid"></section>
<div class="footer">Wikimedia Commons và Openverse cung cấp ảnh kèm nguồn/tác giả/giấy phép khi có. NASA và Internet Archive có thể phát hoặc mở/tải tệp gốc khi hồ sơ công khai liệt kê URL phù hợp; quyền sử dụng khác nhau theo từng mục. PeerTube dùng chỉ mục liên mạng SepiaSearch, không bao phủ mọi instance; video mở tại máy chủ gốc. <strong>Hiện chưa có downloader đa website hoặc kho chia sẻ file riêng tư.</strong> Luồng xử lý tệp qua Telegram vẫn chịu giới hạn tải 20 MB của Bot API. Tính năng tải từ nhiều website, lưu vào private storage và chia sẻ bằng link có hạn dùng cần R2 được kích hoạt trước. Hãy xem trang nguồn và điều khoản trước khi tải hoặc tái sử dụng.</div>
</main>
<script>
(function(){
'use strict';
var $=function(id){return document.getElementById(id)};
var nsfwEnabled=document.body.dataset.nsfwEnabled==='true';
if(nsfwEnabled)$('nsfw-control').classList.remove('hidden');
var last=[];
function safeUrl(value,hosts){
 try{var u=new URL(value);if(u.protocol!=='https:'||u.username||u.password||u.port||(hosts&&hosts.indexOf(u.hostname)<0))return null;return u.href}catch(e){return null}
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
 var card=document.createElement('article');card.className='card';
 var preview=document.createElement('div');preview.className='preview';
 var imageHosts=['upload.wikimedia.org','images-assets.nasa.gov'];
 var imageUrl=item.provider==='Openverse'?safeUrl(item.previewUrl,['api.openverse.org']):item.provider==='Internet Archive'?safeUrl(item.previewUrl,['archive.org']):safeUrl(item.previewUrl,imageHosts);
 var mediaUrl=item.provider==='Openverse'?safeUrl(item.mediaUrl,null):item.provider==='Internet Archive'?safeUrl(item.mediaUrl,['archive.org']):safeUrl(item.mediaUrl,imageHosts);
 if(item.mediaType==='video'&&mediaUrl){
  var video=document.createElement('video');video.controls=true;video.preload='metadata';video.playsInline=true;video.src=mediaUrl;preview.appendChild(video);
 }else if(item.mediaType==='audio'&&mediaUrl){
  var audio=document.createElement('audio');audio.controls=true;audio.preload='metadata';audio.src=mediaUrl;preview.appendChild(audio);
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
 var source=item.provider==='PeerTube'?safeUrl(item.sourceUrl,[item.instanceHost]):item.provider==='Openverse'?safeUrl(item.sourceUrl,null):item.provider==='Internet Archive'?safeUrl(item.sourceUrl,['archive.org']):safeUrl(item.sourceUrl,['commons.wikimedia.org','images.nasa.gov','www.nasa.gov']);
 var sourceLink=anchor(item.provider==='PeerTube'?'Xem trên PeerTube':'Trang nguồn',source,item.provider==='PeerTube');if(sourceLink)actions.appendChild(sourceLink);
 var file=anchor(item.mediaType==='video'?'Mở / tải video gốc':item.mediaType==='audio'?'Mở / tải audio gốc':'Mở / tải ảnh gốc',mediaUrl,true);if(file)actions.appendChild(file);
 if(item.licenseUrl){var license=safeUrl(item.licenseUrl,['creativecommons.org','rightsstatements.org','www.nasa.gov']);var licenseLink=anchor('Giấy phép',license,false);if(licenseLink)actions.appendChild(licenseLink)}
 body.appendChild(actions);card.appendChild(body);return card;
}
function render(items){
 $('results').replaceChildren();last=items||[];
 $('count').textContent=last.length?last.length+' kết quả':'';
 if(!last.length){var empty=document.createElement('div');empty.className='empty';var h=document.createElement('strong');h.textContent='Chưa tìm thấy media';empty.appendChild(h);empty.appendChild(document.createTextNode(' Thử từ khóa khác hoặc đổi nguồn tìm kiếm.'));$('results').appendChild(empty);return}
 last.forEach(function(item){$('results').appendChild(card(item))});
}
async function search(){
 var q=$('q').value.trim();if(q.length<2)return;
 $('go').disabled=true;$('status').textContent='Đang tìm kiếm trên các nguồn media…';$('notice').classList.add('hidden');
 $('results').replaceChildren();
 try{
  var query=new URLSearchParams({q:q,kind:$('kind').value,provider:$('provider').value});
  if(nsfwEnabled && $('includeNsfw').checked)query.set('include_nsfw','true');
  var data=await api('/api/media/search?'+query.toString());
  render(data.items||[]);$('status').textContent='Tìm xong · nguồn: '+(data.providers||[]).join(', ');if(data.warnings&&data.warnings.length){$('notice').classList.remove('hidden');$('notice').textContent='Một số nguồn tạm thời không phản hồi: '+data.warnings.join(' · ')}
 }catch(error){$('results').replaceChildren();$('notice').classList.remove('hidden');$('notice').textContent=error.message;$('status').textContent='Không thể tìm media'}
 finally{$('go').disabled=false}
}
function syncProviderOptions(){
 var kind=$('kind').value;
 var unsupported=kind==='audio'?['commons','nasa','openverse','peertube']:kind==='video'?['commons','openverse']:kind==='image'?['archive','peertube']:[];
 var provider=$('provider');
 for(var i=0;i<provider.options.length;i++){provider.options[i].disabled=unsupported.indexOf(provider.options[i].value)>=0}
 if(provider.options[provider.selectedIndex]&&provider.options[provider.selectedIndex].disabled)provider.value='all';
}
$('kind').addEventListener('change',syncProviderOptions);
syncProviderOptions();
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
      "content-security-policy": "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data: https://upload.wikimedia.org https://images-assets.nasa.gov https://api.openverse.org https://archive.org; media-src 'self' https://images-assets.nasa.gov https://archive.org https://*.archive.org; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
    },
  });
}
