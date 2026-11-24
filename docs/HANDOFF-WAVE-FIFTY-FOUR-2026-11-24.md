# Wave 54 handoff — Open media source expansion

Date: 2026-11-24  
Branch: feat/wave-54-open-media-sources  
Base: 5611d2cd2595767a72df89ecc821b36a0a445965  
Release status: implementation branch; not yet merged or deployed.

## New AI-callable media tools

- search_openverse_images — openly licensed image search with creator, CC license code/version, thumbnail and original source.
- search_internet_archive_videos — public movie item search; returns a player/download link only when a non-private original video file is present in archive metadata.

## Media Portal updates

- Adds Openverse and Internet Archive to the source selector.
- Image sources: Wikimedia Commons, Openverse and NASA.
- Video sources: NASA and Internet Archive.
- Provider calls are independent. A failed/rate-limited source becomes a warning; successful sources can still return results.
- UI embeds only allowlisted preview/media hosts. Openverse full-size image URLs are links only.
- Existing private Telegram-issued web session remains required.

## Code changes

- src/media-discovery-tools.ts: bounded Openverse and Internet Archive provider adapters, metadata normalization and AI dispatch.
- src/agent-tools.ts: schemas for both new tools and agent dispatch.
- src/index.ts: authenticated multi-source Media Portal API with partial-provider failure handling.
- src/media-ui.ts: source selector, preview/player host rules and CSP additions.
- tests/media-discovery-tools.test.ts and tests/agent-tools.test.ts: provider and tool-registration tests.

No new dependency, secret, D1 migration or file processor is introduced. The existing 534 file processors remain unchanged.

## Rights, privacy and safety

- Openverse records without a valid HTTPS source, thumbnail or Creative Commons license URL are omitted. Preserve the creator/source/license and check whether the particular CC license permits the intended use.
- Internet Archive results are capped to five items; metadata requests only inspect validated item IDs. Access-restricted/noindex items, private files, unsafe filenames and non-original derivatives are omitted.
- Internet Archive rights differ by item. When license metadata is absent, results say “Rights not specified” or show the unverified rights statement; they do not claim that a downloadable file is public domain.
- No item bytes are downloaded or rehosted by Nolane.

## Not solved by this wave

- Arbitrary video URL extraction across hundreds of sites using yt-dlp/gallery-dl is not enabled.
- R2 private storage, multipart upload, signed playback/share links, Range playback and expiry cleanup remain pending the account owner's R2 activation.
- No DRM, paywall or access-control bypass is offered.

## Acceptance gates

1. PR CI passes type-check, Vitest, deployment-script checks, Python runner tests and Cloudflare Worker build.
2. Main CI, Cloudflare deploy and Worker export/health smoke pass after merge.
3. Live Openverse and Archive query tests should be run after deploy; provider data completeness and item-specific legal rights are separate from code tests.
