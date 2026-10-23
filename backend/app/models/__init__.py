"""SQLAlchemy models package for PhytoStress TF Atlas.

Re-exports all database models to ensure registration with Base.metadata.
"""

from backend.app.database import Base
from backend.app.models.family import TFFamily
from backend.app.models.plant import Plant
from backend.app.models.tf import TranscriptionFactor
from backend.app.models.stress import StressCondition, TFStressAssociation
from backend.app.models.identifier import TFIdentifier
from backend.app.models.paper import ResearchPaper, TFPaperAssociation
from backend.app.models.target import TargetGene, TFTargetAssociation, Pathway, TFPathwayAssociation
from backend.app.models.sequence import ProteinSequence
from backend.app.models.structure import ProteinStructure
from backend.app.models.interaction import ProteinInteraction
from backend.app.models.audit import ImportAudit

__all__ = [
    "Base",
    "TFFamily",
    "Plant",
    "TranscriptionFactor",
    "StressCondition",
    "TFStressAssociation",
    "TFIdentifier",
    "ResearchPaper",
    "TFPaperAssociation",
    "TargetGene",
    "TFTargetAssociation",
    "Pathway",
    "TFPathwayAssociation",
    "ProteinSequence",
    "ProteinStructure",
    "ProteinInteraction",
    "ImportAudit"
]
