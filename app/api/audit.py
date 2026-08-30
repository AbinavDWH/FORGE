# Replace: app/api/audit.py
from fastapi import APIRouter
from app.audit.hash_chain import verify_chain, AUDIT_LOG_PATH, _ensure_storage
import json

router = APIRouter(prefix="/api/audit", tags=["audit"])

@router.get("/chain")
def get_audit_chain():
    """Returns the full tamper-evident audit log."""
    _ensure_storage() # Guarantee the file exists before reading
    records = []
    
    if AUDIT_LOG_PATH.exists():
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue # Skip corrupted lines safely
                        
    # Reverse so newest is first
    records.reverse()
    return {"records": records, "total": len(records)}

@router.get("/verify")
def verify_audit_chain():
    """Mathematically verifies the integrity of the SHA-256 chain."""
    return verify_chain()