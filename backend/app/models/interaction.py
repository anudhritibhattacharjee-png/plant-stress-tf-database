from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class ProteinInteraction(Base):
    """Protein-protein interactions (PPI) from STRING database with linked Cytoscape figures."""
    __tablename__ = "protein_interactions"

    id = Column(Integer, primary_key=True, index=True)
    tf_id = Column(Integer, ForeignKey("transcription_factors.id", ondelete="CASCADE"), nullable=False, index=True)
    partner_name = Column(String(100), nullable=False, index=True)  # Interacting partner gene/symbol (e.g. ADM, SUVH9)
    partner_uniprot = Column(String(50), nullable=True, index=True)  # Partner UniProtKB identifier
    combined_score = Column(Float, nullable=False, index=True)  # STRING confidence score (0.000 to 1.000)
    experimental_score = Column(Float, nullable=True)  # Biochemical experimental evidence score
    database_score = Column(Float, nullable=True)  # Curated pathway database score
    textmining_score = Column(Float, nullable=True)  # Literature textmining score
    coexpression_score = Column(Float, nullable=True)  # RNA coexpression score
    source_database = Column(String(50), default="STRING", nullable=False)
    source_file = Column(String(255), nullable=True)  # TSV source filename
    cytoscape_image_path = Column(String(500), nullable=True)  # Associated high-res Cytoscape network image path
    string_image_path = Column(String(500), nullable=True)  # STRING network diagram path
    validation_status = Column(String(50), default="Verified", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tf = relationship("TranscriptionFactor", back_populates="interactions")

    def __repr__(self) -> str:
        return f"<ProteinInteraction(tf_id={self.tf_id}, partner='{self.partner_name}', score={self.combined_score})>"
