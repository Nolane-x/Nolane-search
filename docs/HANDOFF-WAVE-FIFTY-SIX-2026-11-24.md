# Wave 56 handoff — Internet Archive audio discovery

Date: 2026-11-24
Branch: feat/wave-56-internet-archive-audio
Base: 4387df73e109b892f16b7cc95cebf56e427eea92
Release status: implementation branch; not yet merged or deployed.

## What changes

- Adds AI-callable `search_internet_archive_audio`.
- Extends the shared Internet Archive metadata normalizer to handle both `mediatype=movies` and `mediatype=audio`.
- Returns only supported non-private original audio files with consistent Archive metadata and source links.
- Extends `MediaSearchItem.mediaType` to `audio`.
- Adds Audio as a Media Portal filter/tab, an HTML audio player, an AUDIO badge and a direct original-audio link.
- Adds audio to all-media search while isolating per-provider failures.

## Supported formats

MP3, M4A, Ogg/OGA, Opus, FLAC, WAV, AAC and AIFF, subject to matching Internet Archive file-format metadata.

The integration queries `mediatype=audio`. Internet Archive identifies Live Music Archive items with a distinct `etree` mediatype; this initial wave does not include that separate catalog.

## Files changed

- `src/media-discovery-tools.ts`: shared IA item normalizer and audio search/dispatch.
- `src/agent-tools.ts`: direct AI function schema and dispatcher registration.
- `src/index.ts`: authenticated media API support for `kind=audio`.
- `src/media-ui.ts`: Audio tab, filter, player and original-file link.
- `tests/media-discovery-tools.test.ts` and `tests/agent-tools.test.ts`: public/private/derivative/missing-source filtering and AI dispatch assertions.
- `tests/media-ui.test.ts`: Audio filter, native player and archive media CSP.
- `tests/web-portal.test.ts`: confirms anonymous audio search remains protected by the Telegram web session.
- `docs/TOOL-RESEARCH-2026-11-24-WAVE56.md`: source, licensing and integration notes.

No dependency, secret, D1 migration, Cloudflare binding or 534-file processor change is intended.

## Rights and privacy

- Private, access-restricted, noindex, derivative, missing-source and unsafe files are excluded. A file must explicitly declare `source: original`.
- Rights may be missing or item-specific; playback does not guarantee permission to reuse or redistribute.
- Media stays on archive.org; Nolane does not proxy/rehost bytes.
- No user file upload, arbitrary cross-site downloader, DRM bypass or private R2 share link is included.

## Acceptance gates

1. PR CI passes TypeScript, Vitest, deployment scripts, Python runner tests and Worker build.
2. Main CI, Cloudflare deployment and Worker export/health smoke pass after merge.
3. A live audio query and player acceptance check should be done after deployment; mocked CI alone cannot establish the availability or rights status of every Archive item.
