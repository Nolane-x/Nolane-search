# Wave 58 research — cross-catalog barcode lookup and food comparison

Date: 2026-11-24
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-58-open-product-lookup

## Product intent

Improve the existing barcode lookup so that a barcode can be resolved against four related Open Facts catalogs, then add a practical side-by-side food nutrition comparison. This is a barcode-based product identity/data lookup, not a current product-name full-text search.

## Open Facts APIs

- API v3 Get Product Data: https://openfoodfacts.github.io/openfoodfacts-server/api/ref/api-v3/#get-/api/v3/product/-code-
- API v3 OpenAPI definition: https://github.com/openfoodfacts/openfoodfacts-server/blob/main/docs/api/ref/api-v3.yaml
- Standard v3 response-status schema: https://github.com/openfoodfacts/openfoodfacts-server/blob/main/docs/api/ref/responses/response-status/response_status.yaml
- Requested product-type parameter: https://github.com/openfoodfacts/openfoodfacts-server/blob/main/docs/api/ref/parameters/requested_product_type.yaml
- Product-type database guide: https://openfoodfacts.github.io/openfoodfacts-server/api/tutorial-off-api/
- API overview and rate limits: https://openfoodfacts.github.io/openfoodfacts-server/api/
- Product data licensing: https://world.openfoodfacts.org/terms-of-use

### Catalogs and official hosts

- Food: `world.openfoodfacts.org`
- Beauty/cosmetics: `world.openbeautyfacts.org`
- Pet food: `world.openpetfoodfacts.org`
- Other consumer products: `world.openproductsfacts.org`

The API's `product_type=all` parameter searches all product types and may answer with an HTTP 302 redirect to the correct Open Facts database. The adapter starts from the food host and follows at most one redirect, only if the destination is HTTPS, its hostname is one of the four official database hosts, and the path is exactly the requested barcode endpoint. It rejects ports, embedded credentials, unknown hosts, malformed paths and further redirects.

The `product_type` selector can also be set explicitly to `food`, `beauty`, `petfood` or `product` to query one catalog directly.

## Important v3 response correction

The current Open Food Facts API v3 response-status schema documents string values:
- `success`
- `success_with_warnings`
- `success_with_errors`
- `failure`

The existing Wave 52 adapter checked only `status === 1`, a legacy numeric status shape shown in older examples. Wave 58 updates the adapter to accept the documented v3 string statuses (while retaining numeric `1` as backward compatibility) and only reports a successful lookup when a valid product object is present. An HTTP 404 is returned to the caller as `not_found`; 429/503 remain rate-limit/availability errors.

### Current nested nutrition representation

The repository's current API v3.5+ product schema exposes nutrition as `product.nutrition.aggregated_set`:
- `per` identifies the reference quantity (`100g`, `100ml` or `serving`).
- Nutrients are nested under `aggregated_set.nutrients`.
- Each nutrient provides a normalized `value` and may also include `value_computed`.

The adapter prefers this current structure and only exposes it as per-100-g data when `per: 100g` is explicit. A 100 ml or per-serving set is never relabeled as per 100 g. When there is no nutrition object, `nutrition_reference` is null. Negative nutrient values are treated as invalid and remain null. Older flat `nutriments.*_100g` values remain supported as a compatibility fallback.

## New AI-callable operations

- `lookup_consumer_product`: barcode lookup across all Open Facts databases by default, or one explicitly selected catalog. Returns the resolved database, product identity, categories, ingredients/allergens where available, scores/labels, product images and nutrition per 100 g when provided.
- `compare_food_products`: compares 2–4 distinct food barcodes. Requests are sequential to limit burst traffic. It returns each product's available nutrition and per-100-g numerical minima/maxima for metrics that exist in at least two records.

The existing `lookup_food_product` function remains available and now delegates to the corrected v3 food lookup path.

## Data interpretation and limits

- Open Facts records are contributed by users and may be incomplete, incorrect, missing or stale. An absent nutrient is null/missing, never inferred as zero; impossible negative nutrient values are rejected.
- Nutrition comparison is strictly per 100 g and food-only. A product redirected to Beauty/Pet Food/Products Facts is excluded from food comparison. It reports numerical values only; a lower or higher number is not presented as an overall health ranking or a personalized dietary recommendation.
- Nutri-Score, NOVA and environmental score values may be absent, not applicable or based on the specific catalog's coverage. The UI/AI must not infer them when absent.
- Food nutrition fields do not apply to many beauty and general-product records; those results remain useful for identity/ingredients/categorization but expose no invented nutrition.
- Read API traffic is rate-limited. The Open Food Facts overview documents 15 requests/minute/IP for individual product reads and 10 requests/minute/IP for search, with additional global throttling. A single barcode operation performs at most one request normally and follows at most one provider redirect; a comparison is sequential and limited to four barcodes.
- Product images are accepted only from the known images hosts for the four official catalogs; no user-controlled redirect destination is embedded.

## Why full-text product-name search is deferred

The Search-a-licious production index is a potentially useful full-text search service, but Open Food Facts issue #469 reports that the production index stopped receiving product updates after 2024-12-18. The issue remained open in the latest review on 2026-11-24; a maintainer commented on 2026-11-06 that a new release would reinitialize the index. Integrating that endpoint as current product-name search before the re-index/release is verified would create misleading omissions. The Open Food Facts v2 search endpoint is structured/faceted rather than a general full-text `search_term` API. Therefore Wave 58 does not claim to provide reliable current full-text product-name search.

Issue: https://github.com/openfoodfacts/search-a-licious/issues/469
Search API docs: https://openfoodfacts.github.io/openfoodfacts-server/api/ref/search/

## Privacy, security and implementation

- Fixed HTTPS base hosts; no caller-supplied URL.
- Product barcode must be 8–14 digits.
- Manual redirect handling is bounded to one hop and exact path/host validation; no arbitrary redirect following.
- 12-second timeout, User-Agent, bounded JSON body (400 KB).
- No credentials or API key are introduced.
- No new dependency, D1 migration, Cloudflare binding or change to the 534 file-processor catalog.

## Validation

Mocked tests cover documented v3 string statuses, legacy numeric compatibility, the nested v3.5+ nutrition schema, per-100-g enforcement, 100 ml exclusion, missing/negative nutrient handling, HTTP 404, automatic beauty-catalog redirect, pet-food/general-product host routing, unsafe redirect rejection, non-food exclusion from comparisons, input bounds and AI-dispatch integration. CI passed TypeScript, 35 Vitest files / 356 tests, deployment-script checks, 449 Python runner tests and Cloudflare Worker build. Main deployment and health smoke passed; provider live availability and per-barcode data quality remain distinct from mocked CI.

## Sources
- Open Food Facts API v3 specification and response-status schema (links above).
- Open Food Facts API overview / rate limits (link above).
- Search-a-licious issue #469 (link above).
