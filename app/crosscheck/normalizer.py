import re

from rapidfuzz import fuzz

SYNONYMS = {
    "concrete pouring": "concrete pour",
    "completed": "complete",
    "done": "complete",
    "finished": "complete",
}


def normalize_value(value):
    if value is None:
        return None
    v = re.sub(r"[^a-z0-9 ]", " ", str(value).lower())
    v = re.sub(r"\s+", " ", v).strip()
    return SYNONYMS.get(v, v)


def values_match(a, b, threshold=85) -> bool:
    a = normalize_value(a)
    b = normalize_value(b)
    if a is None or b is None:
        return a is b
    if a == b:
        return True
    return fuzz.ratio(a, b) >= threshold