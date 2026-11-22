"""Wave 26 offline bioinformatics format inspectors.

Bounded, read-only parsers for common sequence, variant, annotation, alignment,
assembly-graph and macromolecular-structure formats. They do not perform
clinical interpretation, sequence matching, reference downloads or remote
database lookups. Identifiers, sample names, genomic coordinates, sequences,
read names, protein coordinates and other record-level values are not printed.
"""
from __future__ import annotations

import collections
import gzip
import math
import re
import urllib.parse
from pathlib import Path

MAX_INPUT = 20 * 1024 * 1024
MAX_EXPANDED = 120 * 1024 * 1024
MAX_LINE = 1024 * 1024
MAX_RECORDS = 1_000_000
DNA = set("ACGTRYSWKMBDHVNU")
PROTEIN = set("ABCDEFGHIKLMNPQRSTVWXYZJUO")
IUPAC = DNA | PROTEIN | set("-.?*")


def _report(path: Path, slug: str, heading: str, lines: list[str]) -> dict:
    output = path.with_name(path.stem + "-" + slug + "-report.txt")
    body = heading + "\n\n" + "\n".join(lines) + "\n"
    output.write_text(body, encoding="utf-8")
    return {"summary": body[:5_500], "output_path": str(output)}


def _iter_lines(path: Path, max_expanded: int = MAX_EXPANDED):
    if path.stat().st_size > MAX_INPUT:
        raise RuntimeError("Bioinformatics input exceeds the 20 MiB compressed/file limit.")
    compressed = path.name.lower().endswith(".gz")
    stream = gzip.open(path, "rb") if compressed else path.open("rb")
    total = 0
    line_number = 0
    try:
        while True:
            raw = stream.readline(MAX_LINE + 1)
            if not raw:
                break
            line_number += 1
            total += len(raw)
            if len(raw) > MAX_LINE:
                raise RuntimeError("A bioinformatics input line exceeds the 1 MiB line limit.")
            if total > max_expanded:
                raise RuntimeError("Expanded bioinformatics input exceeds the 120 MiB limit.")
            if b"\x00" in raw:
                raise RuntimeError("A text bioinformatics format contains a NUL byte.")
            try:
                text = raw.decode("utf-8-sig" if line_number == 1 else "utf-8")
            except UnicodeError as exc:
                raise RuntimeError("Bioinformatics text input must be valid UTF-8.") from exc
            yield text.rstrip("\r\n")
    except (OSError, EOFError) as exc:
        raise RuntimeError("Bioinformatics text stream is damaged or has invalid gzip compression.") from exc
    finally:
        stream.close()


def _sequence_invalid(sequence: str, alphabet: set[str]) -> int:
    return sum(1 for char in sequence.upper() if char not in alphabet)


def fasta_sequence_audit(path: Path) -> dict:
    records = total_bases = invalid_symbols = empty_records = preamble_lines = 0
    min_length = None
    max_length = 0
    nucleotide_records = protein_records = mixed_records = 0
    duplicate_ids = 0
    identifiers = set()
    current_id = None
    current_length = 0
    current_dna_only = True
    current_protein_only = True

    def finish_record():
        nonlocal records, total_bases, invalid_symbols, empty_records
        nonlocal min_length, max_length, nucleotide_records, protein_records, mixed_records
        nonlocal current_length, current_dna_only, current_protein_only
        if current_id is None:
            return
        records += 1
        total_bases += current_length
        min_length = current_length if min_length is None else min(min_length, current_length)
        max_length = max(max_length, current_length)
        empty_records += current_length == 0
        if current_dna_only:
            nucleotide_records += 1
        elif current_protein_only:
            protein_records += 1
        else:
            mixed_records += 1
        current_length = 0
        current_dna_only = True
        current_protein_only = True

    for line in _iter_lines(path):
        if not line:
            continue
        if line.startswith(">"):
            finish_record()
            header = line[1:].strip()
            if not header:
                current_id = f"__missing_{records}"
                duplicate_ids += 1
                continue
            current_id = header.split(None, 1)[0]
            if current_id in identifiers:
                duplicate_ids += 1
            identifiers.add(current_id)
        else:
            if current_id is None:
                preamble_lines += 1
                continue
            sequence = "".join(line.split()).upper()
            current_length += len(sequence)
            invalid_symbols += _sequence_invalid(sequence, IUPAC)
            current_dna_only &= bool(sequence) and all(char in DNA | set("-.") for char in sequence)
            current_protein_only &= bool(sequence) and all(char in PROTEIN | set("-.") for char in sequence)
    finish_record()
    if records == 0:
        raise RuntimeError("FASTA input contains no definition line/sequence records.")
    lines = [
        f"FASTA records: {records:,}",
        f"Total sequence symbols: {total_bases:,}",
        f"Minimum record length: {min_length or 0:,}",
        f"Maximum record length: {max_length:,}",
        f"Empty sequence records: {empty_records:,}",
        f"Duplicate/missing sequence identifiers: {duplicate_ids:,}",
        f"Records containing only nucleotide IUPAC symbols: {nucleotide_records:,}",
        f"Records containing only protein symbols: {protein_records:,}",
        f"Mixed/other sequence alphabets: {mixed_records:,}",
        f"Symbols outside the broad IUPAC nucleotide/protein alphabet: {invalid_symbols:,}",
        f"Non-header lines before the first record: {preamble_lines:,}",
        "Sequence identifiers, organism labels, sequence strings and accession values are withheld.",
    ]
    return _report(path, "fasta", "FASTA sequence audit", lines)


