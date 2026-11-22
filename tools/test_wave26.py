from __future__ import annotations

import gzip
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wave26


class Wave26BioinformaticsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def write_gzip(self, name: str, content: str) -> Path:
        path = self.root / name
        with gzip.open(path, "wt", encoding="utf-8") as stream:
            stream.write(content)
        return path

    def assert_report(self, result):
        self.assertTrue(Path(result["output_path"]).is_file())
        self.assertIn("audit", result["summary"].lower())

    def test_fasta_audit_counts_nucleotide_and_protein_records_without_headers(self):
        source = ">secret-nucleotide [organism=private]\nACGTNRY\n>secret-protein\nEFILPQM\n"
        result = wave26.fasta_sequence_audit(self.write("records.fasta", source))
        self.assert_report(result)
        self.assertIn("FASTA records: 2", result["summary"])
        self.assertIn("Total sequence symbols: 14", result["summary"])
        self.assertIn("Records containing only nucleotide IUPAC symbols: 1", result["summary"])
        self.assertIn("Records containing only protein symbols: 1", result["summary"])
        self.assertNotIn("secret-nucleotide", result["summary"])
        self.assertNotIn("ACGTNRY", result["summary"])
        self.assertNotIn("private", result["summary"])

    def test_fasta_audit_detects_duplicate_ids_empty_records_and_preamble(self):
        source = "preamble\n>same\n>same\nACGT?\n"
        result = wave26.fasta_sequence_audit(self.write("odd.fa", source))
        self.assert_report(result)
        self.assertIn("Duplicate/missing sequence identifiers: 1", result["summary"])
        self.assertIn("Empty sequence records: 1", result["summary"])
        self.assertIn("Non-header lines before the first record: 1", result["summary"])

    def test_fasta_audit_rejects_files_without_records(self):
        with self.assertRaisesRegex(RuntimeError, "no definition line"):
            wave26.fasta_sequence_audit(self.write("empty.fa", "ACGT\n"))

    def test_fastq_audit_counts_reads_and_quality_range_without_read_content(self):
        source = "@private-read-1 length=4\nACGT\n+private-read-1\n!!!!\n@private-read-2\nAANN\n+\n####\n"
        result = wave26.fastq_quality_audit(self.write("reads.fastq", source))
        self.assert_report(result)
        self.assertIn("FASTQ read records: 2", result["summary"])
        self.assertIn("Total sequence bases: 8", result["summary"])
        self.assertIn("Observed quality ASCII range: 33–35", result["summary"])
        self.assertNotIn("private-read", result["summary"])
        self.assertNotIn("ACGT", result["summary"])
        self.assertNotIn("!!!!", result["summary"])

    def test_fastq_audit_supports_wrapped_sequence_quality_and_flags_mismatch(self):
        source = "@read1\nAC\nGT\n+read1\n!!\n!!\n@read2\nAC\n+\n!!!\n"
        result = wave26.fastq_quality_audit(self.write("wrapped.fq", source))
        self.assert_report(result)
        self.assertIn("FASTQ read records: 2", result["summary"])
        self.assertIn("Malformed/truncated records: 1", result["summary"])
        self.assertIn("Plus-line identifier mismatches: 0", result["summary"])

    def test_fastq_audit_reads_gzip_stream(self):
        source = "@read\nACGT\n+\n!!!!\n"
        result = wave26.fastq_quality_audit(self.write_gzip("reads.fastq.gz", source))
        self.assert_report(result)
        self.assertIn("FASTQ read records: 1", result["summary"])

    def test_vcf_audit_counts_variants_samples_and_types_without_coordinates(self):
        source = """##fileformat=VCFv4.5
##contig=<ID=private-contig,length=1000>
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tsecret-sample
private-contig\t10\trs-secret\tA\tT\t50\tPASS\t.\tGT\t0/1
private-contig\t20\tprivate-id\tC\tG,CT\t.\tLowQual\t.\tGT\t./.
"""
        result = wave26.vcf_variant_audit(self.write("variants.vcf", source))
        self.assert_report(result)
        self.assertIn("Variant records: 2", result["summary"])
        self.assertIn("Sample columns (count only): 1", result["summary"])
        self.assertIn("Multiallelic records: 1", result["summary"])
        self.assertIn("SNV=1", result["summary"])
        self.assertIn("indel=1", result["summary"])
        self.assertIn("Records with only missing genotypes: 1", result["summary"])
        self.assertNotIn("secret-contig", result["summary"])
        self.assertNotIn("secret-sample", result["summary"])
        self.assertNotIn("rs-secret", result["summary"])

    def test_vcf_audit_rejects_missing_header(self):
        with self.assertRaisesRegex(RuntimeError, "missing the #CHROM"):
            wave26.vcf_variant_audit(self.write("bad.vcf", "chr1\t1\t.\tA\tT\t.\tPASS\t.\n"))

    def test_vcf_audit_reads_gzip_and_detects_row_width(self):
        source = "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\nchr1\t1\t.\tA\tT\t.\tPASS\t.\textra\n"
        result = wave26.vcf_variant_audit(self.write_gzip("variants.vcf.gz", source))
        self.assert_report(result)
        self.assertIn("Malformed data/header rows: 1", result["summary"])

    def test_sam_audit_counts_mapping_flags_and_hides_read_fields(self):
        source = """@HD\tVN:1.6\tSO:coordinate
@SQ\tSN:private-ref\tLN:1000
private-read\t0\tprivate-ref\t1\t60\t4M\t*\t0\t0\tACGT\t!!!!
unmapped-read\t4\t*\t0\t0\t*\t*\t0\t0\t*\t*
"""
        result = wave26.sam_alignment_audit(self.write("alignments.sam", source))
        self.assert_report(result)
        self.assertIn("Alignment records: 2", result["summary"])
        self.assertIn("Mapped records: 1", result["summary"])
        self.assertIn("Unmapped records: 1", result["summary"])
        self.assertIn("Reference declarations: 1", result["summary"])
        self.assertNotIn("private-read", result["summary"])
        self.assertNotIn("private-ref", result["summary"])
        self.assertNotIn("ACGT", result["summary"])

    def test_sam_audit_detects_invalid_cigar_and_sequence_quality_lengths(self):
        source = "r1\t0\tref\t1\t30\t2Mgarbage\t*\t0\t0\tACGT\t!!!\n"
        result = wave26.sam_alignment_audit(self.write("bad.sam", source))
        self.assert_report(result)
        self.assertIn("Malformed/CIGAR-length inconsistent records: 1", result["summary"])
        self.assertIn("SEQ/QUAL length mismatches: 1", result["summary"])

    def test_gff3_audit_checks_attributes_parent_references_and_embedded_fasta(self):
        source = """##gff-version 3
##sequence-region secret-contig 1 1000
secret-contig\t.\tgene\t1\t100\t.\t+\t.\tID=gene-private
secret-contig\t.\tmRNA\t1\t100\t.\t+\t.\tID=transcript-private;Parent=gene-private
secret-contig\t.\texon\t1\t50\t.\t+\t.\tParent=missing-parent
##FASTA
>private-contig
ACGT
"""
        result = wave26.gff3_annotation_audit(self.write("annotation.gff3", source))
        self.assert_report(result)
        self.assertIn("Feature rows: 3", result["summary"])
        self.assertIn("GFF version directives: 1", result["summary"])
        self.assertIn("Parent references without a matching ID in this file: 1", result["summary"])
        self.assertIn("Embedded FASTA records (count only): 1", result["summary"])
        self.assertNotIn("secret-contig", result["summary"])
        self.assertNotIn("gene-private", result["summary"])

    def test_gff3_audit_detects_bad_columns_and_coordinates(self):
        source = "##gff-version 3\nseq\t.\tgene\t0\t-5\tbad\tX\t9\tID=a\nbad-row\n"
        result = wave26.gff3_annotation_audit(self.write("bad.gff3", source))
        self.assert_report(result)
        self.assertIn("Feature rows with malformed attributes/column count: 1", result["summary"])
        self.assertIn("Invalid 1-based coordinates: 1", result["summary"])
        self.assertIn("Invalid strand markers: 1", result["summary"])
        self.assertIn("Invalid CDS phase values: 1", result["summary"])

    def test_bed_audit_checks_coordinate_and_block_fields_without_intervals(self):
        source = """chr-secret\t0\t100\tprivate-feature\t0\t+\t0\t100\t0\t2\t50,50\t0,50
chr-secret\t-1\t20\tbad
chr-secret\t30\t30\tzero
"""
        result = wave26.bed_interval_audit(self.write("regions.bed", source))
        self.assert_report(result)
        self.assertIn("BED intervals: 3", result["summary"])
        self.assertIn("Rows with invalid 0-based half-open coordinates: 1", result["summary"])
        self.assertIn("Zero-length intervals: 1", result["summary"])
        self.assertNotIn("chr-secret", result["summary"])
        self.assertNotIn("private-feature", result["summary"])

    def test_genbank_audit_counts_records_features_and_sequence_without_qualifiers(self):
        source = """LOCUS       private-locus       4 bp    DNA     PLN       21-JUN-1999
DEFINITION  Private organism sample.
ACCESSION   PRIVATE0001
FEATURES             Location/Qualifiers
     gene            1..4
                     /gene=\"secret-symbol\"
ORIGIN
        1 acgt
//
"""
        result = wave26.genbank_record_audit(self.write("record.gb", source))
        self.assert_report(result)
        self.assertIn("GenBank records: 1", result["summary"])
        self.assertIn("Total sequence bases: 4", result["summary"])
        self.assertIn("Feature table entries: 1", result["summary"])
        self.assertIn("Feature qualifier lines: 1", result["summary"])
        self.assertNotIn("private-locus", result["summary"])
        self.assertNotIn("secret-symbol", result["summary"])
        self.assertNotIn("PRIVATE0001", result["summary"])

    def test_pdb_audit_counts_atoms_models_and_residues_without_coordinates(self):
        source = """HEADER    PRIVATE STRUCTURE
MODEL        1
ATOM      1  CA  ALA A   1      11.104  13.207  14.099  1.00 20.00           C
HETATM    2  O   HOH A   2      12.104  13.207  14.099  1.00 25.00           O
ENDMDL
END
"""
        result = wave26.pdb_structure_audit(self.write("structure.pdb", source))
        self.assert_report(result)
        self.assertIn("PDB coordinate models: 1", result["summary"])
        self.assertIn("ATOM records: 1", result["summary"])
        self.assertIn("HETATM records: 1", result["summary"])
        self.assertIn("Distinct model/chain/residue keys: 2", result["summary"])
        self.assertNotIn("PRIVATE STRUCTURE", result["summary"])
        self.assertNotIn("11.104", result["summary"])

    def test_gfa_audit_checks_segment_references_and_hides_graph_ids(self):
        source = """H\tVN:Z:1.0
S\tsegment-private-1\tACGT
S\tsegment-private-2\tGG
L\tsegment-private-1\t+\tsegment-private-2\t-\t0M
P\tpath-private\tsegment-private-1+,segment-private-2-\t*
"""
        result = wave26.gfa_assembly_audit(self.write("assembly.gfa", source))
        self.assert_report(result)
        self.assertIn("Segment records: 2", result["summary"])
        self.assertIn("Malformed/unsupported records: 0", result["summary"])
        self.assertIn("References without an S segment: 0", result["summary"])
        self.assertNotIn("segment-private", result["summary"])
        self.assertNotIn("path-private", result["summary"])
        self.assertNotIn("ACGT", result["summary"])

    def test_gfa_audit_detects_missing_segment_reference(self):
        source = "S\ts1\tACGT\nL\ts1\t+\tmissing\t+\t0M\n"
        result = wave26.gfa_assembly_audit(self.write("broken.gfa", source))
        self.assert_report(result)
        self.assertIn("References without an S segment: 1", result["summary"])

    def test_newick_audit_counts_tree_topology_without_taxon_names(self):
        source = "(('private-A':0.1,'private-B':0.2)'private-clade':0.3,'private-C':0.4);\n"
        result = wave26.newick_tree_audit(self.write("tree.nwk", source))
        self.assert_report(result)
        self.assertIn("Trees parsed: 1", result["summary"])
        self.assertIn("Leaf/tip labels: 3", result["summary"])
        self.assertIn("Internal nodes: 2", result["summary"])
        self.assertIn("Branch-length fields: 4", result["summary"])
        self.assertNotIn("private-A", result["summary"])
        self.assertNotIn("private-clade", result["summary"])

    def test_newick_audit_flags_missing_semicolon(self):
        result = wave26.newick_tree_audit(self.write("tree.newick", "(A,B)"))
        self.assert_report(result)
        self.assertIn("Trees missing a final semicolon: 1", result["summary"])

    def test_stockholm_alignment_audit_counts_rows_and_equal_lengths(self):
        source = """# STOCKHOLM 1.0
private-seq-1 AC-G
private-seq-2 ACTG
//
"""
        result = wave26.sequence_alignment_audit(self.write("alignment.sto", source))
        self.assert_report(result)
        self.assertIn("Alignment format: Stockholm", result["summary"])
        self.assertIn("Distinct sequence rows: 2", result["summary"])
        self.assertIn("Unequal row lengths detected: 0", result["summary"])
        self.assertNotIn("private-seq", result["summary"])

    def test_clustal_alignment_audit_detects_unequal_rows(self):
        source = """CLUSTAL W multiple sequence alignment

private-one ACGT 4
private-two AC-T 3
  ** *
"""
        result = wave26.sequence_alignment_audit(self.write("alignment.aln", source))
        self.assert_report(result)
        self.assertIn("Alignment format: Clustal/MUSCLE", result["summary"])
        self.assertIn("Distinct sequence rows: 2", result["summary"])
        self.assertIn("Unequal row lengths detected: 0", result["summary"])
        self.assertNotIn("private-one", result["summary"])

    def test_alignment_audit_rejects_unknown_format(self):
        with self.assertRaisesRegex(RuntimeError, "not recognized"):
            wave26.sequence_alignment_audit(self.write("other.txt", "not an alignment\n"))


if __name__ == "__main__":
    unittest.main()
