#!/usr/bin/env python3
"""PhytoStress TF Atlas — Database Validation Script.

Validates data integrity, entity counts, relationship constraints, provenance,
and 1-to-1 concordance between `data/raw/prototype_63_records.json` and `phytostress.db`.

Usage:
    python scripts/validate_data.py
"""

import os
import sys
import json
from typing import Dict, Any, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.database import SessionLocal
from backend.app.models import (
    TranscriptionFactor,
    Plant,
    TFFamily,
    StressCondition,
    TFStressAssociation,
    TFIdentifier,
    ResearchPaper,
    TFPaperAssociation,
    TargetGene,
    TFTargetAssociation,
    Pathway,
    TFPathwayAssociation,
    ImportAudit,
    ProteinSequence,
    ProteinStructure,
    ProteinInteraction,
)


def validate_database() -> Dict[str, Any]:
    """Runs a complete validation suite against the database and returns results."""
    session = SessionLocal()
    results = {
        "status": "PASSED",
        "errors": [],
        "warnings": [],
        "table_counts": {},
        "concordance_checked": 0,
        "concordance_passed": 0
    }

    try:
        # 1. Exact Table Counts
        expected_counts = {
            "transcription_factors": 63,
            "plants": 30,
            "tf_families": 23,
            "stress_conditions": 21,
            "tf_stress_associations": 89,
            "tf_identifiers": 92,
            "research_papers": 60,
            "tf_paper_associations": 63,
            "target_genes": 75,
            "tf_target_associations": 76,
            "pathways": 110,
            "tf_pathway_associations": 121,
            "protein_sequences": 0,
            "protein_structures": 0,
            "protein_interactions": 0
        }

        actual_counts = {
            "transcription_factors": session.query(TranscriptionFactor).count(),
            "plants": session.query(Plant).count(),
            "tf_families": session.query(TFFamily).count(),
            "stress_conditions": session.query(StressCondition).count(),
            "tf_stress_associations": session.query(TFStressAssociation).count(),
            "tf_identifiers": session.query(TFIdentifier).count(),
            "research_papers": session.query(ResearchPaper).count(),
            "tf_paper_associations": session.query(TFPaperAssociation).count(),
            "target_genes": session.query(TargetGene).count(),
            "tf_target_associations": session.query(TFTargetAssociation).count(),
            "pathways": session.query(Pathway).count(),
            "tf_pathway_associations": session.query(TFPathwayAssociation).count(),
            "protein_sequences": session.query(ProteinSequence).count(),
            "protein_structures": session.query(ProteinStructure).count(),
            "protein_interactions": session.query(ProteinInteraction).count(),
            "import_audits": session.query(ImportAudit).count()
        }
        results["table_counts"] = actual_counts

        for table_name, exp in expected_counts.items():
            act = actual_counts.get(table_name, 0)
            if act != exp:
                results["errors"].append(
                    f"Count mismatch in '{table_name}': expected {exp}, got {act}"
                )

        # 2. Foreign Key & Relationship Integrity
        tfs = session.query(TranscriptionFactor).all()
        family_ids = {f.id for f in session.query(TFFamily.id).all()}
        plant_ids = {p.id for p in session.query(Plant.id).all()}

        for tf in tfs:
            if tf.family_id not in family_ids:
                results["errors"].append(f"TF ID #{tf.id} has invalid family_id {tf.family_id}")
            if tf.plant_id not in plant_ids:
                results["errors"].append(f"TF ID #{tf.id} has invalid plant_id {tf.plant_id}")
            if len(tf.papers) == 0:
                results["errors"].append(f"TF ID #{tf.id} ({tf.tf_name}) is missing research paper association")
            if len(tf.stresses) == 0:
                results["errors"].append(f"TF ID #{tf.id} ({tf.tf_name}) has no stress condition associations")

        # Check orphan identifiers
        tf_ids = {t.id for t in tfs}
        identifiers = session.query(TFIdentifier).all()
        for ident in identifiers:
            if ident.tf_id not in tf_ids:
                results["errors"].append(f"Identifier ID #{ident.id} has invalid tf_id {ident.tf_id}")

        # 3. Source Concordance (Compare against all 63 records)
        source_json_path = os.path.join(PROJECT_ROOT, "data", "raw", "prototype_63_records.json")
        with open(source_json_path, "r", encoding="utf-8") as f:
            source_records = json.load(f)

        results["concordance_checked"] = len(source_records)
        for idx, rec in enumerate(source_records, start=1):
            tf = session.query(TranscriptionFactor).filter(
                TranscriptionFactor.source_row_index == idx
            ).first()
            if not tf:
                results["errors"].append(f"Source Record #{idx} missing from database!")
                continue

            # Verify TF Name
            src_tf = rec.get("TF / TF family", "").strip()
            if tf.tf_name != src_tf:
                results["errors"].append(f"Record #{idx} TF name mismatch: expected '{src_tf}', got '{tf.tf_name}'")

            # Verify Raw Stress
            src_stress = rec.get("Stress condition", "").strip()
            if tf.raw_stress != src_stress:
                results["errors"].append(f"Record #{idx} raw_stress mismatch: expected '{src_stress}', got '{tf.raw_stress}'")

            # Verify Unverified status
            src_id_val = rec.get("Uniprot Accession ID/Valid Gene ID", "").strip()
            if "Not verified" in src_id_val or "not sure" in src_id_val or not src_id_val:
                if tf.is_verified is not False:
                    results["errors"].append(f"Record #{idx} ({tf.tf_name}) should be is_verified=False")

            results["concordance_passed"] += 1

        # 4. Check Composite TFs Preservation
        composite_examples = [
            "SlCDF1 / SlCDF3",
            "BpDOF4 / BpDOF11 / BpDOF17",
            "MADS-box family",
            "NLP1 / NLP5",
            "VOZ1 / VOZ2",
            "TaSPL6-A/B/D",
            "ZmBES1/BZR1-1",
            "SlBZR1 / SlBZR1D"
        ]
        db_tf_names = {t.tf_name for t in tfs}
        for c_tf in composite_examples:
            if c_tf not in db_tf_names:
                results["errors"].append(f"Composite TF name '{c_tf}' not preserved in database!")

        # 5. Check Unverified Count
        unverified_tfs = [t for t in tfs if not t.is_verified]
        if len(unverified_tfs) != 12:
            results["warnings"].append(
                f"Expected 12 unverified/uncertain records, found {len(unverified_tfs)}"
            )

        # 6. Check Import Audit
        audits = session.query(ImportAudit).all()
        if len(audits) == 0:
            results["errors"].append("Missing import_audits entry!")

        if results["errors"]:
            results["status"] = "FAILED"

    finally:
        session.close()

    return results


if __name__ == "__main__":
    print("Running comprehensive data validation on phytostress.db...")
    res = validate_database()
    
    print("\n==================================================")
    print(f"VALIDATION STATUS: {res['status']}")
    print("==================================================")
    print("Database Table Counts:")
    for tbl, cnt in res["table_counts"].items():
        print(f"  • {tbl:<26}: {cnt}")
        
    print(f"\nSource Concordance Checked : {res['concordance_checked']} / 63")
    print(f"Source Concordance Passed  : {res['concordance_passed']} / 63")
    print(f"Disappeared Records Count : {res['concordance_checked'] - res['concordance_passed']}")
    
    if res["warnings"]:
        print("\nWarnings:")
        for w in res["warnings"]:
            print(f"  [!] {w}")
            
    if res["errors"]:
        print("\nErrors:")
        for e in res["errors"]:
            print(f"  [X] {e}")
        sys.exit(1)
    else:
        print("\nAll database validation and concordance checks PASSED with 0 errors!")
        sys.exit(0)
