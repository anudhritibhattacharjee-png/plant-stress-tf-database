from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.app.database import Base

class ImportAudit(Base):
    """Audit log tracking dataset imports and batch updates for provenance and reproducibility."""
    __tablename__ = "import_audits"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(255), nullable=False, index=True)  # File path or batch title
    source_type = Column(String(50), nullable=False)  # EXCEL, CSV, JSON, ASSET_SYNC
    source_hash = Column(String(64), nullable=True)  # SHA-256 digest of imported file
    records_processed = Column(Integer, default=0, nullable=False)
    records_inserted = Column(Integer, default=0, nullable=False)
    records_updated = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="SUCCESS", nullable=False)  # SUCCESS, PARTIAL, FAILED
    validation_summary = Column(Text, nullable=True)  # JSON or formatted summary of import statistics
    error_information = Column(Text, nullable=True)  # Captured exception trace or warning messages
    imported_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ImportAudit(id={self.id}, source='{self.source_name}', status='{self.status}', inserted={self.records_inserted})>"
