# Verified Project Status

Last updated: 2026-11-17. This file records observed state, not intended state.

## GitHub

- Repository: https://github.com/Nolane-x/Nolane-search
- Default branch: main
- Current verified implementation commit: a2452ca030d000e0de3229ee4af80d5cb0035c09
- Repository is public.
- Connected GitHub integration has repository admin/push permission.
- Source tree, worker config, migrations, workflows, tests and handoff documents are committed.

## CI verification

GitHub Actions run for commit a2452ca030d000e0de3229ee4af80d5cb0035c09:

| Run | Result | Verified steps |
|---|---|---|
| CI run 44031058307 | PASS | Checkout, Node setup, dependency install, TypeScript typecheck, unit tests, cf build |
| Deploy run 44031058318 | BLOCKED | Source verification, cf build and cf deploy --dry-run passed; workflow stopped at D1 migration because CLOUDFLARE_API_TOKEN was empty |

The deploy workflow did not proceed to Worker deployment, runtime secret upload, or Telegram webhook registration. Therefore the bot is not yet deployed or live.

## Cloudflare account

The linked Cloudflare account was accessible through the Cloudflare connector.

Account ID: 1172c01120a2470aa12f81e5b4778556

| Resource | Name | ID / details | Verified state |
|---|---|---|---|
| D1 | nolane-search-db | 4f6a8cbd-cc8c-42b9-be6a-ed45c709d3db | Created in APAC; migration 0001_core.sql manually applied and confirmed via Cloudflare D1 API |
| Queue | nolane-search-jobs | 8a09dc04a6824faaa90f379f45f75ac0 | Created |
| Dead-letter Queue | nolane-search-dlq | e44fe78242614ed1b448dbea7dbe94e0 | Created |
| Workers subdomain | nolane-file.workers.dev | Account subdomain confirmed | Available |
| Worker | nolane-search | Expected URL https://nolane-search.nolane-file.workers.dev | Not deployed / not verified |
| R2 | — | — | Not enabled; excluded from MVP |
| KV | — | — | Not created; not used in MVP |

D1 schema confirmation: watches, telegram_updates, indexed_pages, indexed_pages_fts (FTS5), search_cache, and schema_migrations were created successfully in APAC. The initial migration name is recorded, so the GitHub migration script will skip it and continue safely after receiving a valid Cloudflare token.

Existing unrelated Workers in the account were not modified.

## Remaining blockers and inputs

The exact failing deploy log showed CLOUDFLARE_API_TOKEN was empty in the GitHub Actions environment. This is the immediate blocker.

Add these GitHub repository Actions secrets as described in docs/SECRETS.md:

Required:
- CLOUDFLARE_API_TOKEN
- TELEGRAM_BOT_TOKEN
- TELEGRAM_WEBHOOK_SECRET
- TAVILY_API_KEY

Recommended:
- ALLOWED_TELEGRAM_USER_IDS (can be added after first deployment by messaging /id)
- TELEGRAM_ARCHIVE_CHAT_ID (private archive channel, optional but recommended for result/snapshot archiving)

Optional:
- EXA_API_KEY
- BRAVE_SEARCH_API_KEY
- OPENROUTER_API_KEY
- OPENROUTER_MODEL
- GITHUB_TOKEN_SEARCH

No secret values have been exposed in source code or logs.

## Not yet verified

- Deployment with a real Cloudflare API token.
- Runtime secret upload.
- Telegram webhook registration and command menu.
- Owner allowlist.
- Live Tavily request / provider quota.
- /health against the deployed Worker.
- Search response delivered in Telegram.
- Deep Search Queue consumer end-to-end.
- Website watch initial snapshot and change alert end-to-end.
- Archive channel permissions and delivery.

## Release gate

Do not mark the service deployed, live, fully tested, reliable at scale or production-ready until:
1. CI is green.
2. Deploy workflow is green.
3. GET /health returns ok: true.
4. Telegram webhook info shows the expected Worker URL.
5. Owner account can search and receives real results.
6. A Deep Search job is consumed and reported.
7. A website watch produces an initial snapshot and a later real change notification.