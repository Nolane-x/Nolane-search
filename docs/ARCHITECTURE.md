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
- Deduplicate update_id in D1.
- Enforce owner allowlist.
- Parse command and select search mode.

Quick Search → Tavily primary → (when unavailable or fewer than four results) parallel Exa/TinyFish/Brave/Wikipedia fallback → merge → local operator enforcement → normalized URL deduplication → token-overlap relevance + freshness + domain-diversity ranking → up to 12 candidates → Telegram pages of five results.

Deep Search → D1 job record → Cloudflare Queue → bounded query expansion → parallel Tavily/Exa/Brave/TinyFish retrieval → deduplicate/rank → optional TinyFish Fetch enrichment of up to five sources → optional OpenRouter synthesis with ordered model fallback → Telegram report.
- D1 records queued/running/completed/failed state, attempt count and last failure reason.
- Queue deliveries use bounded retry delays; exhausted jobs enter the dead-letter queue and notify the originating user.
- Duplicate deliveries do not re-run jobs that are already completed or currently claimed.
- /jobs lists recent work; /retry JOB_ID creates a new job from a failed query.

Website monitoring → D1 watch metadata → 30-minute Cron → robots.txt policy check → bounded HTTP checks → content hash → compact D1 extract/FTS5 → optional Telegram snapshot document and change alert.

## Provider adapters

- Tavily: primary general web search and news.
- Exa: optional semantic discovery, especially research.
- Brave: optional backup provider.
- TinyFish Search: optional ranked web/news/academic discovery; TinyFish Fetch extracts clean Markdown from selected URLs and powers /read.
- GitHub Search API: public repository search; optional user token raises limits.
- MediaWiki Action API: free English/Vietnamese encyclopedia lookup; the query language is selected heuristically from Vietnamese diacritics. Wikipedia is an optional reference source and is not treated as primary evidence or current news.
- OpenRouter: optional Deep Search synthesis. OPENROUTER_MODELS supplies ordered model fallbacks; the legacy OPENROUTER_MODEL remains supported.

## Modes

- web: Tavily first; if it fails or returns fewer than four results, Exa, TinyFish and Brave are queried in parallel where configured. Results are merged before deduplication and ranking.
- tech: Tavily, TinyFish and GitHub in parallel.
- github: GitHub repositories.
- research: configured Tavily, Exa and TinyFish academic discovery in parallel.
- news: Tavily, Brave and TinyFish news search in parallel.
- wiki: direct Wikipedia reference lookup, English by default and Vietnamese when the query contains Vietnamese diacritics.
- local: FTS5 search over monitored-page extracts.

The `/search` command accepts a small Google-style operator set: `site:domain`, `filetype:pdf`, `intitle:words`, `after:YYYY-MM-DD` and `before:YYYY-MM-DD`. The Worker enforces these filters locally even if a provider ignores them. Date filters use strict boundaries and require a parseable `publishedAt` timestamp; results without one are excluded. The `/site` command is a shortcut that prefixes the query with `site:`. The `/read` command uses TinyFish Fetch to extract a single HTTPS page. General web search only queries fallback providers when Tavily fails or returns fewer than four results; Wikipedia joins that fallback set and is also available directly through `/wiki`.

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
- URL/title/domain and a maximum 5 KB text extract per monitored page.
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
