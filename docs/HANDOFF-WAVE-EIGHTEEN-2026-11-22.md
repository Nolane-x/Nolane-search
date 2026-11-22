# Wave 18 handoff — Cross-domain everyday, data and media tools

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