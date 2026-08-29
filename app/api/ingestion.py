from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    IngestUpdateRequest,
    IngestUpdateResponse,
    PipelineResponse,
)
from app.core.errors import InvalidStateError
from app.services import ingestion as ingestion_service
from app.services import pipeline as pipeline_service

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])


@router.post("/updates/process", response_model=PipelineResponse)
def create_and_process_update(req: IngestUpdateRequest):
    """
    Demo-friendly endpoint:
    Creates a field update and immediately runs the core pipeline.
    """
    record = ingestion_service.create_ingestion(req)

    try:
        return pipeline_service.process_ingestion(record["ingestion_id"])
    except InvalidStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/updates", response_model=IngestUpdateResponse)
def create_update(req: IngestUpdateRequest):
    """
    Creates an ingestion record only.
    Use /updates/{ingestion_id}/process to run the pipeline.
    """
    record = ingestion_service.create_ingestion(req)

    return IngestUpdateResponse(
        ingestion_id=record["ingestion_id"],
        status=record["status"],
    )


@router.post("/updates/{ingestion_id}/process", response_model=PipelineResponse)
def process_update(ingestion_id: str):
    try:
        return pipeline_service.process_ingestion(ingestion_id)
    except InvalidStateError as exc:
        raise HTTPException(status_code=404, detail=str(exc))