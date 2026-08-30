#!/usr/bin/env python3
"""Validate the FORGE audit hash chain integrity."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.audit.hash_chain import verify_chain

def main():
    result = verify_chain()
    print(f"Records: {result['total_records']}")
    print(f"Valid: {result['is_valid']}")
    if result['errors']:
        for err in result['errors']:
            print(f"  ✗ {err}")
    else:
        print("  ✓ Chain integrity verified")

if __name__ == "__main__":
    main()
