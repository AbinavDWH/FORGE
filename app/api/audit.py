from typing import Any, Dict, List

from fastapi import APIRouter

from app.core.state import state

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/logs", response_model=List[Dict[str, Any]])
def get_audit_logs():
    """
    Returns the append-only audit chain.
    """
    return state.audit_log