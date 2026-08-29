from app.api.schemas import ConfidenceResult, ExtractionSchema, MatchResult
from app.core.settings import settings
from app.core.state import state


def compute_confidence(ingestion_id: str) -> ConfidenceResult:
    """
    Temporary confidence engine.

    Later factors:
    - OCR vs VLM agreement
    - Metadata quality
    - Synthetic media screening
    - Dependency validity
    - Evidence availability
    - Matcher explanation strength
    """
    ingestion = state.ingestions.get(ingestion_id)

    if not ingestion:
        raise ValueError(f"Ingestion {ingestion_id} not found.")

    extraction = ExtractionSchema(**ingestion["extraction"])
    match = MatchResult(**ingestion["match"])

    explanation = []

    base_score = (0.6 * match.match_score + 0.4 * extraction.extraction_confidence) * 100
    explanation.append(
        f"Base score from matcher ({match.match_score:.2f}) "
        f"and extraction confidence ({extraction.extraction_confidence:.2f})."
    )

    score = base_score

    if ingestion.get("metadata_status") == "verified":
        score += 5
        explanation.append("Metadata verified.")
    else:
        score -= 10
        explanation.append("Missing or incomplete metadata.")

    if extraction.cross_check_status == "agreed":
        score += 5
        explanation.append("Dual-source extraction agreed.")
    elif extraction.cross_check_status == "partial_mismatch":
        score = min(score, 84)
        explanation.append("Partial cross-check mismatch. Auto-commit capped.")
    elif extraction.cross_check_status == "disagreed":
        score = min(score, 60)
        explanation.append("Cross-check disagreement. Human review required.")
    elif extraction.cross_check_status == "single_source":
        score -= 2
        explanation.append("Single-source extraction.")

    if not extraction.component:
        score -= 8
        explanation.append("Missing component reduces confidence.")

    if extraction.percent_complete is not None:
        score += 3
        explanation.append("Explicit progress value present.")

    if not match.matched_task_id:
        score = min(score, 20)
        explanation.append("No matched schedule task.")

    ai_generation_risk = ingestion.get("ai_generation_risk", "low")

    if ai_generation_risk == "medium":
        score = min(score, 84)
        explanation.append("Medium synthetic-media risk. Auto-commit capped.")
    elif ai_generation_risk == "high":
        score = 0
        explanation.append("High synthetic-media risk. Evidence blocked.")

    score = max(0, min(100, int(round(score))))

    if score >= settings.auto_commit_threshold:
        routing = "auto_commit"
    elif score >= settings.review_threshold:
        routing = "manager_review"
    else:
        routing = "manual_handling"

    result = ConfidenceResult(
        score=score,
        routing=routing,
        explanation=explanation,
    )

    ingestion["confidence"] = result.model_dump()
    ingestion["status"] = "confidence_scored"

    return result