from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database import Base, utc_now

class ResearchPaper(Base):
    """Bibliographic publication documenting transcription factor stress regulation."""
    __tablename__ = "research_papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False, index=True)
    journal = Column(String(255), nullable=True, index=True)
    year = Column(Integer, nullable=True, index=True)
    doi = Column(String(255), nullable=True, index=True)
    doi_url = Column(String(500), nullable=True)
    pubmed_id = Column(String(50), nullable=True, index=True)
    authors = Column(Text, nullable=True)
    raw_citation_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    tf_associations = relationship("TFPaperAssociation", back_populates="paper", cascade="all, delete-orphan")
    transcription_factors = relationship(
        "TranscriptionFactor",
        secondary="tf_paper_associations",
        back_populates="papers",
        viewonly=True
    )

    def __repr__(self) -> str:
        return f"<ResearchPaper(id={self.id}, doi='{self.doi}', year={self.year})>"


class TFPaperAssociation(Base):
    """Many-to-many junction between transcription factors and research papers."""
    __tablename__ = "tf_paper_associations"
    __table_args__ = (
        UniqueConstraint("tf_id", "paper_id", name="uq_tf_paper"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tf_id = Column(Integer, ForeignKey("transcription_factors.id", ondelete="CASCADE"), nullable=False, index=True)
    paper_id = Column(Integer, ForeignKey("research_papers.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_notes = Column(Text, nullable=True)

    # Relationships
    tf = relationship("TranscriptionFactor", back_populates="paper_associations")
    paper = relationship("ResearchPaper", back_populates="tf_associations")

    def __repr__(self) -> str:
        return f"<TFPaperAssociation(tf_id={self.tf_id}, paper_id={self.paper_id})>"
