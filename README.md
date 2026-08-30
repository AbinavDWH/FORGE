# FORGE — Field Operations Reconciliation & Gantt Engine

**Smart India Hackathon 2026 · Problem Statement SIH26122 · Sponsored by Oil India Limited**

FORGE converts informal field updates (voice notes, photos, text, IVR calls) into trusted, real-time project schedule progress without breaking CPM logic.

## The Problem

On large infrastructure sites like NRL Golaghat's 9 MMTPA expansion, ground crews report progress using trade slang, WhatsApp voice notes, and site diary photos. Office planners use rigid Primavera P6 / MS Project schedules. Junior engineers spend 30-40 hours/week manually reconciling these two worlds — hiding critical-path slippages and creating billing disputes.

## The Solution

FORGE bridges this gap with:

1. **Multi-Modal Ingestion** — Voice, text, photo, IVR (zero forms, zero WBS codes)
2. **AI Extraction** — Whisper ASR + RapidOCR + Pydantic LLM structuring
3. **Dual-Source Verification** — OCR vs VLM cross-check (OCR is always source of truth)
4. **Hierarchical Matching** — Zone/discipline pruning + RapidFuzz hybrid search
5. **3-Tier Confidence Routing** — Auto-commit (≥85%), Review (50-84%), Manual (<50%)
6. **CPM-Safe Write-Back** — Updates only actuals, validates dependencies
7. **Tamper-Evident Audit** — SHA-256 hash chain + synthetic media screening

## Quick Start

```bash
# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

- Backend API: http://127.0.0.1:8000/docs
- Frontend UI: http://127.0.0.1:5173

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, Pydantic |
| Frontend | React 19, Vite, Tailwind CSS |
| ASR | faster-whisper (local) |
| OCR | RapidOCR (ONNX, local) |
| VLM Verifier | Qwen2.5-VL / MiniCPM-V (optional, local) |
| Matching | RapidFuzz + hybrid search |
| Schedule | MS Project XML / Primavera P6 .xer |
| Audit | SHA-256 append-only hash chain |

## Project Structure

```
forge/
├── app/              # FastAPI backend
│   ├── api/          # REST endpoints
│   ├── ingestion/    # Field update capture
│   ├── extraction/   # Whisper + OCR + VLM + structurer
│   ├── crosscheck/   # OCR vs VLM comparison
│   ├── matcher/      # Hierarchical semantic matching
│   ├── confidence/   # 3-tier confidence routing
│   ├── schedule/     # XML parser + CPM guard + actuals writer
│   ├── audit/        # Hash chain + synthetic media gate
│   └── models/       # Pydantic data models
├── frontend/         # React dashboard
├── data/             # Sample schedule + demo media
├── storage/          # Runtime artifacts
├── tests/            # Test suite
└── scripts/          # Utility scripts
```

## Team

Built for SIH 2026 by Team FORGE.