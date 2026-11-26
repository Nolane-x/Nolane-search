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
- Storage: temporary files on the operator's local drive. No D1 media bytes, no R2, no GitHub Artifacts, no Container snapshots.
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

No files were installed on the user's computer; no secrets were read or written; no Cloudflare setting, billing plan, R2 bucket, Funnel endpoint or deployment was changed by this work.

## Verification

CI must pass on both Ubuntu and Windows for Python tests, PowerShell parser checks, TypeScript/Vitest and Worker build. Browser HLS/DASH and Safari playback suites are regressions for the existing media discovery/player UI, not proof that a live Funnel download was tested. Manual end-to-end verification remains outstanding until the operator enables the local node.


Final network rule: Python retains loopback for the local API/proxy and is blocked from private/special-use ranges; FFmpeg and Node have all outbound traffic blocked because they process local files and bundled scripts only. The installer verifies rule address filters and passes both authenticated health and HTTPS proxy smoke checks before setup is accepted.
