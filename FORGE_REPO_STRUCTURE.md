
# FORGE Repository Structure

Project: FORGE — Field Operations Reconciliation & Gantt Engine  
Hackathon: Smart India Hackathon 2026  
Problem Statement ID: SIH26122  
Sponsored By: Oil India Limited  

This document defines the correct repository tree structure for FORGE.

It expands the high-level structure from `FORGE_MODULE_PLAN.md` into a clear, build-ready folder and file layout.

---

## Canonical Repository Tree

```text
forge/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── pyproject.toml
├── Makefile
├── docker-compose.yml
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   ├── extraction.py
│   │   ├── crosscheck.py
│   │   ├── matcher.py
│   │   ├── review.py
│   │   ├── schedule.py
│   │   ├── audit.py
│   │   └── schemas.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── settings.py
│   │   ├── logging.py
│   │   └── errors.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── telegram_bot.py
│   │   ├── media_receiver.py
│   │   ├── metadata_manifest.py
│   │   ├── ivr_webhook.py
│   │   ├── offline_queue.py
│   │   └── storage.py
│   │
│   ├── extraction/
│   │   ├── __init__.py
│   │   ├── whisper_asr.py
│   │   ├── ocr_service.py
│   │   ├── vlm_verifier.py
│   │   ├── llm_structurer.py
│   │   ├── schemas.py
│   │   └── extraction_confidence.py
│   │
│   ├── crosscheck/
│   │   ├── __init__.py
│   │   ├── normalizer.py
│   │   ├── comparator.py
│   │   └── schemas.py
│   │
│   ├── matcher/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── chroma_client.py
│   │   ├── zone_discipline_pruner.py
│   │   ├── hybrid_search.py
│   │   ├── context_ranker.py
│   │   └── explanation.py
│   │
│   ├── confidence/
│   │   ├── __init__.py
│   │   ├── scorer.py
│   │   ├── routing.py
│   │   └── adjustments.py
│   │
│   ├── schedule/
│   │   ├── __init__.py
│   │   ├── xer_parser.py
│   │   ├── xml_parser.py
│   │   ├── cpm_guard.py
│   │   ├── actuals_writer.py
│   │   ├── exporter.py
│   │   └── planned_actual.py
│   │
│   ├── audit/
│   │   ├── __init__.py
│   │   ├── hash_chain.py
│   │   ├── metadata_verification.py
│   │   ├── synthetic_media_gate.py
│   │   ├── evidence_linker.py
│   │   └── audit_log.py
│   │
│   └── models/
│       ├── __init__.py
│       ├── ingestion.py
│       ├── extraction.py
│       ├── crosscheck.py
│       ├── matcher.py
│       ├── review.py
│       ├── schedule.py
│       └── audit.py
│
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   │
│   ├── public/
│   │   └── favicon.svg
│   │
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       │
│       ├── api/
│       │   └── client.js
│       │
│       ├── components/
│       │   ├── ConfidenceBadge.jsx
│       │   ├── FieldUpdateCard.jsx
│       │   ├── EvidencePanel.jsx
│       │   ├── MetadataStatus.jsx
│       │   ├── SyntheticMediaBadge.jsx
│       │   └── AuditLogTable.jsx
│       │
│       ├── pages/
│       │   ├── IncomingFieldUpdates.jsx
│       │   ├── ReviewTray.jsx
│       │   ├── ScheduleDashboard.jsx
│       │   ├── GanttView.jsx
│       │   └── AuditLog.jsx
│       │
│       ├── gantt/
│       │   ├── ForgeGantt.jsx
│       │   ├── plannedActualTheme.js
│       │   └── dependencyRenderer.js
│       │
│       └── review/
│           ├── OcrVlmComparison.jsx
│           ├── MatchExplanationPanel.jsx
│           ├── FieldAgreementHighlighter.jsx
│           └── ApproveRejectBar.jsx
│
├── data/
│   ├── sample_schedule/
│   │   ├── nrl_crude_tank.xer
│   │   ├── nrl_crude_tank.xml
│   │   ├── task_hierarchy.json
│   │   │
│   │   └── masters/
│   │       ├── zones.json
│   │       └── disciplines.json
│   │
│   ├── sample_media/
│   │   ├── voice/
│   │   │   └── pier14_concrete_completed.ogg
│   │   │
│   │   ├── images/
│   │   │   └── pier14_site_photo.jpg
│   │   │
│   │   ├── documents/
│   │   │   └── site_diary_page_01.png
│   │   │
│   │   └── synthetic/
│   │       └── ai_generated_sample.jpg
│   │
│   └── demo_scripts/
│       ├── field_updates.json
│       ├── ivr_demo_script.md
│       └── judge_demo_script.md
│
├── docs/
│   ├── FORGE_MODULE_PLAN.md
│   ├── WINNING_PRIORITY.md
│   ├── FORGE_PROJECT_MEMORY.md
│   ├── FORGE_REPO_STRUCTURE.md
│   ├── DEMO_SCRIPT.md
│   │
│   └── architecture/
│       ├── data_flow.md
│       ├── confidence_rules.md
│       └── cpm_guard_rules.md
│
├── scripts/
│   ├── seed_demo_data.py
│   ├── generate_task_embeddings.py
│   ├── run_telegram_bot.py
│   ├── validate_hash_chain.py
│   └── export_updated_schedule.py
│
├── storage/
│   ├── raw/
│   │   └── .gitkeep
│   │
│   ├── processed/
│   │   └── .gitkeep
│   │
│   └── exports/
│       └── .gitkeep
│
└── tests/
    ├── __init__.py
    ├── test_ingestion.py
    ├── test_extraction.py
    ├── test_crosscheck.py
    ├── test_matcher.py
    ├── test_confidence.py
    ├── test_cpm_guard.py
    ├── test_audit.py
    │
    └── fixtures/
        ├── sample_schedule.xer
        ├── sample_text_update.json
        ├── sample_voice_note.ogg
        └── sample_image.jpg
```

