from app.api.schemas import ExtractionSchema, MatchResult
from app.core.errors import (
    DependencyViolationError,
    InvalidStateError,
    TaskNotFoundError,
)
from app.core.state import state
from app.services import (
    audit as audit_service,
    confidence as confidence_service,
    extraction as extraction_service,
    ingestion as ingestion_service,
    matcher as matcher_service,
    schedule as schedule_service,
)


def process_ingestion(ingestion_id: str) -> dict:
    ingestion = ingestion_service.get_ingestion(ingestion_id)

    extraction = extraction_service.extract(ingestion_id)
    match = matcher_service.match(ingestion_id)
    confidence = confidence_service.compute_confidence(ingestion_id)

    status = "pending_review"
    review_message = None
    schedule_update = None

    if not match.matched_task_id:
        status = "manual_handling"
        review_message = "No schedule task matched with sufficient context."

    elif confidence.routing == "auto_commit":
        try:
            schedule_update = schedule_service.apply_actuals(
                task_id=match.matched_task_id,
                extraction=extraction,
                ingestion_id=ingestion_id,
                approved_by="FORGE_AUTO",
            )

            status = "auto_committed"

            audit_service.append_audit(
                ingestion_id=ingestion_id,
                wbs_activity_id=match.matched_task_id,
                action_performed=(
                    "Auto-committed update: "
                    f"{extraction.status or extraction.percent_complete or 'progress'}"
                ),
                confidence_score=confidence.score,
                approved_by="FORGE_AUTO",
                evidence_reference=ingestion.get("evidence_reference"),
                metadata_status=ingestion.get("metadata_status", "unknown"),
                cross_check_status=extraction.cross_check_status,
                ai_generation_risk=ingestion.get("ai_generation_risk", "low"),
            )

        except DependencyViolationError as exc:
            status = "dependency_violation"
            review_message = str(exc)

            confidence.explanation.append(
                "CPM dependency violation: auto-commit blocked."
            )
            confidence.score = min(confidence.score, 60)
            confidence.routing = "manager_review"

            state.ingestions[ingestion_id]["confidence"] = confidence.model_dump()

        except TaskNotFoundError as exc:
            status = "manual_handling"
            review_message = str(exc)

        except InvalidStateError as exc:
            status = "manual_handling"
            review_message = str(exc)

    else:
        if confidence.routing == "manager_review":
            status = "pending_review"
        else:
            status = "manual_handling"

    # Build evidence URL for frontend thumbnail
    evidence_url = None
    if ingestion.get("evidence_reference") and ingestion.get("media_type") in ("image", "document"):
        evidence_url = f"/storage/raw/{ingestion.get('evidence_reference')}"

    update_record = {
        "ingestion_id": ingestion_id,
        "status": status,
        "extraction": extraction.model_dump(),
        "match": match.model_dump(),
        "confidence": confidence.model_dump(),
        "schedule_update": schedule_update,
        "review_message": review_message,
        # Added for Frontend Trust UI
        "media_type": ingestion.get("media_type"),
        "ai_generation_risk": ingestion.get("ai_generation_risk"),
        "cross_check_status": extraction.cross_check_status,
        "evidence_url": evidence_url,
    }

    state.updates[ingestion_id] = update_record

    return update_record


def approve_update(
    ingestion_id: str, 
    approved_by: str = "manager",
    corrected_extraction: ExtractionSchema | None = None,
    overridden_task_id: str | None = None,
) -> dict:
    update = state.updates.get(ingestion_id)

    if not update:
        raise InvalidStateError(f"No pipeline update found for {ingestion_id}.")

    if update["status"] in ["approved_committed", "auto_committed", "rejected"]:
        raise InvalidStateError(f"Update {ingestion_id} is already closed.")

    # 1. Use manager's corrected extraction if provided, else use AI extraction
    extraction = corrected_extraction if corrected_extraction else ExtractionSchema(**update["extraction"])
    
    # 2. Use manager's overridden task ID if provided, else use AI match
    match = MatchResult(**update["match"])
    target_task_id = overridden_task_id or match.matched_task_id

    if not target_task_id:
        raise InvalidStateError("Cannot approve update without a target schedule task.")

    # Apply the schedule update (CPM guard will run here against the target task)
    schedule_update = schedule_service.apply_actuals(
        task_id=target_task_id,
        extraction=extraction,
        ingestion_id=ingestion_id,
        approved_by=approved_by,
    )

    # Update the stored record
    update["status"] = "approved_committed"
    update["schedule_update"] = schedule_update
    update["review_message"] = None
    update["extraction"] = extraction.model_dump()
    
    if overridden_task_id:
        update["match"]["matched_task_id"] = target_task_id
        update["match"]["match_reason"] = "Overridden by manager correction"

    ingestion = state.ingestions.get(ingestion_id, {})

    audit_service.append_audit(
        ingestion_id=ingestion_id,
        wbs_activity_id=target_task_id,
        action_performed=(
            f"Manager corrected & approved: "
            f"{extraction.status or extraction.percent_complete or 'progress'}"
        ),
        confidence_score=update["confidence"]["score"],
        approved_by=approved_by,
        evidence_reference=ingestion.get("evidence_reference"),
        metadata_status=ingestion.get("metadata_status", "unknown"),
        cross_check_status=extraction.cross_check_status,
        ai_generation_risk=ingestion.get("ai_generation_risk", "low"),
    )

    state.updates[ingestion_id] = update

    return update


def reject_update(ingestion_id: str, approved_by: str = "manager") -> dict:
    update = state.updates.get(ingestion_id)

    if not update:
        raise InvalidStateError(f"No pipeline update found for {ingestion_id}.")

    if update["status"] in ["approved_committed", "auto_committed", "rejected"]:
        raise InvalidStateError(f"Update {ingestion_id} is already closed.")

    update["status"] = "rejected"
    update["schedule_update"] = None
    update["review_message"] = "Rejected by manager."

    ingestion = state.ingestions.get(ingestion_id, {})
    extraction = ExtractionSchema(**update["extraction"])
    match = MatchResult(**update["match"])

    audit_service.append_audit(
        ingestion_id=ingestion_id,
        wbs_activity_id=match.matched_task_id,
        action_performed="Manager rejected update",
        confidence_score=update["confidence"]["score"],
        approved_by=approved_by,
        evidence_reference=ingestion.get("evidence_reference"),
        metadata_status=ingestion.get("metadata_status", "unknown"),
        cross_check_status=extraction.cross_check_status,
        ai_generation_risk=ingestion.get("ai_generation_risk", "low"),
    )

    state.updates[ingestion_id] = update

    return update