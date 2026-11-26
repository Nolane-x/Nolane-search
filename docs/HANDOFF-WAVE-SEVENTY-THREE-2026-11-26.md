# Wave 73 handoff — Museum images and zero-cost media path

Date: 2026-11-26  
Museum discovery PR: https://github.com/Nolane-x/Nolane-search/pull/150  
Zero-cost downloader PR: https://github.com/Nolane-x/Nolane-search/pull/149  
Museum branch: `feat/wave-73-met-open-access-media`  
Downloader branch: `feat/wave-73-container-media-downloader`

## Museum image discovery candidate

- The Met Open Access: current paginated `/public/collection/v1.1/search`, explicit `isPublicDomain === true`, exact official image/source hosts, CC0 metadata.
- Art Institute of Chicago: reuses the existing museum artwork search and its request throttle; only API-confirmed public-domain objects and verified museum image/object paths are shown.
- Both providers are image-only, selectable in Media Studio, and unavailable for video/audio filters.
- AI Agent exposes The Met as a dedicated callable tool; Chicago remains available through the existing museum search tool.
- No API key, new secret, storage bucket, media proxy or binary copy is required.

## Zero-cost video download and sharing

Use PR #149 as the separate implementation candidate for user-confirmed single-item downloads:
- Existing Cloudflare Worker Free remains the authenticated gateway and streams responses.
- yt-dlp/yt-dlp-ejs and FFmpeg run on an operator-owned Windows machine through the isolated Media Node.
- SQLite and temporary media remain on that machine; expiring share tokens and HTTP Range/HEAD support provide seekable playback.
- Tailscale Funnel Personal is the optional $0 public HTTPS ingress for personal, non-commercial use. It has non-configurable bandwidth limits and requires the host to stay online.
- GitHub Actions remains CI/CD only. Do not turn hosted Actions runners or artifacts into a user-facing CDN/backend.
- Telegram remains the existing low-friction archive/index and small-file path; it is not the large-video byte store.

**Explicit cost constraint:** do not introduce Cloudflare R2, paid Containers, paid VMs, paid tunnels, paid media APIs, or any recurring storage/compute plan. No billing changes or resources are enabled by these PRs.

## Why GitHub Actions is not the media server

GitHub's Additional Product Terms explicitly prohibit using Actions as a CDN or as part of a serverless application backend. Artifacts are temporary workflow outputs with retention/storage quotas, not a durable private file service. Keep GitHub for source, releases of the software itself, CI, tests, deployment, and reviewed automation—not per-user media hosting.

## Verification and operator boundary

- CI is the authority for code/test/build status. A green run does not mean the local Media Node is installed or live.
- PR #149 remains a draft until local Windows install, network hardening and a real HTTPS share/Range smoke test are completed.
- PR #150 remains a draft until its current CI run passes and the UI/API behavior is reviewed.
- Do not deploy or claim a working public download endpoint until the owner completes the local node setup and supplies its URL/token through repository secrets.
