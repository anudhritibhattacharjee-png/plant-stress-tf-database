from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.schemas.plants import TFSummaryForRelated

class ResearchPaperBase(BaseModel):
    title: str
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    doi_url: Optional[str] = None
    pubmed_id: Optional[str] = None
    authors: Optional[str] = None
    raw_citation_text: Optional[str] = None

class ResearchPaperOut(ResearchPaperBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ResearchPaperDetailOut(ResearchPaperOut):
    transcription_factors: List[TFSummaryForRelated] = []

    model_config = ConfigDict(from_attributes=True)
