# Wave 61 handoff — age-gated PeerTube NSFW search

Date: 2026-11-25
Branch: `feat/wave-61-age-gated-nsfw-media`
Base: `main`
Status: implementation and tests prepared; CI pending.

## Files changed

- `src/media-discovery-tools.ts`: optional `include_nsfw`, source flag handling and NSFW metadata.
- `src/agent-tools.ts`: optional AI tool parameter and server-side feature-gate enforcement.
- `src/index.ts`: authenticated Media Portal API guard and gated UI binding.
- `src/media-ui.ts`: 18+ search control is hidden unless the deployment feature gate is enabled; no thumbnail/direct file preview is added for PeerTube.
- `src/types.ts`, `cloudflare.config.ts`, `.github/workflows/deploy.yml`: optional `MEDIA_ALLOW_NSFW` secret.
- `tests/peertube-discovery.test.ts`, `tests/media-ui.test.ts`: default, opt-in, gate and UI tests.
- `docs/TOOL-RESEARCH-2026-11-25-WAVE61.md`: source evidence, design and limitations.

## Default production state

The PR does not set a production secret. Therefore `MEDIA_ALLOW_NSFW` remains disabled: no NSFW toggle is shown, default search continues to exclude NSFW, and the API returns 403 for explicit inclusion attempts. Do not enable it for a minor audience. A checkbox is not age assurance; any deployment that enables this feature must separately meet applicable age-verification and content moderation requirements.

## Release gates

1. TypeScript check and all Vitest tests.
2. Deployment script checks, Python tool-runner tests and Worker build.
3. Review the PR diff and ensure `MEDIA_ALLOW_NSFW` remains absent.
4. After merge, verify CI, Worker deploy and export smoke test.
