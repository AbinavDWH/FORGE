from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import audit, extraction, ingestion, matcher, review, schedule

app = FastAPI(
    title="FORGE API",
    version="0.1.0",
    description=(
        "Field Operations Reconciliation & Gantt Engine. "
        "Converts informal field updates into trusted schedule progress."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion.router)
app.include_router(extraction.router)
app.include_router(matcher.router)
app.include_router(review.router)
app.include_router(schedule.router)
app.include_router(audit.router)


@app.get("/")
def root():
    return {
        "project": "FORGE",
        "meaning": "Field Operations Reconciliation & Gantt Engine",
        "status": "Phase 1 backend skeleton",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "stage": "core-reconciliation-skeleton",
    }