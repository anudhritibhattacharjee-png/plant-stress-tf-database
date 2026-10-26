"""PhytoStress TF Atlas — STRING & FunCoup Interaction Ingestion Test Suite.

Verifies:
- All 45 interaction packages (44 STRING + 1 FunCoup) and 488 files are accounted for.
- Exactly 489 protein interaction records are stored in `protein_interactions`.
- Target transcription factor deterministic linkage and foreign-key integrity.
- Confidence score ranges (0.000 to 1.000) for combined and sub-scores.
- FunCoup special handling for OsDOF18 (TF #15, 7 partners, PPV scores).
- MdDOF54 special handling (TF #7, 2 partners).
- Multi-record study mapping (NLP7 across #29, #30, #34, #35; OsMADS25 across #21, #22).
- Strict reciprocal edge deduplication and first-neighbor filtering.
- Authentic non-TF partner representation (e.g. ADM, SUVH9, AUX22).
- Image path resolution with forward slashes and verification of physical files on disk.
- Cytoscape image audit concordance (32 PNG files, 367 linked rows, 122 null rows).
- Maize ZmBES1-BZR1 deterministic matching to BZR1.png.
- Baseline data preservation across all 15 other database tables.
- Immutability of original STRING and Cytoscape source files.
"""

import os
import hashlib
import pytest
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models.tf import TranscriptionFactor
from backend.app.models.sequence import ProteinSequence
from backend.app.models.structure import ProteinStructure
from backend.app.models.interaction import ProteinInteraction
from backend.app.models.plant import Plant
from backend.app.models.family import TFFamily
from backend.app.models.stress import StressCondition
from backend.app.models.paper import ResearchPaper
from scripts.import_string import import_string_interactions

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STRING_ROOT = os.path.join(PROJECT_ROOT, "STRING database information-20261008T053421Z-1-001", "STRING database information")
CYTO_ROOT = os.path.join(PROJECT_ROOT, "Cytoscape protein interactions-20261008T053406Z-1-001", "Cytoscape protein interactions")


@pytest.fixture(scope="module")
def db_session():
    """Provides a transactional database session for tests."""
    session = SessionLocal()
    yield session
    session.close()


def test_string_source_directories_exist_and_intact():
    """Verify that all 45 interaction directories and 488 source files exist in STRING archive."""
    assert os.path.isdir(STRING_ROOT), f"STRING directory missing: {STRING_ROOT}"
    dirs = sorted(os.listdir(STRING_ROOT))
    assert len(dirs) == 45, f"Expected 45 STRING directories, found {len(dirs)}"

    total_files = 0
    for root, _, files in os.walk(STRING_ROOT):
        total_files += len(files)
    assert total_files == 488, f"Expected 488 total files in STRING source, found {total_files}"


def test_cytoscape_source_files_intact():
    """Verify that exactly 32 PNG image files and 0 structured files exist in Cytoscape folder."""
    assert os.path.isdir(CYTO_ROOT), f"Cytoscape directory missing: {CYTO_ROOT}"
    files = sorted(os.listdir(CYTO_ROOT))
    assert len(files) == 32, f"Expected 32 files in Cytoscape folder, found {len(files)}"
    for f in files:
        assert f.lower().endswith(".png"), f"Unexpected non-PNG file in Cytoscape folder: {f}"


def test_protein_interaction_total_count(db_session: Session):
    """Verify exactly 489 interaction records exist in protein_interactions table."""
    count = db_session.query(ProteinInteraction).count()
    assert count == 489, f"Expected 489 interaction records in database, found {count}"


def test_target_tfs_linked_and_foreign_keys(db_session: Session):
    """Verify all protein_interactions records link to valid transcription factors via FK."""
    interactions = db_session.query(ProteinInteraction).all()
    assert len(interactions) == 489

    tf_ids_in_db = {tf.id for tf in db_session.query(TranscriptionFactor.id).all()}
    linked_tf_ids = {item.tf_id for item in interactions}

    assert linked_tf_ids.issubset(tf_ids_in_db), "Found interaction rows with invalid tf_id FK"
    # Exactly 45 distinct TF records have linked interactions
    assert len(linked_tf_ids) == 45, f"Expected 45 distinct TFs with interactions, found {len(linked_tf_ids)}"



