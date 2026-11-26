# Wave 73 research — $0 self-hosted media processing and temporary streaming

Checked: 2026-11-26
Branch: feat/wave-73-container-media-downloader
PR: https://github.com/Nolane-x/Nolane-search/pull/149
Status: Draft; not merged, not deployed, and the feature remains disabled until the operator completes local setup.

## Decision

Do not use a paid Cloudflare Worker, Cloudflare Container, Durable Object snapshot, R2, paid VM, subscription, or hosted third-party downloader API.

The selected architecture separates the application from the heavy media workload:

1. Cloudflare Workers Free remains the existing Nolane Search application, session/authentication boundary, owner authorization and streaming proxy. It makes authenticated HTTPS requests to one configured Media Node. It forwards response bodies as streams and preserves browser Range requests; it never stores media bytes.
2. Media Node runs on an existing Windows computer owned by the operator. It uses Python 3.12, SQLite, yt-dlp, yt-dlp-ejs, Node.js 22 and FFmpeg. Job metadata and temporary media files stay on that computer.
3. Tailscale Funnel Personal exposes the loopback-only Media Node over an assigned HTTPS *.ts.net host. The Python server binds to 127.0.0.1:8765; it is not opened on the LAN or router.
4. GitHub Actions is used for project CI and deployment only. It does not process end-user downloads.

This adds no recurring platform fee when using the existing computer and Internet service and an eligible Tailscale Personal account. Electricity, Internet service and the operator's own hardware are not included in the meaning of "$0".

## Why GitHub Actions is not the downloader backend

Public repositories can use GitHub-hosted standard runners without a per-minute bill, but GitHub's Additional Product Terms prohibit using Actions as a CDN or as part of a serverless application. Jobs also run on ephemeral runners; Actions artifacts are not a durable user media store. Using a workflow dispatch for every visitor request would be a poor and potentially disallowed service architecture.

Official policy:
https://docs.github.com/en/site-policy/github-terms/github-additional-product-terms

GitHub remains valuable for Linux and Windows test matrices, syntax/build validation, reproducible dependency pinning, source history, code review, issues, releases and deployment of the existing Worker.

## Why free shared containers are not selected

A free shared container or Space can be useful for a demo, preview or short CI job, but sleeping instances, ephemeral disks, runtime quotas and bandwidth ceilings are unsuitable as a dependable media-processing and share origin. A free service should not be represented as permanent storage or unlimited streaming.

Hugging Face Spaces reference:
https://huggingface.co/docs/hub/spaces-overview#hardware-resources

## Cost and platform constraints

- Cloudflare Workers Free is the existing application and proxy. Current Workers limits allow streaming responses, with no enforced response-body size limit and no hard HTTP wall-time limit while the client remains connected. CPU time is separately limited, so yt-dlp and FFmpeg processing never runs inside the Worker.
- The Worker response streaming path must pass Response.body through; it must not read the entire media into an ArrayBuffer or store media bytes in D1.
- Tailscale Funnel is beta, available on plans including Personal; Funnel bandwidth limits are non-configurable and no numeric throughput SLA is published. Funnel exposes the local service to anyone on the public Internet, so every internal API request requires a 256-bit secret and owner ID.
- Tailscale Personal is intended for personal/non-commercial use. Do not use this design as a commercial public downloader service without a plan that permits that use.
- If Funnel bandwidth or availability is insufficient, the $0 constraints and large-file public sharing requirements conflict. Reduce share sizes, use local playback or wait for a user-approved budget; do not silently migrate to a paid tier.

Official references:
- Workers limits: https://developers.cloudflare.com/workers/platform/limits/
- Tailscale Funnel: https://tailscale.com/kb/1223/funnel
- Tailscale plans: https://tailscale.com/pricing

## Security controls

- Worker validates the user's web session, private-chat identity and allowlist before starting, cancelling or sharing.
- Worker accepts only a configured HTTPS Tailscale Funnel origin (*.ts.net) and fixed /internal/... paths. It strips cookies/authorization headers, adds the 256-bit shared token and authenticated owner ID, and does not follow redirects.
- Node constant-time compares the internal token, validates owner IDs and job IDs, uses SQLite owner scoping, and logs no request paths, query strings, tokens or source URLs.
- Public share uses a random 256-bit token; only its SHA-256 hash is stored. The share token is sent over the authenticated Worker-to-node channel in a header.
- Both Worker and Node reject private, loopback, link-local, CGNAT, multicast, reserved and special-use DNS results, including IPv4-mapped IPv6 and translation prefixes.
- The Windows installer adds per-executable outbound Windows Defender Firewall blocks for Python, Node and FFmpeg to private/special-use address ranges. This second network-layer control protects against extractor redirects and DNS rebinding after the initial hostname preflight. The installer fails closed if the Windows firewall is disabled or rules cannot be installed/verified.
- No cookie import, browser profile, username/password, private account content, DRM/paywall circumvention, playlist extraction or arbitrary proxy route.
- Bounded execution: one active job, queue cap three per owner, source duration at most 2 hours, yt-dlp input file ceiling 1,400 MiB, final output ceiling 3 GiB per job, aggregate retained/in-progress media ceiling 6 GiB and a 30-minute process watchdog.
- Completed output and share links expire after 12 hours. Node serves HEAD and bounded 1 MiB HTTP Range chunks.

## Operator prerequisites

- Existing Windows 10/11 computer with Python 3.12, Node.js 22+, FFmpeg and Tailscale installed.
- Windows Defender Firewall enabled for all profiles.
- Run media-node/install.ps1 in an elevated PowerShell session; do not enable Funnel if it fails.
- Manually sign into Tailscale and run:
  tailscale funnel --bg --https=443 http://127.0.0.1:8765
- Add the resulting HTTPS Funnel URL and local 64-character secret to GitHub Actions secrets MEDIA_NODE_URL and MEDIA_NODE_TOKEN; then deploy the existing Worker workflow after the PR is accepted.
- The computer must be awake, signed in, running the scheduled Media Node task and connected to the Internet for download/playback.

## Upstream tools

- yt-dlp: https://github.com/yt-dlp/yt-dlp
- yt-dlp JavaScript challenge solving: https://github.com/yt-dlp/yt-dlp/wiki/EJS
- FFmpeg: https://ffmpeg.org/
- Tailscale Funnel: https://tailscale.com/kb/1223/funnel

This design is an owner-operated personal utility, not a 24/7 public media CDN. The PR remains draft until both Linux and Windows CI pass and the operator completes and verifies local setup.


## Official Tailscale eligibility and Funnel prerequisites

- Tailscale Personal is $0 and is for personal, non-commercial use. The Personal plan has unlimited user devices and up to six users in one tailnet.
- Funnel is beta and available on all plans; it exposes a local service through a public HTTPS Funnel URL.
- Funnel prerequisites: Tailscale v1.38.3+, MagicDNS, HTTPS certificates, and a Funnel node attribute in the tailnet policy. The CLI can prompt for approval and create the required policy attribute automatically.
- Funnel port limits: 443, 8443, or 10000; traffic has non-configurable bandwidth limits.
- Official references:
  - https://tailscale.com/pricing
  - https://tailscale.com/docs/features/tailscale-funnel
