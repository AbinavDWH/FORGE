from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional

_NON_WORD = re.compile(r"[^\w\s]", re.UNICODE)
_WHITESPACE = re.compile(r"\s+", re.UNICODE)

ALIAS_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "sample_schedule"
    / "masters"
    / "aliases.json"
)

DEFAULT_ALIASES: Dict[str, Dict[str, str]] = {
    "components": {
        "peer 14": "pier 14",
        "pier14": "pier 14",
        "pir 14": "pier 14",
        "pier 14": "pier 14",
    },
    "actions": {
        "concret pour": "concrete pouring",
        "concrete pour": "concrete pouring",
        "pour done": "pouring completed",
        "pour completed": "pouring completed",
        "shuttering removed": "shuttering removal",
        "shuttering remover": "shuttering removal",
        "shuttering removal": "shuttering removal",
    },
}


def normalize_text(value: Optional[str]) -> str:
    """
    Lowercase and clean text for deterministic comparison.

    Example:
        "Sector B, Pier 14!" -> "sector b pier 14"
    """
    if not value:
        return ""

    text = str(value).lower().strip()
    text = _NON_WORD.sub(" ", text)
    text = _WHITESPACE.sub(" ", text).strip()
    return text


@lru_cache(maxsize=1)
def load_alias_map() -> Dict[str, Dict[str, str]]:
    """
    Load alias mapping from JSON. If unavailable, fall back to defaults.
    """
    try:
        payload = json.loads(ALIAS_PATH.read_text(encoding="utf-8"))
        return {
            "components": payload.get("components", {}),
            "actions": payload.get("actions", {}),
        }
    except Exception:
        return DEFAULT_ALIASES


def apply_aliases(
    value: Optional[str],
    groups: Iterable[str] = ("components", "actions"),
) -> str:
    """
    Normalize known site-language aliases.

    Example:
        "Peer 14 concret pour" -> "pier 14 concrete pouring"
    """
    text = normalize_text(value)
    if not text:
        return ""

    alias_map = load_alias_map()
    pairs = []

    for group in groups:
        for source, target in alias_map.get(group, {}).items():
            source_norm = normalize_text(source)
            target_norm = normalize_text(target)

            if source_norm and target_norm:
                pairs.append((source_norm, target_norm))

    # Replace longer aliases first to avoid partial replacement issues.
    pairs.sort(key=lambda item: len(item[0]), reverse=True)

    for source, target in pairs:
        if source in text:
            text = text.replace(source, target)

    return text


def to_list(value) -> List[str]:
    """
    Convert arbitrary task/update values into a clean string list.
    """
    if value is None:
        return []

    if isinstance(value, str):
        return [value]

    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if item]

    return [str(value)]