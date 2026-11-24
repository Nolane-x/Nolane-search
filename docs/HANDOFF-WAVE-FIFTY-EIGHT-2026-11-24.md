# Wave 58 handoff — Open Facts barcode lookup and food comparison

Date: 2026-11-24
Branch: feat/wave-58-open-product-lookup-final
Base: a37bdd07b96e3bfc7a50829b41f55d2bf097f2a2
Release status: merged and deployed via [PR #126](https://github.com/Nolane-x/Nolane-search/pull/126) as `a7551a00ee290e7506d6a38d9ec00d088f01f559`.

## New AI-callable tools

- `lookup_consumer_product` — barcode lookup across Open Food Facts, Open Beauty Facts, Open Pet Food Facts and Open Products Facts. Defaults to `product_type=all` and follows at most one strictly validated redirect among the four official hosts; callers can choose a specific catalog.
- `compare_food_products` — compares two to four distinct packaged-food barcodes by data per 100 g.
- Existing `lookup_food_product` stays available for backwards compatibility and now uses the corrected API v3 response handling.

## API correctness fix

The API v3 response schema documents string statuses (`success`, `success_with_warnings`, `success_with_errors`, `failure`). The previous code accepted only numeric status `1`. The new shared reader accepts the current documented string forms when a valid product object is present, but also keeps numeric 1 for compatibility with older response examples. HTTP 404 becomes a not-found result; 429/503 are explicit rate-limit/temporary-unavailable errors.

The current v3.5+ product schema nests nutrients at `product.nutrition.aggregated_set.nutrients`. Values are read from `value` or `value_computed`; the adapter only exposes them as per-100-g measurements when `aggregated_set.per` is explicitly `100g`. Per-100-ml and serving sets are not mislabeled. Missing nutrition has a null reference; negative nutrient values are rejected as invalid. The legacy flat `nutriments.*_100g` format is still supported.

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

## Production verification — 2026-11-24

- PR CI #523 [45427879864](https://github.com/Nolane-x/Nolane-search/actions/runs/45427879864) passed on the verified PR head.
- Main CI #524 [45428128612](https://github.com/Nolane-x/Nolane-search/actions/runs/45428128612) passed TypeScript, 35 Vitest files / 356 tests, deployment-script checks, 449 Python runner tests and Worker build.
- Cloudflare deploy #162 [45428128141](https://github.com/Nolane-x/Nolane-search/actions/runs/45428128141) succeeded. Worker Version ID: `959b78b3-38a6-45d5-b5a4-c2231de31bf7`.
- Worker export #155 [45428128360](https://github.com/Nolane-x/Nolane-search/actions/runs/45428128360) and public health smoke succeeded: `ok: true`, database `reachable`, archive enabled.
- Telegram webhook validation and bot command registration completed. No D1 migration was needed.
- The release checks verify code, Worker build, deployment and health endpoint. They do not prove every barcode exists or that every community-maintained product field is current. Product-name full-text search is not part of this release.

