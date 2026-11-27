const HTML = String.raw`<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#f8fafc"><meta name="robots" content="noindex,nofollow">
<title>Nolane Search</title>
<style>
:root{color-scheme:light;--bg:#f7f8fc;--panel:#fff;--ink:#182235;--muted:#68758a;--line:#e5eaf2;--accent:#315efb;--accent2:#2449d8;--soft:#edf2ff;--green:#16845b;--shadow:0 14px 45px rgba(20,38,70,.08)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
button,input,textarea{font:inherit}button{cursor:pointer}a{color:inherit}.shell{max-width:1180px;margin:auto;padding:0 28px}.topbar{height:74px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);background:rgba(255,255,255,.78);backdrop-filter:blur(14px);position:sticky;top:0;z-index:5}.brand{display:flex;align-items:center;gap:11px;text-decoration:none;font-weight:780;letter-spacing:-.04em;font-size:20px}.mark{width:34px;height:34px;border-radius:12px;background:linear-gradient(135deg,#315efb,#6e87ff);display:grid;place-items:center;color:white;box-shadow:0 5px 14px #315efb35}.top-actions{display:flex;align-items:center;gap:10px}.pill{border:1px solid var(--line);background:#fff;border-radius:999px;color:var(--muted);padding:7px 12px;font-size:12px}.quiet{border:0;background:transparent;color:var(--muted);padding:9px 12px;border-radius:10px}.quiet:hover{background:#eef1f7}.btn{border:0;background:var(--accent);color:#fff;padding:11px 17px;border-radius:12px;font-weight:650;box-shadow:0 6px 15px #315efb2a}.btn:hover{background:var(--accent2)}.btn:disabled{opacity:.55;cursor:wait}.hero{padding:70px 0 30px;text-align:center}.eyebrow{display:inline-flex;align-items:center;gap:7px;color:var(--accent);background:var(--soft);border:1px solid #dce5ff;border-radius:999px;padding:6px 11px;font-size:12px;font-weight:650}.hero h1{font-size:clamp(34px,5vw,54px);letter-spacing:-.055em;line-height:1.08;margin:18px 0 12px}.hero p{color:var(--muted);font-size:16px;margin:0 auto 26px;max-width:620px}.search-wrap{max-width:790px;margin:0 auto}.searchbox{display:flex;align-items:center;gap:12px;background:#fff;border:1px solid #dce3ef;border-radius:18px;padding:8px 9px 8px 18px;box-shadow:var(--shadow);transition:.2s}.searchbox:focus-within{border-color:#9aafff;box-shadow:0 0 0 4px #315efb16,var(--shadow)}.search-icon{color:#8190a8;font-size:20px}.searchbox input{border:0;outline:0;min-width:0;flex:1;background:transparent;color:var(--ink);font-size:16px;padding:10px 0}.searchbox input::placeholder{color:#9aa5b5}.searchbox .btn{white-space:nowrap}.chips{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin:17px 0}.chip{border:1px solid var(--line);background:#fff;color:#65738a;border-radius:999px;padding:7px 13px;font-size:13px}.chip.active,.chip:hover{background:var(--soft);color:var(--accent);border-color:#cdd9ff}.content{padding:14px 0 70px}.layout{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:26px;align-items:start}.maincol{min-width:0}.summarybar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:7px 0 16px;color:var(--muted);font-size:13px}.result{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:17px 19px;margin:0 0 12px;transition:.18s}.result:hover{border-color:#c5d2f5;box-shadow:0 6px 20px #1f3f7a0a;transform:translateY(-1px)}.result-url{display:flex;gap:8px;align-items:center;color:#6e7b91;font-size:12px;margin-bottom:5px;min-width:0}.favicon{width:18px;height:18px;border-radius:5px;background:#eef2f8;display:grid;place-items:center;font-size:10px;color:#63728a;flex:0 0 auto}.result h3{font-size:18px;line-height:1.35;margin:0 0 6px;color:#2455d6;font-weight:650;letter-spacing:-.015em}.result h3 a{text-decoration:none}.result h3 a:hover{text-decoration:underline}.result p{color:#526077;margin:0;font-size:14px;line-height:1.6}.result-meta{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:10px;color:#8a95a7;font-size:11px}.tag{background:#f0f3f8;border-radius:5px;padding:2px 6px}.empty{background:#fff;border:1px dashed #d6deea;border-radius:16px;text-align:center;padding:36px 20px;color:var(--muted)}.empty strong{display:block;color:var(--ink);font-size:17px;margin-bottom:5px}.side{position:sticky;top:92px}.panel{background:#fff;border:1px solid var(--line);border-radius:18px;box-shadow:0 8px 26px #1d35570a;overflow:hidden}.panel-head{padding:16px 17px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}.panel-head strong{font-size:14px}.panel-body{padding:16px}.ai-card{background:linear-gradient(145deg,#f8faff,#fff);border:1px solid #e1e8ff;border-radius:15px;padding:15px;margin-bottom:12px}.ai-card h3{font-size:14px;margin:0 0 7px}.ai-card p{font-size:13px;color:#58667d;margin:0}.muted{color:var(--muted)}.mini{font-size:11px;color:#8995a7}.answer{white-space:pre-wrap;font-size:14px;line-height:1.7;color:#37445a}.sources{display:grid;gap:7px;margin-top:14px}.source{display:block;text-decoration:none;border:1px solid var(--line);padding:8px 9px;border-radius:10px;font-size:12px;color:#3157be;overflow-wrap:anywhere}.source:hover{background:#f5f7ff}.chat{display:flex;flex-direction:column;min-height:280px}.chat-log{display:flex;flex-direction:column;gap:10px;max-height:380px;overflow:auto;padding:14px}.bubble{max-width:94%;padding:10px 12px;border-radius:13px;font-size:13px;white-space:pre-wrap;overflow-wrap:anywhere}.bubble.user{align-self:flex-end;background:#315efb;color:#fff;border-bottom-right-radius:4px}.bubble.assistant{align-self:flex-start;background:#f0f3f9;color:#344158;border-bottom-left-radius:4px}.chat-form{border-top:1px solid var(--line);padding:11px;display:flex;flex-direction:column;gap:8px}.chat-attachments{display:flex;align-items:center;gap:9px;min-width:0}.chat-attach{display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border:1px solid var(--line);border-radius:9px;background:var(--panel);color:var(--muted);font-size:12px;cursor:pointer;white-space:nowrap}.chat-attach:hover{background:var(--soft);color:var(--accent);border-color:#cdd9ff}.chat-file-name{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.chat-composer{display:flex;gap:7px}.chat-form textarea{resize:vertical;min-height:42px;max-height:110px;flex:1;min-width:0;border:1px solid var(--line);border-radius:11px;padding:9px 10px;outline:0;font-size:13px}.chat-form textarea:focus{border-color:#9aafff}.send{width:42px;flex:0 0 42px;border:0;border-radius:11px;background:var(--accent);color:#fff;font-size:18px}.hidden{display:none!important}.loading{display:flex;align-items:center;gap:10px;color:var(--muted);padding:20px;font-size:13px}.spinner{width:17px;height:17px;border:2px solid #dce4f5;border-top-color:var(--accent);border-radius:50%;animation:spin .8s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}.notice{padding:12px 14px;border-radius:12px;background:#fff7e8;color:#855b15;border:1px solid #f4e1bc;font-size:13px;margin:12px 0}.auth{max-width:540px;margin:62px auto;background:#fff;border:1px solid var(--line);border-radius:22px;padding:28px;box-shadow:var(--shadow);text-align:center}.auth h2{margin:12px 0 6px;letter-spacing:-.03em}.auth p{color:var(--muted);font-size:14px}.footer{padding:22px 0 35px;border-top:1px solid var(--line);color:#8a95a7;font-size:12px;display:flex;justify-content:space-between;gap:12px}.recent{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin:9px auto 0}.recent button{border:0;background:transparent;color:#7a879b;font-size:12px;text-decoration:underline;text-underline-offset:3px}.search-mode{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.desktop-only{display:block}
@media(max-width:900px){.layout{grid-template-columns:minmax(0,1fr)}.side{position:static;display:grid;grid-template-columns:1fr 1fr;gap:12px}.panel{min-width:0}.chat-log{max-height:300px}}
@media(max-width:620px){.shell{padding:0 16px}.topbar{height:62px}.pill{display:none}.hero{padding:46px 0 22px}.hero h1{font-size:37px}.hero p{font-size:14px}.searchbox{border-radius:15px;padding-left:13px;gap:8px}.searchbox .btn{padding:10px 12px}.chips{justify-content:flex-start;overflow:auto;flex-wrap:nowrap;padding-bottom:4px}.chip{white-space:nowrap}.side{grid-template-columns:1fr}.result{padding:15px}.result h3{font-size:16px}.footer{display:block}.footer span{display:block;margin:4px 0}.quiet{padding:8px}}
@media(prefers-color-scheme:dark){body.dark-auto{--bg:#0e1420;--panel:#151e2d;--ink:#e8edf7;--muted:#a0adc1;--line:#2b374a;--soft:#1b2b50;--accent:#7696ff;--accent2:#5579f5;--shadow:0 12px 35px #0005}body.dark-auto .topbar{background:#111a28dc}body.dark-auto .searchbox,body.dark-auto .result,body.dark-auto .panel,body.dark-auto .auth,body.dark-auto .chip{background:#151e2d}body.dark-auto .result h3{color:#91aaff}body.dark-auto .result p,body.dark-auto .answer{color:#bdc8da}body.dark-auto .ai-card{background:#172238;border-color:#2a3b60}body.dark-auto .bubble.assistant{background:#202c3d;color:#e3eaf5}body.dark-auto .chat-form textarea{background:#101927;color:#e8edf7;border-color:#344158}body.dark-auto .quiet{color:#a0adc1}}

:root[data-theme="dark"]{color-scheme:dark;--bg:#0e1420;--panel:#151e2d;--ink:#e8edf7;--muted:#a0adc1;--line:#2b374a;--soft:#1b2b50;--accent:#7696ff;--accent2:#5579f5;--shadow:0 12px 35px #0005}
:root[data-theme="dark"] .topbar{background:#111a28e8}
:root[data-theme="dark"] .searchbox,:root[data-theme="dark"] .result,:root[data-theme="dark"] .panel,:root[data-theme="dark"] .auth,:root[data-theme="dark"] .chip{background:#151e2d}
:root[data-theme="dark"] .result h3{color:#91aaff}
:root[data-theme="dark"] .result p,:root[data-theme="dark"] .answer{color:#bdc8da}
:root[data-theme="dark"] .ai-card{background:#172238;border-color:#2a3b60}
:root[data-theme="dark"] .bubble.assistant{background:#202c3d;color:#e3eaf5}
:root[data-theme="dark"] .chat-form textarea{background:#101927;color:#e8edf7;border-color:#344158}
:root[data-theme="dark"] .quiet{color:#a0adc1}
:root[data-theme="dark"] .result-meta .tag{background:#273348}

.result-actions{display:flex;align-items:center;gap:8px;margin-top:11px;flex-wrap:wrap}
.feedback-btn{border:1px solid var(--line);background:transparent;color:var(--muted);padding:5px 9px;border-radius:8px;font-size:11px}
.feedback-btn:hover{background:var(--soft);color:var(--accent);border-color:#cdd9ff}
.feedback-btn:disabled{opacity:.65;cursor:default}
.crawl-form{display:grid;gap:8px}
.crawl-form input,.crawl-form select{width:100%;border:1px solid var(--line);border-radius:10px;padding:9px 10px;background:var(--panel);color:var(--ink);outline:0;font-size:13px}
.crawl-form input:focus,.crawl-form select:focus{border-color:#9aafff;box-shadow:0 0 0 3px #315efb12}
.crawl-job{padding:9px 10px;border:1px solid var(--line);border-radius:10px;margin-top:8px;font-size:12px;overflow-wrap:anywhere}
.crawl-job strong{display:block;margin-bottom:3px}
.crawl-job .mini{display:block}
.index-tools{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:7px;margin-top:16px}
.index-tools input{min-width:0;width:100%;border:1px solid var(--line);border-radius:9px;padding:8px 9px;background:var(--panel);color:var(--ink);font-size:12px;outline:0}
.index-tools input:focus{border-color:#9aafff}
.index-entry{padding:10px;border:1px solid var(--line);border-radius:11px;margin-top:8px;overflow-wrap:anywhere}
.index-entry a{display:block;color:var(--accent);font-size:12px;font-weight:650;text-decoration:none;line-height:1.45}
.index-entry a:hover{text-decoration:underline}
.index-entry .mini{display:block;margin-top:3px}
.index-entry-actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:7px}
.index-entry-actions button{font-size:10px;padding:4px 7px}
#indexPages{max-height:390px;overflow:auto}.tools-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:16px}.tool-card{border:1px solid var(--line);border-radius:14px;padding:14px;background:var(--panel);min-width:0}.tool-card h3{font-size:14px;margin:0 0 6px}.tool-card p{font-size:12px;color:var(--muted);margin:0 0 11px}.tool-card .mini{display:block;margin:3px 0}.tool-card button{width:100%;margin-top:8px}.tool-jobs{display:grid;gap:8px}.tool-job{border:1px solid var(--line);border-radius:10px;padding:10px;font-size:12px;overflow-wrap:anywhere}.tool-job strong{display:block}.tool-badge{display:inline-block;border-radius:999px;padding:3px 8px;background:var(--soft);color:var(--accent);font-size:10px;font-weight:700}

</style>
</head>
<body>
<header class="topbar"><div class="shell" style="width:100%;display:flex;align-items:center;justify-content:space-between">
<a class="brand" href="/"><span class="mark">N</span><span>Nolane<span style="color:#315efb"> Search</span></span></a>
<div class="top-actions"><span class="pill">Private search workspace</span><button id="mediaBtn" class="quiet hidden" type="button">▣ Media</button><button id="toolsBtn" class="quiet hidden" type="button">🧰 Tools</button><button id="themeBtn" class="quiet" title="Đổi giao diện">◐</button><button id="logoutBtn" class="quiet hidden">Đăng xuất</button></div>
</div></header>
<main class="shell">
<section id="auth" class="auth hidden"><div class="mark" style="margin:auto;width:46px;height:46px;font-size:20px">N</div><h2>Không gian tìm kiếm riêng tư</h2><p id="authText">Để đăng nhập, hãy mở bot Nolane Search trên Telegram, gửi lệnh <b>/web</b>, sau đó mở đường dẫn bot gửi cho bạn.</p><div id="authError" class="notice hidden"></div></section>
<section id="workspace" class="hidden">
<div class="hero"><span class="eyebrow">✦ Tìm kiếm đa nguồn · AI có dẫn chứng</span><h1>Tìm đúng điều bạn cần.</h1><p>Kết hợp tìm kiếm web, nghiên cứu, tin tức và AI để bạn khám phá thông tin nhanh hơn, có nguồn để kiểm chứng.</p>
<div class="search-wrap"><form id="searchForm" class="searchbox"><span class="search-icon">⌕</span><input id="query" autocomplete="off" placeholder="Tìm kiếm bất cứ điều gì..." aria-label="Từ khóa tìm kiếm"><button class="btn" id="searchBtn">Tìm kiếm</button></form></div>
<div id="modeChips" class="chips">
<button class="chip active" data-mode="web">Tất cả</button><button class="chip" data-mode="news">Tin tức</button><button class="chip" data-mode="research">Nghiên cứu</button><button class="chip" data-mode="tech">Công nghệ</button><button class="chip" data-mode="github">GitHub</button><button class="chip" data-mode="wiki">Wikipedia</button><button class="chip" data-mode="local">Website của tôi</button>
</div><div id="recent" class="recent"></div>
</div>
<section id="toolsHub" class="content hidden">
  <div class="panel" style="padding:20px">
    <div class="summarybar"><div><span class="eyebrow">GitHub Actions · Hosted runner</span><h2 style="margin:10px 0 4px">Nolane Tools</h2><p class="muted" style="margin:0">Bộ công cụ xử lý tệp chạy trên GitHub Actions. Tệp có thể gửi qua Telegram hoặc đính kèm từ Web Chat; runner tải tệp từ Telegram khi chạy và không commit vào repository.</p></div><button id="refreshToolJobs" class="quiet" type="button">Làm mới job</button></div>
    <div class="notice">Cách dùng: mở chat riêng với bot, gửi <b>/tools</b>, chọn <b>/tool image-ocr</b> rồi gửi ảnh. Gửi ảnh bình thường cũng tự chạy OCR. PDF, audio, video, CSV, JSON và Office sẽ tự nhận diện công cụ phù hợp.</div>
    <div class="index-tools"><input id="toolFilter" type="search" placeholder="Tìm theo tên, ID, mô tả hoặc định dạng"><select id="toolCategoryFilter" aria-label="Lọc danh mục"><option value="all">Tất cả danh mục</option><option value="image">Hình ảnh & OCR</option><option value="document">PDF & Office</option><option value="audio-video">Âm thanh & Video</option><option value="data">Dữ liệu</option><option value="developer">Lập trình & văn bản</option><option value="repository">Mã nguồn & Repository</option><option value="utility">Tiện ích</option></select></div><div id="toolCatalogMeta" class="mini" style="margin-top:8px">Đang tải catalog…</div>
    <div id="toolCatalog" class="tools-grid"><div class="loading"><span class="spinner"></span><span>Đang tải danh mục công cụ…</span></div></div>
    <h3 style="margin:26px 0 8px">Lịch sử tác vụ</h3><div id="toolJobs" class="tool-jobs"><span class="mini">Chưa tải lịch sử.</span></div>
  </div>
</section>
<section id="searchContent" class="content">
<div id="resultLayout" class="layout">
<div class="maincol"><div class="summarybar"><span id="resultSummary">Sẵn sàng tìm kiếm</span><div class="search-mode"><button id="answerBtn" class="quiet hidden">✧ Tổng hợp bằng AI</button></div></div><div id="results"><div class="empty"><strong>Chào mừng đến Nolane Search</strong>Nhập một câu hỏi hoặc từ khóa để bắt đầu khám phá.</div></div></div>
<aside class="side">
<section class="panel"><div class="panel-head"><strong>⌁ Personal Web Index</strong><button id="refreshCrawls" class="quiet" style="font-size:11px">Làm mới</button></div><div class="panel-body">
<p class="muted" style="font-size:12px;margin:0 0 12px">Thu thập một website công khai để tạo chỉ mục riêng. Chỉ crawl cùng tên miền và tuân thủ robots.txt.</p>
<form id="crawlForm" class="crawl-form"><input id="crawlUrl" type="url" placeholder="https://example.com" required><select id="crawlPages"><option value="5">5 trang</option><option value="10" selected>10 trang</option><option value="20">20 trang</option></select><button id="crawlSubmit" class="btn" type="submit">Lập chỉ mục website</button></form>
<div id="crawlStatus" class="mini" style="margin-top:9px">Chưa có tác vụ crawl.</div><div id="crawlJobs"></div>
<div class="index-tools"><input id="indexFilter" type="search" placeholder="Lọc theo tiêu đề hoặc domain"><button id="indexFilterBtn" class="quiet" type="button">Lọc</button></div>
<div id="indexSummary" class="mini" style="margin-top:7px">Chưa tải chỉ mục.</div><div id="indexPages"></div>
<button id="indexMore" class="quiet hidden" type="button" style="width:100%;margin-top:8px">Tải thêm trang</button>
</div></section>
<section class="panel"><div class="panel-head"><strong>✧ AI Overview</strong><span class="mini">Có nguồn tham khảo</span></div><div id="answerPanel" class="panel-body"><div class="ai-card"><h3>Hỏi AI dựa trên kết quả web</h3><p>Tìm một chủ đề, sau đó yêu cầu Nolane tổng hợp các nguồn thành câu trả lời có dẫn chứng.</p></div><button id="answerSideBtn" class="btn" style="width:100%">Tổng hợp câu trả lời</button><div id="answerOutput" class="hidden" style="margin-top:14px"></div></div></section>
<section class="panel"><div class="panel-head"><strong>✦ Nolane Chat</strong><button id="clearChat" class="quiet" style="font-size:11px">Cuộc trò chuyện mới</button></div><div class="chat"><div id="chatLog" class="chat-log"><div class="bubble assistant">Xin chào! Tôi có thể giúp bạn phân tích, giải thích hoặc tiếp tục một câu hỏi. Dùng Tìm kiếm để lấy thông tin web mới nhất, hoặc hỏi trực tiếp tại đây. Bạn cũng có thể đính kèm tệp để AI xử lý ngay trong cuộc trò chuyện.</div></div><form id="chatForm" class="chat-form"><div class="chat-attachments"><label class="chat-attach" for="chatFile">📎 Đính kèm tệp</label><input id="chatFile" type="file" class="hidden" aria-label="Chọn tệp để AI xử lý"><span id="chatFileName" class="mini chat-file-name">Tối đa 20 MB · mọi định dạng được hỗ trợ</span><button id="clearChatFile" class="quiet hidden" type="button" style="font-size:11px">Bỏ tệp</button></div><div class="chat-composer"><textarea id="chatInput" placeholder="Mô tả việc cần làm với tệp hoặc nhắn tin với Nolane..." rows="1" aria-label="Tin nhắn"></textarea><button class="send" title="Gửi">➤</button></div></form></div></section>
</aside></div>
</section></section>
</main>
<footer class="shell footer"><span>© Nolane Search · Personal search workspace</span><span>Thông tin AI cần được đối chiếu với nguồn gốc.</span></footer>
<script>
(function(){
'use strict';
var state={mode:'web',query:'',results:[],history:[],busy:false,eventId:null,indexOffset:0,indexTotal:0,indexLoading:false,indexQuery:''};var toolCatalogState=[];
var $=function(id){return document.getElementById(id)};
var auth=$('auth'),workspace=$('workspace'),query=$('query'),results=$('results'),summary=$('resultSummary');
function text(el,value){el.textContent=value==null?'':String(value)}
function safeUrl(raw){try{var u=new URL(raw);return (u.protocol==='https:'||u.protocol==='http:')?u.href:null}catch(e){return null}}
function authHeaders(){return {'content-type':'application/json','x-nolane-request':'1'}}
function setBusy(on,label){state.busy=on;$('searchBtn').disabled=on;$('searchBtn').textContent=on?'Đang tìm…':'Tìm kiếm';if(on){results.innerHTML='<div class="loading"><span class="spinner"></span><span></span></div>';results.querySelector('.loading span:last-child').textContent=label||'Đang tìm kiếm qua nhiều nguồn…'}}
function showAuth(message){workspace.classList.add('hidden');auth.classList.remove('hidden');$('mediaBtn').classList.add('hidden');$('toolsBtn').classList.add('hidden');if(message){$('authError').classList.remove('hidden');text($('authError'),message)}}
function showWorkspace(){auth.classList.add('hidden');workspace.classList.remove('hidden');$('logoutBtn').classList.remove('hidden');$('mediaBtn').classList.remove('hidden');$('toolsBtn').classList.remove('hidden')}
function saveRecent(q){try{var arr=JSON.parse(localStorage.getItem('nolane.recent')||'[]');arr=[q].concat(arr.filter(function(x){return x!==q})).slice(0,6);localStorage.setItem('nolane.recent',JSON.stringify(arr));renderRecent()}catch(e){}}
function renderRecent(){var box=$('recent');box.replaceChildren();var arr=[];try{arr=JSON.parse(localStorage.getItem('nolane.recent')||'[]')}catch(e){}arr.forEach(function(item){var b=document.createElement('button');text(b,item);b.addEventListener('click',function(){query.value=item;runSearch()});box.appendChild(b)})}
function addResult(item,index,eventId){
 var card=document.createElement('article');card.className='result';
 var meta=document.createElement('div');meta.className='result-url';
 var favicon=document.createElement('span');favicon.className='favicon';text(favicon,(item.domain||'N').slice(0,1).toUpperCase());meta.appendChild(favicon);
 var domain=document.createElement('span');text(domain,item.domain||'');meta.appendChild(domain);card.appendChild(meta);
 var h=document.createElement('h3');var a=document.createElement('a');var url=safeUrl(item.url);a.href=url||'#';a.target='_blank';a.rel='noopener noreferrer';text(a,(index+1)+'. '+(item.title||item.url));h.appendChild(a);card.appendChild(h);
 var p=document.createElement('p');text(p,item.snippet||'Không có mô tả từ nguồn.');card.appendChild(p);
 var foot=document.createElement('div');foot.className='result-meta';var provider=document.createElement('span');provider.className='tag';text(provider,item.provider||'Web');foot.appendChild(provider);if(Array.isArray(item.discoveredBy)){var paths=item.discoveredBy.filter(function(value){return typeof value==='string'&&value.length>0&&value.length<=80}).slice(0,5);if(paths.length>1){var via=document.createElement('span');via.className='tag';text(via,'Công cụ tìm: '+paths.join(' · '));foot.appendChild(via)}}if(item.possibleDuplicateCoverage&&Number.isInteger(item.possibleDuplicateCoverage.groupSize)&&item.possibleDuplicateCoverage.groupSize>=2){var similarity=document.createElement('span');similarity.className='tag';text(similarity,'Có thể trùng nội dung · '+item.possibleDuplicateCoverage.groupSize+' trang');foot.appendChild(similarity)}
 if(item.publishedAt){var date=document.createElement('span');if(!Number.isNaN(new Date(item.publishedAt).getTime())){text(date,new Date(item.publishedAt).toLocaleDateString('vi-VN'));foot.appendChild(date)}}
 card.appendChild(foot);
 if(eventId&&url&&url.indexOf('https:')===0){
  var actions=document.createElement('div');actions.className='result-actions';
  [[1,'👍 Hữu ích'],[-1,'👎 Không phù hợp']].forEach(function(entry){
   var button=document.createElement('button');button.type='button';button.className='feedback-btn';text(button,entry[1]);
   button.addEventListener('click',async function(){
    button.disabled=true;
    try{await api('/api/feedback',{method:'POST',headers:authHeaders(),body:JSON.stringify({eventId:eventId,url:url,rating:entry[0]})});text(button,entry[0]===1?'✓ Đã ghi nhận':'✓ Đã ghi nhận')}
    catch(error){text(button,'Thử lại');button.disabled=false}
   });
   actions.appendChild(button);
  });
  card.appendChild(actions);
 }
 return card;
}
function renderResults(data,eventId){results.replaceChildren();if(!data.length){var empty=document.createElement('div');empty.className='empty';var strong=document.createElement('strong');text(strong,'Không tìm thấy kết quả');empty.appendChild(strong);empty.appendChild(document.createTextNode('Thử cụm từ khác, đổi danh mục hoặc bỏ bớt bộ lọc.'));results.appendChild(empty);return}data.forEach(function(item,i){results.appendChild(addResult(item,i,eventId))})}
async function api(path,options){var response=await fetch(path,Object.assign({credentials:'same-origin',cache:'no-store'},options||{}));var data=await response.json().catch(function(){return {error:'Phản hồi máy chủ không hợp lệ'}});if(response.status===401){showAuth('Phiên đăng nhập đã hết hạn. Hãy gửi /web cho bot để tạo liên kết mới.');throw new Error(data.error||'Unauthorized')}if(!response.ok)throw new Error(data.error||('Lỗi HTTP '+response.status));return data}
async function runSearch(){var q=query.value.trim();if(q.length<2){query.focus();return}state.query=q;saveRecent(q);setBusy(true);summary.textContent='Đang tìm kiếm';try{var params=new URLSearchParams({q:q,mode:state.mode});var data=await api('/api/search?'+params.toString());state.results=data.results||[];state.eventId=data.eventId||null;renderResults(state.results,state.eventId);text(summary,(data.results||[]).length+' kết quả · '+(data.meta&&data.meta.elapsedMs||0)+' ms');$('answerBtn').classList.remove('hidden');$('answerSideBtn').disabled=false;$('searchContent').scrollIntoView({behavior:'smooth',block:'start'})}catch(e){results.innerHTML='<div class="notice"></div>';text(results.firstChild,e.message);text(summary,'Không thể hoàn tất tìm kiếm')}finally{state.busy=false;$('searchBtn').disabled=false;$('searchBtn').textContent='Tìm kiếm'}}
function renderSources(list){var box=document.createElement('div');box.className='sources';(list||[]).forEach(function(item,i){var u=safeUrl(item.url);if(!u)return;var a=document.createElement('a');a.className='source';a.href=u;a.target='_blank';a.rel='noopener noreferrer';text(a,'['+(i+1)+'] '+(item.title||item.domain));box.appendChild(a)});return box}
async function answer(){if(!state.query){query.focus();return}var output=$('answerOutput');output.classList.remove('hidden');output.replaceChildren();var loading=document.createElement('div');loading.className='loading';loading.innerHTML='<span class="spinner"></span><span>Đang tổng hợp và đối chiếu các nguồn…</span>';output.appendChild(loading);$('answerBtn').disabled=true;$('answerSideBtn').disabled=true;try{var data=await api('/api/ask',{method:'POST',headers:authHeaders(),body:JSON.stringify({q:state.query,mode:state.mode})});output.replaceChildren();var p=document.createElement('div');p.className='answer';text(p,data.answer);output.appendChild(p);output.appendChild(renderSources(data.sources||[]));var note=document.createElement('div');note.className='mini';var details=['AI: '+(data.provider||'AI Router')+' · '+(data.model||'')];if(data.cached)details.push('Đã dùng cache');if(typeof data.latencyMs==='number')details.push(data.latencyMs+' ms');if(typeof data.inputTokens==='number'&&typeof data.outputTokens==='number')details.push(data.inputTokens+' in / '+data.outputTokens+' out tokens');if(typeof data.estimatedCostUsd==='number')details.push('USD '+data.estimatedCostUsd.toFixed(6));text(note,details.join(' · '));output.appendChild(note)}catch(e){output.replaceChildren();var n=document.createElement('div');n.className='notice';text(n,e.message);output.appendChild(n)}finally{$('answerBtn').disabled=false;$('answerSideBtn').disabled=false}}
function addBubble(role,message){var b=document.createElement('div');b.className='bubble '+role;text(b,message);$('chatLog').appendChild(b);$('chatLog').scrollTop=$('chatLog').scrollHeight}
function loadChat(){try{state.history=JSON.parse(localStorage.getItem('nolane.chat')||'[]').slice(-12);state.history.forEach(function(m){addBubble(m.role==='user'?'user':'assistant',m.content)})}catch(e){state.history=[]}}
async function sendChat(){var input=$('chatInput');var message=input.value.trim();var fileInput=$('chatFile');var file=fileInput.files&&fileInput.files[0];if(file&&file.size>20*1024*1024){addBubble('assistant','Tệp vượt giới hạn 20 MB của luồng xử lý hiện tại.');return}if(!message){if(file)addBubble('assistant','Hãy mô tả AI cần làm gì với tệp trước khi gửi.');input.focus();return}input.value='';state.history.push({role:'user',content:message+(file?' · Tệp: '+file.name:'' )});state.history=state.history.slice(-12);addBubble('user',message+(file?'\n📎 '+file.name:''));var pending=document.createElement('div');pending.className='bubble assistant';pending.textContent=file?'Đang tải tệp lên và lập kế hoạch xử lý…':'Đang suy nghĩ…';$('chatLog').appendChild(pending);var btn=$('chatForm').querySelector('.send');btn.disabled=true;try{var data;var answer;if(file){var form=new FormData();form.set('prompt',message);form.set('file',file,file.name);data=await api('/api/ai/upload',{method:'POST',headers:{'x-nolane-request':'1'},body:form});answer='Đã nhận tệp '+data.fileName+'.\nQuy trình: '+(data.pipeline||[]).join(' → ')+'\nJob: '+data.jobId+'\n'+(data.selectedByAi?'AI đã tự chọn pipeline phù hợp.':'Đã dùng phương án dự phòng an toàn.')+'\nKết quả sẽ được gửi về chat Telegram riêng và xuất hiện trong Tool Center khi hoàn tất.';fileInput.value='';text($('chatFileName'),'Tối đa 20 MB · mọi định dạng được hỗ trợ');$('clearChatFile').classList.add('hidden');}else{data=await api('/api/chat',{method:'POST',headers:authHeaders(),body:JSON.stringify({message:message,history:state.history.slice(0,-1).filter(function(m){return !m.content.includes(' · Tệp: ')}),task:'chat'})});answer=data.answer;}pending.remove();state.history.push({role:'assistant',content:answer});state.history=state.history.slice(-12);addBubble('assistant',answer);var metaParts=[];if(file){metaParts.push('AI File · '+(data.selectedByAi?'AI planner':'fallback'))}else if(Array.isArray(data.toolsUsed)&&data.toolsUsed.length)metaParts.push('Tools: '+data.toolsUsed.join(', '));if(typeof data.inputTokens==='number'&&typeof data.outputTokens==='number')metaParts.push(data.inputTokens+' in / '+data.outputTokens+' out tokens');if(typeof data.latencyMs==='number')metaParts.push(data.latencyMs+' ms');if(typeof data.estimatedCostUsd==='number')metaParts.push('USD '+data.estimatedCostUsd.toFixed(6));if(metaParts.length){var usage=document.createElement('div');usage.className='mini';text(usage,metaParts.join(' · '));$('chatLog').appendChild(usage)}localStorage.setItem('nolane.chat',JSON.stringify(state.history));if(file&&typeof refreshToolJobs==='function')refreshToolJobs();}catch(e){pending.remove();addBubble('assistant','Không thể hoàn tất yêu cầu: '+e.message)}finally{btn.disabled=false;input.focus()}}

async function refreshCrawls(){
 try{
  var data=await api('/api/crawls');var box=$('crawlJobs');box.replaceChildren();
  var jobs=data.jobs||[];
  if(!jobs.length){text($('crawlStatus'),'Chưa có tác vụ crawl.');return}
  text($('crawlStatus'),jobs.length+' tác vụ gần đây');
  jobs.forEach(function(job){
   var card=document.createElement('div');card.className='crawl-job';
   var title=document.createElement('strong');text(title,(job.status||'unknown').toString().toUpperCase()+' · '+(job.indexed||0)+'/'+(job.maxPages||0)+' trang');card.appendChild(title);
   var url=document.createElement('span');url.className='mini';text(url,job.seedUrl||'');card.appendChild(url);
   if(job.lastError){var error=document.createElement('span');error.className='mini';text(error,job.lastError);card.appendChild(error)}
   box.appendChild(card);
  });
 }catch(error){text($('crawlStatus'),error.message)}
}

async function removeIndexed(target){
 var isDomain=!!target.domain;
 var label=isDomain?target.domain:target.url;
 var warning=isDomain
  ?'Gỡ toàn bộ trang đã lưu của '+label+'? Các watch khớp URL đã lưu cũng sẽ bị tắt.'
  :'Gỡ trang này khỏi chỉ mục? Watch khớp URL này cũng sẽ bị tắt.';
 if(!window.confirm(warning))return;
 try{
  var payload=isDomain?{domain:target.domain}:{url:target.url};
  var data=await api('/api/index/delete',{method:'POST',headers:authHeaders(),body:JSON.stringify(payload)});
  text($('indexSummary'),'Đã gỡ '+data.pagesDeleted+' trang · Đã tắt '+data.watchesDisabled+' watch.');
  state.indexOffset=0;
  await refreshIndex(true);
  await refreshCrawls();
 }catch(error){text($('indexSummary'),error.message)}
}

async function refreshIndex(reset){
 if(state.indexLoading)return;
 if(reset){state.indexOffset=0;state.indexQuery=$('indexFilter').value.trim();$('indexPages').replaceChildren()}
 state.indexLoading=true;
 $('indexMore').disabled=true;
 try{
  var params=new URLSearchParams({limit:'20',offset:String(state.indexOffset)});
  if(state.indexQuery)params.set('q',state.indexQuery);
  var data=await api('/api/index?'+params.toString());
  var pages=data.pages||[];
  state.indexTotal=Number(data.total)||0;
  pages.forEach(function(page){
   var card=document.createElement('div');card.className='index-entry';
   var link=document.createElement('a');var href=safeUrl(page.url);
   if(href){link.href=href;link.target='_blank';link.rel='noopener noreferrer'}
   text(link,page.title||page.url);card.appendChild(link);
   var meta=document.createElement('span');meta.className='mini';
   text(meta,(page.domain||'')+' · '+(page.contentChars||0).toLocaleString()+' ký tự');card.appendChild(meta);
   var actions=document.createElement('div');actions.className='index-entry-actions';
   var removePage=document.createElement('button');removePage.className='feedback-btn';removePage.type='button';text(removePage,'Gỡ trang');
   removePage.addEventListener('click',function(){removeIndexed({url:page.url})});actions.appendChild(removePage);
   var removeSite=document.createElement('button');removeSite.className='feedback-btn';removeSite.type='button';text(removeSite,'Gỡ domain');
   removeSite.addEventListener('click',function(){removeIndexed({domain:page.domain})});actions.appendChild(removeSite);
   card.appendChild(actions);$('indexPages').appendChild(card);
  });
  if(!state.indexTotal)text($('indexSummary'),state.indexQuery?'Không có trang phù hợp với bộ lọc.':'Chưa có nội dung trong chỉ mục.');
  else text($('indexSummary'),state.indexQuery?state.indexTotal+' trang phù hợp':'Đang lưu '+state.indexTotal+' trang');
  state.indexOffset+=pages.length;
  $('indexMore').classList.toggle('hidden',state.indexOffset>=state.indexTotal||pages.length===0);
 }catch(error){text($('indexSummary'),error.message)}
 finally{state.indexLoading=false;$('indexMore').disabled=false}
}
function normalizeToolSearch(value){return String(value||'').toLocaleLowerCase('vi').normalize('NFD').replace(/[\u0300-\u036f]/g,'')}
function renderToolCatalog(){
 var box=$('toolCatalog');box.replaceChildren();
 var query=normalizeToolSearch($('toolFilter').value.trim());
 var category=$('toolCategoryFilter').value;
 var labels={image:'Hình ảnh & OCR',document:'PDF & Office','audio-video':'Âm thanh & Video',data:'Dữ liệu',developer:'Lập trình & văn bản',repository:'Mã nguồn & Repository',utility:'Tiện ích'};
 var filtered=toolCatalogState.filter(function(tool){
  if(category!=='all'&&tool.category!==category)return false;
  var haystack=normalizeToolSearch([tool.id,tool.name,tool.description,tool.output,(tool.accepts||[]).join(' '),labels[tool.category]||tool.category].join(' '));
  return !query||query.split(/\s+/).every(function(term){return haystack.includes(term)});
 });
 text($('toolCatalogMeta'),filtered.length+' / '+toolCatalogState.length+' công cụ'+(category!=='all'?' · '+(labels[category]||category):''));
 if(!filtered.length){var empty=document.createElement('div');empty.className='empty';var title=document.createElement('strong');text(title,'Không có công cụ phù hợp');empty.appendChild(title);empty.appendChild(document.createTextNode('Thử từ khóa khác hoặc chọn Tất cả danh mục.'));box.appendChild(empty);return}
 filtered.forEach(function(tool){
  var card=document.createElement('article');card.className='tool-card';
  var title=document.createElement('h3');text(title,tool.name);card.appendChild(title);
  var categoryBadge=document.createElement('span');categoryBadge.className='tool-badge';text(categoryBadge,labels[tool.category]||tool.category);card.appendChild(categoryBadge);
  var badge=document.createElement('span');badge.className='mini';text(badge,tool.ready?'READY':'SETUP NEEDED');card.appendChild(badge);
  var desc=document.createElement('p');desc.textContent=tool.description;card.appendChild(desc);
  var input=document.createElement('span');input.className='mini';text(input,'Nhận: '+(tool.accepts||[]).join(', '));card.appendChild(input);
  var output=document.createElement('span');output.className='mini';text(output,'Trả về: '+(tool.output||'Kết quả'));card.appendChild(output);
  var button=document.createElement('button');button.type='button';button.className='feedback-btn';button.disabled=!tool.ready;
  text(button,tool.ready?'Sao chép /tool '+tool.id:'Cần GITHUB_ACTIONS_TOKEN');
  button.addEventListener('click',async function(){
   try{await navigator.clipboard.writeText('/tool '+tool.id);text(button,'Đã sao chép')}
   catch(e){window.prompt('Sao chép lệnh này vào Telegram','/tool '+tool.id)}
  });
  card.appendChild(button);box.appendChild(card);
 });
}
async function loadTools(){
 try{
  var data=await api('/api/tools/catalog');toolCatalogState=data.tools||[];renderToolCatalog();
 }catch(error){var box=$('toolCatalog');box.replaceChildren();var notice=document.createElement('div');notice.className='notice';text(notice,error.message);box.appendChild(notice);text($('toolCatalogMeta'),'Không thể tải catalog')}
}
$('toolFilter').addEventListener('input',renderToolCatalog);
$('toolCategoryFilter').addEventListener('change',renderToolCatalog);

async function refreshToolJobs(){
 try{
  var data=await api('/api/tools/jobs');var box=$('toolJobs');box.replaceChildren();var jobs=data.jobs||[];
  if(!jobs.length){text(box,'Chưa có tác vụ công cụ nào.');return}
  jobs.forEach(function(job){
   var card=document.createElement('div');card.className='tool-job';
   var title=document.createElement('strong');text(title,(job.toolId||'tool')+' · '+(job.status||'unknown').toUpperCase());card.appendChild(title);
   var file=document.createElement('span');file.className='mini';text(file,job.fileName||'');card.appendChild(file);
   var id=document.createElement('span');id.className='mini';text(id,job.id||'');card.appendChild(id);
   if(job.progress){
    var progress=document.createElement('span');progress.className='mini';
    var current=(job.progress.currentToolIds||[]).join(', ');
    text(progress,'Tiến trình: '+(job.progress.completed||0)+'/'+(job.progress.total||0)+(current?' · Đang chạy: '+current:''));
    card.appendChild(progress);
   }
   if(Array.isArray(job.trace)&&job.trace.length){
    var trace=document.createElement('span');trace.className='mini';
    text(trace,'Trace: '+job.trace.length+'/'+((job.pipeline||[]).length||1)+' bước');
    card.appendChild(trace);
   }
   if(job.resultSummary){var summary=document.createElement('p');summary.textContent=job.resultSummary;card.appendChild(summary)}
   if(job.error){var error=document.createElement('p');error.className='mini';error.textContent=job.error;card.appendChild(error)}
   box.appendChild(card);
  });
 }catch(error){text($('toolJobs'),error.message)}
}
function showTools(show){
 $('toolsHub').classList.toggle('hidden',!show);
 document.querySelector('.hero').classList.toggle('hidden',show);
 $('searchContent').classList.toggle('hidden',show);
 text($('toolsBtn'),show?'← Tìm kiếm':'🧰 Tools');
 if(show){loadTools();refreshToolJobs();$('toolsHub').scrollIntoView({behavior:'smooth',block:'start'})}
}
$('mediaBtn').addEventListener('click',function(){location.href='/media'});
$('toolsBtn').addEventListener('click',function(){showTools($('toolsHub').classList.contains('hidden'))});
$('refreshToolJobs').addEventListener('click',refreshToolJobs);

$('crawlForm').addEventListener('submit',async function(e){
 e.preventDefault();var button=$('crawlSubmit');var url=$('crawlUrl').value.trim();var maxPages=Number($('crawlPages').value);
 if(!safeUrl(url)){text($('crawlStatus'),'Chỉ hỗ trợ URL HTTPS public hợp lệ.');return}
 button.disabled=true;button.textContent='Đang xếp hàng…';
 try{
  var data=await api('/api/crawl',{method:'POST',headers:authHeaders(),body:JSON.stringify({url:url,maxPages:maxPages})});
  text($('crawlStatus'),'Đã tạo job '+data.job.id+'. Đang chờ Worker xử lý.');
  await refreshCrawls();
 }catch(error){text($('crawlStatus'),error.message)}
 finally{button.disabled=false;button.textContent='Lập chỉ mục website'}
});
$('refreshCrawls').addEventListener('click',function(){refreshCrawls();refreshIndex(true)});
$('indexFilterBtn').addEventListener('click',function(){refreshIndex(true)});
$('indexFilter').addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();refreshIndex(true)}});
$('indexMore').addEventListener('click',function(){refreshIndex(false)});

$('searchForm').addEventListener('submit',function(e){e.preventDefault();runSearch()});
$('modeChips').addEventListener('click',function(e){var b=e.target.closest('[data-mode]');if(!b)return;state.mode=b.dataset.mode;document.querySelectorAll('.chip').forEach(function(x){x.classList.toggle('active',x===b)});if(query.value.trim())runSearch()});
$('answerBtn').addEventListener('click',answer);$('answerSideBtn').addEventListener('click',answer);
$('chatForm').addEventListener('submit',function(e){e.preventDefault();sendChat()});
 $('chatFile').addEventListener('change',function(){var file=this.files&&this.files[0];text($('chatFileName'),file?file.name+' · '+(file.size/1048576).toFixed(2)+' MB':'Tối đa 20 MB · mọi định dạng được hỗ trợ');$('clearChatFile').classList.toggle('hidden',!file)});
 $('clearChatFile').addEventListener('click',function(){$('chatFile').value='';text($('chatFileName'),'Tối đa 20 MB · mọi định dạng được hỗ trợ');this.classList.add('hidden')});
$('clearChat').addEventListener('click',function(){state.history=[];localStorage.removeItem('nolane.chat');$('chatLog').replaceChildren();addBubble('assistant','Cuộc trò chuyện mới đã bắt đầu. Bạn muốn tìm hiểu điều gì?')});
$('logoutBtn').addEventListener('click',async function(){try{await api('/api/auth/logout',{method:'POST',headers:authHeaders(),body:'{}'})}catch(e){}localStorage.removeItem('nolane.chat');location.reload()});
$('themeBtn').addEventListener('click',function(){var dark=document.documentElement.dataset.theme!=='dark';document.documentElement.dataset.theme=dark?'dark':'light';try{localStorage.setItem('nolane.theme',dark?'dark':'light')}catch(e){}});try{document.documentElement.dataset.theme=localStorage.getItem('nolane.theme')||'light'}catch(e){}
document.addEventListener('keydown',function(e){if(e.key==='/'&&document.activeElement!==query&&document.activeElement!==$('chatInput')){e.preventDefault();query.focus()}});
renderRecent();loadChat();
(async function boot(){var params=new URLSearchParams(location.search);var ticket=params.get('ticket');if(ticket){try{await api('/api/auth/exchange',{method:'POST',headers:authHeaders(),body:JSON.stringify({ticket:ticket})});history.replaceState({},'',location.pathname);showWorkspace();refreshCrawls();refreshIndex(true)}catch(e){showAuth(e.message);return}}else{try{await api('/api/auth/me');showWorkspace();refreshCrawls();refreshIndex(true)}catch(e){showAuth()}}})();
})();
</script></body></html>`;
export function webAppResponse(): Response {
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
