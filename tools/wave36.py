from __future__ import annotations

import json
import re
import shlex
from collections import Counter
from pathlib import Path
from typing import Any

MAX_CONFIG_BYTES = 4 * 1024 * 1024
MAX_CARD_BYTES = 2 * 1024 * 1024
MAX_TOKENIZER_ENTRIES = 2_000_000


def _report(path: Path, prefix: str, title: str, lines: list[str]) -> dict:
    from wave28 import _report as shared_report
    return shared_report(path, prefix, title, lines)


def _read_utf8(path: Path, label: str, limit: int = MAX_CONFIG_BYTES) -> str:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"{label} must be a regular local file.")
    size = path.stat().st_size
    if size <= 0:
        raise RuntimeError(f"{label} is empty.")
    if size > limit:
        raise RuntimeError(f"{label} exceeds the {limit // (1024 * 1024)} MiB processing limit.")
    try:
        return path.read_text(encoding="utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        raise RuntimeError(f"{label} must be valid UTF-8.") from None


def _yaml_mapping(path: Path, label: str, limit: int = MAX_CONFIG_BYTES) -> dict[str, Any]:
    text = _read_utf8(path, label, limit)
    try:
        import yaml
        value = yaml.safe_load(text)
    except Exception:
        raise RuntimeError(f"{label} is not valid YAML.") from None
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} root must be a YAML mapping.")
    return value


def _markdown_card(path: Path, label: str) -> tuple[dict[str, Any], str, int]:
    text = _read_utf8(path, label, MAX_CARD_BYTES)
    lines = text.splitlines()
    metadata: dict[str, Any] = {}
    warnings = 0
    if lines and lines[0].strip() == "---":
        closing = next((i for i in range(1, min(len(lines), 500)) if lines[i].strip() in ("---", "...")), None)
        if closing is not None:
            try:
                import yaml
                value = yaml.safe_load("\n".join(lines[1:closing]))
            except Exception:
                raise RuntimeError(f"{label} YAML front matter is invalid.") from None
            if isinstance(value, dict):
                metadata = value
            else:
                warnings += 1
            body = "\n".join(lines[closing + 1:])
        else:
            body = text
            warnings += 1
    else:
        body = text
        warnings += 1
    return metadata, body, warnings


def _heading_set(body: str) -> set[str]:
    return {
        re.sub(r"\s+", " ", match.group(1).strip().lower())
        for match in re.finditer(r"^#{1,6}\s+(.+?)\s*#*\s*$", body, re.M)
    }


