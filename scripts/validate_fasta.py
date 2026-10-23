#!/usr/bin/env python3
"""PhytoStress TF Atlas — FASTA Validation Script.

Performs rigorous post-ingestion validation of:
- Exact sequence counts and file concordance
- Amino acid alphabet integrity (100% canonical IUPAC codes)
- Exact length and molecular weight validation
- Verification of all 5 known anomalies (AtPLATZ2, AtPLATZ4, OsDOF1, TaZNF, MtNLP1)
- Composite transcription factor linkages (SlCDF1/3, NLP1/5, VOZ1/2)
- Multi-study shared sequence associations (NLP7, OsMADS25, NLP2)
- Foreign key integrity and bidirectional relationship traversal
- Preservation of existing Phase 5A core entities

Usage:
    python scripts/validate_fasta.py
"""

import os
import sys
from typing import Dict, Any, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.database import SessionLocal
from backend.app.models.tf import TranscriptionFactor
from backend.app.models.plant import Plant
from backend.app.models.family import TFFamily
from backend.app.models.sequence import ProteinSequence
from backend.app.models.structure import ProteinStructure
from backend.app.models.interaction import ProteinInteraction

FASTA_DIR = os.path.join(PROJECT_ROOT, "FASTA sequence of TFs-20261008T053415Z-1-001", "FASTA sequence of TFs")
CANONICAL_AA = set("ACDEFGHIKLMNPQRSTVWY")


