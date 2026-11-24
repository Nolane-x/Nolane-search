# Wave 51 research — country data and biodiversity discovery

Date: 2026-11-24  
Branch: `feat/wave-51-country-biodiversity`  
Status: merged and deployed via [PR #108](https://github.com/Nolane-x/Nolane-search/pull/108) as `666c871c8a056b1b0cc7f3569242ab79ede1482b`.

## Scope

Wave 51 adds four direct AI-callable read-only discovery tools. The existing 534 file processors are not changed.

1. `search_country_profiles` — searches World Bank country metadata by name, ISO code, capital or region.
2. `get_world_bank_indicators` — retrieves the latest non-empty World Development Indicators for up to five countries in one request.
3. `search_gbif_species` — matches a scientific or common name against the GBIF Taxonomic Backbone.
4. `search_gbif_observations` — retrieves a small page of GBIF human-observation records for a selected taxon and optional country/year filters.

## Provider research and implementation decisions

### World Bank API v2

Official documentation:
- https://datahelpdesk.worldbank.org/knowledgebase/articles/898581
- https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
- https://datahelpdesk.worldbank.org/knowledgebase/articles/1886674-new-features-and-enhancements-in-the-v2-api

The World Bank states that API keys and authentication are not required. The country metadata endpoint exposes ISO codes, country name, region, income level, lending type, capital and geographic coordinates. The Indicators API supports multiple country codes and multiple indicator codes in one request, as well as `MRNEV` to retrieve the most recent non-empty values.

Implementation uses source 2 (World Development Indicators), requests at most five countries and eight allowlisted indicator series, and returns years per indicator instead of implying that all figures are from the same year. Missing or null values remain missing; no interpolation or estimates are generated.

Initial allowlist:
- `population_total` — `SP.POP.TOTL`
- `gdp_current_usd` — `NY.GDP.MKTP.CD`
- `gdp_per_capita_usd` — `NY.GDP.PCAP.CD`
- `gdp_growth_annual_percent` — `NY.GDP.MKTP.KD.ZG`
- `life_expectancy_years` — `SP.DYN.LE00.IN`
- `internet_users_percent` — `IT.NET.USER.ZS`
- `unemployment_percent` — `SL.UEM.TOTL.ZS`
- `inflation_annual_percent` — `FP.CPI.TOTL.ZG`
- `co2_emissions_per_capita` — `EN.ATM.CO2E.PC`
- `urban_population_percent` — `SP.URB.TOTL.IN.ZS`

### GBIF API

Official documentation:
- https://techdocs.gbif.org/en/openapi/
- https://techdocs.gbif.org/en/openapi/v1/species
- https://techdocs.gbif.org/en/openapi/v1/occurrence
- https://techdocs.gbif.org/en/data-use/api-downloads
- https://www.gbif.org/terms

GBIF documents a stable JSON REST API for taxonomic name matching and occurrence searches. It asks integrating applications to identify themselves with a meaningful User-Agent. GBIF does not promise a fixed search throughput: occurrence searches may return HTTP 429 depending on server load, so callers should slow down rather than retry aggressively. The implementation uses a 12-second timeout, a 500 KB response cap, redirects disabled, and a project-identifying User-Agent. It retrieves a maximum of 100 candidate records from a single page before applying the caller's smaller output limit; it does not paginate or perform bulk downloads.

The occurrence tool is deliberately constrained:
- only `HUMAN_OBSERVATION` and `PRESENT` records are queried;
- only records explicitly marked CC0 1.0 or CC BY 4.0 are returned;
- CC BY-NC, CC BY-SA, other and missing license values are excluded;
- contributor/dataset attribution and license links are retained for returned records;
- exact coordinates and locality descriptions are omitted to avoid disclosing sensitive species locations;
- no occurrence media or raw dataset files are fetched.

Taxon matching is a taxonomy lookup, not photo recognition and not a confirmation that a user-supplied organism has been identified correctly. Occurrence records represent evidence collected at a particular time by contributing datasets; they are not proof of current presence. GBIF search results may be rate-limited under load.

## Rejected / deferred sources

- REST Countries hosted API was not adopted: its current official documentation describes bearer-key authentication, monthly quotas and rate limiting, so it no longer satisfies a no-key default integration.
- iNaturalist direct API access was deferred: its official recommended practices ask clients to stay around one request per second and roughly 10,000 API requests per day, using a custom User-Agent. A future iNaturalist integration should include a shared, cross-isolate request budget rather than assuming a per-isolate delay is sufficient.
- No observation images or media are imported in this wave; image licensing differs record-by-record and is not needed for the metadata discovery workflow.

## Security and operational constraints

- No user-provided URL is fetched; all upstream hosts and paths are fixed in code.
- Redirects are rejected, timeouts are bounded, and JSON response bodies are capped.
- Input lengths, ISO country codes, year ranges, result counts and indicator names are validated before requests.
- Country indicator codes are allowlisted; GBIF occurrence queries require a numeric taxon key.
- No new API keys, package dependencies, database schema, D1 migrations, file downloads or scraping are introduced.
- The four functions are exposed through the existing model tool interface; no new bot command syntax or Telegram command registration is required.
- The 534-item file processor catalogue is unchanged.

## Validation plan

Mocked tests cover World Bank country response parsing, aggregate exclusion, ISO alpha-2/alpha-3 comparison, multi-country/multi-indicator requests, indicator allowlists, GBIF species matches and unmatched names, license filtering, attribution retention, coordinate/locality redaction, input validation and HTTP 429 handling. The full repository CI must also pass before merge. A CI success or Worker health check is not represented as proof that every live provider query works for every user.

## Production evidence

- PR CI [45394865842](https://github.com/Nolane-x/Nolane-search/actions/runs/45394865842) succeeded.
- Main CI [45395128765](https://github.com/Nolane-x/Nolane-search/actions/runs/45395128765) succeeded: type-check, 30 Vitest files / 311 tests, deployment-script checks, 449 Python runner tests and Worker build.
- Cloudflare deployment [45395128692](https://github.com/Nolane-x/Nolane-search/actions/runs/45395128692) succeeded. Worker Version ID: `3e54ef9b-edfb-44e1-b954-736f086aca3f`. Telegram webhook was verified and bot commands were registered; no D1 migration was required.
- Worker build/export and public `/health` smoke [45395128757](https://github.com/Nolane-x/Nolane-search/actions/runs/45395128757) succeeded.
- These CI and health results do not establish successful real queries to every live World Bank or GBIF route. Keep feature-level acceptance separate.

