# Wave 55 handoff — open knowledge, travel and dictionary tools

Date: 2026-11-24
Branch: feat/wave-55-wikipedia-travel-wiktionary
Base: 585c081bcfb2b924ac49648c905733483a74882a
Release status: implementation branch; not yet merged or deployed.

## New AI-callable tools

Wikipedia:
- search_wikipedia_articles — search en/vi/ja/fr/es/de editions.
- get_wikipedia_article — fetch a bounded 8,000-character extract, canonical page link, categories and optional Wikimedia thumbnail.

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
- Search result caps are 10 for Wikipedia and 7 for Wikivoyage; article text is capped at 8,000 characters.
- Thumbnail URLs are accepted only from upload.wikimedia.org.
- HTTP 429/503 and MediaWiki maxlag/API error payloads are surfaced without retry storms.

No new dependencies, API secrets, D1 migrations, Cloudflare bindings or file-processor changes. The existing 534 file processors remain unchanged.

## Important source limitations

- Wikipedia is community edited; important claims require verification against references.
- Wikivoyage may be outdated. Verify transport, hours, fares, visa, safety and current business information through official providers.
- Wiktionary entries may differ by dialect, register or context and should not be described as machine translation.
- A passing mocked test suite does not prove current availability or correctness of live wiki content.

## Acceptance gates

1. PR CI passes TypeScript, Vitest, deployment-script checks, Python runner tests and Worker build.
2. Main CI, Cloudflare deployment and Worker export/health smoke pass after merge.
3. Live queries against en/vi Wikipedia, Wikivoyage and Wiktionary should be tested after deployment; content quality remains a source-level review.
