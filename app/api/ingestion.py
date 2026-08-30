"""MOD-01: Field Ingestion Gateway — Multi-modal pipeline with VLM as Primary Visual & OCR Extractor."""
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

from app.api.extraction import extract_fields, ExtractionRequest
from app.extraction.structurer import structure_text, detect_language
from app.extraction import whisper_asr, ocr_service, vlm_verifier
from app.crosscheck import comparator
from app.api.review import add_to_review_tray
from app.schedule.xml_parser import parse_schedule
from app.schedule.cpm_guard import check_cpm_dependencies
from app.schedule.actuals_writer import write_actuals_to_xml
from app.audit.hash_chain import append_audit_record
from app.audit.synthetic_media_gate import screen_image

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])
STORAGE_RAW = Path("storage/raw")
STORAGE_RAW.mkdir(parents=True, exist_ok=True)


class IngestionResponse(BaseModel):
    ingestion_id: str
    source: str
    media_type: str
    status: str


def _calculate_confidence(
    match_score: float,
    extraction_confidence: float,
    metadata: dict = None,
    cross_check_result: dict = None,
    synthetic_media_result: dict = None,
) -> dict:
    """Calculate confidence using the confidence module."""
    try:
        from app.confidence.scorer import calculate_confidence
        return calculate_confidence(
            match_score=match_score,
            extraction_confidence=extraction_confidence,
            metadata=metadata,
            cross_check_result=cross_check_result,
            synthetic_media_result=synthetic_media_result,
        )
    except ImportError:
        base = int(0.6 * match_score * 100 + 0.4 * extraction_confidence * 100)
        base = max(0, min(100, base))
        if base >= 85:
            routing = "auto_commit"
        elif base >= 50:
            routing = "review"
        else:
            routing = "manual"
        return {"score": base, "routing": routing, "explanation": []}


def run_pipeline(
    ingestion_id: str,
    raw_text: str,
    media_type: str = "text",
    file_path: Optional[str] = None,
    gps_coords: Optional[str] = None,
    exif_present: Optional[bool] = None,
):
    """Background task: Whisper / VLM Primary OCR → Crosscheck → Matcher → Confidence → Routing."""
    try:
        processed_text = raw_text or ""
        language_hint = "english"
        cross_check_status = "single_source"
        extraction_agreement = 1.0
        synthetic_result = None
        ai_generation_risk = "low"
        ocr_struct = {}
        vlm_struct = {}
        field_agreement = {}

        # 1. Multi-Modal Audio Processing (Whisper ASR)
        if media_type == "voice" and file_path and Path(file_path).exists():
            try:
                asr_result = whisper_asr.transcribe(str(file_path))
                if asr_result.get("text"):
                    processed_text = asr_result["text"]
                    language_hint = asr_result.get("language", "english")
            except Exception as e:
                print(f"ASR transcription error: {e}")

        # 2. Image Processing (VLM as Primary Visual & OCR Extractor)
        elif media_type in ("image", "document") and file_path and Path(file_path).exists():
            try:
                raw_bytes = Path(file_path).read_bytes()
                # Synthetic Media Screening
                synthetic_result = screen_image(raw_bytes)
                ai_generation_risk = synthetic_result.get("ai_generation_risk", "low")
                exif_present = synthetic_result.get("exif_present", exif_present)

                # Step 2A: Primary Vision-Language Model Inference
                try:
                    vlm_out = vlm_verifier.extract_from_image(str(file_path))
                    if vlm_out:
                        vlm_struct = vlm_out
                        vlm_text = vlm_out.get("raw_text")
                        if vlm_text and (not processed_text or processed_text.startswith("[")):
                            processed_text = vlm_text
                except Exception as e:
                    print(f"VLM primary extraction error: {e}")

                # Step 2B: Secondary Local OCR (RapidOCR)
                ocr_out = None
                try:
                    ocr_res = ocr_service.extract_text(str(file_path))
                    if ocr_res and ocr_res.get("text"):
                        ocr_out = ocr_res["text"]
                        ocr_struct = structure_text(ocr_out)
                        if not processed_text or processed_text.startswith("["):
                            processed_text = ocr_out
                except Exception as e:
                    print(f"RapidOCR secondary verification fallback: {e}")

                # Step 2C: Cross-Check Comparison
                if vlm_struct and ocr_struct:
                    cmp_res = comparator.compare(ocr_struct, vlm_struct)
                    cross_check_status = cmp_res.get("cross_check_status", "agreed")
                    extraction_agreement = cmp_res.get("agreement_score", 1.0)
                    field_agreement = cmp_res.get("field_agreement", {})
                elif vlm_struct:
                    cross_check_status = "vlm_primary"
                elif ocr_struct:
                    cross_check_status = "ocr_primary"
            except Exception as e:
                print(f"Image processing pipeline error: {e}")

        # 3. Extraction & Structuring
        if language_hint in ("english", "English"):
            language_hint = detect_language(processed_text)

        structured = structure_text(processed_text)
        
        # When VLM is primary, use VLM's structured attributes directly
        if vlm_struct:
            for k in ("spatial_zone", "discipline", "component", "action", "status", "percent_complete"):
                val = vlm_struct.get(k)
                if val is not None:
                    structured[k] = val

        filled = sum(1 for v in structured.values() if v is not None)
        total = len(structured)
        ext_confidence = round(filled / total, 2) if total > 0 else 0.0

        # 4. Schedule Task Matching (Two-Stage Pruning + RapidFuzz Hybrid Search)
        live_schedule = parse_schedule()
        from app.matcher.hybrid_search import match_update
        update_payload = {
            "ingestion_id": ingestion_id,
            "spatial_zone": structured.get("spatial_zone"),
            "discipline": structured.get("discipline"),
            "component": structured.get("component"),
            "action": structured.get("action"),
            "status": structured.get("status"),
            "percent_complete": structured.get("percent_complete"),
            "raw_text": processed_text,
        }
        match_res = match_update(update_payload, live_schedule)

        # 5. Confidence Scoring & Routing
        metadata = {
            "gps_coords": gps_coords,
            "exif_present": exif_present,
            "evidence_present": file_path is not None,
        }
        cross_check_payload = {
            "cross_check_status": cross_check_status,
            "extraction_agreement": extraction_agreement,
        }
        confidence = _calculate_confidence(
            match_score=match_res.get("match_score", 0),
            extraction_confidence=ext_confidence,
            metadata=metadata,
            cross_check_result=cross_check_payload,
            synthetic_media_result=synthetic_result,
        )

        evidence_url = f"/static/{Path(file_path).name}" if file_path else None

        # 6. Build Review Item
        review_item = {
            "ingestion_id": ingestion_id,
            "status": f"pending_{confidence['routing']}",
            "media_type": media_type,
            "ai_generation_risk": ai_generation_risk,
            "evidence_url": evidence_url,
            "cross_check_status": cross_check_status,
            "cross_check": {
                "cross_check_status": cross_check_status,
                "agreement_score": extraction_agreement,
                "ocr_extraction": ocr_struct,
                "vlm_extraction": vlm_struct,
                "field_agreement": field_agreement,
            },
            "extraction": {
                "spatial_zone": structured.get("spatial_zone"),
                "discipline": structured.get("discipline"),
                "component": structured.get("component"),
                "action": structured.get("action"),
                "status": structured.get("status"),
                "percent_complete": structured.get("percent_complete"),
                "raw_text": processed_text,
                "language_hint": language_hint,
                "extraction_confidence": ext_confidence,
                "cross_check_status": cross_check_status,
            },
            "match": {
                "matched_task_id": match_res.get("matched_task_id"),
                "task_name": match_res.get("task_name"),
                "wbs_code": match_res.get("wbs_code"),
                "match_score": match_res.get("match_score", 0),
                "match_reason": match_res.get("match_reason", ""),
                "alternative_matches": match_res.get("alternative_matches", []),
            },
            "confidence": confidence,
            "received_at": datetime.utcnow().isoformat() + "Z",
        }

        # 7. Route based on confidence tier
        if confidence["routing"] == "auto_commit":
            _auto_commit(review_item, live_schedule)
        else:
            add_to_review_tray(review_item)

    except Exception as e:
        print(f"Pipeline error for {ingestion_id}: {e}")
        import traceback
        traceback.print_exc()


