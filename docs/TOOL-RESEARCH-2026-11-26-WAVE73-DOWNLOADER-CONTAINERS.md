# Wave 73 research — self-hosted media downloader and temporary streaming

Checked: 2026-11-26  
Branch: feat/wave-73-container-media-downloader  
State: implementation prototype; feature flag is disabled by default. Not deployed.

## 1. Goal and architecture

Wave 72 closed two discovery gaps (licensed nature photos and city-based place discovery), but Media Studio still could not download source media or share large output files. The GitHub Actions runner is suitable for one-shot file processing, but not a long-running media download service and browser Range streaming.

Wave 73 prototypes a private Cloudflare Container attached to a per-owner Durable Object. The Container runs Node 22, Python, yt-dlp and FFmpeg. The Worker remains the control plane: authenticate the owner, validate URL/options, create a bounded job, poll progress, issue time-limited share tokens and stream Range requests. D1 and Telegram do not hold media bytes.

The chosen engine is yt-dlp, not a hosted third-party API. The image pins yt-dlp[default] 2026.11.23 and yt-dlp-ejs 0.8.0; Node 22 is available as the JavaScript runtime for extractors that require challenge solving. FFmpeg performs audio extraction and media muxing.

Upstream references:
- yt-dlp: https://github.com/yt-dlp/yt-dlp
- yt-dlp EJS: https://github.com/yt-dlp/yt-dlp/wiki/EJS
- FFmpeg: https://ffmpeg.org/
- OpenGrab (UI/queue reference): https://github.com/Skydope/OpenGrab
- MeTube (UI/queue reference): https://github.com/alexta69/metube
- Cobalt API (alternative self-hosted API; AGPL-3.0): https://github.com/imputnet/cobalt

This prototype does not copy OmniGet, OpenGrab, MeTube or Cobalt source/UI. It independently composes yt-dlp and FFmpeg. gallery-dl/image-gallery support is not included yet.

## 2. Cloudflare requirements and constraints

Official documentation:
- Containers scheduling policies: https://developers.cloudflare.com/containers/configuration/scheduling-policy/
- Outbound interception: https://developers.cloudflare.com/containers/configuration/outbound-traffic/
- Durable Object Container API: https://developers.cloudflare.com/containers/api/durable-object-container/
- Snapshots: https://developers.cloudflare.com/containers/guides/snapshots/
- Limits and instance types: https://developers.cloudflare.com/containers/platform/limits/
- Programmatic cloudflare.config.ts: https://developers.cloudflare.com/cf/projects/cloudflare-config/

The implementation uses the durable_object scheduling policy (public beta), with standard-1 selected at runtime. The documented default size is 0.5 vCPU, 4 GiB RAM and 8 GB disk. Containers require Workers Paid. The owner has not confirmed a Paid plan, so this code is not enabled.

The Container starts with enableInternet=false. Every HTTP request and every HTTPS request is intercepted by a WorkerEntrypoint. The egress Worker strips cookies, authorization, proxy credentials, Worker-internal headers and forwarding headers; accepts only public HTTP(S) hosts; checks A/AAAA DNS answers; sends redirects back as manual responses; and applies the policy again when yt-dlp follows a redirect. Non-HTTP(S) egress and direct DNS are blocked by the Container network policy.

Security caveat: the DNS check and the subsequent Worker fetch are separate resolution operations; this prototype does not pin an IP address at the socket layer. It therefore must not be described as a complete DNS-rebinding proof. It is owner-only and remains feature-gated pending a dedicated SSRF/egress review and adversarial tests for DNS changes, redirects, unusual URL forms and provider behavior.

## 3. Download policy and resource bounds

First supported outputs:
- Video: MP4, maximum selected height 1080p (best is capped at 1080p).
- Audio: MP3 at 192 kbps.
- One media item only; playlists are disabled.
- Source duration ceiling: 2 hours.
- Output file ceiling: 3 GiB (also enforced with a process file-size limit).
- Extractor download estimate ceiling: 1,400 MiB.
- One active job per owner/DO.
- Maximum extractor process runtime: 30 minutes; cancellation kills the process group.
- Container service runs as unprivileged Linux user UID 10001, does not log request URLs, and accepts no browser cookies, login profiles, usernames or passwords.
- No DRM/paywall bypass or logged-in content is supported. Users must only download material they have the right to access and save.

