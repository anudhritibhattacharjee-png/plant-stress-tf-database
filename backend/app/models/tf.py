from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class TranscriptionFactor(Base):
    """Core transcription factor entity representing a curated stress regulatory record."""
    __tablename__ = "transcription_factors"

    id = Column(Integer, primary_key=True, index=True)  # Stable internal integer primary key
    tf_name = Column(String(150), nullable=False, index=True)  # Name / symbol as reported in literature
    family_id = Column(Integer, ForeignKey("tf_families.id", ondelete="CASCADE"), nullable=False, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True)
    regulatory_effect = Column(String(100), nullable=True, index=True)  # Positive, Negative, Mixed / context-dependent
    mechanism_description = Column(Text, nullable=True)  # Narrative mechanism of stress regulation
    validation_system = Column(String(255), nullable=True)  # Native transgenic, heterologous expression, etc.
    evidence_summary = Column(Text, nullable=True)  # Experimental assays (RNAi, ChIP-seq, EMSA, etc.)
    
    # Verbatim source fields (guaranteeing exact provenance and zero loss of prototype data)
    raw_supplied_tf = Column(String(150), nullable=True)  # Verbatim cell from 'TF / TF family' column
    raw_stress = Column(String(255), nullable=True)  # Verbatim cell from 'Stress condition' column
    raw_targets = Column(Text, nullable=True)  # Verbatim cell from 'Key Target(s) / Pathway' column
    
    # Metadata & Provenance
    source_dataset = Column(String(100), default="curated_excel", nullable=False)
    source_row_index = Column(Integer, nullable=True)
    is_verified = Column(Boolean, default=True, nullable=False)  # False if accession marked 'Not verified'
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Core Relationships
    family = relationship("TFFamily", back_populates="transcription_factors")
    plant = relationship("Plant", back_populates="transcription_factors")
    identifiers = relationship("TFIdentifier", back_populates="tf", cascade="all, delete-orphan")
    
    # Stress Associations
    stress_associations = relationship("TFStressAssociation", back_populates="tf", cascade="all, delete-orphan")
    stresses = relationship(
        "StressCondition",
        secondary="tf_stress_associations",
        back_populates="transcription_factors",
        viewonly=True
    )

    # Literature Associations
    paper_associations = relationship("TFPaperAssociation", back_populates="tf", cascade="all, delete-orphan")
    papers = relationship(
        "ResearchPaper",
        secondary="tf_paper_associations",
        back_populates="transcription_factors",
        viewonly=True
    )

    # Target Gene & Pathway Associations
    target_associations = relationship("TFTargetAssociation", back_populates="tf", cascade="all, delete-orphan")
    targets = relationship(
        "TargetGene",
        secondary="tf_target_associations",
        back_populates="transcription_factors",
        viewonly=True
    )
    pathway_associations = relationship("TFPathwayAssociation", back_populates="tf", cascade="all, delete-orphan")
    pathways = relationship(
        "Pathway",
        secondary="tf_pathway_associations",
        back_populates="transcription_factors",
        viewonly=True
    )

    # Physical Assets & Functional Interactions
    sequences = relationship("ProteinSequence", back_populates="tf", cascade="all, delete-orphan")
    structures = relationship("ProteinStructure", back_populates="tf", cascade="all, delete-orphan")
    interactions = relationship("ProteinInteraction", back_populates="tf", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<TranscriptionFactor(id={self.id}, tf_name='{self.tf_name}', effect='{self.regulatory_effect}')>"
