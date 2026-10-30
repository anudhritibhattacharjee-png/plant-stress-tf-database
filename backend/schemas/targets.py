from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.schemas.plants import TFSummaryForRelated

class TargetGeneBase(BaseModel):
    gene_symbol: str
    description: Optional[str] = None
    plant_id: Optional[int] = None

class TargetGeneOut(TargetGeneBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TargetGeneDetailOut(TargetGeneOut):
    transcription_factors: List[TFSummaryForRelated] = []

    model_config = ConfigDict(from_attributes=True)
