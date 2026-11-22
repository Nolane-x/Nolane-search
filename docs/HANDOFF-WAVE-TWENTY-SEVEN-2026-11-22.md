# Wave 27 handoff — 2026-11-22

## Branch and scope

- Branch: `feat/wave-twenty-seven-digital-preservation-tools`
- Base production: Wave 26 / 417 tools, Cloudflare Worker Version 83 `a0d66d94-083a-46fa-af0b-1237e435a478`
- Candidate catalog: **426 unique tools**, +9 processors.
- Candidate remains off production until PR CI, Worker export/health smoke and Cloudflare deployment pass.

## Added processors

| ID | Format/domain | Primary checks |
|---|---|---|
| `bagit-archive-audit` | BagIt ZIP/TAR | bagit.txt, payload/tag manifests, file completeness, path safety and real digest verification. |
| `frictionless-package-audit` | Frictionless Data Package | resource descriptors/paths, field schemas, primary/foreign-key references and remote/unsafe path counts. |
| `ro-crate-audit` | RO-Crate JSON-LD | @graph entities, root Dataset/metadata descriptor, duplicate IDs and unresolved local references. |
| `iiif-manifest-audit` | IIIF Presentation API 3.0 | Manifest/Canvas, dimensions, annotation pages, targets, image bodies and service counts. |
| `datacite-metadata-audit` | DataCite XML 4.7 | DOI shape, creator/title/publisher/year/resource type and related-identifier counts. |
| `mets-package-audit` | METS XML 1.12.1 | Header/dmdSec/amdSec/fileSec/structMap, file entries and IDREF cross-checks. |
| `premis-event-audit` | PREMIS XML 3.0 | Object/event/agent/rights counts, identifiers, linking references and timestamp shape. |
| `stac-catalog-audit` | STAC 1.1.0 JSON | Catalog/Collection/Item shape, links, assets/roles, bbox and temporal/spatial extents. |
| `tei-document-audit` | TEI P5 XML 4.12.0 | Header/text/body structure, scholarly elements, duplicate xml:id and broken fragment targets. |

## Implementation map

- Parser module: `tools/wave27.py`.
- Synthetic regression suite: `tools/test_wave27.py` (21 tests).
- Runner imports, allowlist, handler dispatch, text-output support and pipeline transitions: `tools/runner.py`.
- TypeScript catalog, transitions and upload inference: `src/tools.ts`.
- Registry/inference tests and Telegram Tool Center count: `tests/tools.test.ts`, `tests/telegram.test.ts`.
- Research provenance, versioned references, bounds and privacy safeguards: `docs/TOOL-RESEARCH-2026-11-22.md`, `docs/NOLANE-TOOLS.md` and `docs/STATUS.md`.

## Review hardening

- PREMIS linking identifiers are now matched by target entity kind, identifier type and value, avoiding false matches when two object classes reuse the same identifier string.
- TEI fragment checks now count only same-document `#fragment` references; fragments in external URLs and sibling-document URIs are not reported as broken local IDs.
- Two additional synthetic regression tests cover these cases; all 21 Wave 27 tests pass in PR CI.

## Safety and bounds

- No payload file is extracted to disk; BagIt manifests are checked by streaming member bytes and computing the declared digest.
- No external URL, linked resource, IIIF image, STAC asset or Frictionless resource is fetched.
- ZIP/TAR paths are checked; symlinks/special archive members are rejected; input/archive/member/expanded-size limits apply.
- DOI, title, author, depositor, rights, resource names/paths, JSON-LD entity IDs, coordinates, external URLs and scholarly text are withheld.
- XML DTD/entity declarations are rejected. JSON descriptors and XML files have explicit size limits.
- All parsers use Python standard library only; no third-party runtime dependency or D1 schema change is needed.
- Reports are structural diagnostics, not full schema validation, legal deposit certification or proof of future readability.

## Release gates

1. Confirm 426 unique TypeScript catalog IDs, 426 Python RUNNERS IDs and 426 handlers.
2. Type-check, Vitest, Python compile and full runner unittest discovery.
3. Worker build/export and deployed `/health` smoke.
4. Cloudflare deployment, runtime secrets, webhook and command registration.
5. Owner-level Telegram E2E with synthetic/non-sensitive examples and `/tool_retry`.

Wave 27 remains a candidate until all automated release gates pass. Wave 26 is the 417-tool production baseline.