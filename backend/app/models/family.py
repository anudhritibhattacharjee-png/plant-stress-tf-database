from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class TFFamily(Base):
    """Normalized Transcription Factor Family classification."""
    __tablename__ = "tf_families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    transcription_factors = relationship("TranscriptionFactor", back_populates="family")

    def __repr__(self) -> str:
        return f"<TFFamily(id={self.id}, name='{self.name}')>"
