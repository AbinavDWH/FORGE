"""MOD-04: Confidence & Review Engine — API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.schedule.xml_parser import parse_schedule
from app.schedule.cpm_guard import check_cpm_dependencies
from app.schedule.actuals_writer import write_actuals_to_xml
from app.audit.hash_chain import append_audit_record

router = APIRouter(prefix="/api/review", tags=["review"])

# In-memory tray for the demo
REVIEW_TRAY: List[Dict[str, Any]] = []


def add_to_review_tray(item: dict):
    """Add a processed update to the manager's review tray."""
    REVIEW_TRAY.append(item)


class ReviewItem(BaseModel):
    """Legacy model for direct tray additions."""
    ingestion_id: str
    extracted_data: Dict[str, Any]
    matched_task_id: str
    match_score: float
    match_reason: str


class ApprovalRequest(BaseModel):
    approved_by: str = "Manager"
    corrected_extraction: Optional[Dict[str, Any]] = None
    overridden_task_id: Optional[str] = None


@router.post("/tray/add")
def add_to_tray(item: ReviewItem):
    """Adds a medium-confidence match to the manager's review tray (legacy endpoint)."""
    review_item = {
        "ingestion_id": item.ingestion_id,
        "status": "pending_review",
        "media_type": "text",
        "ai_generation_risk": "low",
        "evidence_url": None,
        "cross_check_status": "single_source",
        "extraction": item.extracted_data,
        "match": {
            "matched_task_id": item.matched_task_id,
            "task_name": item.matched_task_id,
            "wbs_code": item.matched_task_id,
            "match_score": item.match_score,
            "match_reason": item.match_reason,
            "alternative_matches": [],
        },
        "confidence": {
            "score": int(item.match_score * 100),
            "routing": "review",
            "explanation": [],
        },
        "received_at": datetime.utcnow().isoformat() + "Z",
    }
    REVIEW_TRAY.append(review_item)
    return {"status": "added to review tray"}


@router.get("/tray")
def get_tray():
    """Returns all pending items for manager review."""
    return REVIEW_TRAY


@router.post("/{ingestion_id}/approve")
def approve_update(ingestion_id: str, request: ApprovalRequest):
    """Manager approves an update. Triggers CPM Guard and writes to XML."""
    global REVIEW_TRAY

    # Find the item in tray
    item = next(
        (i for i in REVIEW_TRAY if i["ingestion_id"] == ingestion_id),
        None,
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in review tray")

    # Use corrected data if provided
    extraction = request.corrected_extraction or item.get("extraction", {})
    task_id = request.overridden_task_id or item.get("match", {}).get("matched_task_id")
    percent_complete = extraction.get("percent_complete", 0)

    if not task_id:
        raise HTTPException(status_code=400, detail="No task matched or selected")

    schedule_data = parse_schedule()

    # 1. CPM Guard Check
    cpm_result = check_cpm_dependencies(
        task_id=task_id,
        proposed_percent=percent_complete,
        schedule_data=schedule_data,
    )

    if not cpm_result["valid"]:
        raise HTTPException(status_code=409, detail=cpm_result["reason"])

    # 2. Write to XML
    now = datetime.utcnow().isoformat() + "Z"
    success = write_actuals_to_xml(
        task_id=task_id,
        percent_complete=percent_complete,
        actual_start=now,
        actual_finish=now if percent_complete == 100 else None,
    )

    if not success:
        raise HTTPException(status_code=404, detail="Task not found in schedule XML")

    # 3. Audit Trail
    append_audit_record(
        ingestion_id=ingestion_id,
        wbs_activity_id=task_id,
        action_performed=f"Approved and updated to {percent_complete}%",
        confidence_score=item.get("confidence", {}).get("score", 0),
        approved_by=request.approved_by,
        cross_check_status=item.get("cross_check_status", "single_source"),
        ai_generation_risk=item.get("ai_generation_risk", "low"),
    )

    # 4. Remove from tray
    REVIEW_TRAY = [i for i in REVIEW_TRAY if i["ingestion_id"] != ingestion_id]

    return {
        "status": "approved",
        "message": f"Schedule updated to {percent_complete}%. Audit logged.",
        "task_id": task_id,
        "cpm_status": cpm_result["reason"],
    }


@router.post("/{ingestion_id}/reject")
def reject_update(ingestion_id: str, request: ApprovalRequest):
    """Manager rejects an update. Creates audit record, removes from tray."""
    global REVIEW_TRAY
    item = next(
        (i for i in REVIEW_TRAY if i["ingestion_id"] == ingestion_id),
        None,
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in review tray")

    # Audit trail for rejection
    append_audit_record(
        ingestion_id=ingestion_id,
        wbs_activity_id=item.get("match", {}).get("matched_task_id", "unknown"),
        action_performed="Rejected by manager",
        confidence_score=item.get("confidence", {}).get("score", 0),
        approved_by=request.approved_by,
        cross_check_status=item.get("cross_check_status", "single_source"),
        ai_generation_risk=item.get("ai_generation_risk", "low"),
    )

    # Remove from tray
    REVIEW_TRAY = [i for i in REVIEW_TRAY if i["ingestion_id"] != ingestion_id]

    return {"status": "rejected", "message": "Update rejected. Audit logged."}


@router.post("/approve")
def approve_update_legacy(request: dict):
    """Legacy approve endpoint for backwards compatibility."""
    ingestion_id = request.get("ingestion_id")
    if not ingestion_id:
        raise HTTPException(status_code=400, detail="ingestion_id required")
    return approve_update(
        ingestion_id,
        ApprovalRequest(
            approved_by=request.get("approved_by", "manager_ui"),
        ),
    )