"""
PhytoStress TF Atlas - Main FastAPI Application
==============================================
Exposes validated transcription factors, plant species, stress conditions,
target genes, pathways, research papers, FASTA protein sequences, AlphaFold 3D
models, and STRING/FunCoup PPI networks.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from backend.app.config import settings
from backend.api.routes import (
    health_router,
    tf_router,
    plants_router,
    families_router,
    stress_router,
    papers_router,
    pathways_router,
    targets_router,
    sequences_router,
    structures_router,
    interactions_router,
    search_router
)

# Initialize FastAPI Application
app = FastAPI(
    title="PhytoStress TF Atlas API",
    description=(
        "Production-grade RESTful API serving curated plant stress transcription factor "
        "dossiers, physical FASTA sequences, AlphaFold 3D coordinates, and PPI networks."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS Middleware
# Default local origins allowed for frontend development
cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]

# Merge any custom configured origins from settings
if isinstance(settings.CORS_ORIGINS, list):
    for origin in settings.CORS_ORIGINS:
        if origin not in cors_origins:
            cors_origins.append(origin)
elif isinstance(settings.CORS_ORIGINS, str) and settings.CORS_ORIGINS != "*":
    for origin in [o.strip() for o in settings.CORS_ORIGINS.split(",")]:
        if origin not in cors_origins:
            cors_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint redirects to interactive Swagger documentation
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

# Register API Routers under /api prefix
api_prefix = "/api"
app.include_router(health_router, prefix=api_prefix)
app.include_router(tf_router, prefix=api_prefix)
app.include_router(plants_router, prefix=api_prefix)
app.include_router(families_router, prefix=api_prefix)
app.include_router(stress_router, prefix=api_prefix)
app.include_router(papers_router, prefix=api_prefix)
app.include_router(pathways_router, prefix=api_prefix)
app.include_router(targets_router, prefix=api_prefix)
app.include_router(sequences_router, prefix=api_prefix)
app.include_router(structures_router, prefix=api_prefix)
app.include_router(interactions_router, prefix=api_prefix)
app.include_router(search_router, prefix=api_prefix)
