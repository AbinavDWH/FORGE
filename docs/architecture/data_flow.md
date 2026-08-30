# FORGE — End-to-End Data Flow Architecture

```
                       [ Field Update Source ]
          (Telegram Voice / Photo / Text / IVR Call)
                             │
                             ▼
               [ MOD-01: Ingestion Gateway ]
             - Generates unique ingestion_id (e.g. ING-1042)
             - Saves raw media in storage/raw/
             - Extracts metadata manifest (GPS, EXIF, hashes)
                             │
                             ▼
          [ MOD-02: Multi-Modal Extraction Pipeline ]
             - Whisper ASR for voice / IVR audio
             - RapidOCR for photo / scanned diary (PRIMARY)
             - Local VLM (Qwen2.5-VL / MiniCPM-V) (SECONDARY VERIFIER)
             - Field-level comparator (OCR ↔ VLM agreement)
             - Pydantic structurer → standardized JSON
                             │
                             ▼
         [ MOD-03: Hierarchical Semantic Matcher ]
             - Stage 1: Zone & Discipline rule-based pruning
             - Stage 2: Dense embedding & RapidFuzz hybrid search
             - Stage 3: Contextual ranking & boost
             - Generates match explanation
                             │
                             ▼
           [ MOD-04: Confidence & Review Engine ]
             - Base = 0.6 * MatchScore + 0.4 * ExtractionConfidence
             - Adjustments for GPS, EXIF, cross-check, synthetic media
             - 3-Tier Routing:
                 • ≥ 85%: Auto-Commit to Schedule
                 • 50% - 84%: Manager Review Tray
                 • < 50%: Flag as Unplanned / Manual
                             │
           ┌─────────────────┴─────────────────┐
           ▼                                   ▼
 [ Auto-Commit (≥85%) ]            [ Manager Review Tray (50-84%) ]
           │                         - Side-by-side OCR vs VLM view
           │                         - Match explanation & confidence
           │                         - 1-Click Approve / Reject / Edit
           │                                   │
           └─────────────────┬─────────────────┘
                             │ (Approved)
                             ▼
        [ MOD-05: Schedule Write-Back & CPM Guard ]
             - Validates Finish-to-Start predecessor completeness
             - Blocks out-of-order progress updates
             - Updates actuals only (ActualStart, ActualFinish, % Complete)
             - Preserves planned baseline dates & float
                             │
                             ▼
               [ MOD-06: Audit & Trust Layer ]
             - Appends immutable block to SHA-256 hash chain
             - Links actor, timestamp, task, confidence, evidence
             - Captures synthetic media screening & cross-check status
                             │
                             ▼
        [ MOD-07: Planner Dashboard & Gantt View ]
             - Live Planned vs Actual visual reconciliation
             - Real-time Gantt bar updates (zero hardcoding)
             - Tamper-evident audit chain inspection
```
