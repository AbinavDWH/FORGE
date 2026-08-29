from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel


class IngestUpdateRequest(BaseModel):
    source: Literal["telegram", "ivr", "web_upload"] = "telegram"
    media_type: Literal["voice", "text", "image", "document"] = "text"

    raw_text: Optional[str] = None

    device_id: Optional[str] = None
    gps_coords: Optional[str] = None
    exif_present: Optional[bool] = None
    capture_timestamp: Optional[str] = None
    evidence_reference: Optional[str] = None


class IngestUpdateResponse(BaseModel):
    ingestion_id: str
    status: str


class ExtractionSchema(BaseModel):
    spatial_zone: Optional[str] = None
    discipline: Optional[str] = None
    component: Optional[str] = None
    action: Optional[str] = None
    status: Optional[str] = None
    percent_complete: Optional[int] = None
    timestamp: Optional[str] = None

    raw_text: Optional[str] = None
    language_hint: Optional[str] = None

    extraction_confidence: float = 0.0
    extraction_agreement: Optional[float] = None
    cross_check_status: str = "single_source"


class MatchCandidate(BaseModel):
    task_id: str
    task_name: str
    wbs_code: str
    match_score: float
    match_reason: str


class MatchResult(BaseModel):
    ingestion_id: str

    matched_task_id: Optional[str] = None
    task_name: Optional[str] = None
    wbs_code: Optional[str] = None

    match_score: float = 0.0
    match_reason: Optional[str] = None

    alternative_matches: List[MatchCandidate] = []


class ConfidenceResult(BaseModel):
    score: int
    routing: str
    explanation: List[str] = []


class PipelineResponse(BaseModel):
    ingestion_id: str
    status: str

    extraction: ExtractionSchema
    match: MatchResult
    confidence: ConfidenceResult

    schedule_update: Optional[Dict[str, Any]] = None
    review_message: Optional[str] = None

    # Added for Frontend Trust UI
    media_type: Optional[str] = None
    ai_generation_risk: Optional[str] = None
    evidence_url: Optional[str] = None
    cross_check_status: Optional[str] = None


class ApproveRequest(BaseModel):
    approved_by: str = "manager"
    # Added for Manager Correction UI
    corrected_extraction: Optional[ExtractionSchema] = None
    overridden_task_id: Optional[str] = None