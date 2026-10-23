from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class ProteinStructure(Base):
    """AlphaFold2 predicted 3D protein coordinate models and diagnostic evaluation assets."""
    __tablename__ = "protein_structures"

    id = Column(Integer, primary_key=True, index=True)
    tf_id = Column(Integer, ForeignKey("transcription_factors.id", ondelete="CASCADE"), nullable=False, index=True)
    model_identifier = Column(String(100), nullable=False, index=True)  # AlphaFold job/folder ID: e.g. "AHL10_f311a"
    structure_type = Column(String(50), default="AlphaFold2", nullable=False)
    rank_num = Column(Integer, default=1, nullable=False)  # Model rank (1 to 5)
    pdb_file_path = Column(String(500), nullable=False)  # Relative path to .pdb coordinate file
    pae_image_path = Column(String(500), nullable=True)  # Relative path to Predicted Aligned Error plot
    plddt_image_path = Column(String(500), nullable=True)  # Relative path to pLDDT plot
    coverage_image_path = Column(String(500), nullable=True)  # Relative path to sequence coverage plot
    mean_plddt = Column(Float, nullable=True)  # Mean per-residue confidence metric (0-100)
    template_homolog = Column(String(100), nullable=True)  # Explicit flag if model based on homolog (e.g. AtDOF5.8 for BnCDF1)
    validation_status = Column(String(50), default="Computed", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tf = relationship("TranscriptionFactor", back_populates="structures")

    def __repr__(self) -> str:
        return f"<ProteinStructure(tf_id={self.tf_id}, model='{self.model_identifier}', rank={self.rank_num})>"
