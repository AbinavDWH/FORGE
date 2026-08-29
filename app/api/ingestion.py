from fastapi import APIRouter, File, Form, HTTPException, UploadFile

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
    record = ingestion_service.create_ingestion(req)
    try:
        return pipeline_service.process_ingestion(record["ingestion_id"])
    except InvalidStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/media/process", response_model=PipelineResponse)
async def upload_and_process_media(
    file: UploadFile = File(...),
    source: str = Form("web_upload"),
    device_id: str | None = Form(None),
    gps_coords: str | None = Form(None),
):
    """
    Zero-friction media input: voice note, site photo, or diary scan.
    Runs synthetic media screening, ASR/OCR, cross-check, then the pipeline.
    """
    raw = await file.read()
    record = ingestion_service.create_media_ingestion(
        filename=file.filename,
        content_type=file.content_type,
        raw=raw,
        source=source,
        device_id=device_id,
        gps_coords=gps_coords,
    )
    try:
        return pipeline_service.process_ingestion(record["ingestion_id"])
    except InvalidStateError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/updates", response_model=IngestUpdateResponse)
def create_update(req: IngestUpdateRequest):
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