def ollama_modelfile_audit(path: Path) -> dict:
    """Statically audit Ollama Modelfile directives; never invokes Ollama or resolves FROM paths."""
    text = _read_utf8(path, "Ollama Modelfile")
    if path.name.lower() not in ("modelfile", "ollama.modelfile") and not path.name.lower().endswith(".modelfile"):
        raise RuntimeError("Ollama Modelfile audit accepts a file named Modelfile or ending in .modelfile.")

    allowed = {"FROM", "PARAMETER", "TEMPLATE", "SYSTEM", "LICENSE", "MESSAGE", "REQUIRES", "CAPABILITY"}
    counts: Counter[str] = Counter()
    unknown = malformed = 0
    from_count = 0
    parameter_keys: Counter[str] = Counter()
    capabilities: Counter[str] = Counter()
    block_open = False
    block_delimiter = '"""'

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if block_open:
            if block_delimiter in line:
                block_open = False
                remainder = line.split(block_delimiter, 1)[1].strip()
                if not remainder or remainder.startswith("#"):
                    continue
                line = remainder
            else:
                continue
        if line.startswith("#"):
            continue
        match = re.match(r"^([A-Za-z_]+)\s*(.*)$", line)
        if not match:
            malformed += 1
            continue
        directive = match.group(1).upper()
        argument = match.group(2).strip()
        if directive not in allowed:
            unknown += 1
            continue
        counts[directive] += 1

        if directive == "FROM":
            from_count += 1
            if not argument:
                malformed += 1
        elif directive == "PARAMETER":
            try:
                tokens = shlex.split(argument, posix=True)
            except ValueError:
                tokens = []
            if len(tokens) < 2:
                malformed += 1
            else:
                parameter_keys[tokens[0].lower()] += 1
        elif directive == "MESSAGE":
            try:
                tokens = shlex.split(argument, posix=True)
            except ValueError:
                tokens = []
            if len(tokens) < 2 or tokens[0].lower() not in ("system", "user", "assistant"):
                malformed += 1
        elif directive == "CAPABILITY":
            try:
                tokens = shlex.split(argument, posix=True)
            except ValueError:
                tokens = []
            if len(tokens) != 1 or tokens[0].lower() not in ("completion", "tools", "vision", "decision"):
                malformed += 1
            elif tokens:
                capabilities[tokens[0].lower()] += 1
        elif directive == "REQUIRES":
            if not re.fullmatch(r"v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", argument):
                malformed += 1
        elif directive in ("TEMPLATE", "SYSTEM", "LICENSE"):
            if not argument:
                malformed += 1

        if argument.count(block_delimiter) % 2 == 1:
            block_open = True

    if from_count == 0:
        malformed += 1
    if block_open:
        malformed += 1
    duplicate_parameters = sum(count - 1 for count in parameter_keys.values() if count > 1)
    return _report(path, "ollama-modelfile", "Ollama Modelfile static directive audit", [
        f"Recognized directives: {sum(counts.values()):,}",
        f"FROM directives: {from_count:,} (at least one required; multiple sources can be intentional)",
        f"PARAMETER directives: {counts['PARAMETER']:,}",
        f"Distinct parameter keys: {len(parameter_keys):,}",
        f"Repeated parameter keys: {duplicate_parameters:,}",
        f"MESSAGE examples: {counts['MESSAGE']:,}",
        f"Declared capabilities: {len(capabilities):,}",
        f"Unknown directives: {unknown:,}",
        f"Malformed or incomplete directives: {malformed:,}",
        "Privacy: model names/paths, parameter values, prompts, system text, templates and license text are withheld",
        "Scope: checks a bounded subset of the documented Modelfile syntax; it does not resolve FROM/ADAPTER paths, verify model compatibility, build a model or run inference",
    ])