def fastq_quality_audit(path: Path) -> dict:
    iterator = iter(_iter_lines(path))
    records = total_bases = quality_chars = invalid_bases = 0
    empty_sequences = malformed_records = plus_id_mismatches = 0
    min_length = None
    max_length = 0
    min_quality_ascii = None
    max_quality_ascii = None
    truncated = 0
    while True:
        try:
            header = next(iterator)
        except StopIteration:
            break
        if not header:
            continue
        if not header.startswith("@"):
            malformed_records += 1
            continue
        identifier = header[1:].strip().split(None, 1)[0] if header[1:].strip() else ""
        sequence_parts = []
        plus_line = None
        for candidate in iterator:
            if candidate.startswith("+"):
                plus_line = candidate
                break
            sequence_parts.append("".join(candidate.split()))
        if plus_line is None:
            truncated += 1
            malformed_records += 1
            break
        sequence = "".join(sequence_parts)
        if not sequence:
            empty_sequences += 1
            malformed_records += 1
        plus_id = plus_line[1:].strip().split(None, 1)[0] if plus_line[1:].strip() else ""
        if plus_id and identifier and plus_id != identifier:
            plus_id_mismatches += 1
        quality_length = 0
        q_min = None
        q_max = None
        quality_overflow = False
        while quality_length < len(sequence):
            try:
                quality_line = next(iterator)
            except StopIteration:
                truncated += 1
                malformed_records += 1
                break
            quality_length += len(quality_line)
            if quality_length > len(sequence):
                quality_overflow = True
            for char in quality_line:
                value = ord(char)
                q_min = value if q_min is None else min(q_min, value)
                q_max = value if q_max is None else max(q_max, value)
        if quality_length != len(sequence) or quality_overflow:
            malformed_records += 1
        if q_min is not None:
            min_quality_ascii = q_min if min_quality_ascii is None else min(min_quality_ascii, q_min)
            max_quality_ascii = q_max if max_quality_ascii is None else max(max_quality_ascii, q_max)
            quality_chars += quality_length
            if q_min < 33 or q_max > 126:
                malformed_records += 1
        records += 1
        total_bases += len(sequence)
        min_length = len(sequence) if min_length is None else min(min_length, len(sequence))
        max_length = max(max_length, len(sequence))
        invalid_bases += _sequence_invalid(sequence, DNA)
        if records > MAX_RECORDS:
            raise RuntimeError("FASTQ exceeds the one-million record limit.")
        if truncated:
            break
    if records == 0:
        raise RuntimeError("FASTQ input contains no complete @/+ read records.")
    lines = [
        f"FASTQ read records: {records:,}",
        f"Total sequence bases: {total_bases:,}",
        f"Total quality characters: {quality_chars:,}",
        f"Minimum read length: {min_length or 0:,}",
        f"Maximum read length: {max_length:,}",
        f"Empty sequence reads: {empty_sequences:,}",
        f"Malformed/truncated records: {malformed_records:,}",
        f"Plus-line identifier mismatches: {plus_id_mismatches:,}",
        f"Sequence symbols outside DNA IUPAC alphabet: {invalid_bases:,}",
        f"Observed quality ASCII range: {min_quality_ascii if min_quality_ascii is not None else 'none'}–{max_quality_ascii if max_quality_ascii is not None else 'none'}",
        "FASTQ has multiple historical quality encodings; the report does not guess a Phred offset or infer sample quality.",
        "Read identifiers, sequence strings, quality strings and sample labels are withheld.",
    ]
    return _report(path, "fastq", "FASTQ read and quality-encoding audit", lines)


