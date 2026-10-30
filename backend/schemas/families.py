from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.schemas.plants import TFSummaryForRelated

class TFFamilyBase(BaseModel):
    name: str
    description: Optional[str] = None

class TFFamilyOut(TFFamilyBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TFFamilyDetailOut(TFFamilyOut):
    transcription_factors: List[TFSummaryForRelated] = []

    model_config = ConfigDict(from_attributes=True)
