"""3-Tier Confidence Routing per FORGE module plan."""
from app.core.settings import settings

def route_by_confidence(score: int) -> str:
    """
    Route based on confidence score using 3-tier thresholds.
    """
    if score >= settings.auto_commit_threshold:
        return "auto_commit"
    elif score >= settings.review_threshold:
        return "review"
    else:
        return "manual"
