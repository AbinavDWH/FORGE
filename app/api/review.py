# Replace: app/api/review.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

from app.schedule.xml_parser import parse_schedule
from app.schedule.cpm_guard import check_cpm_dependencies
from app.schedule.actuals_writer import write_actuals_to_xml
from app.audit.hash_chain import append_audit_record

router = APIRouter(prefix="/api/review", tags=["review"])

# In-memory tray for the demo
REVIEW_TRAY: List[Dict[str, Any]] = []

class ReviewItem(BaseModel):
    ingestion_id: str
    extracted_data: Dict[str, Any]
    matched_task_id: str
    match_score: float
    match_reason: str

@router.post("/tray/add")
def add_to_tray(item: ReviewItem):
    """Adds a medium-confidence match to the manager's review tray."""
    REVIEW_TRAY.append(item.dict())
    return {"status": "added to review tray"}

@router.get("/tray")
def get_tray():
    """Returns all pending items for manager approval."""
    return {"items": REVIEW_TRAY}

class ApprovalRequest(BaseModel):
    ingestion_id: str
    task_id: str
    percent_complete: int
    approved_by: str = "manager_ui"

@router.post("/approve")
def approve_update(request: ApprovalRequest):
    """Manager approves an update. Triggers CPM Guard and writes to XML."""
    schedule_data = parse_schedule()
    
    # 1. CPM Guard Check
    cpm_result = check_cpm_dependencies(
        task_id=request.task_id,
        proposed_percent=request.percent_complete,
        schedule_data=schedule_data
    )
    
    if not cpm_result["valid"]:
        raise HTTPException(status_code=409, detail=cpm_result["reason"])
        
    # 2. Write to XML
    success = write_actuals_to_xml(
        task_id=request.task_id,
        percent_complete=request.percent_complete,
        actual_start=datetime.utcnow().isoformat() + "Z",
        actual_finish=datetime.utcnow().isoformat() + "Z" if request.percent_complete == 100 else None
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found in schedule")
        
    # 3. Audit Trail
    append_audit_record(
        ingestion_id=request.ingestion_id,
        wbs_activity_id=request.task_id,
        action_performed=f"Approved and updated to {request.percent_complete}%",
        confidence_score=0.95,
        approved_by=request.approved_by
    )
    
    # 4. Remove from tray
    global REVIEW_TRAY
    REVIEW_TRAY = [item for item in REVIEW_TRAY if item["ingestion_id"] != request.ingestion_id]
    
    return {"status": "approved", "message": "Schedule updated and audit logged."}