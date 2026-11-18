# Architecture

## Goals

1. Search broadly without attempting to crawl the entire Internet.
2. Combine external search providers only when useful.
3. Maintain a small index of explicitly selected websites.
4. Keep recurring compute on Cloudflare, not a home PC or always-on VPS.
5. Use Telegram as interface and optional archive.
6. Keep implemented behavior separate from roadmap claims.

## Request flow

Telegram user → Telegram webhook → Cloudflare Worker
- Validate Telegram secret header.
- Telegram webhook explicitly subscribes to both `message` and `callback_query`; the deploy script verifies the active configuration with `getWebhookInfo`.
- Acknowledge allowlisted callback taps with `answerCallbackQuery` before D1 deduplication or any callback work, so slow storage cannot leave the Telegram client spinner running.
- Deduplicate update_id in D1.
- Enforce owner allowlist.
- Parse command and select search mode.
- `/start` and `/menu` open an inline dashboard; callbacks edit the same menu message instead of sending a new menu for every navigation step.
- Mode buttons save a one-shot per-user/per-chat input mode in the existing D1 `search_cache` with a 10-minute TTL. The next plain-text message consumes that state and routes to Web, Tech, News, Research, GitHub, Wiki, Local, AI, Ask or Deep Search. Slash commands clear the pending mode.
- Search-result action buttons can launch `/ask` or `/deep` from the stored owner/chat-bound 15-minute search session; the callback is validated against the original user and chat.

Quick Search → Tavily primary → (when unavailable or fewer than six results) parallel Exa/TinyFish/Brave/Wikipedia fallback → merge → local operator enforcement → normalized URL deduplication → IDF-weighted title/snippet/URL coverage + provider prior + snippet quality + query-aware freshness + exact-phrase/source-type priors → domain-diversity ranking → up to 20 candidates. The ranking remains a transparent heuristic, not a learned relevance model.

Deep Search → D1 job record → Cloudflare Queue → AI-assisted complementary query planning (with deterministic fallback) → bounded parallel Tavily/Exa/Brave/TinyFish retrieval → deduplicate/rank → optional TinyFish Fetch enrichment of up to seven sources → re-rank enriched evidence → AI Router research synthesis across configured model/key routes → Telegram report.

Direct AI → `/ai` command → task-aware AI Router → rotated/priority provider-key/model candidates → protocol adapter → bounded failover → Telegram reply. Search-grounded AI → `/ask` → federated search → evidence-only prompt → AI Router → numbered source list.
- D1 records queued/running/completed/failed state, attempt count and last failure reason.
- Queue deliveries use bounded retry delays; exhausted jobs enter the dead-letter queue and notify the originating user.
- Duplicate deliveries do not re-run jobs that are already completed or currently claimed.
- /jobs lists recent work; /retry JOB_ID creates a new job from a failed query.

Website monitoring → D1 watch metadata → 30-minute Cron → robots.txt policy check → bounded HTTP checks → content hash → compact D1 extract/FTS5 → optional Telegram snapshot document and change alert.\n\nOwner-requested site indexing → private browser panel or `/crawl` → D1 cache-backed job record → existing Cloudflare Queue → same-origin public HTTPS fetch → robots.txt policy + robots-declared sitemap locations → bounded recursive sitemap-index traversal (at most five sitemap files) + same-origin links → 1–20 HTML/text pages → semantic article/main extraction → D1 upsert + FTS5 → completion report.

## Private browser portal

- `/web` can be used only by an allowlisted owner in a private Telegram chat. It creates a cryptographically random, one-time ticket, stores only the SHA-256 hash in D1, expires it after five minutes, and sends the owner a private link.
- `POST /api/auth/exchange` consumes the ticket with a conditional D1 update and creates a seven-day server-side session. The browser receives only a Secure, HttpOnly, SameSite=Strict cookie; only its hash is stored in D1.
- `GET /api/auth/me` checks session state. `POST /api/auth/logout` revokes the current session. Expired tickets/sessions and stale rate-limit rows are removed by the scheduled maintenance task.
- `GET /api/search`, `POST /api/ask`, `POST /api/chat`, `POST /api/crawl`, `GET /api/crawls` and `POST /api/feedback` require an authenticated session whose Telegram user remains on the allowlist. Search, AI Overview and chat have separate per-user D1-backed per-minute limits. Unsafe or oversized inputs are rejected.
- Search events store only a hash of the query/mode and hashes of returned URLs. Per-result votes are stored in the existing D1 `search_cache` under internal prefixes; raw search text is not written to the feedback records. Relevance feedback is scoped to the exact query/mode and capped at ±0.10 score.\n- The UI is served inline from the Worker at `/` and uses no external script/font dependencies. Chat history is bounded in browser local storage and sent as context only when the user sends a message; it is not stored as a server transcript.
- This is a private browser search interface backed by external retrieval providers. It is not an independent full-Web crawl/index and should not be described as Google-equivalent coverage.

