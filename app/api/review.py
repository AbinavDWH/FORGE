from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException

from app.api.schemas import ApproveRequest, PipelineResponse
from app.core.errors import (
    DependencyViolationError,
    InvalidStateError,
    TaskNotFoundError,
)
from app.core.state import state
from app.services import pipeline as pipeline_service

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("/tray", response_model=List[PipelineResponse])
def review_tray():
    """
    Manager Review Tray backend.

    Shows updates that need human attention:
    - pending_review
    - dependency_violation
    - manual_handling
    """
    return [
        update
        for update in state.updates.values()
        if update["status"]
        in ["pending_review", "dependency_violation", "manual_handling"]
    ]


@router.post("/{ingestion_id}/approve", response_model=PipelineResponse)
def approve_update(
    ingestion_id: str,
    payload: Optional[ApproveRequest] = Body(default=None),
):
    approved_by = payload.approved_by if payload else "manager"
    corrected_extraction = payload.corrected_extraction if payload else None
    overridden_task_id = payload.overridden_task_id if payload else None

    try:
        return pipeline_service.approve_update(
            ingestion_id=ingestion_id,
            approved_by=approved_by,
            corrected_extraction=corrected_extraction,
            overridden_task_id=overridden_task_id,
        )
    except InvalidStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except DependencyViolationError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{ingestion_id}/reject", response_model=PipelineResponse)
def reject_update(
    ingestion_id: str,
    payload: Optional[ApproveRequest] = Body(default=None),
):
    approved_by = payload.approved_by if payload else "manager"

    try:
        return pipeline_service.reject_update(
            ingestion_id=ingestion_id,
            approved_by=approved_by,
        )
    except InvalidStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc))