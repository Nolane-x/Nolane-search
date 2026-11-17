# Setup guide

This repository deploys through GitHub Actions. No home PC must stay on.

## 1. Create Telegram bot

1. Open https://t.me/BotFather.
2. Send /newbot.
3. Choose display name and username.
4. Copy the bot token.
5. Add it as TELEGRAM_BOT_TOKEN in GitHub Actions secrets.

Never commit the token.

## 2. Create search provider key

1. Create an account at https://app.tavily.com/.
2. Create/copy an API key.
3. Add it as TAVILY_API_KEY.

Tavily is the required initial search provider. Optional providers are described in SECRETS.md.

## 3. Create webhook secret

Generate a random 32+ character hex secret with: openssl rand -hex 32.
Add it as TELEGRAM_WEBHOOK_SECRET. Do not reuse a password.

## 4. Cloudflare API token

Create a scoped token with permissions described in SECRETS.md and add it as CLOUDFLARE_API_TOKEN.

The linked account already contains:
- D1: nolane-search-db
- Queue: nolane-search-jobs
- Dead-letter queue: nolane-search-dlq

Do not create duplicate resources.

## 5. Add GitHub Actions secrets

Minimum:
- CLOUDFLARE_API_TOKEN
- TELEGRAM_BOT_TOKEN
- TELEGRAM_WEBHOOK_SECRET
- TAVILY_API_KEY

Recommended:
- ALLOWED_TELEGRAM_USER_IDS (can be added after first deployment)
- TELEGRAM_ARCHIVE_CHAT_ID (private archive channel)

Optional:
- EXA_API_KEY
- BRAVE_SEARCH_API_KEY
- OPENROUTER_API_KEY
- OPENROUTER_MODEL
- GITHUB_TOKEN_SEARCH

## 6. Deploy

1. Push changes to main or run Actions → Deploy Cloudflare Worker.
2. Workflow installs dependencies, type-checks, tests, builds, dry-runs, applies D1 migrations, deploys Worker + secrets and registers Telegram webhook/commands.
3. Confirm the Actions run is green.
4. Open https://nolane-search.nolane-file.workers.dev/health. Expected response includes ok=true.

If deployment fails, inspect its failing step. Do not assume the bot is live.

## 7. Allowlist owner

If ALLOWED_TELEGRAM_USER_IDS was not configured:
1. Open the bot and send /id.
2. It replies with your numeric Telegram ID.
3. Add this number as ALLOWED_TELEGRAM_USER_IDS.
4. Redeploy so Worker receives the secret.
5. Send /start and /help.

Before allowlisting, normal search commands are blocked.

## 8. Telegram archive channel

1. Create a private channel, for example Nolane Search Archive.
2. Add the bot as administrator with permission to post.
3. Obtain its numeric channel ID, typically starts with -100. A bot such as @RawDataBot can help when forwarding a channel post; verify the returned ID.
4. Add it as TELEGRAM_ARCHIVE_CHAT_ID.
5. Redeploy.
6. Test a search and /watch https://example.com. Confirm result messages and first snapshot files appear in the archive channel.

The archive is not guaranteed unlimited storage and does not replace D1 operational metadata.

## 9. Test commands

- /search Cloudflare Workers
- /tech browser automation agents
- /github telegram database
- /research small language models reasoning
- /news artificial intelligence
- /deep compare open-source search engines
- /watch https://example.com
- /watches
- /status

A watch is checked on a 30-minute Cron schedule, not immediately. First check creates a baseline; later changes trigger alerts.