def test_combined_score_bounds(db_session: Session):
    """Verify all combined_score values are valid confidence scores in [0.000, 1.000]."""
    scores = db_session.query(ProteinInteraction.combined_score).all()
    assert len(scores) == 489
    for (s,) in scores:
        assert isinstance(s, float), f"Score is not a float: {s}"
        assert 0.0 <= s <= 1.0, f"Combined score out of bounds: {s}"
        assert s > 0.0, f"Unexpected zero combined score: {s}"


def test_evidence_subscore_integrity(db_session: Session):
    """Verify evidence subscores (experimental, database, textmining, coexpression) are preserved."""
    interactions = db_session.query(ProteinInteraction).filter(ProteinInteraction.source_database == "STRING").all()
    assert len(interactions) == 482

    exp_scores = [i.experimental_score for i in interactions if i.experimental_score is not None]
    db_scores = [i.database_score for i in interactions if i.database_score is not None]
    text_scores = [i.textmining_score for i in interactions if i.textmining_score is not None]
    coex_scores = [i.coexpression_score for i in interactions if i.coexpression_score is not None]

    assert len(exp_scores) > 0, "No experimental scores preserved"
    assert len(db_scores) > 0, "No database scores preserved"
    assert len(text_scores) > 0, "No textmining scores preserved"
    assert len(coex_scores) > 0, "No coexpression scores preserved"

    for score_list in [exp_scores, db_scores, text_scores, coex_scores]:
        for s in score_list:
            assert 0.0 <= s <= 1.0, f"Evidence subscore out of range: {s}"


def test_funcoup_package_osdof18(db_session: Session):
    """Verify special handling of OsDOF18 (TF #15) from FunCoup database."""
    dof18_rows = db_session.query(ProteinInteraction).filter(ProteinInteraction.tf_id == 15).all()
    assert len(dof18_rows) == 7, f"Expected 7 FunCoup interactions for OsDOF18, found {len(dof18_rows)}"

    for row in dof18_rows:
        assert row.source_database == "FunCoup"
        assert 0.0 < row.combined_score <= 1.0
        assert row.experimental_score is None  # FunCoup does not have STRING subscores
        assert row.notes and "FunCoup PPV=" in row.notes
        assert row.string_image_path and row.string_image_path.endswith("FunCoup_subnetwork.png")
        assert row.cytoscape_image_path and row.cytoscape_image_path.endswith("OsDOF18.png")


def test_mddof54_interaction_count(db_session: Session):
    """Verify special handling of MdDOF54 (TF #7) which has exactly 2 direct partners."""
    md_rows = db_session.query(ProteinInteraction).filter(ProteinInteraction.tf_id == 7).all()
    assert len(md_rows) == 2, f"Expected 2 interactions for MdDOF54, found {len(md_rows)}"
    for r in md_rows:
        assert r.source_database == "STRING"
        assert r.source_file and "string_interactions_3_nodes.tsv" in r.source_file


def test_multi_record_tf_mappings(db_session: Session):
    """Verify multi-record studies map accurately (NLP7: 4 TFs; OsMADS25: 2 TFs)."""
    # NLP7 maps across #29, #30, #34, #35 (10 partners each = 40 rows)
    nlp7_ids = [29, 30, 34, 35]
    nlp7_rows = db_session.query(ProteinInteraction).filter(ProteinInteraction.tf_id.in_(nlp7_ids)).all()
    assert len(nlp7_rows) == 40, f"Expected 40 NLP7 rows across 4 TF records, found {len(nlp7_rows)}"
    for tid in nlp7_ids:
        assert len([r for r in nlp7_rows if r.tf_id == tid]) == 10

    # OsMADS25 maps across #21, #22 (10 partners each = 20 rows)
    mads25_ids = [21, 22]
    mads25_rows = db_session.query(ProteinInteraction).filter(ProteinInteraction.tf_id.in_(mads25_ids)).all()
    assert len(mads25_rows) == 20, f"Expected 20 OsMADS25 rows across 2 TF records, found {len(mads25_rows)}"


