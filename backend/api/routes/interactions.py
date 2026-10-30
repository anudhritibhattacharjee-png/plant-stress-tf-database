from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import math

from backend.app.database import get_db
from backend.app.models.interaction import ProteinInteraction
from backend.schemas.interactions import ProteinInteractionOut
from backend.schemas.pagination import PaginatedResponse
from backend.api.dependencies import get_pagination

router = APIRouter(prefix="/interactions", tags=["Protein Interactions (STRING / FunCoup)"])

@router.get("", response_model=PaginatedResponse[ProteinInteractionOut], summary="List Protein Interactions")
def list_interactions(
    tf_id: Optional[int] = Query(None, description="Filter interactions by focal Transcription Factor ID"),
    partner_name: Optional[str] = Query(None, description="Filter by interacting partner symbol"),
    source_database: Optional[str] = Query(None, description="Filter by source database (STRING or FunCoup)"),
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum combined confidence score"),
    pagination: tuple = Depends(get_pagination),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated protein-protein interaction (PPI) records with confidence and evidence subscores.
    """
    page, page_size = pagination
    query = db.query(ProteinInteraction)

    if tf_id:
        query = query.filter(ProteinInteraction.tf_id == tf_id)

    if partner_name:
        query = query.filter(ProteinInteraction.partner_name.ilike(f"%{partner_name.strip()}%"))

    if source_database:
        query = query.filter(ProteinInteraction.source_database.ilike(f"%{source_database.strip()}%"))

    if min_score is not None:
        query = query.filter(ProteinInteraction.combined_score >= min_score)

    total = query.count()
    items = query.order_by(ProteinInteraction.tf_id, ProteinInteraction.combined_score.desc()).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{interaction_id}", response_model=ProteinInteractionOut, summary="Get Single Interaction by ID")
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """
    Retrieves evidence subscores and network diagram asset paths for a specific PPI record.
    """
    inter = db.query(ProteinInteraction).filter(ProteinInteraction.id == interaction_id).first()
    if not inter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Protein interaction with id {interaction_id} not found"
        )
    return inter
