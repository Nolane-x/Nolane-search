# Implementation plan — media delivery Wave 63

Spec: [2026-11-25-video-delivery-modes-design.md](../specs/2026-11-25-video-delivery-modes-design.md)

## Scope

Ship only the first independently useful slice: official PeerTube embeds in the existing Media Portal. Do not claim the GitHub Actions streaming bridge, HLS/DASH or other provider integrations as complete in this wave.

## Files

- `src/media-discovery-tools.ts`: add `embedUrl: string | null` to `PeerTubeVideoResult`; derive it only from a canonical UUID and validated `instanceHost`.
- `src/media-ui.ts`: render a click-to-load PeerTube iframe, retain the origin link, and add the minimum CSP frame directive and iframe styles.
- `tests/peertube-discovery.test.ts`: assert the canonical embed URL.
- `tests/media-ui.test.ts`: assert click-to-load iframe behavior and CSP.
- `docs/TOOL-RESEARCH-2026-11-25-WAVE63-MEDIA-DELIVERY.md`: record the shipped behavior and deferred phases.
- `docs/STATUS.md` and `README.md`: update only after CI and deployment evidence exists.

## Tasks

### Task 1 — discovery contract (TDD)

- Assert a valid PeerTube UUID produces `https://{validated-instance-host}/videos/embed/{uuid}`.
- Assert malformed/missing UUIDs do not produce an embed URL.
- Keep the existing source URL, NSFW filtering and host validation unchanged.
- Implement a small canonical UUID check; never construct an embed URL from an untrusted URL path.

### Task 2 — safe user-triggered player (TDD)

- Add a button to PeerTube cards. Do not auto-load third-party iframes during search.
- On click, create an iframe using only `embedUrl` after rechecking HTTPS, no credentials/port and exact equality with `instanceHost`.
- Set a descriptive title, `loading=lazy`, `referrerPolicy=no-referrer`, `allowFullscreen`, limited media permissions, and sandbox tokens needed for the cross-origin player.
- Keep the original PeerTube page link in every card.
- Add a `frame-src https:` CSP directive because each federation instance has its own host; restrict creation in code to the validated PeerTube URL shape and sandbox the frame.

### Task 3 — verification and handoff

- Run `npm run typecheck`, `npm test` and `npx cf build` through the repository CI.
- Review the PR diff for host confusion, UUID confusion, iframe permissions and unchanged fallback behavior.
- Update status documents only with the actual CI/deploy state.
- Leave production deployment/merge to the normal release process; do not claim a completed deploy without a successful workflow run.

## Review focus

- Invalid UUID, URL credentials, HTTP, non-default port, mismatched instance host and path confusion.
- Third-party iframe must not load before click.
- Cross-origin iframe cannot navigate the Nolane top-level page or access parent state.
- Embed failures still leave a working source-page link.
