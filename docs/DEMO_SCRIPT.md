# FORGE: 60-Second Demo Script

**Preparation:**
- Run `./scripts/seed_demo_data.py` to reset the schedule and audit chain.
- Start backend (`uvicorn app.main:app`) and frontend (`npm run dev`).
- Have a sample field photo or voice note ready.

**1. Context Setting (10s)**
- Display the problem statement slide: "Bridging the gap between informal field updates and formal P6/MS Project schedules."
- Explain that manual reconciliation takes 30+ hours/week.

**2. Ingestion (10s)**
- Navigate to the FORGE web interface (or show Telegram integration).
- Upload a field update (e.g., photo of a whiteboard/diary or a voice note like "Tank 4 base plate welding complete").
- Emphasize: *No forms, no manual WBS codes required.*

**3. Extraction (10s)**
- Show the extraction result on the dashboard.
- Point out how Whisper and OCR (RapidOCR) pull out the raw text.
- Highlight the VLM structuring that converts the unstructured text into JSON (Discipline, Zone, Status).

**4. Matching & Confidence (10s)**
- Show how RapidFuzz mapped the extracted text to a specific MS Project task ID.
- Note the confidence score. Explain the 3-tier system (Auto-commit, Review, Manual).
- In this demo, point out it landed in the "Review Tray" (50-84% confidence).

**5. Review & Approval (10s)**
- Log in as the Manager/Planner.
- Open the Review Tray.
- Click **Approve** on the matched task.

**6. Schedule Update & Audit (10s)**
- Switch to the Gantt view to show the task progress updated safely (only Actuals updated, CPM logic intact).
- Show the Audit log UI or run `./scripts/validate_hash_chain.py` in terminal.
- Highlight the SHA-256 append-only hash chain entry proving the update's integrity.

*End Demo*