## Provider adapters

- Tavily: primary general web search and news.
- Exa: optional semantic discovery, especially research.
- Brave: optional backup provider.
- TinyFish Search: optional ranked web/news/academic discovery; TinyFish Fetch extracts clean Markdown from selected URLs and powers /read.
- GitHub Search API: public repository search; optional user token raises limits.
- MediaWiki Action API: free English/Vietnamese encyclopedia lookup; the query language is selected heuristically from Vietnamese diacritics. Wikipedia is an optional reference source and is not treated as primary evidence or current news.
- AI Router: multi-key model routes using OpenAI-compatible Chat Completions, Anthropic Messages or Gemini Interactions. Task tags, balanced/priority/cheapest strategy, per-route timeout, bounded failover and optional cost estimates are configured through encrypted `AI_ROUTER_CONFIG`; legacy OpenRouter is retained as a fallback.
- OpenRouter: existing ordered model fallback through `OPENROUTER_MODELS`; the legacy `OPENROUTER_MODEL` remains supported.

## Modes

- web: Tavily first; if it fails or returns fewer than four results, Exa, TinyFish and Brave are queried in parallel where configured. Results are merged before deduplication and ranking.
- tech: Tavily, TinyFish and GitHub in parallel.
- github: GitHub repositories.
- research: configured Tavily, Exa and TinyFish academic discovery in parallel.
- news: Tavily, Brave and TinyFish news search in parallel.
- wiki: direct Wikipedia reference lookup, English by default and Vietnamese when the query contains Vietnamese diacritics.
- local: hybrid personal-index retrieval over FTS5. A safely quoted OR query improves recall when only some query terms occur on a page; BM25 weights titles more heavily than body text, returns up to 60 candidates, and feeds the shared IDF/phrase/quality reranker. The final response remains capped at 20 results. No embedding model or additional API is required.

The `/search` command accepts Google-style operators: `site:domain`, `filetype:pdf`, `intitle:words`, `inurl:path`, negative terms such as `-deprecated`, `after:YYYY-MM-DD` and `before:YYYY-MM-DD`. The Worker enforces these filters locally even if a provider ignores them. Date filters use strict boundaries and require a parseable `publishedAt` timestamp; results without one are excluded. The `/site` command is a shortcut that prefixes the query with `site:`. The `/read` command uses TinyFish Fetch to extract a single HTTPS page. `/crawl https://example.com [1-20]` queues a bounded same-origin public-site crawl; `/crawls` shows recent crawl jobs. The crawler reads `robots.txt`, can seed from `/sitemap.xml`, follows only same-origin HTTPS links and writes compact text extracts to the FTS5 index. General web search only queries fallback providers when Tavily fails or returns fewer than four results; Wikipedia joins that fallback set and is also available directly through `/wiki`.

## AI routing and credential handling

- `AI_ROUTER_CONFIG` is an encrypted Worker secret containing provider entries. Each entry represents one API key; multiple entries may share the same base URL and models to rotate keys from one vendor.
- Supported wire protocols are OpenAI-compatible Chat Completions, Anthropic Messages and Gemini Interactions. Provider entries have a public HTTPS base URL, key, label, priority, model list and optional task/cost metadata.
- Candidate models are filtered by requested task. Strategies are balanced rotation, configured priority order, or cheapest based on declared per-million-token prices.
- Each route is tried at most once per request, with a hard maximum of 24 candidates. HTTP errors, timeouts and empty responses trigger fallback. API-key values are never returned in status or written to logs.
- Optional cost metadata produces estimates only. The current version surfaces token usage when returned by a vendor, but does not yet persist a complete cross-provider billing ledger.
- Balanced rotation is per Worker isolate. Cloudflare may run several isolates, so this is not a globally synchronized round-robin scheduler.

## Ranking

Current ranking is a transparent heuristic using provider scores, whole-token title/snippet overlap, exact-query title boost, freshness/domain adjustments, normalized URL deduplication and a two-results-per-domain first-pass diversity limit. It retains up to 12 candidates for Telegram pagination.

