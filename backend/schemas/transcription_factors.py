from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.schemas.plants import PlantOut
from backend.schemas.families import TFFamilyOut
from backend.schemas.stress_conditions import StressConditionOut
from backend.schemas.papers import ResearchPaperOut
from backend.schemas.targets import TargetGeneOut
from backend.schemas.pathways import PathwayOut
from backend.schemas.sequences import ProteinSequenceOut
from backend.schemas.structures import ProteinStructureOut
from backend.schemas.interactions import ProteinInteractionOut

class TFIdentifierOut(BaseModel):
    id: int
    identifier_type: str
    identifier_value: str
    verification_status: str
    is_primary: bool
    raw_supplied_text: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TFBase(BaseModel):
    tf_name: str
    regulatory_effect: Optional[str] = None
    mechanism_description: Optional[str] = None
    validation_system: Optional[str] = None
    evidence_summary: Optional[str] = None
    raw_supplied_tf: Optional[str] = None
    raw_stress: Optional[str] = None
    raw_targets: Optional[str] = None
    source_dataset: str = "curated_excel"
    is_verified: bool = True
    notes: Optional[str] = None

class TFSummaryOut(BaseModel):
    id: int
    tf_name: str
    regulatory_effect: Optional[str] = None
    family_id: int
    family_name: Optional[str] = None
    plant_id: int
    plant_name: Optional[str] = None
    is_verified: bool = True
    identifiers_count: int = 0
    stresses: List[str] = []
    has_sequence: bool = False
    has_structure: bool = False
    interactions_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class TFDetailOut(TFBase):
    id: int
    family_id: int
    plant_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    plant: Optional[PlantOut] = None
    family: Optional[TFFamilyOut] = None
    identifiers: List[TFIdentifierOut] = []
    stresses: List[StressConditionOut] = []
    papers: List[ResearchPaperOut] = []
    targets: List[TargetGeneOut] = []
    pathways: List[PathwayOut] = []
    sequences_count: int = 0
    structures_count: int = 0
    interactions_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class TFFullOut(TFBase):
    id: int
    family_id: int
    plant_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    plant: Optional[PlantOut] = None
    family: Optional[TFFamilyOut] = None
    identifiers: List[TFIdentifierOut] = []
    stresses: List[StressConditionOut] = []
    papers: List[ResearchPaperOut] = []
    targets: List[TargetGeneOut] = []
    pathways: List[PathwayOut] = []
    sequences: List[ProteinSequenceOut] = []
    structures: List[ProteinStructureOut] = []
    interactions: List[ProteinInteractionOut] = []

    model_config = ConfigDict(from_attributes=True)
