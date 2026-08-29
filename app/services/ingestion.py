import hashlib
from datetime import datetime, timezone

from app.api.schemas import IngestUpdateRequest
from app.core.errors import InvalidStateError
from app.core.state import state


def create_ingestion(req: IngestUpdateRequest) -> dict:
    ingestion_id = state.next_ingestion_id()

    raw_text = req.raw_text
    original_sha256 = None

    if raw_text:
        original_sha256 = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

    metadata_status = "missing_metadata"

    if req.gps_coords and req.exif_present is True:
        metadata_status = "verified"

    record = {
        "ingestion_id": ingestion_id,
        "source": req.source,
        "media_type": req.media_type,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "device_id": req.device_id,
        "gps_coords": req.gps_coords,
        "exif_present": req.exif_present,
        "capture_timestamp": req.capture_timestamp,
        "original_sha256": original_sha256,
        "compressed_sha256": original_sha256,
        "raw_text": raw_text,
        "evidence_reference": req.evidence_reference,
        "metadata_status": metadata_status,
        # Placeholder until synthetic media gate is implemented.
        "ai_generation_risk": "low",
        "status": "ingested",
    }

    state.ingestions[ingestion_id] = record
    return record


def get_ingestion(ingestion_id: str) -> dict:
    ingestion = state.ingestions.get(ingestion_id)

    if not ingestion:
        raise InvalidStateError(f"Ingestion {ingestion_id} not found.")

    return ingestion