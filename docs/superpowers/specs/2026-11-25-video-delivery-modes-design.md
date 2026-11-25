# Media delivery methods — design

Date: 2026-11-25
Status: implementation design; staged delivery, not a claim that all methods are shipped.

## Intent

Make Nolane Search useful for media discovery, playback and user-authorized downloads without requiring a persistent object-storage subscription. A result must expose the methods that its source actually supports rather than treating every media URL as a downloadable file.

## User-facing methods

1. **Official embed** — load a provider's own player in a sandboxed iframe only after the user asks to play it. Examples include PeerTube's documented `/videos/embed/{uuid}` route. The original page remains available as a fallback.
2. **Native media** — play a validated direct MP4/WebM/audio URL using the browser's media element.
3. **Adaptive streaming** — play public, non-DRM HLS or DASH only when the manifest, segment URLs, CORS and source terms permit it. Prefer native playback where supported; otherwise use a maintained browser player. This is distinct from iframe embedding.
4. **Origin page** — open the source page when the provider blocks embedding, gives no stable direct file, requires its own consent/login, or returns a live/unsupported format.
5. **Direct file link** — open the provider's actual original file URL. A cross-origin browser link is not guaranteed to force a download; source headers and browser behavior remain authoritative.
6. **Managed download** — use a short-lived GitHub Actions job with pinned yt-dlp/gallery-dl/FFmpeg/aria2 only for publicly accessible content the user is authorized to save.
7. **Local download bridge** — optional Windows helper for large/long downloads that exceed hosted-runner disk, time or monthly-minute budgets.

## Architecture decision

Use a provider-capability registry and a delivery-method resolver. Do not invent an embed URL by rewriting arbitrary URLs. Providers must explicitly declare how their page identifiers map to official embed endpoints, what hosts are valid, and the fallback behavior.

For this first slice, implement PeerTube's official embed URL from the existing validated SepiaSearch result: use the validated instance host and a canonical UUID only. The iframe is click-to-load, has a meaningful title, no referrer, a narrow sandbox and permissions limited to playback. The source-page link stays visible.

## No-storage download transport (next phase)

- Worker authenticates the owner, creates a short-lived job and one-time transfer ticket, and dispatches only an opaque job ID to GitHub Actions.
- The Actions runner downloads to its ephemeral filesystem and opens an authenticated job-scoped WebSocket to a Durable Object.
- The user's browser connects to the same job-scoped Durable Object. The Durable Object relays bounded binary chunks; it does not persist the media object.
- Use small chunks (initial target 1 MiB), sequence numbers, ACK/backpressure, total-byte limits, idle and overall deadlines, cancellation, and SHA-256 verification.
- Worker/D1 stores only job metadata, owner binding, state, size limits, checksum and ticket hashes. It never stores video bytes.
- A reconnect may resume only while the same runner still has the temporary file. Otherwise the job must be restarted; do not claim durable resume without durable storage.
- GitHub Actions runner disk/time/minutes and Cloudflare Durable Objects/WebSocket quotas remain hard limits. For larger/longer downloads, the local bridge is the fallback.

## Security and rights

- Never accept arbitrary shell commands or user-supplied yt-dlp arguments.
- HTTPS only; validate hostnames, DNS answers, redirects and final connection destinations. Block localhost, private, link-local, metadata and reserved networks.
- No cookies, browser profiles, authentication-token harvesting, DRM/paywall/access-control bypass or private-resource fetches.
- Download only content the user is authorized to save. Preserve source and license metadata; an embeddable/playable item is not automatically licensed for redistribution.
- Embed hosts are generated only by provider-specific resolvers and checked against the provider/instance host. Use click-to-load to reduce third-party tracking.
- Keep downloads private to the authenticated owner. Do not use public GitHub Releases or public Actions artifacts as a substitute for a private media bucket.

## Scope boundaries

This is a staged system, not a promise to support every website, embed provider, DRM scheme or format. Unsupported sources must show an explicit origin-page fallback instead of a fake Download button.

## Delivery stages

- **Wave 63:** PeerTube official click-to-load embed; keep origin fallback; regression tests.
- **Next playback stage:** provider registry for recognized embed URLs (including YouTube, Vimeo and Dailymotion where official player rules permit), native direct media and explicit HLS/DASH capability reporting.
- **Download stage:** metadata-only URL inspection, then bounded single-item download jobs, then job-scoped WebSocket delivery via Durable Objects.
- **Local stage:** optional paired Windows helper for jobs that exceed hosted-runner limits.