def vcf_variant_audit(path: Path) -> dict:
    headers = metadata_lines = contigs = records = malformed = invalid_positions = 0
    sample_count = None
    missing_header = 0
    filters = collections.Counter()
    variant_types = collections.Counter()
    duplicate_keys = set()
    duplicates = multiallelic = missing_genotype_records = 0
    previous_by_contig = {}
    out_of_order = 0

    for line in _iter_lines(path):
        if not line:
            continue
        if line.startswith("##"):
            metadata_lines += 1
            if line.startswith("##contig=<"):
                contigs += 1
            continue
        if line.startswith("#CHROM"):
            if headers:
                malformed += 1
            headers += 1
            columns = line.split("\t")
            if columns[:8] != ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO"]:
                malformed += 1
            sample_count = max(0, len(columns) - 9) if len(columns) >= 9 and columns[8] == "FORMAT" else 0
            if len(columns) > 8 and columns[8] != "FORMAT":
                malformed += 1
            if len(columns) > 9 and columns[8] != "FORMAT":
                malformed += 1
            continue
        if line.startswith("#"):
            malformed += 1
            continue
        if not headers:
            missing_header += 1
            continue
        fields = line.split("\t")
        records += 1
        if len(fields) < 8 or (sample_count and len(fields) != 9 + sample_count):
            malformed += 1
            continue
        position = None
        try:
            position = int(fields[1])
            if position < 1:
                invalid_positions += 1
        except ValueError:
            invalid_positions += 1
        contig = fields[0]
        if position is not None:
            last = previous_by_contig.get(contig)
            if last is not None and position < last:
                out_of_order += 1
            previous_by_contig[contig] = position
        ref = fields[3].upper()
        alts = fields[4].split(",")
        if len(alts) > 1:
            multiallelic += 1
        for alt in alts:
            if alt == ".":
                variant_types["no alternate allele"] += 1
            elif alt == "*":
                variant_types["spanning deletion"] += 1
            elif alt.startswith("<") and alt.endswith(">") or "[" in alt or "]" in alt:
                variant_types["symbolic/breakend"] += 1
            elif len(ref) == len(alt) == 1:
                variant_types["SNV"] += 1
            elif len(ref) == len(alt):
                variant_types["MNV"] += 1
            elif len(ref) != len(alt):
                variant_types["indel"] += 1
            if position is not None:
                key = (contig, position, ref, alt)
                if key in duplicate_keys:
                    duplicates += 1
                duplicate_keys.add(key)
        filters[fields[6] if fields[6] in {"PASS", "."} else "filtered"] += 1
        if sample_count and all(value in {"./.", ".|.", "."} for value in fields[9:]):
            missing_genotype_records += 1
        if records > MAX_RECORDS:
            raise RuntimeError("VCF exceeds the one-million variant record limit.")
    if not headers:
        raise RuntimeError("VCF is missing the #CHROM header line.")
    lines = [
        f"VCF header lines: {headers:,}",
        f"Metadata/header records: {metadata_lines:,}",
        f"Contig declarations: {contigs:,}",
        f"Variant records: {records:,}",
        f"Sample columns (count only): {sample_count or 0:,}",
        f"Multiallelic records: {multiallelic:,}",
        f"Duplicate variant-key rows: {duplicates:,}",
        f"Malformed data/header rows: {malformed:,}",
        f"Rows without a preceding #CHROM header: {missing_header:,}",
        f"Invalid/non-positive positions: {invalid_positions:,}",
        f"Out-of-order positions within a contig: {out_of_order:,}",
        f"Records with only missing genotypes: {missing_genotype_records:,}",
        "Variant categories: " + (", ".join(f"{key}={value}" for key, value in sorted(variant_types.items())) or "none"),
        "Filter categories: " + (", ".join(f"{key}={value}" for key, value in sorted(filters.items())) or "none"),
        "Chromosome names, positions, alleles, sample IDs, genotype calls, INFO annotations and quality values are withheld.",
    ]
    return _report(path, "vcf", "VCF variant-call structure audit", lines)


