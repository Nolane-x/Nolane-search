"""Wave 32: searchable OCR PDFs, RDF graphs, SHACL and cron previews.

All inputs are processed locally on disposable GitHub-hosted runners. RDF parsing
is deliberately limited to offline text syntaxes; SHACL SPARQL/JS extensions,
remote imports and external ontology loading are disabled.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile
import stat

from wave28 import _report, _size_guard


MAX_RDF_BYTES = 5 * 1024 * 1024
MAX_RDF_TRIPLES = 50_000
MAX_SHACL_ZIP_BYTES = 5 * 1024 * 1024
MAX_SHACL_MEMBER_BYTES = 2 * 1024 * 1024
MAX_SHACL_DATA_TRIPLES = 50_000
MAX_SHACL_SHAPE_TRIPLES = 10_000
MAX_CRON_BYTES = 2 * 1024 * 1024
MAX_CRON_SCHEDULES = 1_000
MAX_PDF_OUTPUT_BYTES = 45 * 1024 * 1024
PDF_OCR_TIMEOUT_SECONDS = 20 * 60

RDF_FORMATS = {
    ".ttl": "turtle",
    ".nt": "nt",
    ".nq": "nquads",
    ".trig": "trig",
}


def rdf_graph_audit(path: Path) -> dict:
    """Profile an RDF graph/dataset without exposing any graph terms or values."""
    if path.stat().st_size > MAX_RDF_BYTES:
        raise RuntimeError("RDF input exceeds the 5 MiB limit.")
    rdf_format = RDF_FORMATS.get(path.suffix.lower())
    if not rdf_format:
        raise RuntimeError("Supported RDF uploads are Turtle, N-Triples, N-Quads and TriG.")

    try:
        from rdflib import BNode, Dataset, Literal

        dataset = Dataset()
        dataset.parse(location=str(path), format=rdf_format)
        default_graph_id = dataset.default_graph.identifier
        subjects = set()
        predicates = set()
        named_graphs = set()
        blank_nodes = set()
        triple_count = literal_count = 0
        for subject, predicate, obj, graph_id in dataset.quads((None, None, None, None)):
            triple_count += 1
            if triple_count > MAX_RDF_TRIPLES:
                raise RuntimeError("RDF graph exceeds the 50,000-triple processing limit.")
            subjects.add(subject)
            predicates.add(predicate)
            if isinstance(obj, Literal):
                literal_count += 1
            if isinstance(subject, BNode):
                blank_nodes.add(subject)
            if isinstance(obj, BNode):
                blank_nodes.add(obj)
            if graph_id != default_graph_id:
                named_graphs.add(graph_id)
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("RDF input could not be parsed using its declared syntax.") from exc

    try:
        namespace_count = sum(1 for _ in dataset.namespaces())
    except Exception:
        namespace_count = 0

    return _report(path, "rdf-graph-audit", "RDF graph / dataset profile", [
        f"Syntax: {rdf_format}",
        f"Triples/quads inspected: {triple_count:,}",
        f"Distinct subjects: {len(subjects):,}",
        f"Distinct predicates: {len(predicates):,}",
        f"Literal objects: {literal_count:,}",
        f"Distinct blank nodes: {len(blank_nodes):,}",
        f"Named graphs: {len(named_graphs):,}",
        f"Namespace bindings: {namespace_count:,}",
        "Privacy: graph IRIs, subjects, predicates, literal values, labels and file paths are not included.",
        "Scope: local RDF parsing only; this report does not dereference URLs, load remote contexts or certify ontology semantics.",
    ])


def _read_shacl_package(path: Path) -> tuple[str, str]:
    if path.stat().st_size > MAX_SHACL_ZIP_BYTES:
        raise RuntimeError("SHACL package exceeds the 5 MiB ZIP limit.")
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if len(infos) != 2 or {item.filename for item in infos} != {"data.ttl", "shapes.ttl"}:
                raise RuntimeError("SHACL ZIP must contain exactly data.ttl and shapes.ttl at its root.")
            contents = {}
            for item in infos:
                mode = (item.external_attr >> 16) & 0xFFFF
                if stat.S_ISLNK(mode) or item.is_dir() or item.flag_bits & 0x1:
                    raise RuntimeError("SHACL package contains an unsupported or encrypted entry.")
                if item.file_size <= 0 or item.file_size > MAX_SHACL_MEMBER_BYTES:
                    raise RuntimeError("Each SHACL Turtle file must be between 1 byte and 2 MiB.")
                if item.compress_size == 0 or item.file_size / item.compress_size > 200:
                    raise RuntimeError("SHACL package compression ratio exceeds the safety limit.")
                contents[item.filename] = archive.read(item).decode("utf-8")
    except RuntimeError:
        raise
    except (OSError, zipfile.BadZipFile, UnicodeDecodeError, RuntimeError) as exc:
        raise RuntimeError("SHACL package is not a valid UTF-8 ZIP containing the required Turtle files.") from exc
    return contents["data.ttl"], contents["shapes.ttl"]


def shacl_validate(path: Path) -> dict:
    """Validate data.ttl against shapes.ttl in a bounded, offline SHACL Core package."""
    _size_guard(path)
    data_text, shapes_text = _read_shacl_package(path)
    try:
        from rdflib import Graph
        from rdflib.namespace import OWL, SH

        data_graph = Graph()
        shapes_graph = Graph()
        data_graph.parse(data=data_text, format="turtle")
        shapes_graph.parse(data=shapes_text, format="turtle")
        if len(data_graph) > MAX_SHACL_DATA_TRIPLES:
            raise RuntimeError("SHACL data graph exceeds the 50,000-triple limit.")
        if len(shapes_graph) > MAX_SHACL_SHAPE_TRIPLES:
            raise RuntimeError("SHACL shapes graph exceeds the 10,000-triple limit.")
        forbidden_predicates = (OWL.imports, SH.sparql, SH.select, SH.js, SH.rule)
        if any((None, predicate, None) in shapes_graph for predicate in forbidden_predicates):
            raise RuntimeError("SHACL package uses remote-import, SPARQL, JavaScript or rule extensions that are disabled.")
        if (None, OWL.imports, None) in data_graph:
            raise RuntimeError("RDF data graph cannot request remote ontology imports.")
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("SHACL package contains invalid Turtle data or shapes.") from exc

    try:
        from pyshacl import validate

        conforms, report_graph, _private_report_text = validate(
            data_graph,
            shacl_graph=shapes_graph,
            inference="none",
            abort_on_first=False,
            allow_infos=True,
            allow_warnings=True,
            meta_shacl=True,
            advanced=False,
            js=False,
            inplace=False,
        )
    except Exception as exc:
        raise RuntimeError("SHACL validation failed safely; raw validator diagnostics are withheld.") from exc

    from rdflib.namespace import RDF, SH

    result_nodes = set(report_graph.subjects(RDF.type, SH.ValidationResult))
    severities = Counter()
    components = Counter()
    for node in result_nodes:
        severity = report_graph.value(node, SH.resultSeverity)
        component = report_graph.value(node, SH.sourceConstraintComponent)
        if severity is not None:
            severities[str(severity).rsplit("#", 1)[-1]] += 1
        if component is not None:
            components[str(component).rsplit("#", 1)[-1]] += 1

    severity_lines = [
        f"  {name}: {count:,}"
        for name, count in sorted(severities.items())
    ] or ["  none"]
    component_lines = [
        f"  {name}: {count:,}"
        for name, count in components.most_common(8)
    ] or ["  none"]
    return _report(path, "shacl-validation", "SHACL Core validation report", [
        f"Conforms: {'yes' if conforms else 'no'}",
        f"Data triples: {len(data_graph):,}",
        f"Shape triples: {len(shapes_graph):,}",
        f"Validation results: {len(result_nodes):,}",
        "Result severities:",
        *severity_lines,
        "Most frequent constraint components (counts only):",
        *component_lines,
        "Privacy: focus nodes, RDF terms, literal values, result paths, messages and source identifiers are withheld.",
        "Scope: SHACL Core only; no remote imports, SPARQL constraints, JavaScript constraints, custom rules or inference are executed.",
    ])


def cron_schedule_audit(path: Path, base: datetime | None = None) -> dict:
    """Validate one five-field cron expression per line and preview UTC occurrences."""
    if path.stat().st_size > MAX_CRON_BYTES:
        raise RuntimeError("Cron input exceeds the 2 MiB limit.")
    try:
        from croniter import croniter
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise RuntimeError("Cron input must be UTF-8 text.") from exc

    reference = base or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    reference = reference.astimezone(timezone.utc).replace(second=0, microsecond=0)

    rows = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        candidate = raw.strip()
        if not candidate or candidate.startswith("#"):
            continue
        rows.append((line_number, candidate))
        if len(rows) > MAX_CRON_SCHEDULES:
            raise RuntimeError("Cron input exceeds the 1,000-schedule limit.")

    valid_count = invalid_count = 0
    samples = []
    for line_number, expression in rows[:100]:
        # Accept exactly the five standard minute/hour/day/month/weekday fields.
        if len(expression.split()) != 5 or not croniter.is_valid(expression):
            invalid_count += 1
            samples.append(f"Line {line_number}: invalid five-field expression.")
            continue
        try:
            iterator = croniter(expression, reference)
            occurrences = []
            for _ in range(3):
                next_run = iterator.get_next(datetime)
                if next_run.tzinfo is None:
                    next_run = next_run.replace(tzinfo=timezone.utc)
                occurrences.append(next_run.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
        except Exception:
            invalid_count += 1
            samples.append(f"Line {line_number}: valid syntax, but no safe next-run preview could be calculated.")
            continue
        valid_count += 1
        samples.append(f"Line {line_number}: valid; next runs: " + " · ".join(occurrences))

    remaining = max(0, len(rows) - 100)
    return _report(path, "cron-schedule-audit", "Cron schedule preview (UTC)", [
        f"Schedules inspected: {min(len(rows), 100):,}",
        f"Valid schedules: {valid_count:,}",
        f"Invalid schedules: {invalid_count:,}",
        f"Additional schedules not previewed: {remaining:,}",
        *samples,
        "Privacy and execution boundary: cron expressions and any command text are not echoed; no commands are executed and no schedules are created.",
        "Timezone boundary: previews are UTC and do not infer a target server's local timezone, DST policy or scheduler-specific extensions.",
    ])


def pdf_ocr_searchable(path: Path) -> dict:
    """Create a searchable PDF with OCRmyPDF while keeping temporary names neutral."""
    _size_guard(path)
    if path.suffix.lower() != ".pdf":
        raise RuntimeError("Searchable-PDF OCR accepts PDF files only.")

    destination = path.with_name(path.stem + "-searchable.pdf")
    if destination.exists() or destination.is_symlink():
        raise RuntimeError("A searchable-PDF output with this name already exists.")
    try:
        with tempfile.TemporaryDirectory(prefix="nolane-pdf-ocr-") as temp:
            work = Path(temp)
            input_file = work / "input.pdf"
            output_file = work / "output.pdf"
            shutil.copyfile(path, input_file)
            command = [
                sys.executable, "-m", "ocrmypdf",
                "--skip-text",
                "--rotate-pages",
                "--deskew",
                "--language", "eng+vie",
                "--output-type", "pdf",
                "--jobs", "2",
                "--optimize", "0",
                "input.pdf",
                "output.pdf",
            ]
            try:
                result = subprocess.run(
                    command,
                    cwd=work,
                    capture_output=True,
                    text=True,
                    timeout=PDF_OCR_TIMEOUT_SECONDS,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError("Searchable-PDF OCR exceeded the 20-minute processing limit.") from exc
            except OSError as exc:
                raise RuntimeError("OCRmyPDF or its required local OCR engine is unavailable.") from exc
            if result.returncode != 0:
                raise RuntimeError("OCRmyPDF could not process this PDF; diagnostic output is withheld.")
            if not output_file.is_file() or output_file.is_symlink():
                raise RuntimeError("OCRmyPDF did not produce a valid output file.")
            output_size = output_file.stat().st_size
            if output_size <= 5 or output_size > MAX_PDF_OUTPUT_BYTES:
                raise RuntimeError("Searchable PDF output is empty or exceeds the 45 MiB delivery limit.")
            with output_file.open("rb") as check:
                if check.read(5) != b"%PDF-":
                    raise RuntimeError("OCRmyPDF output does not have a valid PDF signature.")
            shutil.copyfile(output_file, destination)
    except RuntimeError:
        destination.unlink(missing_ok=True)
        raise
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise RuntimeError("Searchable-PDF OCR failed safely.") from exc

    return {
        "summary": (
            "Created a searchable PDF with an OCR text layer. "
            "Languages: English + Vietnamese. Existing text pages are skipped; "
            "automatic rotation and deskew are enabled. Output is a standard PDF, not PDF/A."
        ),
        "output_path": str(destination),
    }
