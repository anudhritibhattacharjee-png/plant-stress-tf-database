import json
import pytest
from sqlalchemy import inspect
from backend.app.models import (
    TranscriptionFactor, Plant, TFFamily, StressCondition,
    TFStressAssociation, TFIdentifier, ResearchPaper,
    TFPaperAssociation, TargetGene, TFTargetAssociation,
    Pathway, TFPathwayAssociation, ImportAudit
)
from scripts.import_test_data import run_test_import


def test_import_completes_successfully(test_db):
    """Verify that run_test_import completes and reports SUCCESS on clean database."""
    res = run_test_import(json_path="data/test/test_records.json", session=test_db, force=False)
    assert res["status"] == "SUCCESS"
    assert res["records_processed"] == 5
    assert res["records_inserted"] == 5


def test_expected_entity_counts(test_db):
    """Verify exact counts of all normalized tables after importing 5 test records."""
    run_test_import(json_path="data/test/test_records.json", session=test_db)
    
    # Core entities
    assert test_db.query(TranscriptionFactor).count() == 5
    assert test_db.query(Plant).count() == 4  # Apple, Arabidopsis, Rice, Tomato (deduplicated)
    assert test_db.query(TFFamily).count() == 3  # DOF, DOF / Cycling DOF Factor (CDF), MADS-box (deduplicated)
    
    # Stress & Junctions
    assert test_db.query(StressCondition).count() == 6
    assert test_db.query(TFStressAssociation).count() == 9
    
    # Identifiers
    assert test_db.query(TFIdentifier).count() == 10
    
    # Literature
    assert test_db.query(ResearchPaper).count() == 5
    assert test_db.query(TFPaperAssociation).count() == 5
    
    # Targets & Pathways
    assert test_db.query(TargetGene).count() == 9
    assert test_db.query(TFTargetAssociation).count() == 9
    assert test_db.query(Pathway).count() == 10
    assert test_db.query(TFPathwayAssociation).count() == 10
    
    # Audit log
    assert test_db.query(ImportAudit).count() == 1


def test_case_a_simple_tf(test_db):
    """CASE A: Verify simple single-identifier TF (MdDOF54 in Apple)."""
    run_test_import(json_path="data/test/test_records.json", session=test_db)
    
    tf = test_db.query(TranscriptionFactor).filter(TranscriptionFactor.tf_name == "MdDOF54").first()
    assert tf is not None
    assert tf.plant.common_name == "Apple"
    assert tf.family.name == "DOF"
    assert tf.regulatory_effect == "Positive"
    assert tf.is_verified is True
    
    # Single verified UniProt identifier
    assert len(tf.identifiers) == 1
    ident = tf.identifiers[0]
    assert ident.identifier_type == "UniProtKB"
    assert ident.identifier_value == "A0A498K1B1"
    assert ident.verification_status == "Verified"
    assert ident.is_primary is True
    
    # Single stress condition
    assert len(tf.stresses) == 1
    assert tf.stresses[0].stress_name == "Drought"
    
    # Research paper
    assert len(tf.papers) == 1
    assert tf.papers[0].doi == "10.1038/s41438-020-00419-5"
    assert tf.papers[0].year == 2020
    
    # Target genes
    target_symbols = {t.gene_symbol for t in tf.targets}
    assert {"MdAPX3", "MdACO1", "MdTGD2", "MdAPL3"}.issubset(target_symbols)


def test_case_b_multiple_stresses(test_db):
    """CASE B: Verify TF associated with multiple stresses (CDF3 in Arabidopsis)."""
    run_test_import(json_path="data/test/test_records.json", session=test_db)
    
    tf = test_db.query(TranscriptionFactor).filter(TranscriptionFactor.tf_name == "CDF3").first()
    assert tf is not None
    assert tf.plant.common_name == "Arabidopsis"
    
    # Raw stress preserved verbatim
    assert tf.raw_stress == "Drought, cold, osmotic stress"
    
    # Stresses normalized into 3 distinct conditions
    stress_names = {s.stress_name for s in tf.stresses}
    assert stress_names == {"Drought", "Cold", "Osmotic stress"}
    assert len(tf.stress_associations) == 3


