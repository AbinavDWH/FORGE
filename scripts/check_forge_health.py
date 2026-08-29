# Replace: scripts/check_forge_health.py
#!/usr/bin/env python3
"""
FORGE health check.
Verifies the current FORGE build state up to MOD-03/04.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PASS: list[str] = []
WARN: list[str] = []
FAIL: list[str] = []


def report(status: str, message: str) -> None:
    print(f"[{status}] {message}")

    if status == "PASS":
        PASS.append(message)
    elif status == "WARN":
        WARN.append(message)
    elif status == "FAIL":
        FAIL.append(message)


def check_file(path: str, required: bool = True) -> None:
    full_path = ROOT / path

    if full_path.exists():
        report("PASS", f"File exists: {path}")
    else:
        if required:
            report("FAIL", f"Missing required file: {path}")
        else:
            report("WARN", f"Missing optional file: {path}")


def check_directory(path: str, required: bool = True) -> None:
    full_path = ROOT / path

    if full_path.exists() and full_path.is_dir():
        report("PASS", f"Directory exists: {path}")
    else:
        if required:
            report("FAIL", f"Missing required directory: {path}")
        else:
            report("WARN", f"Missing optional directory: {path}")


def check_files() -> None:
    print("\n=== FILESYSTEM CHECKS ===")

    required_files = [
        "requirements.txt",
        "app/main.py",
        "app/api/ingestion.py",
        "app/api/extraction.py",
        "app/api/matcher.py",
        "app/api/review.py",
        "app/api/schedule.py",
        "app/api/audit.py",
        "app/matcher/hybrid_search.py",
        "app/matcher/fuzzy_scorer.py",
        "app/audit/hash_chain.py",
        "frontend/package.json",
        "frontend/src/pages/ReviewTray.jsx",
        "frontend/src/pages/GanttView.jsx",
    ]

    optional_files = [
        ".env.example",
        "app/extraction/whisper_asr.py",
        "app/extraction/ocr_service.py",
        "app/extraction/vlm_verifier.py",
        "app/crosscheck/comparator.py",
        "app/audit/synthetic_media_gate.py",
        "data/sample_schedule/masters/aliases.json",
        "data/sample_media/images/pier14_site_photo.jpg",
        "data/sample_media/synthetic/ai_generated_sample.jpg",
        "scripts/demo_fuzzy_matcher.py",
        "tests/test_matcher_fuzzy.py",
    ]

    for path in required_files:
        check_file(path, required=True)

    for path in optional_files:
        check_file(path, required=False)

    required_directories = [
        "app",
        "app/api",
        "app/matcher",
        "app/audit",
        "frontend",
        "frontend/src",
        "data",
    ]

    optional_directories = [
        "app/extraction",
        "app/crosscheck",
        "data/sample_schedule",
        "data/sample_media",
        "storage/raw",
        "storage/processed",
        "storage/exports",
    ]

    for path in required_directories:
        check_directory(path, required=True)

    for path in optional_directories:
        check_directory(path, required=False)


def check_python_module(module_name: str, label: str, required: bool = True) -> None:
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            report("PASS", f"Python module available: {label} ({module_name})")
        else:
            if required:
                report("FAIL", f"Missing required Python module: {label} ({module_name})")
            else:
                report("WARN", f"Missing optional Python module: {label} ({module_name})")
    except Exception as exc:
        if required:
            report("FAIL", f"Cannot check required Python module {label} ({module_name}): {exc}")
        else:
            report("WARN", f"Cannot check optional Python module {label} ({module_name}): {exc}")


def check_python_packages() -> None:
    print("\n=== PYTHON PACKAGE CHECKS ===")

    check_python_module("fastapi", "FastAPI", required=True)
    check_python_module("pydantic", "Pydantic", required=True)
    check_python_module("uvicorn", "Uvicorn", required=True)
    check_python_module("rapidfuzz", "RapidFuzz", required=True)

    check_python_module("whisper", "Whisper ASR", required=False)
    check_python_module("rapidocr_onnxruntime", "RapidOCR", required=False)
    check_python_module("chromadb", "ChromaDB", required=False)
    check_python_module("PIL", "Pillow / image handling", required=False)


def check_matcher_smoke() -> None:
    print("\n=== RAPIDFUZZ MATCHER SMOKE TEST ===")

    try:
        from app.matcher.hybrid_search import match_update
    except Exception as exc:
        report("FAIL", f"Cannot import app.matcher.hybrid_search.match_update: {exc}")
        return

    tasks = [
        {
            "task_id": "CIV-STR-014",
            "wbs_code": "CIV-STR-014",
            "task_name": "Pier 14 Concrete Work",
            "zone": "Zone B",
            "discipline": "Civil",
            "component": "Pier 14",
            "component_aliases": ["Pier 14", "Pier14"],
            "activity_keywords": ["concrete", "pouring", "concrete pouring", "concrete work"],
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
            "component_aliases": ["Pier 14", "Pier14"],
            "activity_keywords": ["curing", "concrete curing"],
            "status": "Not Started",
            "is_active": False,
        },
    ]

    update = {
        "ingestion_id": "ING-HEALTH-CHECK",
        "spatial_zone": "Zone B",
        "discipline": "Civil",
        "component": "Peer 14",
        "action": "concret pour",
        "status": "Completed",
        "raw_text": "Sector B Peer 14 concret pour done",
    }

    try:
        result = match_update(update, tasks)
    except Exception as exc:
        report("FAIL", f"Matcher smoke test raised an exception: {exc}")
        return

    matched_task_id = result.get("matched_task_id")

    if matched_task_id == "CIV-STR-014":
        report("PASS", "RapidFuzz matcher smoke test matched CIV-STR-014 correctly.")
    else:
        report("FAIL", f"RapidFuzz matcher smoke test expected CIV-STR-014 but got {matched_task_id}.")

    if result.get("match_reason"):
        report("PASS", f"Matcher explanation present: {result.get('match_reason')}")
    else:
        report("WARN", "Matcher result does not include match_reason.")


def fetch_url(url: str) -> tuple[bool, int | None, bytes]:
    try:
        with urlopen(url, timeout=3) as response:
            return True, response.status, response.read()
    except HTTPError as exc:
        return False, exc.code, b""
    except URLError:
        return False, None, b""
    except Exception:
        return False, None, b""


def check_backend() -> None:
    print("\n=== BACKEND CHECKS ===")

    backend_url = os.getenv("FORGE_BACKEND_URL", "http://127.0.0.1:8000")

    docs_ok, docs_status, _ = fetch_url(f"{backend_url}/docs")

    if docs_ok and docs_status == 200:
        report("PASS", f"Backend docs available at {backend_url}/docs")
    else:
        report("WARN", f"Backend docs not reachable at {backend_url}/docs.")

    openapi_ok, openapi_status, body = fetch_url(f"{backend_url}/openapi.json")

    if not openapi_ok or openapi_status != 200:
        report("WARN", f"OpenAPI schema not reachable at {backend_url}/openapi.json")
        return

    try:
        openapi = json.loads(body.decode("utf-8"))
    except Exception as exc:
        report("WARN", f"Could not parse OpenAPI JSON: {exc}")
        return

    paths = list(openapi.get("paths", {}).keys())

    if not paths:
        report("WARN", "OpenAPI schema contains no paths.")
        return

    report("PASS", f"OpenAPI schema contains {len(paths)} API paths.")


def check_frontend() -> None:
    print("\n=== FRONTEND CHECKS ===")

    frontend_url = os.getenv("FORGE_FRONTEND_URL", "http://localhost:5173")

    ok, status, _ = fetch_url(frontend_url)

    if ok and status == 200:
        report("PASS", f"Frontend reachable at {frontend_url}")
    else:
        report("WARN", f"Frontend not reachable at {frontend_url}.")


def check_frontend_dynamic_gantt() -> None:
    print("\n=== GANTT HARDCODE / DYNAMIC DATA SCAN ===")

    frontend_src = ROOT / "frontend" / "src"

    if not frontend_src.exists():
        report("WARN", "frontend/src not found. Skipping Gantt hardcoded-data scan.")
        return

    candidate_paths: list[Path] = []

    gantt_dir = frontend_src / "gantt"
    pages_dir = frontend_src / "pages"

    if gantt_dir.exists():
        candidate_paths.extend(gantt_dir.rglob("*.jsx"))
        candidate_paths.extend(gantt_dir.rglob("*.js"))

    if pages_dir.exists():
        candidate_paths.extend(pages_dir.rglob("*.jsx"))
        candidate_paths.extend(pages_dir.rglob("*.js"))

    if not candidate_paths:
        report("WARN", "No frontend Gantt/page files found for hardcoded-data scan.")
        return

    suspicious_patterns = [
        re.compile(r"(?i)(tasks|bars|gantt[_-]?data)\s*[:=]\s*\["),
        re.compile(r"(?i)start_?(date|time).*\d{4}-\d{2}-\d{2}"),
        re.compile(r"(?i)end_?(date|time).*\d{4}-\d{2}-\d{2}"),
        re.compile(r"(?i)progress\s*[:=]\s*\d{1,3}\s*%?"),
    ]

    api_patterns = [
        re.compile(r"fetch\("),
        re.compile(r"axios"),
        re.compile(r"/api/schedule"),
        re.compile(r"/api/gantt"),
        re.compile(r"useQuery"),
        re.compile(r"useSWR"),
    ]

    suspicious_files: set[str] = set()
    api_found = False

    for file_path in candidate_paths:
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern in suspicious_patterns:
            if pattern.search(text):
                suspicious_files.add(str(file_path.relative_to(ROOT)))

        if any(pattern.search(text) for pattern in api_patterns):
            api_found = True

    if suspicious_files:
        report("WARN", "Possible hardcoded Gantt/date/progress data found in: " + ", ".join(sorted(suspicious_files)))
    else:
        report("PASS", "No obvious hardcoded Gantt/date/progress patterns detected.")

    if api_found:
        report("PASS", "Frontend files appear to use API/data-fetching patterns.")
    else:
        report("WARN", "No clear API/data-fetching pattern found in scanned frontend files.")


def print_summary() -> None:
    print("\n=== SUMMARY ===")
    print(f"PASS: {len(PASS)}")
    print(f"WARN: {len(WARN)}")
    print(f"FAIL: {len(FAIL)}")

    if WARN:
        print("\nWarnings:")
        for item in WARN:
            print(f"  - {item}")

    if FAIL:
        print("\nFailures:")
        for item in FAIL:
            print(f"  - {item}")

    if FAIL:
        print("\nFORGE health check finished with failures.")
        sys.exit(1)
    else:
        print("\nFORGE health check finished successfully. Ready for next module.")
        sys.exit(0)


def main() -> None:
    print("FORGE Health Check")
    print(f"Repository root: {ROOT}")

    check_files()
    check_python_packages()
    check_matcher_smoke()
    check_backend()
    check_frontend()
    check_frontend_dynamic_gantt()
    print_summary()


if __name__ == "__main__":
    main()