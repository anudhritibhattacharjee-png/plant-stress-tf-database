from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.schemas.plants import TFSummaryForRelated

class PathwayBase(BaseModel):
    pathway_name: str
    pathway_type: Optional[str] = None

class PathwayOut(PathwayBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PathwayDetailOut(PathwayOut):
    transcription_factors: List[TFSummaryForRelated] = []

    model_config = ConfigDict(from_attributes=True)
