from app.matcher.hybrid_search import match_update

TASKS = [
    {
        "task_id": "CIV-STR-014",
        "wbs_code": "CIV-STR-014",
        "task_name": "Pier 14 Concrete Work",
        "zone": "Zone B",
        "discipline": "Civil",
        "component": "Pier 14",
        "component_aliases": [
            "Pier 14",
            "Pier14",
        ],
        "activity_keywords": [
            "concrete",
            "pouring",
            "concrete pouring",
            "concrete work",
        ],
        "status": "In Progress",
        "is_active": True,
    },
    {
        "task_id": "CIV-STR-015",
        "wbs_code": "CIV-STR-015",
        "task_name": "Pier 14 Curing",
        "zone": "Zone B",
        "discipline": "Civil",
        "component": "Pier 14",
        "component_aliases": [
            "Pier 14",
            "Pier14",
        ],
        "activity_keywords": [
            "curing",
            "concrete curing",
        ],
        "status": "Not Started",
        "is_active": False,
    },
    {
        "task_id": "ELE-CAB-021",
        "wbs_code": "ELE-CAB-021",
        "task_name": "Cable Tray Installation",
        "zone": "Zone B",
        "discipline": "Electrical",
        "component": "Cable Tray",
        "activity_keywords": [
            "cable tray",
            "installation",
        ],
        "status": "Not Started",
        "is_active": False,
    },
]


def _base_update(**overrides):
    update = {
        "ingestion_id": "ING-1001",
        "spatial_zone": "Zone B",
        "discipline": "Civil",
        "component": "Peer 14",
        "action": "concret pour",
        "status": "Completed",
        "raw_text": "Sector B Peer 14 concret pour done",
    }

    update.update(overrides)
    return update


def test_rapidfuzz_handles_asr_typo_for_component_and_action():
    """
    ASR typo:
        Peer 14 -> Pier 14
        concret pour -> concrete pouring
    """
    result = match_update(_base_update(), TASKS)

    assert result["matched_task_id"] == "CIV-STR-014"
    assert result["match_score"] > 0.70
    assert "pier 14" in result["match_reason"].lower()


def test_wrong_discipline_is_not_matched():
    """
    Civil update should not match an electrical task.
    """
    result = match_update(
        _base_update(
            action="cable tray installation",
            raw_text="Sector B Pier 14 cable tray installation done",
        ),
        TASKS,
    )

    assert result["matched_task_id"] != "ELE-CAB-021"

    alternative_task_ids = [
        item["task_id"]
        for item in result["alternative_matches"]
    ]

    assert "ELE-CAB-021" not in alternative_task_ids


def test_no_candidate_when_zone_does_not_match():
    """
    If zone pruning eliminates all tasks, do not blindly search all tasks.
    """
    result = match_update(
        _base_update(spatial_zone="Zone Z"),
        TASKS,
    )

    assert result["matched_task_id"] is None
    assert result["match_score"] == 0.0