def sam_alignment_audit(path: Path) -> dict:
    header_counts = collections.Counter()
    reference_declarations = 0
    alignments = malformed = invalid_flags = invalid_positions = 0
    mapped = unmapped = secondary = supplementary = duplicate = qc_failed = paired = 0
    cigar_invalid = sequence_quality_mismatch = mapq_invalid = 0
    min_mapq = None
    max_mapq = None
    for line in _iter_lines(path):
        if not line:
            continue
        if line.startswith("@") and alignments == 0:
            kind = line[:3]
            header_counts[kind] += 1
            if kind == "@SQ":
                reference_declarations += 1
            continue
        fields = line.split("\t")
        alignments += 1
        if len(fields) < 11:
            malformed += 1
            continue
        try:
            flag = int(fields[1])
            if not 0 <= flag <= 65535:
                invalid_flags += 1
        except ValueError:
            invalid_flags += 1
            flag = 0
        try:
            position = int(fields[3])
            if position < 0:
                invalid_positions += 1
        except ValueError:
            invalid_positions += 1
        try:
            mapq = int(fields[4])
            if not 0 <= mapq <= 255:
                mapq_invalid += 1
            else:
                min_mapq = mapq if min_mapq is None else min(min_mapq, mapq)
                max_mapq = mapq if max_mapq is None else max(max_mapq, mapq)
        except ValueError:
            mapq_invalid += 1
        cigar = fields[5]
        if cigar != "*":
            operations = re.findall(r"(\d+)([MIDNSHP=X])", cigar)
            if not operations or "".join(number + operation for number, operation in operations) != cigar:
                cigar_invalid += 1
            else:
                read_consumed = sum(int(number) for number, operation in operations if operation in "MIS=X")
                if fields[9] != "*" and read_consumed != len(fields[9]):
                    cigar_invalid += 1
        if fields[9] != "*" and fields[10] != "*" and len(fields[9]) != len(fields[10]):
            sequence_quality_mismatch += 1
        unmapped += bool(flag & 0x4)
        mapped += not bool(flag & 0x4)
        paired += bool(flag & 0x1)
        secondary += bool(flag & 0x100)
        supplementary += bool(flag & 0x800)
        duplicate += bool(flag & 0x400)
        qc_failed += bool(flag & 0x200)
        if alignments > MAX_RECORDS:
            raise RuntimeError("SAM exceeds the one-million alignment record limit.")
    if alignments == 0:
        raise RuntimeError("SAM contains no alignment records.")
    lines = [
        f"SAM header record categories: " + (", ".join(f"{key}={value}" for key, value in sorted(header_counts.items())) or "none"),
        f"Reference declarations: {reference_declarations:,}",
        f"Alignment records: {alignments:,}",
        f"Mapped records: {mapped:,}",
        f"Unmapped records: {unmapped:,}",
        f"Paired-end records: {paired:,}",
        f"Secondary alignments: {secondary:,}",
        f"Supplementary alignments: {supplementary:,}",
        f"Duplicate-flagged records: {duplicate:,}",
        f"QC-failed records: {qc_failed:,}",
        f"Malformed records: {malformed:,}",
        f"Invalid FLAG values: {invalid_flags:,}",
        f"Invalid POS values: {invalid_positions:,}",
        f"Invalid MAPQ values: {mapq_invalid:,}",
        f"Malformed/CIGAR-length inconsistent records: {cigar_invalid:,}",
        f"SEQ/QUAL length mismatches: {sequence_quality_mismatch:,}",
        f"Observed MAPQ range: {min_mapq if min_mapq is not None else 'none'}–{max_mapq if max_mapq is not None else 'none'}",
        "Read names, reference names, alignment positions, sequences, qualities, optional tags and sample metadata are withheld.",
    ]
    return _report(path, "sam", "SAM alignment record audit", lines)


def gff3_annotation_audit(path: Path) -> dict:
    version_directives = sequence_regions = feature_rows = malformed = 0
    invalid_coordinates = invalid_scores = invalid_strands = invalid_phases = 0
    fasta_sections = fasta_records = directives = comments = 0
    feature_types = collections.Counter()
    identifiers = set()
    duplicate_ids = 0
    parents = set()
    for line in _iter_lines(path):
        if not line:
            continue
        if line == "##FASTA":
            fasta_sections += 1
            continue
        if fasta_sections:
            fasta_records += line.startswith(">")
            continue
        if line.startswith("##"):
            directives += 1
            version_directives += line.startswith("##gff-version")
            sequence_regions += line.startswith("##sequence-region")
            continue
        if line.startswith("#"):
            comments += 1
            continue
        fields = line.split("\t")
        feature_rows += 1
        if len(fields) != 9:
            malformed += 1
            continue
        try:
            start = int(fields[3])
            end = int(fields[4])
            if start < 1 or end < start:
                invalid_coordinates += 1
        except ValueError:
            invalid_coordinates += 1
        if fields[5] != ".":
            try:
                if not math.isfinite(float(fields[5])):
                    invalid_scores += 1
            except ValueError:
                invalid_scores += 1
        if fields[6] not in {"+", "-", ".", "?"}:
            invalid_strands += 1
        if fields[7] not in {"0", "1", "2", "."}:
            invalid_phases += 1
        feature_types[fields[2]] += 1
        attrs = {}
        for attribute in fields[8].split(";"):
            if not attribute:
                continue
            if "=" not in attribute:
                malformed += 1
                continue
            key, value = attribute.split("=", 1)
            attrs[key] = value
        if "ID" in attrs:
            identifier = urllib.parse.unquote(attrs["ID"])
            if identifier in identifiers:
                duplicate_ids += 1
            identifiers.add(identifier)
        if "Parent" in attrs:
            for parent in attrs["Parent"].split(","):
                parents.add(urllib.parse.unquote(parent))
        if feature_rows > MAX_RECORDS:
            raise RuntimeError("GFF3 exceeds the one-million feature record limit.")
    if feature_rows == 0:
        raise RuntimeError("GFF3 input contains no feature rows.")
    missing_parents = sum(1 for parent in parents if parent not in identifiers)
    top_types = sorted(feature_types.items(), key=lambda item: (-item[1], item[0]))[:12]
    lines = [
        f"GFF3 directive count: {directives:,}",
        f"GFF version directives: {version_directives:,}",
        f"Sequence-region declarations: {sequence_regions:,}",
        f"Comment lines: {comments:,}",
        f"Feature rows: {feature_rows:,}",
        f"Feature types (names withheld): {len(feature_types):,}",
        f"Feature rows with malformed attributes/column count: {malformed:,}",
        f"Invalid 1-based coordinates: {invalid_coordinates:,}",
        f"Invalid score values: {invalid_scores:,}",
        f"Invalid strand markers: {invalid_strands:,}",
        f"Invalid CDS phase values: {invalid_phases:,}",
        f"Feature IDs: {len(identifiers):,}",
        f"Duplicate feature IDs: {duplicate_ids:,}",
        f"Distinct parent references: {len(parents):,}",
        f"Parent references without a matching ID in this file: {missing_parents:,}",
        f"Embedded FASTA sections: {fasta_sections:,}",
        f"Embedded FASTA records (count only): {fasta_records:,}",
        "Sequence IDs, feature names/types, coordinates, attributes, gene symbols and embedded sequences are withheld.",
    ]
    return _report(path, "gff3", "GFF3 genomic-feature annotation audit", lines)


