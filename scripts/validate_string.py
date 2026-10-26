"""
PhytoStress TF Atlas - Phase 5D: Independent STRING & FunCoup PPI Validator
==========================================================================
Verifies database integrity, foreign keys, confidence scores, evidence subscores,
image links, Cytoscape concordance, and baseline data preservation.

Usage:
    python scripts/validate_string.py
"""

import os
import sys
import sqlite3
from typing import Dict, List, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "phytostress.db")


def run_validation() -> bool:
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database file not found: {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    errors: List[str] = []
    print("================================================================================")
    print("PHASE 5D: STRING & FUNCOUP PPI INDEPENDENT VERIFICATION & VALIDATION")
    print("================================================================================")

    # 1. Total record counts
    total_interactions = c.execute("SELECT count(*) FROM protein_interactions").fetchone()[0]
    print(f"\n1. RECORD COUNT CHECK:")
    print(f"   - protein_interactions count: {total_interactions} (Expected: 489)")
    if total_interactions != 489:
        errors.append(f"Expected 489 protein_interactions rows, found {total_interactions}")

    # 2. Distinct TFs linked
    distinct_tfs = c.execute("SELECT count(DISTINCT tf_id) FROM protein_interactions").fetchone()[0]
    print(f"\n2. TARGET TRANSCRIPTION FACTORS LINKED:")
    print(f"   - Distinct TF record IDs linked: {distinct_tfs} (Expected: 45)")
    if distinct_tfs != 45:
        errors.append(f"Expected 45 distinct TF records, found {distinct_tfs}")

    # 3. Foreign key integrity
    orphaned_rows = c.execute("""
        SELECT count(*) FROM protein_interactions
        WHERE tf_id NOT IN (SELECT id FROM transcription_factors)
    """).fetchone()[0]
    print(f"\n3. FOREIGN KEY INTEGRITY CHECK:")
    print(f"   - Orphaned interaction records: {orphaned_rows} (Expected: 0)")
    if orphaned_rows != 0:
        errors.append(f"Found {orphaned_rows} orphaned interaction records")

    # 4. Source database breakdown
    db_counts = dict(c.execute("SELECT source_database, count(*) FROM protein_interactions GROUP BY source_database").fetchall())
    print(f"\n4. SOURCE DATABASE BREAKDOWN:")
    for db_name, cnt in db_counts.items():
        print(f"   - {db_name}: {cnt} rows")
    if db_counts.get("STRING") != 482:
        errors.append(f"Expected 482 STRING rows, found {db_counts.get('STRING')}")
    if db_counts.get("FunCoup") != 7:
        errors.append(f"Expected 7 FunCoup rows, found {db_counts.get('FunCoup')}")

    # 5. Score ranges and distributions
    scores = [r[0] for r in c.execute("SELECT combined_score FROM protein_interactions").fetchall()]
    min_score = min(scores) if scores else 0.0
    max_score = max(scores) if scores else 0.0
    avg_score = sum(scores) / len(scores) if scores else 0.0
    sorted_scores = sorted(scores)
    median_score = sorted_scores[len(sorted_scores) // 2] if sorted_scores else 0.0

    high_conf = sum(1 for s in scores if s >= 0.700)
    med_conf = sum(1 for s in scores if 0.400 <= s < 0.700)
    low_conf = sum(1 for s in scores if s < 0.400)

    print(f"\n5. COMBINED CONFIDENCE SCORE DISTRIBUTION:")
    print(f"   - Min Score:    {min_score:.4f}")
    print(f"   - Max Score:    {max_score:.4f}")
    print(f"   - Mean Score:   {avg_score:.4f}")
    print(f"   - Median Score: {median_score:.4f}")
    print(f"   - High Confidence (>= 0.700):   {high_conf} rows ({high_conf / len(scores) * 100:.1f}%)")
    print(f"   - Medium Confidence (0.4-0.7):  {med_conf} rows ({med_conf / len(scores) * 100:.1f}%)")
    print(f"   - Low Confidence (< 0.400):     {low_conf} rows ({low_conf / len(scores) * 100:.1f}%)")

    invalid_scores = c.execute("SELECT count(*) FROM protein_interactions WHERE combined_score < 0.0 OR combined_score > 1.0").fetchone()[0]
    if invalid_scores != 0:
        errors.append(f"Found {invalid_scores} interaction rows with invalid combined_score outside [0.0, 1.0]")

    # 6. Evidence subscores coverage
    exp_cnt = c.execute("SELECT count(*) FROM protein_interactions WHERE experimental_score IS NOT NULL AND experimental_score > 0").fetchone()[0]
    db_cnt = c.execute("SELECT count(*) FROM protein_interactions WHERE database_score IS NOT NULL AND database_score > 0").fetchone()[0]
    text_cnt = c.execute("SELECT count(*) FROM protein_interactions WHERE textmining_score IS NOT NULL AND textmining_score > 0").fetchone()[0]
    coex_cnt = c.execute("SELECT count(*) FROM protein_interactions WHERE coexpression_score IS NOT NULL AND coexpression_score > 0").fetchone()[0]

    print(f"\n6. EVIDENCE SUBSCORE COVERAGE (Non-Zero Counts):")
    print(f"   - Biochemical Experimental Evidence: {exp_cnt} rows ({exp_cnt / total_interactions * 100:.1f}%)")
    print(f"   - Curated Pathway Database Evidence:  {db_cnt} rows ({db_cnt / total_interactions * 100:.1f}%)")
    print(f"   - Literature Textmining Evidence:    {text_cnt} rows ({text_cnt / total_interactions * 100:.1f}%)")
    print(f"   - RNA Coexpression Evidence:         {coex_cnt} rows ({coex_cnt / total_interactions * 100:.1f}%)")

    # 7. Image linkage metrics
    with_string_img = c.execute("SELECT count(*) FROM protein_interactions WHERE string_image_path IS NOT NULL").fetchone()[0]
    with_cyto_img = c.execute("SELECT count(*) FROM protein_interactions WHERE cytoscape_image_path IS NOT NULL").fetchone()[0]
    without_cyto_img = c.execute("SELECT count(*) FROM protein_interactions WHERE cytoscape_image_path IS NULL").fetchone()[0]

    print(f"\n7. NETWORK DIAGRAM ASSET LINKAGE:")
    print(f"   - STRING/FunCoup image linked: {with_string_img}/{total_interactions} ({with_string_img / total_interactions * 100:.1f}%)")
    print(f"   - Cytoscape PNG linked:        {with_cyto_img}/{total_interactions} ({with_cyto_img / total_interactions * 100:.1f}%)")
    print(f"   - Cytoscape PNG NULL:          {without_cyto_img}/{total_interactions} ({without_cyto_img / total_interactions * 100:.1f}%)")

    if with_string_img != 489:
        errors.append(f"Expected 489 string_image_path links, found {with_string_img}")
    if with_cyto_img != 367:
        errors.append(f"Expected 367 cytoscape_image_path links, found {with_cyto_img}")
    if without_cyto_img != 122:
        errors.append(f"Expected 122 null cytoscape_image_path links, found {without_cyto_img}")

    # Check physical existence of image files on disk
    missing_imgs = 0
    for r in c.execute("SELECT string_image_path, cytoscape_image_path FROM protein_interactions").fetchall():
        s_img, c_img = r
        if s_img and not os.path.exists(os.path.join(PROJECT_ROOT, s_img)):
            missing_imgs += 1
        if c_img and not os.path.exists(os.path.join(PROJECT_ROOT, c_img)):
            missing_imgs += 1
    print(f"   - Missing physical image files on disk: {missing_imgs}")
    if missing_imgs > 0:
        errors.append(f"Found {missing_imgs} missing image files on disk")

    # 8. Baseline database preservation across all 16 tables
    print(f"\n8. DATABASE BASELINE ENTITY AUDIT (ALL 16 TABLES):")
    expected_counts = {
        "transcription_factors": 63,
        "plants": 30,
        "tf_families": 23,
        "stress_conditions": 21,
        "research_papers": 60,
        "tf_identifiers": 92,
        "target_genes": 75,
        "pathways": 110,
        "tf_stress_associations": 89,
        "tf_target_associations": 76,
        "tf_pathway_associations": 121,
        "tf_paper_associations": 63,
        "protein_sequences": 46,
        "protein_structures": 60,
        "protein_interactions": 489,
    }

    for tbl, exp_cnt in expected_counts.items():
        actual_cnt = c.execute(f"SELECT count(*) FROM {tbl}").fetchone()[0]
        match_str = "MATCH" if actual_cnt == exp_cnt else "MISMATCH"
        print(f"   - {tbl:<26}: {actual_cnt:>4} rows (Expected: {exp_cnt:>4}) [{match_str}]")
        if actual_cnt != exp_cnt:
            errors.append(f"Table {tbl} row count mismatch: {actual_cnt} != {exp_cnt}")

    # 9. Source directory immutability check
    string_files_count = sum(len(files) for _, _, files in os.walk(os.path.join(PROJECT_ROOT, "STRING database information-20261008T053421Z-1-001")))
    cyto_files_count = sum(len(files) for _, _, files in os.walk(os.path.join(PROJECT_ROOT, "Cytoscape protein interactions-20261008T053406Z-1-001")))
    print(f"\n9. SOURCE ARCHIVE INTEGRITY AUDIT:")
    print(f"   - STRING archive files:    {string_files_count} (Expected: 488)")
    print(f"   - Cytoscape archive files: {cyto_files_count} (Expected: 32)")
    if string_files_count != 488:
        errors.append(f"STRING source directory modified! Expected 488 files, found {string_files_count}")
    if cyto_files_count != 32:
        errors.append(f"Cytoscape source directory modified! Expected 32 files, found {cyto_files_count}")

    print("\n================================================================================")
    if not errors:
        print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY (0 ERRORS)")
        print("================================================================================")
        return True
    else:
        print(f"VALIDATION FAILED WITH {len(errors)} ERROR(S):")
        for err in errors:
            print(f"  [ERROR] {err}")
        print("================================================================================")
        return False


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
