from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class ProteinSequence(Base):
    """Protein amino acid sequence and FASTA file metadata for transcription factors."""
    __tablename__ = "protein_sequences"

    id = Column(Integer, primary_key=True, index=True)
    tf_id = Column(Integer, ForeignKey("transcription_factors.id", ondelete="CASCADE"), nullable=False, index=True)
    accession = Column(String(100), nullable=True, index=True)
    fasta_header = Column(String(500), nullable=True)
    sequence = Column(Text, nullable=False)
    sequence_length = Column(Integer, nullable=False)
    molecular_weight = Column(Float, nullable=True)
    source_filename = Column(String(255), nullable=True)
    validation_status = Column(String(50), default="Verified", nullable=False)
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    tf = relationship("TranscriptionFactor", back_populates="sequences")

    def __repr__(self) -> str:
        return f"<ProteinSequence(tf_id={self.tf_id}, len={self.sequence_length}, file='{self.source_filename}')>"
