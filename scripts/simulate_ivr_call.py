#!/usr/bin/env python3
"""
Simulate an incoming IVR phone call from a zero-internet site dead zone.
Demonstrates MOD-08 (Telephony IVR Fallback).
"""
import sys
import httpx
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BACKEND_URL = "http://127.0.0.1:8000"


def main():
    spoken_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Sector B Pier 14 concrete pouring completed"
    caller = "+919854012345"  # NRL Golaghat site line

    print(f"📞 [IVR Simulator] Calling FORGE Toll-Free line...")
    print(f"👤 Caller: {caller} (Site Supervisor, Golaghat Dead-Zone)")
    print(f"🎙️ Spoken: \"{spoken_text}\"")

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(
                f"{BACKEND_URL}/api/webhooks/ivr/simulate",
                data={
                    "spoken_text": spoken_text,
                    "caller_phone": caller,
                },
            )
            resp.raise_for_status()
            data = resp.json()

            print("\n✅ IVR Call Connected & Processed!")
            print(f"   • Ingestion ID: {data['ingestion_id']}")
            print(f"   • Source: {data['source']}")
            print(f"   • Media Type: {data['media_type']}")
            print(f"   • Status: {data['status']}")
            print("\n👉 Open the FORGE Review Tray UI at http://localhost:5173/review to see the update.")

    except Exception as e:
        print(f"\n❌ Error contacting FORGE backend: {e}")
        print("   Ensure the backend is running on http://127.0.0.1:8000")
        sys.exit(1)


if __name__ == "__main__":
    main()
