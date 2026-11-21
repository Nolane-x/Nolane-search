# Verified Project Status

Last verified: 2026-11-21. This document distinguishes production deployment and configuration checks from user-level behavior that still requires a real Telegram interaction.

## Repository and production release

- Repository: https://github.com/Nolane-x/Nolane-search
- Default branch: `main`
- Latest production source commit: `a685b9853b86b196b29805f6490ebd37d0144033`
- Browser search and retrieval upgrade: [PR #2](https://github.com/Nolane-x/Nolane-search/pull/2)
- Bounded site indexing and search feedback: [PR #3](https://github.com/Nolane-x/Nolane-search/pull/3)
- Hybrid personal-index retrieval and sitemap crawler upgrade: [PR #4](https://github.com/Nolane-x/Nolane-search/pull/4)
- Interactive Telegram workspace and contextual search actions: [PR #5](https://github.com/Nolane-x/Nolane-search/pull/5)
- Fix Telegram callback delivery and stuck inline-button spinners: [PR #6](https://github.com/Nolane-x/Nolane-search/pull/6)
- Lightweight Personal Memory, AI efficiency, request-body limits and usage visibility: [PR #7](https://github.com/Nolane-x/Nolane-search/pull/7)
- Register Personal Memory commands in Telegram's slash-command menu: [PR #8](https://github.com/Nolane-x/Nolane-search/pull/8)
- Provider response limits, watch redirect isolation and TinyFish URL validation: [PR #9](https://github.com/Nolane-x/Nolane-search/pull/9)
- Personal Web Index manager in Web and Telegram, including safe removal and watch deactivation: [PR #10](https://github.com/Nolane-x/Nolane-search/pull/10)
- Telegram and Web per-minute usage caps introduced by [PR #11](https://github.com/Nolane-x/Nolane-search/pull/11) were removed by [PR #12](https://github.com/Nolane-x/Nolane-search/pull/12); Personal Web Index federation was added in the same release.
- Production Worker: https://nolane-search.nolane-file.workers.dev
- Cloudflare Worker version ID: `519bee0c-6f42-4c76-bcfb-d86c546040ac` (version 58; 100% traffic)

The release adds a private browser search portal, AI Overview, multi-turn chat, multi-signal federated retrieval ranking, relevance-aware provider fallback, AI-assisted Deep Search query planning, owner-controlled bounded site indexing, title-weighted BM25 retrieval over the personal FTS5 index, recursive same-origin sitemap discovery, semantic article/main extraction per-result helpful/not-helpful feedback, an interactive Telegram dashboard with one-shot search/AI modes and contextual search follow-ups, plus a verified Telegram callback webhook and immediate callback acknowledgement.

## Wave 7 production release — 2026-11-21 (superseded by Wave 8 below)

- PR #45 ([261-tool Wave 7](https://github.com/Nolane-x/Nolane-search/pull/45)) was merged into `main`.
- Main commit: `35a33c5b52901e3b3dc1e8471dae18fb9ba4a5c8`.
- Production Worker version 56: `4f33b8bb-47db-4645-b58d-46899021030e`; deployment run [44873192198](https://github.com/Nolane-x/Nolane-search/actions/runs/44873192198) succeeded.
- Main CI [44873192204](https://github.com/Nolane-x/Nolane-search/actions/runs/44873192204) passed type-check, unit tests, deployment-script checks, Python runner tests and Worker build.
- Worker bundle export and production smoke test [44873192195](https://github.com/Nolane-x/Nolane-search/actions/runs/44873192195) passed.
- Telegram deployment verification confirmed both `message` and `callback_query` webhook updates and successful command-menu registration.
- Wave 7 adds 14 processors and raises the catalog from 247 to 261: developer/network text, CSV-to-SQL/YAML, CSV reports and JSON cleanup/type/nesting utilities.
- D1 migrations verified in `schema_migrations`: `0001_core.sql`, `0002_deep_search_jobs.sql`, `0003_web_portal.sql`, `0004_remove_request_rate_limits.sql`. No new migration was needed for Wave 7.
- Read-only D1 inspection confirmed `indexed_pages` (1 row), `watches` (2 rows), `telegram_updates` (55 rows), and the existing tool/search/job tables. Cloudflare's D1 metadata `num_tables` field returned 0 even though `sqlite_master` lists the existing tables; direct SQLite inspection is the authoritative check here.
- Still pending owner-level verification: send a real small text/CSV/JSON file to the Telegram bot, receive the processed output, exercise a safe retry, and confirm optional archive-channel delivery. CI and webhook registration do not prove the full user interaction.

## Wave 8 production release — 2026-11-21 (superseded by Wave 9 below)

- PR #47 ([Configuration and DevOps suite](https://github.com/Nolane-x/Nolane-search/pull/47)) was merged into `main`.
- Main commit: `4b7db4f7eaaae44810df68d43ae3c9486187dbb6`.
- Production Worker version 57: `a86e4cb5-3747-4476-b87e-31abb6793062`; Cloudflare deployment distribution is 100% on this version.
- Main CI [44874848990](https://github.com/Nolane-x/Nolane-search/actions/runs/44874848990) passed type-check, 188 unit tests, deployment-script checks, 94 Python runner tests and Worker build.
- Cloudflare build/export and production Worker smoke test [44874849018](https://github.com/Nolane-x/Nolane-search/actions/runs/44874849018) passed.
- Production deployment [44874848974](https://github.com/Nolane-x/Nolane-search/actions/runs/44874848974) passed runtime-secret upload and Telegram webhook/command-menu registration. Webhook `message` and `callback_query` were verified with `getWebhookInfo`.
- Wave 8 adds 14 tools to the 261-tool Wave 7 catalog, giving 275 unique catalog IDs. New groups cover dotenv safety, INI/TOML/Java Properties, Dockerfile/Compose, Python requirements, package.json, gitignore and environment-variable references.
- Ten Wave 8 processors are enabled for bounded direct AI text processing. TOML, Java Properties and Docker Compose YAML parsing run in the isolated file runner; do not claim they are all direct chat parsers.
- No D1 schema change was included. Deployment correctly skipped migration application; read-only `schema_migrations` inspection still shows `0001_core.sql` through `0004_remove_request_rate_limits.sql`, and the existing tables remain present.
- ENV audit/reference reports expose names and counts, not secret values. Docker and dependency audits are static; they do not build/run containers, install packages, execute scripts or query vulnerability registries.
- Remaining owner-level check: upload a small real `.env`, `.ini`, `.toml`, `compose.yaml` and `.properties` file through Telegram, inspect returned artifacts, and test a safe retry. This has not been exercised by CI, webhook checks or this deployment.

## Latest production release — Wave 9 — 2026-11-21

- PR #49 ([Infrastructure and CI/CD security auditors](https://github.com/Nolane-x/Nolane-search/pull/49)) was merged into `main`.
- Main commit: `a685b9853b86b196b29805f6490ebd37d0144033`.
- Production Cloudflare Worker version 58: `519bee0c-6f42-4c76-bcfb-d86c546040ac`; latest deployment distribution is 100% on this version.
- Main CI [44880518949](https://github.com/Nolane-x/Nolane-search/actions/runs/44880518949) passed TypeScript type-check, 21 test files / 190 unit tests, deployment-script checks, 96 Python runner tests and Worker build.
- Cloudflare export/build and deployed Worker smoke test [44880518912](https://github.com/Nolane-x/Nolane-search/actions/runs/44880518912) passed.
- Production deployment [44880519016](https://github.com/Nolane-x/Nolane-search/actions/runs/44880519016) passed bundle validation, runtime-secret upload and Telegram webhook/command registration. D1 migration step was skipped because Wave 9 changes no schema.
- Telegram webhook was verified for `message` and `callback_query`; the bot command menu was registered successfully.
- Wave 9 adds eight auditors to the 275-tool Wave 8 production catalog, bringing production to 283 unique tools: GitHub Actions, Kubernetes, Terraform, Nginx, Apache, Caddy, systemd and shell.
- Six text-only auditors (Terraform, Nginx, Apache, Caddy, systemd and shell) are available through bounded direct AI processing. GitHub Actions and Kubernetes YAML audits remain runner-based and use YAML parsing.
- Audits are static heuristics: no workflow dispatch, cluster access, terraform init/plan/apply, server/service startup or shell execution. Credential values are omitted from reports.
- Read-only D1 inspection confirms migrations `0001_core.sql` through `0004_remove_request_rate_limits.sql` and the existing SQLite tables. Cloudflare's summary `num_tables` field may return 0; `sqlite_master` inspection is authoritative.
- Still pending owner-level verification: send real `.tf`, `.yaml`, `.conf`, `.service` and `.sh` files through Telegram, inspect returned artifacts and test a safe retry. CI/webhook registration does not prove the complete user interaction.

## CI and deployment verification

| Check | Run | Result |
|---|---:|---|
| PR CI: typecheck, 58 unit tests, script syntax checks and Worker build | [44245521279](https://github.com/Nolane-x/Nolane-search/actions/runs/44245521279) | PASS |
| PR #6 CI: typecheck, 61 unit tests, webhook regression check and Worker build | [44255034696](https://github.com/Nolane-x/Nolane-search/actions/runs/44255034696) | PASS |
| Main CI: typecheck, 61 unit tests, webhook regression check and Worker build | [44255150160](https://github.com/Nolane-x/Nolane-search/actions/runs/44255150160) | PASS |
| Worker bundle export and production smoke test | [44255150131](https://github.com/Nolane-x/Nolane-search/actions/runs/44255150131) | PASS |
| Production Worker deployment, runtime secret upload, webhook and command registration | [44255150124](https://github.com/Nolane-x/Nolane-search/actions/runs/44255150124) | PASS |
| PR #7 CI: typecheck, 72 unit tests, webhook checks and Worker build | [44270510551](https://github.com/Nolane-x/Nolane-search/actions/runs/44270510551) | PASS |
| PR #7 main CI | [44270643224](https://github.com/Nolane-x/Nolane-search/actions/runs/44270643224) | PASS |
| PR #7 Worker bundle export and production smoke test | [44270643846](https://github.com/Nolane-x/Nolane-search/actions/runs/44270643846) | PASS |
| PR #7 production deployment | [44270643085](https://github.com/Nolane-x/Nolane-search/actions/runs/44270643085) | PASS |
| PR #8 CI: Telegram slash-command registration | [44271133530](https://github.com/Nolane-x/Nolane-search/actions/runs/44271133530) | PASS |
| PR #8 main CI: 72 tests and Worker build | [44271236172](https://github.com/Nolane-x/Nolane-search/actions/runs/44271236172) | PASS |
| PR #8 Worker bundle export and production smoke test | [44271236099](https://github.com/Nolane-x/Nolane-search/actions/runs/44271236099) | PASS |
| PR #8 production deployment and Telegram command registration | [44271236228](https://github.com/Nolane-x/Nolane-search/actions/runs/44271236228) | PASS |
| PR #9 CI: typecheck, 78 unit tests, webhook checks and Worker build | [44274411447](https://github.com/Nolane-x/Nolane-search/actions/runs/44274411447) | PASS |
| PR #9 main CI: 78 unit tests and Worker build | [44274472317](https://github.com/Nolane-x/Nolane-search/actions/runs/44274472317) | PASS |
| PR #9 Worker bundle export and production smoke test | [44274472497](https://github.com/Nolane-x/Nolane-search/actions/runs/44274472497) | PASS |
| PR #9 production deployment and Telegram command registration | [44274472339](https://github.com/Nolane-x/Nolane-search/actions/runs/44274472339) | PASS |
| PR #10 CI: typecheck, 84 unit tests, webhook checks and Worker build | [44283578933](https://github.com/Nolane-x/Nolane-search/actions/runs/44283578933) | PASS |
| PR #10 main CI: 84 unit tests and Worker build | [44283762795](https://github.com/Nolane-x/Nolane-search/actions/runs/44283762795) | PASS |
| PR #10 Worker bundle export and production smoke test | [44283762813](https://github.com/Nolane-x/Nolane-search/actions/runs/44283762813) | PASS |
| PR #10 production deployment and Telegram command registration | [44283763167](https://github.com/Nolane-x/Nolane-search/actions/runs/44283763167) | PASS |
| PR #12 CI: type-check, 87 unit tests, webhook checks and Worker build | [44295647765](https://github.com/Nolane-x/Nolane-search/actions/runs/44295647765) | PASS |
| PR #12 main CI: 87 unit tests and Worker build | [44296385809](https://github.com/Nolane-x/Nolane-search/actions/runs/44296385809) | PASS |
| PR #12 Worker bundle export and smoke test | [44296385774](https://github.com/Nolane-x/Nolane-search/actions/runs/44296385774) | PASS |
| PR #12 production deployment and Telegram webhook/command registration | [44296385765](https://github.com/Nolane-x/Nolane-search/actions/runs/44296385765) | PASS |

The deployment log confirms:
- Worker `nolane-search` was uploaded and deployed.
- Runtime `AI_ROUTER_CONFIG` was uploaded as a hidden secret.
- Cron `*/30 * * * *` and Queue producer/consumer bindings remained attached.
- Telegram webhook registration succeeded.
- Telegram bot command registration succeeded, including `/web`, `/start`, `/menu` and `/cancel`.
- Worker version `e182d473-d214-4a0c-82c5-0c8662fb4b87` was deployed from main commit `ffe1564ebfa1db5a00960c92e88e19dc6a84fb20` (PR #6 callback repair).
- Worker version `40974932-b150-4373-995a-ea73facd13ad` deployed PR #7; Worker version `6eaac094-1dbe-494d-9393-ef0a66e94ddb` deployed PR #8 command-menu update; Worker version `a2c2372a-6f95-43f6-9839-9bbf5f7acb0e` deployed PR #9 upstream/redirect hardening.
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
- The private single-owner service has no application-level per-minute request caps. Provider billing/quotas and Cloudflare platform capacity remain external constraints.
- POST requests are same-origin checked; JSON bodies are capped at 30 KB.
- Logout revokes the server-side session. Scheduled cleanup removes expired tickets and sessions.
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
- Personal Web Index results are also federated into ordinary Web, Technology and Research search (and therefore into AI Overview and Telegram `/ask` evidence). Dedicated GitHub and Wikipedia modes remain isolated from private-index content.
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
- `0004_remove_request_rate_limits.sql`

PR #3 and PR #4 did not introduce new D1 migrations; both reuse the existing indexed_pages/FTS5 schema, search_cache and Queue.

`0003_web_portal.sql` originally created `web_login_tickets`, `web_sessions` and `web_rate_limits`. PR #12 applied `0004_remove_request_rate_limits.sql`, removed `idx_web_rate_limits_expiry` and `web_rate_limits`, and recorded the migration. A live `sqlite_master` query returned no remaining objects with either obsolete name.

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


## Personal Memory and efficiency controls — deployed 2026-11-18

PR #7 added the bounded Personal Memory and AI efficiency improvements; PR #8 completed Telegram slash-command registration. Both are merged into `main` and deployed in Worker version `6eaac094-1dbe-494d-9393-ef0a66e94ddb`.

- Personal Memory reuses D1 `search_cache`; no new table, migration, Cloudflare service or secret is required. Each Telegram user can store at most 50 explicitly saved entries, with a five-year expiry. Categories are profile, preference, project and note.
- Telegram commands `/remember`, `/memories` and `/forget` are registered in the bot command menu. Memory is opt-in: the assistant does not automatically extract private conversation content.
- Telegram `/ai` and browser `/api/chat` retrieve at most three relevant saved memories as optional context.
- Browser chat history is bounded to at most eight valid turns and 8,000 aggregate characters before model submission. This is a character-based context budget, not an exact tokenizer count.
- AI Overview and Telegram `/ask` share a short D1 synthesis cache: two minutes for news/current queries, five minutes for research and ten minutes for other modes.
- AI Router defaults to three provider/model attempts per completion and clamps configured attempts to six. Recently failing routes receive a short per-isolate cooldown; it is best-effort and resets when an isolate is replaced.
- Web POST JSON request bodies are read as a stream and capped at 30 KB; oversized bodies are cancelled and rejected.
- Browser AI Overview and chat surface cache, latency, input/output token and estimated-cost metadata when the provider returns those usage fields.
- Final main CI passed type-check, all 72 unit tests, webhook checks and Worker build. The export smoke test and production deployment succeeded.
- Post-deploy `GET /health` returned `ok: true`, `database: reachable`, four AI provider-key routes and nine model routes. Brave is optional and is not configured.
- Deployment log confirms Telegram webhook subscriptions for `message` and `callback_query`, and successful registration of the bot command list.

Automated tests, command registration and live health checks are verified. A real user-level Telegram interaction with `/remember`, `/memories`, `/forget` and a personalized `/ai` prompt remains an owner-side end-to-end check.


## Provider and website-fetch hardening — deployed 2026-11-18

PR #9 is merged into `main` and deployed in Worker version `a2c2372a-6f95-43f6-9839-9bbf5f7acb0e`.

- Provider and Telegram Bot API JSON responses are consumed through a streaming reader with a 1 MB decoded-body cap. Declared oversized responses are rejected early; streaming bodies are cancelled once the cap is exceeded. Malformed and empty JSON responses become controlled failures.
- Website Watch redirects are constrained to the original public HTTPS origin. A monitored URL cannot redirect this Worker to another host. Redirect response bodies are cancelled before following a permitted same-origin redirect.
- The site crawler retains same-origin redirect enforcement and now cancels redirect bodies before following.
- TinyFish Fetch results are associated only with safe public URLs that were included in the request. Unsafe or unrelated result URLs are ignored; unsafe final URLs are not used as lookup keys.
- The `/status` cache count query had a duplicate exclusion removed.
- PR #9 CI passed type-check, all 78 tests, webhook checks and Worker build. Main CI, Worker export/smoke test and production deployment all passed.
- The deploy skipped D1 migration because no schema changed. Queue bindings, Cron and Telegram commands/webhook were retained and re-verified.
- Post-deploy `GET /health` returned `ok: true` and `database: reachable`; the configured provider inventory remains four AI key routes and nine model routes.

The watch redirect change is intentionally stricter: a site that redirects to another hostname will now be reported as a fetch failure. Update its watch target to the canonical destination if cross-host redirects are part of the site's normal behavior.


## Personal Web Index management — deployed 2026-11-18

PR #10 is merged into `main` and deployed in Worker version `74f6a6d4-c91b-4c68-b94d-b65fb152aeea`.

- The private Web Workspace Personal Web Index panel lists recently updated pages, supports filtering by title/URL/domain, and paginates through the saved page list.
- Each page can be removed individually. A domain removal deletes pages for the exact hostname, its `www` alias and subdomains.
- Browser management endpoints are private behind the existing one-time Telegram login / Web session. Destructive POST requests retain the same-origin guard.
- Telegram commands: `/indexed [filter]`, `/unindex https://example.com/page`, and `/unindex_domain example.com`. The commands are included in Telegram's registered slash-command menu and `/help`.
- A deletion removes the FTS5 row and `indexed_pages` source row in one D1 batch, and deactivates any watch whose normalized URL is among the removed pages. Crawl-job history and Telegram archive snapshots are retained.
- A crawl job already in flight is not cancelled; it can write a page after a removal completes. Refresh the index and remove again if that happens.
- No schema migration, new Cloudflare service, paid API or new secret was required. Deployment confirmed `D1 migration required: false`; Queue/Cron bindings were retained, Telegram webhook and command registration succeeded.
- PR CI and main CI passed type-check, all 84 tests, webhook checks and Worker build. Worker export/smoke and production deployment passed.
- Post-deploy `GET /health` returned `ok: true` and `database: reachable`; configured AI routes remain four provider-key routes and nine model routes.

An owner-side browser/Telegram interaction is still needed to verify the visible list and destructive controls against the owner's real stored pages. Automated authorization, pagination, validation and deletion-batch behavior are covered by tests.


## Request-cap removal and Personal Web Index federation — deployed 2026-11-18

PR #12 was merged at `fe988bdbeb4c5c7095c06b03c9f2b08485582d39`. The final Worker deployment was built from main commit `b12aa461af2bb8f366671edc07821ef5549ccf90` and is running Worker version `26f16ed2-8133-457b-a77c-59c93b269a47`.

- Per-minute application-level usage caps have been removed from Telegram commands and authenticated Web Workspace endpoints. The private single-owner bot and browser portal no longer reject `/ai`, `/ask`, `/deep`, `/crawl`, search, or feedback actions due to an app-level request counter.
- D1 migration `0004_remove_request_rate_limits.sql` was applied directly through the connected Cloudflare D1 session after the GitHub D1 migration token was found to be absent. The `web_rate_limits` table and `idx_web_rate_limits_expiry` index were dropped, and migration `0004` was inserted into `schema_migrations`; follow-up `sqlite_master` verification returned no obsolete objects.
- The subsequent GitHub deployment correctly detected `D1 migration required: false`, deployed the Worker, verified Telegram webhook subscriptions for `message` and `callback_query`, and registered the current bot command list.
- Provider-owned quotas/billing, Cloudflare platform limits and Queue capacity still apply. A single website crawl remains bounded to 20 pages per job and keeps the HTTPS/public-host, same-origin and robots.txt safety checks; those are execution/security bounds, not request throttles.
- Personal Web Index FTS5/BM25 results are federated into Web, Technology and Research search. Dedicated GitHub/Wikipedia modes remain isolated; Local remains a direct personal-index lookup. Shared search means AI Overview and Telegram `/ask` can now use indexed personal pages as evidence.
- PR CI and main CI passed type-check, all 87 tests across 14 files, webhook checks and Worker build. Worker export/smoke test and production deployment passed.
- Production `GET /health` returned `ok: true` and `database: reachable`; provider inventory remains Tavily, Exa, TinyFish, GitHub and OpenRouter, with four AI key routes and nine model routes.

The automated behaviors and production release are verified. Real Telegram interaction and browser login still require an owner-side end-to-end check.


## Nolane Tools · implementation under PR #13

The first Tools release is being added in PR #13.

- A registry of 17 implemented tools spans image/OCR, PDF/Office, audio/video, data and utility categories.
- Telegram file uploads automatically select a compatible tool (photos default to Vietnamese/English OCR); `/tool TOOL_ID` can override the next upload.
- The private Web Workspace includes a Tools catalog and personal job history. File uploads are initially handled from the Telegram chat.
- GitHub Actions runs the actual Python processing on ephemeral hosted Ubuntu runners. Worker D1 stores metadata/status in the existing `search_cache`; the runner downloads inputs directly from Telegram and sends output files back, without committing files or using R2.
- A fine-grained `GITHUB_ACTIONS_TOKEN` with repository Actions: Read and write is required before live dispatch works. It is documented in `docs/SECRETS.md`; it must be saved as a GitHub Actions secret, not pasted into chat.
- OCR installs English and Vietnamese Tesseract data; audio transcription uses CPU Whisper; document extraction includes OCR fallback for scanned PDFs.
- CI includes registry/dispatch unit tests plus Python syntax checking. Actual hosted-runner execution requires the token to be configured and a real file to be sent from Telegram; that end-to-end run is not claimed until verified.


## Nolane Tools expansion · PR #14

The registry expands from 17 to 23 implemented tools.

- Added text cleanup for TXT/Markdown/log files, SRT/VTT subtitle-to-transcript extraction and HTML-to-readable-text extraction.
- Added audio loudness normalization to podcast-style -16 LUFS, video-to-MP3 audio extraction and a bounded six-second video-to-GIF preview.
- Added MIME/extension inference and dispatch metadata for the new tools. FFmpeg is installed only for the relevant audio/video jobs.
- CI now runs Python unit tests against the runner's text, subtitle and HTML transforms plus mocked FFmpeg command construction, in addition to Python compilation and the TypeScript suite.


## Telegram Archive Index — deployed 2026-11-21

- PR #51 adds the D1 metadata index and owner-scoped `/archive [query]` / `/archive_restore ID` commands; PR #52 adds filename, file size and SHA-256 prefix to each list item.
- Latest source: `6ab8b45e6c85e9b861bbe481eae439f1874fe381`.
- Production Worker version: `c8a21659-d0f0-47eb-aa9e-941e4b94a748`, 100% traffic.
- CI run #249 (`44888520208`) passed; deployment run #105 (`44888609517`) succeeded, including Worker secret upload and Telegram webhook/command registration.
- D1 readback confirms `0005_archive_snapshots.sql` and `archive_snapshots` are present alongside migrations 0001–0004.
- Telegram channel stores snapshot documents; D1 stores owner-scoped message/file references, URL/title/time/hash metadata only. D1 does not store the snapshot body.
- Real private Telegram watch → capture → archive search → restore testing remains owner-level E2E and has not been claimed as verified.
- Configure `CLOUDFLARE_D1_API_TOKEN` with Account > D1 > Edit in GitHub Actions before future commits that add migration files. The first rollout required a direct D1 migration because this secret was absent; that migration was manually applied and verified before the successful source-only deployment.
