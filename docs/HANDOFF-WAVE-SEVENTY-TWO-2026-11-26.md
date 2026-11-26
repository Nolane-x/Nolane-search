# Wave 72 handoff — 2026-11-26

**Branch:** `feat/wave-72-inaturalist-media-search`  
**Base:** `main` at Wave 71  
**Scope:** practical discovery tools and media architecture research  
**Deployment:** not deployed; this handoff records branch work only.

## Completed on this branch

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
- CI/typecheck/test results must be read from this PR's GitHub Actions runs. Do not mark these changes as passed until the runs complete.

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

## Next steps

1. Run PR CI, typecheck and complete Vitest/Python runner test suites; fix any failures.
2. Merge/deploy only after checks are green; then update `docs/STATUS.md`.
3. Keep the downloader gated until runner-level egress controls and SSRF regression tests exist.
4. Ask the account owner to enable R2 in Cloudflare; then implement and test multipart upload, checksum verification, authenticated playback/download with HTTP Range, expiry and cleanup.
