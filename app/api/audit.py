# Replace: app/api/audit.py
from fastapi import APIRouter
from app.audit.hash_chain import verify_chain, AUDIT_LOG_PATH
import json

router = APIRouter(prefix="/api/audit", tags=["audit"])

@router.get("/chain")
def get_audit_chain():
    """Returns the full tamper-evident audit log."""
    records = []
    if AUDIT_LOG_PATH.exists():
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
                    
    # Reverse so newest is first
    records.reverse()
    return {"records": records, "total": len(records)}

@router.get("/verify")
def verify_audit_chain():
    """Mathematically verifies the integrity of the SHA-256 chain."""
    return verify_chain()