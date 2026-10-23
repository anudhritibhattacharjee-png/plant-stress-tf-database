import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from backend.app.models import (
    Base, TFFamily, Plant, TranscriptionFactor,
    StressCondition, TFStressAssociation, TFIdentifier,
    ResearchPaper, TFPaperAssociation, TargetGene,
    TFTargetAssociation, Pathway, TFPathwayAssociation,
    ProteinSequence, ProteinStructure, ProteinInteraction,
    ImportAudit
)

def test_all_16_tables_exist(test_db):
    """Verify that all 16 normalized tables are registered and created in the database."""
    engine = test_db.get_bind()
    inspector = inspect(engine)
    created_tables = set(inspector.get_table_names())
    
    expected_tables = {
        "tf_families",
        "plants",
        "transcription_factors",
        "stress_conditions",
        "tf_stress_associations",
        "tf_identifiers",
        "research_papers",
        "tf_paper_associations",
        "target_genes",
        "tf_target_associations",
        "pathways",
        "tf_pathway_associations",
        "protein_sequences",
        "protein_structures",
        "protein_interactions",
        "import_audits"
    }
    
    missing = expected_tables - created_tables
    assert not missing, f"Missing tables in database: {missing}"
    assert len(expected_tables.intersection(created_tables)) == 16


def test_primary_keys_defined(test_db):
    """Verify that every table has a single integer primary key named 'id'."""
    engine = test_db.get_bind()
    inspector = inspect(engine)
    
    for table_name in inspector.get_table_names():
        pk = inspector.get_pk_constraint(table_name)
        assert pk is not None, f"Table '{table_name}' has no primary key"
        assert pk["constrained_columns"] == ["id"], f"Table '{table_name}' primary key is not ['id'], got {pk['constrained_columns']}"


def test_foreign_key_definitions(test_db):
    """Verify that all relational foreign keys are correctly defined."""
    engine = test_db.get_bind()
    inspector = inspect(engine)
    
    # Check transcription_factors FKs
    tf_fks = {fk["referred_table"]: fk["constrained_columns"] for fk in inspector.get_foreign_keys("transcription_factors")}
    assert "tf_families" in tf_fks
    assert "plants" in tf_fks
    assert tf_fks["tf_families"] == ["family_id"]
    assert tf_fks["plants"] == ["plant_id"]

    # Check tf_identifiers FK
    id_fks = {fk["referred_table"]: fk["constrained_columns"] for fk in inspector.get_foreign_keys("tf_identifiers")}
    assert "transcription_factors" in id_fks
    assert id_fks["transcription_factors"] == ["tf_id"]

    # Check junction FKs
    stress_fks = {fk["referred_table"]: fk["constrained_columns"] for fk in inspector.get_foreign_keys("tf_stress_associations")}
    assert "transcription_factors" in stress_fks
    assert "stress_conditions" in stress_fks

    paper_fks = {fk["referred_table"]: fk["constrained_columns"] for fk in inspector.get_foreign_keys("tf_paper_associations")}
    assert "transcription_factors" in paper_fks
    assert "research_papers" in paper_fks


def test_uniqueness_constraints(test_db):
    """Verify unique constraints prevent invalid duplicates while allowing legitimate biological repeats."""
    # 1. Family name must be unique
    fam1 = TFFamily(name="DOF", description="Dof family")
    test_db.add(fam1)
    test_db.commit()

    fam2 = TFFamily(name="DOF", description="Duplicate Dof")
    test_db.add(fam2)
    with pytest.raises(IntegrityError):
        test_db.commit()
    test_db.rollback()

    # 2. Stress name must be unique
    s1 = StressCondition(stress_name="Salt stress", stress_type="Abiotic")
    test_db.add(s1)
    test_db.commit()

    s2 = StressCondition(stress_name="Salt stress", stress_type="Abiotic")
    test_db.add(s2)
    with pytest.raises(IntegrityError):
        test_db.commit()
    test_db.rollback()


