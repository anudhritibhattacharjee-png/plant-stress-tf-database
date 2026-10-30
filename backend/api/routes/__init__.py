from backend.api.routes.health import router as health_router
from backend.api.routes.transcription_factors import router as tf_router
from backend.api.routes.plants import router as plants_router
from backend.api.routes.families import router as families_router
from backend.api.routes.stress_conditions import router as stress_router
from backend.api.routes.papers import router as papers_router
from backend.api.routes.pathways import router as pathways_router
from backend.api.routes.targets import router as targets_router
from backend.api.routes.sequences import router as sequences_router
from backend.api.routes.structures import router as structures_router
from backend.api.routes.interactions import router as interactions_router
from backend.api.routes.search import router as search_router

__all__ = [
    "health_router",
    "tf_router",
    "plants_router",
    "families_router",
    "stress_router",
    "papers_router",
    "pathways_router",
    "targets_router",
    "sequences_router",
    "structures_router",
    "interactions_router",
    "search_router"
]