def _auto_commit(review_item: dict, schedule_data: list):
    """Auto-commit high-confidence updates directly to schedule."""
    task_id = review_item["match"]["matched_task_id"]
    pct = review_item["extraction"].get("percent_complete", 0)

    if not task_id or pct is None:
        add_to_review_tray(review_item)
        return

    # CPM guard check
    cpm_result = check_cpm_dependencies(
        task_id=task_id,
        proposed_percent=pct,
        schedule_data=schedule_data,
    )

    if not cpm_result["valid"]:
        review_item["confidence"]["explanation"].append(
            f"Auto-commit blocked: {cpm_result['reason']}"
        )
        review_item["status"] = "pending_review"
        add_to_review_tray(review_item)
        return

    # Write actuals to schedule XML
    now = datetime.utcnow().isoformat() + "Z"
    write_actuals_to_xml(
        task_id=task_id,
        percent_complete=pct,
        actual_start=now,
        actual_finish=now if pct == 100 else None,
    )

    # Immutable audit record
    append_audit_record(
        ingestion_id=review_item["ingestion_id"],
        wbs_activity_id=task_id,
        action_performed=f"Auto-committed to {pct}% (confidence {review_item['confidence']['score']}%)",
        confidence_score=review_item["confidence"]["score"],
        approved_by="system_auto",
        cross_check_status=review_item.get("cross_check_status", "single_source"),
        ai_generation_risk=review_item.get("ai_generation_risk", "low"),
    )

    review_item["status"] = "auto_committed"
    add_to_review_tray(review_item)


@router.post("/upload", response_model=IngestionResponse)
async def upload_field_update(
    background_tasks: BackgroundTasks,
    source: str = Form("web_upload"),
    media_type: str = Form("text"),
    raw_text: Optional[str] = Form(None),
    gps_coords: Optional[str] = Form(None),
    exif_present: Optional[bool] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    ingestion_id = f"ING-{uuid.uuid4().hex[:8].upper()}"
    file_path = None

    if file:
        file_path = str(STORAGE_RAW / f"{ingestion_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    text_to_process = raw_text or f"[{media_type} file uploaded]"

    background_tasks.add_task(
        run_pipeline,
        ingestion_id,
        text_to_process,
        media_type,
        file_path,
        gps_coords,
        exif_present,
    )

    return {
        "ingestion_id": ingestion_id,
        "source": source,
        "media_type": media_type,
        "status": "received_and_processing",
    }