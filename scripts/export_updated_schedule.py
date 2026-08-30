#!/usr/bin/env python3
"""Export the current schedule state."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schedule.xml_parser import parse_schedule

def main():
    tasks = parse_schedule()
    output = Path(__file__).resolve().parents[1] / "storage" / "exports" / "schedule_export.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(tasks, f, indent=2)
    print(f"✓ Exported {len(tasks)} tasks to {output}")

if __name__ == "__main__":
    main()
