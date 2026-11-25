# Wave 65 — Twitch VOD and Clip URL embeds

Date: 2026-11-25  
Status: implementation candidate; stacked on Waves 63–64.

## Goal

Let an authenticated Media Portal user paste a Twitch VOD or Clip page URL and load Twitch's official iframe player after an explicit click. Keep text search and the existing providers unchanged.

## Supported source forms

- Twitch VOD: `twitch.tv/videos/{numeric-id}`
- Twitch Clip: `clips.twitch.tv/{slug}`
- Twitch Clip: `twitch.tv/{channel}/clip/{slug}`

Only exact HTTPS Twitch source hosts are accepted. Live channel pages, chat, collections, and arbitrary Twitch paths are outside this phase.

## Resolution

- VOD player: `https://player.twitch.tv/?video=v{numeric-id}&autoplay=false`
- Clip player: `https://clips.twitch.tv/embed?clip={slug}&autoplay=false`
- The Worker does not fetch the source URL and does not add a caller-supplied parent domain.
- The browser validates the exact output host/path and the allowed query keys, then adds `parent=location.hostname` only after the user clicks.
- Only HTTPS pages with a public DNS hostname can load Twitch's iframe.

## UI requirements

- Keep an original source-page link.
- Load the iframe only after a click.
- Use the documented minimum player size: 400 px wide and 300 px high.
- On narrow layouts below 400 px, show an explanatory message rather than creating a player that cannot meet the provider requirement.
- Keep a restrictive referrer policy and the existing iframe sandbox/permissions.
- Do not insert provider HTML returned from an upstream service.

## Safety constraints

Reject non-HTTPS URLs, credentials, non-default ports, IP literals, local/internal/test hosts, malformed VOD IDs, malformed clip slugs, suffix/lookalike domains and unsupported paths. Revalidate player host, path, query keys and parameter values in the browser. Never trust a parent domain from the pasted link.

## Tests

- Resolver: Twitch VOD, clip subdomain, channel clip, malformed IDs, lookalike hosts, and confirmation that Twitch resolution does not make a server-side request.
- UI: exact iframe host/path validation, parent host derived from current page, original source link label, and generated inline script syntax.
- Full repository CI: typecheck, Vitest, Python runner, deployment-script checks and Worker build.

## Non-goals

No Twitch API, credentials, user identity, live channels, chat, HLS/DASH, direct-file downloader, media proxy, storage or DRM/paywall bypass.
