from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ProteinInteractionBase(BaseModel):
    tf_id: int
    partner_name: str
    partner_uniprot: Optional[str] = None
    combined_score: float
    experimental_score: Optional[float] = None
    database_score: Optional[float] = None
    textmining_score: Optional[float] = None
    coexpression_score: Optional[float] = None
    source_database: str = "STRING"
    source_file: Optional[str] = None
    cytoscape_image_path: Optional[str] = None
    string_image_path: Optional[str] = None
    validation_status: str = "Verified"
    notes: Optional[str] = None

class ProteinInteractionOut(ProteinInteractionBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
