const HTML = String.raw`<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#101827">
<meta name="robots" content="noindex,nofollow">
<title>Nolane · Telegram Workspace</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
:root{
 color-scheme:light dark;
 --bg:var(--tg-theme-bg-color,#0b1220);
 --surface:var(--tg-theme-secondary-bg-color,#121d30);
 --panel:color-mix(in srgb,var(--surface) 90%,var(--tg-theme-button-color,#6f8fff) 10%);
 --panel-strong:color-mix(in srgb,var(--surface) 78%,var(--tg-theme-button-color,#6f8fff) 22%);
 --ink:var(--tg-theme-text-color,#edf3ff);
 --muted:var(--tg-theme-hint-color,#91a0b9);
 --line:color-mix(in srgb,var(--ink) 11%,transparent);
 --accent:var(--tg-theme-button-color,#6e8cff);
 --accent-text:var(--tg-theme-button-text-color,#fff);
 --link:var(--tg-theme-link-color,#8aa7ff);
 --success:#31c48d;
 --danger:var(--tg-theme-destructive-text-color,#fa6b78);
 --radius:20px;
 --shadow:0 18px 48px rgba(0,0,0,.16);
}
*{box-sizing:border-box}
html{min-height:100%;background:var(--bg);scroll-behavior:smooth}
body{margin:0;min-height:100dvh;background:radial-gradient(ellipse at 8% -8%,color-mix(in srgb,var(--accent) 19%,transparent),transparent 34rem),radial-gradient(ellipse at 100% 20%,rgba(92,78,190,.10),transparent 27rem),var(--bg);color:var(--ink);font:14px/1.5 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}
button,input,textarea,select{font:inherit}
button{cursor:pointer}
button:disabled{opacity:.55;cursor:wait}
a{color:inherit}
.hidden{display:none!important}
#app{min-height:100dvh;padding-bottom:calc(92px + var(--tg-content-safe-area-inset-bottom,env(safe-area-inset-bottom,0px)))}
.shell{width:min(100%,760px);margin:0 auto;padding:calc(12px + var(--tg-safe-area-inset-top,env(safe-area-inset-top,0px))) 18px 24px}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:4px 1px 19px}
.brand{display:flex;align-items:center;gap:10px;min-width:0}
.logo{width:38px;height:38px;flex:0 0 38px;display:grid;place-items:center;border-radius:13px;background:linear-gradient(140deg,#4974f7,#886cff);color:#fff;font-size:18px;font-weight:900;box-shadow:0 8px 22px rgba(79,111,239,.28)}
.brand-name{font-weight:850;font-size:15px;letter-spacing:.075em}
.brand-sub{font-size:10px;color:var(--muted);letter-spacing:.11em;text-transform:uppercase;margin-top:1px}
.status-pill{display:flex;align-items:center;gap:7px;border:1px solid var(--line);border-radius:999px;padding:7px 10px;background:color-mix(in srgb,var(--surface) 85%,transparent);font-size:10px;font-weight:750;letter-spacing:.07em;color:var(--muted);white-space:nowrap}
.status-dot{width:7px;height:7px;border-radius:50%;background:#8795a8;box-shadow:0 0 0 3px color-mix(in srgb,#8795a8 16%,transparent)}
.status-pill.ready{color:var(--success)}
.status-pill.ready .status-dot{background:var(--success);box-shadow:0 0 0 3px color-mix(in srgb,var(--success) 17%,transparent)}
.hero{position:relative;overflow:hidden;border:1px solid color-mix(in srgb,var(--accent) 30%,var(--line));border-radius:25px;padding:23px 20px 19px;background:linear-gradient(135deg,color-mix(in srgb,var(--accent) 18%,var(--surface)),var(--panel) 58%,color-mix(in srgb,#886cff 11%,var(--surface)));box-shadow:var(--shadow)}
.hero:after{content:"";position:absolute;width:210px;height:210px;border-radius:50%;right:-85px;top:-110px;background:radial-gradient(circle,color-mix(in srgb,var(--accent) 30%,transparent),transparent 68%);pointer-events:none}
.eyebrow{display:inline-flex;align-items:center;gap:7px;color:var(--link);font-size:10px;font-weight:850;letter-spacing:.15em;text-transform:uppercase}
.eyebrow .spark{font-size:13px}
.hero h1{position:relative;z-index:1;font-size:clamp(27px,7vw,38px);line-height:1.07;letter-spacing:-.055em;margin:13px 0 8px;max-width:510px}
.hero p{position:relative;z-index:1;color:var(--muted);font-size:13px;line-height:1.55;margin:0;max-width:480px}
.hero-bottom{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:17px;position:relative;z-index:1}
.hero-tag{border:1px solid var(--line);border-radius:999px;background:color-mix(in srgb,var(--surface) 65%,transparent);padding:6px 9px;font-size:10px;color:var(--muted);font-weight:650}
.section{margin-top:24px}
.section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin:0 1px 11px}
.section-title{font-size:14px;font-weight:850;letter-spacing:-.015em}
.section-note{color:var(--muted);font-size:11px;margin-top:2px}
.text-link{border:0;background:transparent;color:var(--link);padding:5px 0;font-size:11px;font-weight:750}
.search-card{border:1px solid var(--line);border-radius:19px;background:var(--panel);padding:13px;box-shadow:0 10px 28px rgba(0,0,0,.08)}
.search-field{display:flex;align-items:center;gap:10px;background:color-mix(in srgb,var(--bg) 68%,var(--surface));border:1px solid var(--line);border-radius:14px;padding:0 11px}
.search-symbol{font-size:19px;color:var(--muted)}
.search-field input{width:100%;min-width:0;background:transparent;border:0;outline:0;padding:14px 0;color:var(--ink);font-size:14px}
.search-field input::placeholder{color:var(--muted)}
.search-submit{width:100%;margin-top:10px;border:0;border-radius:13px;padding:12px 14px;background:linear-gradient(110deg,var(--accent),color-mix(in srgb,var(--accent) 66%,#8a70ff));color:var(--accent-text);font-size:13px;font-weight:850;box-shadow:0 8px 18px color-mix(in srgb,var(--accent) 25%,transparent)}
.mode-strip{display:flex;gap:7px;overflow:auto;padding:11px 1px 2px;scrollbar-width:none}
.mode-strip::-webkit-scrollbar{display:none}
.mode-chip{flex:0 0 auto;border:1px solid var(--line);background:color-mix(in srgb,var(--surface) 70%,transparent);color:var(--muted);border-radius:999px;padding:7px 11px;font-size:11px;font-weight:700}
.mode-chip.active{background:color-mix(in srgb,var(--accent) 18%,var(--surface));border-color:color-mix(in srgb,var(--accent) 45%,var(--line));color:var(--link)}
.quick-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.quick-card{position:relative;display:flex;gap:12px;align-items:flex-start;text-align:left;width:100%;min-height:100px;padding:14px;border:1px solid var(--line);border-radius:18px;background:var(--panel);color:var(--ink);transition:transform .16s,border-color .16s,background .16s}
.quick-card:active{transform:scale(.985)}
.quick-card:hover{border-color:color-mix(in srgb,var(--accent) 38%,var(--line))}
.quick-icon{width:38px;height:38px;flex:0 0 38px;display:grid;place-items:center;border-radius:13px;background:color-mix(in srgb,var(--accent) 15%,var(--surface));font-size:18px}
.quick-title{font-size:12px;font-weight:850;display:block;line-height:1.35;margin:1px 0 4px}
.quick-desc{display:block;color:var(--muted);font-size:10px;line-height:1.45}
.quick-arrow{position:absolute;right:11px;bottom:9px;color:var(--muted);font-size:13px}
.metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.metric{border:1px solid var(--line);border-radius:15px;background:color-mix(in srgb,var(--surface) 78%,transparent);padding:11px 12px;min-width:0}
.metric strong{display:block;font-size:18px;letter-spacing:-.04em}
.metric span{display:block;color:var(--muted);font-size:10px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.view{display:none;animation:enter .18s ease}
.view.active{display:block}
@keyframes enter{from{opacity:.5;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
.view-head{padding:8px 1px 15px}
.view-kicker{font-size:10px;letter-spacing:.14em;text-transform:uppercase;font-weight:850;color:var(--link)}
.view-head h1{font-size:26px;letter-spacing:-.045em;line-height:1.15;margin:6px 0}
.view-head p{color:var(--muted);font-size:12px;margin:0}
.results-meta{display:flex;align-items:center;justify-content:space-between;gap:10px;color:var(--muted);font-size:11px;padding:14px 2px 9px}
.result-list{display:grid;gap:9px}
.result-card{border:1px solid var(--line);border-radius:16px;background:var(--panel);padding:13px 14px}
.result-origin{display:flex;align-items:center;gap:7px;color:var(--muted);font-size:10px;margin-bottom:6px}
.result-favicon{width:20px;height:20px;border-radius:7px;background:var(--panel-strong);display:grid;place-items:center;font-size:10px;font-weight:850;color:var(--link)}
.result-card h3{font-size:13px;line-height:1.4;margin:0 0 6px;font-weight:800;letter-spacing:-.01em}
.result-card h3 a{text-decoration:none;color:var(--link)}
.result-card p{font-size:11px;line-height:1.6;color:var(--muted);margin:0}
.result-actions{display:flex;align-items:center;gap:8px;margin-top:10px}
.mini-action{border:1px solid var(--line);background:transparent;color:var(--muted);border-radius:9px;padding:6px 8px;font-size:10px;font-weight:750}
.answer-card{border:1px solid color-mix(in srgb,var(--accent) 35%,var(--line));border-radius:17px;background:color-mix(in srgb,var(--accent) 8%,var(--surface));padding:14px;margin-top:12px}
.answer-card h3{font-size:12px;margin:0 0 7px}
.answer-copy{white-space:pre-wrap;font-size:12px;line-height:1.7;color:var(--ink)}
.source-list{display:grid;gap:6px;margin-top:11px}
.source-link{border:1px solid var(--line);border-radius:9px;padding:8px 9px;color:var(--link);text-decoration:none;font-size:10px;overflow-wrap:anywhere}
.empty-state{border:1px dashed var(--line);border-radius:16px;padding:20px;text-align:center;color:var(--muted);font-size:12px}
.empty-state strong{display:block;color:var(--ink);font-size:13px;margin-bottom:4px}
.status-message{border:1px solid var(--line);border-radius:13px;padding:10px 12px;margin:9px 0;background:var(--panel);color:var(--muted);font-size:11px}
.status-message.error{color:var(--danger);border-color:color-mix(in srgb,var(--danger) 35%,var(--line))}
.chat-log{display:flex;flex-direction:column;gap:9px;max-height:min(48dvh,460px);overflow:auto;padding:3px 1px 12px}
.bubble{max-width:92%;padding:11px 12px;border-radius:15px;font-size:12px;line-height:1.6;white-space:pre-wrap;overflow-wrap:anywhere}
.bubble.user{align-self:flex-end;background:var(--accent);color:var(--accent-text);border-bottom-right-radius:5px}
.bubble.assistant{align-self:flex-start;background:var(--panel);border:1px solid var(--line);color:var(--ink);border-bottom-left-radius:5px}.bubble.pending{color:var(--muted)}.bubble.pending:after{content:' ···';display:inline-block;animation:pulse 1.1s ease-in-out infinite}@keyframes pulse{50%{opacity:.28}}
.chat-composer{border:1px solid var(--line);border-radius:17px;background:var(--panel);padding:10px;margin-top:9px}
.chat-composer textarea{display:block;width:100%;min-height:64px;max-height:140px;resize:vertical;border:0;outline:0;background:transparent;color:var(--ink);font-size:12px}
.chat-composer textarea::placeholder{color:var(--muted)}
.composer-bottom{display:flex;align-items:center;justify-content:space-between;gap:8px;border-top:1px solid var(--line);padding-top:8px}
.attach-btn{border:1px solid var(--line);background:transparent;color:var(--muted);border-radius:10px;padding:7px 9px;font-size:10px;font-weight:750}
.send-btn{border:0;border-radius:11px;background:var(--accent);color:var(--accent-text);padding:8px 14px;font-size:11px;font-weight:850}
.file-name{font-size:10px;color:var(--muted);min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.filter-row{display:flex;gap:8px;margin:8px 0 12px}
.filter-row input,.filter-row select,.field{width:100%;min-width:0;border:1px solid var(--line);border-radius:12px;padding:11px 12px;background:var(--panel);color:var(--ink);outline:0;font-size:12px}
.tool-categories{display:flex;gap:7px;overflow:auto;padding:2px 0 10px;scrollbar-width:none}
.tool-category{flex:0 0 auto;border:1px solid var(--line);border-radius:999px;padding:7px 10px;background:var(--panel);color:var(--muted);font-size:10px;font-weight:750}
.tool-category.active{background:color-mix(in srgb,var(--accent) 17%,var(--surface));border-color:color-mix(in srgb,var(--accent) 42%,var(--line));color:var(--link)}
.tool-list{display:grid;gap:8px}
.tool-card{border:1px solid var(--line);border-radius:15px;background:var(--panel);padding:12px}
.tool-top{display:flex;align-items:flex-start;justify-content:space-between;gap:9px}
.tool-card h3{font-size:12px;margin:0 0 4px;line-height:1.4}
.tool-badge{flex:0 0 auto;border-radius:999px;padding:4px 7px;background:color-mix(in srgb,var(--success) 14%,var(--surface));color:var(--success);font-size:9px;font-weight:850}
.tool-badge.off{background:color-mix(in srgb,var(--danger) 12%,var(--surface));color:var(--danger)}
.tool-card p{font-size:10px;line-height:1.55;color:var(--muted);margin:6px 0}
.tool-meta{font-size:9px;color:var(--muted);line-height:1.5}
.tool-actions{display:flex;gap:7px;margin-top:10px}
.tool-actions button{flex:1;border:1px solid var(--line);border-radius:9px;padding:7px 8px;background:transparent;color:var(--link);font-size:10px;font-weight:800}
.tool-actions button.primary{background:var(--accent);color:var(--accent-text);border-color:transparent}
.job-list,.index-list{display:grid;gap:8px}
.job-card,.index-card{border:1px solid var(--line);border-radius:14px;padding:11px 12px;background:var(--panel)}
.job-card strong,.index-card strong{display:block;font-size:11px;line-height:1.4}
.job-card span,.index-card span{display:block;color:var(--muted);font-size:10px;margin-top:4px;overflow-wrap:anywhere}
.job-status{display:inline-block!important;width:max-content;max-width:100%;border-radius:999px;padding:3px 7px;background:var(--panel-strong);color:var(--muted)!important;font-weight:850;font-size:9px!important}
.library-form{display:grid;grid-template-columns:minmax(0,1fr) 86px;gap:8px}
.library-form button{border:0;border-radius:11px;background:var(--accent);color:var(--accent-text);font-weight:850;font-size:11px}
.primary-btn{border:0;border-radius:12px;padding:11px 14px;background:var(--accent);color:var(--accent-text);font-size:11px;font-weight:850}
.secondary-btn{border:1px solid var(--line);border-radius:12px;padding:10px 13px;background:transparent;color:var(--ink);font-size:11px;font-weight:750}
.bottom-nav{position:fixed;z-index:20;left:0;right:0;bottom:0;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:3px;padding:8px 10px calc(8px + var(--tg-content-safe-area-inset-bottom,env(safe-area-inset-bottom,0px)));border-top:1px solid var(--line);background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(18px)}
.nav-item{display:flex;min-width:0;flex-direction:column;align-items:center;gap:3px;border:0;border-radius:12px;padding:5px 2px;background:transparent;color:var(--muted);font-size:9px;font-weight:750}
.nav-icon{font-size:18px;line-height:1.15}
.nav-item.active{color:var(--link);background:color-mix(in srgb,var(--accent) 13%,transparent)}
.nav-item.active .nav-icon{filter:drop-shadow(0 2px 8px color-mix(in srgb,var(--accent) 32%,transparent))}
.toast{position:fixed;z-index:40;left:50%;bottom:calc(83px + var(--tg-content-safe-area-inset-bottom,env(safe-area-inset-bottom,0px)));transform:translate(-50%,10px);opacity:0;pointer-events:none;max-width:calc(100vw - 36px);background:var(--ink);color:var(--bg);border-radius:12px;padding:9px 13px;font-size:11px;font-weight:750;transition:.18s}
.toast.show{opacity:1;transform:translate(-50%,0)}
.auth-card{width:min(100% - 36px,400px);margin:15vh auto 0;border:1px solid var(--line);border-radius:22px;padding:25px;background:var(--panel);text-align:center}
.auth-card h1{font-size:22px;letter-spacing:-.04em}
.auth-card p{color:var(--muted);font-size:12px;line-height:1.6}
@media(min-width:620px){.shell{padding-left:24px;padding-right:24px}.hero{padding:27px}.quick-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.search-submit{width:auto;min-width:140px}.search-field-row{display:grid;grid-template-columns:1fr 140px;gap:10px}.search-field-row .search-submit{margin:0}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{scroll-behavior:auto!important;animation:none!important;transition:none!important}}
</style>
</head>
<body>
<section id="auth" class="auth-card hidden"><div class="logo" style="margin:0 auto">N</div><h1>Không thể mở Workspace</h1><p id="authMessage">Hãy quay lại chat riêng với Nolane, gửi /start và mở lại nút Workspace. Liên kết đăng nhập chỉ sử dụng một lần và sẽ tự hết hạn.</p></section>
<div id="app" class="hidden">
 <main class="shell">
  <header class="topbar">
   <div class="brand"><div class="logo">N</div><div><div class="brand-name">NOLANE <span style="color:var(--link)">SEARCH</span></div><div class="brand-sub">Private intelligence workspace</div></div></div>
   <div id="systemStatus" class="status-pill"><span class="status-dot"></span><span id="systemStatusText">CONNECTING</span></div>
  </header>

  <section class="view active" id="view-home" data-view="home">
   <div class="hero">
    <div class="eyebrow"><span class="spark">✦</span> INTELLIGENCE COMMAND CENTER</div>
    <h1>Mọi công cụ.<br>Một không gian.</h1>
    <p>Tìm kiếm đa nguồn, AI có dẫn chứng và bộ công cụ xử lý chuyên sâu — được sắp xếp để bạn thao tác nhanh hơn.</p>
    <div class="hero-bottom"><span class="hero-tag">◈ Private workspace</span><span class="hero-tag">✧ AI-assisted research</span><span class="hero-tag">⌁ Connected to Telegram</span></div>
   </div>
   <section class="section">
    <div class="section-head"><div><div class="section-title">Bắt đầu nhanh</div><div class="section-note">Một thao tác để vào đúng luồng công việc</div></div></div>
    <form id="homeSearchForm" class="search-card">
     <div class="search-field"><span class="search-symbol">⌕</span><input id="homeQuery" placeholder="Bạn đang muốn tìm hiểu điều gì?" autocomplete="off" aria-label="Tìm kiếm"></div>
     <div class="search-field-row"><div id="homeModes" class="mode-strip">
      <button class="mode-chip active" type="button" data-mode="web">Tất cả</button><button class="mode-chip" type="button" data-mode="research">Nghiên cứu</button><button class="mode-chip" type="button" data-mode="news">Tin tức</button><button class="mode-chip" type="button" data-mode="tech">Công nghệ</button><button class="mode-chip" type="button" data-mode="github">GitHub</button><button class="mode-chip" type="button" data-mode="wiki">Wikipedia</button><button class="mode-chip" type="button" data-mode="local">Website riêng</button>
     </div><button class="search-submit" type="submit">Tìm kiếm ngay <span aria-hidden="true">→</span></button></div>
    </form>
   </section>
   <section class="section">
    <div class="section-head"><div><div class="section-title">Không gian làm việc</div><div class="section-note">Các khu vực được tách rõ theo mục đích</div></div></div>
    <div class="quick-grid">
     <button class="quick-card" type="button" data-open="search"><span class="quick-icon">⌕</span><span><span class="quick-title">Search Studio</span><span class="quick-desc">Web, tin tức, GitHub và nghiên cứu.</span></span><span class="quick-arrow">↗</span></button>
     <button class="quick-card" type="button" data-open="ai"><span class="quick-icon">✦</span><span><span class="quick-title">AI Workspace</span><span class="quick-desc">Chat, phân tích và xử lý tệp.</span></span><span class="quick-arrow">↗</span></button>
     <button class="quick-card" type="button" data-open="tools"><span class="quick-icon">▦</span><span><span class="quick-title">Tool Center</span><span class="quick-desc">Tra cứu processor và theo dõi job.</span></span><span class="quick-arrow">↗</span></button>
     <a class="quick-card" href="/media"><span class="quick-icon">▶</span><span><span class="quick-title">Media Studio</span><span class="quick-desc">Khám phá hình ảnh, video và audio.</span></span><span class="quick-arrow">↗</span></a>
     <button class="quick-card" type="button" data-open="library"><span class="quick-icon">⌑</span><span><span class="quick-title">Personal Index</span><span class="quick-desc">Website đã lập chỉ mục và tác vụ crawl.</span></span><span class="quick-arrow">↗</span></button>
     <button class="quick-card" type="button" data-open="library"><span class="quick-icon">◷</span><span><span class="quick-title">Crawl Jobs</span><span class="quick-desc">Theo dõi trạng thái thu thập website.</span></span><span class="quick-arrow">↗</span></button>
    </div>
   </section>
   <section class="section">
    <div class="section-head"><div><div class="section-title">Hệ thống</div><div class="section-note">Trạng thái trả về từ dịch vụ hiện tại</div></div><button id="refreshSystem" class="text-link" type="button">Làm mới</button></div>
    <div class="metrics">
     <div class="metric"><strong id="metricSearch">—</strong><span>Database</span></div>
     <div class="metric"><strong id="metricTools">—</strong><span>Tools ready</span></div>
     <div class="metric"><strong id="metricJobs">—</strong><span>Recent jobs</span></div>
    </div>
   </section>
   <section class="section" style="padding-bottom:4px"><div id="recentSearches"></div></section>
  </section>

  <section class="view" id="view-search" data-view="search">
   <div class="view-head"><div class="view-kicker">DISCOVERY ENGINE</div><h1>Search Studio</h1><p>Truy vấn một lần, chọn đúng nguồn dữ liệu.</p></div>
   <form id="searchForm" class="search-card">
    <div class="search-field"><span class="search-symbol">⌕</span><input id="query" placeholder="Nhập từ khóa hoặc câu hỏi..." autocomplete="off" aria-label="Từ khóa"></div>
    <div id="searchModes" class="mode-strip">
     <button class="mode-chip active" type="button" data-mode="web">Tất cả</button><button class="mode-chip" type="button" data-mode="research">Nghiên cứu</button><button class="mode-chip" type="button" data-mode="news">Tin tức</button><button class="mode-chip" type="button" data-mode="tech">Công nghệ</button><button class="mode-chip" type="button" data-mode="github">GitHub</button><button class="mode-chip" type="button" data-mode="wiki">Wikipedia</button><button class="mode-chip" type="button" data-mode="local">Website riêng</button>
    </div><button class="search-submit" type="submit">Tìm kiếm <span aria-hidden="true">→</span></button>
   </form>
   <div class="results-meta"><span id="resultSummary">Sẵn sàng tìm kiếm</span><button id="synthesizeBtn" class="text-link hidden" type="button">✦ Tổng hợp bằng AI</button></div>
   <div id="answerOutput" class="answer-card hidden"></div>
   <div id="results" class="result-list"><div class="empty-state"><strong>Chưa có kết quả</strong>Nhập truy vấn để bắt đầu.</div></div>
  </section>

  <section class="view" id="view-ai" data-view="ai">
   <div class="view-head"><div class="view-kicker">AI ASSISTANT</div><h1>AI Workspace</h1><p>Hỏi, phân tích hoặc giao một nhiệm vụ. Lịch sử gần đây được lưu trên thiết bị này.</p></div>
   <div id="chatLog" class="chat-log"><div class="bubble assistant">Chào bạn. Mình có thể giải thích, lập kế hoạch, viết mã hoặc phân tích dữ liệu. Bạn muốn bắt đầu với việc gì?</div></div>
   <form id="chatForm" class="chat-composer">
    <textarea id="chatInput" rows="2" placeholder="Mô tả điều bạn cần..." aria-label="Tin nhắn AI"></textarea>
    <div class="composer-bottom"><label class="attach-btn" for="chatFile">＋ Tệp</label><input id="chatFile" class="hidden" type="file" aria-label="Chọn tệp"><span id="fileName" class="file-name">Tối đa 20 MB</span><button class="send-btn" type="submit">Gửi ↗</button></div>
   </form>
   <div id="chatNotice" class="status-message">AI có thể gọi các công cụ Nolane đã đăng ký; không có quyền chạy shell tùy ý.</div>
  </section>

  <section class="view" id="view-tools" data-view="tools">
   <div class="view-head"><div class="view-kicker">PROCESSOR LIBRARY</div><h1>Tool Center</h1><p>Danh mục công cụ và lịch sử thực thi được tách riêng.</p></div>
   <div class="filter-row"><input id="toolFilter" type="search" placeholder="Tìm theo tên, mô tả, định dạng..."><select id="toolCategory" aria-label="Danh mục"><option value="all">Tất cả</option><option value="image">Hình ảnh</option><option value="document">Tài liệu</option><option value="audio-video">Audio / Video</option><option value="data">Dữ liệu</option><option value="developer">Lập trình</option><option value="repository">Repository</option><option value="utility">Tiện ích</option></select></div>
   <div id="toolMeta" class="results-meta"><span>Đang tải catalog…</span><button id="reloadTools" class="text-link" type="button">Làm mới</button></div>
   <div id="toolCategories" class="tool-categories"></div>
   <div id="toolList" class="tool-list"><div class="empty-state">Đang tải danh sách công cụ…</div></div>
   <section class="section"><div class="section-head"><div><div class="section-title">Tác vụ gần đây</div><div class="section-note">Theo dõi tiến trình và kết quả xử lý tệp</div></div><button id="reloadJobs" class="text-link" type="button">Làm mới</button></div><div id="jobList" class="job-list"><div class="empty-state">Chưa tải job.</div></div></section>
  </section>

  <section class="view" id="view-library" data-view="library">
   <div class="view-head"><div class="view-kicker">PERSONAL KNOWLEDGE</div><h1>Personal Index</h1><p>Thu thập và tra cứu các website công khai của riêng bạn.</p></div>
   <form id="crawlForm" class="search-card">
    <div class="section-title" style="margin:0 0 9px">Thêm website vào chỉ mục</div>
    <input id="crawlUrl" class="field" type="url" placeholder="https://example.com" required>
    <div class="library-form" style="margin-top:8px"><select id="crawlPages" class="field" aria-label="Số trang"><option value="5">5 trang</option><option value="10" selected>10 trang</option><option value="20">20 trang</option></select><button type="submit">Index site</button></div>
    <div id="crawlMessage" class="status-message">Chỉ thu thập HTTPS public, cùng origin và tuân thủ robots.txt.</div>
   </form>
   <section class="section"><div class="section-head"><div><div class="section-title">Website đã lưu</div><div id="indexMeta" class="section-note">Đang tải chỉ mục…</div></div><button id="reloadIndex" class="text-link" type="button">Làm mới</button></div><div id="indexList" class="index-list"><div class="empty-state">Đang tải…</div></div></section>
   <section class="section"><div class="section-head"><div><div class="section-title">Crawl jobs</div><div class="section-note">Tình trạng thu thập gần đây</div></div><button id="reloadCrawls" class="text-link" type="button">Làm mới</button></div><div id="crawlList" class="job-list"><div class="empty-state">Chưa tải tác vụ.</div></div></section>
  </section>
 </main>

 <nav class="bottom-nav" aria-label="Điều hướng chính">
  <button class="nav-item active" data-tab="home" type="button"><span class="nav-icon">⌂</span><span>Tổng quan</span></button>
  <button class="nav-item" data-tab="search" type="button"><span class="nav-icon">⌕</span><span>Tìm kiếm</span></button>
  <button class="nav-item" data-tab="ai" type="button"><span class="nav-icon">✦</span><span>AI</span></button>
  <button class="nav-item" data-tab="tools" type="button"><span class="nav-icon">▦</span><span>Tools</span></button>
  <button class="nav-item" data-tab="library" type="button"><span class="nav-icon">⌑</span><span>Kho riêng</span></button>
 </nav>
</div>
<div id="toast" class="toast" role="status" aria-live="polite"></div>
<script>
(function(){
'use strict';
var tg=window.Telegram&&window.Telegram.WebApp?window.Telegram.WebApp:null;
var $=function(id){return document.getElementById(id)};
var state={tab:'home',mode:'web',results:[],eventId:null,tools:[],category:'all',history:[],busy:false,toastTimer:null};
function haptic(kind){
 try{if(tg&&tg.HapticFeedback){if(kind==='success'||kind==='error')tg.HapticFeedback.notificationOccurred(kind);else tg.HapticFeedback.impactOccurred(kind||'light')}}catch(e){}
}
function showToast(message){
 var el=$('toast');el.textContent=String(message||'');el.classList.add('show');
 clearTimeout(state.toastTimer);state.toastTimer=setTimeout(function(){el.classList.remove('show')},2300);
}
function authHeaders(){return {'content-type':'application/json','x-nolane-request':'1'}}
async function api(path,options){
 var response=await fetch(path,Object.assign({credentials:'same-origin',cache:'no-store'},options||{}));
 var data;try{data=await response.json()}catch(e){throw new Error('Máy chủ trả về phản hồi không hợp lệ.')}
 if(!response.ok)throw new Error(data.error||('HTTP '+response.status));
 return data;
}
function safeUrl(value){
 try{var u=new URL(value);return u.protocol==='https:'?u.href:null}catch(e){return null}
}
function textNode(el,value){el.textContent=value==null?'':String(value)}
function addText(parent,tag,className,value){
 var el=document.createElement(tag);if(className)el.className=className;textNode(el,value);parent.appendChild(el);return el;
}
function notifyError(container,error){
 container.replaceChildren();var n=addText(container,'div','status-message error',error&&error.message||'Không thể hoàn tất thao tác.');
}
function applyTelegramTheme(){
 if(!tg)return;
 try{
  var p=tg.themeParams||{};
  var root=document.documentElement;
  if(p.bg_color)root.style.setProperty('--tg-theme-bg-color',p.bg_color);
  if(p.secondary_bg_color)root.style.setProperty('--tg-theme-secondary-bg-color',p.secondary_bg_color);
  if(p.text_color)root.style.setProperty('--tg-theme-text-color',p.text_color);
  if(p.hint_color)root.style.setProperty('--tg-theme-hint-color',p.hint_color);
  if(p.button_color)root.style.setProperty('--tg-theme-button-color',p.button_color);
  if(p.button_text_color)root.style.setProperty('--tg-theme-button-text-color',p.button_text_color);
  if(p.link_color)root.style.setProperty('--tg-theme-link-color',p.link_color);
  if(tg.setHeaderColor)tg.setHeaderColor(p.secondary_bg_color||p.bg_color||'#101827');
  if(tg.setBackgroundColor)tg.setBackgroundColor(p.bg_color||'#0b1220');
 }catch(e){}
}
function setTab(tab,record,refreshData){
 if(!['home','search','ai','tools','library'].includes(tab))tab='home';
 if(record!==false&&state.tab!==tab){
  try{history.pushState({tab:tab},'',location.pathname+'#'+tab)}catch(e){}
 }
 state.tab=tab;
 document.querySelectorAll('.view').forEach(function(v){v.classList.toggle('active',v.dataset.view===tab)});
 document.querySelectorAll('.nav-item').forEach(function(v){v.classList.toggle('active',v.dataset.tab===tab)});
 if(tg&&tg.BackButton){if(tab==='home')tg.BackButton.hide();else tg.BackButton.show()}
 if(refreshData!==false){
  if(tab==='tools'){if(!state.tools.length)loadTools();loadJobs()}
  if(tab==='library')loadLibrary();
  if(tab==='home')loadMetrics();
 }
 haptic('selection');
 window.scrollTo({top:0,behavior:'smooth'});
}
function modeSelect(mode){
 state.mode=mode;
 document.querySelectorAll('[data-mode]').forEach(function(b){b.classList.toggle('active',b.dataset.mode===mode)});
}
function renderRecent(){
 var box=$('recentSearches');box.replaceChildren();
 var items=[];try{items=JSON.parse(localStorage.getItem('nolane.tg.recent')||'[]')}catch(e){}
 if(!items.length)return;
 var head=addText(box,'div','section-head','');addText(head,'div','section-title','Tìm kiếm gần đây');
 var row=addText(box,'div','mode-strip','');
 items.slice(0,5).forEach(function(q){
  var b=addText(row,'button','mode-chip',q);b.type='button';b.addEventListener('click',function(){$('query').value=q;setTab('search',true);runSearch(q)});
 });
}
function rememberQuery(query){
 try{var arr=JSON.parse(localStorage.getItem('nolane.tg.recent')||'[]');arr=[query].concat(arr.filter(function(x){return x!==query})).slice(0,6);localStorage.setItem('nolane.tg.recent',JSON.stringify(arr))}catch(e){}
 renderRecent();
}
function setSearchBusy(busy){
 state.busy=busy;$('searchForm').querySelector('button[type=submit]').disabled=busy;
 $('resultSummary').textContent=busy?'Đang tìm kiếm qua nhiều nguồn…':'Đang tải kết quả';
 $('results').replaceChildren();if(busy)addText($('results'),'div','empty-state','Đang truy vấn và xếp hạng kết quả…');
}
function renderResults(results){
 var box=$('results');box.replaceChildren();
 if(!results.length){var empty=addText(box,'div','empty-state','');addText(empty,'strong','','Không tìm thấy kết quả');empty.appendChild(document.createTextNode('Thử cụm từ khác hoặc đổi danh mục.'));return}
 results.forEach(function(item,index){
  var card=addText(box,'article','result-card','');
  var origin=addText(card,'div','result-origin','');
  addText(origin,'span','result-favicon',(item.domain||'N').slice(0,1).toUpperCase());
  addText(origin,'span','',(item.domain||'')+' · '+(item.provider||'Web'));
  var heading=addText(card,'h3','','');
  var url=safeUrl(item.url);var anchor=addText(heading,'a','',String(index+1)+'. '+(item.title||item.url));
  anchor.href=url||'#';anchor.target='_blank';anchor.rel='noopener noreferrer';
  addText(card,'p','',item.snippet||'Không có mô tả từ nguồn.');
 });
}
async function runSearch(explicitQuery){
 var q=String(explicitQuery!==undefined?explicitQuery:$('query').value).trim();
 if(q.length<2){showToast('Nhập ít nhất 2 ký tự.');return}
 state.tab='search';setTab('search',false);rememberQuery(q);setSearchBusy(true);
 try{
  var data=await api('/api/search?'+new URLSearchParams({q:q,mode:state.mode}));
  state.results=data.results||[];state.eventId=data.eventId||null;
  renderResults(state.results);textNode($('resultSummary'),state.results.length+' kết quả · '+((data.meta&&data.meta.elapsedMs)||0)+' ms');
  $('synthesizeBtn').classList.toggle('hidden',!state.results.length);
  haptic('success');
 }catch(error){notifyError($('results'),error);textNode($('resultSummary'),'Không thể hoàn tất tìm kiếm');haptic('error')}
 finally{state.busy=false;$('searchForm').querySelector('button[type=submit]').disabled=false}
}
async function synthesize(){
 if(state.results.length<1)return;
 var output=$('answerOutput');output.classList.remove('hidden');output.replaceChildren();addText(output,'div','status-message','Đang tổng hợp câu trả lời và đối chiếu nguồn…');
 $('synthesizeBtn').disabled=true;
 try{
  var data=await api('/api/ask',{method:'POST',headers:authHeaders(),body:JSON.stringify({q:$('query').value.trim(),mode:state.mode})});
  output.replaceChildren();addText(output,'h3','','✦ Tổng hợp bằng AI');addText(output,'div','answer-copy',data.answer);
  var sources=addText(output,'div','source-list','');
  (data.sources||[]).forEach(function(item,index){var u=safeUrl(item.url);if(!u)return;var a=addText(sources,'a','source-link','['+(index+1)+'] '+(item.title||item.domain));a.href=u;a.target='_blank';a.rel='noopener noreferrer'});
 }catch(error){notifyError(output,error)}
 finally{$('synthesizeBtn').disabled=false}
}
function renderChat(){
 var box=$('chatLog');box.replaceChildren();
 state.history.forEach(function(m){addText(box,'div','bubble '+(m.role==='user'?'user':'assistant'),m.content)});
 box.scrollTop=box.scrollHeight;
}
function saveChat(){
 try{localStorage.setItem('nolane.tg.chat',JSON.stringify(state.history.slice(-10)))}catch(e){}
}
async function sendChat(){
 var input=$('chatInput'),message=input.value.trim(),file=$('chatFile').files[0];
 if(!message&&!file){input.focus();return}
 if(file&&file.size>20*1024*1024){showToast('Tệp vượt giới hạn 20 MB.');return}
 var prompt=message||('Hãy phân tích tệp '+file.name);
 if(file&&prompt.length<6)prompt='Hãy phân tích và tóm tắt tệp '+file.name;
 state.history.push({role:'user',content:prompt+(file?' · '+file.name:'')});state.history=state.history.slice(-10);
 renderChat();input.value='';$('fileName').textContent=file?file.name:'Tối đa 20 MB';
 var button=$('chatForm').querySelector('button[type=submit]');button.disabled=true;
 var pendingText='';
 var pendingBubble=addText($('chatLog'),'div','bubble assistant pending',file?'Đang tải tệp lên và lập kế hoạch xử lý…':'Đang suy nghĩ…');
 $('chatLog').scrollTop=$('chatLog').scrollHeight;
 try{
  if(file){
   var form=new FormData();form.set('prompt',prompt);form.set('file',file,file.name);
   var uploaded=await api('/api/ai/upload',{method:'POST',headers:{'x-nolane-request':'1'},body:form});
   pendingText='Đã nhận tệp '+uploaded.fileName+'.\\nPipeline: '+(uploaded.pipeline||[]).join(' → ')+'\\nJob: '+uploaded.jobId+'\\nKết quả sẽ được gửi về Telegram và xuất hiện trong Tool Center.';
   $('chatFile').value='';$('fileName').textContent='Tối đa 20 MB';
  }else{
   var reply=await api('/api/chat',{method:'POST',headers:authHeaders(),body:JSON.stringify({message:message,history:state.history.slice(0,-1),task:'chat'})});
   pendingText=reply.answer||'AI chưa trả về nội dung.';
  }
  pendingBubble.classList.remove('pending');pendingBubble.textContent=pendingText;
  state.history.push({role:'assistant',content:pendingText});state.history=state.history.slice(-10);saveChat();renderChat();haptic('success');
 }catch(error){
  pendingBubble.classList.remove('pending');pendingBubble.textContent='Không thể hoàn tất: '+error.message;
  state.history.push({role:'assistant',content:pendingBubble.textContent});state.history=state.history.slice(-10);saveChat();renderChat();haptic('error')
 }
 finally{button.disabled=false;$('chatInput').focus()}
}
function normalizeSearch(value){return String(value||'').toLocaleLowerCase('vi').normalize('NFD').replace(/[\u0300-\u036f]/g,'')}
var categoryNames={image:'Hình ảnh',document:'Tài liệu','audio-video':'Audio / Video',data:'Dữ liệu',developer:'Lập trình',repository:'Repository',utility:'Tiện ích'};
function renderTools(){
 var box=$('toolList');box.replaceChildren();
 var query=normalizeSearch($('toolFilter').value.trim());
 var filtered=state.tools.filter(function(tool){
  if(state.category!=='all'&&tool.category!==state.category)return false;
  var hay=normalizeSearch([tool.id,tool.name,tool.description,tool.output,(tool.accepts||[]).join(' '),categoryNames[tool.category]||''].join(' '));
  return !query||query.split(/\s+/).every(function(term){return hay.includes(term)});
 }).slice(0,80);
 textNode($('toolMeta'),filtered.length+' kết quả hiển thị · '+state.tools.length+' công cụ trong catalog');
 if(!filtered.length){var empty=addText(box,'div','empty-state','');addText(empty,'strong','','Không có công cụ phù hợp');return}
 filtered.forEach(function(tool){
  var card=addText(box,'article','tool-card',''),top=addText(card,'div','tool-top',''),left=addText(top,'div','','');
  addText(left,'h3','',tool.name);addText(left,'div','tool-meta',(categoryNames[tool.category]||tool.category)+' · '+tool.id);
  addText(top,'span','tool-badge'+(tool.ready?'':' off'),tool.ready?'READY':'SETUP');
  addText(card,'p','',tool.description);
  addText(card,'div','tool-meta','Nhận: '+(tool.accepts||[]).slice(0,4).join(', ')+' · Trả về: '+tool.output);
  var actions=addText(card,'div','tool-actions','');
  var copy=addText(actions,'button','','Sao chép lệnh');
  copy.type='button';copy.addEventListener('click',async function(){var command='/tool '+tool.id;try{await navigator.clipboard.writeText(command);showToast('Đã sao chép '+command)}catch(e){showToast(command)}haptic('success')});
  var use=addText(actions,'button','primary','Dùng với AI');
  use.type='button';use.addEventListener('click',function(){setTab('ai');$('chatInput').value='Tôi muốn dùng tool '+tool.name+' ('+tool.id+'). Hãy hướng dẫn tôi chọn và xử lý tệp phù hợp.';$('chatInput').focus()});
 });
}
async function loadTools(){
 try{var data=await api('/api/tools/catalog');state.tools=data.tools||[];renderTools()}
 catch(error){notifyError($('toolList'),error)}
}
function renderJobs(jobs){
 var box=$('jobList');box.replaceChildren();
 if(!jobs.length){addText(box,'div','empty-state','Chưa có tác vụ gần đây.');return}
 jobs.slice(0,8).forEach(function(job){
  var card=addText(box,'article','job-card','');addText(card,'strong','',(job.toolId||'Tool job')+' · '+(job.fileName||''));
  var status=job.status==='completed'?'Hoàn thành':job.status==='failed'?'Thất bại':job.status==='running'?'Đang chạy':'Đang chờ';
  addText(card,'span','job-status',status);
  if(job.progress)addText(card,'span','','Tiến trình '+job.progress.completed+'/'+job.progress.total+' bước');
  if(job.resultSummary)addText(card,'span','',job.resultSummary);
  if(job.error)addText(card,'span','',job.error);
 });
}
async function loadJobs(){
 try{var data=await api('/api/tools/jobs');renderJobs(data.jobs||[])}
 catch(error){notifyError($('jobList'),error)}
}
function renderIndex(pages,total){
 var box=$('indexList');box.replaceChildren();textNode($('indexMeta'),total+' trang đã lập chỉ mục');
 if(!pages.length){addText(box,'div','empty-state','Chưa có trang nào. Hãy thêm website công khai ở trên.');return}
 pages.forEach(function(page){
  var card=addText(box,'article','index-card','');var link=addText(card,'a','',page.title||page.url||'Trang đã lập chỉ mục');
  var url=safeUrl(page.url);link.href=url||'#';link.target='_blank';link.rel='noopener noreferrer';link.style.color='var(--link)';link.style.textDecoration='none';
  addText(card,'span','',(page.domain||'')+(page.updatedAt?' · '+new Date(page.updatedAt).toLocaleDateString('vi-VN'):''));
 });
}
async function loadIndex(){
 try{var data=await api('/api/index?limit=20&offset=0');renderIndex(data.pages||data.items||[],data.total||0)}
 catch(error){notifyError($('indexList'),error)}
}
async function loadCrawls(){
 try{var data=await api('/api/crawls');var box=$('crawlList');box.replaceChildren();var jobs=data.jobs||[];if(!jobs.length){addText(box,'div','empty-state','Chưa có crawl job.');return}jobs.slice(0,6).forEach(function(job){var card=addText(box,'article','job-card','');addText(card,'strong','',(job.status||'QUEUED').toUpperCase()+' · '+(job.indexed||0)+'/'+(job.maxPages||0)+' trang');addText(card,'span','',job.seedUrl||'');if(job.lastError)addText(card,'span','',job.lastError)})}
 catch(error){notifyError($('crawlList'),error)}
}
async function loadLibrary(){await Promise.all([loadIndex(),loadCrawls()])}
async function loadMetrics(){
 try{
  var health=await fetch('/health',{credentials:'same-origin',cache:'no-store'}).then(function(r){return r.json()});
  var pill=$('systemStatus');pill.classList.toggle('ready',Boolean(health.ok&&health.database==='reachable'));
  textNode($('systemStatusText'),health.ok?'SYSTEM ONLINE':'LIMITED');
  textNode($('metricSearch'),health.database==='reachable'?'LIVE':'—');
 }catch(e){textNode($('systemStatusText'),'OFFLINE');$('systemStatus').classList.remove('ready')}
 textNode($('metricTools'),state.tools.length?state.tools.filter(function(tool){return tool.ready}).length:'—');
 try{var jobs=await api('/api/tools/jobs');textNode($('metricJobs'),(jobs.jobs||[]).length)}catch(e){textNode($('metricJobs'),'—')}
}
function popHistory(){
 var tab=(location.hash||'').slice(1);
 if(['home','search','ai','tools','library'].includes(tab))setTab(tab,false);
 else setTab('home',false);
}
async function start(){
 try{
  var ticket=new URLSearchParams(location.search).get('ticket');
  if(ticket){
   await api('/api/auth/exchange',{method:'POST',headers:authHeaders(),body:JSON.stringify({ticket:ticket})});
   history.replaceState({},'',location.pathname+location.hash);
  }else{
   // The persistent Telegram Menu shortcut is static and can only reuse the current same-origin session.
   await api('/api/auth/me');
  }
  $('auth').classList.add('hidden');$('app').classList.remove('hidden');
  if(state.history.length===0){try{state.history=JSON.parse(localStorage.getItem('nolane.tg.chat')||'[]').filter(function(m){return m&&['user','assistant'].includes(m.role)&&typeof m.content==='string'}).slice(-10)}catch(e){state.history=[]}}
  renderChat();renderRecent();
  await Promise.all([loadTools(),loadLibrary(),loadMetrics()]);
  var initialTab=(location.hash||'').slice(1);
  if(['home','search','ai','tools','library'].indexOf(initialTab)>=0)setTab(initialTab,false,false);
 }catch(error){$('auth').classList.remove('hidden');textNode($('authMessage'),error.message||'Đăng nhập thất bại. Hãy gửi /start trong Telegram để tạo liên kết mới.')}
}
document.querySelectorAll('[data-tab]').forEach(function(button){button.addEventListener('click',function(){setTab(button.dataset.tab)})});
document.querySelectorAll('[data-open]').forEach(function(button){button.addEventListener('click',function(){setTab(button.dataset.open)})});
document.querySelectorAll('[data-mode]').forEach(function(button){button.addEventListener('click',function(){modeSelect(button.dataset.mode)})});
$('homeModes').addEventListener('click',function(event){var b=event.target.closest('[data-mode]');if(b)modeSelect(b.dataset.mode)});
$('searchModes').addEventListener('click',function(event){var b=event.target.closest('[data-mode]');if(b)modeSelect(b.dataset.mode)});
$('homeSearchForm').addEventListener('submit',function(event){event.preventDefault();var q=$('homeQuery').value.trim();if(q.length<2){showToast('Nhập ít nhất 2 ký tự.');return}$('query').value=q;setTab('search');runSearch(q)});
$('searchForm').addEventListener('submit',function(event){event.preventDefault();runSearch()});
$('synthesizeBtn').addEventListener('click',synthesize);
$('chatForm').addEventListener('submit',function(event){event.preventDefault();sendChat()});
$('toolFilter').addEventListener('input',renderTools);$('toolCategory').addEventListener('change',function(){state.category=$('toolCategory').value;renderTools()});
$('reloadTools').addEventListener('click',loadTools);$('reloadJobs').addEventListener('click',loadJobs);
$('refreshSystem').addEventListener('click',loadMetrics);
$('reloadIndex').addEventListener('click',loadIndex);$('reloadCrawls').addEventListener('click',loadCrawls);
$('crawlForm').addEventListener('submit',async function(event){event.preventDefault();var url=$('crawlUrl').value.trim();if(!url)return;var button=$('crawlForm').querySelector('button');button.disabled=true;try{var data=await api('/api/crawl',{method:'POST',headers:authHeaders(),body:JSON.stringify({url:url,maxPages:Number($('crawlPages').value)})});textNode($('crawlMessage'),'Đã xếp hàng crawl '+data.id+'. Mở lại danh sách sau ít phút để xem tiến trình.');haptic('success');await loadCrawls()}catch(error){textNode($('crawlMessage'),error.message);$('crawlMessage').classList.add('error')}finally{button.disabled=false}});
$('refreshToolJobs')&&$('refreshToolJobs').addEventListener('click',loadJobs);
$('chatFile').addEventListener('change',function(){var file=$('chatFile').files[0];textNode($('fileName'),file?file.name:'Tối đa 20 MB')});
$('query').addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();runSearch()}});
$('homeQuery').addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();$('homeSearchForm').requestSubmit()}});
$('reloadJobs').addEventListener('click',loadJobs);
window.addEventListener('popstate',popHistory);
if(tg){
 try{tg.ready();tg.expand();applyTelegramTheme();if(tg.onEvent){tg.onEvent('themeChanged',applyTelegramTheme)}if(tg.BackButton){tg.BackButton.onClick(function(){if(state.tab!=='home'){if(history.state&&history.state.tab)history.back();else setTab('home',false)}else tg.close()})}}catch(e){}
}
start();
})();
</script>
</body>
</html>`;
export function telegramMiniAppResponse(): Response {
 return new Response(HTML,{
  headers:{
   "content-type":"text/html; charset=utf-8",
   "cache-control":"no-store, max-age=0",
   "x-content-type-options":"nosniff",
   "referrer-policy":"no-referrer",
   "content-security-policy":"default-src 'self'; script-src 'unsafe-inline' https://telegram.org; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
  },
 });
}