def hf_tokenizer_audit(path: Path) -> dict:
    """Check the structure of a Hugging Face tokenizer.json without emitting token strings."""
    size = path.stat().st_size if path.is_file() and not path.is_symlink() else 0
    if size <= 0 or size > MAX_CONFIG_BYTES:
        raise RuntimeError("Tokenizer JSON must be a non-empty regular file no larger than 4 MiB.")
    if path.name.lower() != "tokenizer.json" and not path.name.lower().endswith(".tokenizer.json"):
        raise RuntimeError("Hugging Face tokenizer audit accepts tokenizer.json or *.tokenizer.json.")
    try:
        root = json.loads(_read_utf8(path, "Hugging Face tokenizer JSON"))
    except json.JSONDecodeError:
        raise RuntimeError("Tokenizer file is not valid JSON.") from None
    if not isinstance(root, dict):
        raise RuntimeError("Tokenizer JSON root must be an object.")

    findings = 0
    model = root.get("model")
    if not isinstance(model, dict):
        model = {}
        findings += 1
    model_type = model.get("type")
    if not isinstance(model_type, str) or not model_type:
        findings += 1

    vocab = model.get("vocab", {})
    if not isinstance(vocab, dict):
        findings += 1
        vocab = {}
    if len(vocab) > MAX_TOKENIZER_ENTRIES:
        raise RuntimeError("Tokenizer vocabulary exceeds the 2,000,000-entry processing limit.")
    vocab_ids = []
    invalid_vocab_ids = 0
    for token_id in vocab.values():
        if isinstance(token_id, bool) or not isinstance(token_id, int) or token_id < 0:
            invalid_vocab_ids += 1
        else:
            vocab_ids.append(token_id)
    duplicate_vocab_ids = len(vocab_ids) - len(set(vocab_ids))

    added = root.get("added_tokens", [])
    if not isinstance(added, list):
        findings += 1
        added = []
    if len(added) > MAX_TOKENIZER_ENTRIES:
        raise RuntimeError("Added-token list exceeds the 2,000,000-entry processing limit.")
    added_ids = []
    invalid_added = 0
    for item in added:
        if not isinstance(item, dict):
            invalid_added += 1
            continue
        token_id = item.get("id")
        content = item.get("content")
        if isinstance(token_id, bool) or not isinstance(token_id, int) or token_id < 0 or not isinstance(content, str):
            invalid_added += 1
        else:
            added_ids.append(token_id)
    duplicate_added_ids = len(added_ids) - len(set(added_ids))
    cross_id_collisions = len(set(added_ids) & set(vocab_ids))

    merges = model.get("merges", [])
    if merges is not None and not isinstance(merges, list):
        findings += 1
        merges = []
    invalid_merges = 0
    if isinstance(merges, list):
        for merge in merges:
            if not (isinstance(merge, str) or (
                isinstance(merge, list) and len(merge) == 2 and all(isinstance(part, str) for part in merge)
            )):
                invalid_merges += 1

    for component in ("normalizer", "pre_tokenizer", "post_processor", "decoder"):
        value = root.get(component)
        if value is not None and not isinstance(value, dict):
            findings += 1
    for section in ("padding", "truncation"):
        value = root.get(section)
        if value is not None and not isinstance(value, dict):
            findings += 1
    if not isinstance(root.get("version"), (str, int)):
        findings += 1

    findings += invalid_vocab_ids + duplicate_vocab_ids + invalid_added + duplicate_added_ids + cross_id_collisions + invalid_merges
    return _report(path, "hf-tokenizer", "Hugging Face tokenizer JSON structure audit", [
        f"Tokenizer format version field: {'present' if 'version' in root else 'missing'}",
        f"Model type: {'present' if isinstance(model_type, str) and model_type else 'missing'}",
        f"Vocabulary entries: {len(vocab):,}",
        f"Added-token entries: {len(added):,}",
        f"Merge rules: {len(merges) if isinstance(merges, list) else 0:,}",
        f"Invalid vocabulary IDs: {invalid_vocab_ids:,}",
        f"Duplicate vocabulary IDs: {duplicate_vocab_ids:,}",
        f"Invalid added-token entries: {invalid_added:,}",
        f"Duplicate added-token IDs: {duplicate_added_ids:,}",
        f"Added/base vocabulary ID collisions: {cross_id_collisions:,}",
        f"Malformed merge entries: {invalid_merges:,}",
        f"Other structural findings: {findings - invalid_vocab_ids - duplicate_vocab_ids - invalid_added - duplicate_added_ids - cross_id_collisions - invalid_merges:,}",
        "Privacy: token strings, vocabulary content, special tokens and tokenizer rules are withheld",
        "Scope: checks common tokenizer.json structure and index consistency; it does not execute tokenizer code, encode text or compare against the Hub",
    ])


