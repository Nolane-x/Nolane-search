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

No Cloudflare R2, paid Containers, paid VM, paid tunnel, paid API, or new recurring cost is part of this design.
