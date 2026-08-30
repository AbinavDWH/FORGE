#!/usr/bin/env python3
"""Reset demo data to clean state."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "data" / "sample_schedule" / "nrl_crude_tank.xml"
BACKUP = SCHEDULE.with_suffix(".xml.backup")
AUDIT = ROOT / "storage" / "audit_chain.jsonl"

def main():
    # Reset schedule from backup
    if BACKUP.exists():
        shutil.copy(BACKUP, SCHEDULE)
        print(f"✓ Schedule reset from backup")
    else:
        print(f"⚠ No backup found at {BACKUP}")
    
    # Clear audit log
    if AUDIT.exists():
        AUDIT.write_text("")
        print(f"✓ Audit chain cleared")
    else:
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        AUDIT.touch()
        print(f"✓ Audit chain created")
    
    print("\nDemo data ready.")

if __name__ == "__main__":
    main()
