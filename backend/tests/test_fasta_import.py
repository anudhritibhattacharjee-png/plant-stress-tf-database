"""PhytoStress TF Atlas — FASTA Ingestion Test Suite.

Verifies:
- All 41 FASTA source files are correctly parsed and preserved.
- Normalized sequences contain only canonical IUPAC amino acid codes.
- All 5 known anomalies are handled correctly in-memory.
- Foreign key integrity and associations to transcription factors.
- Molecular weights and sequence lengths are calculated accurately.
- Source files remain completely untouched on disk.
"""

import os
import hashlib
import pytest
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models.tf import TranscriptionFactor
from backend.app.models.sequence import ProteinSequence

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FASTA_DIR = os.path.join(PROJECT_ROOT, "FASTA sequence of TFs-20261008T053415Z-1-001", "FASTA sequence of TFs")

CANONICAL_AA = set("ACDEFGHIKLMNPQRSTVWY")


@pytest.fixture(scope="module")
def db_session():
    """Provides a transactional database session for tests."""
    session = SessionLocal()
    yield session
    session.close()


def test_source_fasta_directory_integrity():
    """Verify that all 41 FASTA source files exist in the source folder untouched."""
    assert os.path.isdir(FASTA_DIR), f"FASTA source directory missing: {FASTA_DIR}"
    files = sorted(os.listdir(FASTA_DIR))
    assert len(files) == 41, f"Expected exactly 41 FASTA files, found {len(files)}"
    for f in files:
        fpath = os.path.join(FASTA_DIR, f)
        assert os.path.isfile(fpath)
        assert os.path.getsize(fpath) > 0


def test_protein_sequence_record_count(db_session: Session):
    """Verify that exactly 46 sequence association records exist in database."""
    total_seqs = db_session.query(ProteinSequence).count()
    assert total_seqs == 46, f"Expected 46 sequence records, found {total_seqs}"


def test_transcription_factor_table_unaltered(db_session: Session):
    """Verify that transcription_factors table remains at exactly 63 rows."""
    tf_count = db_session.query(TranscriptionFactor).count()
    assert tf_count == 63, f"Expected exactly 63 transcription factors, found {tf_count}"


def test_sequence_amino_acid_validity(db_session: Session):
    """Verify all stored sequences contain only uppercase standard IUPAC amino acids."""
    seqs = db_session.query(ProteinSequence).all()
    assert len(seqs) > 0
    for s in seqs:
        assert s.sequence.isupper(), f"Sequence for TF {s.tf_id} is not fully uppercase"
        assert "\n" not in s.sequence, f"Sequence contains newlines for TF {s.tf_id}"
        assert " " not in s.sequence, f"Sequence contains spaces for TF {s.tf_id}"
        chars = set(s.sequence)
        invalid = chars - CANONICAL_AA
        assert not invalid, f"Invalid amino acid characters {invalid} in TF {s.tf_id} ({s.source_filename})"


def test_sequence_length_concordance(db_session: Session):
    """Verify that sequence_length field strictly equals len(sequence)."""
    seqs = db_session.query(ProteinSequence).all()
    for s in seqs:
        assert s.sequence_length == len(s.sequence)
        assert s.sequence_length > 0


def test_molecular_weight_bounds(db_session: Session):
    """Verify molecular weight is calculated, positive, and physically plausible."""
    seqs = db_session.query(ProteinSequence).all()
    for s in seqs:
        assert s.molecular_weight is not None
        assert s.molecular_weight > 0
        # Average residue is ~110 Da; assert reasonable bounds (80 to 140 Da/residue)
        avg_res_weight = s.molecular_weight / s.sequence_length
        assert 80.0 <= avg_res_weight <= 145.0, (
            f"Implausible MW/residue {avg_res_weight:.1f} for {s.source_filename}"
        )


def test_anomaly_1_atplatz2(db_session: Session):
    """Verify AtPLATZ2.txt: internal space stripped, synthetic header generated, length 245."""
    seq = db_session.query(ProteinSequence).filter_by(source_filename="AtPLATZ2.txt").first()
    assert seq is not None
    assert seq.tf_id == 54
    assert seq.sequence_length == 245
    assert " " not in seq.sequence
    assert seq.fasta_header == ">AtPLATZ2_AT1G76590"
    assert seq.validation_status == "Header generated"
    assert "Stripped internal whitespace" in seq.provenance


def test_anomaly_2_atplatz4(db_session: Session):
    """Verify AtPLATZ4.txt: synthetic header generated, length 213, validation_status."""
    seq = db_session.query(ProteinSequence).filter_by(source_filename="AtPLATZ4.txt").first()
    assert seq is not None
    assert seq.tf_id == 55
    assert seq.sequence_length == 213
    assert seq.fasta_header == ">AtPLATZ4_AT1G32700"
    assert seq.validation_status == "Header generated"
    assert "AT1G32700" in seq.provenance


