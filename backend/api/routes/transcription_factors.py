from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
import math

from backend.app.database import get_db
from backend.app.models.tf import TranscriptionFactor
from backend.app.models.plant import Plant
from backend.app.models.family import TFFamily
from backend.app.models.stress import StressCondition
from backend.app.models.sequence import ProteinSequence
from backend.app.models.structure import ProteinStructure
from backend.app.models.interaction import ProteinInteraction
from backend.schemas.transcription_factors import TFSummaryOut, TFDetailOut, TFFullOut
from backend.schemas.sequences import ProteinSequenceOut
from backend.schemas.structures import ProteinStructureOut
from backend.schemas.interactions import ProteinInteractionOut
from backend.schemas.pagination import PaginatedResponse
from backend.api.dependencies import get_pagination

router = APIRouter(prefix="/transcription-factors", tags=["Transcription Factors"])

@router.get("", response_model=PaginatedResponse[TFSummaryOut], summary="List & Filter Transcription Factors")
def list_transcription_factors(
    plant: Optional[str] = Query(None, description="Filter by plant common or scientific name (e.g. Arabidopsis, Rice, Tomato)"),
    family: Optional[str] = Query(None, description="Filter by TF family (e.g. DOF, NAC, WRKY, bZIP)"),
    stress: Optional[str] = Query(None, description="Filter by stress condition (e.g. drought, salinity, cold)"),
    search: Optional[str] = Query(None, description="Search across TF name or mechanism"),
    pagination: tuple = Depends(get_pagination),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated transcription factors with multidimensional biological filters.
    """
    page, page_size = pagination
    query = db.query(TranscriptionFactor).join(TranscriptionFactor.plant).join(TranscriptionFactor.family)

    if plant:
        plant_clean = plant.strip()
        query = query.filter(
            or_(
                Plant.common_name.ilike(f"%{plant_clean}%"),
                Plant.scientific_name.ilike(f"%{plant_clean}%"),
                Plant.display_name.ilike(f"%{plant_clean}%")
            )
        )

    if family:
        family_clean = family.strip()
        query = query.filter(TFFamily.name.ilike(f"%{family_clean}%"))

    if stress:
        stress_clean = stress.strip()
        query = query.join(TranscriptionFactor.stresses).filter(
            StressCondition.stress_name.ilike(f"%{stress_clean}%")
        )

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                TranscriptionFactor.tf_name.ilike(search_pattern),
                TranscriptionFactor.mechanism_description.ilike(search_pattern),
                TranscriptionFactor.raw_supplied_tf.ilike(search_pattern)
            )
        )

    # Ensure distinct results when joining many-to-many
    query = query.distinct()
    total = query.count()
    records = query.order_by(TranscriptionFactor.id).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    items = []
    for tf in records:
        summary = TFSummaryOut(
            id=tf.id,
            tf_name=tf.tf_name,
            regulatory_effect=tf.regulatory_effect,
            family_id=tf.family_id,
            family_name=tf.family.name if tf.family else None,
            plant_id=tf.plant_id,
            plant_name=tf.plant.common_name if tf.plant else None,
            is_verified=tf.is_verified,
            identifiers_count=len(tf.identifiers),
            stresses=[s.stress_name for s in tf.stresses],
            has_sequence=len(tf.sequences) > 0,
            has_structure=len(tf.structures) > 0,
            interactions_count=len(tf.interactions)
        )
        items.append(summary)

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{tf_id}", response_model=TFDetailOut, summary="Get Transcription Factor Overview by ID")
def get_transcription_factor(tf_id: int, db: Session = Depends(get_db)):
    """
    Retrieves standard details for a single transcription factor, including associated plant,
    family, identifiers, stresses, targets, pathways, and summary counts of physical assets.
    """
    tf = db.query(TranscriptionFactor).filter(TranscriptionFactor.id == tf_id).first()
    if not tf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcription factor with id {tf_id} not found"
        )
    detail = TFDetailOut.model_validate(tf)
    detail.sequences_count = len(tf.sequences)
    detail.structures_count = len(tf.structures)
    detail.interactions_count = len(tf.interactions)
    return detail

@router.get("/{tf_id}/full", response_model=TFFullOut, summary="Get Complete Transcription Factor Dossier")
def get_transcription_factor_full(tf_id: int, db: Session = Depends(get_db)):
    """
    Retrieves comprehensive, frontend-friendly biological dossier for a transcription factor,
    including linked plant, family, external identifiers, stress conditions, literature papers,
    downstream targets, pathways, FASTA protein sequences, AlphaFold 3D structures, and PPI networks.
    """
    tf = db.query(TranscriptionFactor).filter(TranscriptionFactor.id == tf_id).first()
    if not tf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcription factor with id {tf_id} not found"
        )
    return TFFullOut.model_validate(tf)

@router.get("/{tf_id}/sequence", response_model=List[ProteinSequenceOut], summary="Get Protein Sequences for TF")
def get_tf_sequence(tf_id: int, db: Session = Depends(get_db)):
    """
    Retrieves protein amino acid sequences and FASTA metadata for a specific transcription factor.
    """
    tf = db.query(TranscriptionFactor).filter(TranscriptionFactor.id == tf_id).first()
    if not tf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcription factor with id {tf_id} not found"
        )
    if not tf.sequences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No protein sequence available for transcription factor {tf_id}"
        )
    return [ProteinSequenceOut.model_validate(s) for s in tf.sequences]

@router.get("/{tf_id}/structures", response_model=List[ProteinStructureOut], summary="Get AlphaFold 3D Structures for TF")
def get_tf_structures(tf_id: int, db: Session = Depends(get_db)):
    """
    Retrieves AlphaFold 3D coordinate models and diagnostic evaluation metrics (Ranks 1 to 5) for a TF.
    """
    tf = db.query(TranscriptionFactor).filter(TranscriptionFactor.id == tf_id).first()
    if not tf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcription factor with id {tf_id} not found"
        )
    structures = sorted(tf.structures, key=lambda s: s.rank_num)
    return [ProteinStructureOut.model_validate(s) for s in structures]

@router.get("/{tf_id}/interactions", response_model=List[ProteinInteractionOut], summary="Get Protein Interactions for TF")
def get_tf_interactions(tf_id: int, db: Session = Depends(get_db)):
    """
    Retrieves STRING and FunCoup protein-protein interactions, confidence scores, and visual diagram paths for a TF.
    """
    tf = db.query(TranscriptionFactor).filter(TranscriptionFactor.id == tf_id).first()
    if not tf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcription factor with id {tf_id} not found"
        )
    interactions = sorted(tf.interactions, key=lambda i: i.combined_score, reverse=True)
    return [ProteinInteractionOut.model_validate(i) for i in interactions]
