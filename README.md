# Nolane Search

**Telegram-first hybrid Internet search engine** built on Cloudflare Workers.

Nolane Search is a personal search interface inside Telegram. It combines external search providers with a small independent index of selected websites. It is not a general-purpose crawler indexing the entire Internet.

## Current status

- Source tree is committed and CI has passed type-checking, unit tests and Cloudflare build validation.
- Cloudflare Worker `nolane-search` has been deployed through the connected Cloudflare integration. Its `/health` endpoint has passed a GitHub Actions smoke test.
- D1 migrations 0001 and 0002 are applied. The main Queue, dead-letter Queue, consumers and 30-minute Cron trigger are configured.
- The latest code includes stale Deep Search job recovery on the 30-minute Cron schedule. CI, bundle validation and the live /health smoke test passed for this implementation.
- Telegram/provider secrets have not been configured yet, so the Worker is reachable but the Telegram bot is not live.
- The GitHub Actions Deploy workflow is awaiting `CLOUDFLARE_API_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET` and `TAVILY_API_KEY` to enable repeatable deployment and end-to-end bot setup.
- Follow docs/SECRETS.md to configure the required secrets. docs/STATUS.md records exact verified status and resource identifiers.

## Initial features

| Feature | Command | Scope |
|---|---|---|
| General web search | /search words | Tavily, with optional Brave fallback |
| Technology search | /tech words | Web search plus GitHub repositories |
| GitHub repositories | /github words | GitHub repository Search API |
| Research discovery | /research topic | Configured Tavily and Exa providers |
| News search | /news topic | Tavily News, optional Brave fallback |
| Deep search | /deep question | Bounded query expansion, merge and optional OpenRouter synthesis |
| Search within a site | /site example.com words | Provider site restriction |
| Personal index | /local words | D1 FTS5 over monitored-page extracts |
| Website monitoring | /watch https://example.com | Scheduled HTTP checks and change alerts |
| Watch management | /watches, /unwatch ID | List and disable watches |
| Deep Search jobs | /jobs, /retry JOB_ID | Inspect recent jobs, view failure reason and retry failed jobs |
| Status | /status | Provider configuration and compact index counters |

Plain text messages are interpreted as web search. Use /help in the bot for the current command list.

## Architecture

- Telegram Bot API: user interface, result delivery and optional archive channel.
- Cloudflare Worker: webhook, authorization, provider routing and response formatting.
- Cloudflare D1: compact operational metadata, short cache, watch state and small FTS5 index.
- Cloudflare Queues: asynchronous Deep Search jobs, retries with backoff and dead-letter handling. D1 tracks job state so users can inspect or retry failed work.
- Cloudflare Cron: periodic website checks and housekeeping.
- Tavily / Exa / Brave / GitHub: external discovery providers, enabled only when their keys exist.
- GitHub Actions: tests, build validation, migrations and deployment. It is not a permanent bot server.

See docs/ARCHITECTURE.md, docs/SETUP.md, docs/SECRETS.md and docs/OPERATIONS.md.

## Important limitations

1. Search coverage and freshness depend on external providers and their quotas.
2. Ranking is currently a transparent heuristic, not a trained relevance model.
3. Deep Search is bounded multi-query retrieval, not exhaustive research or a guarantee of factual correctness.
4. The initial crawler checks only URLs explicitly added by the owner. It does not crawl the whole web, render JavaScript-heavy sites, bypass login or defeat anti-bot controls.
5. D1 keeps only a short extract per monitored page. If a Telegram archive channel is configured, the full extracted text snapshot is sent there on first capture and detected changes. Telegram is an archive, not a queryable database or an unlimited-storage guarantee.
6. The Worker health endpoint is deployed and verified; do not call the Telegram bot live until webhook, credentials, provider search and end-to-end bot tests pass.

## Development

Requires Node.js 22. Run npm install, npm run typecheck, npm test and npx cf build.

Cloudflare project configuration uses the Cloudflare CLI cf and cloudflare.config.ts. This project does not use Wrangler configuration.

## License

No license has been selected. Do not assume this repository grants rights to reuse the code until a license is added.