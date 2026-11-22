# Verified Project Status

Last verified: 2026-11-22. Production deployment evidence is separated from owner-level Telegram upload/retry journeys.

# Verified Project Status

Last verified: 2026-11-22. Production deployment evidence is kept separate from owner-level Telegram file-upload/retry checks.

## In review — Wave 26 candidate (2026-11-22)

- Branch: `feat/wave-twenty-six-bioinformatics-tools`.
- Eleven additional processors are registered across TypeScript catalog, Python RUNNERS allowlist, handler dispatch, pipeline transitions and upload inference. Candidate catalog: **417 tools**; production remains **406** until all release gates pass.
- New domains: FASTA/FASTQ sequence records, VCF variant calls, SAM read alignments, GFF3/GTF annotation, BED genomic intervals, GenBank flat files, PDB structure records, GFA assembly graphs, Newick trees and Clustal/Stockholm alignments.
- Twenty-three dedicated Python regression tests cover privacy-preserving summaries, gzip streams, malformed records, coordinates/field widths, sequence/quality lengths, graph references, tree syntax and alignment block lengths. No new runtime dependency is introduced.
- Genomic/sequence inputs can contain sensitive or identifying human data. Reports withhold identifiers, sample labels, sequence/genotype content and coordinates, but source files still pass through the existing ephemeral GitHub-hosted runner. Do not upload regulated/patient data without authorization.
- Plain `.vcf` is ambiguous with vCard; automatic inference requires genomic MIME or `.vcf.gz`, while direct `/tool vcf-variant-audit` remains available for plain VCF.
- PR CI, Worker export/health smoke and Cloudflare deployment are pending for Wave 26.
- Owner-level E2E after release: test synthetic/non-sensitive FASTA/FASTQ/VCF/SAM/GFF3/BED/GenBank/PDB/GFA/Newick/Stockholm files through private Telegram, inspect delivered reports and verify `/tool_retry`.
## Latest production release — Wave 25 (2026-11-22)

