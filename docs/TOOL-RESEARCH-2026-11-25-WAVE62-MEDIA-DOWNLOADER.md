# Wave 62 — media downloader and large-file storage design

Date: 2026-11-25
Repository: https://github.com/Nolane-x/Nolane-search

## Current production state

The Media Portal is private and authenticated. Current discovery providers are:
- Wikimedia Commons and Openverse for licensed/reusable image discovery.
- NASA Image and Video Library for public NASA images and MP4 assets listed in NASA's asset manifests.
- Internet Archive for public video and audio records where a compatible original file is exposed in the item metadata.
- SepiaSearch for federated PeerTube video metadata and origin links.

Direct playback works where the provider supplies a trusted direct media URL (notably NASA and Internet Archive). PeerTube currently links to the originating instance; it is not rehosted and a universal direct MP4 is not assumed.

A public video search provider is not a downloader. A provider's result count also does not guarantee that each video can be watched, downloaded, or reused.

## Downloader engine research

### yt-dlp — video/audio extractor

Upstream: https://github.com/yt-dlp/yt-dlp
Latest release checked on 2026-11-25: `2026.11.23`.

Use yt-dlp for supported public video and audio pages, metadata inspection, available format listing, subtitles where permitted, and downloading of content the user is authorized to download.

YouTube support requires the EJS component and a compatible JavaScript runtime for current challenge handling. Install and pin both deliberately; do not rely on an unpinned `pip install -U` in every job. FFmpeg and ffprobe are recommended for combining separate audio/video streams and post-processing.

Support is broad but not universal or guaranteed. The extractor list must be treated as a live compatibility catalogue, not as a promise that every page or account can be downloaded.

### gallery-dl — image/gallery extractor

Upstream development: https://codeberg.org/mikf/gallery-dl
PyPI release checked on 2026-11-25: `1.32.21`.

Use for supported public galleries and multi-image pages. The older GitHub mirror is not the preferred current development source; pin and audit the upstream package and its licence before use.

### FFmpeg / ffprobe / aria2

- FFmpeg/ffprobe: inspect media, merge permitted video+audio formats, remux, create thumbnails and generate previews.
- aria2: optional segmented download helper for direct HTTP sources where it is reliable; not a substitute for site-specific extractors.
- Do not ship user-supplied shell strings to any engine. Use fixed argument arrays, no shell, a clean temporary directory and strict time/size/concurrency limits.

### OmniGet

Reference: https://github.com/tonhowtf/omniget

OmniGet is a desktop application with a local MCP service, not a cloud downloader backend. Its architecture combines yt-dlp, gallery-dl, FFmpeg and aria2. Reuse the underlying independently licensed engines, not the assumption that the desktop interface itself provides a remote cloud service. Review each upstream licence before packaging or distributing binaries; do not copy OmniGet's source into Nolane without respecting its GPL-3.0 licence.

## Why no arbitrary URL runner is merged yet

A naive GitHub Actions step that accepts any URL and runs yt-dlp would turn the runner into an untrusted network fetcher. It can be abused to request private, link-local or metadata-service addresses through redirects or DNS rebinding. The Worker-side HTTPS URL check alone does not validate every redirect and every network connection made by an extractor.

Before dispatching any user-controlled media URL, the runner must:
1. Accept HTTPS only, reject credentials, unusual ports, IP literals, localhost and reserved/local host suffixes.
2. Revalidate DNS answers and every resolved destination; block loopback, RFC1918, link-local, CGNAT, IPv6 unique-local, IPv6 link-local, multicast and metadata-service ranges at the runner's egress layer.
3. Use no cookies, browser profiles, account tokens, OAuth sessions or copied site credentials.
4. Call the extractor with fixed arguments and isolated temporary paths; never execute user-provided commands or repository code.
5. Bound URL length, playlist entries (default one), output size, duration, total runtime, retries and concurrency.
6. Keep DRM, paywall, authentication and access-control bypass out of scope. Only download publicly available content the user is authorized to save.

The production implementation should include explicit SSRF and redirect tests, not just URL syntax tests.

## Large-file storage architecture

Telegram Bot API `getFile` is capped at 20 MB for bot downloads. The existing tool runner enforces that limit. Web uploads currently enter the same Telegram path; they do not create a durable large-media object.

