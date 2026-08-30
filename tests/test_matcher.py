from app.schedule.xml_parser import parse_schedule
from app.matcher.hybrid_search import match_update, prune_tasks


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


def test_matcher_piping_hydro_test():
    tasks = parse_schedule()

    update = {
        "ingestion_id": "ING-102",
        "spatial_zone": "Pipeline Corridor",
        "discipline": "Piping",
        "component": "Pipe Spool",
        "action": "Hydro testing",
        "status": "Completed",
        "raw_text": "Pipeline Corridor pipe spool hydro testing done",
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
