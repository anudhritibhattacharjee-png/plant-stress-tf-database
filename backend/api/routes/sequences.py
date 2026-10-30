from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import math

from backend.app.database import get_db
from backend.app.models.sequence import ProteinSequence
from backend.app.models.tf import TranscriptionFactor
from backend.schemas.sequences import ProteinSequenceOut
from backend.schemas.pagination import PaginatedResponse
from backend.api.dependencies import get_pagination

router = APIRouter(prefix="/sequences", tags=["Protein Sequences"])

@router.get("", response_model=PaginatedResponse[ProteinSequenceOut], summary="List Protein Sequences")
def list_sequences(
    tf_id: Optional[int] = Query(None, description="Filter sequences by Transcription Factor ID"),
    accession: Optional[str] = Query(None, description="Filter by protein accession"),
    pagination: tuple = Depends(get_pagination),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated protein sequences with optional TF ID or accession filtering.
    """
    page, page_size = pagination
    query = db.query(ProteinSequence)

    if tf_id:
        query = query.filter(ProteinSequence.tf_id == tf_id)

    if accession:
        query = query.filter(ProteinSequence.accession.ilike(f"%{accession.strip()}%"))

    total = query.count()
    items = query.order_by(ProteinSequence.id).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{sequence_id}", response_model=ProteinSequenceOut, summary="Get Single Protein Sequence by ID")
def get_sequence(sequence_id: int, db: Session = Depends(get_db)):
    """
    Retrieves full details and FASTA sequence content for a specific sequence record.
    """
    seq = db.query(ProteinSequence).filter(ProteinSequence.id == sequence_id).first()
    if not seq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Protein sequence with id {sequence_id} not found"
        )
    return seq
