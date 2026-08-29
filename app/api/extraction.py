# Replace: app/api/extraction.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/extraction", tags=["extraction"])

class ExtractionRequest(BaseModel):
    ingestion_id: str
    raw_text: str

class ExtractionResponse(BaseModel):
    ingestion_id: str
    spatial_zone: Optional[str] = None
    discipline: Optional[str] = None
    component: Optional[str] = None
    action: Optional[str] = None
    status: Optional[str] = None
    percent_complete: Optional[int] = None
    extraction_confidence: float

@router.post("/extract", response_model=ExtractionResponse)
def extract_fields(request: ExtractionRequest):
    """
    Converts raw text into structured project fields.
    (In a full build, this calls Whisper/OCR/LLM. Here we use deterministic 
    rules for demo stability).
    """
    text = request.raw_text.lower()
    
    zone = "Zone B" if "zone b" in text or "sector b" in text else "Zone A"
    discipline = "Civil" if "concrete" in text or "pier" in text or "rebar" in text else "Piping"
    component = "Pier 14" if "pier 14" in text or "peer 14" in text else "Unknown"
    
    return {
        "ingestion_id": request.ingestion_id,
        "spatial_zone": zone,
        "discipline": discipline,
        "component": component,
        "action": request.raw_text,
        "status": "Completed" if "done" in text or "completed" in text else "In Progress",
        "percent_complete": 100 if "done" in text or "completed" in text else 50,
        "extraction_confidence": 0.88
    }