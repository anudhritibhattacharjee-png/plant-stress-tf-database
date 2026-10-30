from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.schemas.plants import TFSummaryForRelated

class StressConditionBase(BaseModel):
    stress_name: str
    stress_type: Optional[str] = None
    category: Optional[str] = None

class StressConditionOut(StressConditionBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class StressConditionDetailOut(StressConditionOut):
    transcription_factors: List[TFSummaryForRelated] = []

    model_config = ConfigDict(from_attributes=True)
