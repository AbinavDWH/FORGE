import re
from typing import Set, Tuple

from app.api.schemas import ExtractionSchema, MatchCandidate, MatchResult
from app.core.errors import InvalidStateError
from app.core.state import state


def _tokens(value: str) -> Set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))


def _score_task(task: dict, extraction: ExtractionSchema) -> Tuple[float, str]:
    score = 0.0
    reasons = []

    if (
        extraction.spatial_zone
        and task.get("zone")
        and extraction.spatial_zone.lower() == task["zone"].lower()
    ):
        score += 0.20
        reasons.append("zone match")

    if (
        extraction.discipline
        and task.get("discipline")
        and extraction.discipline.lower() == task["discipline"].lower()
    ):
        score += 0.20
        reasons.append("discipline match")

    if (
        extraction.component
        and task.get("component")
        and extraction.component.lower() in task["component"].lower()
    ):
        score += 0.35
        reasons.append("component match")

    action_tokens = _tokens(extraction.action or "")
    name_tokens = _tokens(task.get("name", ""))
    overlap = action_tokens & name_tokens

    if overlap:
        score += min(0.20, 0.08 * len(overlap))
        reasons.append("activity term match")

    if task.get("percent_complete", 0) < 100:
        score += 0.05
        reasons.append("task active")

    score = min(1.0, score)

    reason_text = ", ".join(reasons) if reasons else "weak contextual match"

    return round(score, 3), reason_text


def match(ingestion_id: str) -> MatchResult:
    """
    Temporary lightweight matcher.

    Later:
    - Zone/discipline pruning
    - ChromaDB dense vector search
    - RapidFuzz lexical matching
    - Context ranking
    - Explanation generator
    """
    ingestion = state.ingestions.get(ingestion_id)

    if not ingestion:
        raise InvalidStateError(f"Ingestion {ingestion_id} not found.")

    if "extraction" not in ingestion:
        raise InvalidStateError("Run extraction before matching.")

    extraction = ExtractionSchema(**ingestion["extraction"])
    candidates = []

    for task in state.tasks.values():
        # Simple rule-based pruning.
        if (
            extraction.spatial_zone
            and task.get("zone")
            and extraction.spatial_zone.lower() != task["zone"].lower()
        ):
            continue

        if (
            extraction.discipline
            and task.get("discipline")
            and extraction.discipline.lower() != task["discipline"].lower()
        ):
            continue

        score, reason = _score_task(task, extraction)

        if score >= 0.25:
            candidates.append(
                MatchCandidate(
                    task_id=task["activity_id"],
                    task_name=task["name"],
                    wbs_code=task["wbs_code"],
                    match_score=score,
                    match_reason=reason,
                )
            )

    candidates.sort(key=lambda candidate: candidate.match_score, reverse=True)

    top = candidates[0] if candidates else None

    result = MatchResult(
        ingestion_id=ingestion_id,
        matched_task_id=top.task_id if top else None,
        task_name=top.task_name if top else None,
        wbs_code=top.wbs_code if top else None,
        match_score=top.match_score if top else 0.0,
        match_reason=top.match_reason if top else "No sufficiently relevant task found.",
        alternative_matches=candidates[1:4],
    )

    ingestion["match"] = result.model_dump()
    ingestion["status"] = "matched"

    return result