# Wave 60 handoff — Steam game discovery

Date: 2026-11-25
Branch: `feat/wave-60-steam-game-discovery`
Base: `main`
Status: implementation and mocked tests prepared; CI pending.

## Goal

Add useful, consumer-oriented game discovery without adding developer-centric processors or duplicating existing TV/podcast/music catalog tools.

## Files changed

- `src/steam-games-tools.ts` — bounded Steam Store adapter, search and game details normalization.
- `src/agent-tools.ts` — two AI function schemas and dispatch routes.
- `tests/steam-games-tools.test.ts` — search/details, localized parameters, safe URLs, validation, 429 and agent dispatch.
- `docs/TOOL-RESEARCH-2026-11-25-WAVE60.md` — source and limitations.

## Release gates

1. TypeScript check.
2. All Vitest tests.
3. Existing Python runner test suite and Worker build.
4. Inspect the PR diff and test output before merging.
5. After merge, separately verify Worker deploy and a real Steam query; mocked tests are not live provider evidence.

## Product boundary

This is a game catalogue lookup, not a Steam client. It does not sign users into Steam, check their library, download/install games, bypass age restrictions, or promise that listed prices are still current. The default region/language are Vietnam/Vietnamese; users can select another two-letter region and supported language.
