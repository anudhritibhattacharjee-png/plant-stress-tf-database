from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ProteinStructureBase(BaseModel):
    tf_id: int
    model_identifier: str
    structure_type: str = "AlphaFold2"
    rank_num: int = 1
    pdb_file_path: str
    pae_image_path: Optional[str] = None
    plddt_image_path: Optional[str] = None
    coverage_image_path: Optional[str] = None
    mean_plddt: Optional[float] = None
    template_homolog: Optional[str] = None
    validation_status: str = "Computed"
    notes: Optional[str] = None

class ProteinStructureOut(ProteinStructureBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
