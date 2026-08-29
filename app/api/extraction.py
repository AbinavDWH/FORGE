from fastapi import APIRouter, HTTPException

from app.api.schemas import ExtractionSchema
from app.core.errors import InvalidStateError
from app.services import extraction as extraction_service

router = APIRouter(prefix="/api/extraction", tags=["extraction"])


@router.post("/{ingestion_id}/run", response_model=ExtractionSchema)
def run_extraction(ingestion_id: str):
    try:
        return extraction_service.extract(ingestion_id)
    except InvalidStateError as exc:
        raise HTTPException(status_code=404, detail=str(exc))