def bed_interval_audit(path: Path) -> dict:
    intervals = malformed = invalid_coordinates = zero_length = 0
    extra_columns = thick_range_issues = block_issues = 0
    strand_counts = collections.Counter()
    intervals_by_chromosome = collections.Counter()
    for line in _iter_lines(path):
        if not line or line.startswith(("#", "track ", "browser ")):
            continue
        fields = line.split("\t")
        intervals += 1
        if len(fields) < 3:
            malformed += 1
            continue
        if len(fields) > 12:
            extra_columns += 1
        try:
            start = int(fields[1])
            end = int(fields[2])
            if start < 0 or end < start:
                invalid_coordinates += 1
            if end == start:
                zero_length += 1
        except ValueError:
            invalid_coordinates += 1
            continue
        intervals_by_chromosome[fields[0]] += 1
        if len(fields) >= 6:
            if fields[5] not in {"+", "-", "."}:
                strand_counts["invalid"] += 1
            else:
                strand_counts[fields[5]] += 1
        if len(fields) >= 8:
            try:
                thick_start, thick_end = int(fields[6]), int(fields[7])
                if thick_start < start or thick_end > end or thick_start > thick_end:
                    thick_range_issues += 1
            except ValueError:
                thick_range_issues += 1
        if len(fields) >= 12:
            try:
                block_count = int(fields[9])
                sizes = [int(value) for value in fields[10].rstrip(",").split(",") if value]
                starts = [int(value) for value in fields[11].rstrip(",").split(",") if value]
                if block_count <= 0 or len(sizes) != block_count or len(starts) != block_count:
                    block_issues += 1
                elif any(value <= 0 for value in sizes) or any(value < 0 for value in starts):
                    block_issues += 1
                elif any(start + block_start + size > end for block_start, size in zip(starts, sizes)):
                    block_issues += 1
            except ValueError:
                block_issues += 1
        if intervals > MAX_RECORDS:
            raise RuntimeError("BED exceeds the one-million interval limit.")
    if intervals == 0:
        raise RuntimeError("BED input contains no interval rows.")
    lines = [
        f"BED intervals: {intervals:,}",
        f"Distinct reference-sequence identifiers (count only): {len(intervals_by_chromosome):,}",
        f"Rows with invalid 0-based half-open coordinates: {invalid_coordinates:,}",
        f"Zero-length intervals: {zero_length:,}",
        f"Rows with fewer than three columns: {malformed:,}",
        f"Rows with non-standard additional columns beyond BED12: {extra_columns:,}",
        f"ThickStart/ThickEnd range issues: {thick_range_issues:,}",
        f"BED12 block-count/size/start issues: {block_issues:,}",
        "Strand counts: " + (", ".join(f"{key}={value}" for key, value in sorted(strand_counts.items())) or "none"),
        "Chromosome names, interval coordinates, feature names, scores, RGB colors and annotations are withheld.",
    ]
    return _report(path, "bed", "BED genomic-interval audit", lines)


