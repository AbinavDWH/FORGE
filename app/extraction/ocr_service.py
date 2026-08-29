from functools import lru_cache

from app.core.logging import get_logger

log = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_engine():
    try:
        from rapidocr_onnxruntime import RapidOCR

        log.info("RapidOCR engine loaded.")
        return RapidOCR()
    except Exception as exc:
        log.warning("OCR unavailable: %s", exc)
        return None


def extract_text(image_path: str) -> dict:
    """
    PRIMARY image extraction: deterministic local OCR.
    OCR reads the text. The structurer understands the text.
    """
    engine = _load_engine()
    if engine is None:
        raise RuntimeError("OCR unavailable. Install rapidocr-onnxruntime.")

    result, _elapse = engine(image_path)

    lines = []
    if result:
        for item in result:
            lines.append(item[1])

    return {
        "text": "\n".join(lines),
        "engine": "rapidocr_onnxruntime",
    }