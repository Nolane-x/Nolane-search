# Wave 66 implementation plan — browser-side HLS and DASH playback

## Dependency

This work starts from PR #136 head and is intended to stack on top of PR #136, which itself depends on PR #135. Do not merge this branch directly into `main` before the preceding PRs land.

## Implementation sequence

1. Extend the authenticated URL resolver to recognize exact `.m3u8` and `.mpd` manifest paths without fetching user URLs.
2. Return a normalized stream item with the original signed query and an explicit `streamType`.
3. Add click-to-load HLS.js and dash.js integration with pinned versions.
4. Add per-resource HTTPS/public-host checks and no-credential request configuration.
5. Add native HLS fallback only where the browser advertises support.
6. Update CSP for the player CDN, HTTPS media requests, MSE blobs and HLS.js worker.
7. Ensure results replacement destroys active players.
8. Add resolver/UI regression tests and documentation.
9. Add Auto/manual quality selection from actual HLS levels and DASH representations.
10. Verify DASH manual selection disables ABR, Auto restores it, and representation state remains available to quality-change events.
11. Add shared playback-rate controls on the media element for HLS, DASH and native HLS.
12. Verify retry tears down the old player, stale callbacks are ignored, and failed CDN script promises are evicted so a retry reloads the library.
13. Add manifest-backed HLS audio/subtitle track controls and DASH audio/text track controls using documented player APIs.
14. Refresh DASH track controls after stream initialization and text-track events; test audio switching, subtitle switching and subtitle-off behavior.

## Verification gates

- TypeScript typecheck.
- All Vitest suites, including generated inline-script parsing.
- Python tool-runner suite, deployment-script checks and Cloudflare Worker build.
- Manual browser testing must also verify switching Auto/manual quality on manifests containing multiple representations.
- Manual browser testing against public, CORS-enabled clear HLS and DASH examples is still required; CI cannot prove upstream stream availability or codec compatibility.

## Out of scope

Server-side manifest fetching, downloading, caching, rehosting, R2, EME/DRM, protected streams and universal web-site extraction.
