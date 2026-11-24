# Wave 55 handoff — open knowledge, travel and dictionary tools

Date: 2026-11-24
Branch: feat/wave-55-wikipedia-travel-wiktionary
Base: 585c081bcfb2b924ac49648c905733483a74882a
Release status: merged and deployed via [PR #116](https://github.com/Nolane-x/Nolane-search/pull/116) as `d44aaed6c938eda2212387e60b5bc0a7df4ae693`.

## New AI-callable tools

Wikipedia:
- search_wikipedia_articles — search en/vi/ja/fr/es/de editions.
- get_wikipedia_article — fetch a bounded 1,200-character extract, canonical page link, categories and optional Wikimedia thumbnail.

Wikivoyage:
- search_wikivoyage_guides — discover travel guides in English or Vietnamese.
- get_wikivoyage_guide — retrieve the bounded destination guide text and original link.

Wiktionary:
- lookup_wiktionary_entry — retrieve English or Vietnamese dictionary entry text and source link.

## Architecture and safeguards

- New file: src/open-knowledge-tools.ts.
- New focused tests: tests/open-knowledge-tools.test.ts.
- AI schemas/dispatch: src/agent-tools.ts and tests/agent-tools.test.ts.
- Uses fixed Wikimedia project hostnames and query parameters; no user-controlled URL or HTML scraping.
- Descriptive User-Agent + Api-User-Agent, JSON, maxlag=5, 12-second timeout and bounded response bodies.
- Search result caps are 10 for Wikipedia and 7 for Wikivoyage; article text is capped at 1,200 characters.
- Thumbnail URLs are accepted only from upload.wikimedia.org.
- HTTP 429/503 and MediaWiki maxlag/API error payloads are surfaced without retry storms.

No new dependencies, API secrets, D1 migrations, Cloudflare bindings or file-processor changes. The existing 534 file processors remain unchanged.

## Important source limitations

- Wikipedia is community edited; important claims require verification against references.
- Wikivoyage may be outdated. Verify transport, hours, fares, visa, safety and current business information through official providers.
- Wiktionary entries may differ by dialect, register or context and should not be described as machine translation.
- A passing mocked test suite does not prove current availability or correctness of live wiki content.

## Production verification — 2026-11-24

- PR CI [45414597298](https://github.com/Nolane-x/Nolane-search/actions/runs/45414597298) passed on the final PR head.
- Main CI #505 [45415054045](https://github.com/Nolane-x/Nolane-search/actions/runs/45415054045) passed TypeScript, 33 Vitest files / 343 tests, deployment-script checks, 449 Python runner tests and Worker build.
- Cloudflare deploy #159 [45415054134](https://github.com/Nolane-x/Nolane-search/actions/runs/45415054134) succeeded. Worker Version ID: `753f8c11-a10b-40f2-a5f2-e09b4bc56923`.
- Worker export #152 [45415054129](https://github.com/Nolane-x/Nolane-search/actions/runs/45415054129) and public health smoke succeeded: `ok: true`, database `reachable`, archive enabled.
- Telegram webhook config check and command registration completed; no D1 migration was required.
- CI and Worker health verify deployment/build, not that every live Wikimedia page is complete or that all live API queries have been individually tested. The adapter remains a low-volume discovery client; source content should be verified when accuracy matters.
