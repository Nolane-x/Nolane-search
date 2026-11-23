# Wave 35 upstream research — AI model artifacts, evaluation datasets and 3D manufacturing

Date: 2026-11-23  
Scope: six new local-file processors proposed for Nolane Tools. This is a source/specification review, not a claim of complete standard certification.

## Selected upstream projects and why they add distinct coverage

| Upstream source | Format / ecosystem | Nolane processor | Reason to add |
|---|---|---|---|
| [safetensors/safetensors](https://github.com/safetensors/safetensors) | SafeTensors weight container | safetensors-audit | Structural audit for tensor descriptors, dtype/shape byte lengths, offsets and overlaps, without loading weight tensors. |
| [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp), [GGUF header definition](https://github.com/ggml-org/llama.cpp/blob/master/ggml/include/gguf.h) | GGUF model container | gguf-model-audit | Read the GGUF v2/v3 header, metadata index and tensor descriptor table for compact/local LLM files. |
| [huggingface/hub-docs](https://github.com/huggingface/hub-docs) | Hugging Face model-card convention | hf-model-card-audit | Review README YAML front matter and documentation coverage for intended use, limitations, training data and evaluation. |
| [OpenAI supervised fine-tuning guide](https://developers.openai.com/api/docs/guides/supervised-fine-tuning) | Chat Completions JSONL | chat-dataset-audit | Catch malformed message examples, roles, tool-call structures and duplicate lines before upload to a training service. |
| [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | Prompt/model evaluation configuration | promptfoo-config-audit | Validate the local structure of providers, prompts, test cases, variables, assertions and scenarios. |
| [3MF Consortium Core Specification](https://github.com/3MFConsortium/spec_core) | 3MF ZIP/OPC package and mesh XML | 3mf-package-audit | Inspect the package relationships, primary model XML, objects, mesh vertices and triangle indices. |

### Source-format findings

- SafeTensors starts with an unsigned little-endian 64-bit header length, followed by a UTF-8 JSON header. Tensor data offsets are relative to the data buffer, and the format disallows duplicate JSON keys. The processor follows those rules and checks descriptor-size/offset consistency without reading weight bytes. See the [upstream format definition](https://github.com/safetensors/safetensors/blob/main/README.md).
- GGUF files begin with the GGUF magic and version, then tensor/metadata counts, typed metadata values, tensor names/dimensions/types/offsets and an aligned tensor-data region. The processor follows the current header layout and checks metadata uniqueness, supported version, dimension bounds, alignment and file bounds. It intentionally does not decode quantized tensors. See the [upstream header](https://github.com/ggml-org/llama.cpp/blob/master/ggml/include/gguf.h).
- A Hugging Face Hub model card is a Markdown README with YAML metadata at the beginning. The documentation recommends describing the model, intended uses and limitations, training information/datasets and evaluation. The processor treats those as completeness indicators, not verified facts. See [Hugging Face Model Cards](https://huggingface.co/docs/hub/model-cards).
- OpenAI supervised fine-tuning data uses JSONL with one complete chat-completions structure per line and requires at least 10 examples for the documented workflow. The processor checks local message roles/content and basic tool-call shape, but does not upload the dataset. See the [SFT guide](https://developers.openai.com/api/docs/guides/supervised-fine-tuning).
- Promptfoo configs use YAML/JSON and connect prompts with providers and test cases/assertions; scenarios are also supported. The processor checks common top-level structure only. It does not replace Promptfoo's complete upstream schema, resolve references or run an evaluation. See the [configuration guide](https://www.promptfoo.dev/docs/configuration/guide/) and [reference](https://www.promptfoo.dev/docs/configuration/reference/).
- 3MF is an OPC package using ZIP and XML parts; root relationships identify the primary 3D model part. The processor validates the primary package/model path and the local mesh index structure, not every optional 3MF extension. See the [3MF Core Specification](https://3mf.io/spec/) and [specification source](https://github.com/3MFConsortium/spec_core).

## Implementation and safety boundary

- No external CLI, new cloud resource, secret, D1 migration, persistent service or model inference is introduced.
- SafeTensors, GGUF, JSONL and 3MF use Python's standard library. Hugging Face model-card and Promptfoo YAML parsing uses PyYAML 6.0.2, installed only when either corresponding processor is selected.
- The shared runner upload cap remains 20 MiB. SafeTensors and GGUF readers parse only bounded headers/indexes; model tensor/weight bytes are never loaded into memory.
- 3MF ZIP inspection does not extract files. It caps archive entries at 10,000, expanded size at 100 MiB and individual XML parts at 20 MiB; encrypted, duplicate, traversal and excessive-compression entries are rejected.
- Dataset and configuration reports contain aggregate structure/counts only. No prompts, completions, tool arguments, model IDs, metadata values, object names, tensor names, file paths or vertex coordinates are printed.
- PyYAML parsing is local. Promptfoo file/HTTP references are not resolved. No provider is contacted.
- These processors do not certify model quality, license compliance, dataset consent, reproducibility, 3D printability, full GGUF weight integrity or full conformance to every extension of the upstream formats.

## License and reuse

The implementation is an independent parser/auditor based on public format documentation and does not vendor upstream implementation code or schemas. The 3MF spec repository is BSD-2-Clause; no upstream runtime code is copied. No additional upstream runtime dependency is introduced.
