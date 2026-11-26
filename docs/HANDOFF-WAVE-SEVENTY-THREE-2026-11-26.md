# Wave 73 handoff — The Met Open Access

Date: 2026-11-26  
PR: https://github.com/Nolane-x/Nolane-search/pull/150  
Branch: `feat/wave-73-met-open-access-media`  
Status: candidate; update after CI, review, merge and deployment.

## Candidate changes

- Add The Met as an image-only Media Studio source.
- Add callable Agent tool `search_met_open_access_artworks`.
- Use current paginated `/public/collection/v1.1/search`.
- Require a positive public-domain flag and validate all returned image/source URLs against exact official hosts.
- Preserve title, artist, date, medium, collection credit and CC0 metadata.
- Leave video and audio provider behavior unchanged.

## Verification

CI is the authority for test/build status. Do not change production Wave 72 status until this PR is merged and deployment/smoke checks pass.

## Remaining media roadmap

1. Downloader metadata inspection through a private, isolated worker, with no public arbitrary-URL execution until network egress/SSRF restrictions are proven.
2. User-confirmed single-item downloads using pinned yt-dlp / Cobalt, subject to provider terms, no DRM bypass, resource quotas, cancellation and cleanup.
3. Activate private R2 storage before enabling durable large-file sharing. Telegram should carry only the short-lived link, not the media binary.
4. Implement owner-scoped expiring share tokens and HTTP Range support for seekable private playback after R2 is available.
