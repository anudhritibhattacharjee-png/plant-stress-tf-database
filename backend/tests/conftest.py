import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is in python search path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.database import Base
from backend.app.models import (
    TFFamily, Plant, TranscriptionFactor,
    StressCondition, TFStressAssociation, TFIdentifier,
    ResearchPaper, TFPaperAssociation, TargetGene,
    TFTargetAssociation, Pathway, TFPathwayAssociation,
    ProteinSequence, ProteinStructure, ProteinInteraction,
    ImportAudit
)

@pytest.fixture(scope="function")
def test_db():
    """Creates a fresh in-memory SQLite database for each test function."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
