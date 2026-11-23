# Wave 30 handoff — file format, microscopy and geospatial metadata auditors (2026-11-23)

## Final production checkpoint — deployed 2026-11-23

- PR [#83](https://github.com/Nolane-x/Nolane-search/pull/83) merged into `main` as commit `44dc33b71f7317d54e9fa9ae1ac6a48b84a06797`.
- Production catalog: **437 tools** (434 before Wave 30 + 3 new processors).
- Latest Worker Version ID: `8f9ca4bf-21ac-4fb7-9e11-fcaaaa3f3d2b`.
- Main CI [45124586861](https://github.com/Nolane-x/Nolane-search/actions/runs/45124586861) passed type-check, 25 Vitest files / 252 tests, deployment-script checks, 283 Python runner tests and Worker build.
- Worker export/health [45124586793](https://github.com/Nolane-x/Nolane-search/actions/runs/45124586793) passed; production health returned `ok: true`, D1 `reachable`, archive enabled.
- Cloudflare deployment [45124586883](https://github.com/Nolane-x/Nolane-search/actions/runs/45124586883) passed; Telegram webhook (message + callback_query) and command menu registered successfully.
- No D1 migration, new secret, provider or paid resource. `rio-cogeo==7.0.4` is installed only for COG jobs.
- Candidate branch and PR are closed/merged. All 437 catalog IDs are unique; all Wave 30 tools have runner allowlist, handlers, pipeline transitions and upload inference.

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

## Remaining owner-level acceptance

Automated CI, Worker health and deployment passed. The remaining checks require using the private Telegram bot with synthetic/non-sensitive files:

1. Upload an OME-Zarr ZIP with multiscale metadata; verify the summary reports axis/array/transform issues without channel labels, coordinates or chunk bytes.
2. Upload a Parquet file containing synthetic private column names/row values; verify only aggregate footer/schema categories appear and no column names, stats or values leak.
3. Upload a COG GeoTIFF and a regular generic TIFF; verify the explicit COG command validates local layout while generic TIFF continues through the existing image flow.
4. Exercise `/tool_job` and `/tool_retry` for the new processors.

These checks were not performed in the user's live Telegram session. Do not describe them as owner-verified until tested.

## Production checkpoint

- Wave 29 implementation merge: `a1cbf013170d6bd9e8d1877b85a71ac5acd942e0`
- Latest test-only merge: `c621264baa2d832c621d5732bb991921353987c7`
- Main CI: [45117251696](https://github.com/Nolane-x/Nolane-search/actions/runs/45117251696) — 25 Vitest files / 251 tests, 270 Python runner tests.
- Worker export/health: [45117251681](https://github.com/Nolane-x/Nolane-search/actions/runs/45117251681)
- Cloudflare deploy: [45117251720](https://github.com/Nolane-x/Nolane-search/actions/runs/45117251720)
- Latest Worker Version ID: `68ebc068-23aa-4f08-8ff4-d0985926383a`

Use this file as the next continuation checkpoint; inspect the current branch, PR and workflow state before making further changes.
