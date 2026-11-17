# Verified Project Status

Last updated: 2026-11-17. This file records observed state, not intended state.

## GitHub

- Repository: https://github.com/Nolane-x/Nolane-search
- Default branch: main
- Latest source implementation commit: a2452ca030d000e0de3229ee4af80d5cb0035c09
- Documentation status commit: c7a3b64141f324b96513c267411acc156594345d
- Repository is public; connected GitHub integration has admin/push permission.

## CI verification

GitHub Actions verification:

| Run | Result | Verified steps |
|---|---|---|
| CI run 44031058307 | PASS | Checkout, Node setup, dependency install, TypeScript typecheck, unit tests, cf build |
| CI run 44031623739 | PASS | Same checks after status documentation update |
| Deploy run 44031058318 | BLOCKED | Source verification, cf build and cf deploy --dry-run passed; stopped at D1 migration because CLOUDFLARE_API_TOKEN was empty |
| Deploy run 44031623713 | BLOCKED | Same missing CLOUDFLARE_API_TOKEN blocker |

The deploy workflow did not proceed to Worker deployment, runtime secret upload or Telegram webhook registration. The bot is not deployed or live.

## Cloudflare account

Account ID: 1172c01120a2470aa12f81e5b4778556

| Resource | Name | ID / details | Verified state |
|---|---|---|---|
| D1 | nolane-search-db | 4f6a8cbd-cc8c-42b9-be6a-ed45c709d3db | Created in APAC; 0001_core.sql manually applied and confirmed via Cloudflare D1 API |
| Queue | nolane-search-jobs | 8a09dc04a6824faaa90f379f45f75ac0 | Created |
| Dead-letter Queue | nolane-search-dlq | e44fe78242614ed1b448dbea7dbe94e0 | Created |
| Workers subdomain | nolane-file.workers.dev | Account subdomain confirmed | Available |
| Worker | nolane-search | Expected URL https://nolane-search.nolane-file.workers.dev | Not deployed / not verified |
| R2 | — | — | Not enabled; excluded from MVP |
| KV | — | — | Not created; not used in MVP |

D1 schema tables confirmed in APAC: watches, telegram_updates, indexed_pages, indexed_pages_fts (FTS5), search_cache and schema_migrations. The migration script will see 0001_core.sql in schema_migrations and skip it.
Existing unrelated Workers in the account were not modified.

## Immediate blocker

The exact GitHub Actions deployment logs show CLOUDFLARE_API_TOKEN is empty. Add a repository Actions secret with this exact name. A differently named Cloudflare secret will not populate that environment variable.

Required GitHub Actions secrets:
- CLOUDFLARE_API_TOKEN
- TELEGRAM_BOT_TOKEN
- TELEGRAM_WEBHOOK_SECRET
- TAVILY_API_KEY

Recommended:
- ALLOWED_TELEGRAM_USER_IDS (can be added after first deploy by messaging /id)
- TELEGRAM_ARCHIVE_CHAT_ID (private archive channel)

Optional:
- EXA_API_KEY
- BRAVE_SEARCH_API_KEY
- OPENROUTER_API_KEY
- OPENROUTER_MODEL
- GITHUB_TOKEN_SEARCH

## Not yet verified

- Deployment with a real Cloudflare API token.
- Runtime secret upload.
- Telegram webhook and command registration.
- Owner allowlist and bot interaction.
- Live provider request and quota.
- /health against deployed Worker.
- Search response delivered to Telegram.
- Deep Search Queue end-to-end.
- Website watch snapshot and change alert end-to-end.
- Archive channel permissions and delivery.

## Release gate

Do not mark the service deployed or production-ready until CI and deploy are green, /health returns ok=true, the Telegram webhook points to the Worker, search works, a Deep Search job is processed, and a website watch produces an initial snapshot and a real change notification.