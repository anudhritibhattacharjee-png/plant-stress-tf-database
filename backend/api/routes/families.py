from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import math

from backend.app.database import get_db
from backend.app.models.family import TFFamily
from backend.schemas.families import TFFamilyOut, TFFamilyDetailOut
from backend.schemas.pagination import PaginatedResponse
from backend.api.dependencies import get_pagination

router = APIRouter(prefix="/families", tags=["TF Families"])

@router.get("", response_model=PaginatedResponse[TFFamilyOut], summary="List Transcription Factor Families")
def list_families(
    search: Optional[str] = Query(None, description="Search by family name or description"),
    pagination: tuple = Depends(get_pagination),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated TF families with optional search.
    """
    page, page_size = pagination
    query = db.query(TFFamily)

    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            (TFFamily.name.ilike(pattern)) |
            (TFFamily.description.ilike(pattern))
        )

    total = query.count()
    items = query.order_by(TFFamily.name).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{family_id}", response_model=TFFamilyDetailOut, summary="Get TF Family Details with Associated TFs")
def get_family(family_id: int, db: Session = Depends(get_db)):
    """
    Retrieves TF family details and all associated transcription factors.
    """
    fam = db.query(TFFamily).filter(TFFamily.id == family_id).first()
    if not fam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TF Family with id {family_id} not found"
        )
    return fam
