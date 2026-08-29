from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from app.core.state import state

router = APIRouter(prefix="/api/schedule", tags=["schedule"])


@router.get("/tasks", response_model=List[Dict[str, Any]])
def get_tasks():
    """
    Returns live schedule tasks.

    The future frontend Gantt must render from this endpoint.
    No hardcoded Gantt bars are allowed.
    """
    return list(state.tasks.values())


@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
def get_task(task_id: str):
    task = state.tasks.get(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task