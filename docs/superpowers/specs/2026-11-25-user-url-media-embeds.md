# Wave 64 — resolve user-provided media URLs

Date: 2026-11-25
Status: planned; provider-specific, no universal arbitrary URL embed.

## Goal

Allow an authenticated Media Portal user to paste a video page URL and let Nolane resolve a documented official player URL. Do not fetch or proxy the actual video file. The existing query search remains unchanged for ordinary text queries.

## Supported inputs

- **YouTube**: `youtube.com/watch?v=...`, `youtu.be/...`, `youtube.com/shorts/...`, `youtube.com/live/...`, and existing `youtube.com/embed/...`. Use the privacy-enhanced `youtube-nocookie.com/embed/{id}` player.
- **Vimeo**: public and unlisted video URLs. Use Vimeo's official oEmbed endpoint; pass the full source URL so an unlisted video's `h` privacy hash is preserved. Parse only the iframe src and validate that the returned player host/path match `player.vimeo.com/video/{id}`.
- **PeerTube**: `/videos/watch/{uuid}` and official embed URLs on the exact validated HTTPS instance. Construct only `/videos/embed/{uuid}`; no arbitrary redirects or subdomains.
- **Dailymotion**: recognize the source URL, but only construct an embed when a Dailymotion Player ID is configured. The current Dailymotion player API requires a Player ID; an embed without one can return HTTP 403. Do not use a guessed/demo Player ID.

## API and UI

- Add authenticated `GET /api/media/resolve?url=...`.
- No generic fetch/proxy of the user-supplied URL. Vimeo uses only the fixed official `https://vimeo.com/api/oembed.json` endpoint with the validated Vimeo URL as an encoded parameter.
- Return a normalized single video item and a status explaining unsupported sources or missing Dailymotion configuration.
- If the Media Portal search field contains an HTTPS URL, call the resolver. If it is ordinary text, keep the existing provider search.
- Create iframes only after a user click; preserve the origin-page link. Never insert returned provider HTML into the DOM.

## Security/privacy

- HTTPS only; reject username/password, nonstandard ports, IP literals and malformed hosts.
- Use provider-specific host and path allowlists for each embed URL.
- Reject embed origins equal to Nolane's own origin.
- The browser creates the iframe from a validated embed URL, applies provider-specific sandbox/permissions and uses a restrictive referrer policy.
- Use YouTube's privacy-enhanced host and Vimeo's Do Not Track parameter where applicable.
- Dailymotion requires a scoped `strict-origin-when-cross-origin` iframe referrer policy to satisfy its playback requirements; do not weaken the parent page's global referrer policy.
- Do not resolve password-protected, private, DRM, paywalled or otherwise unauthorized content.

## Explicit non-goals

- This is not a website scraper and does not support every host.
- No login/cookie extraction, DRM bypass, paywall bypass, arbitrary command execution, downloader or file proxy.
- HLS/DASH remains a separate playback phase.
