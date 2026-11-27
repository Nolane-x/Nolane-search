# Wave 73 handoff — Museum images and zero-cost media path

Date: 2026-11-26  
Museum discovery PR: https://github.com/Nolane-x/Nolane-search/pull/150  
Zero-cost downloader PR: https://github.com/Nolane-x/Nolane-search/pull/149  
Museum branch: `feat/wave-73-met-open-access-media`  
Downloader branch: `feat/wave-73-container-media-downloader`

## Museum image discovery candidate

- The Met Open Access: current paginated `/public/collection/v1.1/search`, explicit `isPublicDomain === true`, exact official image/source hosts, CC0 metadata.
- Art Institute of Chicago: reuses the existing museum artwork search and its request throttle; only API-confirmed public-domain objects and verified museum image/object paths are shown.
- Cleveland Museum of Art Open Access: uses its public no-key API with the `cc0=1` and `has_image=1` filters; independently requires `share_license_status === "CC0"`, a canonical accession-number artwork page and a matching official web-image CDN path. Creator and artwork metadata are preserved.
- Library of Congress Prints & Photographs: one bounded public `/photos/` JSON request with no API key; only exact official item/image hosts are accepted and records with `access_restricted: true` are omitted. Item-specific `rights_advisory` / `rights` labels are retained verbatim where present; the integration does not assume all LOC images are public domain or CC0.
- All four collection providers are image-only, selectable in Media Studio, and unavailable for video/audio filters.
- The AI Agent can query The Met, Cleveland Museum and Library of Congress directly; Chicago remains available through the existing museum artwork tool.
- AI Agent exposes The Met, Cleveland Museum and Library of Congress as dedicated callable tools; Chicago remains available through the existing museum search tool.
- No API key, new secret, storage bucket, media proxy or binary copy is required for any collection image integration.

## Zero-cost video download and sharing

Use PR #149 as the separate implementation candidate for user-confirmed single-item downloads:
- Existing Cloudflare Worker Free remains the authenticated gateway and streams responses.
- yt-dlp/yt-dlp-ejs and FFmpeg run on an operator-owned Windows machine through the isolated Media Node.
- SQLite and temporary media remain on that machine; expiring share tokens and HTTP Range/HEAD support provide seekable playback.
- Tailscale Funnel Personal is the optional $0 public HTTPS ingress for personal, non-commercial use. It has non-configurable bandwidth limits and requires the host to stay online.
- GitHub Actions remains CI/CD only. Do not turn hosted Actions runners or artifacts into a user-facing CDN/backend.
- Telegram remains the existing low-friction archive/index and small-file path; it is not the large-video byte store.

**Explicit cost constraint:** do not introduce paid storage, paid compute, paid tunnels, paid media APIs or any recurring storage/compute plan. The chosen design must stay within free services and user-owned devices. No billing changes or resources are enabled by these PRs.

## Why GitHub Actions is not the media server

GitHub's Additional Product Terms explicitly prohibit using Actions as a CDN or as part of a serverless application backend. Artifacts are temporary workflow outputs with retention/storage quotas, not a durable private file service. Keep GitHub for source, releases of the software itself, CI, tests, deployment, and reviewed automation—not per-user media hosting.

## Verification and operator boundary

- CI is the authority for code/test/build status. A green run does not mean the local Media Node is installed or live.
- PR #149 remains a draft until local Windows install, network hardening and a real HTTPS share/Range smoke test are completed.
- PR #150 remains a draft until its current CI run passes and the UI/API behavior is reviewed.
- Do not deploy or claim a working public download endpoint until the owner completes the local node setup and supplies its URL/token through repository secrets.


---

## Detailed Media Node handoff from the downloader branch

# Wave 73 handoff — zero-cost self-hosted Media Node

Date: 2026-11-26
Branch: feat/wave-73-container-media-downloader
PR: https://github.com/Nolane-x/Nolane-search/pull/149
State: Draft / open / unmerged / undeployed. No paid feature, cloud resource, tunnel or storage bucket has been enabled.

