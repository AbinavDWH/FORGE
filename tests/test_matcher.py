from app.schedule.xml_parser import parse_schedule
from app.matcher.hybrid_search import match_update, prune_tasks
from app.extraction.structurer import structure_text


def test_matcher_against_sample_schedule():
    tasks = parse_schedule()
    assert len(tasks) >= 20

    update = {
        "ingestion_id": "ING-101",
        "spatial_zone": "Zone B",
        "discipline": "Civil",
        "component": "Pier 14",
        "action": "Concrete pouring",
        "status": "Completed",
        "raw_text": "Sector B Pier 14 concrete pouring completed",
    }

    result = match_update(update, tasks)
    assert result["matched_task_id"] is not None
    assert result["wbs_code"] == "CIV-STR-014"
    assert result["match_score"] > 0.70
    assert "Pier 14" in result["task_name"]
    assert "Civil" in result["match_reason"] or "Pier 14" in result["match_reason"]


def test_matcher_multi_lingual_hinglish_hindi():
    tasks = parse_schedule()
    raw = "Sector B Pier 14 ka dhalai complete ho gaya"
    structured = structure_text(raw)
    structured["raw_text"] = raw

    result = match_update(structured, tasks)
    assert result["matched_task_id"] is not None
    assert result["wbs_code"] == "CIV-STR-014"
    assert "Pier 14" in result["task_name"]


def test_matcher_multi_lingual_assamese():
    tasks = parse_schedule()
    raw = "Zone B Pier 14 r dhalai sesh hol"
    structured = structure_text(raw)
    structured["raw_text"] = raw

    result = match_update(structured, tasks)
    assert result["matched_task_id"] is not None
    assert result["wbs_code"] == "CIV-STR-014"
    assert "Pier 14" in result["task_name"]


def test_matcher_multi_lingual_tamil():
    tasks = parse_schedule()
    raw = "Zone B Pier 14 concrete oothiyaachu"
    structured = structure_text(raw)
    structured["raw_text"] = raw

    result = match_update(structured, tasks)
    assert result["matched_task_id"] is not None
    assert result["wbs_code"] == "CIV-STR-014"
    assert "Pier 14" in result["task_name"]


def test_matcher_piping_hydro_test():
    tasks = parse_schedule()

    update = {
        "ingestion_id": "ING-102",
        "spatial_zone": "Pipeline Corridor",
        "discipline": "Piping",
        "component": "Line 2",
        "action": "Hydro testing",
        "status": "Completed",
        "raw_text": "Pipeline Corridor Line 2 hydro testing completed",
    }

    result = match_update(update, tasks)
    assert result["matched_task_id"] is not None
    assert "PIP" in result["wbs_code"]
    assert "Hydro" in result["task_name"]


def test_matcher_pruning():
    tasks = parse_schedule()
    update = {
        "spatial_zone": "Zone A",
        "discipline": "Civil",
    }
    pruned = prune_tasks(update, tasks)
    for t in pruned:
        if t.get("zone"):
            assert "Zone A" in t["zone"]
        if t.get("discipline"):
            assert "Civil" in t["discipline"]
