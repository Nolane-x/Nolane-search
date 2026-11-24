# Wave 52 research — image, video and product discovery

Date: 2026-11-24
Branch: feat/wave-52-media-discovery

## Scope delivered

Wave 52 adds three model-callable discovery functions and a private browser Media Portal.

1. search_wikimedia_images — Wikimedia Commons discovery with original file, preview, file-description page, author/credit and license.
2. search_nasa_media — NASA Image and Video Library search, including a direct MP4 only when the asset manifest explicitly lists an MP4 from the trusted NASA media asset host.
3. lookup_food_product — Open Food Facts lookup by EAN/UPC barcode, with ingredients, allergens, per-100-g nutrition values and product images where available.
4. /media — private web portal using the existing Telegram-issued session, with image previews and inline playback of direct public NASA MP4 links.

The existing 534 file processors are unchanged.

## Provider research

### Wikimedia Commons

Official references:
- https://commons.wikimedia.org/wiki/Commons:API
- https://commons.wikimedia.org/wiki/Commons:Machine-readable_data
- https://www.mediawiki.org/wiki/API:Search
- https://www.mediawiki.org/wiki/API:Imageinfo
- https://www.mediawiki.org/wiki/Extension:CommonsMetadata

Implementation uses the official MediaWiki Action API on commons.wikimedia.org:
- generator=search, namespace 6 (File), bounded result count;
- prop=imageinfo, iiprop=url|size|mime|extmetadata;
- requests a 720px thumbnail for portal previews;
- requires file URL, thumbnail URL, file-description URL, license name and license URL;
- returns credit/artist, description and dimensions when present.

Files with missing or unparseable license metadata are excluded rather than silently labelled reusable. Each result links to its original file-description page. Reusers still need to read the individual license, attribution and share-alike conditions. The portal does not download or rehost images.

### NASA Image and Video Library

Official reference:
- https://api.nasa.gov/

The NASA Image and Video Library uses:
- GET https://images-api.nasa.gov/search?q=...;
- GET https://images-api.nasa.gov/asset/{nasa_id} for the media asset manifest;
- GET /metadata/{nasa_id};
- GET /captions/{nasa_id} for video captions.

Implementation uses search and asset manifest endpoints. For video assets, it fetches the manifest only for a bounded number of results and selects an MP4 only when the URL host is exactly images-assets.nasa.gov. A NASA result still links to its source page if no MP4 is available. The portal uses NASA preview images and direct MP4 in a browser video element where supported.

NASA attribution/credit fields are preserved. NASA media are subject to NASA usage guidelines; third-party content and identifiable people may carry additional restrictions. Results do not imply NASA endorsement.

### Open Food Facts

Official references:
- https://openfoodfacts.github.io/openfoodfacts-server/api/
- https://openfoodfacts.github.io/documentation/docs/Product-Opener/v2/search/get-search/

The lookup uses the current v3 product endpoint by barcode and requests a narrow list of fields. It sends a meaningful User-Agent. The API documentation states 15 requests/minute/IP for product reads and 10 requests/minute/IP for searches. This wave implements lookup by barcode only, not unrestricted full-text search or search-as-you-type; the v2 structured search API is deprecated for new integrations and v3 does not yet offer structured search.

Open Food Facts is community-contributed and product records may be incomplete or outdated. Nutrition values are reported per 100 g. Database content is subject to the Open Database License (ODbL), including attribution/share-alike obligations for database reuse. Data are not medical or dietary advice.

## Media Portal security

- The root workspace shows the Media button only after the existing private web session is authenticated.
- GET /media checks the existing Telegram-originated web session before serving the page; unauthenticated visitors are redirected to the sign-in workspace.
- GET /api/media/search runs behind the existing protected /api router and web-session check.
- The portal is noindex/nofollow, no-store, and has a restrictive CSP. Image/video CSP hosts are limited to Wikimedia and NASA media asset domains.
- Media links are checked for HTTPS, exact trusted host, no embedded credentials and no nonstandard port before being used in preview/player links.
- The browser constructs DOM with textContent; source metadata is not interpolated into HTML.
- No third-party cookies, user credentials, browser cookies or arbitrary URLs are passed to media providers.
- Upstream requests use a project User-Agent, 12-second timeout, redirect rejection and a bounded JSON response body.