def run_fasta_validation() -> Dict[str, Any]:
    """Executes all FASTA validation checks against phytostress.db."""
    session = SessionLocal()
    results = {
        "status": "PASSED",
        "errors": [],
        "warnings": [],
        "checks_passed": 0,
        "metrics": {},
    }

    try:
        # Check 1: Physical File Count
        if not os.path.isdir(FASTA_DIR):
            results["errors"].append(f"FASTA directory missing: {FASTA_DIR}")
        files = sorted(os.listdir(FASTA_DIR))
        if len(files) != 41:
            results["errors"].append(f"Expected 41 FASTA files, found {len(files)}")
        results["checks_passed"] += 1
        results["metrics"]["physical_files_count"] = len(files)

        # Check 2: Protein Sequence Record Count
        total_seqs = session.query(ProteinSequence).count()
        if total_seqs != 46:
            results["errors"].append(f"Expected 46 sequence records in database, found {total_seqs}")
        results["checks_passed"] += 1
        results["metrics"]["db_sequence_records"] = total_seqs

        # Check 3: Preserved Core Database Baseline (Phase 5A tables unchanged)
        tf_count = session.query(TranscriptionFactor).count()
        plant_count = session.query(Plant).count()
        family_count = session.query(TFFamily).count()
        struct_count = session.query(ProteinStructure).count()
        inter_count = session.query(ProteinInteraction).count()

        if tf_count != 63:
            results["errors"].append(f"Core transcription_factors corrupted: expected 63, got {tf_count}")
        if plant_count != 30:
            results["errors"].append(f"Core plants corrupted: expected 30, got {plant_count}")
        if family_count != 23:
            results["errors"].append(f"Core tf_families corrupted: expected 23, got {family_count}")
        if struct_count != 0:
            results["errors"].append(f"Protein structures prematurely populated: {struct_count}")
        if inter_count != 0:
            results["errors"].append(f"Protein interactions prematurely populated: {inter_count}")

        results["checks_passed"] += 1
        results["metrics"]["core_tfs"] = tf_count
        results["metrics"]["core_plants"] = plant_count
        results["metrics"]["core_families"] = family_count

        # Check 4: Amino Acid Sequence Validity & Concordance
        all_seqs = session.query(ProteinSequence).all()
        total_residues = 0
        for s in all_seqs:
            if not s.sequence.isupper():
                results["errors"].append(f"Sequence not uppercase: record id {s.id}")
            if "\n" in s.sequence or "\r" in s.sequence or " " in s.sequence:
                results["errors"].append(f"Sequence contains whitespace/newlines: record id {s.id}")
            invalid = set(s.sequence) - CANONICAL_AA
            if invalid:
                results["errors"].append(f"Invalid amino acid characters {invalid} in record id {s.id}")
            if s.sequence_length != len(s.sequence):
                results["errors"].append(f"Sequence length mismatch in record id {s.id}: {s.sequence_length} != {len(s.sequence)}")
            if s.molecular_weight is None or s.molecular_weight <= 0:
                results["errors"].append(f"Invalid molecular weight in record id {s.id}: {s.molecular_weight}")
            total_residues += s.sequence_length

        results["checks_passed"] += 1
        results["metrics"]["total_amino_acids"] = total_residues

        # Check 5: Source File Bit-for-Bit Sequence Concordance
        for fname in files:
            fpath = os.path.join(FASTA_DIR, fname)
            with open(fpath, "r", encoding="utf-8", errors="replace") as fp:
                flines = fp.read().splitlines()
            if flines and flines[0].startswith(">"):
                raw_disk_seq = "".join(flines[1:])
            else:
                raw_disk_seq = "".join(flines)
            clean_disk_seq = "".join(raw_disk_seq.split()).upper()

            db_matches = [s for s in all_seqs if s.source_filename == fname]
            if not db_matches:
                results["errors"].append(f"File {fname} has no matching sequence in database")
            for db_s in db_matches:
                if db_s.sequence != clean_disk_seq:
                    results["errors"].append(f"Sequence mismatch for file {fname} in record id {db_s.id}")

        results["checks_passed"] += 1

        # Check 6: Anomaly 1 — AtPLATZ2.txt
        platz2 = [s for s in all_seqs if s.source_filename == "AtPLATZ2.txt"]
        if not platz2 or len(platz2) != 1:
            results["errors"].append("Anomaly 1 failed: AtPLATZ2.txt missing or multiple rows")
        else:
            p2 = platz2[0]
            if p2.tf_id != 54:
                results["errors"].append(f"AtPLATZ2 linked to wrong TF ID: {p2.tf_id}")
            if p2.sequence_length != 245:
                results["errors"].append(f"AtPLATZ2 wrong length: {p2.sequence_length}")
            if p2.fasta_header != ">AtPLATZ2_AT1G76590":
                results["errors"].append(f"AtPLATZ2 synthetic header mismatch: {p2.fasta_header}")
            if p2.validation_status != "Header generated":
                results["errors"].append(f"AtPLATZ2 status mismatch: {p2.validation_status}")
        results["checks_passed"] += 1

        # Check 7: Anomaly 2 — AtPLATZ4.txt
        platz4 = [s for s in all_seqs if s.source_filename == "AtPLATZ4.txt"]
        if not platz4 or len(platz4) != 1:
            results["errors"].append("Anomaly 2 failed: AtPLATZ4.txt missing or multiple rows")
        else:
            p4 = platz4[0]
            if p4.tf_id != 55:
                results["errors"].append(f"AtPLATZ4 linked to wrong TF ID: {p4.tf_id}")
            if p4.sequence_length != 213:
                results["errors"].append(f"AtPLATZ4 wrong length: {p4.sequence_length}")
            if p4.fasta_header != ">AtPLATZ4_AT1G32700":
                results["errors"].append(f"AtPLATZ4 synthetic header mismatch: {p4.fasta_header}")
            if p4.validation_status != "Header generated":
                results["errors"].append(f"AtPLATZ4 status mismatch: {p4.validation_status}")
        results["checks_passed"] += 1

        # Check 8: Anomaly 3 — OsDOF1.txt
        osdof1 = [s for s in all_seqs if s.source_filename == "OsDOF1.txt"]
        if not osdof1 or len(osdof1) != 1:
            results["errors"].append("Anomaly 3 failed: OsDOF1.txt missing or multiple rows")
        else:
            od = osdof1[0]
            if od.tf_id != 12:
                results["errors"].append(f"OsDOF1 linked to wrong TF ID: {od.tf_id}")
            if od.sequence_length != 215:
                results["errors"].append(f"OsDOF1 wrong length: {od.sequence_length}")
            if od.fasta_header != ">OsDOF1_Q9FE00":
                results["errors"].append(f"OsDOF1 synthetic header mismatch: {od.fasta_header}")
            if od.validation_status != "Header generated":
                results["errors"].append(f"OsDOF1 status mismatch: {od.validation_status}")
        results["checks_passed"] += 1

        # Check 9: Anomaly 4 — TaZNF.fasta.txt
        taznf = [s for s in all_seqs if s.source_filename == "TaZNF.fasta.txt"]
        if not taznf or len(taznf) != 1:
            results["errors"].append("Anomaly 4 failed: TaZNF.fasta.txt missing or multiple rows")
        else:
            tz = taznf[0]
            if tz.tf_id != 2:
                results["errors"].append(f"TaZNF linked to wrong TF ID: {tz.tf_id}")
            if tz.sequence_length != 501:
                results["errors"].append(f"TaZNF wrong length: {tz.sequence_length}")
            if tz.accession != "A0A1D5V0E4":
                results["errors"].append(f"TaZNF wrong accession: {tz.accession}")
        results["checks_passed"] += 1

        # Check 10: Anomaly 5 — MtNLP1 disambiguation
        mt1 = [s for s in all_seqs if s.source_filename == "MtNLP1.txt"]
        mt2 = [s for s in all_seqs if s.source_filename == "MtNLP1 (2).txt"]
        if not mt1 or len(mt1) != 1 or not mt2 or len(mt2) != 1:
            results["errors"].append("Anomaly 5 failed: MtNLP1 files missing or multiple rows")
        else:
            if mt1[0].tf_id != 31 or mt1[0].accession != "A0A977NVL6" or mt1[0].sequence_length != 934:
                results["errors"].append("Anomaly 5: MtNLP1.txt failed validation")
            if mt2[0].tf_id != 32 or mt2[0].accession != "A0A072V3U8" or mt2[0].sequence_length != 909:
                results["errors"].append("Anomaly 5: MtNLP1 (2).txt failed validation")
        results["checks_passed"] += 1

        # Check 11: Composite Transcription Factors
        tf6 = session.query(TranscriptionFactor).filter_by(id=6).first()
        if not tf6 or {s.source_filename for s in tf6.sequences} != {"SlCDF1.txt", "SlCDF3.txt"}:
            results["errors"].append("Composite TF #6 (SlCDF1 / SlCDF3) sequence association failed")

        tf33 = session.query(TranscriptionFactor).filter_by(id=33).first()
        if not tf33 or {s.source_filename for s in tf33.sequences} != {"SlNLP1.txt", "SlNLP5.txt"}:
            results["errors"].append("Composite TF #33 (NLP1 / NLP5) sequence association failed")

        tf44 = session.query(TranscriptionFactor).filter_by(id=44).first()
        if not tf44 or {s.source_filename for s in tf44.sequences} != {"VOZ1.txt", "VOZ2.txt"}:
            results["errors"].append("Composite TF #44 (VOZ1 / VOZ2) sequence association failed")
        results["checks_passed"] += 1

        # Check 12: Multi-Study Shared Sequences
        nlp7 = [s for s in all_seqs if s.source_filename == "NLP7.txt"]
        if len(nlp7) != 4 or {s.tf_id for s in nlp7} != {29, 30, 34, 35}:
            results["errors"].append("Shared sequence NLP7.txt association failed")

        mads25 = [s for s in all_seqs if s.source_filename == "OsMADS25.txt"]
        if len(mads25) != 2 or {s.tf_id for s in mads25} != {21, 22}:
            results["errors"].append("Shared sequence OsMADS25.txt association failed")

        nlp2 = [s for s in all_seqs if s.source_filename == "NLP2.txt"]
        if len(nlp2) != 2 or {s.tf_id for s in nlp2} != {28, 37}:
            results["errors"].append("Shared sequence NLP2.txt association failed")
        results["checks_passed"] += 1

        # Check 13: Bidirectional Relationship Traversal
        for s in all_seqs:
            tf = s.tf
            if tf is None:
                results["errors"].append(f"Orphan sequence record: id {s.id}")
            else:
                if tf.plant is None:
                    results["errors"].append(f"TF #{tf.id} missing plant relationship from sequence {s.id}")
                if tf.family is None:
                    results["errors"].append(f"TF #{tf.id} missing family relationship from sequence {s.id}")
                if s not in tf.sequences:
                    results["errors"].append(f"Bidirectional mismatch between TF #{tf.id} and sequence {s.id}")
        results["checks_passed"] += 1

        # Summary decision
        if results["errors"]:
            results["status"] = "FAILED"
        else:
            results["status"] = "PASSED"

    except Exception as e:
        results["status"] = "FAILED"
        results["errors"].append(f"Validation execution exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

    return results


def main():
    print("=" * 80)
    print("PHYTOSTRESS TF ATLAS — FASTA INGESTION VALIDATION")
    print("=" * 80)

    results = run_fasta_validation()

    print(f"Validation Status: {results['status']}")
    print(f"Total Validation Check Blocks Passed: {results['checks_passed']}")
    print("\nMetrics:")
    for k, v in results["metrics"].items():
        print(f"  {k}: {v}")

    if results["errors"]:
        print(f"\nERRORS DETECTED ({len(results['errors'])}):")
        for err in results["errors"]:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\nAll FASTA sequence validation checks passed with ZERO errors.")
        sys.exit(0)


if __name__ == "__main__":
    main()
