# Wave 66 — browser-native HLS and DASH playback

Date: 2026-11-25  
Repository: https://github.com/Nolane-x/Nolane-search  
Branch: `feat/wave-66-hls-dash-browser-playback`

## Decision

Use two established browser-side players:

- **HLS.js 1.7.4** for HLS manifests (`.m3u8`). HLS.js uses Media Source Extensions (MSE) and can use a browser's native HLS implementation where available. Its current UMD build contains its transmuxer worker. The project documents the CORS requirement for all HLS resources.
- **dash.js 5.3.0** for MPEG-DASH manifests (`.mpd`). It is the DASH-IF reference player for browser environments with Media Source Extensions.

The libraries are loaded lazily from exact, version-pinned jsDelivr package URLs only after the user clicks Play. This avoids loading several hundred KB of player code for ordinary search sessions. The CDN scripts are loaded with anonymous CORS and no referrer.

## Supported input

The authenticated URL resolver recognizes only a direct HTTPS manifest URL whose path ends with:

- `.m3u8` for HLS.
- `.mpd` for MPEG-DASH.

The URL is limited to 2,048 characters. User-info, non-default ports, fragments, IP literals and local/reserved hostnames are rejected. Signed query strings remain intact; query parameters are not logged or copied into the Worker.

The Worker does not fetch the manifest, playlist, keys or segments. It only validates and returns the URL to the authenticated browser. The browser contacts the source directly.

## Request controls

- HLS.js sets XHR credentials to false and Fetch credentials to `omit`; both XHR and Fetch setup hooks validate every request URL as HTTPS and reject credentials, IP literals, local/reserved hostnames and unusual ports.
- The native HLS fallback is used only when HLS.js/MSE is unavailable and the browser reports native HLS support. The video element uses `crossOrigin=anonymous`, so it does not send cross-origin cookies.
- dash.js 5 uses its official request-interceptor API. Every request URL is validated; only GET/HEAD requests are allowed; request credentials are set to `omit` and mode to `cors`.
- The Content Security Policy adds the pinned player CDN to `script-src`, HTTPS to `connect-src` and `media-src`, and `blob:` to `worker-src`/ `media-src` for MSE and the HLS.js UMD worker.
- Active players are destroyed when search results are replaced to stop background network activity.

## Browser and source requirements

HLS.js needs MSE on browsers that do not offer native HLS. Safari has native HLS support; native playback is used only when the browser exposes it. DASH.js requires a browser environment with MSE.

The manifest and every child playlist, segment, initialization segment, subtitle and key endpoint must be served over HTTPS and permit cross-origin requests as needed. A valid manifest URL alone does not guarantee a playable stream. The source may still fail because of CORS, codec/container incompatibility, expired signatures, unavailable segments, server geoblocking or unsupported DRM.

The player does not send Nolane credentials, account cookies or user-supplied authorization headers to media servers. It does not configure EME license servers, handle protected playback credentials, bypass DRM, or download/rehost media.

## Important security boundary

Media requests are made by the user's browser, not by the Cloudflare Worker. This removes server-side SSRF exposure from the manifest resolution path. The per-request URL filters reject literal IP and local/reserved hostnames, but a browser cannot reliably prove that an arbitrary public DNS name will never resolve to a private address. Cross-origin CORS, browser private-network protections where supported, no-credential requests and GET/HEAD-only restrictions are additional barriers, not a universal guarantee. Only use stream sources the user is authorized to access.

The native Safari HLS path is controlled by the browser's media stack and does not expose every nested segment URL to application JavaScript; it relies on anonymous CORS and browser network policy.

## Verification

GitHub Actions CI run [#576](https://github.com/Nolane-x/Nolane-search/actions/runs/45596035908) completed successfully on code commit `f48dd670dce07754f4eba08b2a2bd958f9d62c3f`.

- TypeScript type-check: passed.
- Vitest: 38 files, 399 tests passed.
- Deployment-script checks: passed.
- Pinned PRONOM installation: passed.
- Python tool-runner: 449 tests passed.
- Cloudflare Worker build: completed.

The resolver tests cover valid HLS/DASH paths, signed query retention, HTTPS and unsafe-host rejection, and prove that the Worker does not fetch the supplied manifest URL. UI tests cover lazy library loading, request filtering, no-credential mode, cleanup, DRM license request handling, CSP and generated inline-script syntax. Automated CI does not establish that a third-party live stream is currently online or playable.

## External references

- HLS.js README and compatibility/CORS notes: https://github.com/video-dev/hls.js
- HLS.js npm package: https://www.npmjs.com/package/hls.js
- dash.js 5.3.0 release: https://github.com/Dash-Industry-Forum/dash.js/releases/tag/v5.3.0
- dash.js project and player documentation: https://dashif.org/dash.js/
- dash.js network interceptors: https://dashif.org/dash.js/pages/usage/network-interceptor.html
- dash.js CommonMediaRequest fields: https://cdn.dashjs.org/latest/jsdoc/CommonMediaRequest.html

## Not implemented

- Downloader, proxy, permanent cache or R2 storage.
- HLS/DASH DRM license-server configuration, protected playback authentication, or cookie forwarding.
- Generic web page scraping, arbitrary HTML player extraction, or support for media playlists that do not end in `.m3u8`/`.mpd`.