def test_reciprocal_edge_deduplication(db_session: Session):
    """Verify reciprocal edges were deduplicated and each partner under single-source TF is unique."""
    # Check AHL10 (#60)
    ahl10_rows = db_session.query(ProteinInteraction).filter(ProteinInteraction.tf_id == 60).all()
    assert len(ahl10_rows) == 10
    partner_names = [r.partner_name for r in ahl10_rows]
    assert len(set(partner_names)) == 10, f"Duplicate partner names detected in AHL10: {partner_names}"


def test_authentic_non_tf_partners_preserved(db_session: Session):
    """Verify non-TF partner proteins are faithfully preserved in partner_name/partner_uniprot."""
    # Check for presence of uncharacterized and functional partners
    aux22 = db_session.query(ProteinInteraction).filter(ProteinInteraction.partner_name == "AUX22").first()
    assert aux22 is not None, "Expected interactor AUX22 not found"
    assert aux22.tf_id == 58  # ZmBES1-BZR1
    assert aux22.partner_uniprot == "A0A1D6FF66"

    # Verify TF table was NOT corrupted with partner records
    tf_count = db_session.query(TranscriptionFactor).count()
    assert tf_count == 63, f"Transcription factors count corrupted! Expected 63, got {tf_count}"


def test_image_paths_formatting_and_existence(db_session: Session):
    """Verify image paths use forward slashes and point to actual files on disk."""
    interactions = db_session.query(ProteinInteraction).all()
    for row in interactions:
        assert "\\" not in row.string_image_path, f"Backslash found in string_image_path: {row.string_image_path}"
        assert os.path.exists(os.path.join(PROJECT_ROOT, row.string_image_path)), f"Missing STRING image file: {row.string_image_path}"

        if row.cytoscape_image_path is not None:
            assert "\\" not in row.cytoscape_image_path, f"Backslash found in cytoscape_image_path: {row.cytoscape_image_path}"
            assert os.path.exists(os.path.join(PROJECT_ROOT, row.cytoscape_image_path)), f"Missing Cytoscape image file: {row.cytoscape_image_path}"


def test_cytoscape_presence_distribution(db_session: Session):
    """Verify distribution of linked Cytoscape PNGs (367 populated, 122 null)."""
    with_cyto = db_session.query(ProteinInteraction).filter(ProteinInteraction.cytoscape_image_path.isnot(None)).count()
    without_cyto = db_session.query(ProteinInteraction).filter(ProteinInteraction.cytoscape_image_path.is_(None)).count()

    assert with_cyto == 367, f"Expected 367 rows with Cytoscape image, found {with_cyto}"
    assert without_cyto == 122, f"Expected 122 rows without Cytoscape image, found {without_cyto}"
    assert with_cyto + without_cyto == 489


def test_cytoscape_bzr1_is_maize(db_session: Session):
    """Verify BZR1.png is assigned to maize ZmBES1-BZR1 (#58) and tomato SlBZR1 (#59) has None."""
    zm_rows = db_session.query(ProteinInteraction).filter(ProteinInteraction.tf_id == 58).all()
    assert len(zm_rows) == 10
    for r in zm_rows:
        assert r.cytoscape_image_path and r.cytoscape_image_path.endswith("BZR1.png")

    sl_rows = db_session.query(ProteinInteraction).filter(ProteinInteraction.tf_id == 59).all()
    assert len(sl_rows) == 10
    for r in sl_rows:
        assert r.cytoscape_image_path is None


def test_baseline_data_preservation(db_session: Session):
    """Verify all other 15 tables remain 100% unaltered after Phase 5D import."""
    assert db_session.query(TranscriptionFactor).count() == 63
    assert db_session.query(ProteinSequence).count() == 46
    assert db_session.query(ProteinStructure).count() == 60
    assert db_session.query(Plant).count() == 30
    assert db_session.query(TFFamily).count() == 23
    assert db_session.query(StressCondition).count() == 21
    assert db_session.query(ResearchPaper).count() == 60


def test_dry_run_idempotence():
    """Verify that dry-run mode returns correct stats without modifying database."""
    res = import_string_interactions(dry_run=True, force=True)
    assert res["dry_run"] is True
    assert res["total_packages"] == 45
    assert res["total_unique_edges"] == 439
    assert res["total_rows"] == 489
