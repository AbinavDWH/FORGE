"""Confidence adjustment rules per FORGE module plan."""
from typing import Dict, Any, List, Tuple, Optional

def apply_adjustments(
    base_score: float,
    metadata: dict = None,
    cross_check_result: dict = None,
    synthetic_media_result: dict = None,
) -> Tuple[float, List[str]]:
    """
    Apply adjustments to the base confidence score based on various factors.
    """
    metadata = metadata or {}
    cross_check_result = cross_check_result or {}
    synthetic_media_result = synthetic_media_result or {}
    
    score = base_score
    explanations = []

    # Metadata adjustments
    if not metadata.get("gps_coords"):
        score -= 5.0
        explanations.append("Missing GPS (-5 points)")
    if metadata.get("exif_present") is not True:
        score -= 5.0
        explanations.append("Missing EXIF (-5 points)")

    expected = metadata.get("expected_sha256")
    original = metadata.get("original_sha256")
    if expected and original and expected != original:
        score -= 15.0
        explanations.append("Hash mismatch (-15 points)")

    if metadata.get("out_of_order_dependency"):
        score -= 10.0
        explanations.append("Out-of-order dependency detected (-10 points)")

    if metadata.get("evidence_present"):
        score += 3.0
        explanations.append("Photo evidence present (+3 points)")

    # Cross check adjustments
    cross_check_status = cross_check_result.get("cross_check_status")
    if cross_check_status == "agreed":
        score += 8.0
        explanations.append("OCR and VLM agree on all key fields (+8 points)")
    elif cross_check_status == "single_source":
        score -= 3.0
        explanations.append("VLM unavailable (-3 points)")
    
    mismatches = cross_check_result.get("mismatches", [])
    if mismatches:
        critical_fields = {"status", "percent_complete", "component"}
        has_critical = any(m in critical_fields for m in mismatches)
        has_non_critical = any(m not in critical_fields for m in mismatches)
        
        if has_critical:
            score = min(score, 60.0)
            explanations.append("Critical mismatch (status/percent_complete/component) capped at 60")
        elif len(mismatches) == 1 and has_non_critical:
            score = min(score, 84.0)
            explanations.append("Partial mismatch on 1 non-critical field, capped at 84 (force review)")

    # Synthetic media adjustments
    ai_risk = synthetic_media_result.get("ai_generation_risk")
    if ai_risk == "medium":
        score = min(score, 84.0)
        explanations.append("Medium ai_generation_risk capped below 85 (force review)")
    elif ai_risk == "high":
        score = min(score, 30.0)
        explanations.append("BLOCKED: suspected synthetic media")
        
    return score, explanations
