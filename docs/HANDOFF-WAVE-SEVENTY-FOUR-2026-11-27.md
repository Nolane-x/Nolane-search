# Wave 74 handoff — 2026-11-27

**Branch:** `feat/wave-74-search-provider-provenance`  
**Scope:** preserve and surface retrieval-provider provenance for normalized search results  
**State:** merged and deployed. PR [#151](https://github.com/Nolane-x/Nolane-search/pull/151) merged into `main` as `3bcadb6dc860fdfdf0ff040d5cfa445153928a0e`. PR CI #45952497652 and main CI #45953948895 passed; Cloudflare deploy #45953948881 and Worker export #45953948885 succeeded. The feature is also included in the later current-main deployment #46004048399.

## Problem

Federated search merges results from Tavily, Exa, Brave, TinyFish, Wikipedia, GitHub and the private Nolane index. Before this wave, URL deduplication retained only the winning result object, losing the other retrieval providers that had returned the same normalized URL.

## Implementation

- Adds optional `SearchResult.discoveredBy` metadata.
- The shared reranker unions provider labels when normalized URLs collide, deduplicates labels, caps the list at eight and still retains the highest-ranked result's content and primary `provider` field.
- A second ranking pass after TinyFish page enrichment preserves the original provider trail instead of treating the fetch enrichment as a search provider.
- Web UI and Telegram search/Deep Search displays show the retrieval-provider list only when more than one provider found the URL.
- Browser Ask, Telegram Ask and Deep Search synthesis receive retrieval-provider metadata.
- Prompts explicitly state that provider overlap is retrieval metadata only, not independent source corroboration, source verification or proof of truth.
- No new provider, API key, secret, database table, paid service or background service is introduced.

## Tests

- Reranking test covers UTM/fragment URL normalization, multiple provider hits, duplicate hits from the same provider, winner preservation and a second enrichment reranking pass.
- Telegram tests cover provider-path display and HTML escaping.
- Existing CI should continue to run TypeScript checks, all Vitest tests, Python runner tests, Worker build and browser smoke suites.

## Boundaries

- This feature records where Nolane discovered a URL; it does not certify the publisher, page contents, factual accuracy or independence of the underlying reporting.
- Different URLs that syndicate the same article are not clustered by this change.
- Older cached results may lack `discoveredBy` until their existing short TTL expires; renderers safely fall back to the existing primary provider label.
- No owner-side configuration is required. The feature adds no provider, API key, secret, database table, paid service or migration.
