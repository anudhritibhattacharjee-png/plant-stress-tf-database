from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class TargetGene(Base):
    """Downstream target gene regulated by transcription factors."""
    __tablename__ = "target_genes"

    id = Column(Integer, primary_key=True, index=True)
    gene_symbol = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    plant = relationship("Plant", back_populates="target_genes")
    tf_associations = relationship("TFTargetAssociation", back_populates="target_gene", cascade="all, delete-orphan")
    transcription_factors = relationship(
        "TranscriptionFactor",
        secondary="tf_target_associations",
        back_populates="targets",
        viewonly=True
    )

    def __repr__(self) -> str:
        return f"<TargetGene(id={self.id}, symbol='{self.gene_symbol}')>"


class TFTargetAssociation(Base):
    """Many-to-many junction between transcription factors and target genes."""
    __tablename__ = "tf_target_associations"
    __table_args__ = (
        UniqueConstraint("tf_id", "target_gene_id", name="uq_tf_target"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tf_id = Column(Integer, ForeignKey("transcription_factors.id", ondelete="CASCADE"), nullable=False, index=True)
    target_gene_id = Column(Integer, ForeignKey("target_genes.id", ondelete="CASCADE"), nullable=False, index=True)
    regulation_mode = Column(String(100), nullable=True)
    evidence = Column(String(255), nullable=True)

    # Relationships
    tf = relationship("TranscriptionFactor", back_populates="target_associations")
    target_gene = relationship("TargetGene", back_populates="tf_associations")

    def __repr__(self) -> str:
        return f"<TFTargetAssociation(tf_id={self.tf_id}, target_id={self.target_gene_id})>"


class Pathway(Base):
    """Biological or signalling pathway modulated by transcription factors."""
    __tablename__ = "pathways"

    id = Column(Integer, primary_key=True, index=True)
    pathway_name = Column(String(255), unique=True, nullable=False, index=True)
    pathway_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    tf_associations = relationship("TFPathwayAssociation", back_populates="pathway", cascade="all, delete-orphan")
    transcription_factors = relationship(
        "TranscriptionFactor",
        secondary="tf_pathway_associations",
        back_populates="pathways",
        viewonly=True
    )

    def __repr__(self) -> str:
        return f"<Pathway(id={self.id}, name='{self.pathway_name}')>"


class TFPathwayAssociation(Base):
    """Many-to-many junction between transcription factors and pathways."""
    __tablename__ = "tf_pathway_associations"
    __table_args__ = (
        UniqueConstraint("tf_id", "pathway_id", name="uq_tf_pathway"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tf_id = Column(Integer, ForeignKey("transcription_factors.id", ondelete="CASCADE"), nullable=False, index=True)
    pathway_id = Column(Integer, ForeignKey("pathways.id", ondelete="CASCADE"), nullable=False, index=True)
    notes = Column(Text, nullable=True)

    # Relationships
    tf = relationship("TranscriptionFactor", back_populates="pathway_associations")
    pathway = relationship("Pathway", back_populates="tf_associations")

    def __repr__(self) -> str:
        return f"<TFPathwayAssociation(tf_id={self.tf_id}, pathway_id={self.pathway_id})>"
