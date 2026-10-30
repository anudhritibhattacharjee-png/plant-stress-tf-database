from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import math

from backend.app.database import get_db
from backend.app.models.structure import ProteinStructure
from backend.schemas.structures import ProteinStructureOut
from backend.schemas.pagination import PaginatedResponse
from backend.api.dependencies import get_pagination

router = APIRouter(prefix="/structures", tags=["Protein Structures (AlphaFold)"])

@router.get("", response_model=PaginatedResponse[ProteinStructureOut], summary="List AlphaFold 3D Structures")
def list_structures(
    tf_id: Optional[int] = Query(None, description="Filter structures by Transcription Factor ID"),
    rank_num: Optional[int] = Query(None, description="Filter by model rank (1 to 5)"),
    model_identifier: Optional[str] = Query(None, description="Filter by model identifier"),
    pagination: tuple = Depends(get_pagination),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated AlphaFold 3D structural models with pLDDT confidence metrics.
    """
    page, page_size = pagination
    query = db.query(ProteinStructure)

    if tf_id:
        query = query.filter(ProteinStructure.tf_id == tf_id)

    if rank_num is not None:
        query = query.filter(ProteinStructure.rank_num == rank_num)

    if model_identifier:
        query = query.filter(ProteinStructure.model_identifier.ilike(f"%{model_identifier.strip()}%"))

    total = query.count()
    items = query.order_by(ProteinStructure.tf_id, ProteinStructure.rank_num).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{structure_id}", response_model=ProteinStructureOut, summary="Get Single AlphaFold Structure by ID")
def get_structure(structure_id: int, db: Session = Depends(get_db)):
    """
    Retrieves coordinate file paths and diagnostic evaluation metrics for a specific AlphaFold structure model.
    """
    struct = db.query(ProteinStructure).filter(ProteinStructure.id == structure_id).first()
    if not struct:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Protein structure with id {structure_id} not found"
        )
    return struct
