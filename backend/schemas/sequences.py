from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ProteinSequenceBase(BaseModel):
    tf_id: int
    accession: Optional[str] = None
    fasta_header: Optional[str] = None
    sequence: str
    sequence_length: int
    molecular_weight: Optional[float] = None
    source_filename: Optional[str] = None
    validation_status: str = "Verified"
    provenance: Optional[str] = None

class ProteinSequenceOut(ProteinSequenceBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
