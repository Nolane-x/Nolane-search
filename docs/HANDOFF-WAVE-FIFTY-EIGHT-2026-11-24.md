# Wave 58 handoff — Open Facts barcode lookup and food comparison

Date: 2026-11-24
Branch: feat/wave-58-open-product-lookup
Base: a37bdd07b96e3bfc7a50829b41f55d2bf097f2a2
Release status: implementation branch; not yet merged or deployed.

## New AI-callable tools

- `lookup_consumer_product` — barcode lookup across Open Food Facts, Open Beauty Facts, Open Pet Food Facts and Open Products Facts. Defaults to `product_type=all` and follows at most one strictly validated redirect among the four official hosts; callers can choose a specific catalog.
- `compare_food_products` — compares two to four distinct packaged-food barcodes by data per 100 g.
- Existing `lookup_food_product` stays available for backwards compatibility and now uses the corrected API v3 response handling.

## API correctness fix

The API v3 response schema documents string statuses (`success`, `success_with_warnings`, `success_with_errors`, `failure`). The previous code accepted only numeric status `1`. The new shared reader accepts the current documented string forms when a valid product object is present, but also keeps numeric 1 for compatibility with older response examples. HTTP 404 becomes a not-found result; 429/503 are explicit rate-limit/temporary-unavailable errors.

## Safety and data interpretation

- Only four official Open Facts hosts are accepted for automatic redirect; one hop maximum; exact barcode path; HTTPS only; no credentials or nonstandard ports.
- Product images are accepted only from the corresponding Open Facts image hosts.
- Missing nutrient values remain null/missing. Comparison reports numeric minima/maxima, not a health score.
- Comparison is per 100 g and does not provide medical, diet or personalized food recommendations.
- Open Facts community data may be incomplete or stale; product categories differ in available fields.

## Why text search is not included

Search-a-licious issue #469 reported that its production product index stopped updating after 2024-12-18 and remained open when reviewed on 2026-11-24. A maintainer mentioned a planned release/reinitialization, but the production re-index was not verified. The general Open Food Facts v2 search endpoint is structured/faceted rather than free-text search. Wave 58 therefore avoids promising complete/current product-name search until the full-text production index is confirmed healthy.

## Files

- `src/media-discovery-tools.ts`
- `src/agent-tools.ts`
- `tests/media-discovery-tools.test.ts`
- `tests/agent-tools.test.ts`
- Research: `docs/TOOL-RESEARCH-2026-11-24-WAVE58.md`

No new dependencies, API secrets, D1 migrations, Cloudflare bindings or changes to the 534 file-processor catalog.

## Acceptance gates

1. PR CI passes TypeScript, Vitest, deployment-script checks, Python runner tests and Cloudflare Worker build.
2. Main CI, Cloudflare deployment and Worker export/health smoke pass after merge.
3. Live barcode lookups across food/beauty/petfood/product remain separate from mocked tests; not every barcode exists in every catalog.
4. Product-name full-text search remains deferred until Open Food Facts confirms the production search index has been reinitialized and current.