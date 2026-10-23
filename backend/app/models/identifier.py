from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class TFIdentifier(Base):
    """External biological database accessions and locus identifiers for TFs."""
    __tablename__ = "tf_identifiers"

    id = Column(Integer, primary_key=True, index=True)
    tf_id = Column(Integer, ForeignKey("transcription_factors.id", ondelete="CASCADE"), nullable=False, index=True)
    identifier_type = Column(String(100), nullable=False, index=True)
    identifier_value = Column(String(100), nullable=False, index=True)
    verification_status = Column(String(50), default="Verified", nullable=False, index=True)
    raw_supplied_text = Column(Text, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    source_file = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    tf = relationship("TranscriptionFactor", back_populates="identifiers")

    def __repr__(self) -> str:
        return f"<TFIdentifier(tf_id={self.tf_id}, type='{self.identifier_type}', value='{self.identifier_value}', status='{self.verification_status}')>"