def test_scenarios_a_to_n(test_db):
    """Verify all 14 biological representation scenarios (A through N) using synthetic test data."""
    # Setup shared family and plant
    fam = TFFamily(name="Synthetic_DOF", description="Synthetic test family")
    plant = Plant(
        display_name="Synthetic Tomato (Solanum lycopersicum; transgenic test)",
        common_name="Synthetic Tomato",
        scientific_name="Solanum lycopersicum",
        ncbi_taxonomy_id=4081
    )
    test_db.add_all([fam, plant])
    test_db.commit()

    # Scenario A: TF with one UniProt ID
    tf_a = TranscriptionFactor(
        tf_name="SynTF_A",
        family_id=fam.id,
        plant_id=plant.id,
        regulatory_effect="Positive",
        raw_supplied_tf="SynTF_A"
    )
    test_db.add(tf_a)
    test_db.commit()
    id_a = TFIdentifier(
        tf_id=tf_a.id,
        identifier_type="UniProtKB",
        identifier_value="P12345",
        verification_status="Verified",
        is_primary=True
    )
    test_db.add(id_a)
    test_db.commit()
    assert len(tf_a.identifiers) == 1
    assert tf_a.identifiers[0].identifier_value == "P12345"

    # Scenario B: TF with multiple UniProt IDs
    tf_b = TranscriptionFactor(
        tf_name="SynTF_B",
        family_id=fam.id,
        plant_id=plant.id,
        regulatory_effect="Positive",
        raw_supplied_tf="SynTF_B"
    )
    test_db.add(tf_b)
    test_db.commit()
    for acc in ["Q0JEA7", "Q7XVR2", "Q84NC5", "Q01ME4"]:
        test_db.add(TFIdentifier(
            tf_id=tf_b.id,
            identifier_type="UniProtKB",
            identifier_value=acc,
            verification_status="Verified"
        ))
    test_db.commit()
    assert len(tf_b.identifiers) == 4

    # Scenario C: TF with no verified identifier
    tf_c = TranscriptionFactor(
        tf_name="SynTF_C",
        family_id=fam.id,
        plant_id=plant.id,
        is_verified=False,
        notes="Protein accession not verified in UniProt"
    )
    test_db.add(tf_c)
    test_db.commit()
    test_db.add(TFIdentifier(
        tf_id=tf_c.id,
        identifier_type="Gene symbol",
        identifier_value="SynTF_C",
        verification_status="Not verified",
        raw_supplied_text="Not verified"
    ))
    test_db.commit()
    assert tf_c.is_verified is False
    assert tf_c.identifiers[0].verification_status == "Not verified"

    # Scenario D: TF associated with multiple stresses
    s_drought = StressCondition(stress_name="Syn_Drought", stress_type="Abiotic")
    s_cold = StressCondition(stress_name="Syn_Cold", stress_type="Abiotic")
    s_osm = StressCondition(stress_name="Syn_Osmotic", stress_type="Abiotic")
    test_db.add_all([s_drought, s_cold, s_osm])
    test_db.commit()

    test_db.add_all([
        TFStressAssociation(tf_id=tf_a.id, stress_id=s_drought.id, specific_effect="Positive"),
        TFStressAssociation(tf_id=tf_a.id, stress_id=s_cold.id, specific_effect="Positive"),
        TFStressAssociation(tf_id=tf_a.id, stress_id=s_osm.id, specific_effect="Context-dependent")
    ])
    test_db.commit()
    test_db.refresh(tf_a)
    assert len(tf_a.stress_associations) == 3
    assert len(tf_a.stresses) == 3

    # Scenario E: TF associated with multiple research papers
    paper1 = ResearchPaper(title="Study 1 on SynTF_A", journal="J. Exp. Bot.", year=2020, doi="10.1000/1")
    paper2 = ResearchPaper(title="Study 2 on SynTF_A", journal="Plant J.", year=2023, doi="10.1000/2")
    test_db.add_all([paper1, paper2])
    test_db.commit()

    test_db.add_all([
        TFPaperAssociation(tf_id=tf_a.id, paper_id=paper1.id, evidence_notes="Initial discovery"),
        TFPaperAssociation(tf_id=tf_a.id, paper_id=paper2.id, evidence_notes="Transgenic validation")
    ])
    test_db.commit()
    test_db.refresh(tf_a)
    assert len(tf_a.papers) == 2

    # Scenario F: Paper associated with multiple TFs
    paper_shared = ResearchPaper(title="Comparative Study of TFs", journal="Nature Plants", year=2022, doi="10.1000/3")
    test_db.add(paper_shared)
    test_db.commit()
    test_db.add_all([
        TFPaperAssociation(tf_id=tf_a.id, paper_id=paper_shared.id),
        TFPaperAssociation(tf_id=tf_b.id, paper_id=paper_shared.id)
    ])
    test_db.commit()
    test_db.refresh(paper_shared)
    assert len(paper_shared.transcription_factors) == 2

    # Scenario G: TF associated with multiple target genes
    tgt1 = TargetGene(gene_symbol="Syn_SOS1", description="Na+ antiporter", plant_id=plant.id)
    tgt2 = TargetGene(gene_symbol="Syn_APX3", description="Ascorbate peroxidase", plant_id=plant.id)
    test_db.add_all([tgt1, tgt2])
    test_db.commit()
    test_db.add_all([
        TFTargetAssociation(tf_id=tf_a.id, target_gene_id=tgt1.id, regulation_mode="Direct activation"),
        TFTargetAssociation(tf_id=tf_a.id, target_gene_id=tgt2.id, regulation_mode="Transcriptional induction")
    ])
    test_db.commit()
    test_db.refresh(tf_a)
    assert len(tf_a.targets) == 2

    # Scenario H: TF associated with multiple pathways
    path1 = Pathway(pathway_name="Syn_Ascorbate recycling", pathway_type="Metabolic")
    path2 = Pathway(pathway_name="Syn_SOS signalling", pathway_type="Signalling")
    test_db.add_all([path1, path2])
    test_db.commit()
    test_db.add_all([
        TFPathwayAssociation(tf_id=tf_a.id, pathway_id=path1.id),
        TFPathwayAssociation(tf_id=tf_a.id, pathway_id=path2.id)
    ])
    test_db.commit()
    test_db.refresh(tf_a)
    assert len(tf_a.pathways) == 2

    # Scenario I: TF with a FASTA sequence
    seq = ProteinSequence(
        tf_id=tf_a.id,
        accession="P12345",
        fasta_header=">sp|P12345|SynTF_A Synthetic sequence",
        sequence="MSGSETGLMAATRESMQFTMALHQQQQHSQAQPQQSQN",
        sequence_length=38,
        molecular_weight=4200.5,
        source_filename="SynTF_A.txt"
    )
    test_db.add(seq)
    test_db.commit()
    test_db.refresh(tf_a)
    assert len(tf_a.sequences) == 1
    assert tf_a.sequences[0].sequence_length == 38

    # Scenario J: TF with an AlphaFold structure
    struct = ProteinStructure(
        tf_id=tf_a.id,
        model_identifier="SynTF_A_model1",
        structure_type="AlphaFold2",
        rank_num=1,
        pdb_file_path="structures/SynTF_A_rank1.pdb",
        pae_image_path="structures/SynTF_A_pae.png",
        plddt_image_path="structures/SynTF_A_plddt.png",
        mean_plddt=88.45
    )
    test_db.add(struct)
    test_db.commit()
    test_db.refresh(tf_a)
    assert len(tf_a.structures) == 1
    assert tf_a.structures[0].mean_plddt == 88.45

    # Scenario K: TF with STRING interactions
    inter = ProteinInteraction(
        tf_id=tf_a.id,
        partner_name="Syn_PartnerProtein",
        partner_uniprot="Q99999",
        combined_score=0.875,
        experimental_score=0.450,
        source_database="STRING"
    )
    test_db.add(inter)
    test_db.commit()
    test_db.refresh(tf_a)
    assert len(tf_a.interactions) == 1
    assert tf_a.interactions[0].combined_score == 0.875

    # Scenario L: TF with a Cytoscape network asset
    inter.cytoscape_image_path = "interactions/cytoscape/SynTF_A.png"
    test_db.commit()
    test_db.refresh(tf_a)
    assert tf_a.interactions[0].cytoscape_image_path == "interactions/cytoscape/SynTF_A.png"

    # Scenario M: Composite TF source value preserved
    tf_m = TranscriptionFactor(
        tf_name="SlCDF1 / SlCDF3",
        family_id=fam.id,
        plant_id=plant.id,
        raw_supplied_tf="SlCDF1 / SlCDF3",
        mechanism_description="Overexpression of SlCDF1/SlCDF3 improves salt and drought tolerance."
    )
    test_db.add(tf_m)
    test_db.commit()
    assert tf_m.tf_name == "SlCDF1 / SlCDF3"
    assert tf_m.raw_supplied_tf == "SlCDF1 / SlCDF3"

    # Scenario N: Composite stress source value preserved
    tf_n = TranscriptionFactor(
        tf_name="SynTF_MultiStress",
        family_id=fam.id,
        plant_id=plant.id,
        raw_stress="Drought, cold, osmotic stress"
    )
    test_db.add(tf_n)
    test_db.commit()
    # Associate to 3 individual normalized stress entities
    test_db.add_all([
        TFStressAssociation(tf_id=tf_n.id, stress_id=s_drought.id),
        TFStressAssociation(tf_id=tf_n.id, stress_id=s_cold.id),
        TFStressAssociation(tf_id=tf_n.id, stress_id=s_osm.id)
    ])
    test_db.commit()
    test_db.refresh(tf_n)
    assert tf_n.raw_stress == "Drought, cold, osmotic stress"
    assert len(tf_n.stresses) == 3


