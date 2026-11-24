# Wave 54 research — Openverse images and Internet Archive video

Date: 2026-11-24  
Repository: https://github.com/Nolane-x/Nolane-search  
Branch: feat/wave-54-open-media-sources

## Product intent

Extend the authenticated Media Portal with independent open-media indexes, while preserving original source links, attribution and license information. This wave is not a general-purpose video downloader and does not depend on Cloudflare R2.

## Openverse — openly licensed image discovery

API: https://api.openverse.org/v1/images/  
Documentation: https://api.openverse.org/v1/ and https://docs.openverse.org/api/reference/search_algorithm.html

Integration:
- search_openverse_images exposes image discovery as a directly AI-callable function.
- The authenticated Media Portal can select Openverse or include it in the all-sources search.
- Uses the official JSON API with bounded page size (maximum 10), anonymous access, mature=false and filter_dead=true.
- Returns original image URL as an external link only; preview is served from Openverse's thumbnail endpoint. It does not hotlink arbitrary upstream files as embedded previews.
- Requires a valid HTTPS media URL, source landing page, Openverse thumbnail and Creative Commons license URL. Mature and removed-from-source records are omitted.
- Creator, license code/version, license URL and original source link are retained. Do not assume every CC license permits commercial use or derivative works; review the item-specific license conditions and attribution requirements.
- No scraping, deep pagination, bulk harvesting or local media rehosting is performed.

Operational boundaries:
- Openverse offers free anonymous and registered API access, but all users are rate-limited. The API exposes rate-limit headers; this integration returns a clear error on HTTP 429 and does not run aggressive retry loops.
- Search is deliberately limited to the top small result page for interactive UI usage, not exhaustive search or harvesting.

## Internet Archive — public film/video discovery

Search API: https://archive.org/advancedsearch.php  
Metadata API: https://archive.org/metadata/{identifier}  
Developer docs: https://doc-tools.readthedocs.io/en/ia-test-gsod/md-read.html  
Metadata fields: https://internetarchive.readthedocs.io/en/stable/metadata.html

Integration:
- search_internet_archive_videos queries mediatype:movies through the official Advanced Search endpoint and reads a bounded set of exact item IDs.
- For each result, it calls the official item metadata endpoint and considers only non-private original files whose filename and format both identify an MP4/M4V/WebM/Ogg video.
- It omits items marked access-restricted-item, access-restricted or noindex, files marked private, non-original derivatives, malformed identifiers and unsafe filenames.
- The player/download URL is assembled only from the validated Internet Archive identifier and a single validated original filename. Preview and source links remain on archive.org.
- Item rights/license metadata are preserved when present. Where no Creative Commons license URL is provided, the UI reports the item rights text if available or “Rights not specified”; it does not infer permission from the fact that an item is indexed or playable.
- Metadata records and direct media are not copied to Nolane storage.

Operational boundaries:
- Internet Archive itself notes that not all files/items are downloadable; access-restricted items exist. Nolane deliberately omits explicit restricted/private metadata and only returns links for listed original video files.
- Rights statements can be absent, incomplete or item-specific. Playback availability is not a copyright determination. Users must inspect the archive item page and rights statement before reuse.
- Search is limited to five items per request; metadata fan-out is bounded to that result set.

## Media Portal behavior

- Source selector now includes Wikimedia Commons, NASA, Openverse and Internet Archive.
- Image search can combine Commons + Openverse + NASA. Video search can combine NASA + Internet Archive.
- Each source runs independently via Promise.allSettled; a rate-limited or unavailable provider produces a visible warning while successful providers still return results.
- Existing authenticated Telegram Web Workspace session is still required.
- Content Security Policy allows only the specific preview/media hosts needed by the selected providers. Openverse original URLs are external links, not embedded image sources; Internet Archive media playback is limited to archive.org and its archive.org subdomains.

## Explicitly not included

- No arbitrary multi-site video downloader (yt-dlp/gallery-dl) was enabled.
- No R2 bucket, private object upload, signed share URL, HTTP Range proxy or expiry cleanup was added.
- No DRM, paywall, access-control, login-cookie or private content bypass is implemented.
- The R2 owner activation prerequisite from Wave 52 remains open. Internet Archive public-source links do not replace private storage for user-submitted downloads.

## Validation plan

- Mocked API tests verify Openverse source/thumbnail/license validation and mature/unlicensed result exclusion.
- Mocked API tests verify Archive search, exact metadata lookup, direct original file selection and omission of restricted/private/derivative-only items.
- Agent tests assert the tools are exposed through the model function schema.
- CI verifies type-check, Vitest, deployment scripts, Python runner and Cloudflare Worker build.
- Provider live availability and item-by-item rights verification remain separate from mocked CI.
