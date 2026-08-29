# Replace: app/api/matcher.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

from app.matcher.hybrid_search import match_update
from app.schedule.xml_parser import parse_schedule

router = APIRouter(prefix="/api/matcher", tags=["matcher"])

class MatchRequest(BaseModel):
    update: Dict[str, Any]

@router.post("/match")
def match_field_update(request: MatchRequest):
    """
    Takes a raw field update and matches it against the live XML schedule 
    using the RapidFuzz hybrid matcher.
    """
    live_schedule = parse_schedule()
    result = match_update(request.update, live_schedule)
    return result