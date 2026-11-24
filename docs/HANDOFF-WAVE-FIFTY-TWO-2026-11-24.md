# Wave 52 handoff — Media Portal and discovery

Date: 2026-11-24
Branch: feat/wave-52-media-discovery

## Implementation in this branch

Three new model-callable discovery functions:
- search_wikimedia_images — images with creator/credit, license name/URL and source page.
- search_nasa_media — NASA image/video search, with direct MP4 returned only from a trusted NASA asset manifest.
- lookup_food_product — Open Food Facts barcode lookup, ingredients, allergens and per-100-g nutrition.

New files:
- src/media-discovery-tools.ts
- src/media-ui.ts
- tests/media-discovery-tools.test.ts

Updated integration:
- src/agent-tools.ts — tool schemas and dispatch.
- src/index.ts — authenticated GET /media route and GET /api/media/search.
- src/web-ui.ts — Media navigation button shown after login.
- tests/agent-tools.test.ts and tests/web-portal.test.ts — catalog and privacy checks.

The 534 existing file processors are not changed. No new secrets, packages or D1 migrations are required by the discovery/portal part.

## Media Portal behavior

- Uses the same private Telegram-issued web session as the search workspace.
- Supports source selection (Wikimedia Commons / NASA) and media type (images / video / all).
- Commons image cards display previews, link to original file pages and expose credit/license metadata.
- NASA cards play public MP4s inline when the asset manifest explicitly lists a direct MP4 on images-assets.nasa.gov.
- No media bytes are uploaded to or rehosted by the Worker in this branch.

## Downloader and large-file status

Not yet production-enabled. The plan is yt-dlp + gallery-dl + FFmpeg on the existing GitHub Actions hosted runner, with private R2 multipart storage and a short-lived same-origin share/player endpoint supporting byte-range video seek. No DRM/paywall/access-control bypass or credential/cookie support.

**Owner action needed:** Cloudflare R2 is not activated. The Cloudflare API returned error 10042 for the connected account, requiring R2 to be enabled manually in the Cloudflare Dashboard. Do not merge/deploy a feature that claims large-file downloads until R2 activation, bucket binding, multipart upload, signed share access, HTTP Range streaming, expiry cleanup and CI end-to-end tests all pass.

## References

- Wikimedia Commons API / machine-readable licensing: https://commons.wikimedia.org/wiki/Commons:API and https://commons.wikimedia.org/wiki/Commons:Machine-readable_data
- NASA Image and Video Library API: https://api.nasa.gov/
- Open Food Facts API and limits: https://openfoodfacts.github.io/openfoodfacts-server/api/
- yt-dlp: https://github.com/yt-dlp/yt-dlp
- gallery-dl: https://github.com/mikf/gallery-dl
- OmniGet: https://github.com/tonhowtf/omniget
- Cloudflare R2 multipart upload: https://developers.cloudflare.com/r2/objects/upload-objects/
- Cloudflare R2 pricing: https://developers.cloudflare.com/r2/pricing/
