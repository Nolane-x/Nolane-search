# Wave 73 research — The Met Open Access images

Date: 2026-11-26  
Status: implementation candidate in PR #150; not yet merged or deployed.

## Why this source

The Metropolitan Museum of Art exposes a public collection API without an API key. The museum describes its Open Access dataset and corresponding public-domain images as CC0. The source is useful for artwork searches, historical objects, illustration references and visual research.

Official references:
- API: https://metmuseum.github.io/
- Open Access: https://www.metmuseum.org/hubs/open-access
- Dataset: https://github.com/metmuseum/openaccess

## API version and request budget

The legacy `/public/collection/v1/search` endpoint was announced for retirement on October 1, 2026. Use the paginated `/public/collection/v1.1/search` endpoint instead, with `q`, `hasImages=true`, `offset=0` and a bounded `limit`. The API documentation asks users to remain below 80 requests per second.

Search returns object IDs, not the final image or rights decision. For every returned object, fetch its object record and independently require:
- `isPublicDomain === true`
- `primaryImageSmall` and `primaryImage` are HTTPS URLs on `images.metmuseum.org`
- `objectURL` is an HTTPS URL on `www.metmuseum.org`

Only records that satisfy all conditions are returned. Records with unknown, false or missing public-domain status are omitted. The source page, artist and collection credit line are retained. The UI labels the license CC0; source metadata remains available for context.

## Nolane integration scope

- Media Studio: image-only provider `The Met`; disabled for video and audio searches.
- AI Agent: `search_met_open_access_artworks`, bounded to 1–8 objects.
- API responses contain metadata and official origin image URLs. Nolane does not proxy or copy image binaries.
- No API key or new deployment secret is required.

## Verification requirements

- Test the current `v1.1/search` endpoint and pagination parameters.
- Reject non-public-domain objects, missing image URLs, wrong image hosts and untrusted object page URLs.
- Confirm the image CSP allows the exact Met image host in addition to existing sources.
- Confirm Media Studio disables The Met when video or audio is selected.
- CI must pass before merge. This candidate document does not imply the PR has been merged or deployed.

## Known scope boundaries

This is a museum/open-access image source, not general reverse-image search, not an image generator and not a general video downloader. It does not infer or override rights for items outside The Met's Open Access collection.
