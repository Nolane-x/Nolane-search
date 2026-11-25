const HTML = `<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>Nolane · Địa điểm quanh đây</title>
<style>
:root{color-scheme:light dark;--bg:#f3f5f9;--surface:#fff;--panel:#f9faff;--ink:#1b2233;--muted:#68738a;--line:#e2e7f0;--accent:#5379e7;--accent-text:#fff;--success:#14845b;--danger:#bd4252}
@media(prefers-color-scheme:dark){:root{--bg:#10141d;--surface:#171e2b;--panel:#1c2635;--ink:#eef3fc;--muted:#9ba8bc;--line:#303b4e;--accent:#7898ff;--accent-text:#101625;--success:#65d7a5;--danger:#ff8492}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
.shell{width:min(100% - 28px,760px);margin:0 auto;padding:calc(16px + env(safe-area-inset-top)) 0 calc(40px + env(safe-area-inset-bottom))}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:22px}
.back{color:var(--muted);font-size:12px;font-weight:800;text-decoration:none}
.brand{display:flex;align-items:center;gap:9px;font-weight:900;font-size:12px;letter-spacing:.08em}
.logo{display:grid;place-items:center;width:33px;height:33px;border-radius:12px;background:linear-gradient(135deg,var(--accent),#8c74ec);color:#fff;font-size:17px}
.hero{padding:22px;border:1px solid var(--line);border-radius:22px;background:linear-gradient(140deg,var(--surface),var(--panel))}
.eyebrow{font-size:10px;font-weight:900;letter-spacing:.16em;color:var(--accent)}
h1{font-size:clamp(25px,6vw,36px);line-height:1.08;letter-spacing:-.045em;margin:10px 0}
.hero p{font-size:13px;color:var(--muted);line-height:1.65;margin:0;max-width:580px}
.panel{margin-top:14px;padding:16px;border:1px solid var(--line);border-radius:18px;background:var(--surface)}
.panel h2{font-size:14px;margin:0 0 5px}
.help{font-size:11px;line-height:1.55;color:var(--muted);margin:0 0 14px}
.location-row{display:flex;gap:8px;flex-wrap:wrap}
button,select,input{font:inherit}
button{cursor:pointer}
.location-btn,.search-btn{border:0;border-radius:12px;padding:11px 14px;background:var(--accent);color:var(--accent-text);font-size:12px;font-weight:850}
.location-btn{background:var(--panel);color:var(--ink);border:1px solid var(--line)}
.location-btn:disabled,.search-btn:disabled{opacity:.55;cursor:wait}
.coords,.filters{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;margin-top:11px}
.field{display:grid;gap:5px;min-width:0}
.field label{font-size:10px;font-weight:800;color:var(--muted)}
.field input,.field select{width:100%;min-width:0;border:1px solid var(--line);border-radius:11px;padding:10px 11px;background:var(--panel);color:var(--ink);outline:0;font-size:12px}
.filters .field:first-child{grid-column:1 / -1}
.search-btn{width:100%;margin-top:12px}
.privacy{font-size:10px;line-height:1.55;color:var(--muted);border-left:2px solid var(--accent);padding:7px 0 7px 10px;margin:13px 0 0}
.status{font-size:11px;line-height:1.55;color:var(--muted);margin-top:12px;white-space:pre-wrap}
.status.error{color:var(--danger)}
.results-head{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin-bottom:10px}
.results-head strong{font-size:13px}
.results-head span{font-size:10px;color:var(--muted);text-align:right}
.result-list{display:grid;gap:9px}
.place{border:1px solid var(--line);border-radius:15px;background:var(--panel);padding:12px}
.place-top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.place h3{font-size:13px;line-height:1.4;margin:0 0 4px}
.place-type{font-size:10px;color:var(--muted)}
.distance{flex:0 0 auto;padding:4px 7px;border-radius:8px;background:color-mix(in srgb,var(--accent) 12%,transparent);color:var(--accent);font-size:10px;font-weight:850}
.place-meta{font-size:10px;line-height:1.5;color:var(--muted);margin-top:8px}
.place-actions{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px}
.place-actions a{border:1px solid var(--line);border-radius:9px;padding:7px 9px;color:var(--accent);font-size:10px;font-weight:800;text-decoration:none}
.empty{border:1px dashed var(--line);border-radius:14px;padding:18px;text-align:center;color:var(--muted);font-size:11px;line-height:1.6}
.attribution{font-size:10px;color:var(--muted);line-height:1.6;margin-top:12px}
.attribution a{color:var(--accent)}
@media(max-width:440px){.coords,.filters{grid-template-columns:1fr 1fr}.location-row button{flex:1}.hero{padding:18px}}
</style>
</head>
<body>
<main class="shell">
<header class="topbar"><a class="back" href="/telegram">← Nolane Workspace</a><div class="brand"><span class="logo">N</span><span>NOLANE SEARCH</span></div></header>
<section class="hero"><div class="eyebrow">LOCAL DISCOVERY</div><h1>Tìm địa điểm<br>quanh đây.</h1><p>Tra cứu nhà thuốc, ATM, siêu thị, quán ăn, bệnh viện, trạm sạc và nhiều điểm hữu ích quanh một vị trí bạn chọn.</p></section>
<section class="panel">
<h2>Vị trí tìm kiếm</h2>
<p class="help">Chỉ đọc vị trí khi bạn bấm nút bên dưới. Bạn cũng có thể nhập tọa độ thủ công.</p>
<div class="location-row"><button id="locate" class="location-btn" type="button">◎ Dùng vị trí hiện tại</button></div>
<div class="coords">
 <div class="field"><label for="latitude">Vĩ độ (latitude)</label><input id="latitude" type="number" inputmode="decimal" step="any" min="-90" max="90" placeholder="Ví dụ: 20.8449"></div>
 <div class="field"><label for="longitude">Kinh độ (longitude)</label><input id="longitude" type="number" inputmode="decimal" step="any" min="-180" max="180" placeholder="Ví dụ: 106.6881"></div>
</div>
<div class="filters">
 <div class="field"><label for="category">Bạn muốn tìm gì?</label><select id="category">
  <option value="food">Quán ăn, cà phê</option><option value="shopping">Siêu thị, cửa hàng</option><option value="pharmacy">Nhà thuốc</option><option value="medical">Bệnh viện, phòng khám</option><option value="atm">ATM, ngân hàng</option><option value="fuel">Trạm xăng</option><option value="charging">Trạm sạc xe điện</option><option value="parks">Công viên, sân chơi</option><option value="sightseeing">Điểm tham quan, bảo tàng</option><option value="stay">Khách sạn, nơi lưu trú</option>
 </select></div>
 <div class="field"><label for="radius">Bán kính tìm kiếm</label><select id="radius"><option value="500">500 m</option><option value="1000">1 km</option><option value="1500" selected>1,5 km</option><option value="3000">3 km</option><option value="5000">5 km</option></select></div>
</div>
<button id="search" class="search-btn" type="button">Tìm địa điểm quanh đây ↗</button>
<p class="privacy">Quyền riêng tư: tọa độ chỉ được gửi cho truy vấn bạn chủ động yêu cầu tới OpenStreetMap Overpass API. Nolane không lưu tọa độ vào D1 hoặc lịch sử tìm kiếm. Không có vị trí nào được tự động suy đoán.</p>
<div id="status" class="status" role="status" aria-live="polite"></div>
</section>
<section class="panel" aria-live="polite">
<div class="results-head"><strong>Kết quả tìm kiếm</strong><span id="resultCount">Chưa có truy vấn</span></div>
<div id="results" class="result-list"><div class="empty">Chọn vị trí và danh mục ở trên để bắt đầu.</div></div>
<div class="attribution">Dữ liệu bản đồ © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a>, được cung cấp theo Open Database License (ODbL).</div>
</section>
</main>
<script>
(function(){
var $=function(id){return document.getElementById(id)};
function setStatus(value,error){$('status').textContent=value||'';$('status').classList.toggle('error',Boolean(error))}
function validCoordinate(input,min,max){var value=Number(input.value);return input.value.trim()!==''&&Number.isFinite(value)&&value>=min&&value<=max?value:null}
$('locate').addEventListener('click',function(){
 if(!navigator.geolocation){setStatus('Trình duyệt hiện tại không hỗ trợ định vị. Hãy nhập tọa độ thủ công.',true);return}
 var button=$('locate');button.disabled=true;setStatus('Đang chờ quyền vị trí từ thiết bị…');
 navigator.geolocation.getCurrentPosition(function(position){
  $('latitude').value=position.coords.latitude.toFixed(5);$('longitude').value=position.coords.longitude.toFixed(5);
  setStatus('Đã nhận vị trí từ thiết bị. Chọn danh mục rồi bấm Tìm địa điểm.');
  button.disabled=false;
 },function(error){
  var message=error.code===1?'Bạn chưa cấp quyền vị trí. Có thể nhập tọa độ thủ công.':error.code===2?'Thiết bị không xác định được vị trí. Hãy thử lại hoặc nhập tọa độ.':'Hết thời gian chờ định vị. Hãy thử lại hoặc nhập tọa độ.';
  setStatus(message,true);button.disabled=false;
 },{enableHighAccuracy:false,maximumAge:60000,timeout:15000});
});
function addText(parent,tag,className,value){var el=document.createElement(tag);if(className)el.className=className;el.textContent=value||'';parent.appendChild(el);return el}
function safeHttps(value){try{var url=new URL(value);return url.protocol==='https:'&&!url.username&&!url.password&&!url.port?url.toString():null}catch(e){return null}}
function distanceText(m){return m<1000?m+' m':(m/1000).toFixed(1)+' km'}
function render(data){
 var box=$('results');box.replaceChildren();
 $('resultCount').textContent=data.resultCount+' địa điểm · '+distanceText(data.radiusMeters);
 if(!data.places.length){addText(box,'div','empty','Không tìm thấy địa điểm có tên trong bán kính này. Hãy thử tăng bán kính hoặc chọn danh mục khác.');return}
 data.places.forEach(function(place){
  var card=addText(box,'article','place','');
  var top=addText(card,'div','place-top','');var title=addText(top,'div','','');
  addText(title,'h3','',place.name);addText(title,'div','place-type',place.detailType||place.categoryLabel);
  addText(top,'span','distance',distanceText(place.distanceMeters));
  if(place.address)addText(card,'div','place-meta',place.address);
  if(place.openingHours)addText(card,'div','place-meta','Giờ ghi trên OSM: '+place.openingHours+' · Chưa xác nhận đang mở.');
  var actions=addText(card,'div','place-actions','');
  var map=safeHttps(place.mapUrl);if(map){var link=addText(actions,'a','','Xem bản đồ');link.href=map;link.target='_blank';link.rel='noopener noreferrer'}
  var osm=safeHttps(place.osmUrl);if(osm){var source=addText(actions,'a','','Trang dữ liệu OSM');source.href=osm;source.target='_blank';source.rel='noopener noreferrer'}
  var website=safeHttps(place.website);if(website){var site=addText(actions,'a','','Website');site.href=website;site.target='_blank';site.rel='noopener noreferrer'}
 });
 var note=data.note||'Dữ liệu có thể chưa đầy đủ hoặc đã cũ.';
 addText(box,'div','attribution',note+(data.dataUpdatedAt?' · Dữ liệu OSM cập nhật: '+data.dataUpdatedAt:''));
}
$('search').addEventListener('click',async function(){
 var latitude=validCoordinate($('latitude'),-90,90),longitude=validCoordinate($('longitude'),-180,180);
 if(latitude===null||longitude===null){setStatus('Nhập hoặc lấy đủ vĩ độ và kinh độ hợp lệ trước khi tìm.',true);return}
 var button=$('search');button.disabled=true;setStatus('Đang tra cứu dữ liệu OpenStreetMap…');
 try{
  var response=await fetch('/api/nearby/search',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'content-type':'application/json','x-nolane-request':'1'},body:JSON.stringify({latitude:latitude,longitude:longitude,category:$('category').value,radius_m:Number($('radius').value),limit:15})});
  var data=await response.json();
  if(!response.ok)throw new Error(data.error||'Không thể tìm địa điểm lúc này.');
  render(data);setStatus(data.resultCount?'Đã tìm thấy địa điểm gần vị trí đã chọn.':'Không có địa điểm phù hợp trong vùng này.');
 }catch(error){setStatus(error&&error.message?error.message:'Không thể hoàn tất truy vấn.',true)}
 finally{button.disabled=false}
});
})();
</script>
</body>
</html>`;

export function nearbyAppResponse(): Response {
  return new Response(HTML, {
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store, max-age=0",
      "x-content-type-options": "nosniff",
      "referrer-policy": "no-referrer",
      "content-security-policy": "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
    },
  });
}
