from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from rapidfuzz import fuzz

from app.matcher.normalizer import apply_aliases, normalize_text
from app.matcher.fuzzy_scorer import score_fuzzy_match

DEFAULT_WEIGHTS = {
    "semantic": 0.55,
    "fuzzy": 0.30,
    "context": 0.15,
}


def _field_matches(update_value: Optional[str], task_value: Optional[str]) -> bool:
    """
    Zone/discipline pruning gate.

    We intentionally keep this conservative.
    If both values exist and do not appear compatible, the task is pruned.
    """
    update_norm = normalize_text(update_value)
    task_norm = normalize_text(task_value)

    # If either side is missing, do not prune on that field.
    if not update_norm or not task_norm:
        return True

    if update_norm == task_norm:
        return True

    if update_norm in task_norm or task_norm in update_norm:
        return True

    # Conservative fuzzy compatibility.
    # Avoids matching Zone B with Zone C just because both contain "zone".
    return fuzz.ratio(update_norm, task_norm) >= 88


def prune_tasks(
    update: Dict[str, Any],
    tasks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Stage 1: Rule-based pruning.

    Filter tasks by spatial zone and discipline before scoring.
    """
    candidates = []

    for task in tasks:
        if not _field_matches(update.get("spatial_zone"), task.get("zone")):
            continue

        if not _field_matches(update.get("discipline"), task.get("discipline")):
            continue

        candidates.append(task)

    return candidates


def default_context_score(
    update: Dict[str, Any],
    task: Dict[str, Any],
    fuzzy_details: Optional[Dict[str, Any]] = None,
) -> float:
    """
    Stage 3: Context ranking.

    Boost active tasks, strong component matches, and strong action matches.
    """
    score = 0.0
    fuzzy_details = fuzzy_details or {}

    if task.get("is_active"):
        score += 0.25

    status_norm = normalize_text(task.get("status"))
    if status_norm in {"active", "in progress", "in_progress", "ongoing"}:
        score += 0.25

    if fuzzy_details.get("matched_component"):
        score += 0.35

    if fuzzy_details.get("matched_action"):
        score += 0.25

    update_component = apply_aliases(update.get("component"))
    task_component = apply_aliases(task.get("component"))

    if update_component and task_component and update_component == task_component:
        score += 0.15

    return min(score, 1.0)


def build_match_reason(
    update: Dict[str, Any],
    task: Dict[str, Any],
    fuzzy_details: Dict[str, Any],
) -> str:
    """
    Build a human-readable match explanation.
    This is important for judge trust and manager review.
    """
    parts = []

    if update.get("spatial_zone"):
        parts.append(str(update["spatial_zone"]).strip())

    if update.get("discipline"):
        parts.append(str(update["discipline"]).strip())

    if fuzzy_details.get("matched_component"):
        parts.append(f"component ≈ {fuzzy_details['matched_component']}")

    if fuzzy_details.get("matched_action"):
        parts.append(f"action ≈ {fuzzy_details['matched_action']}")

    if not parts:
        parts = [
            task.get("task_name", "task"),
            "hybrid fuzzy match",
        ]

    return " + ".join(parts)


def _call_semantic_scorer(
    semantic_scorer: Optional[Callable],
    update: Dict[str, Any],
    task: Dict[str, Any],
    fallback_score: float,
) -> float:
    """
    Call your existing embedding/ChromaDB scorer if available.

    If no semantic scorer is supplied, fall back to fuzzy score.
    This keeps the module testable without ChromaDB.
    """
    if semantic_scorer is None:
        return fallback_score

    try:
        return float(semantic_scorer(update, task))
    except TypeError:
        return float(semantic_scorer(update))


def _call_context_scorer(
    context_scorer: Optional[Callable],
    update: Dict[str, Any],
    task: Dict[str, Any],
    fuzzy_details: Dict[str, Any],
) -> float:
    """
    Call custom context scorer if available.
    """
    if context_scorer is None:
        return default_context_score(update, task, fuzzy_details)

    try:
        return float(context_scorer(update, task, fuzzy_details))
    except TypeError:
        return float(context_scorer(update, task))


def rank_tasks(
    update: Dict[str, Any],
    tasks: List[Dict[str, Any]],
    semantic_scorer: Optional[Callable] = None,
    context_scorer: Optional[Callable] = None,
    weights: Optional[Dict[str, float]] = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Stage 2 + Stage 3:
        1. Prune by zone/discipline.
        2. Score with semantic + RapidFuzz + context.
        3. Return ranked matches with explanation.
    """
    weights = {**DEFAULT_WEIGHTS, **(weights or {})}
    candidates = prune_tasks(update, tasks)

    ranked = []

    for task in candidates:
        fuzzy_score, fuzzy_details = score_fuzzy_match(update, task)

        semantic_score = _call_semantic_scorer(
            semantic_scorer,
            update,
            task,
            fallback_score=fuzzy_score,
        )

        context_score = _call_context_scorer(
            context_scorer,
            update,
            task,
            fuzzy_details,
        )

        final_score = (
            weights["semantic"] * semantic_score
            + weights["fuzzy"] * fuzzy_score
            + weights["context"] * context_score
        )

        ranked.append(
            {
                "task_id": task.get("task_id") or task.get("id"),
                "task_name": task.get("task_name"),
                "wbs_code": task.get("wbs_code"),
                "match_score": round(final_score, 4),
                "semantic_score": round(semantic_score, 4),
                "fuzzy_score": round(fuzzy_score, 4),
                "context_score": round(context_score, 4),
                "match_reason": build_match_reason(update, task, fuzzy_details),
                "fuzzy_details": fuzzy_details,
            }
        )

    ranked.sort(key=lambda item: item["match_score"], reverse=True)

    if limit is not None:
        ranked = ranked[:limit]

    return ranked


def match_update(
    update: Dict[str, Any],
    tasks: List[Dict[str, Any]],
    semantic_scorer: Optional[Callable] = None,
    context_scorer: Optional[Callable] = None,
    weights: Optional[Dict[str, float]] = None,
    limit: int = 5,
) -> Dict[str, Any]:
    """
    Public matcher API.

    Returns a matcher result aligned with the FORGE module plan:
    - matched_task_id
    - task_name
    - wbs_code
    - match_score
    - match_reason
    - alternative_matches
    """
    ranked = rank_tasks(
        update=update,
        tasks=tasks,
        semantic_scorer=semantic_scorer,
        context_scorer=context_scorer,
        weights=weights,
        limit=limit,
    )

    if not ranked:
        return {
            "ingestion_id": update.get("ingestion_id"),
            "matched_task_id": None,
            "task_name": None,
            "wbs_code": None,
            "match_score": 0.0,
            "match_reason": "No candidate tasks after zone/discipline pruning",
            "alternative_matches": [],
        }

    top = ranked[0]

    return {
        "ingestion_id": update.get("ingestion_id"),
        "matched_task_id": top.get("task_id"),
        "task_name": top.get("task_name"),
        "wbs_code": top.get("wbs_code"),
        "match_score": top.get("match_score"),
        "match_reason": top.get("match_reason"),
        "semantic_score": top.get("semantic_score"),
        "fuzzy_score": top.get("fuzzy_score"),
        "context_score": top.get("context_score"),
        "alternative_matches": [
            {
                "task_id": item.get("task_id"),
                "task_name": item.get("task_name"),
                "match_score": item.get("match_score"),
            }
            for item in ranked[1:]
        ],
    }