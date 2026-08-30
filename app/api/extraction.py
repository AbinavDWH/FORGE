"""MOD-02: Multi-Modal Extraction Pipeline — API endpoint."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.extraction.structurer import structure_text

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
    raw_text: Optional[str] = None
    language_hint: Optional[str] = None
    extraction_confidence: float = 0.0
    extraction_agreement: Optional[float] = None
    cross_check_status: str = "single_source"


@router.post("/extract", response_model=ExtractionResponse)
def extract_fields(request: ExtractionRequest):
    """
    Converts raw text into structured project fields.
    Uses the deterministic structurer for stable demo results.
    Never invents missing fields — unknown values stay None.
    """
    structured = structure_text(request.raw_text)

    # Calculate extraction confidence based on field completeness
    filled = sum(1 for v in structured.values() if v is not None)
    total = len(structured)
    confidence = round(filled / total, 2) if total > 0 else 0.0

    return ExtractionResponse(
        ingestion_id=request.ingestion_id,
        spatial_zone=structured.get("spatial_zone"),
        discipline=structured.get("discipline"),
        component=structured.get("component"),
        action=structured.get("action"),
        status=structured.get("status"),
        percent_complete=structured.get("percent_complete"),
        raw_text=request.raw_text,
        extraction_confidence=confidence,
    )