The Worker validates the submitted URL before dispatch. It rejects non-HTTP(S) schemes, IP literals (including IPv4-mapped and obfuscated numeric forms), reserved/local hostnames, URL credentials, custom ports, fragments and control characters. DNS checks fail closed when the resolver returns private, link-local, loopback, CGNAT, ULA, multicast, reserved or no address. The Container has no direct Internet or DNS route.

A supported yt-dlp extractor does not mean every site/video is guaranteed to work; site changes, geo restrictions, rate limits, codecs and legal rights still apply.

## 4. Temporary share and Range streaming

R2 remains disabled on the connected Cloudflare account. A live R2 bucket was checked through Cloudflare API and returned HTTP 403 / code 10042 ("Please enable R2 through the Cloudflare Dashboard"). Wave 73 therefore prototypes temporary Container snapshots rather than pretending R2 is available.

On successful download:
1. The Durable Object validates output metadata and snapshots the Container filesystem.
2. The snapshot handle is stored in DO SQLite state; media bytes are not written to D1 or Telegram.
3. The Container is destroyed.
4. An owner-authorized, random 256-bit share token is issued only after the snapshot exists. Only the token hash is stored.
5. The public player validates the token and streams media through the Container TCP port with HTTP Range support, private no-store caching and no-referrer policy.

Application-level link expiry is 12 hours. The owner can rotate the token or revoke it; revocation prevents future requests but cannot delete the underlying snapshot. The snapshot API is public beta, snapshots are immutable, and Cloudflare documents automatic expiry up to 30 days after the last restore; there is no manual delete/list API.

To avoid accumulating snapshots, the prototype retains at most one snapshot per owner and blocks a new download until 30 days after the last restore (or initial snapshot creation if it was never restored). Revoking a share does not shorten the physical snapshot retention window.

This is temporary sharing, not permanent object storage. If frequent or durable sharing is required, enable R2 and replace snapshots with a private R2 bucket, multipart uploads, checksum verification, short-lived authorized links and Range streaming.

## 5. Feature gate and deployment state

Two independent switches protect the feature:
- MEDIA_DOWNLOADER_CONTAINER_ENABLED: GitHub Actions secret. When true, the programmatic config defines the Container application and DO export.
- MEDIA_DOWNLOADER_ENABLED: Cloudflare runtime secret. Must also be true before Media Studio/API accepts download jobs. Deploy defaults it to false when unset.

Both must be explicitly configured by the account owner after confirming Workers Paid and Container availability. If either is absent, the API returns 503 and the UI stays disabled. No Paid plan, Container or R2 resource is activated by this branch.

## 6. Test plan

The branch adds:
- TypeScript URL/IP/DNS policy tests, including numeric IP obfuscation and reserved IPv6 ranges.
- Python service tests for UUID job IDs, fixed argument arrays, no credential inputs, safe output paths, symlink rejection, supported MIME types and HTTP Range edge cases.
- CI steps that build the Docker image, run its private health endpoint with an internal token and verify the unauthenticated endpoint returns 401.
- Existing full Worker Vitest/typecheck/build and 449-test Python file-runner suite remain required.

A passing unit/build test does not establish that Containers are enabled on this account or prove every third-party extractor works. No production download or public share link is claimed until the owner enables the required plan/switches and an end-to-end smoke test is performed.

## 7. Next gates

1. CI must pass TypeScript, Vitest, Python service tests, Docker build/private endpoint smoke and Worker build.
2. Review Container outbound interception and DNS-rebinding residual risk before enabling.
3. Confirm Workers Paid and Container beta availability with the account owner; do not silently change billing.
4. If frequent or durable sharing is required, enable R2 and move completed files to private R2 instead of retaining Container snapshots.
