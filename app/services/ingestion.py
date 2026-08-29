import hashlib
import os
from datetime import datetime, timezone

from app.api.schemas import IngestUpdateRequest
from app.core.errors import InvalidStateError
from app.core.settings import settings
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
        "ai_generation_risk": "low",
        "status": "ingested",
    }

    state.ingestions[ingestion_id] = record
    return record


def _detect_media_type(content_type: str, filename: str) -> str:
    ct = (content_type or "").lower()
    if ct.startswith("image/"):
        return "image"
    if ct.startswith("audio/"):
        return "voice"
    ext = os.path.splitext(filename or "")[1].lower()
    if ext in (".png", ".jpg", ".jpeg", ".webp"):
        return "image"
    if ext in (".ogg", ".mp3", ".wav", ".m4a", ".opus"):
        return "voice"
    return "document"


def create_media_ingestion(
    filename: str,
    content_type: str,
    raw: bytes,
    source: str,
    device_id: str | None,
    gps_coords: str | None,
) -> dict:
    ingestion_id = state.next_ingestion_id()
    media_type = _detect_media_type(content_type, filename)

    raw_dir = os.path.join(settings.storage_root, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    safe_name = os.path.basename(filename or "upload.bin")
    file_path = os.path.join(raw_dir, f"{ingestion_id}_{safe_name}")
    with open(file_path, "wb") as fh:
        fh.write(raw)

    original_sha256 = hashlib.sha256(raw).hexdigest()

    exif_present = None
    capture_timestamp = None
    ai_generation_risk = "low"
    c2pa_detected = False
    screening = None

    if media_type == "image":
        from app.audit.synthetic_media_gate import screen_image

        screening = screen_image(raw)
        exif_present = screening["exif_present"]
        ai_generation_risk = screening["ai_generation_risk"]
        c2pa_detected = screening["c2pa_detected"]

        try:
            import io
            from PIL import Image

            exif = Image.open(io.BytesIO(raw)).getexif()
            capture_timestamp = exif.get(0x9003) or exif.get(0x0132)
        except Exception:
            capture_timestamp = None

    if gps_coords and (exif_present or media_type == "voice"):
        metadata_status = "verified"
    else:
        metadata_status = "missing_metadata"

    record = {
        "ingestion_id": ingestion_id,
        "source": source,
        "media_type": media_type,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "device_id": device_id,
        "gps_coords": gps_coords,
        "exif_present": exif_present,
        "capture_timestamp": capture_timestamp,
        "original_sha256": original_sha256,
        "compressed_sha256": original_sha256,
        "raw_text": None,
        "file_path": file_path,
        "filename": safe_name,
        "evidence_reference": safe_name,
        "metadata_status": metadata_status,
        "ai_generation_risk": ai_generation_risk,
        "c2pa_detected": c2pa_detected,
        "screening": screening,
        "status": "ingested",
    }

    state.ingestions[ingestion_id] = record
    return record


def get_ingestion(ingestion_id: str) -> dict:
    ingestion = state.ingestions.get(ingestion_id)
    if not ingestion:
        raise InvalidStateError(f"Ingestion {ingestion_id} not found.")
    return ingestion