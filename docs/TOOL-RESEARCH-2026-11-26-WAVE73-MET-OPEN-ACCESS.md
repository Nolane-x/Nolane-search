# Wave 73 research — Museum Open Access image discovery

Date: 2026-11-26  
Status: implementation candidate in PR #150; not merged or deployed.

## The Met Open Access

The Metropolitan Museum of Art exposes a public collection API without an API key. Its Open Access dataset and eligible public-domain images are released under CC0.

Official references:
- API: https://metmuseum.github.io/
- Open Access: https://www.metmuseum.org/hubs/open-access
- Dataset: https://github.com/metmuseum/openaccess

The retired legacy search endpoint is replaced by paginated `/public/collection/v1.1/search`. Search results are candidate object IDs only. For each item, the integration fetches the object record and requires:
- `isPublicDomain === true`
- `primaryImageSmall` and `primaryImage` use HTTPS on `images.metmuseum.org`
- `objectURL` uses HTTPS on `www.metmuseum.org`

Missing/unknown rights and untrusted URLs are rejected. Artist, date, medium, credit and source-page metadata are preserved. Requests are bounded to 1–8 objects.

## Art Institute of Chicago

Official API documentation: https://api.artic.edu/docs/

Media Studio reuses the existing `search_museum_artworks` implementation rather than duplicating the API client. The adapter accepts only records explicitly marked public domain, verifies the museum's IIIF image path and artwork page, and preserves artist/date/medium/context. The existing museum request throttle and identifying User-Agent remain in force.

## Nolane integration

- Media Studio adds The Met and Art Institute of Chicago as image-only providers.
- Provider filters prevent museum sources appearing in video/audio searches.
- The Met is also available to the AI Agent as `search_met_open_access_artworks`.
- Images are loaded from official museum origins; Nolane does not proxy/copy the image binaries.
- No API key, new deployment secret, paid service or storage is needed.

## Boundaries

These are curated museum collections, not general reverse-image search, generated imagery or a universal web image crawler. Public-domain flags are honored per object; the integration does not override rights notices or imply that every museum object is reusable.

## Related no-cost video path

Large video download/playback is a separate problem and must not be solved by turning GitHub Actions into a public CDN. PR #149 proposes an owner-operated Media Node:
- GitHub Actions is used for CI/CD only.
- yt-dlp and FFmpeg execute locally on the operator's Windows host.
- Temporary media remains on local disk, with expiring owner-scoped links and HTTP Range streaming through the existing Worker Free gateway.
- Tailscale Funnel Personal can expose the local service over HTTPS at $0 for personal, non-commercial use, subject to beta bandwidth limits and host uptime.
- Telegram remains the small-file/archive-index route, not the large-video storage layer.

The design uses the operator's own host and free personal ingress, with no recurring media storage or compute service.



## Cleveland Museum of Art Open Access

Official API documentation: https://openaccess-api.clevelandart.org/

The museum publishes more than 64,000 artwork records and image assets for over 37,000 works under CC0 where applicable. The public API requires no API key. Search uses the documented `cc0` flag and `has_image=1` filter, with a small bounded result limit; the adapter independently checks `share_license_status === "CC0"`.

Only records whose API rights field explicitly says CC0 are returned. The integration sends the documented `cc0=1` and `has_image=1` filters, then independently checks the canonical artwork path on `clevelandart.org` or `www.clevelandart.org` and the official web-image CDN host/path against the accession number. Creator, date, technique, culture, department, type and measurements are retained when present. The browser CSP only permits the museum image CDN; images are loaded directly and are not copied or proxied. This source is image-only and unavailable for video/audio filters.

Official docs: https://openaccess-api.clevelandart.org/ (CC0 policy, filters and response schema); https://www.clevelandart.org/open-access (reuse terms).


## Library of Congress Prints & Photographs API

Official documentation:
- https://www.loc.gov/apis/json-and-yaml/
- https://www.loc.gov/apis/json-and-yaml/requests/
- https://www.loc.gov/apis/json-and-yaml/responses/search-results/
- https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/
- https://www.loc.gov/apis/json-and-yaml/working-with-limits/

The integration makes one bounded request per search to `https://www.loc.gov/photos/` with `q`, `fo=json`, `at=results` and a maximum of 8 results. It does not fetch a second item-detail endpoint for every result. The public JSON/YAML API requires no API key; its published rate limit is 20 requests per minute and may be reduced during heavy traffic.

Only records with a validated official Library of Congress item URL and a supported image URL on the exact `tile.loc.gov` or `cdn.loc.gov` hosts are shown. Image URLs are restricted to the documented service/storage paths and browser-renderable image formats. Records explicitly marked `access_restricted: true` are omitted.

The adapter preserves the record's title, contributor/creator, date, medium, description, subjects, and `rights_advisory` / `rights` metadata. It does not infer public-domain status from being hosted by the Library of Congress, from `access_restricted: false`, or from the presence of a downloadable image. A missing rights field is displayed as a prompt to check the item page. Rights statements vary by item and must be reviewed before reuse. Media Studio loads the image directly from the official image host.

This source is image-only; it is disabled in video/audio filters. The request is single-call and result-bounded to respect the provider's public capacity limits.
