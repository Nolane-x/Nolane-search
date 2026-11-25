# Implementation plan — Wave 64 user-provided URL embeds

Spec: [2026-11-25-user-url-media-embeds.md](../specs/2026-11-25-user-url-media-embeds.md)

## Files

- `src/media-embed-resolver.ts`: pure URL validation/recognition and Vimeo oEmbed adapter.
- `src/index.ts`: authenticated, bounded `GET /api/media/resolve` route.
- `src/media-ui.ts`: detect URL input, call resolver, render provider-specific click-to-load player.
- `src/types.ts` and `cloudflare.config.ts`: optional Dailymotion Player ID binding if necessary.
- `tests/media-embed-resolver.test.ts`: provider URL parsing, invalid input, no network for untrusted hosts and oEmbed response validation.
- `tests/web-portal.test.ts`: authenticated endpoint, input bounds and Dailymotion config state.
- `tests/media-ui.test.ts`: URL-vs-search behavior, provider-specific iframe allowlists and referrer policies.

## Tasks (TDD)

### 1. Pure source URL resolver
- YouTube: parse 11-character IDs from watch/shorts/live/short URLs and emit privacy-enhanced embed URL.
- PeerTube: accept only exact `/videos/watch/{uuid}` URLs; reject IP/local hosts and same-origin host.
- Vimeo: validate allowed public URL schemes, call only the fixed oEmbed endpoint, reject redirects/oversized responses, and accept only an exact `player.vimeo.com/video/{same-id}` iframe src. Preserve unlisted hash from full URL.
- Dailymotion: parse source URL and video ID; return `requires_configuration` until a valid Player ID exists; with a configured ID, emit only `https://geo.dailymotion.com/player/{id}.html?video={videoId}`.

### 2. Authenticated resolver route
- Use the existing web-session gate.
- Validate `url` length and reject non-HTTPS before invoking resolver.
- Do not pass user URL to any generic fetch function. Vimeo is a preconstructed oEmbed API call only.
- Return a clear 4xx result for unsupported or unconfigured providers; no server-side media proxy.

### 3. Media Portal integration
- Treat URLs as an explicit single-item resolve action; keep text search unchanged.
- Render iframe only after click.
- Validate the embed URL again in the browser with exact provider host/path and origin inequality.
- PeerTube: `p2p=0`; Vimeo: `dnt=1`; YouTube: privacy-enhanced domain.
- Dailymotion: set iframe `referrerPolicy='strict-origin-when-cross-origin'`; other players retain `no-referrer`.
- Always show the original page link.

### 4. Verification and handoff
- Run all repository CI gates.
- Test malformed IDs, credentials, HTTP, ports, local hosts, encoded paths, forged oEmbed HTML, redirects and mismatched Vimeo IDs.
- Update docs only with the actual test/deploy state. This branch stacks on Wave 63; do not merge it into main before PR #135 lands.
