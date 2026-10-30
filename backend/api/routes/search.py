from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.database import get_db
from backend.app.models.tf import TranscriptionFactor
from backend.app.models.plant import Plant
from backend.app.models.family import TFFamily
from backend.app.models.stress import StressCondition
from backend.app.models.target import TargetGene, Pathway
from backend.app.models.paper import ResearchPaper
from backend.app.models.identifier import TFIdentifier
from backend.schemas.search import SearchResultOut
from backend.schemas.transcription_factors import TFSummaryOut
from backend.schemas.plants import PlantOut
from backend.schemas.families import TFFamilyOut
from backend.schemas.stress_conditions import StressConditionOut
from backend.schemas.targets import TargetGeneOut
from backend.schemas.pathways import PathwayOut
from backend.schemas.papers import ResearchPaperOut

router = APIRouter(prefix="/search", tags=["Global Search"])

@router.get("", response_model=SearchResultOut, summary="Deterministic Cross-Entity Global Biological Search")
def global_search(
    q: str = Query(..., min_length=1, description="Search term across TFs, identifiers, plants, families, stresses, targets, pathways, papers"),
    limit: int = Query(20, ge=1, le=100, description="Maximum matches per entity category"),
    db: Session = Depends(get_db)
):
    """
    Executes a deterministic case-insensitive search across all primary biological entities in the PhytoStress Atlas.
    """
    term = q.strip()
    if not term:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search term cannot be empty"
        )
    pattern = f"%{term}%"

    # 1. Search TFs directly or via linked identifiers, stresses, plants, or families
    matching_tf_ids_from_ids = [
        r[0] for r in db.query(TFIdentifier.tf_id).filter(TFIdentifier.identifier_value.ilike(pattern)).distinct().all()
    ]
    
    tfs = db.query(TranscriptionFactor).filter(
        or_(
            TranscriptionFactor.tf_name.ilike(pattern),
            TranscriptionFactor.raw_supplied_tf.ilike(pattern),
            TranscriptionFactor.mechanism_description.ilike(pattern),
            TranscriptionFactor.id.in_(matching_tf_ids_from_ids),
            TranscriptionFactor.stresses.any(StressCondition.stress_name.ilike(pattern)),
            TranscriptionFactor.plant.has(or_(Plant.common_name.ilike(pattern), Plant.scientific_name.ilike(pattern))),
            TranscriptionFactor.family.has(TFFamily.name.ilike(pattern))
        )
    ).distinct().limit(limit).all()

    tf_summaries = []
    for tf in tfs:
        tf_summaries.append(
            TFSummaryOut(
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
        )

    # 2. Search Plants
    plants = db.query(Plant).filter(
        or_(
            Plant.common_name.ilike(pattern),
            Plant.scientific_name.ilike(pattern),
            Plant.display_name.ilike(pattern)
        )
    ).limit(limit).all()

    # 3. Search Families
    families = db.query(TFFamily).filter(
        or_(
            TFFamily.name.ilike(pattern),
            TFFamily.description.ilike(pattern)
        )
    ).limit(limit).all()

    # 4. Search Stress Conditions
    stresses = db.query(StressCondition).filter(
        or_(
            StressCondition.stress_name.ilike(pattern),
            StressCondition.category.ilike(pattern),
            StressCondition.stress_type.ilike(pattern)
        )
    ).limit(limit).all()

    # 5. Search Target Genes
    targets = db.query(TargetGene).filter(
        or_(
            TargetGene.gene_symbol.ilike(pattern),
            TargetGene.description.ilike(pattern)
        )
    ).limit(limit).all()

    # 6. Search Pathways
    pathways = db.query(Pathway).filter(
        or_(
            Pathway.pathway_name.ilike(pattern),
            Pathway.pathway_type.ilike(pattern)
        )
    ).limit(limit).all()

    # 7. Search Research Papers
    papers = db.query(ResearchPaper).filter(
        or_(
            ResearchPaper.title.ilike(pattern),
            ResearchPaper.journal.ilike(pattern),
            ResearchPaper.doi.ilike(pattern),
            ResearchPaper.authors.ilike(pattern)
        )
    ).limit(limit).all()

    total_matches = (
        len(tf_summaries) +
        len(plants) +
        len(families) +
        len(stresses) +
        len(targets) +
        len(pathways) +
        len(papers)
    )

    return SearchResultOut(
        query=term,
        total_matches=total_matches,
        transcription_factors=tf_summaries,
        plants=[PlantOut.model_validate(p) for p in plants],
        families=[TFFamilyOut.model_validate(f) for f in families],
        stress_conditions=[StressConditionOut.model_validate(s) for s in stresses],
        target_genes=[TargetGeneOut.model_validate(t) for t in targets],
        pathways=[PathwayOut.model_validate(pw) for pw in pathways],
        research_papers=[ResearchPaperOut.model_validate(rp) for rp in papers]
    )