def genbank_record_audit(path: Path) -> dict:
    records = malformed = missing_terminators = feature_count = qualifier_count = 0
    sequence_bases = empty_sequences = 0
    min_length = None
    max_length = 0
    current = False
    in_features = False
    in_origin = False
    current_sequence_length = 0
    declared_length_mismatches = 0
    declared_length = None

    def finish():
        nonlocal records, malformed, missing_terminators, sequence_bases
        nonlocal min_length, max_length, current_sequence_length, empty_sequences
        nonlocal declared_length_mismatches, declared_length
        if not current:
            return
        records += 1
        sequence_bases += current_sequence_length
        min_length = current_sequence_length if min_length is None else min(min_length, current_sequence_length)
        max_length = max(max_length, current_sequence_length)
        empty_sequences += current_sequence_length == 0
        if declared_length is not None and declared_length != current_sequence_length:
            declared_length_mismatches += 1
        current_sequence_length = 0
        declared_length = None
        in_features_local = False
        _ = in_features_local

    for line in _iter_lines(path):
        if line.startswith("LOCUS"):
            if current:
                finish()
                missing_terminators += 1
            current = True
            in_features = False
            in_origin = False
            parts = line.split()
            declared_length = None
            if len(parts) > 2:
                try:
                    declared_length = int(parts[2])
                except ValueError:
                    malformed += 1
            continue
        if not current:
            if line.strip():
                malformed += 1
            continue
        if line.strip() == "//":
            finish()
            current = False
            in_features = False
            in_origin = False
            continue
        if line.startswith("FEATURES"):
            in_features = True
            in_origin = False
            continue
        if line.startswith("ORIGIN"):
            in_origin = True
            in_features = False
            continue
        if in_features:
            if len(line) >= 21 and line[5:21].strip():
                feature_count += 1
            elif len(line) >= 22 and line[21:].lstrip().startswith("/"):
                qualifier_count += 1
        elif in_origin:
            sequence_part = re.sub(r"[^A-Za-z]", "", line).upper()
            current_sequence_length += len(sequence_part)
            if _sequence_invalid(sequence_part, DNA):
                malformed += 1
        if records > MAX_RECORDS:
            raise RuntimeError("GenBank exceeds the one-million record limit.")
    if current:
        finish()
        missing_terminators += 1
    if records == 0:
        raise RuntimeError("GenBank input contains no LOCUS records.")
    lines = [
        f"GenBank records: {records:,}",
        f"Total sequence bases: {sequence_bases:,}",
        f"Minimum record sequence length: {min_length or 0:,}",
        f"Maximum record sequence length: {max_length:,}",
        f"Records with empty/no ORIGIN sequence: {empty_sequences:,}",
        f"Feature table entries: {feature_count:,}",
        f"Feature qualifier lines: {qualifier_count:,}",
        f"Records missing // terminators: {missing_terminators:,}",
        f"Declared LOCUS length vs ORIGIN sequence mismatches: {declared_length_mismatches:,}",
        f"Other malformed/invalid sequence rows: {malformed:,}",
        "LOCUS names, accession IDs, organism/taxonomy, feature locations, qualifiers and sequence strings are withheld.",
    ]
    return _report(path, "genbank", "GenBank flat-file structure audit", lines)


def pdb_structure_audit(path: Path) -> dict:
    atoms = hetatoms = models = malformed = invalid_coordinates = invalid_occupancy = 0
    altloc_atoms = chains = residues = 0
    elements = collections.Counter()
    residue_keys = set()
    chain_keys = set()
    current_model = 1
    explicit_models = False
    for line in _iter_lines(path):
        record = line[:6].strip().upper()
        if record == "MODEL":
            explicit_models = True
            current_model += 1
            models += 1
            continue
        if record == "ENDMDL":
            continue
        if record not in {"ATOM", "HETATM"}:
            continue
        atoms += record == "ATOM"
        hetatoms += record == "HETATM"
        if len(line) < 54:
            malformed += 1
            continue
        try:
            serial = int(line[6:11].strip())
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
            if not all(math.isfinite(value) for value in (x, y, z)):
                invalid_coordinates += 1
            occupancy = float(line[54:60].strip() or "1") if len(line) >= 60 else 1.0
            if not math.isfinite(occupancy) or occupancy < 0 or occupancy > 1.5:
                invalid_occupancy += 1
            if line[16:17].strip():
                altloc_atoms += 1
            chain = line[21:22]
            chain_keys.add((current_model, chain))
            residue_keys.add((current_model, chain, line[22:27], line[17:20]))
            element = line[76:78].strip().upper() if len(line) >= 78 else ""
            if element:
                elements[element] += 1
        except ValueError:
            malformed += 1
        if atoms + hetatoms > MAX_RECORDS:
            raise RuntimeError("PDB exceeds the one-million coordinate-record limit.")
    if atoms + hetatoms == 0:
        raise RuntimeError("PDB input contains no ATOM/HETATM coordinate records.")
    models = models if explicit_models else 1
    lines = [
        f"PDB coordinate models: {models:,}",
        f"ATOM records: {atoms:,}",
        f"HETATM records: {hetatoms:,}",
        f"Distinct model/chain pairs: {len(chain_keys):,}",
        f"Distinct model/chain/residue keys: {len(residue_keys):,}",
        f"Alternate-location atom records: {altloc_atoms:,}",
        f"Malformed coordinate records: {malformed:,}",
        f"Invalid/non-finite coordinate tuples: {invalid_coordinates:,}",
        f"Occupancy values outside the broad 0..1.5 check: {invalid_occupancy:,}",
        "Element counts: " + (", ".join(f"{key}={value}" for key, value in sorted(elements.items())) or "none"),
        "Atom/residue/chain identifiers, structure titles, coordinates, sequences and experimental metadata are withheld.",
    ]
    return _report(path, "pdb", "PDB macromolecular coordinate audit", lines)


