import re

from app.api.schemas import ExtractionSchema
from app.core.errors import InvalidStateError
from app.core.state import state


def extract(ingestion_id: str) -> ExtractionSchema:
    """
    Temporary deterministic extraction.

    Later:
    - Voice: Whisper ASR
    - Image/document: PaddleOCR / RapidOCR primary extraction
    - Image/document: VLM secondary verifier only
    - Text: structured LLM extraction with Pydantic constraints
    """
    ingestion = state.ingestions.get(ingestion_id)

    if not ingestion:
        raise InvalidStateError(f"Ingestion {ingestion_id} not found.")

    raw_text = (ingestion.get("raw_text") or "").strip()
    text = raw_text.lower()

    spatial_zone = None
    discipline = None
    component = None
    action = None
    status = None
    percent_complete = None

    zone_match = re.search(r"(?:zone|sector)\s*([a-z0-9]+)", text)
    if zone_match:
        spatial_zone = f"Zone {zone_match.group(1).upper()}"

    pier_match = re.search(r"pier\s*(\d+)", text)
    if pier_match:
        component = f"Pier {pier_match.group(1)}"
        discipline = "Civil"

    if "concrete" in text:
        action = "Concrete pouring"
        discipline = discipline or "Civil"
    elif "shuttering" in text:
        action = "Shuttering removal"
        discipline = discipline or "Civil"
    elif "rebar" in text:
        action = "Rebar inspection"
        discipline = discipline or "Civil"
    elif "hydro" in text:
        action = "Hydro testing"
        discipline = discipline or "Piping"
    elif "insulation" in text:
        action = "Insulation"
        discipline = discipline or "Piping"

    if any(word in text for word in ["completed", "done", "complete", "finished"]):
        status = "Completed"
        percent_complete = 100
    else:
        percent_match = re.search(r"(\d{1,3})\s*%", text)

        if percent_match:
            percent_complete = min(100, int(percent_match.group(1)))
            status = "Completed" if percent_complete == 100 else "In Progress"
        elif action:
            status = "In Progress"

    fields_present = sum(
        1
        for value in (
            spatial_zone,
            discipline,
            component,
            action,
            status,
            percent_complete,
        )
        if value is not None
    )

    extraction_confidence = round(min(0.95, 0.35 + 0.10 * fields_present), 2)

    # Placeholder cross-check behavior.
    # For image/document updates, later implement OCR vs VLM comparison.
    if ingestion.get("media_type") in ["image", "document"]:
        cross_check_status = "agreed"
        extraction_agreement = 0.90
    else:
        cross_check_status = "single_source"
        extraction_agreement = None

    result = ExtractionSchema(
        spatial_zone=spatial_zone,
        discipline=discipline,
        component=component,
        action=action,
        status=status,
        percent_complete=percent_complete,
        timestamp=ingestion.get("capture_timestamp") or ingestion.get("received_at"),
        raw_text=raw_text,
        language_hint="hinglish" if raw_text else None,
        extraction_confidence=extraction_confidence,
        extraction_agreement=extraction_agreement,
        cross_check_status=cross_check_status,
    )

    ingestion["extraction"] = result.model_dump()
    ingestion["status"] = "extracted"

    return result