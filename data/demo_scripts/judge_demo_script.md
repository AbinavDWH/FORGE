# FORGE — 60-Second Judge Demo Script

**Hackathon**: Smart India Hackathon 2026  
**Problem Statement ID**: SIH26122 (Sponsored by Oil India Limited)  
**Setting**: NRL 9 MMTPA Expansion Megaproject, Golaghat, Assam  

---

## 1. Problem Pitch (0:00 - 0:15)
> "On large megaprojects like the NRL expansion, ground supervisors report progress over WhatsApp voice notes and phone calls using site slang like 'Pier 14 concrete done'. Meanwhile, office planners work in formal Primavera and MS Project schedules. Junior engineers spend 30 to 40 hours a week manually mapping these notes. This lag causes delayed visibility into critical path delays and multi-crore billing disputes. FORGE solves this by building a real-time, deterministic bridge from field updates to enterprise schedules."

---

## 2. Field Ingestion & Extraction (0:15 - 0:30)
> "Watch this live: Rahul, the site supervisor, sends an informal Hinglish voice note: *'Sector B Pier 14 concrete pouring completed.'*
> FORGE's Multi-Modal Pipeline instantly transcribes it with Whisper, performs deterministic local OCR on the attached photo, validates GPS metadata, and runs our Synthetic Media Gate to screen against AI-generated fake progress photos."

---

## 3. Intelligent Matching & Review (0:30 - 0:45)
> "Our Hierarchical Semantic Matcher uses two-stage zone/discipline pruning plus RapidFuzz hybrid search to match the update to WBS activity `CIV-STR-014` with a 92% confidence score.
> Because it meets trust criteria, Priya, the project planner, sees the match explanation, cross-check verification, and evidence panel in her Review Tray. With one click, she approves."

---

## 4. CPM-Safe Write-Back & Audit Trail (0:45 - 1:00)
> "FORGE checks the CPM logic: Finish-to-Start predecessor `CIV-STR-013` (Rebar Inspection) is 100% complete, so the CPM Guard validates the update and writes actuals directly to the schedule XML.
> The Gantt chart dynamically shifts in real-time, and an append-only SHA-256 hash chain record is created. Contractor billing disputes are eliminated with immutable mathematical proof."

---

## Winning Checklist Reference
- [x] Zero forms / zero WBS codes for site workers
- [x] Dual-source OCR vs VLM cross-verification
- [x] Synthetic media screening
- [x] CPM dependency integrity guard
- [x] 100% dynamic Gantt view (no hardcoded bars)
- [x] SHA-256 tamper-evident audit trail
