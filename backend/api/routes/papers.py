from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import math

from backend.app.database import get_db
from backend.app.models.paper import ResearchPaper
from backend.schemas.papers import ResearchPaperOut, ResearchPaperDetailOut
from backend.schemas.pagination import PaginatedResponse
from backend.api.dependencies import get_pagination

router = APIRouter(prefix="/papers", tags=["Research Papers"])

@router.get("", response_model=PaginatedResponse[ResearchPaperOut], summary="List Research Papers")
def list_papers(
    journal: Optional[str] = Query(None, description="Filter by journal name"),
    year: Optional[int] = Query(None, description="Filter by publication year"),
    search: Optional[str] = Query(None, description="Search title, DOI, or authors"),
    pagination: tuple = Depends(get_pagination),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated research papers with journal, year, and keyword search filters.
    """
    page, page_size = pagination
    query = db.query(ResearchPaper)

    if journal:
        query = query.filter(ResearchPaper.journal.ilike(f"%{journal.strip()}%"))

    if year:
        query = query.filter(ResearchPaper.year == year)

    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            (ResearchPaper.title.ilike(pattern)) |
            (ResearchPaper.doi.ilike(pattern)) |
            (ResearchPaper.authors.ilike(pattern))
        )

    total = query.count()
    items = query.order_by(ResearchPaper.id).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{paper_id}", response_model=ResearchPaperDetailOut, summary="Get Paper Details with Associated TFs")
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    """
    Retrieves research paper details and associated transcription factors.
    """
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research paper with id {paper_id} not found"
        )
    return paper
