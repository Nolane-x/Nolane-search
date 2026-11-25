# Wave 66 — HLS and DASH manifest playback

Date: 2026-11-25  
Status: implementation candidate; stacked on PR #136.

## Goal

Allow an authenticated Media Portal user to paste a direct HLS or MPEG-DASH manifest URL and play it in the browser without downloading or proxying source bytes through Nolane.

## Input contract

- HTTPS URL, maximum 2,048 characters.
- Path must end in `.m3u8` (HLS) or `.mpd` (DASH).
- Reject user-info, non-default ports, URL fragments, IP literals and local/reserved hostnames.
- Preserve signed query parameters without logging them.
- URL resolution on the Worker must not fetch the supplied manifest or child resources.

## Playback

- HLS: lazily load the pinned HLS.js 1.7.4 UMD build after an explicit click. Use native HLS only where HLS.js/MSE is unavailable and the browser advertises native HLS support.
- DASH: lazily load the pinned dash.js 5.3.0 legacy UMD build after an explicit click.
- No autoplay. Use the browser's native video controls.
- Expose Auto plus manifest-derived manual video quality options when two or more representations exist.
- HLS manual selection uses `hls.currentLevel`; setting `-1` returns to ABR.
- DASH manual selection uses the relative index from `getRepresentationsByType('video')` and disables `autoSwitchBitrate.video`; Auto re-enables ABR.
- Display height and bitrate where the manifest provides them; do not invent labels for missing metadata.
- Show source-page and manifest links; do not label a manifest as a downloaded video file.

## Network policy

- Only HTTPS resources with public DNS-style hostnames are accepted by the player request filters.
- Reject credentials, non-default ports, IP literals, local/reserved hostnames and URL fragments.
- HLS.js XHR/Fetch requests are anonymous and credential-free.
- dash.js requests are restricted to GET/HEAD and use `credentials: omit`.
- Manifest child playlists, segments, subtitles and keys must meet the same HTTPS/CORS requirements.
- Native HLS fallback uses `crossOrigin=anonymous`.
- Destroy active players and remove media sources when results change.
- Do not configure EME license servers, forward cookies/authorization headers, or bypass DRM.

## CSP

Permit the pinned jsDelivr origin in `script-src`, HTTPS sources in `connect-src` and `media-src`, and `blob:` in `worker-src` and `media-src` for HLS.js worker and MSE playback. Keep iframe host validation for provider embeds unchanged.

## Tests

- Resolver: HLS and DASH recognition, query preservation, no Worker-side fetch, rejection of HTTP/local/IP/credentials/ports/fragments and unrelated file extensions.
- UI: lazy version-pinned script loading, per-resource URL guards, no-credential request mode, player cleanup, CSP and inline-script parsing, including quality selector wiring and DASH representation state.
- Full CI: typecheck, Vitest, Python runner, deployment-script checks and Worker build.

## Non-goals

No downloader, source proxy, file storage, credentials/cookies, DRM license support or arbitrary web-page extraction.
