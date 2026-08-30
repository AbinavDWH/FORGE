from app.schedule.cpm_guard import check_cpm_dependencies


SAMPLE_SCHEDULE = [
    {
        "task_id": "1",
        "wbs_code": "CIV-STR-013",
        "task_name": "Pier 14 Rebar Inspection",
        "percent_complete": 0,
        "predecessors": None,
    },
    {
        "task_id": "2",
        "wbs_code": "CIV-STR-014",
        "task_name": "Pier 14 Concrete Work",
        "percent_complete": 0,
        "predecessors": "1",
    },
    {
        "task_id": "3",
        "wbs_code": "CIV-STR-015",
        "task_name": "Pier 14 Curing",
        "percent_complete": 0,
        "predecessors": "2",
    },
]


def test_cpm_guard_blocks_when_predecessor_incomplete():
    # Task 2 depends on Task 1 (which is 0% complete)
    result = check_cpm_dependencies(
        task_id="2",
        proposed_percent=100,
        schedule_data=SAMPLE_SCHEDULE,
    )
    assert result["valid"] is False
    assert "Dependency Violation" in result["reason"]


def test_cpm_guard_allows_independent_task():
    # Task 1 has no predecessors
    result = check_cpm_dependencies(
        task_id="1",
        proposed_percent=100,
        schedule_data=SAMPLE_SCHEDULE,
    )
    assert result["valid"] is True


def test_cpm_guard_allows_when_predecessors_complete():
    schedule = [
        {
            "task_id": "1",
            "wbs_code": "CIV-STR-013",
            "task_name": "Pier 14 Rebar Inspection",
            "percent_complete": 100,
            "predecessors": None,
        },
        {
            "task_id": "2",
            "wbs_code": "CIV-STR-014",
            "task_name": "Pier 14 Concrete Work",
            "percent_complete": 0,
            "predecessors": "1",
        },
    ]

    result = check_cpm_dependencies(
        task_id="2",
        proposed_percent=50,
        schedule_data=schedule,
    )
    assert result["valid"] is True
