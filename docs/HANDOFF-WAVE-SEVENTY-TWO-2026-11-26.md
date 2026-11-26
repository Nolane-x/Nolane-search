# Wave 72 handoff — 2026-11-26

**Branch:** `feat/wave-72-inaturalist-media-search`  
**Merged:** PR [#148](https://github.com/Nolane-x/Nolane-search/pull/148) merged into `main` as `039514d03dfb1fa9f7fa2c6fbae9d8136812b051`  
**Scope:** practical discovery tools and media architecture research  
**Production deployment:** Cloudflare Deploy #179 succeeded on 2026-11-26. Worker Version ID: `587cbb01-8adc-45d9-b7d0-a3c1d2df456f`. Telegram webhook, bot command registration and Telegram Mini App route smoke passed.

## Released in Wave 72

### 1. Licensed nature media discovery

- Added `search_inaturalist_observations` to the media discovery engine and AI Agent.
- Integrated iNaturalist as a searchable image provider in `/api/media/search` and Media Studio.
- Only surfaces research-grade observations with a recognized CC0/Creative Commons license, a non-empty attribution string, and an image URL on the iNaturalist Open Data S3 host.
- Returns observation source page, preview/original URLs, credit, license, dimensions and date when available.
- Omits exact observation coordinates.
- Supports bounded optional taxonomic filters: Animalia, Plantae, Fungi, Aves, Mammalia, Insecta, Reptilia and Amphibia.

### 2. City-named public place discovery

- Added `search_places_in_city` to the AI Agent.
- Geocodes only the city/town explicitly provided by the user, optionally constrained by ISO country code.
- Returns clarification choices rather than guessing when the same city name maps to multiple plausible country/region records.
- Calls the existing OpenStreetMap category search only after an unambiguous city is selected.
- Preserves current limits, category filtering, OSM attribution and straight-line/opening-hours caveats.
- Leaves `search_nearby_places` unchanged: that tool still requires coordinates deliberately supplied/shared by the user.

### 3. Tests added

- iNaturalist tests cover endpoint/parameters, research-grade results, license mapping, allowed Open Data photo host, exclusion of unlicensed/unrecognized/other-host photos, no-coordinate output, bounds and Agent dispatch.
- Nearby tests cover explicit city resolution, ISO country filtering, OSM query coordinates, ambiguous city clarification, preflight validation and Agent-tool dispatch.
- PR CI #676 passed: TypeScript, **41 Vitest files / 434 tests**, deployment checks, **449 Python runner tests** and Worker build. Main CI #677 also passed the same checks.
- Real Apple Safari native-HLS test #11 passed on macOS Safari; Chromium HLS/DASH playback matrix #47 passed. These validate the tested browser/source matrix, not every public stream or physical iOS device.
- Cloudflare deployment #179 passed Worker upload, Telegram webhook verification, command registration and Mini App smoke. Worker export #172 passed.

## Downloader: researched, not enabled

OpenGrab, yt-dlp, gallery-dl, FFmpeg and aria2 were reviewed as potential upstream engines. OpenGrab is self-hosted and documents host-level egress filtering as a second SSRF defense. It is a reference application, not a remote API backend. OmniGet is also a desktop/local-service reference; do not copy GPL-3.0 application source without license review. Cobalt is now the preferred self-hosted API prototype candidate: it offers URL processing and temporary stream/tunnel responses across a broad service matrix, but its API is AGPL-3.0, its separate web UI is CC-BY-NC-SA-4.0/non-commercial, and upstream explicitly disallows using the public hosted API in third-party projects without permission. MeTube is another self-hosted yt-dlp UI reference, not a ready Cloudflare API. See the expanded candidate comparison in the research document.

A universal downloader was deliberately not enabled because the runner still needs enforceable network egress protection against private IPs, metadata endpoints, redirects and DNS rebinding. Public-site extraction must not use cookies, logged-in sessions or DRM/paywall bypasses. Use fixed arguments and bounded job resources.

## Large file storage blocker

The Wave 62 R2 architecture remains unchanged: private R2 object storage + D1 metadata + short-lived owner-authorized links + HTTP Range streaming. The last account check returned Cloudflare R2 error `10042` (R2 must be enabled in Dashboard), and no R2 binding/credentials are configured. Telegram `getFile` remains capped at 20 MB. Do not claim large-video links work until R2 is enabled and upload, checksum, Range, expiry and deletion tests pass.

## Files changed

- `src/media-discovery-tools.ts`
- `src/agent-tools.ts`
- `src/index.ts`
- `src/media-ui.ts`
- `src/nearby-places-tools.ts`
- `tests/media-discovery-tools.test.ts`
- `tests/nearby-places-tools.test.ts`
- `tests/agent-tools.test.ts`
- `tests/media-ui.test.ts`
- `docs/TOOL-RESEARCH-2026-11-26-WAVE72-NATURE-LOCAL-DOWNLOADER.md`
- `docs/HANDOFF-WAVE-SEVENTY-TWO-2026-11-26.md`

## Next steps

1. Build a private, isolated downloader prototype around the Cobalt API or a separately sandboxed yt-dlp worker only after reviewing the upstream license and implementing runner-level egress protection plus SSRF/redirect/DNS-rebinding regression tests.
2. Keep the public downloader gated until per-user authentication, quotas, file/duration caps, cancellation, job cleanup and rights guidance are in place.
3. Ask the account owner to enable Cloudflare R2 (the previous account response was error `10042`), then implement multipart upload, checksum verification, private short-lived share links, HTTP Range playback/download, expiry and deletion.
4. Do not treat Telegram's 20 MB `getFile` limit as a path for delivering larger media. Use the private web-media flow only after the R2 lifecycle is tested.