def gfa_assembly_audit(path: Path) -> dict:
    records = collections.Counter()
    segments = set()
    references = set()
    segment_bases = known_length_segments = unknown_length_segments = 0
    malformed = duplicate_segments = 0
    version_headers = 0
    for line in _iter_lines(path):
        if not line:
            continue
        fields = line.split("\t")
        kind = fields[0]
        records[kind] += 1
        if kind == "H":
            version_headers += 1
        elif kind == "S":
            if len(fields) < 3:
                malformed += 1
                continue
            identifier = fields[1]
            if identifier in segments:
                duplicate_segments += 1
            segments.add(identifier)
            if len(fields) >= 4 and fields[2].isdigit():
                length = int(fields[2])
                known_length_segments += 1
                segment_bases += length
            elif fields[2] == "*":
                unknown_length_segments += 1
            else:
                known_length_segments += 1
                segment_bases += len(fields[2])
        elif kind == "L":
            if len(fields) < 6:
                malformed += 1
                continue
            references.update((fields[1], fields[3]))
        elif kind == "C":
            if len(fields) < 8:
                malformed += 1
                continue
            references.update((fields[1], fields[3]))
        elif kind == "P":
            if len(fields) < 3:
                malformed += 1
                continue
            for component in fields[2].split(","):
                if component:
                    references.add(component.rstrip("+-"))
        elif kind == "W":
            if len(fields) < 7:
                malformed += 1
                continue
            walk = fields[6]
            references.update(re.findall(r"[><]([^><]+)", walk))
        elif kind == "E":
            if len(fields) < 9:
                malformed += 1
                continue
            references.update((fields[2].rstrip("+-"), fields[3].rstrip("+-")))
        elif kind in {"G", "O", "U"}:
            if kind == "O" and len(fields) >= 3:
                references.update(component.rstrip("+-") for component in fields[2].split())
        else:
            malformed += 1
        if sum(records.values()) > MAX_RECORDS:
            raise RuntimeError("GFA exceeds the one-million record limit.")
    if not segments:
        raise RuntimeError("GFA input contains no S segment records.")
    missing_references = sum(1 for identifier in references if identifier not in segments)
    lines = [
        f"GFA records: {sum(records.values()):,}",
        f"Segment records: {len(segments):,}",
        f"Duplicate segment identifiers: {duplicate_segments:,}",
        f"Known segment-length records: {known_length_segments:,}",
        f"Segments with unknown sequence/length: {unknown_length_segments:,}",
        f"Declared/observed segment bases (count only): {segment_bases:,}",
        f"Distinct segment references: {len(references):,}",
        f"References without an S segment: {missing_references:,}",
        f"Header records: {version_headers:,}",
        f"Malformed/unsupported records: {malformed:,}",
        "Record categories: " + (", ".join(f"{key}={value}" for key, value in sorted(records.items())) or "none"),
        "Segment IDs, read/sequence strings, path names, sample/haplotype fields, overlap CIGARs and graph labels are withheld.",
    ]
    return _report(path, "gfa", "GFA genome assembly graph audit", lines)


def _newick_tokens(text: str):
    index = 0
    length = len(text)
    delimiters = set("(),:;[]")
    while index < length:
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char == "[":
            depth = 1
            index += 1
            while index < length and depth:
                if text[index] == "[":
                    depth += 1
                elif text[index] == "]":
                    depth -= 1
                index += 1
            if depth:
                raise RuntimeError("Newick comment is not closed.")
            continue
        if char in "(),:;":
            yield char
            index += 1
            continue
        if char == "'":
            index += 1
            value = []
            while index < length:
                if text[index] == "'":
                    if index + 1 < length and text[index + 1] == "'":
                        value.append("'")
                        index += 2
                        continue
                    index += 1
                    break
                value.append(text[index])
                index += 1
            else:
                raise RuntimeError("Newick quoted label is not closed.")
            yield ("label", "".join(value))
            continue
        start = index
        while index < length and not text[index].isspace() and text[index] not in delimiters:
            index += 1
        if index == start:
            raise RuntimeError("Newick contains an unexpected token.")
        yield ("label", text[start:index])