## Downloader architecture research and decision

OmniGet is a desktop application, not a Cloudflare download backend. Its public README credits yt-dlp, gallery-dl, FFmpeg and aria2; it describes broad site support, gallery/profile extraction, parallel direct-link downloads and resumable jobs:
- https://github.com/tonhowtf/omniget
- https://github.com/yt-dlp/yt-dlp
- https://github.com/mikf/gallery-dl

Nolane should use these engines in its existing GitHub-hosted runner, not run native media binaries inside Cloudflare Worker. Planned separation:
- yt-dlp for public video/audio extractors and supported-site metadata;
- gallery-dl for supported image galleries/profiles;
- FFmpeg for permitted merge, remux, thumbnail and preview jobs;
- resumable job state and chunked upload handled by a separate media workflow.

The yt-dlp release researched on 2026-11-24 is 2026.11.23 (Python 3.11+). Pin a tested version instead of downloading an unpinned executable on every run.

Strict usage boundaries:
- only public HTTPS pages and media the user is authorized to access;
- no DRM removal, paywall bypass, access-control bypass, credential/cookie import, token replay, private-account scraping or circumvention;
- never run a user-provided shell command; call the downloader as a fixed argument array with shell disabled;
- bounded file size, duration, playlist count, job runtime and concurrency;
- honor platform-owner opt-outs and platform terms; users remain responsible for copyright and local law.

## Large-file sharing architecture — current blocker

The current Telegram file processor uses a 20 MiB bound and the GitHub Actions runner downloads Telegram getFile inputs with the same 20 MiB cap. The web workspace's existing /api/ai/upload sends browser uploads to Telegram first; it is not a durable large-video store.

A private R2 bucket is the intended media store:
- Worker bucket binding keeps storage private;
- GitHub Actions runner uploads with resumable multipart operations;
- D1 stores owner, job state, object key, metadata, share-token hash and expiry, never binary media;
- a short-lived share page reads R2 through the Worker and supports HTTP Range for video seeking and downloads;
- Telegram receives a link only, never the large media binary;
- object and share metadata expire together, with cleanup on the scheduled Worker.

Cloudflare documentation:
- https://developers.cloudflare.com/r2/objects/upload-objects/
- https://developers.cloudflare.com/r2/api/workers/workers-api-reference/
- https://developers.cloudflare.com/r2/buckets/public-buckets/
- https://developers.cloudflare.com/r2/pricing/

**Blocking infrastructure condition discovered during this work:** the connected Cloudflare account returns R2 error 10042, "Please enable R2 through the Cloudflare Dashboard." R2 is not activated for account 1172c01120a2470aa12f81e5b4778556. The Cloudflare API cannot provision a bucket until the account owner enables R2 in the Dashboard. The source branch deliberately does not claim to download, store, share or play arbitrary downloaded files. No public GitHub Releases or public R2 bucket is used as a workaround for private media.

Cloudflare's R2 pricing documentation currently lists a 10 GB-month Standard storage free tier and free egress, with operation/storage charges beyond the included quotas. The owner should check current account pricing and set a lifecycle retention policy before enabling user-facing downloads.

## Validation plan

Provider tests mock:
- Commons API search and license metadata, including unlicensed and off-host records;
- NASA image search, MP4 asset manifests and off-host URL rejection;
- Open Food Facts barcode parsing and invalid input;
- model tool schema registration and dispatch;
- private Media Portal route and auth-protected media search API.

CI and /health prove the application builds and deploys; they do not prove every upstream asset is available or licensed for the user's specific reuse. Downloader + R2 upload/player tests remain a separate follow-up once R2 is enabled.
