import json
import pytest
from backend.app.models import (
    TranscriptionFactor, Plant, TFFamily, StressCondition,
    TFStressAssociation, TFIdentifier, ResearchPaper,
    TFPaperAssociation, TargetGene, TFTargetAssociation,
    Pathway, TFPathwayAssociation, ImportAudit,
    ProteinSequence, ProteinStructure, ProteinInteraction
)
from scripts.import_data import run_full_import


@pytest.fixture(scope="function")
def populated_db(test_db):
    """Fixture providing an in-memory SQLite database populated with all 63 records."""
    run_full_import(
        json_path="data/raw/prototype_63_records.json",
        session=test_db,
        dry_run=False,
        reset_existing=False
    )
    return test_db


def test_full_dataset_entity_counts(populated_db):
    """Verify exact counts of all normalized tables for the full 63-record dataset."""
    assert populated_db.query(TranscriptionFactor).count() == 63
    assert populated_db.query(Plant).count() == 30
    assert populated_db.query(TFFamily).count() == 23
    assert populated_db.query(StressCondition).count() == 21
    assert populated_db.query(TFStressAssociation).count() == 89
    assert populated_db.query(TFIdentifier).count() == 92
    assert populated_db.query(ResearchPaper).count() == 60
    assert populated_db.query(TFPaperAssociation).count() == 63
    assert populated_db.query(TargetGene).count() == 75
    assert populated_db.query(TFTargetAssociation).count() == 76
    assert populated_db.query(Pathway).count() == 110
    assert populated_db.query(TFPathwayAssociation).count() == 121
    assert populated_db.query(ImportAudit).count() >= 1

    # Asset tables must remain empty in this phase
    assert populated_db.query(ProteinSequence).count() == 0
    assert populated_db.query(ProteinStructure).count() == 0
    assert populated_db.query(ProteinInteraction).count() == 0


def test_all_63_source_records_present(populated_db):
    """Verify that every single source record from prototype_63_records.json is in the database."""
    with open("data/raw/prototype_63_records.json", "r", encoding="utf-8") as f:
        source_records = json.load(f)

    assert len(source_records) == 63
    for idx, rec in enumerate(source_records, start=1):
        tf = populated_db.query(TranscriptionFactor).filter(
            TranscriptionFactor.source_row_index == idx
        ).first()
        assert tf is not None, f"Source record #{idx} disappeared from database!"
        assert tf.tf_name == rec.get("TF / TF family").strip()
        assert tf.raw_stress == rec.get("Stress condition").strip()


def test_html_only_records_reconciled(populated_db):
    """Verify that the two HTML-only records are properly ingested with source provenance."""
    # Record 30: NLP7 in Arabidopsis (Nature Communications 2013)
    rec30 = populated_db.query(TranscriptionFactor).filter(
        TranscriptionFactor.source_row_index == 30
    ).first()
    assert rec30 is not None
    assert rec30.tf_name == "NLP7"
    assert rec30.plant.common_name == "Arabidopsis"
    assert rec30.source_dataset == "html_supplement"
    assert rec30.papers[0].doi == "10.1038/ncomms2650"

    # Record 36: NLP family in Rice (BMC Plant Biology 2019)
    rec36 = populated_db.query(TranscriptionFactor).filter(
        TranscriptionFactor.source_row_index == 36
    ).first()
    assert rec36 is not None
    assert rec36.tf_name == "NLP family"
    assert rec36.plant.common_name == "Rice"
    assert rec36.source_dataset == "html_supplement"
    assert rec36.papers[0].doi == "10.1186/s12870-019-1922-8"
    assert rec36.is_verified is False


def test_repeated_tf_studies_not_collapsed(populated_db):
    """Verify that biologically distinct studies on the same TF are not incorrectly collapsed."""
    # NLP7 has 3 independent studies
    nlp7_records = populated_db.query(TranscriptionFactor).filter(
        TranscriptionFactor.tf_name == "NLP7"
    ).all()
    assert len(nlp7_records) == 3

    # OsMADS25 has 2 independent studies
    mads25_records = populated_db.query(TranscriptionFactor).filter(
        TranscriptionFactor.tf_name == "OsMADS25"
    ).all()
    assert len(mads25_records) == 2

    # NLP1 has 2 independent studies
    nlp1_records = populated_db.query(TranscriptionFactor).filter(
        TranscriptionFactor.tf_name == "NLP1"
    ).all()
    assert len(nlp1_records) == 2

    # NLP family has 3 independent studies
    nlp_fam_records = populated_db.query(TranscriptionFactor).filter(
        TranscriptionFactor.tf_name == "NLP family"
    ).all()
    assert len(nlp_fam_records) == 3


def test_composite_tf_names_preserved(populated_db):
    """Verify that composite TF designations are retained verbatim."""
    composite_tfs = [
        "SlCDF1 / SlCDF3",
        "BpDOF4 / BpDOF11 / BpDOF17",
        "MADS-box family",
        "NLP1 / NLP5",
        "VOZ1 / VOZ2",
        "TaSPL6-A/B/D",
        "ZmBES1/BZR1-1",
        "SlBZR1 / SlBZR1D"
    ]
    db_names = {t.tf_name for t in populated_db.query(TranscriptionFactor).all()}
    for c_tf in composite_tfs:
        assert c_tf in db_names, f"Composite TF '{c_tf}' not preserved!"


def test_unverified_identifiers_zero_fabrication(populated_db):
    """Verify that all 12 unverified/uncertain records have is_verified=False and zero fabricated UniProt IDs."""
    unverified_tfs = populated_db.query(TranscriptionFactor).filter(
        TranscriptionFactor.is_verified == False
    ).all()
    assert len(unverified_tfs) == 12

    for tf in unverified_tfs:
        if tf.tf_name == "MADS-box family":
            assert len(tf.identifiers) == 0
        elif tf.source_row_index == 36:
            # Candidate accessions
            for ident in tf.identifiers:
                assert ident.verification_status == "Candidate / Uncertain"
        else:
            for ident in tf.identifiers:
                assert ident.verification_status == "Not verified"
                assert ident.identifier_type != "UniProtKB"


def test_foreign_key_and_orphan_integrity(populated_db):
    """Verify that all foreign keys reference valid entities and no orphan records exist."""
    tf_ids = {t.id for t in populated_db.query(TranscriptionFactor.id).all()}
    plant_ids = {p.id for p in populated_db.query(Plant.id).all()}
    family_ids = {f.id for f in populated_db.query(TFFamily.id).all()}

    for tf in populated_db.query(TranscriptionFactor).all():
        assert tf.plant_id in plant_ids
        assert tf.family_id in family_ids

    for ident in populated_db.query(TFIdentifier).all():
        assert ident.tf_id in tf_ids


def test_full_import_duplicate_safety(populated_db):
    """Verify that re-running full import on populated database safely skips existing records."""
    res = run_full_import(
        json_path="data/raw/prototype_63_records.json",
        session=populated_db,
        dry_run=False,
        reset_existing=False
    )
    assert res["status"] == "SKIPPED_EXISTING"
    assert res["records_inserted"] == 0
    assert populated_db.query(TranscriptionFactor).count() == 63
