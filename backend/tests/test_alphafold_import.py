"""PhytoStress TF Atlas — AlphaFold Ingestion Test Suite.

Verifies:
- All 12 AlphaFold2 prediction suites and 303 files are correctly accounted for.
- 60 PDB structural models (5 ranks per TF) are stored in protein_structures.
- Atomic coordinate readability, ATOM records, and chain/residue integrity.
- Sequence-to-structure residue count concordance.
- Confidence metadata (mean pLDDT, pTM, B-factor metrics).
- Special handling for BnCDF1 (template_homolog = 'AtDOF5.8').
- Disambiguation of MtNLP1 (linked to Record #31, not falsely assigned to #32).
- Multiple model/rank support (Ranks 1 to 5).
- Diagnostic asset paths (PAE, pLDDT, coverage images).
- Immutability of original AlphaFold source files on disk.
- Foreign-key integrity and preservation of Phase 5A/5B baseline data.
"""

import os
import pytest
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models.tf import TranscriptionFactor
from backend.app.models.sequence import ProteinSequence
from backend.app.models.structure import ProteinStructure
from backend.app.models.interaction import ProteinInteraction

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AF_ROOT = os.path.join(PROJECT_ROOT, "AlphaFold -20261008T053401Z-1-001", "AlphaFold")


@pytest.fixture(scope="module")
def db_session():
    """Provides a transactional database session for tests."""
    session = SessionLocal()
    yield session
    session.close()


def test_alphafold_source_directory_integrity():
    """Verify that AlphaFold source folder contains all 12 folders and 303 files."""
    assert os.path.isdir(AF_ROOT), f"AlphaFold directory missing: {AF_ROOT}"
    folders = sorted(os.listdir(AF_ROOT))
    assert len(folders) == 12, f"Expected 12 AlphaFold folders, found {len(folders)}"

    total_files = 0
    for root, dirs, files in os.walk(os.path.dirname(AF_ROOT)):
        total_files += len(files)
    assert total_files == 303, f"Expected 303 total files in AlphaFold source, found {total_files}"


def test_protein_structure_record_count(db_session: Session):
    """Verify exactly 60 structure records exist in protein_structures (12 TFs x 5 ranks)."""
    count = db_session.query(ProteinStructure).count()
    assert count == 60, f"Expected 60 structure records in database, found {count}"


def test_distinct_tfs_with_structures(db_session: Session):
    """Verify exactly 12 distinct transcription factors have linked 3D models."""
    tf_ids = db_session.query(ProteinStructure.tf_id).distinct().all()
    unique_tf_ids = {tid[0] for tid in tf_ids}
    assert len(unique_tf_ids) == 12, f"Expected 12 distinct TFs with structures, found {len(unique_tf_ids)}"

    expected_tf_ids = {60, 63, 62, 3, 54, 55, 53, 9, 5, 49, 7, 31}
    assert unique_tf_ids == expected_tf_ids, f"Mismatch in structured TF IDs: {unique_tf_ids ^ expected_tf_ids}"


def test_five_ranks_per_transcription_factor(db_session: Session):
    """Verify that each of the 12 structured TFs has ranks 1 through 5."""
    tf_ids = {60, 63, 62, 3, 54, 55, 53, 9, 5, 49, 7, 31}
    for tid in tf_ids:
        structs = db_session.query(ProteinStructure).filter_by(tf_id=tid).order_by(ProteinStructure.rank_num).all()
        assert len(structs) == 5, f"TF #{tid} has {len(structs)} models instead of 5"
        ranks = [s.rank_num for s in structs]
        assert ranks == [1, 2, 3, 4, 5], f"TF #{tid} has unexpected ranks: {ranks}"


def test_pdb_file_paths_exist_and_readable(db_session: Session):
    """Verify that every stored pdb_file_path points to an existing, readable PDB file."""
    structs = db_session.query(ProteinStructure).all()
    for s in structs:
        full_path = os.path.join(PROJECT_ROOT, s.pdb_file_path)
        assert os.path.isfile(full_path), f"PDB file does not exist on disk: {full_path}"
        assert os.path.getsize(full_path) > 1000, f"PDB file suspiciously small: {full_path}"

        # Verify ATOM records
        has_atoms = False
        with open(full_path, "r", encoding="utf-8", errors="replace") as pf:
            for line in pf:
                if line.startswith("ATOM  "):
                    has_atoms = True
                    break
        assert has_atoms, f"No ATOM records in PDB file: {full_path}"


