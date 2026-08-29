# Replace: app/api/schedule.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.schedule.xml_parser import parse_schedule
from app.schedule.cpm_guard import check_cpm_dependencies
from app.schedule.actuals_writer import write_actuals_to_xml
from app.audit.hash_chain import append_audit_record

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

class UpdateActualsRequest(BaseModel):
    task_id: str
    percent_complete: int
    actual_start: Optional[str] = None
    actual_finish: Optional[str] = None
    ingestion_id: Optional[str] = None
    approved_by: Optional[str] = "manager_ui"

@router.get("/tasks")
def get_schedule_tasks():
    """
    Returns the live schedule parsed from the MS Project XML file.
    """
    tasks = parse_schedule()
    return {"tasks": tasks, "source": "nrl_crude_tank.xml"}

@router.post("/update_actuals")
def update_actuals(request: UpdateActualsRequest):
    """
    Updates actual progress. Protected by CPM Guard.
    """
    schedule_data = parse_schedule()
    
    # 1. CPM Guard Check
    cpm_result = check_cpm_dependencies(
        task_id=request.task_id,
        proposed_percent=request.percent_complete,
        schedule_data=schedule_data
    )
    
    if not cpm_result["valid"]:
        # Return 409 Conflict to trigger the CPM Guard UI alert
        raise HTTPException(status_code=409, detail=cpm_result["reason"])
        
    # 2. Auto-fill dates if not provided
    actual_start = request.actual_start
    actual_finish = request.actual_finish
    
    if request.percent_complete > 0 and not actual_start:
        actual_start = datetime.utcnow().isoformat() + "Z"
        
    if request.percent_complete == 100 and not actual_finish:
        actual_finish = datetime.utcnow().isoformat() + "Z"
        
    # 3. Write to XML
    success = write_actuals_to_xml(
        task_id=request.task_id,
        percent_complete=request.percent_complete,
        actual_start=actual_start,
        actual_finish=actual_finish
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Task ID not found in XML schedule.")
        
    # 4. Audit Trail
    append_audit_record(
        ingestion_id=request.ingestion_id or "manual_update",
        wbs_activity_id=request.task_id,
        action_performed=f"Progress updated to {request.percent_complete}%",
        confidence_score=1.0,
        approved_by=request.approved_by,
        metadata_status="verified",
        cross_check_status="agreed"
    )
    
    return {
        "status": "success",
        "message": "Schedule actuals updated successfully. Baseline preserved.",
        "task_id": request.task_id,
        "new_percent_complete": request.percent_complete,
        "cpm_status": cpm_result["reason"]
    }