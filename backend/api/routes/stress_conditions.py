from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import math

from backend.app.database import get_db
from backend.app.models.stress import StressCondition
from backend.schemas.stress_conditions import StressConditionOut, StressConditionDetailOut
from backend.schemas.pagination import PaginatedResponse
from backend.api.dependencies import get_pagination

router = APIRouter(prefix="/stress-conditions", tags=["Stress Conditions"])

@router.get("", response_model=PaginatedResponse[StressConditionOut], summary="List Stress Conditions")
def list_stress_conditions(
    stress_type: Optional[str] = Query(None, description="Filter by stress type (e.g. Abiotic, Biotic, Nutrient)"),
    search: Optional[str] = Query(None, description="Search across stress name or category"),
    pagination: tuple = Depends(get_pagination),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated stress conditions with type and name filters.
    """
    page, page_size = pagination
    query = db.query(StressCondition)

    if stress_type:
        query = query.filter(StressCondition.stress_type.ilike(f"%{stress_type.strip()}%"))

    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            (StressCondition.stress_name.ilike(pattern)) |
            (StressCondition.category.ilike(pattern))
        )

    total = query.count()
    items = query.order_by(StressCondition.stress_name).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{stress_id}", response_model=StressConditionDetailOut, summary="Get Stress Condition Details with Associated TFs")
def get_stress_condition(stress_id: int, db: Session = Depends(get_db)):
    """
    Retrieves stress condition details and all associated transcription factors.
    """
    stress = db.query(StressCondition).filter(StressCondition.id == stress_id).first()
    if not stress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stress condition with id {stress_id} not found"
        )
    return stress
