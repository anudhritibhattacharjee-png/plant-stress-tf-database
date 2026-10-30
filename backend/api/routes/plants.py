from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import math

from backend.app.database import get_db
from backend.app.models.plant import Plant
from backend.app.models.tf import TranscriptionFactor
from backend.schemas.plants import PlantOut, PlantDetailOut, TFSummaryForRelated
from backend.schemas.pagination import PaginatedResponse
from backend.api.dependencies import get_pagination

router = APIRouter(prefix="/plants", tags=["Plants"])

@router.get("", response_model=PaginatedResponse[PlantOut], summary="List Plant Species")
def list_plants(
    search: Optional[str] = Query(None, description="Search across common or scientific name"),
    pagination: tuple = Depends(get_pagination),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated host plant species with optional substring search.
    """
    page, page_size = pagination
    query = db.query(Plant)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Plant.common_name.ilike(search_pattern)) |
            (Plant.scientific_name.ilike(search_pattern)) |
            (Plant.display_name.ilike(search_pattern))
        )

    total = query.count()
    items = query.order_by(Plant.id).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{plant_id}", response_model=PlantDetailOut, summary="Get Plant Details with Associated TFs")
def get_plant(plant_id: int, db: Session = Depends(get_db)):
    """
    Retrieves plant details and all associated transcription factors.
    """
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant species with id {plant_id} not found"
        )
    return plant
