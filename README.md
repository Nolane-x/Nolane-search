# Nolane Search

**Telegram-first hybrid Internet search engine** built on Cloudflare Workers.

Nolane Search is a personal search interface inside Telegram. It combines external search providers with a small independent index of selected websites. It is not a general-purpose crawler indexing the entire Internet.

## Current status

- Source tree is committed and CI has passed type-checking, unit tests and Cloudflare build validation.
- Cloudflare Worker `nolane-search` is deployed from `main`; its live `/health` endpoint returns `ok: true` and `database: reachable`.
- D1 migrations 0001 and 0002 are applied. The main Queue, dead-letter Queue, consumers and 30-minute Cron trigger are configured.
- GitHub Actions deployment has succeeded, including runtime-secret upload, Telegram webhook registration and Telegram command-menu registration.
- TinyFish Search/Fetch and OpenRouter multi-model routing are deployed. The live health endpoint reports TinyFish and OpenRouter configured, with six OpenRouter model IDs.
- CI, Worker build, deployment and health smoke checks passed. Real Telegram command execution and live provider-key acceptance still need owner-level end-to-end testing.
- Runtime credentials are managed as GitHub Actions secrets and are never stored in source control. See `docs/SECRETS.md` and `docs/STATUS.md` for verified details.

## Initial features

| Feature | Command | Scope |
|---|---|---|
| General web search | /search words | Federated Tavily/Exa/TinyFish/Brave/Wikipedia fallback, relevance and domain-diversity ranking, up to 12 candidates with Telegram pagination |
| Technology search | /tech words | Web search plus GitHub repositories |
| GitHub repositories | /github words | GitHub repository Search API |
| Encyclopedia reference | /wiki words | Free English/Vietnamese Wikipedia lookup via MediaWiki API |
| Research discovery | /research topic | Tavily, Exa and TinyFish Search |
| News search | /news topic | Tavily, Brave and TinyFish news discovery |
| Deep search | /deep question | Bounded multi-provider retrieval, TinyFish page extraction and optional OpenRouter multi-model synthesis |
| Search within a site | /site example.com words | Provider site restriction |
| Read a page | /read https://example.com | TinyFish Fetch extracts clean page text |
| Personal index | /local words | D1 FTS5 over monitored-page extracts |
| Website monitoring | /watch https://example.com | Scheduled HTTP checks and change alerts |
| Watch management | /watches, /unwatch ID | List and disable watches |
| Deep Search jobs | /jobs, /retry JOB_ID | Inspect recent jobs, view failure reason and retry failed jobs |
| Status | /status | Provider configuration and compact index counters |

Plain text messages are interpreted as web search. Results show five items per page; inline Previous/Next buttons browse up to 12 ranked candidates. Pagination sessions are private to the requesting user/chat and expire after 15 minutes. `/wiki` is a reference lookup, not a substitute for primary sources or current reporting. Use /help in the bot for the current command list.

## Architecture

- Telegram Bot API: user interface, result delivery and optional archive channel.
- Cloudflare Worker: webhook, authorization, provider routing and response formatting.
- Cloudflare D1: compact operational metadata, short cache, watch state and small FTS5 index.
- Cloudflare Queues: asynchronous Deep Search jobs, retries with backoff and dead-letter handling. D1 tracks job state so users can inspect or retry failed work.
- Cloudflare Cron: periodic website checks and housekeeping.
- Tavily / Exa / Brave / TinyFish / GitHub: external discovery providers, enabled only when their keys exist. The public MediaWiki API adds a free bilingual encyclopedia reference source without another API secret.
- OpenRouter: optional AI synthesis with ordered model fallback via OPENROUTER_MODELS; OPENROUTER_MODEL remains supported for older deployments.
- GitHub Actions: tests, build validation, migrations and deployment. It is not a permanent bot server.

See docs/ARCHITECTURE.md, docs/SETUP.md, docs/SECRETS.md and docs/OPERATIONS.md.

## Important limitations

1. Search coverage and freshness depend on external providers and their quotas.
2. Ranking is currently a transparent heuristic, not a trained relevance model. Search retains up to 12 candidates, displays five per page and caps the first-pass contribution at two results per domain.
3. Deep Search is bounded multi-query retrieval, not exhaustive research or a guarantee of factual correctness.
4. The initial crawler checks only URLs explicitly added by the owner. It does not crawl the whole web, render JavaScript-heavy sites, bypass login or defeat anti-bot controls.
5. Website monitoring reads and applies the origin's robots.txt policy before fetching a watched page. D1 keeps only a short extract per monitored page. If a Telegram archive channel is configured, the full extracted text snapshot is sent there on first capture and detected changes. Telegram is an archive, not a queryable database or an unlimited-storage guarantee.
6. The Worker, health endpoint, Telegram webhook and command menu are deployed. A successful configuration/health check does not guarantee that every provider key or user-level command works; test the bot in Telegram before relying on search or archive delivery.

## Development

Requires Node.js 22. Run npm install, npm run typecheck, npm test and npx cf build.

Cloudflare project configuration uses the Cloudflare CLI cf and cloudflare.config.ts. This project does not use Wrangler configuration.

## License

No license has been selected. Do not assume this repository grants rights to reuse the code until a license is added.