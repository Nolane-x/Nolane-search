# Verified Project Status

Last updated: 2026-11-17. This file separates verified live resources from functionality that still depends on owner credentials and end-to-end testing.

## GitHub

- Repository: https://github.com/Nolane-x/Nolane-search
- Default branch: main
- Latest tested source implementation before this feature: 6ca9584732a68d951f13d5cd4a404dd19dd65132
- Latest feature implementation merged: PR #1, head 61674f70559c9091517bcade266cd247f7de1f1b
- Latest repository HEAD: b5dcf0f5140336d6f0d5e469d34b66b2c3015d2e (squash merge of PR #1)
- The repository is public; the connected GitHub integration has admin/push permission.
- .github/workflows/export-worker.yml installs dependencies, type-checks, tests, builds with cf build, verifies the stale-job recovery marker in the compiled bundle, publishes output to cloudflare-build and smoke-tests the live Worker health endpoint.

## CI and deployment checks

| GitHub Actions run | Result | Verified scope |
|---|---|---|
| CI run 44059740938 | PASS | TypeScript type-check, unit tests and Cloudflare build for stale-job recovery implementation |
| CI run 44074939761 | PASS | TypeScript type-check, unit tests including TinyFish/OpenRouter tests, and Cloudflare Worker build for PR #1 |
| Export + smoke run 44059740893 | PASS | Compiled bundle contains stale-job recovery, output exported and live /health returned ok: true with database reachable |
| Deploy run 44059740833 | BLOCKED | Required-secret validation stopped before GitHub Actions deployment, migration, secret upload or Telegram webhook registration |

The currently deployed Worker bundle was built from source commit 6ca9584 and uploaded via the connected Cloudflare integration. The export + smoke run above tested the deployed Worker after that upload. The GitHub Actions Deploy workflow remains unavailable until the owner adds the required secrets.

## Cloudflare account

Account ID: 1172c01120a2470aa12f81e5b4778556

| Resource | Name | ID / details | Verified state |
|---|---|---|---|
| Worker | nolane-search | Script tag c1ef61d64bae4c6a96ed81c738fab9b8; deployment 125a118dab1a425eb2e696aed7600ae5 | Deployed; handlers fetch, queue and scheduled |
| Worker URL | https://nolane-search.nolane-file.workers.dev | workers.dev enabled | Live health smoke test passed |
| D1 | nolane-search-db | 4f6a8cbd-cc8c-42b9-be6a-ed45c709d3db | APAC primary; migrations 0001 and 0002 applied |
| Main Queue | nolane-search-jobs | 8a09dc04a6824faaa90f379f45f75ac0 | Created; Worker consumer attached |
| Dead-letter Queue | nolane-search-dlq | e44fe78242614ed1b448dbea7dbe94e0 | Created; Worker consumer attached |
| Cron | */30 * * * * | Worker schedule | Created and verified |
| Git repository connection | Nolane-x/Nolane-search | 71f0889c-6700-4a25-9917-29749083eb09 | Repository connection created; automatic Workers Builds trigger not configured |
| R2 | — | — | Not enabled; excluded from MVP |
| KV | — | — | Not created; not used in MVP |

### D1 schema

Confirmed live in APAC:
- 0001_core.sql
- 0002_deep_search_jobs.sql
- deep_search_jobs
- idx_deep_search_jobs_user_created
- idx_deep_search_jobs_status_updated

The D1 schema_migrations table contains both migration names. D1 stores watch state, compact FTS5 extracts, search cache, Telegram update deduplication and Deep Search job metadata.

### Queue consumers

- Main consumer ID: b0bbd368155949aeba589b36293e3c31; batch size 3; max retries 3; retry delay 30 seconds; concurrency 1; DLQ configured.
- DLQ consumer ID: 9f634f11f5704620a045c3d9727b1ea5; batch size 3; max retries 1; retry delay 60 seconds; concurrency 1.

### Worker bindings and secrets

At the last verified pre-feature deployment snapshot, the Worker had D1 binding DB and Queue producer binding SEARCH_JOBS. That snapshot did not verify Telegram/provider runtime secrets. PR #1 has since been merged; re-check the Deploy workflow and /health before treating the new provider bindings or Telegram flow as live.

## Expected deployment credentials

The repository Deploy workflow expects these exact GitHub Actions secret names:

Required:
- CLOUDFLARE_API_TOKEN — required for repeatable GitHub Actions deployment/migrations. The currently deployed Worker was uploaded through the connected Cloudflare integration without this GitHub secret.
- TELEGRAM_BOT_TOKEN
- TELEGRAM_WEBHOOK_SECRET
- TAVILY_API_KEY

Recommended:
- ALLOWED_TELEGRAM_USER_IDS
- TELEGRAM_ARCHIVE_CHAT_ID

Optional:
- EXA_API_KEY
- BRAVE_SEARCH_API_KEY
- TINYFISH_API_KEY
- OPENROUTER_API_KEY
- OPENROUTER_MODEL (legacy)
- OPENROUTER_MODELS (ordered fallback list)
- GITHUB_TOKEN_SEARCH

Secret values are masked by GitHub and cannot be inspected through repository source. Confirm configuration through the Deploy workflow and `/health`/`/status`; do not paste secret values into chat, source files, issues or logs.

## New capabilities merged but not yet live-verified

- TinyFish Search is integrated into web fallback, technology, research and news search.
- TinyFish Fetch enriches up to five Deep Search sources and powers the private `/read https://...` command.
- OpenRouter accepts ordered model fallbacks through `OPENROUTER_MODELS`; legacy `OPENROUTER_MODEL` remains supported.
- GitHub Actions deployment now uploads `TINYFISH_API_KEY` and `OPENROUTER_MODELS` when present.
- PR #1 CI passed type-check, unit tests and Cloudflare build. This is build validation, not proof of live API credentials or a production deployment.

## Not yet verified

- Telegram webhook and command registration.
- Telegram bot replies and owner allowlist.
- Live Tavily, Exa, Brave, TinyFish and OpenRouter API requests.
- Quick Search response delivery to Telegram.
- Deep Search Queue processing, retries, DLQ and /jobs + /retry end-to-end.
- Stale-job recovery on an actual interrupted job (source is deployed and build-verified, but no induced failure test has been performed).
- Website watch snapshot and subsequent change notification.
- Telegram archive channel permissions and delivery.
- Automatic Workers Builds trigger from Git pushes.

## Release gate

The Worker, D1 schema, Queue consumers, Cron schedule and health path are deployed and verified. Do not call the Telegram search bot fully live or production-ready until credentials are configured, the webhook is registered, provider-backed search works, a Deep Search job completes, and a website watch produces a baseline and a real change notification.
