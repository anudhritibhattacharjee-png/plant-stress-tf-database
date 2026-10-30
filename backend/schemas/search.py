from typing import List
from pydantic import BaseModel, ConfigDict
from backend.schemas.plants import PlantOut
from backend.schemas.families import TFFamilyOut
from backend.schemas.stress_conditions import StressConditionOut
from backend.schemas.papers import ResearchPaperOut
from backend.schemas.targets import TargetGeneOut
from backend.schemas.pathways import PathwayOut
from backend.schemas.transcription_factors import TFSummaryOut

class SearchResultOut(BaseModel):
    query: str
    total_matches: int
    transcription_factors: List[TFSummaryOut] = []
    plants: List[PlantOut] = []
    families: List[TFFamilyOut] = []
    stress_conditions: List[StressConditionOut] = []
    target_genes: List[TargetGeneOut] = []
    pathways: List[PathwayOut] = []
    research_papers: List[ResearchPaperOut] = []

    model_config = ConfigDict(from_attributes=True)
