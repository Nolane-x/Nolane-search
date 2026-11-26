const HTML = `<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>Nolane · Địa điểm quanh đây</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="anonymous">
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
.place-actions button,.saved-actions button{border:1px solid var(--line);border-radius:9px;padding:7px 9px;background:var(--surface);color:var(--ink);font-size:10px;font-weight:800}
.place-actions .save-btn{border-color:color-mix(in srgb,var(--accent) 45%,var(--line));color:var(--accent)}
.place-actions button:disabled,.saved-actions button:disabled{opacity:.45;cursor:not-allowed}
.saved-list{display:grid;gap:8px}
.saved-place{display:grid;grid-template-columns:28px minmax(0,1fr) auto;gap:9px;align-items:center;border:1px solid var(--line);border-radius:13px;padding:10px;background:var(--panel)}
.stop-number{display:grid;place-items:center;width:26px;height:26px;border-radius:9px;background:color-mix(in srgb,var(--accent) 14%,transparent);color:var(--accent);font-size:11px;font-weight:900}
.saved-place h3{font-size:12px;line-height:1.4;margin:0 0 3px}
.saved-place .place-meta{margin:0}
.saved-actions{display:flex;justify-content:flex-end;gap:5px;flex-wrap:wrap}
.saved-actions button{padding:6px 7px}
.saved-actions a{border:1px solid var(--line);border-radius:8px;padding:6px 7px;color:var(--accent);font-size:10px;font-weight:800;text-decoration:none}
.export-btn{border:0;border-radius:11px;padding:10px 13px;background:var(--accent);color:var(--accent-text);font-size:11px;font-weight:850}
.saved-toolbar{display:flex;gap:8px;align-items:center;justify-content:space-between;flex-wrap:wrap;margin:12px 0 0}
.saved-toolbar span{font-size:10px;color:var(--muted)}
.route-controls{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:9px;align-items:end}
.route-controls .field{min-width:0}
.route-controls select{width:100%;border:1px solid var(--line);border-radius:11px;padding:10px 11px;background:var(--panel);color:var(--ink);font:inherit;font-size:12px}
.route-button{border:0;border-radius:11px;padding:11px 14px;background:var(--accent);color:var(--accent-text);font-size:11px;font-weight:850;white-space:nowrap}
.route-button:disabled{opacity:.5;cursor:not-allowed}
.route-summary{font-size:12px;line-height:1.5;font-weight:850;margin-top:12px}
.route-status{font-size:10px;line-height:1.55;color:var(--muted);margin-top:8px;white-space:pre-wrap}
.route-status.error{color:var(--danger)}
.route-map{position:relative;height:340px;min-height:270px;border:1px solid var(--line);border-radius:14px;overflow:hidden;margin-top:12px;background:var(--panel);z-index:0}
.route-map-placeholder{position:absolute;inset:0;display:grid;place-items:center;padding:24px;text-align:center;color:var(--muted);font-size:11px;line-height:1.6;pointer-events:none;z-index:500}
.route-legs{display:grid;gap:7px;margin-top:10px}
.route-leg{border:1px solid var(--line);border-radius:11px;padding:9px 10px;background:var(--panel);font-size:10px;line-height:1.5}
.route-leg strong{font-size:11px}
.route-provider-note{font-size:10px;color:var(--muted);line-height:1.6;margin-top:10px}
.route-provider-note a{color:var(--accent)}
.route-stop-icon{display:grid;place-items:center;width:28px;height:28px;border:2px solid white;border-radius:50%;background:var(--accent);color:white;box-shadow:0 1px 5px #0008;font-size:11px;font-weight:900}
@media(max-width:440px){.route-controls{grid-template-columns:1fr}.route-controls button{width:100%}.route-map{height:300px}}
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
  <option value="food">Quán ăn, cà phê</option><option value="shopping">Siêu thị, cửa hàng</option><option value="pharmacy">Nhà thuốc</option><option value="medical">Bệnh viện, phòng khám</option><option value="atm">ATM, ngân hàng</option><option value="fuel">Trạm xăng</option><option value="charging">Trạm sạc xe điện</option><option value="parks">Công viên, sân chơi</option><option value="sightseeing">Điểm tham quan, bảo tàng</option><option value="stay">Khách sạn, nơi lưu trú</option><option value="essentials">Tiện ích thiết yếu (nhiều nhóm)</option>
 </select></div>
 <div class="field"><label for="radius">Bán kính tìm kiếm</label><select id="radius"><option value="500">500 m</option><option value="1000">1 km</option><option value="1500" selected>1,5 km</option><option value="3000">3 km</option><option value="5000">5 km</option></select></div>
</div>
<button id="search" class="search-btn" type="button">Tìm địa điểm quanh đây ↗</button>
<p class="privacy">Quyền riêng tư: tọa độ tìm kiếm chỉ được gửi cho truy vấn bạn chủ động yêu cầu tới OpenStreetMap Overpass API; Nolane không lưu vị trí tìm kiếm vào D1 hoặc lịch sử. Địa điểm yêu thích chỉ được lưu trên trình duyệt này sau khi bạn bấm Lưu, gồm tên, loại và tọa độ của điểm đã chọn; không tải lên máy chủ và không đồng bộ giữa thiết bị.</p>
<div id="status" class="status" role="status" aria-live="polite"></div>
</section>
<section class="panel" aria-live="polite">
<div class="results-head"><strong>Kết quả tìm kiếm</strong><span id="resultCount">Chưa có truy vấn</span></div>
<div id="results" class="result-list"><div class="empty">Chọn vị trí và danh mục ở trên để bắt đầu.</div></div>
<div class="attribution">Dữ liệu bản đồ © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a>, được cung cấp theo Open Database License (ODbL).</div>
</section>
<section class="panel" aria-live="polite">
 <div class="results-head"><strong>Địa điểm đã lưu · Lịch trình</strong><span id="savedCount">0 / 50 điểm</span></div>
 <p class="help">Lưu các địa điểm bạn quan tâm, sau đó dùng nút lên/xuống để xếp thứ tự ghé thăm. Dữ liệu chỉ nằm trong bộ nhớ trình duyệt của thiết bị này.</p>
 <div id="savedPlaces" class="saved-list"><div class="empty">Chưa có điểm nào được lưu. Bấm “Lưu địa điểm” ở một kết quả để thêm vào lịch trình.</div></div>
 <div class="saved-toolbar"><span id="savedHint">Lịch trình là thứ tự do bạn tự sắp xếp, chưa phải tuyến đường được tối ưu.</span><button id="exportGpx" class="export-btn" type="button" disabled>Xuất lịch trình GPX ↓</button></div>
 <p class="attribution">GPX chứa các điểm dừng theo đúng thứ tự bạn sắp xếp. Nó không chứa đường đi, thời gian di chuyển hoặc chỉ dẫn rẽ; hãy mở bằng ứng dụng bản đồ có hỗ trợ GPX. Việc xuất tệp chỉ diễn ra khi bạn bấm nút.</p>
</section>
<section class="panel" aria-live="polite">
 <h2>Bản đồ tuyến đường</h2>
 <p class="help">Hiển thị đường đi theo đúng thứ tự điểm bạn đã xếp. Chỉ gửi yêu cầu định tuyến khi bạn bấm nút; thời gian là ước tính theo hồ sơ đường, không phải giao thông trực tiếp.</p>
 <div class="route-controls">
  <div class="field"><label for="routeProfile">Phương tiện</label><select id="routeProfile"><option value="driving">Ô tô</option><option value="cycling">Xe đạp</option><option value="walking">Đi bộ</option></select></div>
  <button id="routeButton" class="route-button" type="button">Tính tuyến đường ↗</button>
 </div>
 <div id="routeStatus" class="route-status" role="status" aria-live="polite">Lưu ít nhất hai địa điểm rồi bấm Tính tuyến đường để tính quãng đường thực tế.</div>
 <div id="routeSummary" class="route-summary" aria-live="polite"></div>
 <div id="routeMap" class="route-map" role="region" aria-label="Bản đồ các điểm dừng và tuyến đường được tính" tabindex="0"><div id="routeMapPlaceholder" class="route-map-placeholder">Bản đồ chỉ tải sau khi bạn chủ động bấm “Tính tuyến đường”. Khi đó nhà cung cấp bản đồ sẽ thấy khu vực đang xem qua yêu cầu các ô bản đồ.</div></div>
 <div id="routeLegs" class="route-legs"></div>
 <p class="route-provider-note">Yêu cầu tuyến đường gửi tọa độ các điểm dừng trực tiếp tới OSRM hoặc FOSSGIS theo phương tiện đã chọn; nhà cung cấp có thể ghi log yêu cầu. Dịch vụ công cộng dùng cho lưu lượng cá nhân thấp, tối đa một yêu cầu mỗi giây, không có SLA. Khi bản đồ mở sau thao tác đó, yêu cầu ô bản đồ cũng cho nhà cung cấp OSM biết vùng đang xem. Bản đồ © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a>. Chỉ tải các ô bản đồ cần cho vùng đang xem, không tải trước hoặc dùng ngoại tuyến.</p>
</section>
</main>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin="anonymous"></script>
<script>
(function(){
var $=function(id){return document.getElementById(id)};
function setStatus(value,error){$('status').textContent=value||'';$('status').classList.toggle('error',Boolean(error))}
function validCoordinate(input,min,max){var value=Number(input.value);return input.value.trim()!==''&&Number.isFinite(value)&&value>=min&&value<=max?value:null}
function syncEssentialsRadius(){
 var essentials=$('category').value==='essentials';
 var five=$('radius').querySelector('option[value="5000"]');
 if(five)five.disabled=essentials;
 if(essentials&&$('radius').value==='5000')$('radius').value='3000';
}
$('category').addEventListener('change',syncEssentialsRadius);
syncEssentialsRadius();
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
var STORAGE_KEY='nolane.nearby.saved-places.v1';
var MAX_SAVED=50;
function cleanSavedPlace(raw){
 if(!raw||typeof raw!=='object'||Array.isArray(raw))return null;
 var id=String(raw.id||'').match(/^(node|way|relation)\\/([1-9]\\d{0,15})$/);
 var latitude=raw.latitude,longitude=raw.longitude;
 if(!id||typeof latitude!=='number'||!Number.isFinite(latitude)||latitude < -90||latitude > 90||typeof longitude!=='number'||!Number.isFinite(longitude)||longitude < -180||longitude > 180)return null;
 function cleanText(value,max){return String(value||'').replace(/[\\u0000-\\u001f\\u007f]/g,' ').trim().slice(0,max)}
 var name=cleanText(raw.name,160);if(!name)return null;
 return {id:id[1]+'/'+id[2],name:name,category:cleanText(raw.category,40),categoryLabel:cleanText(raw.categoryLabel,60),detailType:cleanText(raw.detailType,80),latitude:latitude,longitude:longitude,address:cleanText(raw.address,220)};
}
function loadSavedPlaces(){
 try{
  var raw=JSON.parse(localStorage.getItem(STORAGE_KEY)||'[]');
  if(!Array.isArray(raw))return [];
  var seen={};return raw.slice(0,MAX_SAVED).map(cleanSavedPlace).filter(function(place){if(!place||seen[place.id])return false;seen[place.id]=true;return true}).slice(0,MAX_SAVED);
 }catch(error){return []}
}
var savedPlaces=loadSavedPlaces();
var ROUTE_PROFILES={
 driving:'https://router.project-osrm.org/route/v1/driving/',
 cycling:'https://routing.openstreetmap.de/routed-bike/route/v1/bike/',
 walking:'https://routing.openstreetmap.de/routed-foot/route/v1/foot/'
};
var ROUTE_MAX_STOPS=10;
var ROUTE_MAX_RESPONSE_BYTES=1500000;
var ROUTE_MAX_GEOMETRY_POINTS=20000;
var ROUTE_COOLDOWN_KEY='nolane.nearby.route-last-request-at.v1';
var routeMap=null,routeLineLayer=null,routeStopLayer=null,routeMapFailed=false,routeMapRequested=false;
var routeRequestInFlight=false,lastRouteRequestAt=0,lastRenderedRouteKey=null,routeRevision=0;
function reserveRouteRequestTime(now){
 var persisted=0;
 try{
  var stored=Number(localStorage.getItem(ROUTE_COOLDOWN_KEY));
  if(Number.isFinite(stored)&&stored>0)persisted=stored;
 }catch(error){}
 var last=Math.max(lastRouteRequestAt,persisted);
 var wait=last?1100-(now-last):0;
 if(wait>0)return wait;
 lastRouteRequestAt=now;
 try{localStorage.setItem(ROUTE_COOLDOWN_KEY,String(now))}catch(error){}
 return 0;
}
function routeProfileValue(){var value=$('routeProfile').value;return Object.prototype.hasOwnProperty.call(ROUTE_PROFILES,value)?value:'driving'}
function routeKey(){
 return routeProfileValue()+'|'+savedPlaces.slice(0,ROUTE_MAX_STOPS).map(function(place){return place.id+':'+place.latitude+','+place.longitude}).join(';');
}
function routeDistanceText(meters){return meters>=1000?(meters/1000).toFixed(2)+' km':Math.round(meters)+' m'}
function routeDurationText(seconds){
 var minutes=Math.max(1,Math.round(seconds/60));
 if(minutes<60)return minutes+' phút';
 var hours=Math.floor(minutes/60),remaining=minutes%60;
 return hours+' giờ'+(remaining?' '+remaining+' phút':'');
}
function clearRouteResult(message){
 if(routeLineLayer&&typeof routeLineLayer.clearLayers==='function')routeLineLayer.clearLayers();
 $('routeSummary').textContent='';
 $('routeLegs').replaceChildren();
 if(message)$('routeStatus').textContent=message;
}
function routeMapLibrary(){return typeof L!=='undefined'&&L&&typeof L.map==='function'?L:null}
function ensureRouteMap(){
 if(routeMap)return routeMap;
 if(routeMapFailed)return null;
 var leaflet=routeMapLibrary();
 if(!leaflet){routeMapFailed=true;$('routeMapPlaceholder').style.display='grid';$('routeMapPlaceholder').textContent='Thư viện Leaflet chưa sẵn sàng. Bạn vẫn có thể tính tổng quãng đường và thời gian; đường vẽ sẽ không hiển thị.';$('routeStatus').textContent='Thư viện bản đồ không tải được. Danh sách địa điểm và GPX vẫn dùng được; hãy thử tải lại trang.';return null}
 try{
  var initialPoints=savedPlaces.slice(0,ROUTE_MAX_STOPS);
  var initialCenter=initialPoints.length
   ? [initialPoints.reduce(function(sum,place){return sum+place.latitude},0)/initialPoints.length,
      initialPoints.reduce(function(sum,place){return sum+place.longitude},0)/initialPoints.length]
   : [0,0];
  routeMap=leaflet.map('routeMap',{scrollWheelZoom:false}).setView(initialCenter,13);
  if(initialPoints.length>1){
   var initialBounds=leaflet.latLngBounds(initialPoints.map(function(place){return [place.latitude,place.longitude]}));
   routeMap.fitBounds(initialBounds,{padding:[28,28],maxZoom:15});
  }
  $('routeMapPlaceholder').style.display='none';
  leaflet.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
   maxZoom:19,attribution:'© OpenStreetMap contributors'
  }).addTo(routeMap);
  routeLineLayer=leaflet.layerGroup().addTo(routeMap);
  routeStopLayer=leaflet.layerGroup().addTo(routeMap);
  return routeMap;
 }catch(error){
  routeMapFailed=true;routeMap=null;
  $('routeStatus').textContent='Không thể khởi tạo bản đồ. Danh sách điểm và xuất GPX vẫn hoạt động.';
  return null;
 }
}
function refreshRouteStops(){
 var nextKey=routeKey();
 if(lastRenderedRouteKey!==null&&lastRenderedRouteKey!==nextKey){
  routeRevision+=1;clearRouteResult('Lịch trình hoặc phương tiện đã thay đổi. Hãy tính lại tuyến đường nếu cần.');
 }
 lastRenderedRouteKey=nextKey;
 if(!routeMapRequested)return;
 var map=ensureRouteMap();var leaflet=routeMapLibrary();
 if(!map||!leaflet||!routeStopLayer)return;
 routeStopLayer.clearLayers();
 var points=savedPlaces.slice(0,ROUTE_MAX_STOPS);
 points.forEach(function(place,index){
  var icon=leaflet.divIcon({
   className:'route-stop-icon',html:String(index+1),iconSize:[28,28],iconAnchor:[14,14]
  });
  var marker=leaflet.marker([place.latitude,place.longitude],{icon:icon});
  marker.bindTooltip(String(index+1),{direction:'top',offset:[0,-10]});
  routeStopLayer.addLayer(marker);
 });
 if(points.length>0){
  var bounds=leaflet.latLngBounds(points.map(function(place){return [place.latitude,place.longitude]}));
  map.fitBounds(bounds,{padding:[28,28],maxZoom:15});
 }
 map.invalidateSize();
 if(savedPlaces.length>ROUTE_MAX_STOPS){
  $('routeStatus').textContent='Danh sách có '+savedPlaces.length+' điểm. Tuyến đường dùng 10 điểm đầu theo đúng thứ tự hiện tại.';
 }else if(points.length<2){
  $('routeStatus').textContent='Lưu ít nhất hai địa điểm rồi bấm Tính tuyến đường để tính quãng đường thực tế.';
 }
}
async function readRoutePayload(response){
 var max=ROUTE_MAX_RESPONSE_BYTES;
 var declared=Number(response.headers.get('content-length'));
 if(Number.isFinite(declared)&&declared>max)throw new Error('Phản hồi định tuyến vượt giới hạn kích thước cho phép.');
 if(!response.body)throw new Error('Nhà cung cấp trả về phản hồi rỗng.');
 var reader=response.body.getReader(),chunks=[],total=0;
 try{
  while(true){
   var part=await reader.read();if(part.done)break;
   total+=part.value.byteLength;
   if(total>max){await reader.cancel('route response too large').catch(function(){});throw new Error('Phản hồi định tuyến vượt giới hạn kích thước cho phép.')}
   chunks.push(part.value);
  }
 }finally{reader.releaseLock()}
 var bytes=new Uint8Array(total),offset=0;
 chunks.forEach(function(chunk){bytes.set(chunk,offset);offset+=chunk.byteLength});
 try{return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes))}
 catch(error){throw new Error('Nhà cung cấp trả về dữ liệu JSON không hợp lệ.')}
}
function validateRoutePayload(data,expectedStops){
 if(!data||typeof data!=='object'||Array.isArray(data))throw new Error('Dữ liệu tuyến đường không hợp lệ.');
 if(data.code!=='Ok'){
  if(data.code==='NoRoute')throw new Error('Không tìm được đường nối tất cả điểm dừng. Hãy thử danh mục hoặc phương tiện khác.');
  if(data.code==='NoSegment')throw new Error('Một điểm dừng không nằm gần đường có thể định tuyến. Hãy kiểm tra lại địa điểm.');
  if(data.code==='TooBig')throw new Error('Tuyến đường quá lớn. Hãy giảm số điểm dừng.');
  throw new Error('Dịch vụ định tuyến trả về lỗi: '+String(data.code||'không rõ').slice(0,40));
 }
 var route=Array.isArray(data.routes)?data.routes[0]:null;
 if(!route||!Number.isFinite(route.distance)||route.distance<0||!Number.isFinite(route.duration)||route.duration<0)
  throw new Error('Nhà cung cấp không trả về tổng quãng đường/thời gian hợp lệ.');
 if(!route.geometry||route.geometry.type!=='LineString'||!Array.isArray(route.geometry.coordinates)||
    route.geometry.coordinates.length<2||route.geometry.coordinates.length>ROUTE_MAX_GEOMETRY_POINTS)
  throw new Error('Hình dạng tuyến đường không hợp lệ hoặc vượt giới hạn điểm.');
 var coordinates=route.geometry.coordinates.map(function(point){
  if(!Array.isArray(point)||point.length<2||typeof point[0]!=='number'||typeof point[1]!=='number'||
     !Number.isFinite(point[0])||!Number.isFinite(point[1])||point[0]<-180||point[0]>180||point[1]<-90||point[1]>90)
   throw new Error('Tọa độ trong hình học tuyến đường không hợp lệ.');
  return [point[0],point[1]];
 });
 if(!Array.isArray(route.legs)||route.legs.length!==expectedStops-1)
  throw new Error('Số chặng tuyến đường không khớp với danh sách điểm dừng.');
 var legs=route.legs.map(function(leg){
  if(!leg||!Number.isFinite(leg.distance)||leg.distance<0||!Number.isFinite(leg.duration)||leg.duration<0)
   throw new Error('Thông tin một chặng tuyến đường không hợp lệ.');
  return {distance:leg.distance,duration:leg.duration};
 });
 if(!Array.isArray(data.waypoints)||data.waypoints.length!==expectedStops)
  throw new Error('Số điểm định tuyến trả về không khớp với lịch trình.');
 return {distance:route.distance,duration:route.duration,geometry:{type:'LineString',coordinates:coordinates},legs:legs};
}
function buildRouteUrl(profile,places){
 var base=ROUTE_PROFILES[profile];
 if(!base)throw new Error('Phương tiện định tuyến không hợp lệ.');
 var coordinates=places.map(function(place){return place.longitude.toFixed(5)+','+place.latitude.toFixed(5)}).join(';');
 return base+coordinates+'?overview=full&geometries=geojson&steps=false&alternatives=false';
}
function drawComputedRoute(route,places){
 var leaflet=routeMapLibrary();
 if(!routeMap||!leaflet||!routeLineLayer){
  $('routeStatus').textContent='Đã tính được quãng đường và thời gian, nhưng bản đồ không hiển thị do thư viện Leaflet không tải được.';
  return;
 }
 routeLineLayer.clearLayers();
 var feature={type:'Feature',properties:{},geometry:route.geometry};
 routeLineLayer.addLayer(leaflet.geoJSON(feature,{style:{color:'#5379e7',weight:5,opacity:.88,lineCap:'round',lineJoin:'round'}}));
 var bounds=leaflet.latLngBounds(route.geometry.coordinates.map(function(point){return [point[1],point[0]]}));
 routeMap.fitBounds(bounds,{padding:[34,34],maxZoom:16});
 routeMap.invalidateSize();
}
function renderRouteMetrics(route,places){
 $('routeSummary').textContent='Tổng quãng đường: '+routeDistanceText(route.distance)+' · Thời gian ước tính: '+routeDurationText(route.duration);
 var box=$('routeLegs');box.replaceChildren();
 route.legs.forEach(function(leg,index){
  var label=places[index].name+' → '+places[index+1].name;
  var row=addText(box,'div','route-leg','');
  addText(row,'strong','',String(index+1)+'. '+label);
  addText(row,'div','',routeDistanceText(leg.distance)+' · '+routeDurationText(leg.duration));
 });
}
async function requestSavedPlacesRoute(){
 if(routeRequestInFlight)return;
 if(savedPlaces.length<2){$('routeStatus').textContent='Cần ít nhất hai địa điểm đã lưu để tính tuyến đường.';return}
 var profile=routeProfileValue(),places=savedPlaces.slice(0,ROUTE_MAX_STOPS);
 var url;
 try{url=buildRouteUrl(profile,places)}catch(error){$('routeStatus').textContent=error.message;return}
 var now=Date.now(),wait=reserveRouteRequestTime(now);
 if(wait>0){
  $('routeStatus').textContent='Để bảo vệ dịch vụ bản đồ công cộng, hãy chờ '+(wait/1000).toFixed(1)+' giây trước yêu cầu tiếp theo.';
  return;
 }
 routeRequestInFlight=true;$('routeButton').disabled=true;
 routeMapRequested=true;refreshRouteStops();
 var signature=routeKey(),revision=routeRevision;
 $('routeStatus').classList.remove('error');
 $('routeStatus').textContent='Đang tính tuyến đường qua dịch vụ '+(profile==='driving'?'ô tô':profile==='cycling'?'xe đạp':'đi bộ')+'…';
 try{
  var response=await fetch(url,{
   method:'GET',mode:'cors',credentials:'omit',redirect:'error',
   headers:{accept:'application/json'},referrerPolicy:'strict-origin-when-cross-origin'
  });
  if(!response.ok)throw new Error('Dịch vụ định tuyến trả về HTTP '+response.status+'. Hãy thử lại sau.');
  var payload=await readRoutePayload(response);
  var route=validateRoutePayload(payload,places.length);
  if(revision!==routeRevision||signature!==routeKey()){
   $('routeStatus').textContent='Lịch trình đã thay đổi trong lúc chờ định tuyến. Kết quả cũ đã bị bỏ qua; hãy bấm tính lại.';
   return;
  }
  drawComputedRoute(route,places);
  renderRouteMetrics(route,places);
  $('routeStatus').textContent='Đã tính tuyến theo thứ tự bạn đã xếp. Thời gian chỉ là ước tính theo hồ sơ đường, không phản ánh giao thông trực tiếp.'+
   (savedPlaces.length>ROUTE_MAX_STOPS?' Đã dùng 10 điểm đầu; các điểm còn lại chưa được đưa vào tuyến.':'');
 }catch(error){
  $('routeStatus').textContent=error&&error.message?error.message:'Không thể tính tuyến đường lúc này.';
  $('routeStatus').classList.add('error');
 }finally{
  routeRequestInFlight=false;$('routeButton').disabled=savedPlaces.length<2;
 }
}
$('routeButton').addEventListener('click',requestSavedPlacesRoute);
$('routeProfile').addEventListener('change',function(){
 routeRevision+=1;clearRouteResult('Đã đổi phương tiện. Bấm Tính tuyến đường để tính lại.');
});
function persistSavedPlaces(next){
 try{localStorage.setItem(STORAGE_KEY,JSON.stringify(next));savedPlaces=next;renderSavedPlaces();return true}
 catch(error){setStatus('Không thể lưu trên trình duyệt này. Hãy kiểm tra chế độ riêng tư hoặc dung lượng lưu trữ.',true);return false}
}
function savePlace(raw){
 var place=cleanSavedPlace({id:raw.id,name:raw.name,category:raw.category,categoryLabel:raw.categoryLabel,detailType:raw.detailType,latitude:raw.latitude,longitude:raw.longitude,address:raw.address});
 if(!place){setStatus('Không thể lưu địa điểm do dữ liệu không hợp lệ.',true);return}
 if(savedPlaces.some(function(item){return item.id===place.id})){setStatus('Địa điểm này đã có trong danh sách lưu.');return}
 if(savedPlaces.length>=MAX_SAVED){setStatus('Danh sách đã đạt giới hạn '+MAX_SAVED+' địa điểm. Hãy xóa bớt trước khi lưu thêm.',true);return}
 if(persistSavedPlaces(savedPlaces.concat([place])))setStatus('Đã lưu “'+place.name+'” trên thiết bị này.');
}
function moveSavedPlace(index,delta){
 var target=index+delta;if(target<0||target>=savedPlaces.length)return;
 var next=savedPlaces.slice();var item=next[index];next[index]=next[target];next[target]=item;persistSavedPlaces(next);
}
function removeSavedPlace(index){
 if(index<0||index>=savedPlaces.length)return;
 var removed=savedPlaces[index];if(persistSavedPlaces(savedPlaces.filter(function(_,i){return i!==index})))setStatus('Đã xóa “'+removed.name+'” khỏi danh sách trên thiết bị này.');
}
function osmMapUrl(place){
 var lat=place.latitude.toFixed(5),lon=place.longitude.toFixed(5);
 return 'https://www.openstreetmap.org/?mlat='+lat+'&mlon='+lon+'#map=18/'+lat+'/'+lon;
}
function syncResultSaveButtons(){
 document.querySelectorAll('.place').forEach(function(card){
  var id=card.getAttribute('data-osm-id'),button=card.querySelector('.save-btn');if(!id||!button)return;
  var isSaved=savedPlaces.some(function(item){return item.id===id});button.textContent=isSaved?'Đã lưu':'＋ Lưu địa điểm';button.disabled=isSaved;
 });
}
function renderSavedPlaces(){
 var box=$('savedPlaces');if(!box)return;box.replaceChildren();
 $('savedCount').textContent=savedPlaces.length+' / '+MAX_SAVED+' điểm';
 $('exportGpx').disabled=savedPlaces.length===0;
 syncResultSaveButtons();
 if(!savedPlaces.length){addText(box,'div','empty','Chưa có điểm nào được lưu. Bấm “Lưu địa điểm” ở một kết quả để thêm vào lịch trình.');refreshRouteStops();$('routeButton').disabled=true;return}
 savedPlaces.forEach(function(place,index){
  var card=addText(box,'article','saved-place','');
  addText(card,'span','stop-number',String(index+1));
  var details=addText(card,'div','','');addText(details,'h3','',place.name);
  addText(details,'div','place-meta',[place.categoryLabel||place.category,place.address].filter(Boolean).join(' · '));
  var actions=addText(card,'div','saved-actions','');
  var up=addText(actions,'button','','↑');up.type='button';up.setAttribute('aria-label','Đưa '+place.name+' lên');up.disabled=index===0;up.addEventListener('click',function(){moveSavedPlace(index,-1)});
  var down=addText(actions,'button','','↓');down.type='button';down.setAttribute('aria-label','Đưa '+place.name+' xuống');down.disabled=index===savedPlaces.length-1;down.addEventListener('click',function(){moveSavedPlace(index,1)});
  var map=addText(actions,'a','','OSM');map.href=osmMapUrl(place);map.target='_blank';map.rel='noopener noreferrer';map.className='saved-map-link';
  var remove=addText(actions,'button','','Xóa');remove.type='button';remove.setAttribute('aria-label','Xóa '+place.name);remove.addEventListener('click',function(){removeSavedPlace(index)});
 });
 refreshRouteStops();
 $('routeButton').disabled=savedPlaces.length<2||routeRequestInFlight;
}
function xmlEscape(value){return String(value).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;')}
function exportSavedPlaces(){
 if(!savedPlaces.length)return;
 var route=savedPlaces.map(function(place){return '    <rtept lat="'+place.latitude.toFixed(7)+'" lon="'+place.longitude.toFixed(7)+'"><name>'+xmlEscape(place.name)+'</name><desc>'+xmlEscape(place.categoryLabel||place.category)+'</desc></rtept>'}).join('\\n');
 var gpx='<?xml version="1.0" encoding="UTF-8"?>\\n<gpx version="1.1" creator="Nolane Search" xmlns="http://www.topografix.com/GPX/1/1">\\n  <rte>\\n    <name>Nolane itinerary</name>\\n'+route+'\\n  </rte>\\n</gpx>\\n';
 var url=URL.createObjectURL(new Blob([gpx],{type:'application/gpx+xml;charset=utf-8'}));
 var link=document.createElement('a');link.href=url;link.download='nolane-itinerary.gpx';document.body.appendChild(link);link.click();link.remove();window.setTimeout(function(){URL.revokeObjectURL(url)},1000);
 setStatus('Đã xuất '+savedPlaces.length+' điểm dừng thành tệp GPX. Tệp giữ thứ tự đã sắp xếp, không chứa tuyến đường được tính toán.');
}
$('exportGpx').addEventListener('click',exportSavedPlaces);
function render(data){
 var box=$('results');box.replaceChildren();
 $('resultCount').textContent=data.resultCount+' địa điểm · '+distanceText(data.radiusMeters);
 if(!data.places.length){addText(box,'div','empty','Không tìm thấy địa điểm có tên trong bán kính này. Hãy thử tăng bán kính hoặc chọn danh mục khác.');return}
 data.places.forEach(function(place){
  var card=addText(box,'article','place','');card.setAttribute('data-osm-id',place.id);
  var top=addText(card,'div','place-top','');var title=addText(top,'div','','');
  addText(title,'h3','',place.name);addText(title,'div','place-type',place.detailType||place.categoryLabel);
  addText(top,'span','distance',distanceText(place.distanceMeters));
  if(place.address)addText(card,'div','place-meta',place.address);
  if(place.openingHours)addText(card,'div','place-meta','Giờ ghi trên OSM: '+place.openingHours+' · Chưa xác nhận đang mở.');
  var actions=addText(card,'div','place-actions','');
  var map=safeHttps(place.mapUrl);if(map){var link=addText(actions,'a','','Xem bản đồ');link.href=map;link.target='_blank';link.rel='noopener noreferrer'}
  var osm=safeHttps(place.osmUrl);if(osm){var source=addText(actions,'a','','Trang dữ liệu OSM');source.href=osm;source.target='_blank';source.rel='noopener noreferrer'}
  var website=safeHttps(place.website);if(website){var site=addText(actions,'a','','Website');site.href=website;site.target='_blank';site.rel='noopener noreferrer'}
  var alreadySaved=savedPlaces.some(function(item){return item.id===place.id});
  var save=addText(actions,'button','save-btn',alreadySaved?'Đã lưu':'＋ Lưu địa điểm');save.type='button';save.disabled=alreadySaved;
  save.addEventListener('click',function(){savePlace(place);if(savedPlaces.some(function(item){return item.id===place.id})){save.textContent='Đã lưu';save.disabled=true}});
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
renderSavedPlaces();
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
      "referrer-policy": "strict-origin-when-cross-origin",
      "content-security-policy": "default-src 'self'; script-src 'unsafe-inline' https://unpkg.com; style-src 'unsafe-inline' https://unpkg.com; connect-src 'self' https://router.project-osrm.org https://routing.openstreetmap.de; img-src 'self' data: https://tile.openstreetmap.org https://unpkg.com; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
    },
  });
}
