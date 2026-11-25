# Wave 63 — provider-safe media embedding

Date: 2026-11-25
Repository: https://github.com/Nolane-x/Nolane-search
Branch: `feat/wave-63-multi-method-video-player`
Pull request: https://github.com/Nolane-x/Nolane-search/pull/135

## Scope implemented in this slice

- PeerTube results retain the existing validated source page URL and now expose an `embedUrl` only when SepiaSearch supplies a canonical RFC-4122-shaped UUID.
- The URL is generated from the already validated PeerTube instance host, not by rewriting arbitrary source-page paths.
- The Media Portal does not load third-party frames during search. A user clicks **Nhúng player PeerTube** to create the iframe.
- The iframe is titled, lazy-loaded, sends no referrer, permits only media-related features, and uses PeerTube-compatible sandbox tokens. Its instance origin must differ from Nolane's own page origin; it is loaded only after a click. The original PeerTube page link remains available. The embed URL receives `p2p=0` by default so visitors are not opted into PeerTube's P2P peer-sharing network.
- The CSP now allows HTTPS frames because PeerTube instances are federated and can use different hosts. The application code separately enforces the exact instance host and canonical `/videos/embed/{uuid}` path before creating a frame.

Official PeerTube API reference for video embeds:
- https://docs.joinpeertube.org/api/embed-player

## Verification

The first PR CI run was intentionally red after tests were added before production code: it identified the missing embed URL and missing frame policy. The implementation was added afterward.
- Final GitHub Actions CI run #553 on HEAD `9e209ac30034506f17aff7ffc7880f603873c1ab`: **success**. TypeScript type-check, Vitest suite (383 tests), deployment-script checks, Python tool runner and Cloudflare Worker build all passed.
- This confirms build/test integrity, not a production deployment or a live test against arbitrary PeerTube instances.
- A valid embed still depends on the source instance allowing external embeds and the browser reaching that instance.

## What this does not implement

- It does not provide universal embeds for YouTube, Vimeo, Dailymotion, Twitch or arbitrary websites.
- It does not add HLS/DASH manifest playback.
- It does not download remote media.
- It does not add a GitHub Actions-to-browser transfer bridge or durable storage.
- It does not alter the existing NASA and Internet Archive native-player behavior.
- It does not make a playable/embeddable item automatically reusable or redistributable.

## Planned delivery order

1. Add explicit embed adapters for additional supported providers only after confirming their official player URL patterns and domain restrictions.
2. Add playback capability detection: native file, HLS, DASH, official embed, origin-page fallback.
3. Build metadata-only URL inspection using pinned yt-dlp/gallery-dl on ephemeral GitHub Actions runners.
4. Prototype no-storage download delivery: authenticated job-scoped WebSocket bridge via Durable Objects, with chunking, backpressure, checksum and cancellation. D1 must store metadata only.
5. Add an optional Windows local bridge for larger/longer downloads that exceed Actions runner limits.

## Security boundaries

- Do not load frames from arbitrary URLs.
- Do not accept arbitrary shell commands or user-supplied extractor options.
- Do not extract site cookies, sessions or access tokens.
- Do not bypass DRM, paywalls, logins or other access controls.
- Validate URL/redirect/DNS destinations before server-side fetching and apply strict resource caps.
- Download only media the user is authorized to save; retain source and license attribution.
- GitHub Releases and Actions artifacts are not private media storage substitutes.