## What changed

The original Cloudflare Container and Durable Object snapshot prototype is being replaced with a personal Media Node.

- Cloudflare Worker: existing Free plan, user session and owner access checks, node request authentication, Range-preserving response streaming.
- Local Windows Media Node: Python 3.12 service, SQLite job state, yt-dlp + yt-dlp-ejs + Node 22, FFmpeg.
- Public HTTPS ingress: Tailscale Funnel Personal pointing to 127.0.0.1:8765.
- Storage: temporary files on the operator's local drive. Media bytes are not sent to the database, GitHub Actions artifacts or a hosted bucket.
- GitHub Actions: CI/CD only, never per-user download compute.

## Operational limits

- One download process at a time.
- At most three queued/running jobs per owner.
- Maximum source duration 7,200 seconds.
- yt-dlp input file guard 1,400 MiB; final output ceiling 3 GiB per job; total local retained/in-progress media ceiling 6 GiB.
- 30-minute job watchdog.
- Completed file retention 12 hours; public share token TTL 12 hours.
- MP4 video up to 1080p or MP3 audio 192 kbps.
- No credentials, browser cookies, private account content, playlists, DRM/paywall bypass or generic URL proxy.
- The host must be awake and online. Funnel is beta with non-configurable bandwidth limits and no published numeric throughput SLA.
- Tailscale Personal is for personal/non-commercial use only; this branch is not a commercial service.

## Files

- media-node/server.py: local API, URL/DNS policy, SQLite store, worker, output checks and Range/HEAD streaming.
- media-node/requirements.txt: pinned yt-dlp packages.
- media-node/install.ps1: fail-closed Windows prerequisites, firewall policy, local token and scheduled task.
- media-node/start.ps1, uninstall.ps1, .env.example and README.md: operator lifecycle/setup.
- src/media-downloader.ts: strict Tailscale Funnel origin/path request helper.
- src/index.ts: owner authorization, node requests and streamed share route.
- src/types.ts and cloudflare.config.ts: Worker Free-only bindings.
- tests/media-downloader.test.ts and media-node/test_server.py: policy and API tests.
- docs/superpowers/specs/2026-11-26-zero-cost-media-node-design.md: design.
- docs/superpowers/plans/2026-11-26-zero-cost-media-node.md: execution checklist.

## Manual owner steps — not yet done

1. Ensure required software is already installed on the Windows host: Python 3.12, Node.js 22+, FFmpeg and Tailscale.
2. Run media-node/install.ps1 from an elevated PowerShell session. This installs local Python packages and Windows Firewall rules; it fails closed if any rule cannot be verified.
3. Verify local service logs and then manually enable Funnel:
   tailscale funnel --bg --https=443 http://127.0.0.1:8765
   tailscale funnel status
4. Copy only the HTTPS Funnel URL and generated 64-character local token to GitHub Actions secrets MEDIA_NODE_URL and MEDIA_NODE_TOKEN. Never commit or message the token.
5. After PR merge is explicitly authorized, run the normal deploy workflow. Until these secrets are configured, the feature stays disabled.

No files were installed on the user's computer; no secrets were read or written; no account setting, billing plan, Funnel endpoint or deployment was changed by this work.

## Verification

CI must pass on both Ubuntu and Windows for Python tests, PowerShell parser checks, TypeScript/Vitest and Worker build. Browser HLS/DASH and Safari playback suites are regressions for the existing media discovery/player UI, not proof that a live Funnel download was tested. Manual end-to-end verification remains outstanding until the operator enables the local node.


Final network rule: Python retains loopback for the local API/proxy and is blocked from private/special-use ranges; FFmpeg and Node have all outbound traffic blocked because they process local files and bundled scripts only. The installer verifies rule address filters and passes both authenticated health and HTTPS proxy smoke checks before setup is accepted.
