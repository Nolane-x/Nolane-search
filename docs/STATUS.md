# Verified Project Status

Last updated: 2026-11-17. This file distinguishes verified live resources from features that still require user credentials or end-to-end testing.

## GitHub

- Repository: https://github.com/Nolane-x/Nolane-search
- Default branch: main
- Latest implementation commit before stale-job recovery: 68655908d7e2484a37dde693191bc22e4566f387
- Repository is public; the connected GitHub integration has admin/push permission.
- `.github/workflows/export-worker.yml` builds the Cloudflare output and publishes it to the `cloudflare-build` branch. A later workflow run performs a live `/health` smoke test.

## CI and deployment checks

| GitHub Actions run | Result | Verified scope |
|---|---|---|
| CI run 44058641961 | PASS | TypeScript type-check, unit tests, Cloudflare build |
| Export + smoke run 44058641881 | PASS | Build output exported to `cloudflare-build`; deployed Worker `/health` returned `ok: true` and database `reachable` |
| Deploy run 44058641901 | BLOCKED | Required-secret validation stopped before GitHub Actions deployment, migration, secret upload or Telegram webhook registration |

The stale-job recovery source change committed after these runs requires a fresh CI/build/export/smoke run. The Worker currently deployed is the last smoke-tested build, not yet the stale-recovery build.

## Cloudflare account

Account ID: `1172c01120a2470aa12f81e5b4778556`

| Resource | Name | ID / details | Verified state |
|---|---|---|---|
| Worker | `nolane-search` | Script tag `c1ef61d64bae4c6a96ed81c738fab9b8` | Uploaded from a verified `cf build` bundle; handlers fetch, queue and scheduled |
| Worker URL | `https://nolane-search.nolane-file.workers.dev` | workers.dev subdomain enabled | Live health smoke test passed |
| D1 | `nolane-search-db` | `4f6a8cbd-cc8c-42b9-be6a-ed45c709d3db` | APAC primary; both migrations applied |
| Main Queue | `nolane-search-jobs` | `8a09dc04a6824faaa90f379f45f75ac0` | Created; Worker consumer attached |
| Dead-letter Queue | `nolane-search-dlq` | `e44fe78242614ed1b448dbea7dbe94e0` | Created; Worker consumer attached |
| Cron | `*/30 * * * *` | Worker schedule | Created and verified |
| Git repository connection | `Nolane-x/Nolane-search` | `71f0889c-6700-4a25-9917-29749083eb09` | Repository connection created; automatic Workers Builds trigger is not yet configured |
| R2 | — | — | Not enabled; excluded from MVP |
| KV | — | — | Not created; not used in MVP |

### D1 schema

Confirmed live in APAC:
- `0001_core.sql`
- `0002_deep_search_jobs.sql`
- `deep_search_jobs` table
- `idx_deep_search_jobs_user_created`
- `idx_deep_search_jobs_status_updated`

The `schema_migrations` table contains both migration names. The D1 database stores watch state, a compact FTS5 index, cache, Telegram update deduplication and Deep Search job metadata.

### Queue consumers

- Main consumer ID: `b0bbd368155949aeba589b36293e3c31`; batch size 3; max retries 3; retry delay 30 seconds; concurrency 1; DLQ configured.
- DLQ consumer ID: `9f634f11f5704620a045c3d9727b1ea5`; batch size 3; max retries 1; retry delay 60 seconds; concurrency 1.

### Worker bindings and secrets

The uploaded Worker has D1 binding `DB` and producer Queue binding `SEARCH_JOBS`. No Telegram or search-provider secrets have been configured on this Worker. Health is therefore available, but Telegram Bot API calls and provider-backed searches are not ready.

## Credentials still awaited from the owner

The repository Deploy workflow expects these exact GitHub Actions secret names:

Required:
- `CLOUDFLARE_API_TOKEN` — for repeatable GitHub Actions deploys and migrations; the current Worker was uploaded through the connected Cloudflare integration instead.
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`
- `TAVILY_API_KEY`

Recommended:
- `ALLOWED_TELEGRAM_USER_IDS`
- `TELEGRAM_ARCHIVE_CHAT_ID`

Optional:
- `EXA_API_KEY`
- `BRAVE_SEARCH_API_KEY`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `GITHUB_TOKEN_SEARCH`

Do not paste secret values into chat, source files, issues or logs. Add them through GitHub repository Settings → Secrets and variables → Actions.

## Not yet verified

- The latest stale-job recovery source patch has not yet passed a new CI/build/export/smoke cycle or been deployed.
- Telegram webhook and command registration.
- Telegram bot replies and owner allowlist.
- Live Tavily, Exa, Brave and OpenRouter API requests.
- Quick Search response delivery to Telegram.
- Deep Search job processing, retry/DLQ and `/jobs` + `/retry` end-to-end.
- Website watch snapshot and subsequent change notification.
- Telegram archive channel permissions and delivery.
- Automatic Workers Builds trigger from Git pushes.

## Release gate

The Worker and D1 health path are deployed and verified. Do not call the Telegram search bot fully live or production-ready until credentials are configured, the webhook is registered, provider-backed search works, a Deep Search job completes, and a website watch produces a baseline and a real change notification.
