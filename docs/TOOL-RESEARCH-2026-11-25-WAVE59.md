# Wave 59 research — PeerTube federated video search

Date: 2026-11-25

## Goal

Add a provider that discovers public videos across independent PeerTube instances, rather than searching only the video catalogue of one hosting server. This is a discovery integration; it is not an extractor, downloader, mirror or content host.

## Primary sources reviewed

- PeerTube user guide, Search: https://docs.joinpeertube.org/use/search
  - PeerTube distinguishes platform search from global search.
  - Global search uses an external global index and must be enabled by the PeerTube administrator.
  - Global results can include instances that the local instance does not follow.
- PeerTube REST API reference: https://docs.joinpeertube.org/api-rest-reference.html
  - The video search operation is `GET /api/v1/search/videos`.
  - Its documented inputs include `search`, `start`, `count`, `sort`, and NSFW filtering.
  - Search returns a VideoListResponse with `total` and `data`.
- PeerTube OpenAPI specification: https://github.com/Chocobozzz/PeerTube/blob/develop/support/doc/api/openapi.yaml
  - Defines the public video metadata fields used by the normalizer, including `name`, `duration`, `views`, `publishedAt`, `nsfw`, `account`, `channel`, `licence`, and `language`.
- SearXNG's maintained SepiaSearch adapter: https://raw.githubusercontent.com/searxng/searxng/master/searx/engines/sepiasearch.py
  - Confirms the public base `https://sepiasearch.org`, endpoint `/api/v1/search/videos`, and query parameters `search`, `start`, `count`, `sort=-match`, and `nsfw=false`.
  - The adapter marks the API as official, JSON, and not requiring an API key.
- Related PeerTube adapter: https://raw.githubusercontent.com/searxng/searxng/master/searx/engines/peertube.py
  - Uses the same response parser for PeerTube and SepiaSearch and reads the canonical video URL, title, description, creator, duration, views and publication date.

## Implemented contract

The AI-callable function `search_peertube_videos`:
- accepts a 2–140 character query and 1–8 results (default 6);
- calls the public SepiaSearch HTTPS API with bounded result count, relevance ordering and `nsfw=false`;
- rejects explicit NSFW records;
- accepts a result URL only when it is HTTPS, has no credentials or non-standard port, is not an IP/local host, and its hostname exactly matches the account or channel host in that same result;
- normalizes title, description, originating host, creator/channel, duration, view count, language, license label and publication timestamp when supplied;
- returns the original-instance page URL and does not proxy, embed, download or rehost the video.

## Limitations and trust boundaries

- SepiaSearch is an index, not a guarantee that every PeerTube instance or every public video is represented. Search coverage depends on the index and its crawl/federation state.
- Instances can disappear, block access, change their metadata or have different moderation policies.
- The query excludes NSFW results; this is not a guarantee that every instance's metadata is accurate.
- License metadata is supplied by the hosting instance and may be absent or incorrect. Users must inspect the original video page and applicable license before reuse.
- Search and metadata results are untrusted input. No result URL is fetched by Nolane and no remote host is trusted for server-side execution.
- Direct file extraction/downloading remains outside this wave.

## Verification boundary

Unit tests cover query parameters, result normalization, NSFW exclusion, host binding, unsafe URL rejection, bounds, rate-limit behavior and AI tool dispatch. These tests mock the HTTP response; they do not prove live SepiaSearch availability or index freshness. Do not describe the provider as live-verified unless a real upstream request succeeds in a connected runtime.
