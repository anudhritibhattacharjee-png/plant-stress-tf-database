from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import math

from backend.app.database import get_db
from backend.app.models.target import TargetGene
from backend.schemas.targets import TargetGeneOut, TargetGeneDetailOut
from backend.schemas.pagination import PaginatedResponse
from backend.api.dependencies import get_pagination

router = APIRouter(prefix="/targets", tags=["Target Genes"])

@router.get("", response_model=PaginatedResponse[TargetGeneOut], summary="List Target Genes")
def list_targets(
    search: Optional[str] = Query(None, description="Search by gene symbol or description"),
    plant_id: Optional[int] = Query(None, description="Filter by plant ID"),
    pagination: tuple = Depends(get_pagination),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated downstream target genes.
    """
    page, page_size = pagination
    query = db.query(TargetGene)

    if plant_id:
        query = query.filter(TargetGene.plant_id == plant_id)

    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            (TargetGene.gene_symbol.ilike(pattern)) |
            (TargetGene.description.ilike(pattern))
        )

    total = query.count()
    items = query.order_by(TargetGene.gene_symbol).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{target_id}", response_model=TargetGeneDetailOut, summary="Get Target Gene Details with Associated TFs")
def get_target(target_id: int, db: Session = Depends(get_db)):
    """
    Retrieves target gene details and regulating transcription factors.
    """
    target = db.query(TargetGene).filter(TargetGene.id == target_id).first()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target gene with id {target_id} not found"
        )
    return target