def test_case_c_multiple_identifiers(test_db):
    """CASE C: Verify TF containing multiple UniProt accessions (OsMADS25 in Rice)."""
    run_test_import(json_path="data/test/test_records.json", session=test_db)
    
    tf = test_db.query(TranscriptionFactor).filter(TranscriptionFactor.tf_name == "OsMADS25").first()
    assert tf is not None
    assert tf.plant.common_name == "Rice"
    
    # 4 UniProt accessions parsed from a single cell
    assert len(tf.identifiers) == 4
    acc_values = {i.identifier_value for i in tf.identifiers}
    assert acc_values == {"Q0JEA7", "Q7XVR2", "Q84NC5", "Q01ME4"}
    
    for ident in tf.identifiers:
        assert ident.identifier_type == "UniProtKB"
        assert ident.verification_status == "Verified"
        if ident.identifier_value == "Q84NC5":
            assert ident.is_primary is True
        else:
            assert ident.is_primary is False
        assert ident.raw_supplied_text == "Q0JEA7, Q7XVR2, Q84NC5, Q01ME4"


def test_case_d_composite_tf_name(test_db):
    """CASE D: Verify composite TF name preserved verbatim (SlCDF1 / SlCDF3 in Tomato)."""
    run_test_import(json_path="data/test/test_records.json", session=test_db)
    
    tf = test_db.query(TranscriptionFactor).filter(TranscriptionFactor.tf_name == "SlCDF1 / SlCDF3").first()
    assert tf is not None
    assert tf.raw_supplied_tf == "SlCDF1 / SlCDF3"
    assert tf.raw_stress == "Salt, drought"
    
    # Check constituent gene models
    solyc_ids = {i.identifier_value for i in tf.identifiers}
    assert solyc_ids == {"Solyc02g087980", "Solyc06g074350"}
    for i in tf.identifiers:
        assert i.identifier_type == "Sol Genomics Network"
        assert i.verification_status == "Verified"
    
    # Check shared entities deduplication
    tomato_plant = test_db.query(Plant).filter(Plant.common_name == "Tomato").first()
    assert tf.plant_id == tomato_plant.id
    
    cdf_family = test_db.query(TFFamily).filter(TFFamily.name == "DOF / Cycling DOF Factor (CDF)").first()
    assert tf.family_id == cdf_family.id


def test_case_e_unverified_identifier(test_db):
    """CASE E: Verify unverified identifier handling without fabrication (SlDOF22 in Tomato)."""
    run_test_import(json_path="data/test/test_records.json", session=test_db)
    
    tf = test_db.query(TranscriptionFactor).filter(TranscriptionFactor.tf_name == "SlDOF22").first()
    assert tf is not None
    assert tf.is_verified is False
    assert "Not verified" in (tf.notes or "")
    
    # Verify no fabricated UniProt ID exists
    for ident in tf.identifiers:
        assert ident.identifier_type != "UniProtKB"
        assert ident.verification_status == "Not verified"
        assert ident.raw_supplied_text == "Not verified"
        
    ident_types = {i.identifier_type: i.identifier_value for i in tf.identifiers}
    assert ident_types.get("NCBI Gene") == "101255410"
    assert ident_types.get("Gene symbol") == "SlDof22"


def test_provenance_and_audit(test_db):
    """Verify provenance metadata and import audit logging."""
    run_test_import(json_path="data/test/test_records.json", session=test_db)
    
    audit = test_db.query(ImportAudit).first()
    assert audit is not None
    assert audit.source_name == "data/test/test_records.json"
    assert audit.source_type == "JSON"
    assert audit.records_processed == 5
    assert audit.records_inserted == 5
    assert audit.status == "SUCCESS"
    assert len(audit.source_hash) == 64
    
    # Check summary JSON
    summary = json.loads(audit.validation_summary)
    assert summary["imported_count"] == 5
    assert "SlDOF22" in summary["tfs"]
    assert "MdDOF54" in summary["tfs"]


def test_duplicate_safety_idempotency(test_db):
    """Verify that re-running the importer on an already-imported database safely skips duplicates."""
    # First import
    res1 = run_test_import(json_path="data/test/test_records.json", session=test_db)
    assert res1["status"] == "SUCCESS"
    assert test_db.query(TranscriptionFactor).count() == 5
    
    # Second import (without force)
    res2 = run_test_import(json_path="data/test/test_records.json", session=test_db, force=False)
    assert res2["status"] == "SKIPPED_EXISTING"
    assert res2["records_inserted"] == 0
    
    # Total row counts must NOT have duplicated
    assert test_db.query(TranscriptionFactor).count() == 5
    assert test_db.query(Plant).count() == 4
    assert test_db.query(TFFamily).count() == 3
    assert test_db.query(TFIdentifier).count() == 10
