# Verified Project Status

Last verified: 2026-11-18. This document distinguishes production deployment and configuration checks from user-level behavior that still requires a real Telegram interaction.

## Repository and production release

- Repository: https://github.com/Nolane-x/Nolane-search
- Default branch: `main`
- Latest production source commit: `ea01f12c15520092bae1a0b439f93dff0c6eea6b`
- Browser search and retrieval upgrade: [PR #2](https://github.com/Nolane-x/Nolane-search/pull/2)
- Bounded site indexing and search feedback: [PR #3](https://github.com/Nolane-x/Nolane-search/pull/3)
- Production Worker: https://nolane-search.nolane-file.workers.dev
- Cloudflare Worker version ID: `3f012fc3-68d1-44fc-8d57-44fa214ea1b9`

The release adds a private browser search portal, AI Overview, multi-turn chat, multi-signal retrieval ranking, relevance-aware provider fallback, AI-assisted Deep Search query planning, an owner-controlled bounded site crawler, a Personal Web Index panel, and per-result helpful/not-helpful feedback.

## CI and deployment verification

| Check | Run | Result |
|---|---:|---|
| PR CI: typecheck, 55 unit tests, script syntax checks and Worker build | [44242461140](https://github.com/Nolane-x/Nolane-search/actions/runs/44118842734) | PASS |
| Main CI: typecheck, 51 unit tests, script syntax checks and Worker build | [44242568805](https://github.com/Nolane-x/Nolane-search/actions/runs/44119582728) | PASS |
| Worker bundle export and production smoke test | [44242568822](https://github.com/Nolane-x/Nolane-search/actions/runs/44119582985) | PASS |
| Production Worker deployment, runtime secret upload, webhook and command registration | [44242568919](https://github.com/Nolane-x/Nolane-search/actions/runs/44119582847) | PASS |

The deployment log confirms:
- Worker `nolane-search` was uploaded and deployed.
- Runtime `AI_ROUTER_CONFIG` was uploaded as a hidden secret.
- Cron `*/30 * * * *` and Queue producer/consumer bindings remained attached.
- Telegram webhook registration succeeded.
- Telegram bot command registration succeeded, including `/web`.

## Live health verification

Fetched production endpoints on 2026-11-18:
- `GET /health` returned `ok: true` and `database: reachable`.
- Configured search sources: Tavily, Exa, TinyFish and GitHub public search.
- Brave remains optional and is not configured.
- OpenRouter legacy key route is present with six configured model IDs.
- AI Router reports `aiRouter: true`, **4 provider-key routes** and **9 model routes**.
- Telegram archive is enabled.

The four configured AI routes correspond to the additional provider configuration plus the retained OpenRouter legacy fallback. Health verifies that routes and model entries were loaded; it does not prove that each upstream API key, model entitlement, quota or live inference is working. No billable live inference probe was run during deployment.

The browser root returns the new Nolane Search HTML page, identifies itself as `noindex,nofollow`, and prompts anonymous visitors to authenticate through the Telegram `/web` command.

## Browser portal and access controls

- `/web` is available only to an allowlisted Telegram user in a private bot chat.
- Login ticket: 256-bit random token, SHA-256 hash stored in D1, five-minute expiry and one-time atomic consumption.
- Browser session: random token whose SHA-256 hash is stored in D1; seven-day expiry; Secure, HttpOnly and SameSite=Strict cookie.
- `/api/search`, `/api/ask`, `/api/chat`, `/api/crawl`, `/api/crawls` and `/api/feedback` require an active session whose Telegram user remains on the allowlist.
- Per-user minute limits: search 30, AI Overview 8, chat 12.
- POST requests are same-origin checked; JSON bodies are capped at 30 KB.
- Logout revokes the server-side session. Scheduled cleanup removes expired tickets/sessions and stale rate-limit rows.
- Chat history and recent searches are bounded in browser local storage; conversation transcripts are not persisted as server-side chat records.

The web interface includes Web, News, Research, Technology, GitHub, Wikipedia and private-site search categories, result cards with helpful/not-helpful controls, AI Overview with linked sources, multi-turn Nolane Chat, Personal Web Index, responsive layout, recent searches and a light/dark theme.

## Search and retrieval behavior

- Search remains a federated metasearch engine backed by external provider APIs, not an independent crawler/index of the entire Internet.
- General web search queries Tavily first. If Tavily fails, returns fewer than six links, or the result set is lexically weak for the user's query, independent Exa, TinyFish, Brave and Wikipedia sources are queried as available.
- Technology search uses Tavily, Exa, TinyFish and GitHub; research uses Tavily, Exa and TinyFish research discovery; news uses Tavily, Brave, TinyFish and Exa as available.
- Ranking now uses IDF-weighted query coverage across title/snippet/URL, a weak provider-score prior, snippet quality, phrase matching, a small .gov/.edu source-type prior, freshness weighted by query intent, URL deduplication and domain diversity. It is a transparent heuristic, not a learned Google-scale ranking system.
- Candidate limit is 20. Telegram continues to display five results per page, with pagination sessions bound to owner user ID and chat ID and a 15-minute TTL.
- Relative publication ages are normalized to ISO timestamps when their format is recognized.
- Supported query operators: `site:`, `filetype:`, `intitle:`, `inurl:`, negative terms such as `-deprecated`, `after:YYYY-MM-DD` and `before:YYYY-MM-DD`. Operators are also enforced locally, even when an external provider does not implement them.
- Deep Search uses AI to propose complementary query angles when AI routes are configured, falls back to deterministic queries if planning fails, gathers results across configured providers, fetches/enriches up to seven selected pages with TinyFish and re-ranks the extracted evidence before synthesis.
- Search cache TTLs are mode-sensitive: news is short-lived, research is cached longer than general web search.

## Owner-controlled site indexing

- Telegram: `/crawl https://example.com [1-20]` enqueues a bounded crawl (default 10 pages); `/crawls` lists the current user's recent crawl jobs.
- Browser: Personal Web Index panel accepts a public HTTPS seed URL and a 5/10/20 page cap; status is refreshed from authenticated `/api/crawls`.
- Crawl jobs use the existing Queue and D1 search_cache `site-crawl:` prefix; there is no new D1 schema or additional API secret.
- The crawler is same-origin only, validates redirects, checks robots.txt, follows same-origin sitemap locations declared by robots.txt (including bounded nested sitemap indexes) plus `/sitemap.xml`, follows bounded same-origin HTML links, extracts article/main text where available and stores compact title/text in existing D1 indexed_pages and FTS5.
- Local retrieval combines FTS5 OR-term recall with title-weighted BM25 and the shared heuristic reranker; it does not require a vector database or embedding API.
- Hard limits: 20 pages per job, 350 KB maximum response read per page and 10-second page fetch timeout. It skips binary assets and URL paths with query strings.
- It does not render JavaScript-heavy websites, bypass login, defeat anti-bot controls or crawl external domains. Use it only for sites whose robots policy permits it.

## Search relevance feedback

- Search results have optional helpful/not-helpful controls. Feedback is verified against the caller's authenticated search event and a hash of the result URL.
- Search events store hashes of query+mode and result URLs; raw query strings are not written to feedback metadata.
- Aggregate votes are query/mode-specific, smoothed for small sample sizes and capped to a +/-0.10 ranking score adjustment. Individual votes expire after 30 days and aggregates after 180 days.
- Feedback is a small owner preference signal, not a trained relevance model and not a measure of factual accuracy.

## Cloudflare resources

Account ID: `1172c01120a2470aa12f81e5b4778556`

| Resource | Name | ID / details | State |
|---|---|---|---|
| Worker | `nolane-search` | https://nolane-search.nolane-file.workers.dev | Deployed |
| D1 | `nolane-search-db` | `4f6a8cbd-cc8c-42b9-be6a-ed45c709d3db` | APAC; reachable |
| Main Queue | `nolane-search-jobs` | `8a09dc04a6824faaa90f379f45f75ac0` | Producer and consumer attached |
| Dead-letter Queue | `nolane-search-dlq` | `e44fe78242614ed1b448dbea7dbe94e0` | Consumer attached |
| Cron | `*/30 * * * *` | Every 30 minutes | Active |
| R2 / KV | — | — | Not used |

### D1 schema

The live D1 `schema_migrations` table contains:
- `0001_core.sql`
- `0002_deep_search_jobs.sql`
- `0003_web_portal.sql`

PR #3 did not introduce a new D1 migration; it reuses the existing indexed_pages/FTS5 schema, search_cache and Queue.

The new migration creates `web_login_tickets`, `web_sessions` and `web_rate_limits`, plus supporting indexes. All three tables and the migration record were queried after applying the migration.

### D1 permission handling

The first automatic deployment attempt found that `CLOUDFLARE_API_TOKEN` can deploy Workers but is not authorized for D1 Query API calls (HTTP 403). The migration was then successfully applied and verified directly against the connected Cloudflare D1 database. A subsequent Worker deployment succeeded with the migration step skipped because the migration had already been applied.

The deploy workflow now separates permissions:
- `CLOUDFLARE_API_TOKEN`: Worker deployment and Queue configuration.
- `CLOUDFLARE_D1_API_TOKEN`: optional separate token with Account → D1 → Edit, required only when a future changed migration needs to run.

Create the second secret before the next commit that introduces a new file under `database/migrations/`. Ordinary code deployments do not need the D1 token.

## Remaining owner-level end-to-end checks

These need a real interaction from the owner's Telegram account; CI and the public health endpoint cannot complete them:
1. Open the private Telegram chat and send `/web`. Open the returned one-time link and confirm browser login works, then test logout and a fresh login link.
2. Try `/crawl https://your-own-public-site.example 10` on a website you control, then use `/crawls` and search its contents with `/local` or Website của tôi. Confirm only permitted pages are indexed.
3. Use Personal Web Index in the browser to enqueue a small crawl and refresh its status.
4. Vote helpful/not-helpful on a few search results, then repeat the exact same query to observe the small ranking nudge.
2. Run a browser search in Web, News, Research and GitHub categories. Confirm results open and the result count / timing are sensible.
3. Use AI Overview on a current topic and check that inline source numbers correspond to the linked sources.
4. Send a few chat messages to verify conversation continuity and verify that chat does not claim it performed live web search.
5. Run `/ai_status`, then one low-cost `/ai fast ...` request to verify live API-key acceptance. Test failover only if needed; it can spend provider quota.
6. Try a 20-result Telegram search pagination case, `/deep`, `/read`, `/watch` and archive delivery.

No API key, bot token, webhook secret or session token should be pasted into chat, committed to the repository, or included in screenshots/logs.
