# Wave 72 research — nature media, city discovery and downloader architecture

**Checked:** 2026-11-26  
**Branch:** `feat/wave-72-inaturalist-media-search`  
**State:** implementation branch; not deployed by this handoff.

## 1. Practical additions in this wave

### iNaturalist licensed nature-photo discovery

Upstream references:

- iNaturalist API documentation: https://api.inaturalist.org/v1/docs/
- iNaturalist API usage practices: https://www.inaturalist.org/pages/api+recommended+practices
- iNaturalist Open Data photo layout: https://github.com/inaturalist/inaturalist-open-data

The new `search_inaturalist_observations` tool searches research-grade observations by common/scientific name or nature subject. It can optionally filter to a bounded taxonomic group. It only returns photos whose API record includes a recognized CC0/Creative Commons license, a creator-attribution string and an image URL on `inaturalist-open-data.s3.amazonaws.com`. It deliberately omits exact observation coordinates.

The UI is integrated as an image-only provider; it is not a general-purpose image host or an image-identification model. A research-grade observation is still a community-submitted record, not a guarantee of identification. Each photo's own license and attribution must be reviewed at the source.

The API's recommended-practice page asks clients to send a meaningful User-Agent and keep request rates around one request per second. The current code uses a bounded single request per tool invocation; deployment-level rate limiting/caching remains a follow-up before high-volume public access.

### City-named public place discovery

The new `search_places_in_city` tool accepts a city/town the user explicitly names, optionally with an ISO country code. It uses Open-Meteo's public geocoding API to resolve that supplied name, then queries the existing bounded OpenStreetMap Overpass category filters. If more than one matching place/region is plausible, it returns a clarification object and does not run Overpass until the user chooses.

This is a separate tool from `search_nearby_places`: it never reads browser geolocation, Telegram location, IP-derived location or any hidden user coordinates. OSM distance is still straight-line distance; opening-hours tags are not a live open/closed check.

Upstream references:

- Open-Meteo Geocoding API: https://open-meteo.com/en/docs/geocoding-api
- OpenStreetMap Overpass API: https://wiki.openstreetmap.org/wiki/Overpass_API

## 2. Downloader research and why it is not activated in this wave

### OpenGrab

Repository: https://github.com/Skydope/OpenGrab  
License: MIT (verify current upstream license before redistributing any bundled components).

OpenGrab is a self-hosted downloader application. Its README describes a web UI around yt-dlp (approximately 1,800 supported extractors) and FFmpeg, with download jobs, progress events, history and local storage. Its architecture is a useful reference for a future Media Portal experience, but it is not a cloud API that can simply be called from a Cloudflare Worker.

The source checks URL syntax and resolves DNS at the application layer. Its own deployment guidance treats host-level egress filtering as a second, recommended defense to mitigate DNS rebinding/TOCTOU. A GitHub Actions runner that downloads arbitrary user-supplied URLs needs equivalent or stronger enforced egress controls; merely copying a URL validator into the Worker is insufficient.

### Engines and reference projects

- yt-dlp: https://github.com/yt-dlp/yt-dlp
- yt-dlp EJS challenge components: https://github.com/yt-dlp/yt-dlp/wiki/EJS
- gallery-dl current upstream: https://codeberg.org/mikf/gallery-dl
- FFmpeg: https://ffmpeg.org/
- aria2: https://github.com/aria2/aria2
- OmniGet: https://github.com/tonhowtf/omniget

yt-dlp is the broad site-specific extractor engine. Current YouTube challenge handling requires the documented EJS setup and a compatible JavaScript runtime; FFmpeg/ffprobe are used for muxing and media inspection. gallery-dl covers supported public image galleries. aria2 can help with suitable direct HTTP downloads, but is not a replacement for site-specific extractors.

OmniGet is a desktop/local-service application. Treat it as a reference for how the engines can be composed, not as a hosted downloader service. Do not copy its GPL-3.0 source into this project without a deliberate license/compliance decision; independently licensed engines can be integrated on their own terms.

### Required security boundary before arbitrary-site downloads

No user-facing universal downloader is enabled by Wave 72. Before dispatching user URLs to a runner:

1. Enforce network egress rules on the runner/isolated downloader, not just a Worker-side preflight check. Block loopback, private, link-local, CGNAT, IPv6 unique-local/link-local, multicast and cloud metadata destinations.
2. Address DNS rebinding and redirects at connection/egress level; every destination reached by the extractor must remain public.
3. Accept public HTTP(S) pages only under a reviewed URL policy; reject credentials, IP literals, internal hostnames and unusual ports.
4. Do not load cookies, browser profiles, OAuth sessions or account credentials. Do not bypass DRM, paywalls, authentication or other access controls.
5. Use fixed argument arrays, no shell interpolation, a fresh job directory, one media item by default, bounded runtime, file size, duration, retries and concurrency.
6. Add SSRF, redirect, DNS-rebinding, cancellation, size-limit and failure-cleanup tests before enabling a public button.

A provider returning a media URL is not proof that a file has been downloaded, stored or made shareable.

## 3. Large-video delivery: Telegram and private storage

The current Telegram Bot API download path is capped at 20 MB for `getFile`. The existing file-processing path honors that limit. Telegram archive channels preserve files sent through the archive workflow, but that is not a general-purpose private media object store or browser streaming service.

The Wave 62 design remains the correct next architecture once the account owner activates R2:

- Create a private R2 bucket named `nolane-search-media`.
- Keep media bytes out of D1; D1 stores owner/job/object metadata, checksum, size, expiry and a hashed share token only.
- Upload from a short-lived runner using bounded multipart/resumable transfers and verify the checksum.
- Serve through an owner-authorized Worker endpoint with short-lived share tokens and HTTP Range support so video seeking works.
- Mark private responses no-store, avoid shared caching, coordinate share/object expiry, abort incomplete multipart uploads and clean expired records/objects.
- Telegram sends a small authenticated link and summary rather than a binary payload.

**Account blocker:** the latest checked Cloudflare account response was `10042: Please enable R2 through the Cloudflare Dashboard.` No R2 binding or R2 credentials are configured. Until the account owner enables R2 and the private-bucket/player tests pass, Nolane must not claim durable large-file sharing is live.

GitHub Actions artifacts are test/build artifacts with retention controls, not a substitute for user-owned private media storage.

## 4. Verification scope

Wave 72 adds unit coverage for:
- iNaturalist query bounds, license/host/attribution filtering, no-coordinate output and AI-agent dispatch.
- City geocoding, country/region disambiguation, category/radius validation and AI-agent dispatch.

The actual CI result is tracked by the pull request, not presumed from source edits. `docs/STATUS.md` and production status must remain on the last merged/deployed wave until this branch is merged and deployed.
