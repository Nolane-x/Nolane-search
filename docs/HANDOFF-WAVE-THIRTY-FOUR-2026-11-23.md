# Wave 34 handoff — robotics, lakehouse, model and trace formats

Date: 2026-11-23
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-thirty-four-robotics-ml-observability
Status: implementation branch; not merged and not deployed.

## Production boundary

Wave 33 remains the latest production release: **446 tools**. This branch contains four new catalog entries (450 on the branch); they are not production until PR CI, Worker export/health smoke and Cloudflare deployment all pass after merge.

## Added processors

| ID | Purpose |
|---|---|
| `mcap-recording-audit` | Read MCAP header/footer and optional index summary; never read message payloads or decompress chunks. |
| `iceberg-metadata-audit` | Parse Apache Iceberg table metadata v1/v2/v3 locally and check snapshot/schema/spec references. |
| `onnx-model-audit` | Run ONNX structural checker only; no inference, custom op execution or external tensor load. |
| `otel-trace-audit` | Audit OTLP/JSON trace IDs, time ordering, enums, duplicate span IDs and collection shape with aggregate-only output. |

## Code and integration

- Python implementations: `tools/wave34.py`.
- Focused tests: `tools/test_wave34.py` (11 tests, including synthetic MCAP writer fixtures and actual PyIceberg/ONNX parsing).
- TypeScript catalog and upload inference updated; Python runner allowlist, handler map, text-output registry and pipeline transitions mirrored.
- Conditional runtime packages: `mcap==1.6.0`, `pyiceberg==0.12.0`, `onnx==1.23.2`; OTLP is standard-library JSON.
- No Worker/D1 schema changes, new secret or persistent service.

## Security boundaries

- MCAP audit reads header/footer/index summary only. It does not scan/decompress message chunks; therefore no chunk CRC or data-section CRC verification is claimed.
- Iceberg audit parses only a local metadata JSON file; no remote catalog, manifest or object-store access.
- ONNX audit does not execute model code or inference and does not load external weights.
- OTLP reports aggregate structure only and does not emit trace/span identifiers, span names or attribute values.
- Inputs and record/model/span counts are bounded; raw parser errors are withheld.

## Verification status

Pending: update the Tool Center documentation with the four `/tool` IDs, confirm catalog/runner/handler/pipeline parity, run TypeScript/Vitest/Python/Worker CI, then verify post-merge export/health smoke and Cloudflare deployment. Production remains **446** until those release gates pass.

Detailed upstream sources, versions, licenses, limits and scope: `docs/TOOL-RESEARCH-2026-11-23-WAVE34.md`.
