# Wave 73 handoff — 2026-11-26

Branch: feat/wave-73-container-media-downloader  
Base: current main after Wave 72  
Scope: private, feature-gated yt-dlp/FFmpeg Container downloader and temporary Range share prototype  
Merge/deploy: not merged or deployed. Keep both feature switches off.

## What has been built on this branch

### 1. Container downloader service

- Docker image: Node 22, Python 3, yt-dlp, yt-dlp-ejs, FFmpeg, tini and util-linux.
- yt-dlp pinned at 2026.11.23; EJS component 0.8.0.
- Private Python HTTP service with a per-owner internal token, no URL access logs, a single active job, cancellation, progress, MP4/MP3 output and Range/HEAD/GET serving.
- Runs as unprivileged UID 10001. Extractor arguments are passed as an argv array, not a shell string. Browser cookies, login profiles, usernames/passwords, playlist processing and metadata files are disabled.
- Limits: 1080p maximum, one item, source duration up to 2 hours, 3 GiB output ceiling, 1,400 MiB extractor estimate ceiling and 30-minute process watchdog.

### 2. Worker control plane and egress policy

- Added TypeScript URL normalization, reserved/private IP checks and DoH A/AAAA checks that fail closed.
- Added MediaDownloaderEgress WorkerEntrypoint. The Container starts with enableInternet=false; outbound HTTP/HTTPS is intercepted by Worker code, which removes authorization/cookie/forwarding headers, validates host/DNS and uses manual redirects so later hops are rechecked.
- Added MediaDownloader Durable Object, one named instance per allowlisted owner, owner-only start/status/cancel, internal token, progress polling, snapshot state, share-token rotation and revoke.
- Explicitly note residual DNS time-of-check/time-of-use: DNS is checked before Worker fetch, but the Worker fetch does not pin the resolver answer to a socket IP. Keep the feature off until a dedicated security review/adversarial test proves the deployment-specific egress boundary is acceptable.

### 3. Temporary web sharing

- A successful job is snapshotted; media bytes stay out of D1 and Telegram.
- Share links use a random 256-bit bearer token and store only its hash in Durable Object SQLite state.
- Browser player supports GET/HEAD and HTTP Range; private no-store headers are used.
- Link expiry: 12 hours. Share token can be rotated or revoked.
- Cloudflare snapshot is public beta, cannot be manually deleted, and can remain up to 30 days after last restore. The implementation allows only one retained snapshot per owner and blocks a new download until 30 days after the last restore (or initial snapshot creation if never restored). Revoking link access does not delete the snapshot.

### 4. Feature gates

- MEDIA_DOWNLOADER_CONTAINER_ENABLED: GitHub Actions secret. When true, programmatic config defines the Container image and DO export.
- MEDIA_DOWNLOADER_ENABLED: Cloudflare runtime secret. Must also be true before Media Studio/Worker accepts download jobs. Deployment writes false when unset.
- Do not set either secret or deploy with the Container enabled until the owner confirms Workers Paid, Container availability and the security review. No Paid billing change or R2 activation was made by this branch.

## Known limitations / blockers

1. R2 remains disabled. The Cloudflare API was checked and still returns HTTP 403 / code 10042, requiring activation in Dashboard. R2-based durable storage is still the long-term option.
2. Cloudflare Containers require Workers Paid, use metered compute, and durable_object scheduling/snapshots are public beta. The connected account's plan has not been confirmed for this deployment.
3. Snapshot retention is not deletion: the application invalidates links, but Cloudflare snapshots expire automatically up to 30 days after last restore and cannot be manually deleted. One active snapshot per owner is enforced to avoid accumulation.
4. yt-dlp extractor coverage is not a guarantee. Provider changes, georestrictions, rate limits, codecs and content rights affect individual URLs.
5. No gallery-dl image-gallery support, no multi-item playlists, no logged-in sources, no DRM/paywall bypass, no permanent share links.

## Files changed / added

- cloudflare.config.ts
- src/types.ts
- src/index.ts
- src/media-ui.ts
- src/media-downloader-policy.ts
- src/media-downloader.ts
- media-downloader/Dockerfile
- media-downloader/entrypoint.sh
- media-downloader/server.py
- media-downloader/test_server.py
- tests/media-downloader-policy.test.ts
- tests/media-ui.test.ts
- tests/cloudflare-workers.ts (Vitest-only Cloudflare runtime shim)
- vitest.config.ts (Node test-only alias; not used by production Worker builds)
- .github/workflows/ci.yml
- .github/workflows/deploy.yml

Research: docs/TOOL-RESEARCH-2026-11-26-WAVE73-DOWNLOADER-CONTAINERS.md.

## Required verification before merging

- TypeScript typecheck and full Vitest suite pass.
- Python downloader server tests pass.
- Docker image builds; the container internal health endpoint succeeds with the random internal token and returns 401 without it.
- Cloudflare Worker build passes with the default feature gates off and with `MEDIA_DOWNLOADER_CONTAINER_ENABLED=true` (opt-in config validation only; no deploy).
- Adversarial SSRF/redirect/DNS-rebinding review is recorded. A green build is not proof of safe egress.
- Do not merge/deploy the Container path unless the account owner has confirmed Workers Paid and explicitly chosen to enable the feature.
