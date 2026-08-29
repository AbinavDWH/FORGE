# Replace: scripts/demo_fuzzy_matcher.py
"""
Quick local demo for MOD-03 RapidFuzz matcher upgrade.

Run from repository root:

    python scripts/demo_fuzzy_matcher.py
"""

import json
import sys
from pathlib import Path

# Make the repository root importable so `app.*` modules can be loaded.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
]

UPDATE = {
    "ingestion_id": "ING-1001",
    "spatial_zone": "Zone B",
    "discipline": "Civil",
    "component": "Peer 14",
    "action": "concret pour",
    "status": "Completed",
    "raw_text": "Sector B Peer 14 concret pour done",
}

if __name__ == "__main__":
    result = match_update(UPDATE, TASKS)

    print("FORGE RapidFuzz Matcher Demo")
    print("=" * 40)
    print("Field update:")
    print(UPDATE["raw_text"])
    print("=" * 40)
    print("Match result:")
    print(json.dumps(result, indent=2))