# Verified Project Status

Last verified: 2026-11-18. This document distinguishes production deployment and configuration checks from user-level behavior that still requires a real Telegram interaction.

## Repository and production release

- Repository: https://github.com/Nolane-x/Nolane-search
- Default branch: `main`
- Latest production source commit: `ffe1564ebfa1db5a00960c92e88e19dc6a84fb20`
- Browser search and retrieval upgrade: [PR #2](https://github.com/Nolane-x/Nolane-search/pull/2)
- Bounded site indexing and search feedback: [PR #3](https://github.com/Nolane-x/Nolane-search/pull/3)
- Hybrid personal-index retrieval and sitemap crawler upgrade: [PR #4](https://github.com/Nolane-x/Nolane-search/pull/4)
- Interactive Telegram workspace and contextual search actions: [PR #5](https://github.com/Nolane-x/Nolane-search/pull/5)
- Fix Telegram callback delivery and stuck inline-button spinners: [PR #6](https://github.com/Nolane-x/Nolane-search/pull/6)
- Production Worker: https://nolane-search.nolane-file.workers.dev
- Cloudflare Worker version ID: `e182d473-d214-4a0c-82c5-0c8662fb4b87`

The release adds a private browser search portal, AI Overview, multi-turn chat, multi-signal federated retrieval ranking, relevance-aware provider fallback, AI-assisted Deep Search query planning, owner-controlled bounded site indexing, title-weighted BM25 retrieval over the personal FTS5 index, recursive same-origin sitemap discovery, semantic article/main extraction per-result helpful/not-helpful feedback, an interactive Telegram dashboard with one-shot search/AI modes and contextual search follow-ups, plus a verified Telegram callback webhook and immediate callback acknowledgement.

## CI and deployment verification

| Check | Run | Result |
|---|---:|---|
| PR CI: typecheck, 58 unit tests, script syntax checks and Worker build | [44245521279](https://github.com/Nolane-x/Nolane-search/actions/runs/44245521279) | PASS |
| PR #6 CI: typecheck, 61 unit tests, webhook regression check and Worker build | [44255034696](https://github.com/Nolane-x/Nolane-search/actions/runs/44255034696) | PASS |
| Main CI: typecheck, 61 unit tests, webhook regression check and Worker build | [44255150160](https://github.com/Nolane-x/Nolane-search/actions/runs/44255150160) | PASS |
| Worker bundle export and production smoke test | [44255150131](https://github.com/Nolane-x/Nolane-search/actions/runs/44255150131) | PASS |
| Production Worker deployment, runtime secret upload, webhook and command registration | [44255150124](https://github.com/Nolane-x/Nolane-search/actions/runs/44255150124) | PASS |

The deployment log confirms:
- Worker `nolane-search` was uploaded and deployed.
- Runtime `AI_ROUTER_CONFIG` was uploaded as a hidden secret.
- Cron `*/30 * * * *` and Queue producer/consumer bindings remained attached.
- Telegram webhook registration succeeded.
- Telegram bot command registration succeeded, including `/web`, `/start`, `/menu` and `/cancel`.
- Worker version `e182d473-d214-4a0c-82c5-0c8662fb4b87` was deployed from main commit `ffe1564ebfa1db5a00960c92e88e19dc6a84fb20`.
- Telegram webhook update subscriptions were verified by calling `getWebhookInfo`; the returned configuration contains both `message` and `callback_query` for the expected Worker URL.
- No D1 migration was needed for the Telegram callback fix.
- Worker version `ccbb1cb9-3d89-4290-a471-92c44a333711` was deployed from main commit `1c17cd1e77a5b83fc57a0ed86e9ace595f58d31e`.
- No D1 migration was needed; the deployment's migration check correctly skipped the migration apply step.

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

## Telegram interactive workspace

- `/start`, `/menu` and `/home` send the inline dashboard for the allowlisted owner in the private chat.
- The dashboard provides one-tap Web, AI Chat, AI with sources, Deep Research, Technology, News, GitHub, Wikipedia and personal-site modes, plus status/help and a link to the existing browser workspace.
- Selecting a mode edits the dashboard message to show an input prompt and stores a per-user/per-chat pending mode in D1 `search_cache` for 10 minutes.
- The next plain-text message atomically consumes that pending mode once. Without a pending mode, plain text retains the old default Web Search behavior. Slash commands cancel pending mode; `/cancel` clears it and returns to the dashboard.
- Search results keep existing five-item pagination and now include inline follow-ups for source-grounded AI (`/ask`) and Deep Search (`/deep`) using the original query from the owner's 15-minute search session.
- UI and follow-up callbacks validate the allowlisted user and private chat. Dashboard navigation edits the same message to reduce chat clutter.
- This release reuses the existing D1 cache; no schema migration or new API secret was introduced.
- CI verifies formatting, callback construction and Worker build. A real Telegram tap-through still requires the owner's account.

## Telegram callback delivery repair

- Root cause of the stuck inline buttons: the previous webhook registration explicitly allowed only `message` updates. Inline keyboard taps arrive as `callback_query`, which Telegram therefore did not forward to the Worker.
- `scripts/set-webhook.mjs` now registers both `message` and `callback_query`, then calls Telegram `getWebhookInfo` and fails unless the expected webhook URL and callback subscription are present.
- The Worker acknowledges an allowlisted callback with `answerCallbackQuery` before D1 deduplication or callback work, so Telegram's loading indicator is not held open by slow storage.
- Callback handlers no longer issue late/double acknowledgements. If a callback is acknowledged but processing fails, the Worker sends an actionable chat message.
- Automated regression test verifies acknowledgement occurs before the first D1 operation; a standalone Node check verifies the webhook script subscribes to and verifies callback updates.
- Production deploy 2026-11-18 verified the configured webhook through Telegram `getWebhookInfo`; a real owner tap-through is still the final UI end-to-end check.

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

PR #3 and PR #4 did not introduce new D1 migrations; both reuse the existing indexed_pages/FTS5 schema, search_cache and Queue.

The new migration creates `web_login_tickets`, `web_sessions` and `web_rate_limits`, plus supporting indexes. All three tables and the migration record were queried after applying the migration.

### D1 permission handling

The first automatic deployment attempt found that `CLOUDFLARE_API_TOKEN` can deploy Workers but is not authorized for D1 Query API calls (HTTP 403). The migration was then successfully applied and verified directly against the connected Cloudflare D1 database. A subsequent Worker deployment succeeded with the migration step skipped because the migration had already been applied.

The deploy workflow now separates permissions:
- `CLOUDFLARE_API_TOKEN`: Worker deployment and Queue configuration.
- `CLOUDFLARE_D1_API_TOKEN`: optional separate token with Account → D1 → Edit, required only when a future changed migration needs to run.

Create the second secret before the next commit that introduces a new file under `database/migrations/`. Ordinary code deployments do not need the D1 token.

## Remaining owner-level end-to-end checks

These need a real interaction from the owner's Telegram account; CI and the public health endpoint cannot complete them:
1. Send `/start` or `/menu` in the private Telegram chat and tap Web Search, AI Chat, or AI with sources. The button should respond immediately and edit the dashboard prompt; it must no longer show an endless loading spinner.

1. Send `/start` or `/menu` in the private bot chat; try each dashboard mode, send one query, test `/cancel`, and confirm that the next unselected plain-text message falls back to Web Search.
2. From a search result, use the AI-with-sources and Deep Search buttons; confirm only the matching original query is used and that the job appears in `/jobs`.

1. Open the private Telegram chat and send `/web`. Open the returned one-time link and confirm browser login works, then test logout and a fresh login link.
2. Try `/crawl https://your-own-public-site.example 10` on a website you control, then use `/crawls` and search its contents with `/local` or Website của tôi. Confirm only permitted pages are indexed.
3. Use Personal Web Index in the browser to enqueue a small crawl and refresh its status.
4. Vote helpful/not-helpful on a few search results, then repeat the exact same query to observe the small ranking nudge.
5. Run a browser search in Web, News, Research and GitHub categories. Confirm results open and the result count / timing are sensible.
6. Use AI Overview on a current topic and check that inline source numbers correspond to the linked sources.
7. Send a few chat messages to verify conversation continuity and verify that chat does not claim it performed live web search.
8. Run `/ai_status`, then one low-cost `/ai fast ...` request to verify live API-key acceptance. Test failover only if needed; it can spend provider quota.
9. Try a 20-result Telegram search pagination case, `/deep`, `/read`, `/watch` and archive delivery.
No API key, bot token, webhook secret or session token should be pasted into chat, committed to the repository, or included in screenshots/logs.
