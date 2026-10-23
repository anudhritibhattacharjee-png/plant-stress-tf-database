from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class Plant(Base):
    """Host plant species entity."""
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String(255), nullable=False, index=True)
    common_name = Column(String(100), nullable=False, index=True)
    scientific_name = Column(String(150), nullable=True, index=True)
    ncbi_taxonomy_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    transcription_factors = relationship("TranscriptionFactor", back_populates="plant")
    target_genes = relationship("TargetGene", back_populates="plant")

    def __repr__(self) -> str:
        return f"<Plant(id={self.id}, common_name='{self.common_name}', scientific='{self.scientific_name}')>"
