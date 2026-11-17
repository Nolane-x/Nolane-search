# Verified Project Status

Last verified: 2026-11-17. This document distinguishes successful deployment and configuration checks from user-level end-to-end behavior that still needs a Telegram message.

## Repository and source

- Repository: https://github.com/Nolane-x/Nolane-search
- Default branch: `main`
- Latest deployed source commit: `0b2f3b9bca33d9fed7dffe3c915ad4ed0fc8945a`
- PR #1 merged: https://github.com/Nolane-x/Nolane-search/pull/1
- Source changes include TinyFish Search/Fetch, OpenRouter multi-model fallback, Telegram `/read`, deployment fixes, and expanded tests.

## Latest verification

| Check | Run | Result |
|---|---:|---|
| CI: typecheck, unit tests, script syntax checks, Worker build | [44078400343](https://github.com/Nolane-x/Nolane-search/actions/runs/44078400343) | PASS |
| Export Worker bundle and health smoke test | [44078400338](https://github.com/Nolane-x/Nolane-search/actions/runs/44078400338) | PASS |
| Production deployment, secret upload, webhook and command registration | [44078400367](https://github.com/Nolane-x/Nolane-search/actions/runs/44078400367) | PASS |

The production deployment completed with Worker version ID `d13ffe93-6335-4113-b0c7-b7c7b62a979e`. GitHub Actions confirmed:
- Worker uploaded successfully using the repository source and configured runtime secrets.
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
- Try `/search Cloudflare Workers`, `/research small language models`, `/read https://example.com` and `/deep compare open-source search engines`.
- Confirm the six configured OpenRouter model IDs are valid and that fallback occurs when a model is unavailable.
- Confirm archive delivery to the configured Telegram archive chat.
- Test `/watch https://example.com`, then verify a later change notification.
- Exercise Deep Search Queue retry and DLQ behavior under an induced failure.

Do not paste API keys, bot tokens, webhook secrets or other credentials into chat, source files, issues or logs.