def test_cascade_delete(test_db):
    """Verify that deleting a TF record cascades cleanly to all subordinate records without leaving orphans."""
    fam = TFFamily(name="CascadeFam")
    plant = Plant(display_name="CascadePlant", common_name="CascadePlant")
    test_db.add_all([fam, plant])
    test_db.commit()

    tf = TranscriptionFactor(tf_name="TF_Cascade", family_id=fam.id, plant_id=plant.id)
    test_db.add(tf)
    test_db.commit()

    # Add subordinate entities
    ident = TFIdentifier(tf_id=tf.id, identifier_type="UniProtKB", identifier_value="C12345")
    seq = ProteinSequence(tf_id=tf.id, sequence="MVK", sequence_length=3)
    struct = ProteinStructure(tf_id=tf.id, model_identifier="m1", pdb_file_path="p.pdb")
    inter = ProteinInteraction(tf_id=tf.id, partner_name="P1", combined_score=0.5)
    
    stress = StressCondition(stress_name="CascadeStress")
    test_db.add(stress)
    test_db.commit()
    assoc = TFStressAssociation(tf_id=tf.id, stress_id=stress.id)

    test_db.add_all([ident, seq, struct, inter, assoc])
    test_db.commit()

    tf_id = tf.id
    # Delete the TF
    test_db.delete(tf)
    test_db.commit()

    # Verify subordinate records are deleted
    assert test_db.query(TFIdentifier).filter_by(tf_id=tf_id).count() == 0
    assert test_db.query(ProteinSequence).filter_by(tf_id=tf_id).count() == 0
    assert test_db.query(ProteinStructure).filter_by(tf_id=tf_id).count() == 0
    assert test_db.query(ProteinInteraction).filter_by(tf_id=tf_id).count() == 0
    assert test_db.query(TFStressAssociation).filter_by(tf_id=tf_id).count() == 0
    # Independent parent tables remain untouched
    assert test_db.query(TFFamily).filter_by(id=fam.id).count() == 1
    assert test_db.query(Plant).filter_by(id=plant.id).count() == 1
    assert test_db.query(StressCondition).filter_by(id=stress.id).count() == 1
