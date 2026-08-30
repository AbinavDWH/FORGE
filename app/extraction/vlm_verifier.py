"""MOD-02: Vision-Language Model (VLM) Primary Visual Extractor & OCR.

Uses real Vision-Language Models (Qwen3-VL 4B / Ollama / Gemini Vision) directly on site images.
Zero mock data: live inference with temperature=0.0.
"""
import base64
import json
import re
import os
from pathlib import Path
from typing import Optional, Dict, Any

import httpx

from app.core.logging import get_logger
from app.core.settings import settings

log = get_logger(__name__)

VLM_EXTRACTION_PROMPT = (
    "You are an expert infrastructure construction engineer and visual inspector for Oil India Limited / NRL Golaghat.\n"
    "Analyze this construction site photo or site diary image thoroughly.\n"
    "Extract all visible text (OCR) and identify structured engineering attributes.\n"
    "Return ONLY valid JSON with these exact fields:\n"
    "{\n"
    '  "raw_text": "all verbatim text, numbers, and handwritten notes visible in the image",\n'
    '  "spatial_zone": "Zone A | Zone B | Tank Farm | Pipeline Corridor | Pump House | or null",\n'
    '  "discipline": "Civil | Structural | Piping | Electrical | Instrumentation | Insulation | or null",\n'
    '  "component": "detected component e.g. Pier 14, Tank Shell, Line 1 Spool | or null",\n'
    '  "action": "detected construction activity e.g. Concrete pouring, Hydro testing | or null",\n'
    '  "status": "Completed | In Progress | Not Started | or null",\n'
    '  "percent_complete": integer 0-100 or null,\n'
    '  "visual_description": "brief physical description of the site evidence observed"\n'
    "}\n"
    "Rules: Use null for any field that cannot be observed with certainty. Do not guess."
)


def _call_ollama_native(b64_image: str) -> Optional[Dict[str, Any]]:
    """Calls Ollama native /api/chat with base64 image."""
    try:
        ollama_host = settings.vlm_base_url.replace("/v1", "").rstrip("/")
        ollama_url = f"{ollama_host}/api/chat"
        resp = httpx.post(
            ollama_url,
            json={
                "model": settings.vlm_model,
                "messages": [
                    {
                        "role": "user",
                        "content": VLM_EXTRACTION_PROMPT,
                        "images": [b64_image],
                    }
                ],
                "stream": False,
                "options": {
                    "temperature": settings.vlm_temperature,
                },
            },
            timeout=120,
        )
        if resp.status_code == 200:
            content = resp.json().get("message", {}).get("content", "")
            match = re.search(r"\{.*\}", content, re.S)
            if match:
                parsed = json.loads(match.group(0))
                log.info("VLM extraction succeeded via Ollama native /api/chat (%s)", settings.vlm_model)
                return parsed
    except Exception as exc:
        log.debug("Ollama native /api/chat error: %s", exc)
    return None


def _call_openai_compatible(b64_image: str) -> Optional[Dict[str, Any]]:
    """Calls standard /chat/completions OpenAI endpoint."""
    endpoints = [
        f"{settings.vlm_base_url.rstrip('/')}/chat/completions",
        f"{settings.vlm_base_url.rstrip('/')}/v1/chat/completions",
    ]
    for url in endpoints:
        try:
            resp = httpx.post(
                url,
                headers={"Authorization": f"Bearer {settings.vlm_api_key}"},
                json={
                    "model": settings.vlm_model,
                    "temperature": settings.vlm_temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": VLM_EXTRACTION_PROMPT},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                                },
                            ],
                        }
                    ],
                },
                timeout=120,
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                match = re.search(r"\{.*\}", content, re.S)
                if match:
                    parsed = json.loads(match.group(0))
                    log.info("VLM extraction succeeded via %s", url)
                    return parsed
        except Exception as exc:
            log.debug("OpenAI-compatible request to %s failed: %s", url, exc)
    return None


def _call_gemini_vision(b64_image: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Calls Google Gemini Vision API if configured."""
    try:
        model_name = "gemini-2.0-flash" if "gemini" in settings.vlm_model else settings.vlm_model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        resp = httpx.post(
            url,
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": VLM_EXTRACTION_PROMPT},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": b64_image,
                                }
                            },
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": settings.vlm_temperature,
                    "responseMimeType": "application/json",
                },
            },
            timeout=30,
        )
        if resp.status_code == 200:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            match = re.search(r"\{.*\}", text, re.S)
            if match:
                return json.loads(match.group(0))
    except Exception as exc:
        log.warning("Gemini Vision call failed: %s", exc)
    return None


def extract_from_image(image_path: str) -> Optional[Dict[str, Any]]:
    """
    PRIMARY image analysis: sends the raw image to the Vision-Language Model.
    Extracts visible text (OCR) and structured project fields with zero mock data.
    """
    if not image_path or not Path(image_path).exists():
        return None

    try:
        raw_bytes = Path(image_path).read_bytes()
        b64_image = base64.b64encode(raw_bytes).decode("utf-8")
    except Exception as e:
        log.error("Could not read image file %s: %e", image_path, e)
        return None

    # 1. Try Gemini Vision if cloud API key is configured
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        result = _call_gemini_vision(b64_image, gemini_key)
        if result:
            return result

    # 2. Call Ollama native API (e.g. qwen3-vl:4b)
    result = _call_ollama_native(b64_image)
    if result:
        return result

    # 3. Call standard OpenAI-compatible vision endpoint
    result = _call_openai_compatible(b64_image)
    if result:
        return result

    log.warning(
        "VLM inference could not be completed on %s. Ensure Ollama with '%s' is running at %s.",
        image_path,
        settings.vlm_model,
        settings.vlm_base_url,
    )
    return None


# Backward compatibility alias
verify = extract_from_image