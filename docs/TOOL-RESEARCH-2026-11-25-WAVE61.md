# Wave 61 research — gated PeerTube NSFW discovery

Date: 2026-11-25
Repository: https://github.com/Nolane-x/Nolane-search

## Evidence

- PeerTube's current Video REST API documents `nsfw=true|false` as the query parameter controlling whether NSFW videos are included. It also documents `nsfw` as a boolean on returned video records and `nsfwFlags` values that can be combined: `0` none, `1` violent, `2` explicit sex, `4` other flag. Reference: https://docs.joinpeertube.org/api-rest-reference/api/video.html
- SearXNG's SepiaSearch engine sends its SafeSearch-derived value to `https://sepiasearch.org/api/v1/search/videos` through the `nsfw` parameter. Reference: https://docs.searxng.org/_modules/searx/engines/sepiasearch.html
- A live request to SepiaSearch with `nsfw=true` returned public records with `nsfw: true`; the same source therefore supports retrieving records tagged NSFW. This is a source-integration smoke check, not a quality or legality audit of every returned item.

## Implemented

- PeerTube search accepts an explicit boolean `include_nsfw`; absent means false.
- The adapter sends `nsfw=false` by default and `nsfw=true` only when explicitly requested.
- The post-response filter now removes `nsfw:true` records only when the caller did not request inclusion.
- Results expose the source's `nsfw` boolean and bounded `nsfwFlags` value (0–7); no sensitive-content summary is copied into the result.
- AI tool schema supports the optional `include_nsfw` flag. The agent rejects it unless the deployment feature gate is set.
- Media Portal shows an 18+ opt-in control only when the deployment feature gate is enabled. NSFW results do not receive thumbnail or direct media playback URLs; users can open the originating PeerTube page.
- The Worker endpoint rejects `include_nsfw=true` unless `MEDIA_ALLOW_NSFW=true`.
- The deployment workflow binds and optionally uploads the feature-gate secret. The secret is intentionally not set by this PR.

## Default production state

`MEDIA_ALLOW_NSFW` is absent/disabled. Normal search continues to exclude NSFW records. The adult-mode UI control remains hidden, and requests trying to set `include_nsfw=true` receive HTTP 403. Enabling an adult-only catalogue on a real service requires appropriate age assurance, legal review, and controls against illegal material; a UI checkbox alone is not identity or age verification.

## Security and limitations

- PeerTube/instance NSFW flags are publisher metadata and can be missing, inaccurate or inconsistent.
- Search results are metadata and links to source instances only; this feature does not download, mirror or host the videos.
- Only public origin URLs on the exact account/channel host are returned; existing HTTPS/host validation remains.
- NSFW mode is opt-in and deployment-gated, not the default experience.
- This work does not relax restrictions on illegal material, non-consensual abuse, or content involving minors.

## Verification boundary

Tests cover default exclusion, explicit inclusion, source flags, invalid control types, AI dispatch gating and hidden-by-default UI. Mocked CI does not prove that every result is correctly classified by the source. Live SepiaSearch support for the query parameter was separately checked.