- [PR #77](https://github.com/Nolane-x/Nolane-search/pull/77) merged into `main` as commit `bd5b51cd119d049dd14a654147d03a4303fa7e2c`; eleven processors increased production from 395 to **406 tools**.
- Main CI [45017239242](https://github.com/Nolane-x/Nolane-search/actions/runs/45017239242) passed TypeScript type-check, all **25 Vitest files**, deployment-script checks, **206 Python runner tests** and Worker build.
- Worker export [45017239294](https://github.com/Nolane-x/Nolane-search/actions/runs/45017239294) passed source verification, Cloudflare build, build-output publication and production `/health` smoke.
- Cloudflare deployment [45017239222](https://github.com/Nolane-x/Nolane-search/actions/runs/45017239222) passed source validation, build, deployment-bundle validation, Worker upload, runtime-secret upload and Telegram webhook/command-menu registration. D1 migration was skipped because Wave 25 introduced no database schema changes.
- Cloudflare API confirms Worker Version 82, `22378573-aa24-444d-96b0-59e8df345b75`, receives **100% of production traffic** under deployment `1479f8fc-5c7c-4615-a3af-abe1fbb895f5`.
- Added WebAssembly, SARIF, CycloneDX/SPDX SBOM, JUnit, Cobertura/JaCoCo, FITS, STEP CAD, OpenTelemetry, Godot, Unity and Unreal inspectors.
- Registry parity: **406 unique TypeScript catalog IDs, 406 Python runner allowlist IDs and 406 Python handlers**. All eleven new IDs have upload inference and pipeline transitions.
- No new runtime dependency or D1 migration was required; PyYAML is installed conditionally for the OpenTelemetry auditor.
- Owner-level E2E remains: upload representative WASM, SARIF, CycloneDX/SPDX, JUnit, coverage, FITS, STEP, OTel YAML, Godot, Unity and Unreal files through the private Telegram bot, inspect reports and test `/tool_retry`. CI and webhook registration do not prove every Telegram upload journey.

## Previous production release — Wave 24 (2026-11-22)

- [PR #76](https://github.com/Nolane-x/Nolane-search/pull/76) merged into `main` as commit `dc13766a6afdef744e165c231803130db5e2a3a0`; twelve processors increased production from 383 to **395 tools**.
- Main CI [45015606847](https://github.com/Nolane-x/Nolane-search/actions/runs/45015606847) passed TypeScript type-check, all **25 Vitest files**, deployment-script checks, **189 Python runner tests** and Worker build.
- Worker export [45015606799](https://github.com/Nolane-x/Nolane-search/actions/runs/45015606799) passed source verification, Cloudflare build, build-output publication and production `/health` smoke. The health response was `ok: true` with database `reachable`.
- Cloudflare deployment [45015606838](https://github.com/Nolane-x/Nolane-search/actions/runs/45015606838) passed source validation, build, deployment-bundle validation, Worker upload, runtime-secret upload and Telegram webhook/command-menu registration. D1 migration was skipped because Wave 24 introduced no database schema changes.
- Cloudflare API confirms Worker Version 81, `af2311df-8bac-4597-aaec-e0115fb3106f`, receives **100% of production traffic** under deployment `83aa00b4-99f7-4477-8273-ed29ce46879f`.
- Added OpenDocument package, XLIFF translation QA, MBOX privacy audit, GeoPackage and MBTiles, OpenRaster and Krita project, glTF/GLB, draw.io, n8n workflow, W3C Design Tokens and WARC auditors.
- Registry parity: **395 unique TypeScript catalog IDs, 395 Python runner allowlist IDs and 395 Python handlers**. All twelve new IDs have upload inference and pipeline transitions.
- No new runtime/CI dependency or D1 migration was required; Wave 24 uses Python standard library and SQLite only.
- Owner-level E2E remains: send representative ODT/ODS/ODP, XLIFF, MBOX, GPKG/MBTiles, ORA/KRA, glTF/GLB, draw.io, n8n JSON, Design Tokens and WARC files through the private Telegram bot, inspect delivered reports and test `/tool_retry`. Automated tests and webhook registration do not prove every Telegram upload journey.

## Previous production release — Wave 23 (2026-11-22)

- [PR #75](https://github.com/Nolane-x/Nolane-search/pull/75) merged into `main` as commit `32f2fbb4e6936a5caea0bf552e337c852797a1e7`; twelve processors increased the catalog from 371 to **383 tools**.
- Main CI [45013947086](https://github.com/Nolane-x/Nolane-search/actions/runs/45013947086) passed type-check, all **25 Vitest files**, deployment-script checks, **175 Python runner tests** and Worker build.
- Worker export [45013946991](https://github.com/Nolane-x/Nolane-search/actions/runs/45013946991) passed the production health smoke; deployment [45013946981](https://github.com/Nolane-x/Nolane-search/actions/runs/45013946981) passed. Cloudflare Worker Version 80 `f30ef26b-02c1-4d57-922a-acf3e698669d` received 100% traffic before Wave 24.
- Wave 23 added CNC/G-code, MIDI, MusicXML, BibTeX, NMEA/GNSS, Ansible, Prometheus, Grafana, HDF5, Avro, GraphQL SDL and Protocol Buffers.
- Owner-level Telegram E2E remains a separate check for representative uploads and `/tool_retry`.

## Previous production release — Wave 20 (2026-11-22)

- Wave 20 landed directly on `main` as commit `32aede18727b75b2cef2a06b7d603615bedcdac0`; it adds nine processors and raises the production catalog from 336 to **345 tools**.
- Main CI [44982433603](https://github.com/Nolane-x/Nolane-search/actions/runs/44982433603) passed TypeScript type-check, Vitest, deployment-script checks, **136 Python runner tests**, and Worker build.
- Worker export and production health smoke [44982433601](https://github.com/Nolane-x/Nolane-search/actions/runs/44982433601) passed.
- Cloudflare deployment [44982433602](https://github.com/Nolane-x/Nolane-search/actions/runs/44982433602) passed source/bundle validation, Worker upload, runtime-secret upload and Telegram webhook/command-menu registration. D1 migration was skipped because Wave 20 has no schema changes.
- Production Worker Version ID: `8eeb9bd7-77f7-4205-898a-db49f35424ce`.
- Added tools: RSS/Atom audit, sitemap XML audit, robots.txt audit, JSONL profiling, image metadata privacy audit, SVG active-content audit, WCAG contrast checker, SSH public-key audit and ZIP SHA-256 manifest.
- Owner-level E2E remains: upload representative RSS/Atom, sitemap/robots, JSONL, image, SVG, color-pair TXT, SSH public-key and ZIP files in private Telegram; inspect outputs and test `/tool_retry`. CI/deployment does not prove that direct Telegram journey.

## Previous production release — Wave 19 (2026-11-22)

- [PR #69](https://github.com/Nolane-x/Nolane-search/pull/69) merged as commit `063b73168111db96acb799df27e1c9fb5f11d3e6`.
- Production catalog: **336 processors**, up from 328 in Wave 18.
- Added eight distinct processors: PCAP/PCAPNG network audit, audio tag completeness, 16×16 DCT perceptual image similarity, JSON Schema validation, EPUB structure audit, Markdown quality audit, BIND DNS zone audit and X.509 certificate audit.
- Main CI [44981447755](https://github.com/Nolane-x/Nolane-search/actions/runs/44981447755), Worker export and production health smoke [44981447745](https://github.com/Nolane-x/Nolane-search/actions/runs/44981447745) and Cloudflare deploy [44981447683](https://github.com/Nolane-x/Nolane-search/actions/runs/44981447683) all passed.
- Main CI passed TypeScript type-check, Vitest, deployment script checks, **127 Python runner tests**, and Worker build.
- Deployment verified Worker bundle, runtime secrets, Telegram webhook and command-menu registration. D1 migration was skipped because Wave 19 made no schema change.
- Production Worker Version ID: `f7be3cf0-1370-4333-84be-af5f22e6f012`.
- Remaining owner-level E2E: send representative PCAP/PCAPNG, audio, image ZIP, JSON Schema envelope, EPUB, Markdown, DNS zone and X.509 files to the private Telegram bot; inspect results and test `/tool_retry`. CI/deploy does not prove these direct user interactions.

## Previous production release — Wave 18 (2026-11-22)

- [PR #68](https://github.com/Nolane-x/Nolane-search/pull/68) merged as commit `374f4c011a59e50e30ac0ace5891d458b32407ff`.
- Production catalog: **328 processors**, up from 318 in Wave 17.
- Added ten cross-domain processors for HAR privacy, iCalendar, vCard, GPX, GeoJSON, QR generation, font metadata, subtitle repair, OpenAPI contracts and color conversion.
- Main CI [44980373517](https://github.com/Nolane-x/Nolane-search/actions/runs/44980373517), Worker export/production smoke [44980373519](https://github.com/Nolane-x/Nolane-search/actions/runs/44980373519) and Cloudflare deploy [44980373529](https://github.com/Nolane-x/Nolane-search/actions/runs/44980373529) passed.
- CI passed TypeScript type-check, Vitest, deployment-script checks, all **119 Python runner tests** and Worker build.
- Deployment verified Worker bundle, runtime-secret upload, Telegram webhook and command-menu registration. D1 migration step was skipped because Wave 18 introduced no schema change.
- Production Worker Version ID: `1271380c-e118-4731-ad33-5f38adcd20c8`.
- Remaining owner-level E2E: upload representative HAR, ICS, VCF, GPX, GeoJSON, TXT, font, SRT/VTT and OpenAPI files in private Telegram; inspect reports/output and exercise `/tool_retry`. CI and deployment do not prove these real Telegram interactions.

## Previous production release — Wave 17 (2026-11-22)

- [PR #67](https://github.com/Nolane-x/Nolane-search/pull/67) merged as commit `66aeb33c1319c161b224d8e65df1832e11bce4ac`.
- Production catalog: **318 processors**, up from 316 in Wave 16.
- Added `email-security-audit` (.eml) and `jwt-security-audit` structural auditors. They redact addresses, URLs, attachment names, JWTs and claim values. Email authentication headers are untrusted assertions; the tools do not query DNS, verify SPF/DKIM/DMARC or cryptographically validate JWT signatures.
- Main CI [44977998187](https://github.com/Nolane-x/Nolane-search/actions/runs/44977998187), Worker export/smoke [44977998129](https://github.com/Nolane-x/Nolane-search/actions/runs/44977998129) and production deployment [44977998189](https://github.com/Nolane-x/Nolane-search/actions/runs/44977998189) passed.
- Deployment verified source, Worker bundle, runtime-secret upload and Telegram webhook/command registration. D1 migration step was skipped because no migration changed.
- Worker Version ID: `f3180bcc-896d-4fef-9887-c81146865265`.
- Remaining owner-level E2E: upload representative EML/JWT files in private Telegram, inspect reports and test retry. CI and deployment do not prove these real Telegram interactions.
## Repository and production release

- Repository: https://github.com/Nolane-x/Nolane-search
- Default branch: `main`
- Latest production source commit: `063b73168111db96acb799df27e1c9fb5f11d3e6`
- Browser search and retrieval upgrade: [PR #2](https://github.com/Nolane-x/Nolane-search/pull/2)
- Bounded site indexing and search feedback: [PR #3](https://github.com/Nolane-x/Nolane-search/pull/3)
- Hybrid personal-index retrieval and sitemap crawler upgrade: [PR #4](https://github.com/Nolane-x/Nolane-search/pull/4)
- Interactive Telegram workspace and contextual search actions: [PR #5](https://github.com/Nolane-x/Nolane-search/pull/5)
- Fix Telegram callback delivery and stuck inline-button spinners: [PR #6](https://github.com/Nolane-x/Nolane-search/pull/6)
- Lightweight Personal Memory, AI efficiency, request-body limits and usage visibility: [PR #7](https://github.com/Nolane-x/Nolane-search/pull/7)
- Register Personal Memory commands in Telegram's slash-command menu: [PR #8](https://github.com/Nolane-x/Nolane-search/pull/8)
- Provider response limits, watch redirect isolation and TinyFish URL validation: [PR #9](https://github.com/Nolane-x/Nolane-search/pull/9)
- Personal Web Index manager in Web and Telegram, including safe removal and watch deactivation: [PR #10](https://github.com/Nolane-x/Nolane-search/pull/10)
- Telegram and Web per-minute usage caps introduced by [PR #11](https://github.com/Nolane-x/Nolane-search/pull/11) were removed by [PR #12](https://github.com/Nolane-x/Nolane-search/pull/12); Personal Web Index federation was added in the same release.
- Production Worker: https://nolane-search.nolane-file.workers.dev
- Cloudflare Worker Version ID: `f7be3cf0-1370-4333-84be-af5f22e6f012`, deployed by [GitHub Actions run 44981447683](https://github.com/Nolane-x/Nolane-search/actions/runs/44981447683) on 2026-11-22 at 03:37 UTC from main commit `063b73168111db96acb799df27e1c9fb5f11d3e6`.

The release adds a private browser search portal, AI Overview, multi-turn chat, multi-signal federated retrieval ranking, relevance-aware provider fallback, AI-assisted Deep Search query planning, owner-controlled bounded site indexing, title-weighted BM25 retrieval over the personal FTS5 index, recursive same-origin sitemap discovery, semantic article/main extraction per-result helpful/not-helpful feedback, an interactive Telegram dashboard with one-shot search/AI modes and contextual search follow-ups, plus a verified Telegram callback webhook and immediate callback acknowledgement.

## Wave 7 production release — 2026-11-21 (superseded by Wave 8 below)

- PR #45 ([261-tool Wave 7](https://github.com/Nolane-x/Nolane-search/pull/45)) was merged into `main`.
- Main commit: `35a33c5b52901e3b3dc1e8471dae18fb9ba4a5c8`.
- Production Worker version 56: `4f33b8bb-47db-4645-b58d-46899021030e`; deployment run [44873192198](https://github.com/Nolane-x/Nolane-search/actions/runs/44873192198) succeeded.
- Main CI [44873192204](https://github.com/Nolane-x/Nolane-search/actions/runs/44873192204) passed type-check, unit tests, deployment-script checks, Python runner tests and Worker build.
- Worker bundle export and production smoke test [44873192195](https://github.com/Nolane-x/Nolane-search/actions/runs/44873192195) passed.
- Telegram deployment verification confirmed both `message` and `callback_query` webhook updates and successful command-menu registration.
- Wave 7 adds 14 processors and raises the catalog from 247 to 261: developer/network text, CSV-to-SQL/YAML, CSV reports and JSON cleanup/type/nesting utilities.
- D1 migrations verified in `schema_migrations`: `0001_core.sql`, `0002_deep_search_jobs.sql`, `0003_web_portal.sql`, `0004_remove_request_rate_limits.sql`. No new migration was needed for Wave 7.
- Read-only D1 inspection confirmed `indexed_pages` (1 row), `watches` (2 rows), `telegram_updates` (55 rows), and the existing tool/search/job tables. Cloudflare's D1 metadata `num_tables` field returned 0 even though `sqlite_master` lists the existing tables; direct SQLite inspection is the authoritative check here.
- Still pending owner-level verification: send a real small text/CSV/JSON file to the Telegram bot, receive the processed output, exercise a safe retry, and confirm optional archive-channel delivery. CI and webhook registration do not prove the full user interaction.

## Wave 8 production release — 2026-11-21 (superseded by Wave 9 below)

- PR #47 ([Configuration and DevOps suite](https://github.com/Nolane-x/Nolane-search/pull/47)) was merged into `main`.
- Main commit: `4b7db4f7eaaae44810df68d43ae3c9486187dbb6`.
- Production Worker version 57: `a86e4cb5-3747-4476-b87e-31abb6793062`; Cloudflare deployment distribution is 100% on this version.
- Main CI [44874848990](https://github.com/Nolane-x/Nolane-search/actions/runs/44874848990) passed type-check, 188 unit tests, deployment-script checks, 94 Python runner tests and Worker build.
- Cloudflare build/export and production Worker smoke test [44874849018](https://github.com/Nolane-x/Nolane-search/actions/runs/44874849018) passed.
- Production deployment [44874848974](https://github.com/Nolane-x/Nolane-search/actions/runs/44874848974) passed runtime-secret upload and Telegram webhook/command-menu registration. Webhook `message` and `callback_query` were verified with `getWebhookInfo`.
- Wave 8 adds 14 tools to the 261-tool Wave 7 catalog, giving 275 unique catalog IDs. New groups cover dotenv safety, INI/TOML/Java Properties, Dockerfile/Compose, Python requirements, package.json, gitignore and environment-variable references.
- Ten Wave 8 processors are enabled for bounded direct AI text processing. TOML, Java Properties and Docker Compose YAML parsing run in the isolated file runner; do not claim they are all direct chat parsers.
- No D1 schema change was included. Deployment correctly skipped migration application; read-only `schema_migrations` inspection still shows `0001_core.sql` through `0004_remove_request_rate_limits.sql`, and the existing tables remain present.
- ENV audit/reference reports expose names and counts, not secret values. Docker and dependency audits are static; they do not build/run containers, install packages, execute scripts or query vulnerability registries.
- Remaining owner-level check: upload a small real `.env`, `.ini`, `.toml`, `compose.yaml` and `.properties` file through Telegram, inspect returned artifacts, and test a safe retry. This has not been exercised by CI, webhook checks or this deployment.

## Latest production release — Wave 9 — 2026-11-21

- PR #49 ([Infrastructure and CI/CD security auditors](https://github.com/Nolane-x/Nolane-search/pull/49)) was merged into `main`.
- Main commit: `a685b9853b86b196b29805f6490ebd37d0144033`.
- Production Cloudflare Worker version 58: `519bee0c-6f42-4c76-bcfb-d86c546040ac`; latest deployment distribution is 100% on this version.
- Main CI [44880518949](https://github.com/Nolane-x/Nolane-search/actions/runs/44880518949) passed TypeScript type-check, 21 test files / 190 unit tests, deployment-script checks, 96 Python runner tests and Worker build.
- Cloudflare export/build and deployed Worker smoke test [44880518912](https://github.com/Nolane-x/Nolane-search/actions/runs/44880518912) passed.
- Production deployment [44880519016](https://github.com/Nolane-x/Nolane-search/actions/runs/44880519016) passed bundle validation, runtime-secret upload and Telegram webhook/command registration. D1 migration step was skipped because Wave 9 changes no schema.
- Telegram webhook was verified for `message` and `callback_query`; the bot command menu was registered successfully.
- Wave 9 adds eight auditors to the 275-tool Wave 8 production catalog, bringing production to 283 unique tools: GitHub Actions, Kubernetes, Terraform, Nginx, Apache, Caddy, systemd and shell.
- Six text-only auditors (Terraform, Nginx, Apache, Caddy, systemd and shell) are available through bounded direct AI processing. GitHub Actions and Kubernetes YAML audits remain runner-based and use YAML parsing.
- Audits are static heuristics: no workflow dispatch, cluster access, terraform init/plan/apply, server/service startup or shell execution. Credential values are omitted from reports.
- Read-only D1 inspection confirms migrations `0001_core.sql` through `0004_remove_request_rate_limits.sql` and the existing SQLite tables. Cloudflare's summary `num_tables` field may return 0; `sqlite_master` inspection is authoritative.
- Still pending owner-level verification: send real `.tf`, `.yaml`, `.conf`, `.service` and `.sh` files through Telegram, inspect returned artifacts and test a safe retry. CI/webhook registration does not prove the complete user interaction.

## CI and deployment verification

| Check | Run | Result |
|---|---:|---|
| PR CI: typecheck, 58 unit tests, script syntax checks and Worker build | [44245521279](https://github.com/Nolane-x/Nolane-search/actions/runs/44245521279) | PASS |
| PR #6 CI: typecheck, 61 unit tests, webhook regression check and Worker build | [44255034696](https://github.com/Nolane-x/Nolane-search/actions/runs/44255034696) | PASS |
| Main CI: typecheck, 61 unit tests, webhook regression check and Worker build | [44255150160](https://github.com/Nolane-x/Nolane-search/actions/runs/44255150160) | PASS |
| Worker bundle export and production smoke test | [44255150131](https://github.com/Nolane-x/Nolane-search/actions/runs/44255150131) | PASS |
| Production Worker deployment, runtime secret upload, webhook and command registration | [44255150124](https://github.com/Nolane-x/Nolane-search/actions/runs/44255150124) | PASS |
| PR #7 CI: typecheck, 72 unit tests, webhook checks and Worker build | [44270510551](https://github.com/Nolane-x/Nolane-search/actions/runs/44270510551) | PASS |
| PR #7 main CI | [44270643224](https://github.com/Nolane-x/Nolane-search/actions/runs/44270643224) | PASS |
| PR #7 Worker bundle export and production smoke test | [44270643846](https://github.com/Nolane-x/Nolane-search/actions/runs/44270643846) | PASS |
| PR #7 production deployment | [44270643085](https://github.com/Nolane-x/Nolane-search/actions/runs/44270643085) | PASS |
| PR #8 CI: Telegram slash-command registration | [44271133530](https://github.com/Nolane-x/Nolane-search/actions/runs/44271133530) | PASS |
| PR #8 main CI: 72 tests and Worker build | [44271236172](https://github.com/Nolane-x/Nolane-search/actions/runs/44271236172) | PASS |
| PR #8 Worker bundle export and production smoke test | [44271236099](https://github.com/Nolane-x/Nolane-search/actions/runs/44271236099) | PASS |
| PR #8 production deployment and Telegram command registration | [44271236228](https://github.com/Nolane-x/Nolane-search/actions/runs/44271236228) | PASS |
| PR #9 CI: typecheck, 78 unit tests, webhook checks and Worker build | [44274411447](https://github.com/Nolane-x/Nolane-search/actions/runs/44274411447) | PASS |
| PR #9 main CI: 78 unit tests and Worker build | [44274472317](https://github.com/Nolane-x/Nolane-search/actions/runs/44274472317) | PASS |
| PR #9 Worker bundle export and production smoke test | [44274472497](https://github.com/Nolane-x/Nolane-search/actions/runs/44274472497) | PASS |
| PR #9 production deployment and Telegram command registration | [44274472339](https://github.com/Nolane-x/Nolane-search/actions/runs/44274472339) | PASS |
| PR #10 CI: typecheck, 84 unit tests, webhook checks and Worker build | [44283578933](https://github.com/Nolane-x/Nolane-search/actions/runs/44283578933) | PASS |
| PR #10 main CI: 84 unit tests and Worker build | [44283762795](https://github.com/Nolane-x/Nolane-search/actions/runs/44283762795) | PASS |
| PR #10 Worker bundle export and production smoke test | [44283762813](https://github.com/Nolane-x/Nolane-search/actions/runs/44283762813) | PASS |
| PR #10 production deployment and Telegram command registration | [44283763167](https://github.com/Nolane-x/Nolane-search/actions/runs/44283763167) | PASS |
| PR #12 CI: type-check, 87 unit tests, webhook checks and Worker build | [44295647765](https://github.com/Nolane-x/Nolane-search/actions/runs/44295647765) | PASS |
| PR #12 main CI: 87 unit tests and Worker build | [44296385809](https://github.com/Nolane-x/Nolane-search/actions/runs/44296385809) | PASS |
| PR #12 Worker bundle export and smoke test | [44296385774](https://github.com/Nolane-x/Nolane-search/actions/runs/44296385774) | PASS |
| PR #12 production deployment and Telegram webhook/command registration | [44296385765](https://github.com/Nolane-x/Nolane-search/actions/runs/44296385765) | PASS |

The deployment log confirms:
- Worker `nolane-search` was uploaded and deployed.
- Runtime `AI_ROUTER_CONFIG` was uploaded as a hidden secret.
- Cron `*/30 * * * *` and Queue producer/consumer bindings remained attached.
- Telegram webhook registration succeeded.
- Telegram bot command registration succeeded, including `/web`, `/start`, `/menu` and `/cancel`.
- Worker version `e182d473-d214-4a0c-82c5-0c8662fb4b87` was deployed from main commit `ffe1564ebfa1db5a00960c92e88e19dc6a84fb20` (PR #6 callback repair).
- Worker version `40974932-b150-4373-995a-ea73facd13ad` deployed PR #7; Worker version `6eaac094-1dbe-494d-9393-ef0a66e94ddb` deployed PR #8 command-menu update; Worker version `a2c2372a-6f95-43f6-9839-9bbf5f7acb0e` deployed PR #9 upstream/redirect hardening.
- Telegram webhook update subscriptions were verified by calling `getWebhookInfo`; the returned configuration contains both `message` and `callback_query` for the expected Worker URL.
- No D1 migration was needed for the Telegram callback fix.
- Worker version `ccbb1cb9-3d89-4290-a471-92c44a333711` was deployed from main commit `1c17cd1e77a5b83fc57a0ed86e9ace595f58d31e`.
- No D1 migration was needed; the deployment's migration check correctly skipped the migration apply step.

## Live health verification

Fetched production endpoints on 2026-11-18:
- `GET /health` returned `ok: true` and `database: reachable`.
- Configured search sources: Tavily, Exa, TinyFish and GitHub public search.
- Brave remains optional and is not configured.
- OpenRouter legacy key route is present with six configured model IDs.
- AI Router reports `aiRouter: true`, **4 provider-key routes** and **9 model routes**.
- Telegram archive is enabled.

The four configured AI routes correspond to the additional provider configuration plus the retained OpenRouter legacy fallback. Health verifies that routes and model entries were loaded; it does not prove that each upstream API key, model entitlement, quota or live inference is working. No billable live inference probe was run during deployment.

The browser root returns the new Nolane Search HTML page, identifies itself as `noindex,nofollow`, and prompts anonymous visitors to authenticate through the Telegram `/web` command.

## Browser portal and access controls

- `/web` is available only to an allowlisted Telegram user in a private bot chat.
- Login ticket: 256-bit random token, SHA-256 hash stored in D1, five-minute expiry and one-time atomic consumption.
- Browser session: random token whose SHA-256 hash is stored in D1; seven-day expiry; Secure, HttpOnly and SameSite=Strict cookie.
- `/api/search`, `/api/ask`, `/api/chat`, `/api/crawl`, `/api/crawls` and `/api/feedback` require an active session whose Telegram user remains on the allowlist.
- The private single-owner service has no application-level per-minute request caps. Provider billing/quotas and Cloudflare platform capacity remain external constraints.
- POST requests are same-origin checked; JSON bodies are capped at 30 KB.
- Logout revokes the server-side session. Scheduled cleanup removes expired tickets and sessions.
- Chat history and recent searches are bounded in browser local storage; conversation transcripts are not persisted as server-side chat records.

The web interface includes Web, News, Research, Technology, GitHub, Wikipedia and private-site search categories, result cards with helpful/not-helpful controls, AI Overview with linked sources, multi-turn Nolane Chat, Personal Web Index, responsive layout, recent searches and a light/dark theme.

## Telegram interactive workspace

- `/start`, `/menu` and `/home` send the inline dashboard for the allowlisted owner in the private chat.
- The dashboard provides one-tap Web, AI Chat, AI with sources, Deep Research, Technology, News, GitHub, Wikipedia and personal-site modes, plus status/help and a link to the existing browser workspace.
- Selecting a mode edits the dashboard message to show an input prompt and stores a per-user/per-chat pending mode in D1 `search_cache` for 10 minutes.
- The next plain-text message atomically consumes that pending mode once. Without a pending mode, plain text retains the old default Web Search behavior. Slash commands cancel pending mode; `/cancel` clears it and returns to the dashboard.
- Search results keep existing five-item pagination and now include inline follow-ups for source-grounded AI (`/ask`) and Deep Search (`/deep`) using the original query from the owner's 15-minute search session.
- UI and follow-up callbacks validate the allowlisted user and private chat. Dashboard navigation edits the same message to reduce chat clutter.
- This release reuses the existing D1 cache; no schema migration or new API secret was introduced.
- CI verifies formatting, callback construction and Worker build. A real Telegram tap-through still requires the owner's account.

## Telegram callback delivery repair

- Root cause of the stuck inline buttons: the previous webhook registration explicitly allowed only `message` updates. Inline keyboard taps arrive as `callback_query`, which Telegram therefore did not forward to the Worker.
- `scripts/set-webhook.mjs` now registers both `message` and `callback_query`, then calls Telegram `getWebhookInfo` and fails unless the expected webhook URL and callback subscription are present.
- The Worker acknowledges an allowlisted callback with `answerCallbackQuery` before D1 deduplication or callback work, so Telegram's loading indicator is not held open by slow storage.
- Callback handlers no longer issue late/double acknowledgements. If a callback is acknowledged but processing fails, the Worker sends an actionable chat message.
- Automated regression test verifies acknowledgement occurs before the first D1 operation; a standalone Node check verifies the webhook script subscribes to and verifies callback updates.
- Production deploy 2026-11-18 verified the configured webhook through Telegram `getWebhookInfo`; a real owner tap-through is still the final UI end-to-end check.

## Search and retrieval behavior

- Search remains a federated metasearch engine backed by external provider APIs, not an independent crawler/index of the entire Internet.
- General web search queries Tavily first. If Tavily fails, returns fewer than six links, or the result set is lexically weak for the user's query, independent Exa, TinyFish, Brave and Wikipedia sources are queried as available.
- Technology search uses Tavily, Exa, TinyFish and GitHub; research uses Tavily, Exa and TinyFish research discovery; news uses Tavily, Brave, TinyFish and Exa as available.
- Ranking now uses IDF-weighted query coverage across title/snippet/URL, a weak provider-score prior, snippet quality, phrase matching, a small .gov/.edu source-type prior, freshness weighted by query intent, URL deduplication and domain diversity. It is a transparent heuristic, not a learned Google-scale ranking system.
- Candidate limit is 20. Telegram continues to display five results per page, with pagination sessions bound to owner user ID and chat ID and a 15-minute TTL.
- Relative publication ages are normalized to ISO timestamps when their format is recognized.
- Supported query operators: `site:`, `filetype:`, `intitle:`, `inurl:`, negative terms such as `-deprecated`, `after:YYYY-MM-DD` and `before:YYYY-MM-DD`. Operators are also enforced locally, even when an external provider does not implement them.
- Deep Search uses AI to propose complementary query angles when AI routes are configured, falls back to deterministic queries if planning fails, gathers results across configured providers, fetches/enriches up to seven selected pages with TinyFish and re-ranks the extracted evidence before synthesis.
- Search cache TTLs are mode-sensitive: news is short-lived, research is cached longer than general web search.

## Owner-controlled site indexing

- Telegram: `/crawl https://example.com [1-20]` enqueues a bounded crawl (default 10 pages); `/crawls` lists the current user's recent crawl jobs.
- Browser: Personal Web Index panel accepts a public HTTPS seed URL and a 5/10/20 page cap; status is refreshed from authenticated `/api/crawls`.
- Crawl jobs use the existing Queue and D1 search_cache `site-crawl:` prefix; there is no new D1 schema or additional API secret.
- The crawler is same-origin only, validates redirects, checks robots.txt, follows same-origin sitemap locations declared by robots.txt (including bounded nested sitemap indexes) plus `/sitemap.xml`, follows bounded same-origin HTML links, extracts article/main text where available and stores compact title/text in existing D1 indexed_pages and FTS5.
- Local retrieval combines FTS5 OR-term recall with title-weighted BM25 and the shared heuristic reranker; it does not require a vector database or embedding API.
- Personal Web Index results are also federated into ordinary Web, Technology and Research search (and therefore into AI Overview and Telegram `/ask` evidence). Dedicated GitHub and Wikipedia modes remain isolated from private-index content.
- Hard limits: 20 pages per job, 350 KB maximum response read per page and 10-second page fetch timeout. It skips binary assets and URL paths with query strings.
- It does not render JavaScript-heavy websites, bypass login, defeat anti-bot controls or crawl external domains. Use it only for sites whose robots policy permits it.

## Search relevance feedback

- Search results have optional helpful/not-helpful controls. Feedback is verified against the caller's authenticated search event and a hash of the result URL.
- Search events store hashes of query+mode and result URLs; raw query strings are not written to feedback metadata.
- Aggregate votes are query/mode-specific, smoothed for small sample sizes and capped to a +/-0.10 ranking score adjustment. Individual votes expire after 30 days and aggregates after 180 days.
- Feedback is a small owner preference signal, not a trained relevance model and not a measure of factual accuracy.

## Cloudflare resources

Account ID: `1172c01120a2470aa12f81e5b4778556`

| Resource | Name | ID / details | State |
|---|---|---|---|
| Worker | `nolane-search` | https://nolane-search.nolane-file.workers.dev | Deployed |
| D1 | `nolane-search-db` | `4f6a8cbd-cc8c-42b9-be6a-ed45c709d3db` | APAC; reachable |
| Main Queue | `nolane-search-jobs` | `8a09dc04a6824faaa90f379f45f75ac0` | Producer and consumer attached |
| Dead-letter Queue | `nolane-search-dlq` | `e44fe78242614ed1b448dbea7dbe94e0` | Consumer attached |
| Cron | `*/30 * * * *` | Every 30 minutes | Active |
| R2 / KV | — | — | Not used |

### D1 schema

The live D1 `schema_migrations` table contains:
- `0001_core.sql`
- `0002_deep_search_jobs.sql`
- `0003_web_portal.sql`
- `0004_remove_request_rate_limits.sql`

PR #3 and PR #4 did not introduce new D1 migrations; both reuse the existing indexed_pages/FTS5 schema, search_cache and Queue.

`0003_web_portal.sql` originally created `web_login_tickets`, `web_sessions` and `web_rate_limits`. PR #12 applied `0004_remove_request_rate_limits.sql`, removed `idx_web_rate_limits_expiry` and `web_rate_limits`, and recorded the migration. A live `sqlite_master` query returned no remaining objects with either obsolete name.

### D1 permission handling

The first automatic deployment attempt found that `CLOUDFLARE_API_TOKEN` can deploy Workers but is not authorized for D1 Query API calls (HTTP 403). The migration was then successfully applied and verified directly against the connected Cloudflare D1 database. A subsequent Worker deployment succeeded with the migration step skipped because the migration had already been applied.

The deploy workflow now separates permissions:
- `CLOUDFLARE_API_TOKEN`: Worker deployment and Queue configuration.
- `CLOUDFLARE_D1_API_TOKEN`: optional separate token with Account → D1 → Edit, required only when a future changed migration needs to run.

Create the second secret before the next commit that introduces a new file under `database/migrations/`. Ordinary code deployments do not need the D1 token.

## Remaining owner-level end-to-end checks

These need a real interaction from the owner's Telegram account; CI and the public health endpoint cannot complete them:
1. Send `/start` or `/menu` in the private Telegram chat and tap Web Search, AI Chat, or AI with sources. The button should respond immediately and edit the dashboard prompt; it must no longer show an endless loading spinner.

1. Send `/start` or `/menu` in the private bot chat; try each dashboard mode, send one query, test `/cancel`, and confirm that the next unselected plain-text message falls back to Web Search.
2. From a search result, use the AI-with-sources and Deep Search buttons; confirm only the matching original query is used and that the job appears in `/jobs`.

1. Open the private Telegram chat and send `/web`. Open the returned one-time link and confirm browser login works, then test logout and a fresh login link.
2. Try `/crawl https://your-own-public-site.example 10` on a website you control, then use `/crawls` and search its contents with `/local` or Website của tôi. Confirm only permitted pages are indexed.
3. Use Personal Web Index in the browser to enqueue a small crawl and refresh its status.
4. Vote helpful/not-helpful on a few search results, then repeat the exact same query to observe the small ranking nudge.
5. Run a browser search in Web, News, Research and GitHub categories. Confirm results open and the result count / timing are sensible.
6. Use AI Overview on a current topic and check that inline source numbers correspond to the linked sources.
7. Send a few chat messages to verify conversation continuity and verify that chat does not claim it performed live web search.
8. Run `/ai_status`, then one low-cost `/ai fast ...` request to verify live API-key acceptance. Test failover only if needed; it can spend provider quota.
9. Try a 20-result Telegram search pagination case, `/deep`, `/read`, `/watch` and archive delivery.
No API key, bot token, webhook secret or session token should be pasted into chat, committed to the repository, or included in screenshots/logs.


## Personal Memory and efficiency controls — deployed 2026-11-18

PR #7 added the bounded Personal Memory and AI efficiency improvements; PR #8 completed Telegram slash-command registration. Both are merged into `main` and deployed in Worker version `6eaac094-1dbe-494d-9393-ef0a66e94ddb`.

- Personal Memory reuses D1 `search_cache`; no new table, migration, Cloudflare service or secret is required. Each Telegram user can store at most 50 explicitly saved entries, with a five-year expiry. Categories are profile, preference, project and note.
- Telegram commands `/remember`, `/memories` and `/forget` are registered in the bot command menu. Memory is opt-in: the assistant does not automatically extract private conversation content.
- Telegram `/ai` and browser `/api/chat` retrieve at most three relevant saved memories as optional context.
- Browser chat history is bounded to at most eight valid turns and 8,000 aggregate characters before model submission. This is a character-based context budget, not an exact tokenizer count.
- AI Overview and Telegram `/ask` share a short D1 synthesis cache: two minutes for news/current queries, five minutes for research and ten minutes for other modes.
- AI Router defaults to three provider/model attempts per completion and clamps configured attempts to six. Recently failing routes receive a short per-isolate cooldown; it is best-effort and resets when an isolate is replaced.
- Web POST JSON request bodies are read as a stream and capped at 30 KB; oversized bodies are cancelled and rejected.
- Browser AI Overview and chat surface cache, latency, input/output token and estimated-cost metadata when the provider returns those usage fields.
- Final main CI passed type-check, all 72 unit tests, webhook checks and Worker build. The export smoke test and production deployment succeeded.
- Post-deploy `GET /health` returned `ok: true`, `database: reachable`, four AI provider-key routes and nine model routes. Brave is optional and is not configured.
- Deployment log confirms Telegram webhook subscriptions for `message` and `callback_query`, and successful registration of the bot command list.

Automated tests, command registration and live health checks are verified. A real user-level Telegram interaction with `/remember`, `/memories`, `/forget` and a personalized `/ai` prompt remains an owner-side end-to-end check.


## Provider and website-fetch hardening — deployed 2026-11-18

PR #9 is merged into `main` and deployed in Worker version `a2c2372a-6f95-43f6-9839-9bbf5f7acb0e`.

- Provider and Telegram Bot API JSON responses are consumed through a streaming reader with a 1 MB decoded-body cap. Declared oversized responses are rejected early; streaming bodies are cancelled once the cap is exceeded. Malformed and empty JSON responses become controlled failures.
- Website Watch redirects are constrained to the original public HTTPS origin. A monitored URL cannot redirect this Worker to another host. Redirect response bodies are cancelled before following a permitted same-origin redirect.
- The site crawler retains same-origin redirect enforcement and now cancels redirect bodies before following.
- TinyFish Fetch results are associated only with safe public URLs that were included in the request. Unsafe or unrelated result URLs are ignored; unsafe final URLs are not used as lookup keys.
- The `/status` cache count query had a duplicate exclusion removed.
- PR #9 CI passed type-check, all 78 tests, webhook checks and Worker build. Main CI, Worker export/smoke test and production deployment all passed.
- The deploy skipped D1 migration because no schema changed. Queue bindings, Cron and Telegram commands/webhook were retained and re-verified.
- Post-deploy `GET /health` returned `ok: true` and `database: reachable`; the configured provider inventory remains four AI key routes and nine model routes.

The watch redirect change is intentionally stricter: a site that redirects to another hostname will now be reported as a fetch failure. Update its watch target to the canonical destination if cross-host redirects are part of the site's normal behavior.


## Personal Web Index management — deployed 2026-11-18

PR #10 is merged into `main` and deployed in Worker version `74f6a6d4-c91b-4c68-b94d-b65fb152aeea`.

- The private Web Workspace Personal Web Index panel lists recently updated pages, supports filtering by title/URL/domain, and paginates through the saved page list.
- Each page can be removed individually. A domain removal deletes pages for the exact hostname, its `www` alias and subdomains.
- Browser management endpoints are private behind the existing one-time Telegram login / Web session. Destructive POST requests retain the same-origin guard.
- Telegram commands: `/indexed [filter]`, `/unindex https://example.com/page`, and `/unindex_domain example.com`. The commands are included in Telegram's registered slash-command menu and `/help`.
- A deletion removes the FTS5 row and `indexed_pages` source row in one D1 batch, and deactivates any watch whose normalized URL is among the removed pages. Crawl-job history and Telegram archive snapshots are retained.
- A crawl job already in flight is not cancelled; it can write a page after a removal completes. Refresh the index and remove again if that happens.
- No schema migration, new Cloudflare service, paid API or new secret was required. Deployment confirmed `D1 migration required: false`; Queue/Cron bindings were retained, Telegram webhook and command registration succeeded.
- PR CI and main CI passed type-check, all 84 tests, webhook checks and Worker build. Worker export/smoke and production deployment passed.
- Post-deploy `GET /health` returned `ok: true` and `database: reachable`; configured AI routes remain four provider-key routes and nine model routes.

An owner-side browser/Telegram interaction is still needed to verify the visible list and destructive controls against the owner's real stored pages. Automated authorization, pagination, validation and deletion-batch behavior are covered by tests.


## Request-cap removal and Personal Web Index federation — deployed 2026-11-18

PR #12 was merged at `fe988bdbeb4c5c7095c06b03c9f2b08485582d39`. The final Worker deployment was built from main commit `b12aa461af2bb8f366671edc07821ef5549ccf90` and is running Worker version `26f16ed2-8133-457b-a77c-59c93b269a47`.

- Per-minute application-level usage caps have been removed from Telegram commands and authenticated Web Workspace endpoints. The private single-owner bot and browser portal no longer reject `/ai`, `/ask`, `/deep`, `/crawl`, search, or feedback actions due to an app-level request counter.
- D1 migration `0004_remove_request_rate_limits.sql` was applied directly through the connected Cloudflare D1 session after the GitHub D1 migration token was found to be absent. The `web_rate_limits` table and `idx_web_rate_limits_expiry` index were dropped, and migration `0004` was inserted into `schema_migrations`; follow-up `sqlite_master` verification returned no obsolete objects.
- The subsequent GitHub deployment correctly detected `D1 migration required: false`, deployed the Worker, verified Telegram webhook subscriptions for `message` and `callback_query`, and registered the current bot command list.
- Provider-owned quotas/billing, Cloudflare platform limits and Queue capacity still apply. A single website crawl remains bounded to 20 pages per job and keeps the HTTPS/public-host, same-origin and robots.txt safety checks; those are execution/security bounds, not request throttles.
- Personal Web Index FTS5/BM25 results are federated into Web, Technology and Research search. Dedicated GitHub/Wikipedia modes remain isolated; Local remains a direct personal-index lookup. Shared search means AI Overview and Telegram `/ask` can now use indexed personal pages as evidence.
- PR CI and main CI passed type-check, all 87 tests across 14 files, webhook checks and Worker build. Worker export/smoke test and production deployment passed.
- Production `GET /health` returned `ok: true` and `database: reachable`; provider inventory remains Tavily, Exa, TinyFish, GitHub and OpenRouter, with four AI key routes and nine model routes.

The automated behaviors and production release are verified. Real Telegram interaction and browser login still require an owner-side end-to-end check.


## Nolane Tools · implementation under PR #13

The first Tools release is being added in PR #13.

- A registry of 17 implemented tools spans image/OCR, PDF/Office, audio/video, data and utility categories.
- Telegram file uploads automatically select a compatible tool (photos default to Vietnamese/English OCR); `/tool TOOL_ID` can override the next upload.
- The private Web Workspace includes a Tools catalog and personal job history. File uploads are initially handled from the Telegram chat.
- GitHub Actions runs the actual Python processing on ephemeral hosted Ubuntu runners. Worker D1 stores metadata/status in the existing `search_cache`; the runner downloads inputs directly from Telegram and sends output files back, without committing files or using R2.
- A fine-grained `GITHUB_ACTIONS_TOKEN` with repository Actions: Read and write is required before live dispatch works. It is documented in `docs/SECRETS.md`; it must be saved as a GitHub Actions secret, not pasted into chat.
- OCR installs English and Vietnamese Tesseract data; audio transcription uses CPU Whisper; document extraction includes OCR fallback for scanned PDFs.
- CI includes registry/dispatch unit tests plus Python syntax checking. Actual hosted-runner execution requires the token to be configured and a real file to be sent from Telegram; that end-to-end run is not claimed until verified.


## Nolane Tools expansion · PR #14

The registry expands from 17 to 23 implemented tools.

- Added text cleanup for TXT/Markdown/log files, SRT/VTT subtitle-to-transcript extraction and HTML-to-readable-text extraction.
- Added audio loudness normalization to podcast-style -16 LUFS, video-to-MP3 audio extraction and a bounded six-second video-to-GIF preview.
- Added MIME/extension inference and dispatch metadata for the new tools. FFmpeg is installed only for the relevant audio/video jobs.
- CI now runs Python unit tests against the runner's text, subtitle and HTML transforms plus mocked FFmpeg command construction, in addition to Python compilation and the TypeScript suite.


## Telegram Archive Index — deployed 2026-11-21

- PR #51 adds the D1 metadata index and owner-scoped `/archive [query]` / `/archive_restore ID` commands; PR #52 adds filename, file size and SHA-256 prefix to each list item.
- Latest source: `6ab8b45e6c85e9b861bbe481eae439f1874fe381`.
- Production Worker version: `c8a21659-d0f0-47eb-aa9e-941e4b94a748`, 100% traffic.
- CI run #249 (`44888520208`) passed; deployment run #105 (`44888609517`) succeeded, including Worker secret upload and Telegram webhook/command registration.
- D1 readback confirms `0005_archive_snapshots.sql` and `archive_snapshots` are present alongside migrations 0001–0004.
- Telegram channel stores snapshot documents; D1 stores owner-scoped message/file references, URL/title/time/hash metadata only. D1 does not store the snapshot body.
- Real private Telegram watch → capture → archive search → restore testing remains owner-level E2E and has not been claimed as verified.
- Configure `CLOUDFLARE_D1_API_TOKEN` with Account > D1 > Edit in GitHub Actions before future commits that add migration files. The first rollout required a direct D1 migration because this secret was absent; that migration was manually applied and verified before the successful source-only deployment.

## Telegram archive pagination — deployed 2026-11-21

- PR #53 merged: https://github.com/Nolane-x/Nolane-search/pull/53
- Main commit: `69c131775570a2bdb93653d4576c1ef3801ae6ac`.
- `/archive` and `/archive [query]` now show five snapshots per page; `/archive_page PAGE [query]` navigates to previous/next pages while preserving the query. The command is registered in Telegram.
- Page input is bounded to 1–1001 and 120 query characters, matching the existing 5,000-row maximum offset. Query strings are escaped before being embedded in Telegram HTML.
- PR CI run #252 and main CI run #253 passed; both include type-check, unit tests, deployment-script checks, 96 Python tool-runner tests and Worker build.
- Deployment run #106 and build-export run #99 succeeded. The D1 migration step was skipped because no schema change was required; Worker secrets and Telegram webhook/command registration succeeded.
- Current production Worker version: `8c8cbfb8-15dc-4ec8-98ee-adabb0c0133c`, receiving 100% of traffic (Cloudflare deployment `643b4ef0-c98a-4eab-9649-47af2ea9bbb1`, created 2026-11-21T09:25:06Z).

## Telegram archive index failure recovery — deployed 2026-11-21

- PR #54 merged: https://github.com/Nolane-x/Nolane-search/pull/54
- Main commit: `5f0744a6714c1a343dc4541b1b648e2f903dae25`.
- If Telegram accepts a snapshot document but the following D1 metadata insert fails, the Worker now attempts to copy that exact Telegram message into the owner's private chat and sends a clear warning that the entry is not searchable in `/archive` yet.
- If the direct copy also fails, the owner is notified with the filename and source Telegram message ID; errors are contained so a metadata outage does not turn into a failed watch check.
- PR CI #254 and main CI #255 passed, including the new D1 failure/recovery integration test, type-check, all unit tests, deployment-script checks, 96 Python runner tests and Worker build.
- Deployment #107 and export/smoke-test #100 succeeded; no D1 schema migration was required.
- Current production Worker version: `508f7849-fefc-4592-b93a-f871ec1ed27a`, 100% traffic (deployment `05ab3e95-3f5e-43b1-b16d-af73ee6184a8`, created 2026-11-21T09:29:55Z).

## Watch archive retry reliability — deployed 2026-11-21

- PR #55 merged: https://github.com/Nolane-x/Nolane-search/pull/55
- Main commit: `9e36d4bbb99fab28f7532d97cc8f5e0f9e556639`.
- Fixed a snapshot-loss race: a watch no longer advances `content_hash`, ETag or Last-Modified until its configured Telegram document upload and D1 archive index both succeed.
- Failed initial/change captures keep the previous hash, clear HTTP validators and set `last_status = -4`. The next Cron check makes an unconditional full fetch and retries archive; pending state survives temporary HTTP/robots errors. No schema migration was needed.
- `/watches` exposes `archive pending · retry scheduled`; the owner receives one initial warning, and the normal change alert is sent only after a successful archive index.
- Regression tests cover Telegram upload failure, hash preservation, ETag clearing, and successful retry without conditional request headers.
- PR CI #258 and main CI #259 passed; all unit tests (207), typecheck, deployment script checks, 96 Python runner tests and Worker build succeeded.
- Deploy #108 and build/export smoke test #101 succeeded, including Worker/runtime-secret upload and Telegram webhook/command registration.
- Current production Worker version: `cb1e062b-386e-4ed5-aae8-f8a8d5c1959c`, receiving 100% traffic (deployment `012484ba-8d33-4772-ad6e-3d03f075062f`, created 2026-11-21T10:07:13Z).


## Watch alert isolation — deployed 2026-11-21

- PR #56 merged: https://github.com/Nolane-x/Nolane-search/pull/56
- Main commit: `f08257952cdebd7435daf59aec08c27254f9f9e0`.
- A failed owner-facing "Website changed" Telegram notification is now isolated from archive state. Once the Telegram document and D1 snapshot index succeed, notification failure is logged locally and cannot re-arm `last_status = -4` or cause the next Cron run to capture the same page again.
- The change alert is still attempted in the Telegram archive channel; archive-message delivery retains its own contained error handling.
- Regression coverage simulates successful document upload + D1 indexing followed by private-chat notification failure. It verifies one document upload, committed watch hash and no retry-state rollback.
- PR CI #260 passed: 24 test files / 206 unit tests, type-check, deployment-script checks, 96 Python tool-runner tests and Worker build. Main CI #261 passed the same checks.
- Deploy #109 and Export/Smoke #102 succeeded. D1 migration was skipped because no schema changed; Worker upload and Telegram webhook/command registration succeeded.
- Current production Worker version: `d0e64bf3-7b72-44bf-98fa-1fb35b520a33`, receiving 100% traffic (deployment `b6fac148-86ca-43aa-8008-060e240964c1`, created 2026-11-21T12:01:29Z).
- Owner-side Telegram E2E validation remains separate and outstanding; CI and deployment do not prove real private-chat archive capture/search/restore behavior.


## Watch archive-state messaging — deployed 2026-11-21

- PR #57 merged: https://github.com/Nolane-x/Nolane-search/pull/57
- Main commit: `019abadd9a36cf8599e9e0b9bdc6ebab81876fe1`.
- Change alerts now state the actual archive outcome. When `TELEGRAM_ARCHIVE_CHAT_ID` is unset, Watch still reports changed content but explicitly says that no snapshot was saved; it no longer claims an archive upload occurred.
- Added regression coverage: archive-disabled change alert sends one notification, never calls `sendDocument`, updates the latest page hash and does not claim archive success.
- PR CI #262 passed: 24 test files / 207 unit tests, TypeScript typecheck, deployment-script checks, 96 Python runner tests and Worker build.
- Main CI #263 passed; Deploy #110 and Export/Smoke #103 also succeeded. The Worker health smoke test passed, and Telegram webhook/command registration succeeded. No D1 schema migration was required.
- Current production Worker version: `09d9e4ab-dc2b-4084-ac29-e81e61f27449`, receiving 100% traffic (deployment `9dfd8640-15f9-4861-8a28-9b5f60e945ae`, created 2026-11-21T12:07:22Z).
- Owner-side Telegram E2E remains outstanding and must be tested separately from CI.


## Watch title-only change detection — deployed 2026-11-21

- PR #58 merged: https://github.com/Nolane-x/Nolane-search/pull/58
- Main commit: `b4558ecf74c95affd7d7e30c3feb48b0c190d5d3`.
- Watch change detection now compares both the existing body hash and the prior indexed page title. A title-only edit is therefore captured and notified even when the extracted body text is unchanged.
- Existing watch `content_hash` format remains unchanged (SHA-256 of body text); this avoids a schema migration and prevents every existing watch from generating a one-time false change.
- Regression coverage simulates an unchanged body with a different title and verifies a `change` archive record plus owner alert.
- PR CI #264 and main CI #265 passed: 24 test files / 208 unit tests, TypeScript typecheck, deployment-script checks, 96 Python runner tests and Worker build.
- Deploy #111 and Export/Smoke #104 succeeded. Worker health smoke test passed; Telegram webhook/command registration succeeded. D1 migration was skipped because no schema changed.
- Current production Worker version: `32899f51-e00a-45e5-84c8-cba7e062035a`, receiving 100% traffic (deployment `0546742a-f0d3-4747-80ac-09447f48a776`, created 2026-11-21T12:11:17Z).
- Owner-side Telegram E2E remains outstanding and separate from CI validation.


## Wave 10 — Repository Engineering Intelligence — deployed 2026-11-21

- PR #59 merged: https://github.com/Nolane-x/Nolane-search/pull/59
- Main commit: `70ac5ed5a646beeeda6a6842c299cc06c9153fc7`.
- Tool catalog expanded from 283 to **291 executable tools**. Wave 10 adds eight static repository analyzers:
  - `repo-test-map`: filename/path-based source-to-test candidates; not line coverage.
  - `repo-test-quality`: test declarations, assertion signals, skip/focus markers, broad exception and TODO signals.
  - `repo-complexity-report`: Python AST decision counts and explicitly heuristic JS/TS branch signals.
  - `repo-api-surface`: route/handler candidates for Python, JS/TS, Java and Go.
  - `repo-docs-audit`: required documentation and relative Markdown links.
  - `repo-migration-audit`: destructive DDL/DML review signals.
  - `repo-runtime-risk`: risky runtime/API patterns, without echoing matched source values.
  - `repo-i18n-audit`: JSON locale key parity.
- All eight tools are in the TypeScript catalog, Python allowlist/handler map, matching pipeline transition graphs and user documentation. The `repo-intelligence` composite now bundles 18 report groups.
- GitHub public snapshot jobs are allowed only for tools in the `repository` category, one processor per job; Python runner also enforces an explicit allowlist. All processors inspect ZIP data only: they do not execute repository code/workflows/tests/migrations/build scripts, install dependencies or access databases.
- PR CI #269 and main CI #270 passed: 24 test files / 209 unit tests, TypeScript typecheck, deployment-script checks, 97 Python runner tests and Worker build.
- Deploy #112 and Export/Smoke #105 succeeded. Worker health smoke test passed; Telegram webhook and command registration succeeded. No D1 migration was required.
- Current production Worker version: `8835dad6-86ba-485f-a4b5-86b995c50631`, receiving 100% traffic (deployment `9ebe527f-a873-4f45-9347-14ad6658c5ca`, created 2026-11-21T13:14:43Z).
- The repository analyzers are heuristic static reviews. Test mapping is not coverage; test quality is not test execution; API detection is not a complete OpenAPI spec; migration/runtime signals do not prove exploitability or impact; i18n compares keys but not translation quality.


## Direct GitHub repository tool command — deployed 2026-11-21

- PR #60 merged: https://github.com/Nolane-x/Nolane-search/pull/60
- Main commit: `c6bdde7a39382f832ff129ff6199f65d3c1fd80a`.
- Added `/repo_tool TOOL_ID https://github.com/owner/repo` (also accepts safe `/tree/branch` refs) to run one ready tool from the Repository category directly on a public GitHub snapshot.
- The command requires an authorized private Telegram chat, validates the tool ID/category and reuses the existing strict GitHub URL parser and repository snapshot job flow. `/repo` composite intelligence and `/repo_compare` continue to work unchanged.
- Added parser tests for an existing repo tool, Wave 10 tools, slash-containing branch refs, non-repository IDs, unknown IDs, malformed/non-GitHub URLs, credentials, path traversal, extra arguments and oversized input.
- PR CI #271 and main CI #272 passed: 25 test files / 210 unit tests, TypeScript, deployment-script checks, 97 Python runner tests and Worker build.
- Deploy #113 and Export/Smoke #106 succeeded. Worker health smoke passed and Telegram webhook/commands were registered. No D1 migration was required.
- Current production Worker version: `cc4a124a-aa79-4631-bd0e-187bd0bac8e5`, receiving 100% traffic (deployment `eb5d8517-0401-48e6-a309-65303d14dbdc`, created 2026-11-21T13:21:38Z).


## Wave 11 — Repository Architecture & Delivery Checks — deployed 2026-11-21

- PR #61 merged: https://github.com/Nolane-x/Nolane-search/pull/61
- Main commit: `be239c42c3464faceb84194aea8af4f88b0b4046`.
- Tool catalog expanded from 291 to **297 executable tools** with six new Repository analyzers:
  - `repo-env-contract`: maps environment-variable names referenced in source against tracked examples, container ARG/ENV and GitHub Actions names; never prints values.
  - `repo-architecture-cycles`: detects cyclic strongly connected components in the extracted local-import graph.
  - `repo-change-impact`: uses GitHub Compare changed-file metadata and reverse local-import edges to identify possible dependent modules; full results require `/repo_compare`.
  - `repo-api-spec-audit`: checks OpenAPI/Swagger JSON/YAML for duplicate operation IDs, missing responses/path parameters and unresolved local refs; does not fetch remote refs.
  - `repo-container-audit`: reviews Dockerfile/Compose signals including base-image tags, USER/HEALTHCHECK, credential ARG/ENV, privileged mode, host networking and Docker socket.
  - `repo-ci-reliability`: checks GitHub Actions timeout/concurrency, `continue-on-error`, failure masking and moving action refs.
- All six tools are registered in TypeScript catalog, Python runner handlers/allowlist and matching pipeline transition maps. The `repo-intelligence` composite now packages 24 report groups. `docs/NOLANE-TOOLS.md` records the 297-tool count and one Wave 11 guide section.
- PR CI #276 and main CI #278 passed: 25 test files / 222 unit tests, TypeScript typecheck, deployment-script checks, 98 Python runner tests and Worker build.
- Deploy #114 and Export/Smoke #107 succeeded. Worker health smoke passed; Telegram webhook and command registration succeeded. No D1 migration was required.
- Current production Worker version: `07f9fee8-37be-4630-ae76-8febfebfa614`, receiving 100% traffic (deployment `a4cd587b-e343-4c45-af19-15fde499930a`, created 2026-11-21T14:27:41Z).
- All Wave 11 analyzers inspect repository ZIP and bounded GitHub Compare metadata as data. They do not run repository code, workflows, tests, migrations, Docker/Compose commands, package installs or database connections. Environment values are not included in reports; the other checks are static heuristics with stated scope limitations.


## Wave 12 — Static HTML quality auditors — deployed 2026-11-21

- PR #62 merged: https://github.com/Nolane-x/Nolane-search/pull/62
- Main commit: `a0919d77a76e3077aad485b4f621f4206ff6e24d`.
- The catalog expanded from 297 to **302 executable tools** with five HTML processors:
  - `html-seo-audit`: static title/meta description, canonical, robots, Open Graph, language, H1 and image-alt checks.
  - `html-accessibility-audit`: static accessible-name, label, alt, main-landmark, language and heading-level checks.
  - `html-link-audit`: missing/empty href, unsafe schemes, unresolved local fragments and target-blank rel checks.
  - `html-form-audit`: form method/action, control name/label, password-in-GET and autocomplete checks.
  - `html-image-audit`: image alt, dimensions and loading hints.
- Main CI #281 passed: 25 test files / 223 Vitest tests, TypeScript type-check, deployment-script checks, 99 Python runner tests and Worker build: https://github.com/Nolane-x/Nolane-search/actions/runs/44919157392
- PR CI #280 also passed on the final PR head: https://github.com/Nolane-x/Nolane-search/actions/runs/44919056298
- Cloudflare build/export and production Worker smoke test #108 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44919157432
- Production deployment #115 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44919157401. It validated deployment secrets, uploaded the Worker/runtime secrets and registered Telegram webhook updates and command menu. D1 migration was skipped because Wave 12 adds no database schema.
- Cloudflare deployment API confirms Worker version 69 `741a6df7-916b-4f19-a75f-f8ea95863960` receives 100% traffic.
- Fresh production `GET /health` returned `ok: true` and `database: reachable`; it reported four AI provider-key routes, nine model routes and archive enabled. A health/configuration response confirms route loading, not the current quota or live inference health of every upstream key.
- All five HTML processors are bounded static heuristics: they do not fetch remote URLs/images, execute scripts, submit forms or run browser-based checks. SEO/accessibility findings are not Google ranking predictions or WCAG certification.
- Still pending owner-level verification: upload representative HTML files through the real Telegram bot, inspect delivered TXT reports, and test a retry. CI, webhook registration and health checks do not prove this complete user interaction.


## Wave 13 — Practical productivity processors — deployed 2026-11-22

- PR #63 merged: https://github.com/Nolane-x/Nolane-search/pull/63
- Main commit: `1aba865d8265485dc1ccded67d379598092305cc`.
- Catalog expanded from 302 to **308 executable tools** with six new processors:
  - `xlsx-formula-report`: inventories formulas per sheet, volatile functions, external-workbook references and cached formula errors/missing results; never recalculates formulas or prints cell data.
  - `xlsx-to-markdown`: exports bounded XLSX sheets as Markdown tables using cached values only.
  - `subtitle-audit`: detects malformed timestamps, non-positive durations, out-of-order/overlapping intervals, duplicate captions and long lines/cues.
  - `image-favicon`: creates ICO favicons at 16/32/48/64/128/256 px, preserves transparency when possible and does not retain EXIF.
  - `pdf-page-audit`: reports per-page text/image/vector counts, dimensions and rotation, with heuristic hints for blank or image-only pages; performs no OCR.
  - `markdown-toc`: adds a generated Table of Contents to a copy of a Markdown file, ignoring fenced code and disambiguating duplicate heading slugs.
- Main CI #283 passed: 25 test files / 224 Vitest tests, 103 Python runner tests, TypeScript type-check, deployment-script checks and Cloudflare Worker build: https://github.com/Nolane-x/Nolane-search/actions/runs/44965103274
- PR CI #282 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44965015650
- Cloudflare build/export and Worker smoke test #109 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44965103506
- Production deployment #116 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44965103181. It validated deployment secrets, uploaded the Worker/runtime secrets and registered Telegram webhook updates/commands. D1 migration was skipped because Wave 13 does not change the schema.
- Cloudflare API confirms Worker version 70 `59beaf42-8526-49d5-821f-e13b783d9d50` receives 100% traffic through deployment `c39e7ba5-e0af-4d66-bb31-034541c8b256`.
- Fresh production `GET /health` returned `ok: true` and `database: reachable`; it reports four AI provider-key routes, nine model routes and archive enabled. This confirms route configuration is loaded, not that every upstream key has quota or can complete inference.
- All six tools are bounded file processors; no D1 migration, new external service or new secret was added. XLSX reads cached formula values without recalculation; PDF scan/blank labels and subtitle line/duration flags are heuristics.
- Still pending owner-level end-to-end verification: upload representative XLSX, SRT/VTT, image, PDF and Markdown files through the live Telegram bot, inspect delivered artifacts and exercise retry. CI and webhook registration do not prove this full user interaction.

## Wave 14 — Document quality, privacy and archive security — deployed 2026-11-22

- PR #64 merged: https://github.com/Nolane-x/Nolane-search/pull/64
- Production source commit: `ccd74ad52825c498413622e571cfb2970da4b995`.
- Catalog expanded from 308 to **312 production tools** with four additional bounded auditors:
  - `docx-audit`: checks heading hierarchy, missing Heading 1, empty heading paragraphs/table first rows, image alternative text, unsafe external hyperlink schemes and tracked-change/comment markers. Reports structural counters only; document paragraph/table content is not copied.
  - `pptx-audit`: reports per-slide word/text/image counts, missing titles, blank slides, repeated/long titles, dense slides, explicitly declared font runs below 12 pt and images missing alt text. Does not render slides or detect actual clipping/overlap.
  - `csv-privacy-audit`: detects email-like values, Luhn-valid card candidates, IPv4 addresses, phone-like values in phone-named columns and sensitive headers. Report shows column/type/count and a small set of row numbers; raw cell values are never included.
  - `archive-security-audit`: metadata-only ZIP/TAR preflight for absolute/traversal paths, duplicate/case-colliding paths, links/special entries, encrypted ZIP members, extreme compression ratios, large members, nested archives and executable/script extensions. It never extracts or executes archive content.
- PR CI #64 passed: type-check, Vitest, deployment-script checks, Python runner suite (104 tests) and Worker build: https://github.com/Nolane-x/Nolane-search/actions/runs/44966857743
- Main CI #286 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44966971539
- Cloudflare build/export and live Worker smoke test #110 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44966971507
- Production deployment #117 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44966971557. Deployment secret validation, Worker/runtime secret upload and Telegram webhook/command registration all succeeded. D1 migration was skipped because no schema changed.
- Cloudflare deployment API confirms Worker version 71 `8c86c559-30c2-4ba4-a7e4-5365751df737` receives 100% traffic through deployment `9194f2a0-9974-4961-8433-9109066cf4b1`.
- Fresh production `GET /health` returned `ok: true` and `database: reachable`; it reports four AI provider-key routes, nine model routes and archive enabled. This reports configuration/route availability, not successful inference or remaining quota for every upstream provider.
- Registry parity was checked directly: 312 unique TypeScript catalog IDs, all 312 in the Python RUNNERS allowlist and 312 Python handlers; the 752 TypeScript/Python pipeline transition edges matched exactly.
- No new secret, D1 migration or external service was introduced. DOCX/PPTX are structure heuristics, CSV privacy detection is pattern/header-based, and archive executable-extension findings are review signals rather than malware verdicts.
- Still pending owner-level end-to-end verification: upload representative DOCX, PPTX, CSV and ZIP files through the live Telegram bot, inspect delivered reports/artifacts and test retry. CI, webhook registration and health do not prove this entire Telegram interaction.

## Wave 15 — Spreadsheet and PDF privacy auditors — deployed 2026-11-22

- PR #65 merged: https://github.com/Nolane-x/Nolane-search/pull/65
- Production source commit: `f94cc153936de383e629ed92fcd0fab011883b41`.
- Catalog expanded from 312 to **314 production tools** with two privacy-focused auditors:
  - `xlsx-privacy-audit`: scans cached XLSX values for email-like values, Luhn-valid payment-card candidates, credential-like tokens, IPv4 addresses, phone-like values on phone-named columns and sensitive headers. Reports sheet/column/cell coordinates/type/count only; never copies raw cell values into the report.
  - `pdf-privacy-audit`: scans the PDF text layer for email-like values, Luhn-valid card candidates, labelled phone-like values, IPv4 addresses, identity-document-like patterns and credential-like tokens. Reports page/type/count only; no OCR, raw values or surrounding text.
- PR CI on final head passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44967612153
- Main CI #288 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44967710533 (105 Python runner tests, type-check, Vitest, deployment-script checks and Worker build).
- Cloudflare build/export and live Worker smoke test #112 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44967710414
- Production deployment #119 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44967710386. Deployment secrets were validated, runtime secrets uploaded, and Telegram webhook/commands registered. D1 migration was skipped because the wave has no schema change.
- Cloudflare deployment API confirms Worker version 72 `ec64a6ca-e7a8-402b-88c4-e06f0d50c294` receives 100% traffic through deployment `23d28228-ab44-41e7-a0ee-a9eeb5fb0641`.
- Fresh production `GET /health` returned `ok: true` and `database: reachable`; four AI provider-key routes and nine model routes are loaded. Route configuration does not prove each upstream key has live quota or can complete inference.
- Registry parity was checked: 314 unique TypeScript catalog IDs, 314 Python runner allowlist IDs, 314 Python handlers and 756 matching TypeScript/Python pipeline edges.
- No D1 migration, new secret or external service was added. XLSX inspects cached formula values only; PDF scans text layer only and does not OCR. Both audits use bounded heuristic detection and never include raw sensitive values.
- Still pending owner-level end-to-end verification: upload representative XLSX and PDF files through the actual Telegram bot, inspect the delivered reports and exercise retry. CI, webhook registration and health checks do not prove that entire Telegram user journey.

## Wave 16 — Office and PDF active-content security audits — deployed 2026-11-22

- PR #66 merged: https://github.com/Nolane-x/Nolane-search/pull/66
- Production source commit: `cae8ddd629f5bccc30199e7d036dd89377cf7b6f`.
- Catalog expanded from 314 to **316 production tools** with two static security auditors:
  - `office-active-content-audit`: scans supported OOXML Office packages for VBA project binaries/macro-enabled content types, ActiveX, OLE/embedded parts, customUI, external relationships/workbook links/connections, unsafe URI schemes, encrypted members and traversal-like paths. It reads ZIP metadata and bounded relationship/content-type XML only; no macro or embedded object is opened/executed.
  - `pdf-active-content-audit`: scans PDF indirect object dictionaries and link metadata for JavaScript/JS, OpenAction, Additional Actions, Launch, EmbeddedFiles/Filespec, RichMedia, AcroForm/XFA, SubmitForm/ImportData, remote GoTo and URI actions. It reports counts only and never runs actions or extracts attachments.
- PR CI passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44975448150 (107 Python runner tests, TypeScript type-check, Vitest, deployment-script checks and Worker build).
- Main CI #294 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44975539445 (107 Python runner tests; TypeScript/Vitest/type-check and Worker build all green).
- Cloudflare build/export and production Worker smoke test #112 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44975539435
- Production deployment #119 passed: https://github.com/Nolane-x/Nolane-search/actions/runs/44975539446. Required deployment secrets were validated, Worker/runtime secrets uploaded and Telegram webhook/command menu registered. D1 migration was skipped because no schema changed.
- Cloudflare API confirms Worker version 73 `03210f3c-6bd5-47a9-ab1d-deeac1fca8a1` receives 100% traffic through deployment `c39bb7f6-fb16-4749-ac9c-a540400483de`.
- Fresh production `GET /health` returned `ok: true` and `database: reachable`; four AI provider-key routes and nine model routes were reported. This verifies configuration/route loading, not active quota or inference success for each upstream provider.
- Registry parity was checked: 316 unique TypeScript catalog IDs, 316 Python runner allowlist IDs, 316 Python handlers and 760 matching TypeScript/Python transition edges.
- No new dependency, D1 migration, secret or external service was added. Office inspection reads ZIP metadata and selected bounded XML; PDF inspection reads object dictionaries only. Findings are static review signals, not a malware verdict or guarantee of safety.
- Still pending owner-level end-to-end verification: upload representative DOCX/XLSM/PPTX and PDF samples through the actual Telegram bot, inspect delivered reports and test retry. CI, webhook registration and health checks do not prove the full Telegram user journey.
