from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import math

from backend.app.database import get_db
from backend.app.models.target import Pathway
from backend.schemas.pathways import PathwayOut, PathwayDetailOut
from backend.schemas.pagination import PaginatedResponse
from backend.api.dependencies import get_pagination

router = APIRouter(prefix="/pathways", tags=["Pathways"])

@router.get("", response_model=PaginatedResponse[PathwayOut], summary="List Pathways")
def list_pathways(
    pathway_type: Optional[str] = Query(None, description="Filter by pathway type"),
    search: Optional[str] = Query(None, description="Search by pathway name"),
    pagination: tuple = Depends(get_pagination),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated biological/signaling pathways.
    """
    page, page_size = pagination
    query = db.query(Pathway)

    if pathway_type:
        query = query.filter(Pathway.pathway_type.ilike(f"%{pathway_type.strip()}%"))

    if search:
        query = query.filter(Pathway.pathway_name.ilike(f"%{search.strip()}%"))

    total = query.count()
    items = query.order_by(Pathway.pathway_name).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{pathway_id}", response_model=PathwayDetailOut, summary="Get Pathway Details with Associated TFs")
def get_pathway(pathway_id: int, db: Session = Depends(get_db)):
    """
    Retrieves pathway details and associated transcription factors.
    """
    pathway = db.query(Pathway).filter(Pathway.id == pathway_id).first()
    if not pathway:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pathway with id {pathway_id} not found"
        )
    return pathway