def hf_dataset_card_audit(path: Path) -> dict:
    """Review Hugging Face dataset README metadata and documentation coverage."""
    if path.suffix.lower() not in (".md", ".markdown"):
        raise RuntimeError("Hugging Face dataset-card audit accepts Markdown files.")
    metadata, body, warnings = _markdown_card(path, "Hugging Face dataset card")
    field_types = {
        "license": (str,), "language": (list, str), "tags": (list, str),
        "task_categories": (list, str), "task_ids": (list, str),
        "size_categories": (list, str), "pretty_name": (str,),
        "configs": (list, dict), "dataset_info": (list, dict),
    }
    malformed = 0
    for field, allowed in field_types.items():
        if field in metadata and not isinstance(metadata[field], allowed):
            malformed += 1
    required_metadata = ("license", "language", "tags", "task_categories", "size_categories")
    missing_metadata = sum(field not in metadata for field in required_metadata)

    headings = _heading_set(body)
    required_sections = {
        "dataset description": ("dataset description", "dataset summary", "about the dataset"),
        "dataset structure": ("dataset structure", "data structure"),
        "data fields": ("data fields", "features"),
        "data splits": ("data splits", "splits"),
        "dataset creation": ("dataset creation", "data collection", "data generation"),
        "personal / sensitive data": ("personal and sensitive information", "personal information", "sensitive data"),
        "bias / limitations": ("bias", "limitations", "known limitations"),
        "licensing / terms": ("licensing", "license", "terms of use"),
    }
    coverage = {
        label: any(any(token in heading for token in alternatives) for heading in headings)
        for label, alternatives in required_sections.items()
    }
    missing_sections = sum(not value for value in coverage.values())
    return _report(path, "hf-dataset-card", "Hugging Face dataset-card metadata and completeness audit", [
        f"YAML front matter: {'present' if bool(metadata) else 'missing or empty'}",
        f"Metadata fields: {len(metadata):,}",
        f"Common metadata fields missing: {missing_metadata:,}",
        f"Malformed common metadata fields: {malformed:,}",
        f"Documentation sections present: {sum(coverage.values())}/{len(coverage)}",
        "Section coverage: " + ", ".join(f"{key}={'yes' if value else 'no'}" for key, value in coverage.items()),
        f"Completeness warnings: {warnings + missing_metadata + missing_sections + malformed:,}",
        "Privacy: dataset identifiers, metadata values, source URLs and README body text are withheld",
        "Scope: checks local card completeness only; it does not verify Hub metadata, dataset provenance, rights, consent, bias claims or data quality",
    ])


def mlflow_model_manifest_audit(path: Path) -> dict:
    """Statically audit MLflow MLmodel metadata; never loads flavors, pickle files or model artifacts."""
    if path.name.lower() != "mlmodel":
        raise RuntimeError("MLflow manifest audit accepts a file named MLmodel.")
    manifest = _yaml_mapping(path, "MLflow MLmodel manifest")
    flavors = manifest.get("flavors")
    findings = 0
    if not isinstance(flavors, dict) or not flavors:
        findings += 1
        flavors = {}
    invalid_flavors = sum(not isinstance(value, dict) for value in flavors.values())
    findings += invalid_flavors

    pyfunc = flavors.get("python_function")
    loader_reference = False
    data_reference_count = 0
    environment_reference_count = 0
    if pyfunc is not None:
        if not isinstance(pyfunc, dict):
            findings += 1
        else:
            loader_reference = bool(pyfunc.get("loader_module") or pyfunc.get("loader_module_class"))
            data_value = pyfunc.get("data")
            data_reference_count = int(isinstance(data_value, str) and bool(data_value))
            for key in ("env", "conda_env", "python_env", "requirements"):
                value = pyfunc.get(key)
                if isinstance(value, str) and value:
                    environment_reference_count += 1
                elif value is not None and not isinstance(value, (dict, list)):
                    findings += 1

    signature = manifest.get("signature")
    signature_counts = {"inputs": 0, "outputs": 0, "params": 0}
    signature_valid = signature is None or isinstance(signature, dict)
    if isinstance(signature, dict):
        for field in signature_counts:
            value = signature.get(field)
            if value is None:
                continue
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    signature_valid = False
                    continue
            if isinstance(value, list):
                signature_counts[field] = len(value)
            elif isinstance(value, dict) and field == "params":
                signature_counts[field] = len(value)
            else:
                signature_valid = False
    if not signature_valid:
        findings += 1

    artifact_metadata = manifest.get("metadata")
    if artifact_metadata is not None and not isinstance(artifact_metadata, dict):
        findings += 1
    flavors_with_custom_code = sum(
        1 for value in flavors.values()
        if isinstance(value, dict) and any(key in value for key in ("loader_module", "loader_module_class", "code"))
    )
    return _report(path, "mlflow-model", "MLflow model manifest static audit", [
        f"MLmodel root metadata fields: {len(manifest):,}",
        f"Declared model flavors: {len(flavors):,}",
        f"Malformed flavor descriptors: {invalid_flavors:,}",
        f"Python-function flavor: {'present' if isinstance(pyfunc, dict) else 'absent'}",
        f"Loader/custom-code references: {flavors_with_custom_code:,}",
        f"Python-function loader reference: {'present' if loader_reference else 'absent'}",
        f"Python-function data reference: {'present' if data_reference_count else 'absent'}",
        f"Environment reference entries: {environment_reference_count:,}",
        f"Signature: {'present' if isinstance(signature, dict) else 'absent'}",
        f"Signature input/output/parameter declarations: {signature_counts['inputs']:,}/{signature_counts['outputs']:,}/{signature_counts['params']:,}",
        f"Structural findings: {findings:,}",
        "Privacy: flavor names, loader modules, paths, run IDs, model IDs, signature column names and metadata values are withheld",
        "Security boundary: no MLflow flavor is imported; no pickle/cloudpickle/joblib or model payload is loaded or deserialized",
        "Scope: checks the MLmodel YAML manifest only; it does not validate external files, dependencies, signatures against live data or model behavior",
    ])


