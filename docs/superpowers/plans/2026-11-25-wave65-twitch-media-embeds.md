# Wave 65 implementation plan — Twitch VOD and Clip embeds

## Dependency

This work is included in PR #136 and uses the Wave 63 PeerTube/player foundation from PR #135. Do not merge PR #136 before PR #135 lands.

## Implementation sequence

1. Extend the normalized resolver provider union with Twitch.
2. Add exact-host parsing for VOD and Clip source URL forms. Construct only the official Twitch player endpoints, with autoplay disabled and no upstream fetch.
3. Extend browser-side embed validation for the exact player domains, paths and query keys.
4. Add `parent` only in the click handler from the current page hostname. Reject non-HTTPS, local/test and IP-hosted contexts.
5. Keep source links visible and respect Twitch's 400 × 300 px player minimum.
6. Add resolver and UI regression coverage, including syntax-compilation of the generated browser script.
7. Add this spec, plan and research report.

## Verification gates

- TypeScript typecheck passes.
- Resolver tests prove accepted/rejected URL cases and no network call.
- UI tests prove exact Twitch embed allowlists and syntactically valid inline JavaScript.
- Full CI passes all Vitest files, Python runner tests, deployment-script checks and the Cloudflare Worker build.
- PR #136 remains draft until PR #135 is reviewed and merged. This branch does not authorize production deployment.

## Out of scope

HLS/DASH, downloading, storage, live Twitch channel streams, chat and universal URL embedding remain separate work.
