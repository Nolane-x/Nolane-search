# Wave 18 release handoff — Cross-domain everyday, data and media tools

Date: 2026-11-22
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-eighteen-har-openapi-security-auditors

## Scope

Adds ten focused processors to diversify beyond developer and security tools:

- har-privacy-audit: inspect HAR metadata and count sensitive header/cookie/query/form names and token-like body patterns. Does not print URLs, values or response/request body text.
- ics-calendar-audit: parse iCalendar events, duplicate/missing UIDs, start/end ranges, recurrence, timezone and alarms. Does not print event details or attendee addresses.
- vcard-privacy-audit: report contact-card completeness and duplicate normalized emails/phones without exposing values.
- gpx-track-report: calculate route distance, ascent/descent and duration while withholding route coordinates, place names and exact timestamps.
- geojson-audit: count geometry types and coordinate positions and flag invalid longitude/latitude pairs; coordinates and property values are withheld.
- qr-code-generate: generate PNG from a UTF-8 text file (maximum 4 KiB); never echo the payload in job summary.
- font-inspect: read TTF/OTF/WOFF family/version/glyph/cmap/variable axes and OS/2 embedding flags. This is not a legal license determination.
- subtitle-fix: sort SRT/VTT cues, renumber SRT, drop malformed/empty cues and correct non-positive cue durations. It is not a full subtitle specification validator.
- openapi-contract-audit: check OpenAPI 3.x/Swagger 2 structure, operation IDs, responses, path parameters, local refs and insecure server URLs. Does not fetch remote refs.
- color-convert: convert HEX/RGB values to HEX/RGB/HSL/CMYK across a text list.

## Bounds and dependencies

- HAR: 20 MiB input, 100,000 entries and up to 2 MiB of combined body text pattern scanning.
- iCalendar/vCard: 10 MiB input and maximum component nesting 40 through VObject.
- GPX/GeoJSON: 20 MiB input; reports omit coordinates and personal property values.
- QR: 4 KiB text payload.
- Font: 20 MiB font file.
- Subtitle: 10 MiB.
- OpenAPI: 10 MiB; YAML uses SafeLoader and remote refs are not fetched.
- Color: 2 MiB input.
- Conditional GitHub Actions runner packages: vobject (Apache-2.0), fonttools (MIT), qrcode/Pillow (BSD-3-Clause for qrcode); existing PyYAML dependency is reused.
- No D1 migration, secret, persistent service, live network query or repository-code execution is added.

## Acceptance gates

1. 328 unique TypeScript catalog IDs, Python RUNNERS entries and Python handler mappings; 328 matching registered processors.
2. New report-only tools are present in TEXT_OUTPUT_TOOLS; TypeScript and Python pipeline transitions match.
3. Python fixtures cover privacy redaction, malformed inputs, geometry range checks, subtitle repair, OpenAPI findings and generated QR artifact.
4. Type-check, Vitest, deployment-script checks, Python runner suite and Worker build pass.
5. Worker export/smoke and production deployment pass before reporting 328 production tools.
6. Live Telegram upload/report/retry for representative HAR, ICS, VCF, GPX, GeoJSON, TXT, font, SRT/VTT and OpenAPI files remains owner-level E2E.

Research notes and upstream repository links: docs/TOOL-RESEARCH-2026-11-22.md
## Production rollout — 2026-11-22

- PR #68 merged into `main`: https://github.com/Nolane-x/Nolane-search/pull/68
- Main commit: `374f4c011a59e50e30ac0ace5891d458b32407ff`.
- Main CI [44980373517](https://github.com/Nolane-x/Nolane-search/actions/runs/44980373517), Worker export and production health smoke [44980373519](https://github.com/Nolane-x/Nolane-search/actions/runs/44980373519), and production deployment [44980373529](https://github.com/Nolane-x/Nolane-search/actions/runs/44980373529) all passed.
- Main CI passed type-check, Vitest, deployment-script checks, 119 Python runner tests and Worker build.
- Deployment verified bundle, runtime-secret upload and Telegram webhook/command-menu registration. D1 migration was correctly skipped because no schema changed.
- Production catalog: 328 processors. Cloudflare Worker Version ID: `1271380c-e118-4731-ad33-5f38adcd20c8`.
- Still required: owner-level private Telegram E2E upload/report/retry across representative formats. CI/deployment do not verify the end-to-end chat interaction.
