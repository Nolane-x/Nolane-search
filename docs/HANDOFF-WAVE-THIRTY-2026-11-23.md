# Wave 30 handoff — file format, microscopy and geospatial metadata auditors (2026-11-23)

## Current checkpoint

- Repository: `Nolane-x/Nolane-search`
- Production baseline: **434 tools**, latest deployed Worker Version ID `68ebc068-23aa-4f08-8ff4-d0985926383a`.
- Candidate branch: `feat/wave-thirty-format-and-science-auditors`
- Candidate processors: 3; candidate catalog **437** (434 production + 3 unmerged).
- PR: [#83 — Wave 30: add OME-NGFF, Parquet metadata and COG auditors](https://github.com/Nolane-x/Nolane-search/pull/83). Current head: `f0475a2d3436351f5dee11da836c033a649415fc`.
- No D1 schema change, provider credential, new secret or paid Cloudflare resource is expected.

## Wave 30 processors

1. `ome-ngff-audit` — OME-NGFF 0.6 metadata-only audit for OME version, multiscales, coordinate systems/axes, array dataset paths, array shape/rank, transform metadata and descending resolution order. Reads only bounded Zarr `zarr.json` files from ZIP; never reads pixel/voxel chunks or remote assets.
2. `parquet-metadata-audit` — inspect Parquet file/footer metadata, row-group and column-chunk layout, physical/logical type categories, compression/encoding and GeoParquet `geo` key. DuckDB queries metadata tables only; column names, row data, min/max stats and custom metadata values are suppressed.
3. `cog-geotiff-audit` — run rio-cogeo 7.0.4 COG validation against the local upload path. It does not accept/fetch remote URLs and suppresses raw validation messages, TIFF tags, CRS, bounds and pixels.

## Implementation and limits

- Module: `tools/wave30.py`
- Tests: `tools/test_wave30.py` — 13 synthetic regression tests.
- Catalog and pipeline: `src/tools.ts`.
- Runner: `tools/runner.py`.
- CI dependencies: `.github/workflows/ci.yml`.
- Conditional runner dependencies: `.github/workflows/tool-runner.yml`.
- Upload inference: `experiment.ome.zarr.zip`, `.parquet`, and explicit `.cog.tif/.cog.tiff`. Generic TIFF keeps the existing image flow. Parquet uploads now default to metadata audit; CSV conversion remains available using `/tool parquet-to-csv`.
- OME ZIP bounds reuse Wave 28 safety: 20 MiB compressed input, 10,000 members, 180 MiB expanded; Zarr metadata 2 MiB/file, 10 MiB aggregate.
- Parquet and COG input capped at 20 MiB. Parquet metadata record counts bounded. DuckDB memory is limited to 256 MiB, one thread, and only footer/schema fields are selected. COG dependency is optional and installed only when that tool is selected.
- Current branch registry parity was checked: 437 unique catalog IDs and 437 runner IDs; all three Wave 30 processors have pipeline transitions, handlers and upload inference.
- Wave 30 source has not been deployed. Production stays at 434 until merge, Worker export/health smoke and Cloudflare deployment all pass.

## Test and release gates

1. PR #83 is open. Latest current-head CI [45119158868](https://github.com/Nolane-x/Nolane-search/actions/runs/45119158868) passed type-check, 25 Vitest files / 252 tests, deployment-script checks, 283 Python runner tests and Worker build.
2. Re-check the latest PR head and all checks immediately before merge; fix any new failures before merge.
3. Verify runner/catalog parity and all three inference rules.
4. Merge only when latest-head CI passes.
5. Confirm main CI, Worker export/health smoke and Cloudflare deployment.
6. Check Telegram command menu remains unchanged; no new Telegram command is required.
7. Owner-level acceptance after deployment: upload a synthetic OME-Zarr fixture, a Parquet fixture containing private row values, and a non-sensitive GeoTIFF; confirm metadata reports contain no chunk/pixel/column/statistical values.
8. Keep the production tool count at 434 until deployment is confirmed.

## Production checkpoint

- Wave 29 implementation merge: `a1cbf013170d6bd9e8d1877b85a71ac5acd942e0`
- Latest test-only merge: `c621264baa2d832c621d5732bb991921353987c7`
- Main CI: [45117251696](https://github.com/Nolane-x/Nolane-search/actions/runs/45117251696) — 25 Vitest files / 251 tests, 270 Python runner tests.
- Worker export/health: [45117251681](https://github.com/Nolane-x/Nolane-search/actions/runs/45117251681)
- Cloudflare deploy: [45117251720](https://github.com/Nolane-x/Nolane-search/actions/runs/45117251720)
- Latest Worker Version ID: `68ebc068-23aa-4f08-8ff4-d0985926383a`

Use this file as the next continuation checkpoint; inspect the current branch, PR and workflow state before making further changes.