It is not a learned ranking model, does not rigorously assess source reliability and does not identify syndicated copies at different URLs. Telegram displays five results per page with inline Previous/Next controls. The D1 session is bound to the requesting user and chat and expires after 15 minutes.

## Data placement

### Telegram archive

When TELEGRAM_ARCHIVE_CHAT_ID is configured:
- Search results and Deep Search reports are copied to the archive channel.
- Website page snapshots are sent as TXT documents on first capture and detected changes.
- Watch alerts are sent to the requesting chat and archive.

Telegram is an archive destination, not a queryable database. A bot cannot efficiently query arbitrary chat history as a general-purpose index. Telegram is subject to platform limits and retention behavior; it is not unlimited storage or the only backup.

### D1

D1 stores compact operational information:
- Watch definitions and ETag/Last-Modified/hash state.
- Telegram update IDs for webhook deduplication, pruned after seven days.
- Search cache with two-minute TTL, pruned during scheduled maintenance.
- Owner-bound Telegram pagination sessions with a 15-minute TTL in the same table; session entries use a dedicated `telegram-search:` key prefix and are excluded from the cached-query status count.
- URL/title/domain and a maximum 5 KB text extract per monitored or crawled page.\n- Search event, site-crawl job and aggregate relevance-feedback metadata stored with dedicated key prefixes in `search_cache`; event URLs and query strings are hashed in the feedback records.
- FTS5 index over title and short text extract.

Full extracted text (up to 100 KB after parsing, with a 500 KB response-read cap) is sent to Telegram archive if configured. D1 does not keep the full page body.

### Queues and job lifecycle

Deep Search jobs are asynchronous and are recorded in D1 before enqueueing.
- Main Queue retries failed deliveries up to three times with increasing delays.
- Exhausted messages move to the dead-letter Queue.
- The dead-letter consumer marks the D1 job failed and attempts to notify the originating Telegram chat.
- /jobs exposes the latest eight jobs for the requesting user; /retry JOB_ID re-enqueues a failed query as a new job.
- Duplicate or stale deliveries are guarded by a conditional D1 claim. This reduces duplicate work but does not guarantee exactly-once Telegram delivery if an external send succeeds immediately before a Worker crash.
- A 30-minute Cron sweep re-enqueues up to 10 jobs whose queued/running state has not changed for more than 10 minutes. The D1 update is conditional to avoid overwriting a concurrently changed state. This is a recovery path, not exactly-once execution.
- Completed and failed job records are pruned after 30 days; queued/running jobs are not automatically deleted.

### No R2 or KV in MVP

R2 is not enabled in the linked account and neither R2 nor KV is required for the first release. Do not provision them without a measured need.

## Website monitoring limits

- Only explicitly watched URLs are fetched; there is no general crawler.
- HTTPS public hostnames only; credentials, IP literals, custom ports and obvious local hosts are rejected.
- Redirects are manual and limited to three hops; each redirect is checked.
- ETag and Last-Modified are used where present.
- At most 12 due pages per Cron invocation. Applicable robots.txt user-agent groups are combined; the longest matching rule wins and Allow wins an equal-length tie. A 404/410 robots file means no policy was published; 401/403/429, 5xx and network/read failures defer the watch rather than fetching the page.
- Response read cap is 500 KB; FTS extract cap is 5 KB.
- First successful check establishes a baseline; later hash changes trigger alerts.
- JavaScript-rendered apps, authenticated pages and anti-bot protected sites are not supported.
- Never bypass access controls, robots instructions or terms.

## Security

- Telegram webhook requires X-Telegram-Bot-Api-Secret-Token.
- Normal bot functions are private to allowlisted user IDs.
- Provider credentials remain Worker secrets.
- Website URLs and redirects are untrusted. Restrict URL schemes/hosts and rely on Cloudflare egress controls as an additional boundary. Do not treat this simple URL validation as a perfect defense against all DNS rebinding/SSRF cases.
- Webpage content is untrusted input. AI synthesis must not follow prompt-like instructions found in source pages.
- Escape provider content before Telegram HTML output.

## Scaling path

1. Build ranking evaluation before increasing crawl volume.
2. Add robust extraction and RSS/sitemap discovery.
3. Add crawl Queue, per-domain rate limits and robots/terms checks.
4. Add source provenance and richer metadata.
5. Consider Vectorize/external embeddings only after FTS quality has been measured.
6. Add R2 only if snapshot volume exceeds practical Telegram archive workflows.
7. Consider paid plans or dedicated crawler infrastructure only when real quota metrics justify it.
