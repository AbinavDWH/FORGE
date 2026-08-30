from app.confidence.scorer import calculate_confidence
from app.confidence.routing import route_by_confidence


def test_confidence_auto_commit():
    res = calculate_confidence(
        match_score=0.95,
        extraction_confidence=0.90,
        metadata={"gps_coords": "26.58, 93.96", "exif_present": True, "evidence_present": True},
        cross_check_result={"cross_check_status": "agreed"},
        synthetic_media_result={"ai_generation_risk": "low"},
    )
    assert res["score"] >= 85
    assert res["routing"] == "auto_commit"


def test_confidence_review_on_missing_metadata():
    res = calculate_confidence(
        match_score=0.85,
        extraction_confidence=0.80,
        metadata={"gps_coords": None, "exif_present": False},
        cross_check_result={"cross_check_status": "single_source"},
        synthetic_media_result={"ai_generation_risk": "low"},
    )
    assert res["routing"] == "review"
    assert any("Missing GPS" in exp for exp in res["explanation"])
    assert any("Missing EXIF" in exp for exp in res["explanation"])


def test_confidence_blocked_on_synthetic_media():
    res = calculate_confidence(
        match_score=0.95,
        extraction_confidence=0.95,
        metadata={"gps_coords": "26.58, 93.96", "exif_present": True},
        synthetic_media_result={"ai_generation_risk": "high"},
    )
    assert res["score"] <= 30
    assert res["routing"] == "manual"
    assert any("BLOCKED" in exp or "synthetic" in exp for exp in res["explanation"])


def test_routing_thresholds():
    assert route_by_confidence(85) == "auto_commit"
    assert route_by_confidence(90) == "auto_commit"
    assert route_by_confidence(84) == "review"
    assert route_by_confidence(50) == "review"
    assert route_by_confidence(49) == "manual"
    assert route_by_confidence(10) == "manual"
