# Replace: app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API routers
from app.api import ingestion, extraction, matcher, review, schedule, audit

app = FastAPI(
    title="FORGE API",
    description="Field Operations Reconciliation & Gantt Engine",
    version="1.0.0"
)

# Allow frontend (Vite/React) to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(ingestion.router)
app.include_router(extraction.router)
app.include_router(matcher.router)
app.include_router(review.router)
app.include_router(schedule.router)
app.include_router(audit.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "project": "FORGE",
        "message": "Field Operations Reconciliation & Gantt Engine is active."
    }