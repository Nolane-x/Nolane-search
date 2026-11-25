# Wave 59 handoff — PeerTube federated video search

Date: 2026-11-25
Branch: `feat/wave-59-peertube-federated-video-search`
Base: `e56763479f51ef9a8474241fa881b52fcc8ea2e2`
Release status: merged and deployed via [PR #128](https://github.com/Nolane-x/Nolane-search/pull/128), merge commit 2cc7f546828ea0818da68f5b15da9fe2903762c0. PeerTube is exposed through both the AI tool catalog and authenticated Media Portal.

## New AI-callable tool

- `search_peertube_videos` searches the public SepiaSearch index across the PeerTube federation.
- Query length is 2–140 characters; result limit is 1–8 (default 6).
- Requests use relevance ordering (`sort=-match`) and `nsfw=false`.
- Results preserve the originating PeerTube video page, host, creator/channel, duration, views, language, license label and publication time where available.
- No API key, new secret, D1 migration, Cloudflare binding or new dependency is introduced.

## Safety

- A result page URL must be HTTPS, have no credentials or nonstandard port, and match the account/channel host reported in the same API record.
- IP-literal, local/private-style hostnames, HTTP URLs, cross-host URLs and explicit NSFW results are rejected.
- The tool does not fetch result URLs, embed remote players, download media or rehost files.
- SepiaSearch coverage is partial. License and publication metadata must be verified on the origin instance.

## Changed files

- `src/media-discovery-tools.ts`
- `src/agent-tools.ts`
- `src/index.ts` (authenticated Media Portal API route and provider validation)
- `src/media-ui.ts` (provider selector and origin-instance link)
- `tests/peertube-discovery.test.ts`
- `tests/media-ui.test.ts`
- `docs/TOOL-RESEARCH-2026-11-25-WAVE59.md`
- `docs/HANDOFF-WAVE-FIFTY-NINE-2026-11-25.md`

## Release verification — 2026-11-25

- PR CI #530: https://github.com/Nolane-x/Nolane-search/actions/runs/45551369316 — passed.
- Main CI #531: https://github.com/Nolane-x/Nolane-search/actions/runs/45551570106 — passed TypeScript, 36 Vitest files / 372 tests, deployment-script checks, 449 Python tool-runner tests and Worker build.
- Merge commit: 2cc7f546828ea0818da68f5b15da9fe2903762c0.
- Cloudflare deployment #163: https://github.com/Nolane-x/Nolane-search/actions/runs/45551570024 — succeeded. Worker Version ID: e1dc5532-d34e-4b9d-bcbd-906a15211576.
- Telegram webhook was verified and bot commands were registered. No D1 migration was needed.
- Worker export #156: https://github.com/Nolane-x/Nolane-search/actions/runs/45551570134 — succeeded; health smoke returned ok=true, database reachable and archiveEnabled=true.
- Provider verification remains limited: unit tests mock SepiaSearch; an actual search request could not be executed from the development environment because DNS resolution failed. Do not infer live provider availability from Worker health checks.
