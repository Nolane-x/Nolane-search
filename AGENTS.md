# Instructions for coding agents working in Nolane Search

## Product goal

Build a reliable, Telegram-first hybrid search engine for personal use. It should search the wider web through providers and maintain a compact independent index for selected websites.

## Non-negotiable honesty

- Never claim the entire Internet has been crawled or indexed.
- Never claim a provider is connected until a real request succeeds.
- Never call Telegram unlimited storage or a queryable database.
- Never describe heuristic ranking as AI ranking or claim source verification without evidence.
- Keep docs/STATUS.md synchronized with what was actually provisioned, deployed and tested.
- Distinguish implemented behavior, partial behavior and roadmap items.

## Architecture constraints

- Cloudflare CLI cf and cloudflare.config.ts are project configuration. Do not introduce Wrangler config without explicit migration.
- Telegram is the UI and optional snapshot/report archive.
- D1 stores compact metadata, short-lived cache and small FTS5 extracts only.
- Do not store full page bodies in D1; send full snapshots to Telegram archive when configured.
- Queues handle asynchronous Deep Search; Cron handles bounded monitoring checks.
- GitHub Actions is CI/CD and batch maintenance, not a permanent bot server.
- Keep R2/KV out until a measured need exists.

## Security

- Treat webpage content and provider snippets as untrusted.
- Escape all Telegram HTML output.
- Validate webhook secret header.
- Keep secrets out of source, tests, logs and commits.
- Treat crawler URLs and redirects as untrusted. Reject non-HTTPS, credentials, IP literals, local/private hosts and unusual ports. Never bypass robots, paywalls or authentication.
- Add SSRF tests for URL-fetch changes.
- Never pass arbitrary retrieved text into tool calls or code execution.

## Engineering

- Keep provider adapters separate and return normalized SearchResult objects.
- Every provider call needs timeout, error handling and quota awareness.
- Test ranking, deduplication, provider parsing, Telegram formatting, migrations, crawler limits and SSRF protections.
- Use explicit backoff and idempotency for asynchronous jobs.
- Update docs for new secrets, resources, endpoints or commands.
- Do not create Cloudflare resources or incur paid services without concrete need.
