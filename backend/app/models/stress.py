from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class StressCondition(Base):
    """Normalized environmental or biological stress condition."""
    __tablename__ = "stress_conditions"

    id = Column(Integer, primary_key=True, index=True)
    stress_name = Column(String(100), unique=True, nullable=False, index=True)
    stress_type = Column(String(50), nullable=True, index=True)  # Abiotic, Biotic, Nutrient
    category = Column(String(50), nullable=True)  # Osmotic, Temperature, Pathogen
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    tf_associations = relationship("TFStressAssociation", back_populates="stress", cascade="all, delete-orphan")
    transcription_factors = relationship(
        "TranscriptionFactor",
        secondary="tf_stress_associations",
        back_populates="stresses",
        viewonly=True
    )

    def __repr__(self) -> str:
        return f"<StressCondition(id={self.id}, name='{self.stress_name}')>"


class TFStressAssociation(Base):
    """Many-to-many junction between transcription factors and stress conditions."""
    __tablename__ = "tf_stress_associations"
    __table_args__ = (
        UniqueConstraint("tf_id", "stress_id", name="uq_tf_stress"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tf_id = Column(Integer, ForeignKey("transcription_factors.id", ondelete="CASCADE"), nullable=False, index=True)
    stress_id = Column(Integer, ForeignKey("stress_conditions.id", ondelete="CASCADE"), nullable=False, index=True)
    specific_effect = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    tf = relationship("TranscriptionFactor", back_populates="stress_associations")
    stress = relationship("StressCondition", back_populates="tf_associations")

    def __repr__(self) -> str:
        return f"<TFStressAssociation(tf_id={self.tf_id}, stress_id={self.stress_id})>"