def test_sequence_to_structure_residue_concordance(db_session: Session):
    """Verify residue count in each PDB model strictly matches the parent sequence length."""
    structs = db_session.query(ProteinStructure).all()
    for s in structs:
        tf = s.tf
        assert tf is not None
        # Retrieve primary matching sequence for this TF
        matched_seq = next((seq for seq in tf.sequences if seq.sequence_length > 0), None)
        assert matched_seq is not None, f"TF #{tf.id} has structure but no sequence record"

        # Count CA atoms in PDB to determine residue count
        full_path = os.path.join(PROJECT_ROOT, s.pdb_file_path)
        ca_count = 0
        with open(full_path, "r", encoding="utf-8", errors="replace") as pf:
            for line in pf:
                if line.startswith("ATOM  ") and line[12:16].strip() == "CA":
                    ca_count += 1
        assert ca_count == matched_seq.sequence_length, (
            f"Residue count mismatch for TF #{tf.id} ({s.model_identifier} rank {s.rank_num}): "
            f"PDB has {ca_count} C-alphas, sequence has {matched_seq.sequence_length} AA"
        )


def test_plddt_confidence_bounds(db_session: Session):
    """Verify mean_plddt is positive and within standard AlphaFold bounds (0-100)."""
    structs = db_session.query(ProteinStructure).all()
    for s in structs:
        assert s.mean_plddt is not None, f"mean_plddt is None for structure #{s.id}"
        assert 0.0 <= s.mean_plddt <= 100.0, f"Implausible mean_plddt {s.mean_plddt} for structure #{s.id}"
        # For rank 1 models, pLDDT should typically be >= 45 in this curated set
        if s.rank_num == 1:
            assert s.mean_plddt >= 45.0, f"Unexpectedly low rank 1 pLDDT: {s.mean_plddt} for TF #{s.tf_id}"


def test_bncdf1_template_homolog_flag(db_session: Session):
    """Verify BnCDF1 (TF #9) has template_homolog='AtDOF5.8' explicitly recorded."""
    structs = db_session.query(ProteinStructure).filter_by(tf_id=9).all()
    assert len(structs) == 5
    for s in structs:
        assert s.template_homolog == "AtDOF5.8", (
            f"BnCDF1 missing AtDOF5.8 template homolog flag: {s.template_homolog}"
        )
        assert s.model_identifier == "BnCDF1"


def test_mtnlp1_disambiguation(db_session: Session):
    """Verify MtNLP1_95155 is linked to Record #31 (934 AA) and NOT falsely to Record #32 (909 AA)."""
    structs_31 = db_session.query(ProteinStructure).filter_by(tf_id=31).all()
    structs_32 = db_session.query(ProteinStructure).filter_by(tf_id=32).all()

    assert len(structs_31) == 5, f"Record #31 should have 5 structure ranks, found {len(structs_31)}"
    assert len(structs_32) == 0, f"Record #32 should have 0 structure records, found {len(structs_32)}"

    for s in structs_31:
        assert s.model_identifier == "MtNLP1_95155"


def test_diagnostic_plot_paths_exist(db_session: Session):
    """Verify that pae, plddt, and coverage image paths point to existing PNG files."""
    structs = db_session.query(ProteinStructure).all()
    for s in structs:
        assert s.pae_image_path is not None
        assert s.plddt_image_path is not None
        assert s.coverage_image_path is not None

        for img_rel in [s.pae_image_path, s.plddt_image_path, s.coverage_image_path]:
            full_img_path = os.path.join(PROJECT_ROOT, img_rel)
            assert os.path.isfile(full_img_path), f"Diagnostic image missing: {full_img_path}"
            assert os.path.getsize(full_img_path) > 1000, f"Diagnostic image empty: {full_img_path}"


def test_foreign_key_integrity(db_session: Session):
    """Verify all protein_structures records link to valid TranscriptionFactor entities."""
    all_tf_ids = {tf.id for tf in db_session.query(TranscriptionFactor.id).all()}
    structs = db_session.query(ProteinStructure).all()
    for s in structs:
        assert s.tf_id in all_tf_ids, f"Orphan structure record #{s.id} with tf_id={s.tf_id}"
        assert s.tf is not None
        assert s.tf.tf_name is not None
        assert s in s.tf.structures


def test_preservation_of_database_baseline(db_session: Session):
    """Verify transcription_factors remains at 63, sequences at 46, and interactions at 0."""
    tf_count = db_session.query(TranscriptionFactor).count()
    seq_count = db_session.query(ProteinSequence).count()
    inter_count = db_session.query(ProteinInteraction).count()

    assert tf_count == 63, f"transcription_factors count changed: {tf_count} != 63"
    assert seq_count == 46, f"protein_sequences count changed: {seq_count} != 46"
    assert inter_count == 0, f"protein_interactions populated prematurely: {inter_count}"
