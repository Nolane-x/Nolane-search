# Wave 51 handoff — country and biodiversity discovery

Date: 2026-11-24  
Branch: `feat/wave-51-country-biodiversity`  
Release status: merged and deployed via [PR #108](https://github.com/Nolane-x/Nolane-search/pull/108) as `666c871c8a056b1b0cc7f3569242ab79ede1482b`.

## Work in this wave

Four new direct model-callable information tools were added:
- `search_country_profiles`
- `get_world_bank_indicators`
- `search_gbif_species`
- `search_gbif_observations`

New implementation: `src/world-data-tools.ts`  
New provider tests: `tests/world-data-tools.test.ts`  
Agent schemas and dispatch: `src/agent-tools.ts`  
Agent catalog expectation: `tests/agent-tools.test.ts`

The existing 534 file processors are unchanged. No API keys, dependencies, migrations or persisted data are added.

## Important behavior

- World Bank indicators return the latest non-empty value per country/indicator; years can differ. Missing data are not filled in.
- The World Bank tool supports a comparison request for up to five ISO alpha-2/alpha-3 country codes and at most eight allowlisted indicators.
- GBIF taxonomy matching is not photo recognition.
- GBIF observations only return human-observation records marked CC0 1.0 or CC BY 4.0, retain attribution/license links, and omit coordinates and precise locality.
- GBIF search can be rate-limited based on server load. The tool surfaces HTTP 429 as a back-off instruction; it does not retry aggressively.
- iNaturalist was deferred until a shared request-budget mechanism can respect its approximately one-request-per-second recommended API use.

## Validation and production status

- PR #108 was merged on 2026-11-24; merge commit: `666c871c8a056b1b0cc7f3569242ab79ede1482b`.
- PR CI [45394865842](https://github.com/Nolane-x/Nolane-search/actions/runs/45394865842) passed.
- Main CI [45395128765](https://github.com/Nolane-x/Nolane-search/actions/runs/45395128765) passed TypeScript, 30 Vitest files / 311 tests, deployment-script checks, 449 Python runner tests and Worker build.
- Cloudflare deploy [45395128692](https://github.com/Nolane-x/Nolane-search/actions/runs/45395128692) succeeded; Worker Version ID: `3e54ef9b-edfb-44e1-b954-736f086aca3f`. Telegram webhook verification and bot-command registration succeeded. D1 migration was skipped because this wave adds no schema changes.
- Worker export/build and public `/health` smoke [45395128757](https://github.com/Nolane-x/Nolane-search/actions/runs/45395128757) succeeded.
- Mocked tests validate parsing, filtering, attribution, redaction and dispatch. They do not prove that every live World Bank/GBIF query will succeed. Perform feature-level sample queries through Telegram/Web Chat separately.


## Primary references

- World Bank API access and query structure: https://datahelpdesk.worldbank.org/knowledgebase/articles/898581
- World Bank API authentication: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
- World Bank API v2 updates: https://datahelpdesk.worldbank.org/knowledgebase/articles/1886674-new-features-and-enhancements-in-the-v2-api
- GBIF API reference: https://techdocs.gbif.org/en/openapi/
- GBIF occurrence search: https://techdocs.gbif.org/en/openapi/v1/occurrence
- GBIF species API: https://techdocs.gbif.org/en/openapi/v1/species
- GBIF rate limits and attribution: https://techdocs.gbif.org/en/openapi/
- iNaturalist recommended practices (source rationale for deferral): https://www.inaturalist.org/pages/api+recommended+practices
- Current REST Countries API documentation (source rationale for deferral): https://restcountries.com/docs
