"""MOD-04: Confidence & Review Engine - Scoring Service"""
from typing import Dict, Any, List, Optional

from app.confidence.adjustments import apply_adjustments
from app.confidence.routing import route_by_confidence

def calculate_confidence(
    match_score: float,
    extraction_confidence: float,
    metadata: Optional[Dict[str, Any]] = None,
    cross_check_result: Optional[Dict[str, Any]] = None,
    synthetic_media_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calculate confidence score based on match and extraction scores, 
    applying adjustments and routing logic.
    """
    base_score = (0.6 * match_score + 0.4 * extraction_confidence) * 100
    explanations = []
    
    if match_score > 0.85:
        base_score += 5.0
        explanations.append("Clear component match (+5 points)")
        
    adjusted_score, adj_explanations = apply_adjustments(
        base_score=base_score,
        metadata=metadata,
        cross_check_result=cross_check_result,
        synthetic_media_result=synthetic_media_result,
    )
    
    explanations.extend(adj_explanations)
    
    final_score = int(max(0, min(100, adjusted_score)))
    routing = route_by_confidence(final_score)
    
    return {
        "score": final_score,
        "routing": routing,
        "explanation": explanations,
    }
