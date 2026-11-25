# Wave 59 handoff — PeerTube federated video search

Date: 2026-11-25
Branch: \`feat/wave-59-peertube-federated-video-search\`
Base: \`e56763479f51ef9a8474241fa881b52fcc8ea2e2\`
Release status: implementation branch; CI and production deployment verification pending.

## New AI-callable tool

- \`search_peertube_videos\` searches the public SepiaSearch index across the PeerTube federation.
- Query length is 2–140 characters; result limit is 1–8 (default 6).
- Requests use relevance ordering (\`sort=-match\`) and \`nsfw=false\`.
- Results preserve the originating PeerTube video page, host, creator/channel, duration, views, language, license label and publication time where available.
- No API key, new secret, D1 migration, Cloudflare binding or new dependency is introduced.

## Safety

- A result page URL must be HTTPS, have no credentials or nonstandard port, and match the account/channel host reported in the same API record.
- IP-literal, local/private-style hostnames, HTTP URLs, cross-host URLs and explicit NSFW results are rejected.
- The tool does not fetch result URLs, embed remote players, download media or rehost files.
- SepiaSearch coverage is partial. License and publication metadata must be verified on the origin instance.

## Changed files

- \`src/media-discovery-tools.ts\`
- \`src/agent-tools.ts\`
- \`tests/peertube-discovery.test.ts\`
- \`docs/TOOL-RESEARCH-2026-11-25-WAVE59.md\`
- \`docs/HANDOFF-WAVE-FIFTY-NINE-2026-11-25.md\`

## Release verification

- Unit tests are mocked contract tests, not a live provider check.
- CI result: pending.
- Merge commit: pending.
- Cloudflare Worker deployment and version: pending.
- Worker export and public \`/health\` smoke: pending.
- Live SepiaSearch response: not verified in the development environment because outbound DNS resolution was unavailable; never describe the provider as live-verified based only on mocked tests.
