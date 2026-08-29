import base64
import json
import re

import httpx

from app.core.logging import get_logger
from app.core.settings import settings

log = get_logger(__name__)

PROMPT = (
    "You are a construction site photo verifier. Extract structured fields "
    "from this image. Return ONLY JSON with keys: spatial_zone, discipline, "
    "component, action, status, percent_complete. Use null for unknown "
    "fields. Do not invent values."
)


def verify(image_path: str):
    """
    SECONDARY verifier only. Its output never overwrites OCR.
    Returns None when VLM is disabled/unavailable -> single_source mode.
    """
    if not settings.vlm_enabled or not image_path:
        return None

    try:
        with open(image_path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode()

        resp = httpx.post(
            f"{settings.vlm_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.vlm_api_key}"},
            json={
                "model": settings.vlm_model,
                "temperature": 0,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{b64}"
                                },
                            },
                        ],
                    }
                ],
            },
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        match = re.search(r"\{.*\}", content, re.S)
        return json.loads(match.group(0)) if match else None
    except Exception as exc:
        log.warning("VLM verifier unavailable: %s", exc)
        return None