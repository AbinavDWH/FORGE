from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from app.matcher.hybrid_search import match_update

router = APIRouter(prefix="/api/matcher", tags=["matcher"])


class MatchRequest(BaseModel):
    update: Dict[str, Any]
    tasks: List[Dict[str, Any]]
    limit: int = 5


@router.post("/match")
def match(request: MatchRequest):
    """
    Development endpoint for matcher testing.

    In production flow, tasks should come from the schedule service/parser,
    not from the client.
    """
    return match_update(
        update=request.update,
        tasks=request.tasks,
        limit=request.limit,
    )