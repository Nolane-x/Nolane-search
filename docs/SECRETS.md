# Secrets and external configuration

Add these values in GitHub repository Settings → Secrets and variables → Actions. Never commit secret values or paste them into repository files, issues or screenshots. Deployment uploads runtime values from a temporary file and deletes it after use.

## Required for initial deployment

| GitHub Actions secret | Purpose | Where to obtain |
|---|---|---|
| CLOUDFLARE_API_TOKEN | Deploy Worker, apply D1 migrations and configure Queue consumer | Cloudflare Dashboard → My Profile → API Tokens |
| TELEGRAM_BOT_TOKEN | Telegram bot authentication | Create a bot with https://t.me/BotFather |
| TELEGRAM_WEBHOOK_SECRET | Authenticate Telegram webhook requests | Generate a random 32+ character value using A-Z, a-z, 0-9, underscore or hyphen |
| TAVILY_API_KEY | Main web search provider | https://app.tavily.com/ |

Generate a webhook secret with OpenSSL: openssl rand -hex 32.

## Cloudflare token permissions

Create a scoped API token for this repository. The workflow needs:
- Account → Workers Scripts: Edit
- Account → D1: Edit
- Account → Queues: Edit

If Cloudflare's current token UI requires an additional read scope, add only the minimum scope requested by the CLI/API error. Do not use the Global API Key.

Cloudflare account ID is already recorded in cloudflare.config.ts and the workflow: 1172c01120a2470aa12f81e5b4778556.

## Recommended

| Secret | Purpose | Notes |
|---|---|---|
| ALLOWED_TELEGRAM_USER_IDS | Restrict use to the owner's numeric Telegram ID | Comma-separated IDs. Initially optional so first deploy can occur; message /id, then add your ID and redeploy. Without IDs, only /id and /start bootstrap responses work. |
| TELEGRAM_ARCHIVE_CHAT_ID | Destination for result archives and website snapshot documents | Create a private channel, add bot as administrator with post permission, then obtain channel ID (usually starts with -100). |

## Optional search and AI providers

| Secret | Feature |
|---|---|
| EXA_API_KEY | Semantic research discovery |
| BRAVE_SEARCH_API_KEY | Backup web/news search |
| TINYFISH_API_KEY | TinyFish Search and Fetch; enables /read and Deep Search source enrichment |
| OPENROUTER_API_KEY | AI synthesis for Deep Search |
| OPENROUTER_MODEL | Legacy single model ID; still supported |
| OPENROUTER_MODELS | Optional comma- or semicolon-separated model IDs, tried in priority order |
| GITHUB_TOKEN_SEARCH | Optional authenticated GitHub Search API |

The workflow maps GITHUB_TOKEN_SEARCH to Worker secret GITHUB_TOKEN. It does not store a short-lived GitHub Actions job token in the deployed Worker.

## Not required

No R2 credentials, KV namespace ID, VPS SSH key or local computer credentials are required for this MVP.

## After adding secrets

1. Push to main or run the Deploy Cloudflare Worker workflow.
2. Inspect Actions logs.
3. When deploy succeeds, message the bot with /id.
4. Add the numeric ID to ALLOWED_TELEGRAM_USER_IDS and redeploy.
5. Optionally create a private archive channel and add TELEGRAM_ARCHIVE_CHAT_ID.
6. Add optional providers only when needed. For TinyFish, create a key at https://agent.tinyfish.ai/api-keys and add it as TINYFISH_API_KEY. For multi-model OpenRouter, set OPENROUTER_API_KEY and add OPENROUTER_MODELS, for example: provider-a/model-id, provider-b/model-id. Use model IDs shown in your OpenRouter model catalogue. Keep OPENROUTER_MODEL if you want the legacy single-model setting; OPENROUTER_MODELS takes priority and the legacy value is appended as a fallback if not duplicated.

An existing secret can still be invalid or lack permissions. Deployment and runtime checks are the source of truth.
