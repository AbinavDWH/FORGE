"""MOD-02: Multi-Lingual Whisper ASR Service.

Supports automatic speech recognition across Indian languages:
Hindi (hi), Assamese (as), Bengali (bn), Marathi (mr), Tamil (ta), Telugu (te), and English (en).
"""
from functools import lru_cache
from typing import Dict, Any

from app.core.logging import get_logger
from app.core.settings import settings

log = get_logger(__name__)

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi / Hinglish",
    "as": "Assamese",
    "bn": "Bengali",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "gu": "Gujarati",
    "ur": "Urdu",
    "pa": "Punjabi",
}


@lru_cache(maxsize=1)
def _load_model():
    try:
        from faster_whisper import WhisperModel

        model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
        log.info("Whisper ASR model '%s' loaded for multi-lingual speech recognition.", settings.whisper_model)
        return model
    except Exception as exc:
        log.warning("Whisper unavailable: %s", exc)
        return None


def transcribe(file_path: str) -> Dict[str, Any]:
    """Transcribes audio file and returns text and detected language."""
    model = _load_model()
    if model is None:
        raise RuntimeError(
            "Whisper ASR unavailable. Install faster-whisper or use text input."
        )

    segments, info = model.transcribe(file_path)
    text = " ".join(segment.text for segment in segments).strip()

    lang_code = info.language or "en"
    lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())

    return {
        "text": text,
        "language": lang_name,
        "language_code": lang_code,
        "language_probability": round(info.language_probability, 2),
    }