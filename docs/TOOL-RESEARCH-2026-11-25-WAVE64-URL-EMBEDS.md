# Wave 64 — user-provided video URL resolution

Date: 2026-11-25
Repository: https://github.com/Nolane-x/Nolane-search
PR: https://github.com/Nolane-x/Nolane-search/pull/136

## What the user can do

Paste a supported HTTPS video page URL into the Media Portal search field. Nolane recognizes it as a single-video request and resolves a provider-owned player rather than treating the URL as text keywords. Ordinary search terms still use the existing multi-provider search API.

## Provider behavior

- **YouTube:** supports exact YouTube/youtu.be URL hosts and the watch, short, shorts, live and embed path forms. Requires an 11-character video ID and uses the privacy-enhanced `youtube-nocookie.com/embed/{id}` player.
- **Vimeo:** resolves public and unlisted page URLs through the fixed official Vimeo oEmbed endpoint. The full URL is sent so an unlisted hash can be retained. The returned iframe source is parsed and must match `player.vimeo.com/video/{same-id}`; unrelated hosts, IDs, paths and query keys are rejected. DNT is enabled.
- **PeerTube:** supports a direct `/videos/watch/{uuid}` or existing `/videos/embed/{uuid}` URL on a valid HTTPS instance. It uses only the same instance's official embed path and retains the origin page.
- **Dailymotion:** recognizes `dailymotion.com/video/{id}` and `dai.ly/{id}`. The current Dailymotion player requires a Player ID configured by the account owner. Without it, Nolane returns a clear configuration-needed response and does not invent an embed identifier. When present, the official `geo.dailymotion.com/player/{PlayerID}.html?video={id}` pattern is used with the provider-required `strict-origin-when-cross-origin` iframe referrer policy.

## Security and privacy

- The new API is behind the existing authenticated Web Session check.
- Only HTTPS is accepted; credentials, non-default ports, IP literals, local/internal hostnames and overlong inputs are rejected.
- Vimeo is the only source lookup that makes an upstream request, and it calls one fixed official oEmbed endpoint with redirects disabled and a bounded JSON response. User URLs are never fetched as generic server-side pages or proxied media.
- Every embed URL is checked a second time in the browser against the exact provider host/path. Same-origin frames and URL fragments are rejected.
- Iframes remain click-to-load. The original source page link remains available.
- PeerTube has P2P sharing disabled by default in its embed URL; Vimeo uses DNT and YouTube uses the privacy-enhanced host.
- No downloader, HLS/DASH transport, cookie handling, authentication harvesting, DRM/paywall bypass or content rehosting is included.

## Known configuration requirement

Dailymotion playback remains unavailable until a valid Player ID is configured by the owner. The resolver accepts the optional `MEDIA_DAILYMOTION_PLAYER_ID` runtime value; it is not committed as a public identifier in the repository. Dailymotion's embed API requires the Player ID associated with the owner's player.

## Verification

The new resolver test file covers YouTube URL variants, malformed hosts/IDs, HTTPS/credentials/ports/IP rejection, PeerTube UUID paths, Vimeo oEmbed success and forged player rejection, Dailymotion missing/configured Player ID paths, and URL length bounds. The UI tests cover URL-vs-text behavior, provider-specific iframe checks and source-page fallback. Full repository CI status is tracked on PR #136; this document does not claim a production deployment.

## Not yet implemented

- HLS or DASH adaptive playback.
- Managed downloads through ephemeral GitHub Actions runners.
- A no-storage runner-to-browser transfer bridge.
- A paired Windows local download helper.
- Universal support for arbitrary websites or sites that require their own login, consent, DRM or private access.
