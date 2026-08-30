from app.crosscheck.comparator import compare


def test_crosscheck_agreed():
    ocr_ext = {
        "spatial_zone": "Zone B",
        "discipline": "Civil",
        "component": "Pier 14",
        "action": "Concrete pouring",
        "status": "Completed",
        "percent_complete": 100,
    }
    vlm_ext = {
        "spatial_zone": "Zone B",
        "discipline": "Civil",
        "component": "Pier 14",
        "action": "Concrete pour",
        "status": "Complete",
        "percent_complete": 100,
    }
    result = compare(ocr_ext, vlm_ext)
    assert result["cross_check_status"] == "agreed"
    assert result["agreement_score"] == 1.0
    assert result["source_of_truth"] == "ocr"
    assert result["ocr_extraction"] == ocr_ext


def test_crosscheck_partial_mismatch():
    ocr_ext = {
        "component": "Pier 14",
        "action": "Concrete pouring",
        "status": "Completed",
    }
    vlm_ext = {
        "component": "Pier 14",
        "action": "Rebar inspection",
        "status": "Completed",
    }
    result = compare(ocr_ext, vlm_ext)
    assert result["cross_check_status"] == "partial_mismatch"
    assert result["field_agreement"]["component"] == "match"
    assert result["field_agreement"]["action"] == "mismatch"
    assert result["field_agreement"]["status"] == "match"
    assert result["source_of_truth"] == "ocr"


def test_crosscheck_disagreed():
    ocr_ext = {
        "component": "Pier 14",
        "action": "Concrete pouring",
        "status": "Completed",
    }
    vlm_ext = {
        "component": "Tank Base",
        "action": "Excavation",
        "status": "In Progress",
    }
    result = compare(ocr_ext, vlm_ext)
    assert result["cross_check_status"] == "disagreed"
    assert result["agreement_score"] == 0.0
