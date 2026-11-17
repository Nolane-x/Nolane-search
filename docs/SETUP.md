# Setup guide

The Cloudflare Worker and core storage resources have already been provisioned. No home PC must stay on. The current Worker health endpoint is live; the Telegram bot is waiting for the owner's credentials.

## Current deployment

- Worker: nolane-search
- URL: https://nolane-search.nolane-file.workers.dev
- Health: https://nolane-search.nolane-file.workers.dev/health
- D1: nolane-search-db (APAC)
- Main Queue: nolane-search-jobs
- Dead-letter Queue: nolane-search-dlq
- Cron: every 30 minutes

The D1 migrations are already applied and both Queue consumers are attached. Do not create duplicate Cloudflare resources.

## 1. Create Telegram bot

1. Open https://t.me/BotFather.
2. Send /newbot.
3. Choose display name and username.
4. Copy the bot token.
5. Add it as TELEGRAM_BOT_TOKEN in GitHub Actions secrets.

Never commit or paste the token into chat.

## 2. Create search provider key

1. Create an account at https://app.tavily.com/.
2. Create/copy an API key.
3. Add it as TAVILY_API_KEY.

Tavily is the required initial search provider. Optional providers are described in SECRETS.md.

## 3. Create webhook secret

Generate a random 32+ character hex secret with:

```sh
openssl rand -hex 32
```

Add it as TELEGRAM_WEBHOOK_SECRET. Do not reuse a password.

## 4. Configure GitHub Actions secrets

Open GitHub → Nolane-search → Settings → Secrets and variables → Actions.

Required for the repeatable Deploy workflow:
- CLOUDFLARE_API_TOKEN
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
- OPENROUTER_MODELS (ordered comma- or newline-separated model IDs)
- GITHUB_TOKEN_SEARCH

Create a scoped Cloudflare API token with the permissions documented in SECRETS.md. The existing Worker was uploaded through the connected Cloudflare integration; the GitHub secret is needed so future pushes can deploy automatically.

## 5. Deploy and register the webhook

Once the required secrets have been added:
1. Push a source change to main or open Actions → Deploy Cloudflare Worker → Run workflow.
2. The workflow runs typecheck/tests/build validation, applies unapplied D1 migrations, deploys the Worker and runtime secrets, then registers the Telegram webhook and command menu.
3. Confirm the Deploy workflow is green.
4. Open the health URL above. Expected JSON includes ok: true and database: reachable.

The health endpoint is already verified for the current Worker; after adding secrets, rerun deployment to install runtime secret bindings and configure Telegram.

## 6. Allowlist the owner

After the bot token and webhook are configured:
1. Open the bot and send /id.
2. It replies with your numeric Telegram ID.
3. Add the ID as ALLOWED_TELEGRAM_USER_IDS.
4. Redeploy so the Worker receives the secret.
5. Send /start and /help.

Before allowlisting, normal bot functions are blocked.

## 7. Optional Telegram archive channel

1. Create a private channel, for example Nolane Search Archive.
2. Add the bot as administrator with permission to post.
3. Obtain its numeric channel ID, typically starting with -100.
4. Add it as TELEGRAM_ARCHIVE_CHAT_ID.
5. Redeploy.
6. Test a search and /watch https://example.com. Confirm result messages and snapshot documents appear in the archive channel.

The archive is not guaranteed unlimited storage and does not replace D1 operational metadata.

## 8. Test commands

- /search Cloudflare Workers
- /tech browser automation agents
- /github telegram database
- /research small language models reasoning
- /read https://example.com
- /news artificial intelligence
- /deep compare open-source search engines
- /jobs
- /watch https://example.com
- /watches
- /status

A watch is checked on a 30-minute Cron schedule, not immediately. First check creates a baseline; later changes trigger alerts.
