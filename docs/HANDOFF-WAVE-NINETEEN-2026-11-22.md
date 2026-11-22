# Wave 19 release handoff — Network, media, ebook and data quality tools

Date: 2026-11-22
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-nineteen-network-media-ebook-data-tools

## Scope

Wave 19 is merged and deployed. Eight distinct processors extend the 328-tool Wave 18 production catalog to 336:

- pcap-network-audit: read PCAP/PCAPNG offline, count protocols/ports/packets/duration and unique endpoint count; no IP addresses, DNS names or payloads in the report.
- audio-tag-audit: check common title/artist/album/date/genre/track/disc/album artist/composer tag groups and cover-art presence via FFprobe; never emits tag values.
- image-similarity-audit: compare images inside ZIPs with SHA-256 and a 16×16 DCT perceptual hash; emit CSV pairs, not image content.
- json-schema-validate: validate an envelope with schema + data using jsonschema, reject remote references and emit error pointers/rules only.
- epub-structure-audit: inspect mimetype, container.xml, OPF manifest/spine/nav and href targets; no title, author or chapter content in report.
- markdown-quality-audit: report heading hierarchy/duplicates, trailing whitespace, long lines, empty link targets and code-fence issues using line/rule codes only.
- dns-zone-audit: parse BIND zone files offline and count record types; reject $INCLUDE/$GENERATE and never emit names, IP or TXT/mailbox values.
- x509-certificate-audit: inspect PEM/DER certificate validity, expiry, key types/sizes, weak signature hash algorithms, CA and SAN counts; no identity values, trust-chain or revocation queries.

## Bounds

- PCAP/PCAPNG: 20 MiB input, 200,000 packets.
- Audio tag audit: 100 MiB input.
- Image ZIP: 1,000 archive entries, max 200 images, 150 MiB declared image content, 20 MiB per image.
- JSON Schema: 10 MiB JSON input, reject non-local refs, cap validation errors.
- EPUB: 20 MiB archive, 3,000 entries, 120 MiB declared uncompressed data; XML DTD/ENTITY disabled.
- Markdown: 5 MiB, 100,000 lines, at most 120 reported findings.
- DNS zone: 10 MiB; no file includes or generation directives.
- X.509: 5 MiB, 1–50 certificates.

## Dependencies and licenses checked

- dpkt — BSD-style; PCAP/PCAPNG.
- jsonschema — MIT; JSON Schema.
- dnspython — ISC; DNS zone parsing.
- cryptography — Apache-2.0 OR BSD-3-Clause; X.509 parsing.
- ImageHash (2-Clause BSD) reviewed but not added; pHash is implemented locally with Pillow to avoid NumPy/SciPy overhead.
- Mutagen is GPL-2.0-or-later and is not integrated. FFprobe is reused for audio metadata presence only.
- EPUBCheck was reviewed for coverage; the Java application is not bundled. This is a limited structural audit, not full conformance validation.

## Acceptance gates

1. 336 unique TypeScript catalog IDs, 336 Python RUNNERS entries and 336 handler mappings.
2. Eight new processors have matching Python and TypeScript transition edges; image-similarity output feeds CSV processors.
3. Python fixtures exercise all eight tools, including privacy assertions.
4. Type-check, Vitest, deployment-script checks, Python runner suite and Worker build pass.
5. Worker export/health smoke and Cloudflare production deployment pass before counting 336 production processors.
6. Live Telegram upload/report/retry for representative PCAP, audio, ZIP of images, JSON envelope, EPUB, Markdown, DNS zone and X.509 files remains owner-level E2E.

Research notes: docs/TOOL-RESEARCH-2026-11-22.md

## Production rollout — 2026-11-22

- PR #69 merged into `main`: https://github.com/Nolane-x/Nolane-search/pull/69
- Main commit: `063b73168111db96acb799df27e1c9fb5f11d3e6`.
- Main CI [44981447755](https://github.com/Nolane-x/Nolane-search/actions/runs/44981447755), Worker export/production health smoke [44981447745](https://github.com/Nolane-x/Nolane-search/actions/runs/44981447745) and production deployment [44981447683](https://github.com/Nolane-x/Nolane-search/actions/runs/44981447683) all passed.
- CI passed TypeScript type-check, Vitest, deployment-script checks, 127 Python runner tests and Worker build.
- Deployment verified Worker bundle, runtime-secret upload and Telegram webhook/command-menu registration. D1 migration was skipped because no schema changed.
- Production catalog: 336 processors. Cloudflare Worker Version ID: `f7be3cf0-1370-4333-84be-af5f22e6f012`.
- Still required: owner-level private Telegram upload/report/retry for representative input files. CI and deployment do not prove the entire chat interaction.
