"""MOD-01 & MOD-08: Telephony & Messaging Webhook Ingestion (Twilio / Exotel / IVR)."""
from fastapi import APIRouter, Form, BackgroundTasks, Response
from typing import Optional
from pathlib import Path
import httpx
import uuid

from app.api.ingestion import upload_field_update, run_pipeline

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
STORAGE_RAW = Path("storage/raw")
STORAGE_RAW.mkdir(parents=True, exist_ok=True)


@router.post("/twilio/messaging")
@router.post("/twilio")
async def twilio_messaging_webhook(
    background_tasks: BackgroundTasks,
    From: str = Form(...),
    Body: str = Form(""),
    NumMedia: str = Form("0"),
    MediaUrl0: Optional[str] = Form(None),
):
    """
    Receives Twilio WhatsApp/SMS webhooks and maps them to the FORGE ingestion pipeline.
    """
    media_type = "text" if int(NumMedia) == 0 else "image"
    source = "whatsapp" if "whatsapp" in From.lower() else "sms"

    return await upload_field_update(
        background_tasks=background_tasks,
        source=source,
        media_type=media_type,
        raw_text=Body,
        file=None,
    )


@router.post("/ivr/twiml", response_class=Response)
@router.get("/ivr/twiml", response_class=Response)
def ivr_voice_twiml():
    """
    Returns TwiML instructions for incoming voice phone calls from zero-internet site zones.
    """
    twiml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Response>\n'
        '    <Say voice="Polly.Aditi" language="en-IN">Welcome to FORGE Site Reporting for Oil India Limited. '
        'Please speak your zone, component, and completed work after the tone.</Say>\n'
        '    <Record maxLength="60" action="/api/webhooks/ivr/recording" method="POST" playBeep="true" />\n'
        '    <Say>Thank you. Your update has been queued for reconciliation.</Say>\n'
        '</Response>'
    )
    return Response(content=twiml, media_type="application/xml")


@router.post("/ivr/recording")
async def ivr_recording_webhook(
    background_tasks: BackgroundTasks,
    RecordingUrl: Optional[str] = Form(None),
    From: Optional[str] = Form("Unknown Supervisor"),
    SpeechResult: Optional[str] = Form(None),
):
    """
    Receives recorded IVR audio from telephony provider, downloads audio, and triggers Whisper extraction.
    """
    ingestion_id = f"ING-{uuid.uuid4().hex[:8].upper()}"
    file_path = None
    raw_text = SpeechResult

    # Download call audio if URL provided
    if RecordingUrl:
        file_path = str(STORAGE_RAW / f"{ingestion_id}_ivr_call.wav")
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{RecordingUrl}.wav", timeout=30)
                if resp.status_code == 200:
                    Path(file_path).write_bytes(resp.content)
        except Exception as e:
            print(f"Failed to download IVR audio from {RecordingUrl}: {e}")

    background_tasks.add_task(
        run_pipeline,
        ingestion_id=ingestion_id,
        raw_text=raw_text or "[IVR Phone Call Update]",
        media_type="voice",
        file_path=file_path,
        gps_coords=None,  # Cellular IVR doesn't supply high-precision GPS
        exif_present=False,
    )

    return {
        "ingestion_id": ingestion_id,
        "source": "ivr",
        "media_type": "voice",
        "status": "recording_queued_for_whisper",
    }


@router.post("/ivr/simulate")
async def simulate_ivr_call(
    background_tasks: BackgroundTasks,
    spoken_text: str = Form("Sector B Pier 14 concrete pouring completed"),
    caller_phone: str = Form("+919876543210"),
):
    """
    Demo utility endpoint to simulate an IVR toll-free call from a remote connectivity dead zone.
    """
    ingestion_id = f"ING-{uuid.uuid4().hex[:8].upper()}"

    background_tasks.add_task(
        run_pipeline,
        ingestion_id=ingestion_id,
        raw_text=spoken_text,
        media_type="voice",
        file_path=None,
        gps_coords=None,
        exif_present=False,
    )

    return {
        "ingestion_id": ingestion_id,
        "source": "ivr",
        "media_type": "voice",
        "caller": caller_phone,
        "spoken_text": spoken_text,
        "status": "simulated_ivr_call_processing",
    }