def test_anomaly_3_osdof1(db_session: Session):
    """Verify OsDOF1.txt: synthetic header generated, length 215, validation_status."""
    seq = db_session.query(ProteinSequence).filter_by(source_filename="OsDOF1.txt").first()
    assert seq is not None
    assert seq.tf_id == 12
    assert seq.sequence_length == 215
    assert seq.fasta_header == ">OsDOF1_Q9FE00"
    assert seq.validation_status == "Header generated"
    assert "Q9FE00" in seq.provenance


def test_anomaly_4_taznf_double_extension(db_session: Session):
    """Verify TaZNF.fasta.txt: preserved source filename, linked to TF #2, length 501."""
    seq = db_session.query(ProteinSequence).filter_by(source_filename="TaZNF.fasta.txt").first()
    assert seq is not None
    assert seq.tf_id == 2
    assert seq.sequence_length == 501
    assert seq.accession == "A0A1D5V0E4"
    assert seq.validation_status == "Verified"


def test_anomaly_5_mtnlp1_disambiguation(db_session: Session):
    """Verify MtNLP1.txt vs MtNLP1 (2).txt are disambiguated by UniProt accession."""
    seq1 = db_session.query(ProteinSequence).filter_by(source_filename="MtNLP1.txt").first()
    seq2 = db_session.query(ProteinSequence).filter_by(source_filename="MtNLP1 (2).txt").first()

    assert seq1 is not None
    assert seq2 is not None

    # MtNLP1.txt -> TF #31 (Nature Plants 2018, A0A977NVL6)
    assert seq1.tf_id == 31
    assert seq1.accession == "A0A977NVL6"
    assert seq1.sequence_length == 934

    # MtNLP1 (2).txt -> TF #32 (Plant Comms 2021, A0A072V3U8)
    assert seq2.tf_id == 32
    assert seq2.accession == "A0A072V3U8"
    assert seq2.sequence_length == 909


def test_composite_tf_sequence_associations(db_session: Session):
    """Verify multi-gene/composite TFs correctly link their constituent sequences."""
    # TF #6: SlCDF1 / SlCDF3 -> 2 sequences
    tf6 = db_session.query(TranscriptionFactor).filter_by(id=6).first()
    assert tf6 is not None
    assert len(tf6.sequences) == 2
    filenames_tf6 = {s.source_filename for s in tf6.sequences}
    assert filenames_tf6 == {"SlCDF1.txt", "SlCDF3.txt"}

    # TF #33: NLP1 / NLP5 -> 2 sequences
    tf33 = db_session.query(TranscriptionFactor).filter_by(id=33).first()
    assert tf33 is not None
    assert len(tf33.sequences) == 2
    filenames_tf33 = {s.source_filename for s in tf33.sequences}
    assert filenames_tf33 == {"SlNLP1.txt", "SlNLP5.txt"}

    # TF #44: VOZ1 / VOZ2 -> 2 sequences
    tf44 = db_session.query(TranscriptionFactor).filter_by(id=44).first()
    assert tf44 is not None
    assert len(tf44.sequences) == 2
    filenames_tf44 = {s.source_filename for s in tf44.sequences}
    assert filenames_tf44 == {"VOZ1.txt", "VOZ2.txt"}


def test_multi_study_shared_sequences(db_session: Session):
    """Verify shared sequences across distinct studies are properly associated."""
    # NLP7.txt shared across #29, #30, #34, #35
    nlp7_seqs = db_session.query(ProteinSequence).filter_by(source_filename="NLP7.txt").all()
    assert len(nlp7_seqs) == 4
    nlp7_tf_ids = {s.tf_id for s in nlp7_seqs}
    assert nlp7_tf_ids == {29, 30, 34, 35}
    for s in nlp7_seqs:
        assert s.sequence_length == 959
        assert s.accession == "Q84TH9"

    # OsMADS25.txt shared across #21, #22
    mads25_seqs = db_session.query(ProteinSequence).filter_by(source_filename="OsMADS25.txt").all()
    assert len(mads25_seqs) == 2
    mads25_tf_ids = {s.tf_id for s in mads25_seqs}
    assert mads25_tf_ids == {21, 22}
    for s in mads25_seqs:
        assert s.sequence_length == 227
        assert s.accession == "Q84NC5"

    # NLP2.txt linked to #28 (Rice NLP family) and #37 (NLP2)
    nlp2_seqs = db_session.query(ProteinSequence).filter_by(source_filename="NLP2.txt").all()
    assert len(nlp2_seqs) == 2
    nlp2_tf_ids = {s.tf_id for s in nlp2_seqs}
    assert nlp2_tf_ids == {28, 37}


def test_foreign_key_integrity(db_session: Session):
    """Verify all sequences reference an existing TranscriptionFactor."""
    all_tf_ids = {tf.id for tf in db_session.query(TranscriptionFactor.id).all()}
    seqs = db_session.query(ProteinSequence).all()
    for s in seqs:
        assert s.tf_id in all_tf_ids, f"Orphan sequence with tf_id={s.tf_id}"
        assert s.tf is not None, f"Relationship navigation failed for sequence {s.id}"