def dvc_pipeline_manifest_audit(path: Path) -> dict:
    """Check local dvc.yaml or dvc.lock structure; never executes stages or reads remote caches."""
    if path.name.lower() not in ("dvc.yaml", "dvc.yml", "dvc.lock"):
        raise RuntimeError("DVC pipeline audit accepts dvc.yaml, dvc.yml or dvc.lock.")
    manifest = _yaml_mapping(path, "DVC pipeline manifest")
    is_lock = path.name.lower() == "dvc.lock"
    findings = 0
    schema = manifest.get("schema")
    if schema is not None and str(schema) not in ("2.0",):
        findings += 1
    stages = manifest.get("stages")
    if not isinstance(stages, dict):
        stages = {}
        findings += 1

    dependency_count = output_count = parameter_count = 0
    missing_commands = malformed_stages = 0
    paths_seen: Counter[str] = Counter()
    for _, stage in stages.items():
        if not isinstance(stage, dict):
            malformed_stages += 1
            continue
        if not is_lock and not isinstance(stage.get("cmd"), (str, list)):
            missing_commands += 1
        for field in ("deps", "outs", "params", "metrics", "plots"):
            value = stage.get(field, [])
            if value is None:
                continue
            if not isinstance(value, list):
                malformed_stages += 1
                continue
            if field in ("deps", "outs", "metrics", "plots"):
                if field == "deps":
                    dependency_count += len(value)
                elif field in ("outs", "metrics", "plots"):
                    output_count += len(value)
            elif field == "params":
                parameter_count += len(value)
            for item in value:
                if isinstance(item, str):
                    item_path = item
                elif isinstance(item, dict):
                    item_path = item.get("path")
                    if not isinstance(item_path, str) or not item_path:
                        malformed_stages += 1
                        continue
                else:
                    malformed_stages += 1
                    continue
                if field in ("outs", "metrics", "plots"):
                    paths_seen[item_path] += 1
        for field in ("wdir", "desc"):
            if field in stage and not isinstance(stage[field], str):
                malformed_stages += 1
    repeated_output_paths = sum(count - 1 for count in paths_seen.values() if count > 1)
    findings += malformed_stages + missing_commands + repeated_output_paths
    return _report(path, "dvc-pipeline", "DVC pipeline/lock manifest audit", [
        f"Manifest kind: {'lock file' if is_lock else 'pipeline definition'}",
        f"Schema version: {schema if schema is not None else 'not declared'}",
        f"Stage entries: {len(stages):,}",
        f"Dependency entries: {dependency_count:,}",
        f"Output/metric/plot entries: {output_count:,}",
        f"Parameter entries: {parameter_count:,}",
        f"Stages missing a command: {missing_commands:,}",
        f"Malformed stage descriptors or path entries: {malformed_stages:,}",
        f"Repeated output paths across stages: {repeated_output_paths:,}",
        f"Structural findings: {findings:,}",
        "Privacy: stage names, commands, parameter names/values, paths, hashes and remote locations are withheld",
        "Scope: checks one local DVC manifest; it does not resolve dependencies, construct the complete DAG, read DVC cache/remotes, run commands or verify artifact hashes",
    ])


