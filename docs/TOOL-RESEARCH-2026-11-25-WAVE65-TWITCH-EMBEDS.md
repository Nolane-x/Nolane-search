# Wave 65 — Twitch VOD and Clip embeds

Date: 2026-11-25  
Repository: https://github.com/Nolane-x/Nolane-search  
Branch: `feat/wave-65-twitch-video-embeds`

## Scope

Wave 65 extends the authenticated Media Portal URL resolver with Twitch video-on-demand (VOD) and Clip page URLs. It does not add live-channel playback, chat, Twitch API access, downloading or media proxying.

## Official embed contract

Twitch documents two distinct iframe players:

- VODs use `https://player.twitch.tv/` with a `video=v{numeric-id}` query parameter.
- Clips use `https://clips.twitch.tv/embed` with a `clip={slug}` query parameter.
- Both iframe forms require a `parent` query parameter identifying the embedding domain.
- Twitch documents minimum iframe dimensions of 400 px wide by 300 px high.

Official references:

- https://dev.twitch.tv/docs/embed/video-and-clips/
- https://dev.twitch.tv/docs/embed/

## Accepted source URL forms

- `https://www.twitch.tv/videos/{numeric-id}`
- `https://twitch.tv/videos/{numeric-id}`
- `https://clips.twitch.tv/{clip-slug}`
- `https://www.twitch.tv/{channel}/clip/{clip-slug}`

The resolver accepts only exact Twitch-owned source hosts and HTTPS URLs. It creates only the corresponding official embed host/path and does not make an upstream request. Other Twitch paths, lookalike domains, malformed IDs, HTTP URLs, credentials, non-default ports, IP literals and private/local hostnames remain unsupported.

## Parent and iframe behavior

The backend does not trust a caller-supplied parent domain and does not accept a parent value from the source URL. The browser adds exactly one `parent` value from `location.hostname` after the user clicks the embed button. The page must be HTTPS and use a public DNS hostname; IP literals and local/test hostnames are rejected.

The Twitch card spans two grid columns on wide layouts to reach the provider's documented width. On narrower layouts, the UI refuses to create a player when the preview area is under 400 px and keeps the original Twitch page link available. The iframe also receives a minimum height of 300 px, click-to-load behavior, a restrictive referrer policy, and the existing sandbox/permissions.

## Security and privacy boundaries

- The authenticated `GET /api/media/resolve` gate remains unchanged.
- No user-provided URL is fetched by the Worker.
- The embed URL is revalidated in the browser against exact Twitch player hosts, exact paths, and an exact parameter allowlist.
- The Twitch `parent` is generated from the current page hostname, never from user input or an untrusted URL parameter.
- Autoplay is explicitly set to false.
- No login-cookie extraction, chat embedding, downloads, DRM bypass or content rehosting is implemented.

## Verification target

CI must run the complete TypeScript, Vitest, Python tool-runner, deployment-script and Worker-build checks. A new UI regression test compiles the generated inline browser script so regex/syntax defects cannot pass as string-only assertions. CI does not prove that every Twitch VOD or Clip is still public or playable; production end-to-end playback should be checked with public examples after the dependent PRs are merged and deployed.
