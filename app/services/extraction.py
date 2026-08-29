from app.api.schemas import ExtractionSchema
from app.core.errors import InvalidStateError
from app.core.logging import get_logger
from app.core.state import state
from app.crosscheck import comparator
from app.extraction import ocr_service, structurer, vlm_verifier, whisper_asr

log = get_logger(__name__)


def extract(ingestion_id: str) -> ExtractionSchema:
    ingestion = state.ingestions.get(ingestion_id)
    if not ingestion:
        raise InvalidStateError(f"Ingestion {ingestion_id} not found.")

    media_type = ingestion.get("media_type", "text")
    cross_check_status = "single_source"
    extraction_agreement = None

    # Voice -> text (Whisper ASR)
    if media_type == "voice" and not ingestion.get("raw_text"):
        try:
            asr = whisper_asr.transcribe(ingestion["file_path"])
            ingestion["raw_text"] = asr["text"]
            ingestion["asr"] = asr
        except Exception as exc:
            log.warning("ASR failed: %s", exc)
            ingestion["asr_error"] = str(exc)

    # Image/document -> text (OCR primary) + optional VLM cross-check
    if media_type in ("image", "document") and not ingestion.get("raw_text"):
        try:
            ocr = ocr_service.extract_text(ingestion["file_path"])
            ingestion["raw_text"] = ocr["text"]
            ingestion["ocr_text"] = ocr["text"]
        except Exception as exc:
            log.warning("OCR failed: %s", exc)
            ingestion["ocr_error"] = str(exc)

        if ingestion.get("raw_text"):
            ocr_fields = structurer.structure_text(ingestion["raw_text"])
            vlm_fields = vlm_verifier.verify(ingestion.get("file_path"))
            if vlm_fields:
                comparison = comparator.compare(ocr_fields, vlm_fields)
                ingestion["vlm_extraction"] = comparison["vlm_extraction"]
                ingestion["crosscheck"] = comparison
                cross_check_status = comparison["cross_check_status"]
                extraction_agreement = comparison["agreement_score"]

    fields = structurer.structure_text(ingestion.get("raw_text"))

    fields_present = sum(1 for value in fields.values() if value is not None)
    extraction_confidence = round(min(0.95, 0.35 + 0.10 * fields_present), 2)

    if media_type in ("image", "document") and ingestion.get("ocr_error"):
        extraction_confidence = round(max(0.1, extraction_confidence - 0.3), 2)

    language_hint = None
    if ingestion.get("asr"):
        language_hint = ingestion["asr"].get("language")
    elif ingestion.get("raw_text"):
        language_hint = "hinglish"

    result = ExtractionSchema(
        spatial_zone=fields["spatial_zone"],
        discipline=fields["discipline"],
        component=fields["component"],
        action=fields["action"],
        status=fields["status"],
        percent_complete=fields["percent_complete"],
        timestamp=ingestion.get("capture_timestamp") or ingestion.get("received_at"),
        raw_text=ingestion.get("raw_text"),
        language_hint=language_hint,
        extraction_confidence=extraction_confidence,
        extraction_agreement=extraction_agreement,
        cross_check_status=cross_check_status,
    )

    ingestion["extraction"] = result.model_dump()
    ingestion["status"] = "extracted"
    return result