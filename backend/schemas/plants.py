from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PlantBase(BaseModel):
    display_name: str
    common_name: str
    scientific_name: Optional[str] = None
    ncbi_taxonomy_id: Optional[int] = None

class PlantOut(PlantBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TFSummaryForRelated(BaseModel):
    id: int
    tf_name: str
    regulatory_effect: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PlantDetailOut(PlantOut):
    transcription_factors: List[TFSummaryForRelated] = []

    model_config = ConfigDict(from_attributes=True)
