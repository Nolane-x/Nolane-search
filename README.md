# Nolane Search

**Private hybrid web search and AI research workspace** built on Cloudflare Workers, with Telegram as the secure login and bot interface.

Nolane Search is a personal search interface inside Telegram. It combines external search providers with a small independent index of selected websites. It is not a general-purpose crawler indexing the entire Internet.

## Current status

- Source tree is committed and CI has passed type-checking, unit tests and Cloudflare build validation.
- Cloudflare Worker `nolane-search` is deployed from `main`; its live `/health` endpoint returns `ok: true` and `database: reachable`.
- D1 migrations 0001 and 0002 are applied. The main Queue, dead-letter Queue, consumers and 30-minute Cron trigger are configured.
- GitHub Actions deployment has succeeded, including runtime-secret upload, Telegram webhook registration and Telegram command-menu registration.
- The AI Router accepts the owner's multi-provider `AI_ROUTER_CONFIG` secret plus the legacy OpenRouter fallback. A successful configuration check shows loaded routes, not proof that every upstream model key or quota is currently healthy.
- CI, Worker build, deployment and health smoke checks passed. Real Telegram command execution and live provider-key acceptance still need owner-level end-to-end testing.
- Runtime credentials are managed as GitHub Actions secrets and are never stored in source control. See `docs/SECRETS.md` and `docs/STATUS.md` for verified details.

## Initial features

| Feature | Command | Scope |
|---|---|---|
| General web search | /search words or browser portal | Federated Tavily/Exa/TinyFish/Brave/Wikipedia fallback, multi-signal reranking, up to 20 candidates |
| Technology search | /tech words | Web search plus GitHub repositories |
| GitHub repositories | /github words | GitHub repository Search API |
| Encyclopedia reference | /wiki words | Free English/Vietnamese Wikipedia lookup via MediaWiki API |
| Research discovery | /research topic | Tavily, Exa and TinyFish Search |
| News search | /news topic | Tavily, Brave and TinyFish news discovery |
| Deep search | /deep question | Bounded multi-provider retrieval, TinyFish page extraction and AI Router synthesis across configured model/key routes |
| Direct AI | /ai prompt | Task-aware multi-provider AI router with bounded key/model failover |
| AI web answer | /ask question or Web AI Overview | Web retrieval, evidence-grounded AI synthesis and linked sources |
| AI configuration | /ai_status, /models | Inspect configured providers, key-route count, models and task tags without exposing keys |
| Search within a site | /site example.com words | Provider site restriction |
| Read a page | /read https://example.com | TinyFish Fetch extracts clean page text |
| Personal index | /local words | D1 FTS5 over monitored-page extracts |
| Website monitoring | /watch https://example.com | Scheduled HTTP checks and change alerts |
| Watch management | /watches, /unwatch ID | List and disable watches |
| Deep Search jobs | /jobs, /retry JOB_ID | Inspect recent jobs, view failure reason and retry failed jobs |
| Status | /status | Provider configuration and compact index counters |

Plain text messages are interpreted as web search. Use `/web` in the private Telegram conversation to create a one-time, five-minute browser login link. The web portal offers category search, ranked result cards, AI Overview and a multi-turn chat panel. Browser sessions are stored server-side, use HttpOnly/Secure/SameSite cookies, expire after seven days, and are revocable. Search APIs require an authenticated allowlisted Telegram user and have per-user rate limits. Use `/ai prompt` for direct AI, `/ai fast prompt` or `/ai reasoning prompt` for task routing, `/ask question` for web-grounded AI synthesis, and `/ai_status` to inspect configured routes. Telegram results show five items per page; inline Previous/Next buttons browse up to 20 ranked candidates. Pagination sessions are private to the requesting user/chat and expire after 15 minutes. `/wiki` is a reference lookup, not a substitute for primary sources or current reporting.

### Search operators

`/search cloudflare site:developers.cloudflare.com` restricts results to a domain and its subdomains. `filetype:pdf` filters by URL extension; `intitle:workers` requires those title tokens. `after:2026-01-10 before:2026-02-01` restricts results to publication timestamps strictly after 10 January and strictly before 1 February. Date filters exclude results without a parseable publication timestamp. Use ISO dates (`YYYY-MM-DD`).

Use /help in the bot for the current command list.

## Architecture

- Telegram Bot API: user interface, result delivery and optional archive channel.
- Cloudflare Worker: webhook, authorization, provider routing and response formatting.
- Cloudflare D1: compact operational metadata, short cache, watch state and small FTS5 index.
- Cloudflare Queues: asynchronous Deep Search jobs, retries with backoff and dead-letter handling. D1 tracks job state so users can inspect or retry failed work.
- Cloudflare Cron: periodic website checks and housekeeping.
- Tavily / Exa / Brave / TinyFish / GitHub: external discovery providers, enabled only when their keys exist. The public MediaWiki API adds a free bilingual encyclopedia reference source without another API secret.
- AI Router: configured through encrypted GitHub Actions secret `AI_ROUTER_CONFIG`; supports multiple keys per provider and OpenAI-compatible, Anthropic Messages and Gemini Interactions APIs. It routes by task and falls back between configured key/model routes. Legacy OpenRouter secrets remain supported.
- GitHub Actions: tests, build validation, migrations and deployment. It is not a permanent bot server.

See docs/ARCHITECTURE.md, docs/SETUP.md, docs/SECRETS.md and docs/OPERATIONS.md. Add AI provider credentials only through GitHub Actions Secrets; never commit or paste keys into chat.

## Important limitations

1. Search coverage and freshness depend on external providers and their quotas.
2. Ranking is currently a transparent heuristic, not a trained relevance model. Search retains up to 12 candidates, displays five per page and caps the first-pass contribution at two results per domain.
3. Deep Search is bounded multi-query retrieval, not exhaustive research or a guarantee of factual correctness.
4. The browser portal is a private search UI, not a public anonymous search API. The initial crawler checks only URLs explicitly added by the owner. It does not crawl the whole web, render JavaScript-heavy sites, bypass login or defeat anti-bot controls.
5. Website monitoring reads and applies the origin's robots.txt policy before fetching a watched page. D1 keeps only a short extract per monitored page. If a Telegram archive channel is configured, the full extracted text snapshot is sent there on first capture and detected changes. Telegram is an archive, not a queryable database or an unlimited-storage guarantee.
6. The Worker, health endpoint, Telegram webhook and command menu are deployed. A successful configuration/health check does not guarantee that every provider key or user-level command works; test the bot in Telegram before relying on search or archive delivery.

## Development

Requires Node.js 22. Run npm install, npm run typecheck, npm test and npx cf build.

Cloudflare project configuration uses the Cloudflare CLI cf and cloudflare.config.ts. This project does not use Wrangler configuration.

## License

No license has been selected. Do not assume this repository grants rights to reuse the code until a license is added.