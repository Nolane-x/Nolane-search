# Verified Project Status

Last verified: 2026-11-17. This document distinguishes successful deployment and configuration checks from user-level end-to-end behavior that still needs a Telegram message.

## Repository and source

- Repository: https://github.com/Nolane-x/Nolane-search
- Default branch: `main`
- Latest deployed source commit: `e8bae3d4a1635c23306c30ff676fe4993e90ea4a`
- PR #1 merged: https://github.com/Nolane-x/Nolane-search/pull/1
- Source changes include TinyFish Search/Fetch, OpenRouter multi-model fallback, Telegram `/read`, Exa/TinyFish/Brave/Wikipedia federated fallback, free bilingual `/wiki`, Telegram search pagination (five items per page, up to 12 candidates, owner-bound 15-minute sessions), improved token-overlap/domain-diversity ranking, Google-style `site:`, `filetype:`, `intitle:`, `after:` and `before:` operators, and robots.txt-aware website monitoring.

## Latest verification

| Check | Run | Result |
|---|---:|---|
| CI: typecheck, unit tests, script syntax checks, Worker build | [44098353225](https://github.com/Nolane-x/Nolane-search/actions/runs/44098353225) | PASS |
| Export Worker bundle and health smoke test | [44098353255](https://github.com/Nolane-x/Nolane-search/actions/runs/44098353255) | Rerun after runner `ETXTBSY` error |
| Production deployment, secret upload, webhook and command registration | [44098353347](https://github.com/Nolane-x/Nolane-search/actions/runs/44098353347) | PASS |

The production deployment completed with Worker version ID `eed80315-03a0-4702-9ba6-33a59de35780`. GitHub Actions confirmed:
- Worker uploaded successfully using the repository source and configured runtime secrets.
- The deployed version includes Telegram five-result pages with owner-bound inline pagination, the free bilingual Wikipedia provider/mode, and local enforcement for the Google-style search operators.
- The public `/health` endpoint was fetched after deployment and returned `ok: true` and `database: reachable`.
- CI passed with 35 unit tests, type-check, script syntax checks and Worker build. The export workflow hit an `esbuild` `ETXTBSY` during dependency installation on the first run; the failed job was requested to rerun.
- Production `/health` was fetched after deployment and returned `ok: true`, `database: reachable`, and all expected configured providers (Tavily, Exa, TinyFish, OpenRouter with six model IDs); Brave remained optional and unconfigured.
- D1 and Queue bindings are attached.
- Main Queue and DLQ consumers plus the 30-minute Cron trigger are registered.
- Telegram webhook registration succeeded.
- Telegram command registration succeeded, including `/read` and `/status`.

## Live Worker health

Worker: https://nolane-search.nolane-file.workers.dev

The deployed `/health` endpoint was fetched after the latest deployment and returned:
- `ok: true`
- `database: reachable`
- Tavily: configured
- Exa: configured
- TinyFish: configured
- OpenRouter: configured with **6 model IDs**
- Telegram archive: configured
- Brave: not configured (optional)
- GitHub: public search path enabled; no optional GitHub token was supplied in the latest deployment

This verifies Worker reachability, D1 connectivity and runtime binding presence. It does not prove that every external provider key is accepted by its provider or that every Telegram command has been exercised end-to-end. The latest provider hardening also rejects search-result URLs containing embedded username/password credentials and avoids associating TinyFish Fetch content with a request URL unless the provider identifies that URL.

## Cloudflare resources

Account ID: `1172c01120a2470aa12f81e5b4778556`

| Resource | Name | ID / details | State |
|---|---|---|---|
| Worker | `nolane-search` | https://nolane-search.nolane-file.workers.dev | Deployed |
| D1 | `nolane-search-db` | `4f6a8cbd-cc8c-42b9-be6a-ed45c709d3db` | APAC; reachable |
| Main Queue | `nolane-search-jobs` | `8a09dc04a6824faaa90f379f45f75ac0` | Producer and consumer attached |
| Dead-letter Queue | `nolane-search-dlq` | `e44fe78242614ed1b448dbea7dbe94e0` | Consumer attached |
| Cron | `*/30 * * * *` | Every 30 minutes | Active |
| R2 | — | — | Not enabled; not required |
| KV | — | — | Not used |

### D1 schema

The live `schema_migrations` table confirms:
- `0001_core.sql`
- `0002_deep_search_jobs.sql`

Both were already applied. No new D1 migration was required for the latest feature release.

## Provider implementation

- Tavily: primary web/news search.
- Exa: semantic/research discovery.
- TinyFish Search: web, technology, research and news discovery; source intent is expressed through documented query/location/language parameters.
- TinyFish Fetch: extracts page content; used by `/read https://...` and to enrich up to five Deep Search sources.
- OpenRouter: synthesis with ordered model fallback through `OPENROUTER_MODELS`; legacy `OPENROUTER_MODEL` remains supported. The parser accepts up to eight model IDs and the current health endpoint reports six configured IDs.
- GitHub: public repository search works without an optional token; `GITHUB_TOKEN_SEARCH` can raise rate limits.
- Google-style filters: `site:`, `filetype:`, `intitle:`, `after:` and `before:` are parsed and enforced locally. Site matching includes subdomains but not lookalike suffixes; filetype matches URL path extension; date filters use strict boundaries and drop records with unknown publication dates. Only ISO `YYYY-MM-DD` is accepted.
- General `/search`: Tavily is the primary provider. If it fails or returns fewer than four results, configured Exa, TinyFish, Brave and free Wikipedia providers are queried in parallel and merged before ranking. This reduces unnecessary calls on healthy full Tavily responses.
- `/wiki`: public MediaWiki Action API lookup, with Vietnamese diacritics selecting Vietnamese Wikipedia and other queries defaulting to English. Wikipedia is a reference/overview source, not a current-news or primary-evidence source.
- Telegram result pagination: up to 12 candidates, five shown at a time, D1 session TTL 15 minutes, callbacks checked against both allowlisted user ID and chat ID. Session keys use `telegram-search:`.
- Website Watch: each origin's robots.txt is checked before the watched page is fetched. Applicable groups are combined, longest-match wins, and Allow wins an equal-length tie. A blocked target is shown as `robots disallow`; an unreadable/temporarily unavailable policy is deferred and shown as `robots unavailable · deferred`.
- Brave: optional and currently not configured.

## Deployment workflow behavior

- Routine deployments skip D1 migration calls when no files under `database/migrations/` changed.
- Manual `workflow_dispatch` exposes an `apply_migrations` input. Enable it only when a new migration is present and the Cloudflare token has Account > D1 > Edit.
- The deployment uses `cf deploy --force` because the existing Worker had previously been updated through the Script API; this makes the Git repository source the deployment source of truth.
- Optional `BRAVE_SEARCH_API_KEY` and `GITHUB_TOKEN_SEARCH` are not required to deploy when absent.

The GitHub Actions Cloudflare token previously received HTTP 403 from the D1 Query API. Routine deployments now skip migrations when no migration file changed; this is safe for the current schema because both live migrations were verified as applied. If a future commit adds a D1 migration, the token must have Account > D1 > Edit in addition to the Worker and Queue permissions documented in `docs/SECRETS.md`.

## Remaining end-to-end checks

These need a real message from the owner's Telegram account; they cannot be truthfully marked complete from CI or health checks alone:
- Send `/start`, `/help` and `/status`; confirm the bot responds.
- Try `/search Cloudflare Workers` and tap Next/Previous when multiple pages appear; test `/search cloudflare site:developers.cloudflare.com`, `/search workers filetype:pdf`, `/search AI after:2026-01-10 before:2026-02-01`, `/wiki trí tuệ nhân tạo`, `/wiki artificial intelligence`, `/research small language models`, `/read https://example.com` and `/deep compare open-source search engines`.
- Confirm the six configured OpenRouter model IDs are valid and that fallback occurs when a model is unavailable.
- Confirm archive delivery to the configured Telegram archive chat.
- Test `/watch https://example.com`, then verify a later change notification.
- Exercise Deep Search Queue retry and DLQ behavior under an induced failure.

Do not paste API keys, bot tokens, webhook secrets or other credentials into chat, source files, issues or logs.
