# Wave 35 implementation handoff

Date: 2026-11-23  
Branch: feat/wave-thirty-five-ai-model-and-3mf-tools  
Status: implementation committed to branch; PR/CI/deployment acceptance pending.

## Purpose

Expand Nolane Tools into model packaging, model documentation, training-data validation, prompt-evaluation setup and 3D manufacturing. The new processors are deliberately orthogonal to existing MBOX, ICS, G-code, ONNX, MCAP, Iceberg, Parquet, CAD and scientific-format tools.

## Added processors

| ID | Category | Scope |
|---|---|---|
| safetensors-audit | developer | SafeTensors JSON header, dtype/shape byte lengths, offsets and overlap; never reads tensor weights. |
| gguf-model-audit | developer | GGUF v2/v3 metadata/tensor index, dimensions, alignment and offset bounds; never reads weights or executes inference. |
| hf-model-card-audit | developer | Hugging Face README YAML front matter and model-card section coverage; no Hub API. |
| chat-dataset-audit | data | Chat-completions JSONL roles/content/tool calls, malformed lines, duplicate rows and minimum example count; no prompt/completion output. |
| promptfoo-config-audit | developer | Local Promptfoo YAML/JSON providers/prompts/tests/assertions/scenarios structure; no reference resolution or model execution. |
| 3mf-package-audit | utility | 3MF OPC root relationships, primary model part, objects, mesh vertices and triangle indices; no extraction/rendering. |

## Files changed

- tools/wave35.py: six bounded local-file processors.
- tools/test_wave35.py: 12 focused regression/privacy tests.
- tools/runner.py: imports, allowlist, handler map, text-output registry and pipeline transitions.
- src/tools.ts: six catalog rows, upload inference and mirrored pipeline transitions.
- .github/workflows/tool-runner.yml: installs PyYAML only for Hugging Face model-card or Promptfoo YAML jobs.
- docs/TOOL-RESEARCH-2026-11-23-WAVE35.md: source and scope review.
- docs/NOLANE-TOOLS.md: candidate catalog entries and operator guidance.
- docs/STATUS.md and README.md: distinguish candidate code from current production until merge/deploy.

## Test gates

- TypeScript type-check and complete Vitest suite.
- Python runner parity: catalog IDs = RUNNERS = TOOLS; TypeScript/runner pipeline transitions identical; documentation lists every tool ID.
- Python runner unit suite including the 12 Wave 35 tests.
- Cloudflare Worker build, Worker export/health smoke and deploy workflow.
- Real owner-side Telegram uploads for representative non-sensitive files and /tool_retry remain a separate acceptance gate. CI, command-menu registration or a healthy webhook does not prove individual upload journeys.

## Limits / operational notes

- Shared input cap remains 20 MiB; 3MF expanded archive metadata is capped at 100 MiB.
- No D1 schema change, secret, paid service, new persistent runtime, remote data fetch or inference.
- PyYAML is installed conditionally in the private GitHub Actions runner, not in the Worker.
- The branch's first CI run must be treated as authoritative. Do not mark Wave 35 as production before main merge, Worker smoke and Cloudflare deployment succeed.
