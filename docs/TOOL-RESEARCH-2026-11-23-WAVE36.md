# Wave 36 upstream research — local AI, MLOps and Kubernetes manifests

Date: 2026-11-23  
Branch status: candidate implementation; production remains Wave 35 at 456 tools until CI, merge and Cloudflare deployment complete.

## Why these ecosystems were selected

The existing Tool Center already checks SafeTensors, GGUF, model cards, chat fine-tuning JSONL, Promptfoo configs and 3MF. Wave 36 moves to adjacent ecosystems that were not represented by a dedicated processor in the 456-ID catalog: local Ollama model recipes, serialized Hugging Face tokenizer metadata, dataset documentation cards, MLflow model manifests, DVC pipeline manifests and Helm chart metadata.

| Upstream project / specification | Local artifact | Proposed processor | What it checks |
|---|---|---|---|
| [Ollama Modelfile reference](https://github.com/ollama/ollama/blob/main/docs/modelfile.mdx) | `Modelfile` | `ollama-modelfile-audit` | Required FROM, PARAMETER, TEMPLATE/SYSTEM/LICENSE/MESSAGE directives, REQUIRES version, CAPABILITY values, unknown/incomplete directives. |
| [Hugging Face Tokenizers](https://github.com/huggingface/tokenizers) | `tokenizer.json` | `hf-tokenizer-audit` | Model family, mapping/Unigram vocabulary shape, ID uniqueness, added-token IDs, BPE merges and common pipeline component objects. |
| [Hugging Face Dataset Card guide](https://github.com/huggingface/datasets/blob/main/docs/source/dataset_card.mdx) | `dataset-card.md` / `README.dataset.md` | `hf-dataset-card-audit` | YAML front matter for license/language/tags/task/size/configs plus dataset structure, fields, splits, creation, sensitive data, bias and licensing sections. |
| [MLflow model format](https://github.com/mlflow/mlflow/blob/master/mlflow/models/model.py) | `MLmodel` | `mlflow-model-audit` | Flavors, python_function loader/data/environment references, optional signature input/output/parameter declarations and malformed manifest structures. |
| [DVC pipeline file guide](https://dvc.org/doc/user-guide/project-structure/dvcyaml-files) | `dvc.yaml`, `dvc.yml`, `dvc.lock` | `dvc-pipeline-audit` | Schema version, stages, command fields, dependency/output/parameter/metric/plot entries, lockfile shape and repeated output paths. |
| [Helm chart metadata implementation](https://github.com/helm/helm/blob/main/pkg/chart/v2/metadata.go) | `Chart.yaml` | `helm-chart-audit` | API version, chart name, SemVer, application/library type, dependencies/aliases, maintainers and annotations. |

## Upstream observations

- Ollama documents Modelfile as line-oriented instructions with FROM required and directives including PARAMETER, TEMPLATE, SYSTEM, LICENSE, MESSAGE, REQUIRES and CAPABILITY. The file states that instructions are case-insensitive and can appear in any order. This processor is intentionally an advisory subset parser, not an Ollama build validator.
- Hugging Face Tokenizers serializes tokenizer models with vocabulary and merge data. BPE/WordPiece vocabularies are commonly token-to-ID mappings; Unigram model vocabulary is an ordered list of token/score pairs. Added tokens are stored separately with explicit IDs and flags. The processor supports both forms without printing token strings.
- Hugging Face recommends a README dataset card with YAML metadata such as license, language, pretty name, task categories and size categories, and narrative sections that explain dataset content, creation and responsible use. The processor measures documentation coverage; it cannot verify truthfulness or data rights.
- MLflow's MLmodel file is a YAML model manifest with a flavors mapping. A python_function flavor can include a loader module, model-data location and environment references; signatures may describe inputs, outputs and inference parameters. The processor reads that metadata only and does not load any model flavor.
- DVC pipeline definitions contain named stages and fields such as cmd, deps, params and outs; DVC lock files record resolved stage state. This processor checks one local YAML manifest at a time, not the complete dependency graph or DVC cache.
- Helm Chart.yaml metadata carries apiVersion, name and version and may declare dependencies, maintainers, annotations, kubeVersion and application/library type. The processor validates metadata only; it does not render templates or install dependencies.

## Implementation and privacy boundaries

- No upstream implementation code is vendored. The six auditors are independent, read-only local parsers.
- YAML parsing uses the already-pinned PyYAML 6.0.2 dependency and is installed in the one-off GitHub Actions runner only when a YAML-based Wave 36 tool is selected.
- Ollama Modelfile and Hugging Face tokenizer JSON use the Python standard library. All YAML/Markdown/JSON files are capped at 4 MiB (dataset cards at 2 MiB).
- Reports contain counts and yes/no coverage only. They do not echo prompts, model names/paths, tokens/vocabulary entries, dataset IDs, commands, stage names, cache paths/hashes, loader module strings, chart names, repository URLs, maintainer details or annotation values.
- No Ollama daemon, Hub endpoint, MLflow server, DVC remote, Helm CLI, Kubernetes cluster, model, pipeline stage or chart template is contacted or executed.
- MLflow safety is deliberately conservative: no flavor imports and no pickle, cloudpickle, joblib or serialized model deserialization occurs.
- These tools do not establish model quality, licensing/consent, dataset correctness, reproducibility, DVC DAG completeness, Helm template correctness, Kubernetes deployability or full upstream-spec conformance.

## Expected impact

Six additions increase the proposed branch catalog from 456 to 462 IDs. They expand coverage into local model setup, tokenizer engineering, dataset stewardship, MLflow model packaging, reproducible ML pipelines and Kubernetes packaging without changing the Cloudflare Worker architecture, D1 schema or production secrets.
