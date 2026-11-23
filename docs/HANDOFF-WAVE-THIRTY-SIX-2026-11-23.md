# Wave 36 implementation handoff

Date: 2026-11-23  
Branch: feat/wave-thirty-six-ai-mlops-and-helm-tools  
Status: implementation and documentation committed to branch; PR/CI/deployment acceptance pending. Production remains Wave 35 at 456 tools.

## Six processors

| ID | Input | Capability |
|---|---|---|
| ollama-modelfile-audit | Modelfile / *.modelfile | Advisory static checks for FROM, PARAMETER, multiline blocks, MESSAGE, REQUIRES and CAPABILITY. No Ollama daemon/build/inference. |
| hf-tokenizer-audit | tokenizer.json / *.tokenizer.json | Checks mapping and Unigram vocabularies, token IDs, added tokens, BPE merges and tokenizer component structure without exposing token strings. |
| hf-dataset-card-audit | dataset-card.md / README.dataset.md | Checks dataset YAML metadata and responsible-documentation section coverage. |
| mlflow-model-audit | MLmodel | Checks MLflow flavors, python_function metadata, signature shape and environment references. Never imports loaders or deserializes artifacts. |
| dvc-pipeline-audit | dvc.yaml / dvc.yml / dvc.lock | Checks schema, stage fields, dependencies, outputs, params and lock-manifest shape. Never resolves remotes or runs stages. |
| helm-chart-audit | Chart.yaml | Checks chart API version, name, SemVer, type, dependencies, aliases, maintainers and annotations. Never renders or installs a chart. |

## Changed files

- tools/wave36.py: six bounded static auditors.
- tools/test_wave36.py: 13 focused regression, structural and privacy tests.
- tools/runner.py: imports, RUNNERS allowlist, TOOLS handler map, pipeline transitions and text-output registry.
- src/tools.ts: six catalog rows, file inference and mirrored pipeline transitions.
- tests/tools.test.ts: Wave 36 registry, inference and pipeline acceptance.
- tests/telegram.test.ts: Tool Center count from 456 to 462.
- .github/workflows/tool-runner.yml: conditional PyYAML install for YAML processors only.
- docs/TOOL-RESEARCH-2026-11-23-WAVE36.md and docs/NOLANE-TOOLS.md: source review and operator documentation.
- README.md and docs/STATUS.md: candidate status; production remains 456 until merge and deploy.

## Test gates

- TypeScript type-check and complete Vitest suite.
- Python runner tests including all 13 Wave 36 tests.
- Catalog uniqueness and parity: TypeScript catalog = RUNNERS = TOOLS; TypeScript and Python pipeline transitions equal; docs list every ID.
- Cloudflare Worker build, production health smoke and deployment workflow.
- Verify Telegram webhook and command menu after deploy.
- Owner-side private Telegram upload tests for each supported input and /tool_retry remain a separate manual acceptance gate.

## Limits

- Existing runner upload limit remains 20 MiB.
- YAML/JSON/Modelfile input limits are 4 MiB; dataset cards are capped at 2 MiB.
- No D1 migration, Cloudflare secret, paid API, new persistent service, external model inference, remote data fetch or cluster deployment.
- Current production stays at 456 tools until all CI, merge, Worker health smoke and Cloudflare deployment checks succeed.
