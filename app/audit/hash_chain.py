# Replace: app/audit/hash_chain.py
import hashlib
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

AUDIT_LOG_PATH = Path(__file__).resolve().parents[2] / "storage" / "audit_chain.jsonl"

def _ensure_storage() -> None:
    """Ensure the storage directory and audit log file exist."""
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not AUDIT_LOG_PATH.exists():
        AUDIT_LOG_PATH.touch()

def _calculate_hash(record: Dict[str, Any]) -> str:
    """Generate a deterministic SHA-256 hash for an audit record."""
    # We must exclude the current_hash field itself when calculating the hash
    record_copy = {k: v for k, v in record.items() if k != "current_hash"}
    record_str = json.dumps(record_copy, sort_keys=True, default=str)
    return hashlib.sha256(record_str.encode("utf-8")).hexdigest()

def get_last_hash() -> str:
    """Retrieve the current_hash of the last entry in the chain."""
    _ensure_storage()
    last_hash = "0" * 64  # Genesis hash
    
    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line)
                    last_hash = entry.get("current_hash", last_hash)
                except json.JSONDecodeError:
                    continue
    return last_hash

def append_audit_record(
    ingestion_id: str,
    wbs_activity_id: str,
    action_performed: str,
    confidence_score: float,
    approved_by: Optional[str] = None,
    evidence_reference: Optional[str] = None,
    metadata_status: str = "unknown",
    cross_check_status: str = "single_source",
    ai_generation_risk: str = "low",
) -> Dict[str, Any]:
    """
    Append a new tamper-evident record to the audit chain.
    This is called after a manager approves/rejects an update, or after auto-commit.
    """
    _ensure_storage()
    
    # Calculate next sequential index
    log_index = 1
    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                log_index += 1
                
    previous_hash = get_last_hash()
    
    record = {
        "log_index": log_index,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "ingestion_id": ingestion_id,
        "wbs_activity_id": wbs_activity_id,
        "action_performed": action_performed,
        "confidence_score": confidence_score,
        "approved_by": approved_by or "system_auto",
        "evidence_reference": evidence_reference,
        "metadata_status": metadata_status,
        "cross_check_status": cross_check_status,
        "ai_generation_risk": ai_generation_risk,
        "previous_hash": previous_hash,
    }
    
    current_hash = _calculate_hash(record)
    record["current_hash"] = current_hash
    
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
        
    return record

def verify_chain() -> Dict[str, Any]:
    """
    Verify the integrity of the entire audit chain.
    Returns validation status and any errors found.
    """
    _ensure_storage()
    is_valid = True
    errors = []
    previous_hash = "0" * 64
    total_records = 0
    
    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
                
            total_records += 1
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                is_valid = False
                errors.append(f"Line {line_num}: Invalid JSON format")
                continue
                
            # Check chain linkage
            if entry.get("previous_hash") != previous_hash:
                is_valid = False
                errors.append(
                    f"Line {line_num}: Chain broken. Expected {previous_hash[:8]}..., "
                    f"got {entry.get('previous_hash', 'MISSING')[:8]}..."
                )
                
            # Verify record integrity (tamper check)
            stored_hash = entry.get("current_hash")
            calculated_hash = _calculate_hash(entry)
            
            if stored_hash != calculated_hash:
                is_valid = False
                errors.append(f"Line {line_num}: Record tampered. Hash mismatch.")
                
            previous_hash = stored_hash
            
    return {
        "is_valid": is_valid,
        "total_records": total_records,
        "errors": errors,
    }