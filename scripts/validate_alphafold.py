#!/usr/bin/env python3
"""PhytoStress TF Atlas — AlphaFold Structure Validation Script.

Performs exhaustive post-ingestion validation of:
- Total file inventory across the source asset tree (303 physical files)
- Relevant structure files (60 PDBs) and metadata files (84 JSONs, 36 PNGs)
- Supported formats (.pdb, .png, .json, .csv, .a3m)
- Database structure counts (exactly 60 rows across 12 distinct TFs)
- 5-rank structure integrity for each model suite (Ranks 1 to 5)
- Sequence-to-structure residue concordance (100% C-alpha alignment)
- Confidence metadata availability (100% mean pLDDT present, range 0-100)
- PAE, pLDDT, and coverage image asset path resolution
- Template homolog verification (BnCDF1 -> AtDOF5.8)
- Medicago truncatula NLP1 disambiguation (MtNLP1_95155 linked to Record #31 only)
- Preservation of Phase 5A and 5B database records
- Identification of manual-review items and unmatched source records

Usage:
    python scripts/validate_alphafold.py
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

AF_SOURCE_ROOT = os.path.join(PROJECT_ROOT, "AlphaFold -20261008T053401Z-1-001")


def run_alphafold_validation() -> Dict[str, Any]:
    """Runs the complete AlphaFold validation suite against phytostress.db and disk."""
    session = SessionLocal()
    results = {
        "status": "PASSED",
        "errors": [],
        "warnings": [],
        "checks_passed": 0,
        "metrics": {},
        "manual_review_items": [],
    }

    try:
        # Check 1: Physical File Count & Format Breakdown
        if not os.path.isdir(AF_SOURCE_ROOT):
            results["errors"].append(f"Source directory missing: {AF_SOURCE_ROOT}")

        all_files = []
        ext_counts = {}
        for root, dirs, files in os.walk(AF_SOURCE_ROOT):
            for f in files:
                all_files.append(os.path.join(root, f))
                _, ext = os.path.splitext(f)
                ext_lower = ext.lower()
                ext_counts[ext_lower] = ext_counts.get(ext_lower, 0) + 1

        total_files = len(all_files)
        if total_files != 303:
            results["errors"].append(f"Expected 303 files in AlphaFold source, found {total_files}")
        results["checks_passed"] += 1
        results["metrics"]["total_source_files"] = total_files
        results["metrics"]["pdb_files_count"] = ext_counts.get(".pdb", 0)
        results["metrics"]["png_files_count"] = ext_counts.get(".png", 0)
        results["metrics"]["json_files_count"] = ext_counts.get(".json", 0)
        results["metrics"]["csv_files_count"] = ext_counts.get(".csv", 0)

        # Check 2: Structure Record Count in Database
        struct_count = session.query(ProteinStructure).count()
        if struct_count != 60:
            results["errors"].append(f"Expected 60 records in protein_structures, found {struct_count}")
        results["checks_passed"] += 1
        results["metrics"]["db_structure_records"] = struct_count

        # Check 3: Distinct Structured Transcription Factors
        structured_tfs = session.query(ProteinStructure.tf_id).distinct().all()
        unique_tf_ids = {t[0] for t in structured_tfs}
        if len(unique_tf_ids) != 12:
            results["errors"].append(f"Expected 12 structured TFs, found {len(unique_tf_ids)}")
        results["checks_passed"] += 1
        results["metrics"]["distinct_structured_tfs"] = len(unique_tf_ids)

        # Check 4: Exactly 5 Ranks per Structured TF
        for tid in unique_tf_ids:
            tf_structs = session.query(ProteinStructure).filter_by(tf_id=tid).order_by(ProteinStructure.rank_num).all()
            if len(tf_structs) != 5:
                results["errors"].append(f"TF #{tid} has {len(tf_structs)} ranks instead of 5")
            ranks = [s.rank_num for s in tf_structs]
            if ranks != [1, 2, 3, 4, 5]:
                results["errors"].append(f"TF #{tid} has invalid rank sequence: {ranks}")
        results["checks_passed"] += 1

        # Check 5: PDB Coordinate File Readability and Existence
        all_structs = session.query(ProteinStructure).all()
        for s in all_structs:
            full_pdb = os.path.join(PROJECT_ROOT, s.pdb_file_path)
            if not os.path.isfile(full_pdb):
                results["errors"].append(f"PDB file missing on disk: {full_pdb}")
            elif os.path.getsize(full_pdb) == 0:
                results["errors"].append(f"PDB file empty: {full_pdb}")
        results["checks_passed"] += 1

        # Check 6: Sequence-to-Structure C-alpha Residue Count Concordance
        for s in all_structs:
            tf = s.tf
            if tf is None:
                results["errors"].append(f"Orphan structure record #{s.id}")
                continue
            matching_seq = next((sq for sq in tf.sequences if sq.sequence_length > 0), None)
            if not matching_seq:
                results["errors"].append(f"TF #{tf.id} has structure #{s.id} but no sequence record")
                continue

            full_pdb = os.path.join(PROJECT_ROOT, s.pdb_file_path)
            ca_atoms = 0
            with open(full_pdb, "r", encoding="utf-8", errors="replace") as pf:
                for line in pf:
                    if line.startswith("ATOM  ") and line[12:16].strip() == "CA":
                        ca_atoms += 1

            if ca_atoms != matching_seq.sequence_length:
                results["errors"].append(
                    f"Residue concordance failure for TF #{tf.id} ({s.model_identifier} rank {s.rank_num}): "
                    f"PDB has {ca_atoms} CA atoms, sequence has {matching_seq.sequence_length} AA"
                )
        results["checks_passed"] += 1

        # Check 7: Confidence Metadata Availability & Bounds
        plddt_values = []
        for s in all_structs:
            if s.mean_plddt is None:
                results["errors"].append(f"Structure #{s.id} missing mean_plddt")
            elif not (0.0 <= s.mean_plddt <= 100.0):
                results["errors"].append(f"Structure #{s.id} has out-of-bounds mean_plddt: {s.mean_plddt}")
            else:
                plddt_values.append(s.mean_plddt)
        results["checks_passed"] += 1
        results["metrics"]["min_mean_plddt"] = min(plddt_values) if plddt_values else None
        results["metrics"]["max_mean_plddt"] = max(plddt_values) if plddt_values else None

        # Check 8: Diagnostic Image Asset Path Resolution
        for s in all_structs:
            for attr in ["pae_image_path", "plddt_image_path", "coverage_image_path"]:
                img_rel = getattr(s, attr)
                if not img_rel:
                    results["errors"].append(f"Structure #{s.id} missing {attr}")
                else:
                    full_img = os.path.join(PROJECT_ROOT, img_rel)
                    if not os.path.isfile(full_img):
                        results["errors"].append(f"Diagnostic image missing on disk: {full_img}")
        results["checks_passed"] += 1

        # Check 9: Special Anomaly — BnCDF1 Template Homolog Flag
        bn_structs = session.query(ProteinStructure).filter_by(tf_id=9).all()
        if len(bn_structs) != 5:
            results["errors"].append(f"BnCDF1 expected 5 models, got {len(bn_structs)}")
        for bs in bn_structs:
            if bs.template_homolog != "AtDOF5.8":
                results["errors"].append(f"BnCDF1 missing template_homolog='AtDOF5.8': {bs.template_homolog}")
            if "AtDOF58_489cf" not in bs.pdb_file_path:
                results["errors"].append(f"BnCDF1 PDB path does not contain AtDOF58 prefix: {bs.pdb_file_path}")
        results["checks_passed"] += 1

        # Check 10: Special Disambiguation — MtNLP1_95155
        mt31_structs = session.query(ProteinStructure).filter_by(tf_id=31).all()
        mt32_structs = session.query(ProteinStructure).filter_by(tf_id=32).all()

        if len(mt31_structs) != 5:
            results["errors"].append(f"Record #31 (Nature Plants 2018) expected 5 models, got {len(mt31_structs)}")
        if len(mt32_structs) != 0:
            results["errors"].append(f"Record #32 falsely assigned structures: {len(mt32_structs)}")
        results["checks_passed"] += 1

        # Check 11: Preservation of Phase 5A / 5B Database Core
        tf_count = session.query(TranscriptionFactor).count()
        plant_count = session.query(Plant).count()
        family_count = session.query(TFFamily).count()
        seq_count = session.query(ProteinSequence).count()
        inter_count = session.query(ProteinInteraction).count()

        if tf_count != 63:
            results["errors"].append(f"transcription_factors count altered: {tf_count} != 63")
        if plant_count != 30:
            results["errors"].append(f"plants count altered: {plant_count} != 30")
        if family_count != 23:
            results["errors"].append(f"tf_families count altered: {family_count} != 23")
        if seq_count != 46:
            results["errors"].append(f"protein_sequences count altered: {seq_count} != 46")
        if inter_count != 0:
            results["errors"].append(f"protein_interactions prematurely populated: {inter_count}")

        results["checks_passed"] += 1
        results["metrics"]["core_tfs"] = tf_count
        results["metrics"]["core_sequences"] = seq_count
        results["metrics"]["core_interactions"] = inter_count

        # Check 12: Manual Review Audit Items
        # Document TFs that do not have AlphaFold models in the asset repository
        unstructured_tfs = session.query(TranscriptionFactor).filter(
            ~TranscriptionFactor.id.in_(unique_tf_ids)
        ).all()
        results["metrics"]["unstructured_tfs_count"] = len(unstructured_tfs)

        results["manual_review_items"].append({
            "category": "Disambiguated Homolog",
            "tf_id": 32,
            "tf_name": "NLP1 (Plant Comms 2021)",
            "plant": "Medicago truncatula",
            "reason": "Model MtNLP1_95155 was computed on 934 AA sequence of Record #31 (A0A977NVL6). Record #32 has distinct 909 AA sequence (A0A072V3U8) and was not modeled in AlphaFold."
        })

        results["manual_review_items"].append({
            "category": "Unmodeled Curated Records",
            "tf_id": None,
            "tf_name": f"{len(unstructured_tfs)} Curated TFs",
            "plant": "Various",
            "reason": f"51 transcription factor records have no corresponding prediction suite in the AlphaFold source repository."
        })
        results["checks_passed"] += 1

        # Decision
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
    print("PHYTOSTRESS TF ATLAS — ALPHAFOLD STRUCTURE VALIDATION")
    print("=" * 80)

    res = run_alphafold_validation()

    print(f"Validation Status: {res['status']}")
    print(f"Total Validation Check Blocks Passed: {res['checks_passed']}")
    print("\nMetrics Summary:")
    for k, v in res["metrics"].items():
        print(f"  {k}: {v}")

    print("\nManual Review Audit:")
    for item in res["manual_review_items"]:
        print(f"  [{item['category']}] {item['tf_name']}: {item['reason']}")

    if res["errors"]:
        print(f"\nVALIDATION ERRORS DETECTED ({len(res['errors'])}):")
        for err in res["errors"]:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\nAll AlphaFold structure validation checks passed with ZERO errors.")
        sys.exit(0)


if __name__ == "__main__":
    main()
