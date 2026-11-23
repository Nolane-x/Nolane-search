# Wave 35 implementation handoff

Date: 2026-11-23  
Branch: feat/wave-thirty-five-ai-model-and-3mf-tools  
Status: merged and deployed to production on 2026-11-23.

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
| three-mf-package-audit | utility | 3MF OPC root relationships, primary model part, objects, mesh vertices and triangle indices; no extraction/rendering. |

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

## Production rollout — 2026-11-23

- [PR #88](https://github.com/Nolane-x/Nolane-search/pull/88) merged to main as `3e20f1fe423b68fc453af14ef9fc3026c274a9d0`.
- PR CI [45175181809](https://github.com/Nolane-x/Nolane-search/actions/runs/45175181809) passed 25 Vitest files / 253 tests, TypeScript type-check, deployment-script checks, 341 Python runner tests and Worker build.
- Main CI [45175463155](https://github.com/Nolane-x/Nolane-search/actions/runs/45175463155), Worker export/health smoke [45175463060](https://github.com/Nolane-x/Nolane-search/actions/runs/45175463060) and Cloudflare deployment [45175463070](https://github.com/Nolane-x/Nolane-search/actions/runs/45175463070) all succeeded.
- The health smoke returned `ok: true` and `database: reachable`. D1 migration was skipped because this release changes no database schema.
- Cloudflare Worker Version ID: `4e6aebb9-655d-4b33-9233-dd29540d1788`. Telegram webhook (message + callback_query) was verified and bot commands registered.
- Production tool catalog: **456 tools**, up from 450. All six Wave 35 IDs are in the TypeScript catalog, Python runner allowlist, handler map, upload inference, pipeline transitions and operator documentation.
- No new Cloudflare secret, paid resource, D1 migration or persistent service was introduced.

## Owner-side acceptance still required

The code, CI, Worker build/health smoke, Cloudflare deployment and Telegram command registration are verified. The real private Telegram upload journey for each new file type has not been exercised in this session. Upload representative non-sensitive fixtures for SafeTensors, GGUF, model cards, chat JSONL, Promptfoo YAML and 3MF, inspect reports and verify retry behavior with `/tool_retry`. This manual acceptance must not be treated as complete until confirmed.
