from datetime import datetime, timezone
from typing import Any, Dict, List

from app.api.schemas import ExtractionSchema
from app.core.errors import (
    DependencyViolationError,
    InvalidStateError,
    TaskNotFoundError,
)
from app.core.state import state


def get_task(task_id: str) -> Dict[str, Any]:
    task = state.tasks.get(task_id)

    if not task:
        raise TaskNotFoundError(f"Task {task_id} not found.")

    return task


def _incomplete_predecessors(task: Dict[str, Any]) -> List[str]:
    incomplete = []

    for dependency_id in task.get("dependencies", []):
        dependency = state.tasks.get(dependency_id)

        if not dependency:
            incomplete.append(dependency_id)
            continue

        if dependency.get("percent_complete", 0) < 100:
            incomplete.append(dependency_id)

    return incomplete


def validate_dependency_order(task: Dict[str, Any], extraction: ExtractionSchema) -> None:
    """
    CPM Guard:
    - Do not allow progress if predecessor is incomplete.
    - Do not allow completion if predecessor is incomplete.
    """
    has_actionable_progress = (
        extraction.status == "Completed"
        or (extraction.percent_complete or 0) > 0
    )

    if not has_actionable_progress:
        return

    incomplete = _incomplete_predecessors(task)

    if incomplete:
        raise DependencyViolationError(
            f"Cannot update {task['activity_id']} because predecessor tasks are incomplete: "
            f"{', '.join(incomplete)}."
        )


def apply_actuals(
    task_id: str,
    extraction: ExtractionSchema,
    ingestion_id: str,
    approved_by: str,
) -> Dict[str, Any]:
    """
    Non-destructive schedule write-back.

    Only actuals are updated:
    - actual_start
    - actual_finish
    - percent_complete
    - status
    - evidence reference
    - update metadata

    Baseline and dependencies are not modified.
    """
    task = get_task(task_id)

    if not extraction.status and extraction.percent_complete is None:
        raise InvalidStateError("No actionable schedule update found.")

    validate_dependency_order(task, extraction)

    now = datetime.now(timezone.utc).isoformat()

    before = {
        "percent_complete": task["percent_complete"],
        "actual_start": task["actual_start"],
        "actual_finish": task["actual_finish"],
        "status": task["status"],
    }

    if extraction.status == "Completed" or extraction.percent_complete == 100:
        task["percent_complete"] = 100
        task["status"] = "completed"

        if not task["actual_start"]:
            task["actual_start"] = task.get("planned_start")

        task["actual_finish"] = now

    elif extraction.percent_complete is not None:
        task["percent_complete"] = max(
            task["percent_complete"],
            min(100, extraction.percent_complete),
        )

        if task["percent_complete"] >= 100:
            task["status"] = "completed"
            task["actual_finish"] = now
        else:
            task["status"] = "in_progress"

        if not task["actual_start"]:
            task["actual_start"] = now

    elif extraction.status == "In Progress":
        task["status"] = "in_progress"

        if not task["actual_start"]:
            task["actual_start"] = now

    task["last_updated"] = now
    task["last_update_ingestion_id"] = ingestion_id
    task["last_update_approved_by"] = approved_by

    ingestion = state.ingestions.get(ingestion_id, {})
    task["evidence_reference"] = ingestion.get("evidence_reference")

    after = {
        "percent_complete": task["percent_complete"],
        "actual_start": task["actual_start"],
        "actual_finish": task["actual_finish"],
        "status": task["status"],
    }

    return {
        "task_id": task_id,
        "wbs_code": task["wbs_code"],
        "before": before,
        "after": after,
        "approved_by": approved_by,
        "ingestion_id": ingestion_id,
        "updated_at": now,
    }