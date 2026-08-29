from functools import lru_cache

from app.core.logging import get_logger
from app.core.settings import settings

log = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_model():
    try:
        from faster_whisper import WhisperModel

        model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
        log.info("Whisper model '%s' loaded.", settings.whisper_model)
        return model
    except Exception as exc:
        log.warning("Whisper unavailable: %s", exc)
        return None


def transcribe(file_path: str) -> dict:
    model = _load_model()
    if model is None:
        raise RuntimeError(
            "Whisper ASR unavailable. Install faster-whisper or use text input."
        )

    segments, info = model.transcribe(file_path)
    text = " ".join(segment.text for segment in segments).strip()

    return {
        "text": text,
        "language": info.language,
        "language_probability": round(info.language_probability, 2),
    }