def newick_tree_audit(path: Path) -> dict:
    chunks = []
    total = 0
    for line in _iter_lines(path):
        chunks.append(line)
        total += len(line) + 1
        if total > MAX_TEXT:
            raise RuntimeError("Newick text exceeds the 10 MiB parser limit.")
    text = "\n".join(chunks)
    stack = []
    trees = leaves = internal_nodes = branches = invalid_lengths = malformed = missing_terminators = 0
    expecting_subtree = True
    last_complete = False
    after_close = False
    started = False
    tokens = list(_newick_tokens(text))
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if token == "(":
            if not expecting_subtree:
                malformed += 1
            stack.append(0)
            expecting_subtree = True
            last_complete = False
            after_close = False
            started = True
        elif token == ",":
            if not stack or not last_complete:
                malformed += 1
            else:
                stack[-1] += 1
                expecting_subtree = True
                last_complete = False
                after_close = False
        elif token == ")":
            if not stack or expecting_subtree or not last_complete:
                malformed += 1
            else:
                stack[-1] += 1
                if stack[-1] < 2:
                    malformed += 1
                stack.pop()
                internal_nodes += 1
                expecting_subtree = False
                last_complete = True
                after_close = True
        elif token == ":":
            if not last_complete or index >= len(tokens):
                malformed += 1
                continue
            value = tokens[index]
            index += 1
            try:
                if not isinstance(value, tuple):
                    raise ValueError
                branch_length = float(value[1])
                if not math.isfinite(branch_length) or branch_length < 0:
                    invalid_lengths += 1
            except (ValueError, TypeError):
                invalid_lengths += 1
            branches += 1
        elif token == ";":
            if stack or not last_complete or expecting_subtree:
                malformed += 1
                stack.clear()
            else:
                trees += 1
            expecting_subtree = True
            last_complete = False
            after_close = False
            started = False
        else:
            if isinstance(token, tuple) and token[0] == "label":
                if expecting_subtree:
                    leaves += 1
                    expecting_subtree = False
                    last_complete = True
                    after_close = False
                    started = True
                elif after_close:
                    after_close = False
                else:
                    malformed += 1
    if stack:
        malformed += 1
    if last_complete and not stack:
        missing_terminators += 1
        trees += 1
    if trees == 0:
        raise RuntimeError("Newick input contains no complete tree.")
    lines = [
        f"Trees parsed: {trees:,}",
        f"Leaf/tip labels: {leaves:,}",
        f"Internal nodes: {internal_nodes:,}",
        f"Branch-length fields: {branches:,}",
        f"Invalid/negative branch lengths: {invalid_lengths:,}",
        f"Malformed tree syntax events: {malformed:,}",
        f"Trees missing a final semicolon: {missing_terminators:,}",
        "Tree labels, taxon names, branch lengths and annotations are not exposed.",
    ]
    return _report(path, "newick", "Newick phylogenetic tree audit", lines)


def sequence_alignment_audit(path: Path) -> dict:
    lines = list(_iter_lines(path, max_expanded=MAX_TEXT))
    nonempty = [line for line in lines if line.strip()]
    if not nonempty:
        raise RuntimeError("Alignment input is empty.")
    first = nonempty[0].strip().upper()
    format_name = "unknown"
    sequence_lengths = collections.defaultdict(int)
    malformed = comments = block_count = 0
    if first.startswith("CLUSTAL") or first.startswith("MUSCLE"):
        format_name = "Clustal/MUSCLE"
        if not lines or not lines[0].strip().upper().startswith(("CLUSTAL", "MUSCLE")):
            malformed += 1
        for line in lines[1:]:
            if not line.strip():
                block_count += 1
                continue
            if line[0].isspace() and re.fullmatch(r"[\s.*:]+", line):
                continue
            if line.lstrip().startswith("#"):
                comments += 1
                continue
            fields = line.split()
            if len(fields) >= 2 and re.fullmatch(r"[A-Za-z.*?-]+", fields[1]):
                sequence_lengths[fields[0]] += len(fields[1])
            else:
                malformed += 1
    elif first.startswith("# STOCKHOLM"):
        format_name = "Stockholm"
        terminators = 0
        for line in lines:
            stripped = line.strip()
            if not stripped:
                block_count += 1
                continue
            if stripped == "//":
                terminators += 1
                continue
            if stripped.startswith("#"):
                comments += 1
                continue
            fields = stripped.split()
            if len(fields) == 2 and re.fullmatch(r"[A-Za-z.*?~-]+", fields[1]):
                sequence_lengths[fields[0]] += len(fields[1])
            else:
                malformed += 1
        if terminators == 0:
            malformed += 1
    else:
        raise RuntimeError("Alignment format is not recognized as Clustal/MUSCLE or Stockholm.")
    if not sequence_lengths:
        raise RuntimeError("Alignment contains no parseable sequence rows.")
    unique_lengths = set(sequence_lengths.values())
    unequal_lengths = int(len(unique_lengths) > 1)
    lines_out = [
        f"Alignment format: {format_name}",
        f"Distinct sequence rows: {len(sequence_lengths):,}",
        f"Total aligned symbols: {sum(sequence_lengths.values()):,}",
        f"Minimum aligned row length: {min(sequence_lengths.values()):,}",
        f"Maximum aligned row length: {max(sequence_lengths.values()):,}",
        f"Unequal row lengths detected: {unequal_lengths}",
        f"Blank block separators: {block_count:,}",
        f"Comment/annotation lines: {comments:,}",
        f"Malformed/unsupported lines: {malformed:,}",
        "Sequence identifiers, aligned characters, annotations and consensus text are withheld.",
    ]
    return _report(path, "alignment", "Multiple sequence alignment audit", lines)
