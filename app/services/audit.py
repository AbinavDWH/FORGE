import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.core.state import state


def _canonical_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def append_audit(
    *,
    ingestion_id: str,
    wbs_activity_id: Optional[str] = None,
    action_performed: str,
    confidence_score: Optional[int] = None,
    approved_by: Optional[str] = None,
    evidence_reference: Optional[str] = None,
    metadata_status: str = "unknown",
    cross_check_status: str = "single_source",
    ai_generation_risk: str = "low",
) -> Dict[str, Any]:
    """
    Append-only SHA-256 hash-chain audit log.

    This is not marketed as blockchain.
    It is a tamper-evident audit chain.
    """
    previous_hash = (
        state.audit_log[-1]["current_hash"]
        if state.audit_log
        else "GENESIS"
    )

    log_index = len(state.audit_log) + 1
    timestamp = datetime.now(timezone.utc).isoformat()

    base_payload = {
        "log_index": log_index,
        "timestamp": timestamp,
        "ingestion_id": ingestion_id,
        "wbs_activity_id": wbs_activity_id,
        "action_performed": action_performed,
        "confidence_score": confidence_score,
        "approved_by": approved_by,
        "evidence_reference": evidence_reference,
        "metadata_status": metadata_status,
        "cross_check_status": cross_check_status,
        "ai_generation_risk": ai_generation_risk,
        "previous_hash": previous_hash,
    }

    canonical = _canonical_json(base_payload)
    current_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    record = {
        **base_payload,
        "current_hash": current_hash,
    }

    state.audit_log.append(record)

    return record