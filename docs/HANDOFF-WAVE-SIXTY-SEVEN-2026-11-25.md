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
