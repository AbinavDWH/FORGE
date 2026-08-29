from typing import Any, Dict


def _sample_tasks() -> Dict[str, Dict[str, Any]]:
    """
    Demo schedule for NRL-style crude tank / pier construction.

    Later this will be replaced by real .xer / .xml parsing.
    """
    return {
        "CIV-STR-010": {
            "activity_id": "CIV-STR-010",
            "wbs_code": "CIV-STR-010",
            "name": "Excavation for Pier 14",
            "zone": "Zone B",
            "discipline": "Civil",
            "component": "Pier 14",
            "planned_start": "2026-08-01T08:00:00Z",
            "planned_finish": "2026-08-03T17:00:00Z",
            "baseline_start": "2026-08-01T08:00:00Z",
            "baseline_finish": "2026-08-03T17:00:00Z",
            "actual_start": "2026-08-01T08:20:00Z",
            "actual_finish": "2026-08-03T16:10:00Z",
            "percent_complete": 100,
            "dependencies": [],
            "status": "completed",
            "evidence_reference": None,
            "last_updated": None,
            "last_update_ingestion_id": None,
            "last_update_approved_by": None,
        },
        "CIV-STR-011": {
            "activity_id": "CIV-STR-011",
            "wbs_code": "CIV-STR-011",
            "name": "Rebar Inspection for Pier 14",
            "zone": "Zone B",
            "discipline": "Civil",
            "component": "Pier 14",
            "planned_start": "2026-08-04T08:00:00Z",
            "planned_finish": "2026-08-04T17:00:00Z",
            "baseline_start": "2026-08-04T08:00:00Z",
            "baseline_finish": "2026-08-04T17:00:00Z",
            "actual_start": "2026-08-04T08:15:00Z",
            "actual_finish": "2026-08-04T15:40:00Z",
            "percent_complete": 100,
            "dependencies": ["CIV-STR-010"],
            "status": "completed",
            "evidence_reference": None,
            "last_updated": None,
            "last_update_ingestion_id": None,
            "last_update_approved_by": None,
        },
        "CIV-STR-014": {
            "activity_id": "CIV-STR-014",
            "wbs_code": "CIV-STR-014",
            "name": "Pier 14 Concrete Work",
            "zone": "Zone B",
            "discipline": "Civil",
            "component": "Pier 14",
            "planned_start": "2026-08-05T08:00:00Z",
            "planned_finish": "2026-08-05T17:00:00Z",
            "baseline_start": "2026-08-05T08:00:00Z",
            "baseline_finish": "2026-08-05T17:00:00Z",
            "actual_start": None,
            "actual_finish": None,
            "percent_complete": 0,
            "dependencies": ["CIV-STR-011"],
            "status": "planned",
            "evidence_reference": None,
            "last_updated": None,
            "last_update_ingestion_id": None,
            "last_update_approved_by": None,
        },
        "CIV-STR-015": {
            "activity_id": "CIV-STR-015",
            "wbs_code": "CIV-STR-015",
            "name": "Pier 14 Curing",
            "zone": "Zone B",
            "discipline": "Civil",
            "component": "Pier 14",
            "planned_start": "2026-08-06T08:00:00Z",
            "planned_finish": "2026-08-12T17:00:00Z",
            "baseline_start": "2026-08-06T08:00:00Z",
            "baseline_finish": "2026-08-12T17:00:00Z",
            "actual_start": None,
            "actual_finish": None,
            "percent_complete": 0,
            "dependencies": ["CIV-STR-014"],
            "status": "planned",
            "evidence_reference": None,
            "last_updated": None,
            "last_update_ingestion_id": None,
            "last_update_approved_by": None,
        },
        "PIP-HYD-021": {
            "activity_id": "PIP-HYD-021",
            "wbs_code": "PIP-HYD-021",
            "name": "Hydro Testing for Line 2",
            "zone": "Zone B",
            "discipline": "Piping",
            "component": "Line 2",
            "planned_start": "2026-08-10T08:00:00Z",
            "planned_finish": "2026-08-11T17:00:00Z",
            "baseline_start": "2026-08-10T08:00:00Z",
            "baseline_finish": "2026-08-11T17:00:00Z",
            "actual_start": None,
            "actual_finish": None,
            "percent_complete": 0,
            "dependencies": [],
            "status": "planned",
            "evidence_reference": None,
            "last_updated": None,
            "last_update_ingestion_id": None,
            "last_update_approved_by": None,
        },
        "INS-PIP-022": {
            "activity_id": "INS-PIP-022",
            "wbs_code": "INS-PIP-022",
            "name": "Insulation for Line 2",
            "zone": "Zone B",
            "discipline": "Piping",
            "component": "Line 2",
            "planned_start": "2026-08-12T08:00:00Z",
            "planned_finish": "2026-08-14T17:00:00Z",
            "baseline_start": "2026-08-12T08:00:00Z",
            "baseline_finish": "2026-08-14T17:00:00Z",
            "actual_start": None,
            "actual_finish": None,
            "percent_complete": 0,
            "dependencies": ["PIP-HYD-021"],
            "status": "planned",
            "evidence_reference": None,
            "last_updated": None,
            "last_update_ingestion_id": None,
            "last_update_approved_by": None,
        },
    }


class InMemoryState:
    """
    Temporary in-memory state for the first runnable MVP.

    Later:
    - Tasks come from .xer / .xml parser.
    - Ingestions, updates, and audit logs move to PostgreSQL / SQLite.
    - File evidence moves to storage/ with metadata manifests.
    """

    def __init__(self) -> None:
        self.seq = 1
        self.tasks = _sample_tasks()
        self.ingestions: Dict[str, Dict[str, Any]] = {}
        self.updates: Dict[str, Dict[str, Any]] = {}
        self.audit_log: list[Dict[str, Any]] = []

    def next_ingestion_id(self) -> str:
        ingestion_id = f"ING-{1000 + self.seq}"
        self.seq += 1
        return ingestion_id


state = InMemoryState()