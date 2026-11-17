# Verified Project Status

Last updated: 2026-11-17. This file records observed state, not intended state.

## GitHub

- Repository: https://github.com/Nolane-x/Nolane-search
- Default branch: main
- Repository is public.
- Connected GitHub integration has admin/push permission.
- Confirm the implementation commit and full tree are present before treating source assembly as complete.

## Cloudflare account

The linked Cloudflare account was accessible through the Cloudflare connector.

Account ID: 1172c01120a2470aa12f81e5b4778556

| Resource | Name | ID / details | Verified state |
|---|---|---|---|
| D1 | nolane-search-db | 4f6a8cbd-cc8c-42b9-be6a-ed45c709d3db | Created in APAC; migration still required |
| Queue | nolane-search-jobs | 8a09dc04a6824faaa90f379f45f75ac0 | Created |
| Dead-letter Queue | nolane-search-dlq | e44fe78242614ed1b448dbea7dbe94e0 | Created |
| Workers subdomain | nolane-file.workers.dev | Account subdomain confirmed | Available |
| Worker | nolane-search | Expected URL https://nolane-search.nolane-file.workers.dev | Deployment not yet verified |
| R2 | — | — | Not enabled; excluded from MVP |
| KV | — | — | Not created; not used in MVP |

Existing unrelated Workers in the account were not modified.

## Not yet verified

- Source builds with pinned packages.
- D1 FTS5 migration applies successfully.
- Worker deploy succeeds.
- Runtime secrets exist on the deployed Worker.
- Telegram webhook and command menu are registered.
- Owner is allowlisted.
- Tavily API key is valid and has quota.
- Health, search, Queue consumer, watch Cron and archive channel work end to end.

## User inputs still needed

Minimum: CLOUDFLARE_API_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_SECRET, TAVILY_API_KEY.

Recommended after first deploy: ALLOWED_TELEGRAM_USER_IDS and TELEGRAM_ARCHIVE_CHAT_ID.

Optional: EXA_API_KEY, BRAVE_SEARCH_API_KEY, OPENROUTER_API_KEY, OPENROUTER_MODEL and GITHUB_TOKEN_SEARCH.

See docs/SECRETS.md.

## Release gate

Do not mark the service deployed, live, fully tested or production-ready until CI is green, deploy is green, /health returns ok=true, Telegram webhook points to the Worker, owner can search, Deep Search is consumed and a website watch produces a baseline snapshot and later change notification.
