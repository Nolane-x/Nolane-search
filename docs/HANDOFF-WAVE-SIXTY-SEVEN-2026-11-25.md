# Wave 67 handoff — Telegram Mini App production smoke verification

Date: 2026-11-25

## Production baseline

- PR #138 merged to `main` as `db24b36acd3eee2a82f5b9a65993aa691e04e2a8`.
- Cloudflare deploy run #169 (`45636870984`) succeeded.
- Telegram webhook registration and bot command registration succeeded.
- Worker export/build and the existing Worker health smoke succeeded.
- The Mini App is served at `GET /telegram`; the owner should send `/start` in the private Telegram chat to receive a fresh single-use launch button. The deployment does not rewrite previously sent Telegram messages.
- Mini App owner authentication remains ticket-based: the inline launch ticket is short-lived, single-use and owner/chat-bound; D1 stores only its SHA-256 hash, then the browser receives the existing Secure, HttpOnly, SameSite=Strict session cookie.

## Wave 67 change

- Add `scripts/check-telegram-mini-app.mjs` as a post-deploy external smoke test against the production `/telegram` route.
- Verify HTTPS origin and exact route, HTML content type, `no-store`, `nosniff`, CSP directives, workspace tab markers, auth bootstrap marker and the Media Studio link.
- Run the script after Worker upload and Telegram webhook/command registration, so a successful deploy now requires the Mini App page itself to be reachable and structurally present.
- Add CI syntax validation for the smoke script and a regression assertion that the Mini App overview exposes Media Studio.

## Scope and non-claims

- The smoke test validates the production HTTP route and required static UI markers. It does not simulate a real Telegram Android/iOS/Desktop client, authenticate an owner session, or prove each provider API is live.
- A real Telegram client check is still needed after sending `/start`: tap **Mở Nolane Workspace**, confirm the login exchange succeeds, test bottom navigation and then open Media Studio.
- This wave does not add a downloader, R2 bucket, signed media links or a bypass for Telegram's 20 MB bot file-download limit.

## Wave 67 production verification

- PR #139 merged into `main` as `9d057c62c478969d0a69d024025a21418e355973`.
- Main CI #618 (`45638102164`) passed.
- Cloudflare deploy #170 (`45638101970`) succeeded, including the new post-deploy **Smoke test Telegram Mini App route** step.
- Export/build and Worker smoke #163 (`45638102400`) succeeded.
- The smoke test read the production `GET /telegram` route and verified HTML, `no-store`, `nosniff`, CSP, authentication bootstrap markers, five workspace tabs and the Media Studio link.
- This proves the deployed HTTP route and static page contract, not a Telegram native-client session. Owner-side verification is still: send `/start`, open **Mở Nolane Workspace**, finish first-time ticket exchange, then test navigation and Media Studio.


## Subsequent production media rollout — Waves 63–65

- PR #135 merged and deployed: official PeerTube player embeds, validated same-instance origin and canonical UUID, click-to-load, P2P disabled by default.
- PR #140 merged and deployed: URL-based video players for YouTube, Vimeo, PeerTube, Dailymotion and Twitch VOD/Clips. Provider URL validation, click-to-load and source-page links are retained. Dailymotion needs the optional `MEDIA_DAILYMOTION_PLAYER_ID` secret, which is passed to the Worker only if configured.
- Main CI #624, deployment #172 and export #165 succeeded. Deploy #172 again passed the production `/telegram` smoke test.
- Draft PR #141 contains browser-side HLS/DASH support; its Chromium real-source matrix passed 6/6 in run #36. It is not deployed. A separate real Safari/macOS native-HLS WebDriver check is being added.
- R2 remains disabled at the Cloudflare account level (API error 10042); no private bucket, signed media URLs, or large-file downloader is available. A Telegram `/start` message is still required for first Mini App launch.