R2 is the preferred storage backend once the account owner activates it:
- Create a **private** bucket named `nolane-search-media`.
- Worker mediates authorization and serves private objects; never expose a public bucket for personal media.
- Runner downloads into ephemeral disk, then uploads through a short-lived job-scoped path using multipart/resumable upload.
- D1 keeps metadata only: owner, job ID, filename, media type, size, checksum, status, object key, expiry and share-token hash. Never put media bytes in D1.
- Worker issues high-entropy, short-lived, owner-authorized share links. Access checks happen before serving the object.
- Worker supports HTTP Range for video seeking and partial download. Private responses are no-store and do not enter a shared public cache.
- Share expiry and object expiry are coordinated. Incomplete multipart uploads are aborted; a scheduled cleanup removes expired objects and stale job metadata.
- Telegram receives only the small share link/result summary, not the large binary.

Current account state checked on 2026-11-25:
- Cloudflare R2 bucket listing returns error `10042: Please enable R2 through the Cloudflare Dashboard.`
- There is no R2 bucket binding in `cloudflare.config.ts`.
- No R2 access key/secret or storage credentials are configured.
- Therefore the downloader must not claim that large files are stored or shared from Nolane production.

Official R2 references:
- Workers binding setup: https://developers.cloudflare.com/r2/get-started/workers-api/
- Multipart uploads: https://developers.cloudflare.com/r2/api/workers/workers-multipart-usage/
- Workers object API: https://developers.cloudflare.com/r2/api/workers/workers-api-reference/
- Presigned URLs: https://developers.cloudflare.com/r2/api/s3/presigned-urls/
- CORS: https://developers.cloudflare.com/r2/buckets/cors/
- Lifecycle rules: https://developers.cloudflare.com/r2/buckets/object-lifecycles/
- Pricing: https://developers.cloudflare.com/r2/pricing/

If R2 cannot be activated, evaluate Backblaze B2's S3-compatible API as a separate owner-approved storage provider. Do not silently switch to public object hosting, GitHub Releases, or GitHub Actions artifacts.

## Providers investigated and not added

### Dailymotion

The current API v2 migration guide requires a **private API key** with client-credentials authentication; there is no anonymous public-key search integration ready for this account. The old legacy search request returned HTTP 400, and the new v2 API should not be coded as a free unauthenticated provider. Reference: https://developers.dailymotion.com/docs/migrating-from-legacy-api-to-api-v2

### Odysee / LBRY Lighthouse

The public Lighthouse endpoint `https://lighthouse.odysee.tv/search` works without an API key using parameters `s`, `size`, `from`, `include` and `mediaType=video`. However, testing `nsfw=false` still returned adult-related titles without any per-result mature-content flag in the returned fields. There is no reliable age-safe classification in the fields inspected, so Odysee is not added to the default Media Portal until a trustworthy classification/age gate is available.

### Current NSFW handling

PeerTube's API has a documented `nsfw` query parameter and returns `nsfw` / `nsfwFlags` metadata. Wave 61 added explicit, deployment-gated opt-in support, but production remains `MEDIA_ALLOW_NSFW=false`. A source flag is not a complete legality or age-safety audit.

## Release plan and gates

**Phase 1 — URL inspection (without downloading):**
- Add a private Media Portal form accepting one public HTTPS URL.
- Run pinned yt-dlp/gallery-dl metadata inspection on an ephemeral GitHub Actions runner with network egress protections.
- Return title, source, duration, thumbnail and a bounded list of formats. Do not return an unbounded raw extractor JSON blob.
- No cookie or login support. No file is stored.

**Phase 2 — Download job:**
- User chooses a format/quality and confirms they have the right to download it.
- Runner fetches one asset by default. Playlists are a separate explicit feature with tighter caps.
- Verify media type and size; compute SHA-256; produce a safe filename and optional preview.

**Phase 3 — Private R2 upload:**
- Provision and bind the private bucket.
- Multipart upload with retries, checksum verification and abort cleanup.
- Test large objects, resumed parts and failure recovery.

**Phase 4 — Share/player:**
- Owner-scoped D1 metadata and short-lived signed share tokens.
- Authenticated player/download endpoint with HTTP Range.
- Expiry, deletion and owner-only history.

**Do not enable a user-facing arbitrary-site download button before the R2 upload/player tests pass.**
