from fastapi import APIRouter, HTTPException

from app.api.schemas import MatchResult
from app.core.errors import InvalidStateError
from app.services import matcher as matcher_service

router = APIRouter(prefix="/api/matcher", tags=["matcher"])


@router.post("/{ingestion_id}/run", response_model=MatchResult)
def run_matcher(ingestion_id: str):
    try:
        return matcher_service.match(ingestion_id)
    except InvalidStateError as exc:
        raise HTTPException(status_code=404, detail=str(exc))