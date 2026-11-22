# Wave 20 handoff — Creator, publishing and content utilities

Date: 2026-11-22
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-twenty-creator-content-utilities

## Scope

Adds nine processors beyond the 336-tool Wave 19 production catalog:

- rss-atom-audit: parse RSS/Atom/RDF feeds offline; count missing/duplicate IDs and missing title/link/date without printing content or URLs.
- sitemap-xml-audit: inspect sitemap urlset/index structure, loc duplicates, lastmod, priority and changefreq; never fetch URLs.
- robots-txt-audit: inspect user-agent groups, allow/disallow rules, sitemap and crawl-delay directives locally; never fetch robots.txt or crawl.
- jsonl-profile: stream JSONL record, field presence/type drift, invalid lines and duplicate-key counters; field values are withheld.
- image-privacy-audit: report EXIF GPS/date/device/owner/thumbnail/XMP/IPTC/ICC metadata presence and counts; never print values/coordinates.
- svg-safety-audit: inspect scripts, foreignObject, event attributes, external/data references and CSS URLs/imports; read-only, not a sanitizer.
- wcag-contrast-audit: calculate HEX-pair contrast ratios and check WCAG 2.2 AA/AAA normal/large text thresholds.
- ssh-public-key-audit: inspect OpenSSH authorized_keys/public keys and PEM public keys; count duplicates and weak algorithms/key sizes; no private-key support, no SSH connections.
- archive-checksum-manifest: stream ZIP member contents to produce a CSV path/size/SHA-256 manifest; no extraction to filesystem.

## Limits

- RSS/Atom: 10 MiB, 50,000 entries; DTD/ENTITY blocked.
- Sitemap: 20 MiB, 50,000 entries; DTD/ENTITY blocked.
- robots.txt: 2 MiB, 20,000 lines.
- JSONL: 20 MiB, 100,000 lines, 1 MiB max line.
- Image privacy: 20 MiB, 80 megapixels.
- SVG: 5 MiB, 100,000 elements, 250,000 attributes, DTD/ENTITY blocked.
- WCAG: 2 MiB, 5,000 input lines.
- SSH public keys: 2 MiB, 1,000 keys.
- ZIP checksum: 20 MiB archive, 1,000 members, 200 MiB declared uncompressed data, 50 MiB per member.

## Upstream review and licensing

- feedparser (BSD-2-Clause) and color-contrast-checker (MIT) reviewed.
- image-metadata-toolkit (MIT, Pillow) reviewed; only privacy metadata counts were reimplemented.
- ssh-audit (MIT) reviewed; this processor does not connect to servers.
- darylldoyle/svg-sanitizer (GPLv2) and dhvcc/rss-parser (GPL-3.0) deliberately not integrated.
- No new dependency; existing Pillow and cryptography are reused, and remaining work uses Python standard library.

## Acceptance gates

1. 345 unique TypeScript catalog IDs, 345 Python RUNNERS entries and 345 handler mappings.
2. Nine new tools have matching pipeline transitions; report-only tools appear in TEXT_OUTPUT_TOOLS; CSV checksum output feeds CSV processors.
3. Python fixtures cover all nine tools and privacy boundaries.
4. Type-check, Vitest, deployment-script checks, Python runner suite and Worker build pass.
5. Worker export/health smoke and Cloudflare deploy pass before counting 345 production processors.
6. Real Telegram upload/report/retry remains owner-level E2E after deployment.

Research notes: docs/TOOL-RESEARCH-2026-11-22.md