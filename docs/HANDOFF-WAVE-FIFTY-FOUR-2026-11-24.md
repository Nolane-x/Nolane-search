# Wave 54 handoff — Open media source expansion

Date: 2026-11-24  
Branch: feat/wave-54-open-media-sources  
Base: 5611d2cd2595767a72df89ecc821b36a0a445965  
Release status: merged and deployed via [PR #114](https://github.com/Nolane-x/Nolane-search/pull/114) as `8c3d05d40c93be76a28244e792aeb6e3b5990c9a`.

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

## Production verification — 2026-11-24

- PR CI #500 [45412093218](https://github.com/Nolane-x/Nolane-search/actions/runs/45412093218) passed TypeScript, 32 Vitest files / 333 tests, deployment checks, 449 Python runner tests and Cloudflare Worker build.
- Main CI #501 [45412464406](https://github.com/Nolane-x/Nolane-search/actions/runs/45412464406) passed the same verification set.
- Cloudflare deploy #158 [45412464223](https://github.com/Nolane-x/Nolane-search/actions/runs/45412464223) succeeded. Worker Version ID: `a53eafb0-631a-48dd-a65d-ea44af3fbcd7`.
- Worker export #151 [45412464207](https://github.com/Nolane-x/Nolane-search/actions/runs/45412464207) and public health smoke succeeded. Health response: `ok: true`, database `reachable`, archive enabled.
- Telegram webhook and command registration succeeded. No D1 migration was required.
- The CI and health smoke verify code/build/deployment health, not every live upstream search response. A live query/rights check against Openverse and Internet Archive remains separate; public data availability and item-specific reuse rights can vary.
