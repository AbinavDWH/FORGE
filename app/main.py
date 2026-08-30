"""FORGE — Field Operations Reconciliation & Gantt Engine."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api import ingestion, extraction, matcher, review, schedule, audit, webhooks

app = FastAPI(title="FORGE API", version="1.0.0")

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
app.include_router(webhooks.router)

# Serve uploaded evidence files
storage_raw = Path("storage/raw")
storage_raw.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(storage_raw)), name="static")


@app.get("/")
def root():
    return {"status": "online", "project": "FORGE", "version": "0.3.0"}