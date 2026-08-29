from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from rapidfuzz import fuzz

from app.matcher.normalizer import apply_aliases, normalize_text, to_list

FIELD_WEIGHTS = {
    "component": 0.42,
    "action": 0.34,
    "status": 0.10,
    "raw": 0.14,
}


def _combined_ratio(candidate: str, target: str) -> float:
    """
    Combine multiple RapidFuzz ratios.

    token_set_ratio:
        Good for reordered / partial keyword sets.
    partial_ratio:
        Good for substring-style OCR/ASR errors.
    WRatio:
        General-purpose weighted fallback.
    """
    token_set = fuzz.token_set_ratio(candidate, target)
    partial = fuzz.partial_ratio(candidate, target)
    wratio = fuzz.WRatio(candidate, target)

    return (0.45 * token_set + 0.30 * partial + 0.25 * wratio) / 100.0


def _best_target(
    candidate: Optional[str],
    targets: List[str],
) -> Tuple[float, Optional[str]]:
    """
    Compare one extracted field against multiple possible task values.
    """
    candidate_norm = apply_aliases(candidate)

    if not candidate_norm:
        return 0.0, None

    best_score = 0.0
    best_target = None

    for target in targets:
        target_norm = apply_aliases(target)

        if not target_norm:
            continue

        score = _combined_ratio(candidate_norm, target_norm)

        if score > best_score:
            best_score = score
            best_target = target_norm

    return round(best_score, 4), best_target


def _task_targets(task: Dict[str, Any], field: str) -> List[str]:
    """
    Build a list of possible target strings from the task.
    """
    if field == "component":
        return (
            to_list(task.get("component_aliases"))
            or to_list(task.get("component"))
            or to_list(task.get("task_name"))
        )

    if field == "action":
        return (
            to_list(task.get("activity_keywords"))
            or to_list(task.get("task_name"))
        )

    if field == "status":
        return (
            to_list(task.get("status_keywords"))
            or to_list(task.get("status"))
        )

    if field == "raw":
        return (
            to_list(task.get("task_name"))
            + to_list(task.get("wbs_code"))
            + to_list(task.get("activity_keywords"))
        )

    return []


def score_fuzzy_match(
    update: Dict[str, Any],
    task: Dict[str, Any],
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate a RapidFuzz-based lexical match score between a field update
    and a schedule task.

    This does not write to the schedule.
    It only produces a matcher signal.
    """
    update = update or {}
    task = task or {}

    scores = {}
    signals = []

    # Component matching.
    # If component is missing, fall back to raw text, but with reduced trust.
    component_value = update.get("component") or update.get("raw_text")
    component_score, component_target = _best_target(
        component_value,
        _task_targets(task, "component"),
    )
    scores["component"] = component_score

    # Action matching.
    action_value = update.get("action") or update.get("raw_text")
    action_score, action_target = _best_target(
        action_value,
        _task_targets(task, "action"),
    )
    scores["action"] = action_score

    # Status matching.
    status_value = update.get("status")
    status_score, status_target = _best_target(
        status_value,
        _task_targets(task, "status"),
    )
    scores["status"] = status_score

    # Raw text matching as a weaker supporting signal.
    raw_score, raw_target = _best_target(
        update.get("raw_text"),
        _task_targets(task, "raw"),
    )
    scores["raw"] = raw_score

    if component_score >= 0.75 and component_target:
        source = normalize_text(update.get("component")) or "raw text"
        signals.append(f"{source} ≈ {component_target}")

    if action_score >= 0.70 and action_target:
        source = normalize_text(update.get("action")) or "raw text"
        signals.append(f"{source} ≈ {action_target}")

    final_score = sum(
        weight * scores.get(field, 0.0)
        for field, weight in FIELD_WEIGHTS.items()
    )

    # If neither component nor action is convincing,
    # prevent raw-text similarity from inflating the match.
    if scores["component"] < 0.35 and scores["action"] < 0.35:
        final_score *= 0.75

    details = {
        "fuzzy_score": round(final_score, 4),
        "field_scores": {
            key: round(value, 4)
            for key, value in scores.items()
        },
        "matched_component": component_target if component_score >= 0.75 else None,
        "matched_action": action_target if action_score >= 0.70 else None,
        "signals": signals,
    }

    return round(final_score, 4), details