def helm_chart_metadata_audit(path: Path) -> dict:
    """Validate Helm Chart.yaml metadata without rendering templates or contacting a cluster."""
    if path.name.lower() != "chart.yaml":
        raise RuntimeError("Helm chart audit accepts a file named Chart.yaml.")
    metadata = _yaml_mapping(path, "Helm Chart.yaml")
    findings = 0
    api_version = metadata.get("apiVersion")
    name = metadata.get("name")
    version = metadata.get("version")
    chart_type = metadata.get("type", "application")
    if api_version not in ("v1", "v2"):
        findings += 1
    if not isinstance(name, str) or not name or name in (".", "..") or "/" in name or "\\" in name:
        findings += 1
    semver = re.compile(r"^v?\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
    if not isinstance(version, str) or not semver.fullmatch(version):
        findings += 1
    if chart_type not in ("application", "library"):
        findings += 1

    dependencies = metadata.get("dependencies", [])
    if dependencies is None:
        dependencies = []
    if not isinstance(dependencies, list):
        findings += 1
        dependencies = []
    dependency_keys = []
    invalid_dependencies = 0
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            invalid_dependencies += 1
            continue
        dep_name = dependency.get("name")
        dep_version = dependency.get("version")
        alias = dependency.get("alias")
        repository = dependency.get("repository")
        if not isinstance(dep_name, str) or not dep_name:
            invalid_dependencies += 1
            continue
        if not isinstance(dep_version, str) or not semver.fullmatch(dep_version):
            invalid_dependencies += 1
        if repository is not None and not isinstance(repository, str):
            invalid_dependencies += 1
        if alias is not None and not isinstance(alias, str):
            invalid_dependencies += 1
        key = alias if isinstance(alias, str) and alias else dep_name
        dependency_keys.append(key)
    duplicate_dependencies = len(dependency_keys) - len(set(dependency_keys))
    findings += invalid_dependencies + duplicate_dependencies

    maintainers = metadata.get("maintainers", [])
    if maintainers is not None and not isinstance(maintainers, list):
        findings += 1
        maintainers = []
    invalid_maintainers = sum(
        not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item.get("name")
        for item in maintainers
    )
    findings += invalid_maintainers
    annotations = metadata.get("annotations", {})
    if annotations is not None and not isinstance(annotations, dict):
        findings += 1
    elif isinstance(annotations, dict) and any(not isinstance(k, str) or not isinstance(v, str) for k, v in annotations.items()):
        findings += 1

    return _report(path, "helm-chart", "Helm Chart.yaml metadata audit", [
        f"Chart API version: {api_version if isinstance(api_version, str) else 'missing or invalid'}",
        f"Chart name: {'present' if isinstance(name, str) and bool(name) else 'missing or invalid'}",
        f"Chart version: {'valid semver' if isinstance(version, str) and semver.fullmatch(version) else 'missing or invalid'}",
        f"Chart type: {'valid' if chart_type in ('application', 'library') else 'invalid'}",
        f"Dependency declarations: {len(dependencies):,}",
        f"Invalid dependency declarations: {invalid_dependencies:,}",
        f"Duplicate dependency names/aliases: {duplicate_dependencies:,}",
        f"Maintainer entries: {len(maintainers) if isinstance(maintainers, list) else 0:,}",
        f"Invalid maintainer entries: {invalid_maintainers:,}",
        f"Structural findings: {findings:,}",
        "Privacy: chart name, version values, repository URLs, maintainer details and annotation values are withheld",
        "Scope: checks Chart.yaml metadata only; it does not install dependencies, render templates, validate values.schema.json or connect to Kubernetes",
    ])