---

## Module-to-Folder Mapping

| Module | Primary Folder(s) |
|---|---|
| MOD-00 Demo Data & Project Scaffold | `data/`, `scripts/seed_demo_data.py` |
| MOD-01 Field Ingestion Gateway | `app/ingestion/`, `app/api/ingestion.py` |
| MOD-02 Multi-Modal Extraction Pipeline | `app/extraction/`, `app/api/extraction.py` |
| MOD-02 Dual-Source Cross-Check | `app/crosscheck/`, `app/api/crosscheck.py` |
| MOD-03 Hierarchical Semantic Matcher | `app/matcher/`, `app/api/matcher.py` |
| MOD-04 Confidence & Review Engine | `app/confidence/`, `app/api/review.py`, `frontend/src/review/` |
| MOD-05 Schedule Write-Back & CPM Guard | `app/schedule/`, `app/api/schedule.py` |
| MOD-06 Audit & Trust Layer | `app/audit/`, `app/api/audit.py` |
| MOD-07 Planner Dashboard & Gantt View | `frontend/src/pages/`, `frontend/src/gantt/` |
| MOD-08 IVR Offline Fallback | `app/ingestion/ivr_webhook.py` |
| MOD-11 Demo Script & Pitch Readiness | `docs/DEMO_SCRIPT.md`, `data/demo_scripts/` |

---

## Important Rules

1. Do not place hardcoded Gantt data inside `frontend/src/gantt/`.
   The Gantt view must always render from backend schedule data.

2. Do not place AI model weights inside the main repository unless required for demo portability.
   Use environment variables or local model paths.

3. Do not store real secrets in `.env`.
   Keep `.env.example` as the safe template.

4. Use `storage/` for runtime-generated files only.
   It should remain mostly empty in version control.

5. Use `data/sample_media/synthetic/` only for controlled demo evidence.
   The synthetic image is used to demonstrate the synthetic media gate.

---

## Recommended Root Files

| File | Purpose |
|---|---|
| `README.md` | Project overview, setup, demo instructions |
| `.gitignore` | Ignore environment files, storage artifacts, model weights |
| `.env.example` | Safe environment variable template |
| `requirements.txt` | Python dependencies |
| `pyproject.toml` | Optional modern Python packaging/config |
| `Makefile` | Common commands: run, test, seed, lint |
| `docker-compose.yml` | Backend, frontend, database, ChromaDB setup |

---

## Minimal Backend Flow

```text
Field Update
    ↓
app/ingestion/
    ↓
app/extraction/
    ↓
app/crosscheck/
    ↓
app/matcher/
    ↓
app/confidence/
    ↓
app/api/review.py
    ↓
app/schedule/
    ↓
app/audit/
    ↓
frontend dashboard + Gantt update
```

---

## Minimal Frontend Screen Mapping

| Screen | File |
|---|---|
| Incoming Field Updates | `frontend/src/pages/IncomingFieldUpdates.jsx` |
| Review Tray | `frontend/src/pages/ReviewTray.jsx` |
| Schedule Dashboard | `frontend/src/pages/ScheduleDashboard.jsx` |
| Gantt View | `frontend/src/pages/GanttView.jsx` |
| Audit Log | `frontend/src/pages/AuditLog.jsx` |

---
