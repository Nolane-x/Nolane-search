# Wave 26 handoff — 2026-11-22

## Release status — deployed 2026-11-22

- PR: [#78](https://github.com/Nolane-x/Nolane-search/pull/78), merged into main.
- Production commit: fd60df0480a82775e6ba6974e386096fa58f6a0c.
- Catalog: **417 production tools**, up from 406; +11 processors.
- Main CI [45030758881](https://github.com/Nolane-x/Nolane-search/actions/runs/45030758881): success; 25 Vitest files and 229 Python runner tests passed.
- Worker export/health smoke [45030758769](https://github.com/Nolane-x/Nolane-search/actions/runs/45030758769): success.
- Cloudflare deploy [45030758729](https://github.com/Nolane-x/Nolane-search/actions/runs/45030758729): success; Telegram webhook and command menu registered; D1 migration skipped (no schema change).
- Cloudflare confirms Worker Version 83 (a0d66d94-083a-46fa-af0b-1237e435a478) receives 100% traffic; deployment ID 95d12888-5427-4ac6-bb98-3bf4cb40fe89.

## Added processors

| ID | Format/domain | Primary checks |
|---|---|---|
| `fasta-sequence-audit` | FASTA | Records, sequence lengths, broad IUPAC alphabet, duplicate IDs and empty records. |
| `fastq-quality-audit` | FASTQ | Wrapped read/quality records, exact lengths, separators and quality ASCII range; no guessed Phred offset. |
| `vcf-variant-audit` | VCF v4.x | Header/column width, positions, allele classes, sample count, multiallelic rows and ordering. |
| `sam-alignment-audit` | SAM | Headers, flags, MAPQ/POS, CIGAR-vs-SEQ and SEQ/QUAL length checks. |
| `gff3-annotation-audit` | GFF3/GTF | Nine columns, coordinates, strand/phase, attributes and Parent references. |
| `bed-interval-audit` | BED | 0-based half-open coordinates and BED3–BED12 thick/block validation. |
| `genbank-record-audit` | GenBank | LOCUS/FEATURES/ORIGIN, feature/qualifier counts and record terminators. |
| `pdb-structure-audit` | PDB | MODEL/ATOM/HETATM, model/chain/residue counts and coordinate/occupancy parseability. |
| `gfa-assembly-audit` | GFA 1/1.1/2 | Record categories, segments, links, paths/walks and dangling segment references. |
| `newick-tree-audit` | Newick | Trees, leaves, internal nodes, branch-length fields, comments and syntax markers. |
| `sequence-alignment-audit` | Clustal/MUSCLE/Stockholm | Sequence rows, aligned lengths, blocks, annotations and unequal-length detection. |

## Implementation map

- New parser module: `tools/wave26.py`.
- New isolated regression suite: `tools/test_wave26.py` (23 tests).
- Runner imports, RUNNERS, handler dispatch, TEXT_OUTPUT_TOOLS and pipeline transitions: `tools/runner.py`.
- TypeScript catalog, pipeline transitions and upload inference: `src/tools.ts`.
- Registry/upload-inference tests and Telegram Tool Center count: `tests/tools.test.ts`, `tests/telegram.test.ts`.
- Research sources, limitations and privacy note: `docs/TOOL-RESEARCH-2026-11-22.md`, `docs/NOLANE-TOOLS.md`, `docs/STATUS.md`.

## Privacy and bounds

- Reports withhold sequences, read IDs, sample/genotype identifiers, genomic coordinates, gene/accession labels, PDB atom coordinates, GFA graph identifiers and phylogenetic taxon labels.
- Source files themselves still pass through the configured ephemeral GitHub-hosted runner; summary redaction is not equivalent to source-file de-identification. Do not upload patient/clinical data without authorization.
- Plain `.vcf` can be a vCard. Upload inference requires genomic MIME or `.vcf.gz`; MIME `text/vcard` keeps the vCard processor. Use `/tool vcf-variant-audit` to select plain genomic VCF explicitly.
- Input limit 20 MiB; gzip expanded limit 120 MiB; line limit 1 MiB; record cap one million; Newick/alignment text cap 10 MiB.
- Standard-library only; no new third-party runtime dependency, database schema or external lookups.
- These processors are structural diagnostics, not clinical interpretation, variant annotation, read alignment, sequence alignment, gene prediction, phylogenetic inference or full structural-biology validation.

## Release gates

1. Verify 417 unique IDs in TypeScript catalog, Python RUNNERS allowlist and Python handler map.
2. Type-check, Vitest, Python compile and full runner unittest discovery.
3. Worker build/export and deployed `/health` smoke.
4. Cloudflare deployment, runtime-secret upload, webhook and command registration.
5. Owner-level Telegram E2E using synthetic/non-sensitive examples and `/tool_retry`.

Wave 26 is production. Remaining work is owner-level Telegram E2E using synthetic/non-sensitive examples and /tool_retry; do not infer successful uploads solely from CI and deployment evidence.