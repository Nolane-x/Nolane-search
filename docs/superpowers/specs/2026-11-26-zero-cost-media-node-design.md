# Zero-cost self-hosted Media Node — Design

Date: 2026-11-26
Status: proposed implementation in PR #149; not deployed.

## Intent

Replace the Wave 73 Cloudflare Containers and Durable Object snapshot design with a no-subscription media downloader that uses the existing Cloudflare Workers Free deployment and a computer already owned by the operator.

## Goals

- Download one public video or audio item supported by yt-dlp.
- Produce MP4 video up to 1080p or MP3 audio at 192 kbps.
- Run jobs on an operator-controlled Windows machine, with SQLite metadata and temporary local file storage.
- Preserve owner-only create, inspect, cancel, renew-share and revoke operations in Media Studio.
- Share a completed file temporarily with HTTP Range support for browser seeking.
- Keep GitHub Actions as CI/CD only; do not use hosted Actions runners as a user-facing backend.
- Avoid paid Workers, R2, hosted compute, external media storage and paid tunnel plans.

## Non-goals

- 24/7 availability when the operator's computer or network is offline.
- Unlimited bandwidth, permanent storage or CDN-like distribution.
- Public multi-user downloader service.
- Authenticated downloads, browser cookies, login material, DRM or paywall circumvention, playlists, or arbitrary proxying.

## Hard constraints

- Additional recurring platform charge: $0. Existing electricity and Internet service are assumed.
- Node service binds only to 127.0.0.1:8765.
- Public ingress uses Tailscale Funnel over HTTPS on the assigned *.ts.net hostname.
- Tailscale Personal is free for personal non-commercial use. Funnel is beta and has non-configurable bandwidth limits; the official documentation does not provide a numeric throughput guarantee.
- Worker requires the existing Workers Free plan only. It proxies media response bodies as streams; it does not buffer or persist them.
- Local media files and share links expire after 12 hours.
- Operator manually signs into Tailscale, approves Funnel, and adds MEDIA_NODE_URL and MEDIA_NODE_TOKEN to GitHub Actions secrets.
- The feature remains disabled until both secrets are configured and validated.
- PR remains draft; this work does not deploy or modify billing.

## Approaches considered

1. GitHub Actions per-download backend — rejected. Hosted runners are available without charge for public repositories, but GitHub's Additional Product Terms prohibit using Actions as a CDN or serverless application backend. Runners are ephemeral and artifacts are not durable media storage.
2. Free hosted containers or Spaces — rejected as the core runtime. Free plans can sleep, lack persistent storage, cap bandwidth/runtime, or reserve persistent Docker/Gradio runtimes for paid subscriptions. They cannot provide a robust durable media service at $0.
3. Self-hosted Media Node plus Tailscale Funnel plus Workers Free — selected. yt-dlp and FFmpeg run on the operator's own host; SQLite and media files remain local; Funnel exposes only the loopback-bound API over HTTPS; Worker handles application auth and streams media responses to the browser.

## Security and operations

- Worker requires a valid web session, private chat owner identity and allowlist before dispatch.
- Worker-to-node requests carry a 256-bit random shared token and the verified owner ID.
- Node internal routes require both headers. Health is also protected.
- Node stores only SHA-256 hashes of temporary share tokens.
- URL policy accepts public HTTP(S) hostnames only, rejects userinfo, unusual ports, IP literals and internal names.
- yt-dlp is forced through a bounded loopback HTTP/CONNECT egress proxy. Every initial URL and redirect is resolved immediately before connection; all DNS answers must be globally routable; sockets connect to the already-validated numeric address, preventing DNS rebinding between validation and connect. Only ports 80 and 443 are supported.
- Windows installer adds program-scoped outbound firewall rules: Python is blocked from private, link-local, CGNAT, reserved IPv4 and special IPv6 ranges while retaining loopback for the local API/proxy; FFmpeg and Node are blocked from all outbound destinations because they perform local-only work. The installer verifies the configured remote-address filters and fails closed if firewall and local proxy smoke checks cannot be installed and verified.
- No generic proxy, filesystem endpoint, cookie support, browser profiles, or credentials.
- One exclusive Media Node process per data directory, one active download globally, at most three queued or running jobs for the owner.
- Max source duration 7,200 seconds, output 3 GiB per job, total retained/in-progress media 6 GiB, watchdog 30 minutes.
- Cancel terminates the process tree; expired files are removed by the local cleanup job.
- HTTP Range and HEAD are streamed in bounded chunks. Never load the entire file into memory.
- Tailscale Funnel's beta status and unquantified bandwidth limits mean no throughput SLA can be promised.

## Acceptance

- Python policy, store, job, cancellation, security and Range tests pass on Ubuntu and Windows.
- Worker tests validate the *.ts.net origin allowlist, secret and owner headers, and fixed internal route paths.
- Existing TypeScript suite, type-check and Worker build pass.
- CI no longer builds Cloudflare Containers.
- Docs include setup requirements, personal/non-commercial restriction, bandwidth/uptime caveats and manual secret setup.
