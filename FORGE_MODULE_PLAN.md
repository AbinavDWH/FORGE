FORGE_MODULE_PLAN.md

Project Name: FORGE — Field Operations Reconciliation & Gantt Engine
Hackathon: Smart India Hackathon 2026
Problem Statement ID: SIH26122
Sponsored By: Oil India Limited

Real-World Context
- Numaligarh Refinery Limited, Golaghat, Assam
- Expansion from 3 MMTPA to 9 MMTPA
- Remote site conditions
- Connectivity dead zones
- Contractor billing proof requirements
- Large infrastructure scheduling using Primavera P6 / MS Project

1. Purpose
This single document contains the complete module-wise plan for building FORGE.
FORGE must prove:
Messy, informal ground-site updates can be converted into trusted, real-time project schedule progress without breaking official schedule logic.
FORGE is not a generic project management app.
It is a Planning-to-Execution Bridge.

2. Winning Goal
The judges must clearly understand:
- The problem is real.
- The solution is practical.
- The system saves manual reconciliation effort.
- The system is trustworthy.
- The system works with real project schedules.
- The solution is demo-ready.

3. Core Winning Flow
FORGE must demonstrate this complete flow:
Field update arrives
   ↓
System extracts meaningful project data
   ↓
System cross-verifies extraction (OCR vs VLM for images)
   ↓
System matches update to schedule task
   ↓
System shows confidence
   ↓
Manager reviews if needed
   ↓
Schedule actual progress updates
   ↓
Planned vs Actual becomes visible
   ↓
Audit record is created
This is the Minimum Winning Experience.

4. Strict Rules
Must Follow
- Simple field input
- Voice, text, photo, IVR support
- Confidence scoring
- Human-in-the-loop review
- CPM dependency protection
- Tamper-evident audit trail
- Real schedule response
- Offline-tolerant design
- FOSS-first stack
- OCR as primary image extraction, VLM only as secondary verifier
- Synthetic media screening for image evidence

Must Not Do
- No fake or hardcoded Gantt bars
- No AI claims of 100% accuracy
- No complex field forms
- No forcing field users to select WBS codes
- No blind automatic schedule writes
- No breaking of task dependencies
- No VLM-based OCR as primary OCR if it risks hallucination
- No VLM output overwriting OCR source of truth
- No auto-commit when OCR and VLM disagree
- No AI-generated image accepted as evidence without review
- No unnecessary dashboards or admin panels
- No buzzword-heavy blockchain claims

5. Module Overview
| Module ID | Module Name | Priority | Purpose |
|---|---|---|---|
| MOD-00 | Demo Data & Project Scaffold | Priority 1 | Prepare base project, sample schedule, demo dataset |
| MOD-01 | Field Ingestion Gateway | Priority 1 | Capture informal field updates easily |
| MOD-02 | Multi-Modal Extraction Pipeline | Priority 1 | Convert voice/photo/text into structured JSON + cross-verify |
| MOD-03 | Hierarchical Semantic Matcher | Priority 1 | Match field update to correct WBS task |
| MOD-04 | Confidence & Review Engine | Priority 2 | Show confidence and enable manager approval |
| MOD-05 | Schedule Write-Back & CPM Guard | Priority 3 | Update schedule safely without breaking logic |
| MOD-06 | Audit & Trust Layer | Priority 2 | Create tamper-evident proof for every update |
| MOD-07 | Planner Dashboard & Gantt View | Priority 3 | Show Planned vs Actual and live schedule |
| MOD-08 | IVR Offline Fallback | Priority 4 | Enable updates from zero-internet areas |
| MOD-09 | Butterfly Effect Engine | Priority 5 | Suggest corrective actions after delay |
| MOD-10 | Shadow Schedule | Priority 5 | Use historical learning for future planning |
| MOD-11 | Demo Script & Pitch Readiness | Priority 1 | Prepare 60-second winning demo |

6. Module Details

MOD-00 — Demo Data & Project Scaffold
Purpose
Create a realistic demo environment with sample schedule, tasks, zones, disciplines, and dependencies.
Why It Matters
Without realistic demo data, the system will feel fake.
Judges must see a believable infrastructure project.
Recommended Demo Scenario
Construction of a Crude Oil Storage Tank at NRL Golaghat
Sample WBS Areas
Civil, Structural, Piping, Electrical, Instrumentation, Insulation, Testing & Commissioning
Sample Zones
Zone A, Zone B, Tank Farm, Pipeline Corridor, Pump Room, Substation
Sample Tasks
Excavation, PCC, RCC, Shuttering, Reinforcement, Concrete Pouring, Curing, Equipment Foundation, Pipe Spool Erection, Hydro Testing, Cable Tray Installation, Insulation
Deliverables
- Sample `.xer` or `.xml` schedule
- Task hierarchy JSON
- Zone and discipline master data
- Sample field update scripts
- Sample photos / scanned diary pages (including one synthetic/AI-generated sample for the screening demo)
- Demo database setup
Acceptance Criteria
[ ] Sample schedule has at least 20–50 tasks
[ ] Tasks have dependencies
[ ] Tasks have planned start and finish
[ ] Tasks have WBS codes
[ ] At least 5 demo field updates are ready
[ ] One sample AI-generated image is ready to test the synthetic media gate
[ ] Demo scenario is easy to explain in 60 seconds
Dependencies
None. This is the first module.
Risks
- Demo data too complex
- Too many tasks confuse the team
- Schedule not realistic
Rule
Keep demo data realistic but limited.

MOD-01 — Field Ingestion Gateway
Purpose
Allow site supervisors to send updates with zero friction.
Core Principle
Field users should not use forms, dropdowns, or WBS codes.
Supported Inputs
Telegram voice note, Telegram text message, Site photo, Scanned site diary page, IVR call recording
Features
- Telegram bot integration
- Media upload support
- Offline queue placeholder
- Metadata capture
- Ingestion ID generation
- Raw payload storage
Metadata Capture
For every incoming update, capture:
{
  "ingestion_id": "string",
  "source": "telegram | ivr | web_upload",
  "media_type": "voice | text | image | document",
  "received_at": "timestamp",
  "device_id": "string",
  "gps_coords": "string",
  "exif_present": true,
  "original_sha256": "string",
  "compressed_sha256": "string",
  "capture_timestamp": "timestamp"
}
Important Rule
If image metadata is missing or suspicious:
- Do not reject immediately
- Reduce confidence score
- Flag for review
Deliverables
- Telegram bot endpoint
- Media receiver API
- Ingestion table/model
- Metadata manifest generator
- Simple upload fallback UI
Acceptance Criteria
[ ] Supervisor can send voice note
[ ] Supervisor can send text
[ ] Supervisor can send photo
[ ] Each update receives unique ID
[ ] Metadata is captured
[ ] Raw file is stored
[ ] Update appears in processing queue
Dependencies
MOD-00
Risks
- Telegram bot setup delays
- Media handling failures
- Metadata not captured properly
Rule
Input must feel as easy as sending a WhatsApp message.

MOD-02 — Multi-Modal Extraction Pipeline
Purpose
Convert informal field updates into structured project information and cross-verify image extraction.
Core Principle
OCR reads the text. LLM understands the text. A VLM only verifies — it never replaces OCR.
Extraction Sources
Voice notes, Text messages, Photos of site notes, Scanned site diaries, IVR call recordings
Technologies
- Whisper ASR for voice
- PaddleOCR or RapidOCR for image/document text (PRIMARY)
- Local VLM (Qwen2.5-VL / MiniCPM-V) as SECONDARY verifier for images
- LLM with structured output
- Pydantic schema validation
Extraction Output Schema
{
  "spatial_zone": "Zone B",
  "discipline": "Civil",
  "component": "Pier 14",
  "action": "Concrete pouring completed",
  "status": "Completed",
  "percent_complete": 100,
  "timestamp": "2026-08-28T10:30:00Z",
  "raw_text": "Sector B Pier 14 concrete pouring completed",
  "language_hint": "hinglish",
  "extraction_confidence": 0.86,
  "extraction_agreement": 0.9,
  "cross_check_status": "agreed"
}
Supported Language Style
Hinglish, Trade slang, Short incomplete sentences, Site terminology, Voice transcription errors
Example Field Input
"Sector B Pier 14 concrete pouring done."
Expected Structured Output
Zone: Sector B / Zone B, Discipline: Civil, Component: Pier 14, Action: Concrete pouring, Status: Completed, Percent Complete: 100

Dual-Source Verification (Image Updates Only)
Flow:
Image
  ↓
Primary: PaddleOCR/RapidOCR → raw text → structured JSON A (source of truth)
  ↓
Secondary: local VLM → structured JSON B (verifier only)
  ↓
Field-level comparator (fuzzy-normalized)
  ↓
agreement_score + cross_check_status
Rules:
- OCR output is always the source of truth.
- VLM output never overwrites OCR output.
- Normalize before comparing (e.g., "Concrete pouring" == "Concrete pour" via RapidFuzz).
- If VLM is unavailable, run in single_source mode with a small confidence penalty.
Comparator Output Schema:
{
  "ingestion_id": "ING-1042",
  "ocr_extraction": {...},
  "vlm_extraction": {...},
  "field_agreement": {
    "component": "match",
    "action": "match",
    "status": "match",
    "percent_complete": "mismatch"
  },
  "agreement_score": 0.85,
  "cross_check_status": "partial_mismatch",
  "source_of_truth": "ocr"
}
Build note: Build dual-source verification only after the core OCR extraction pipeline works. For the demo, compare only 3 fields: component, action, status.

Guardrails
- Do not invent missing fields
- Mark uncertain fields as null
- Do not use VLM as primary OCR if it can hallucinate
- VLM may only verify, never overwrite OCR
- Always keep raw input for audit
Deliverables
- Whisper transcription service
- OCR service
- VLM verification service
- Field-level comparator
- Structured extraction prompt
- Pydantic schema
- Extraction confidence score
- Extracted JSON storage
Acceptance Criteria
[ ] Voice note converts to text
[ ] Text message extracts structured fields
[ ] OCR reads scanned diary text
[ ] LLM returns valid JSON
[ ] Missing fields are not invented
[ ] Extraction confidence is visible
[ ] Raw input and extracted output are linked
[ ] Image updates run OCR primary extraction
[ ] VLM cross-check runs when enabled
[ ] Comparator produces agreement score
[ ] OCR remains source of truth on disagreement
[ ] single_source fallback works when VLM unavailable
Dependencies
MOD-01
Risks
- Poor transcription of noisy site audio
- OCR quality on handwritten notes
- LLM overconfidence
- Inconsistent zone names
- VLM disagreement confusion
Rule
Extraction must be explainable.

MOD-03 — Hierarchical Semantic Matcher
Purpose
Match informal field update to the correct schedule task.
Why It Matters
This is one of the most important winning areas.
The system must not blindly search all tasks.
It must narrow down intelligently.
Matching Context
Spatial zone, Discipline, Component, Activity type, Timestamp, Previous updates
Matching Strategy
Stage 1: Rule-Based Pruning
Filter tasks by Zone, Discipline.
Example: Update: "Pier 14 shuttering removed" → Prune to: Civil + Pier 14 related tasks
Stage 2: Hybrid Search
Use Dense vector similarity using ChromaDB, Lexical fuzzy matching using RapidFuzz
Stage 3: Context Ranking
Boost score if: Component matches, Activity verb matches, Task is currently active, Previous updates relate to same component, Task sequence is valid
Matcher Output Schema
{
  "ingestion_id": "string",
  "matched_task_id": "CIV-STR-014",
  "task_name": "Pier 14 Concrete Work",
  "wbs_code": "CIV-STR-014",
  "match_score": 0.92,
  "match_reason": "Zone B + Civil + Pier 14 + concrete activity",
  "alternative_matches": [
    { "task_id": "CIV-STR-015", "task_name": "Pier 14 Curing", "match_score": 0.71 }
  ]
}
Deliverables
- Task embedding generator
- ChromaDB collection
- Zone/discipline filter
- Fuzzy matching utility
- Match ranking logic
- Match explanation generator
Acceptance Criteria
[ ] Update is first filtered by zone and discipline
[ ] Matching returns ranked candidates
[ ] Top match has explanation
[ ] Alternative matches are visible
[ ] Unrelated tasks are not strongly matched
[ ] Matching works with small demo schedule
[ ] Matching result is stored
Dependencies
MOD-00, MOD-02
Risks
- Wrong task selected due to similar names
- Too many candidate tasks
- Poor embedding quality
- No explainability
Rule
Judges must understand why a task was matched.

MOD-04 — Confidence & Review Engine
Purpose
Prevent overconfident AI and enable human control.
Core Principle
FORGE supports planners. It does not replace them.
Confidence Factors
Confidence score should depend on:
- Extraction clarity
- Matcher score
- Metadata quality
- Dependency validity
- Evidence availability
- Field update completeness
- Extraction cross-verification agreement (OCR vs VLM)
- Synthetic media screening result
Example Confidence Logic
Base Confidence = 0.6 * matcher_score + 0.4 * extraction_confidence
Then apply adjustments:
- Missing GPS: reduce confidence
- Missing EXIF: reduce confidence
- Hash mismatch: reduce confidence significantly
- Out-of-order dependency: reduce confidence
- Clear component match: increase confidence
- Photo evidence present: increase confidence
- OCR and VLM agree on all key fields: increase confidence (+5 to +10)
- Partial mismatch on 1 non-critical field: cap confidence at 84 (force review)
- Critical mismatch (status / percent_complete / component): cap confidence at 60, flag "cross-verification conflict"
- VLM unavailable (single_source): small penalty, mark in review tray
- Medium ai_generation_risk: cap confidence below auto-commit
- High ai_generation_risk: block evidence, force review/reject
3-Tier Confidence Routing
| Confidence | Action |
|---|---|
| 85% and above | Auto-commit to schedule |
| 50% to 84% | Send to Manager Review Tray |
| Below 50% | Mark as unplanned / manual handling |
Review Tray Requirements
Manager should see:
- Original field update
- Transcribed text
- Extracted fields
- Matched task
- Confidence score
- Match explanation
- Metadata status
- Cross-check status (OCR vs VLM)
- Side-by-side OCR vs VLM extraction view
- Matched fields highlighted green
- Mismatched fields highlighted amber/red
- Synthetic media screening result
- Photo evidence
- Approve button
- Reject button
- Correct task option
Deliverables
- Confidence scoring service
- Confidence explanation
- Review tray UI
- Approve/reject API
- Task correction API
- Routing logic
Acceptance Criteria
[ ] Every update has a confidence score
[ ] Confidence is visible in UI
[ ] High confidence updates auto-commit
[ ] Medium confidence updates go to review
[ ] Low confidence updates are flagged
[ ] Manager can approve or reject
[ ] Manager can correct matched task
[ ] Missing metadata reduces confidence
[ ] Cross-check disagreement prevents auto-commit
[ ] Review tray shows OCR vs VLM comparison
[ ] Mismatched fields are visually highlighted
Dependencies
MOD-02, MOD-03
Risks
- Confidence score looks random
- Review tray is too complicated
- Auto-commit happens without trust signals
Rule
The AI must know when it is unsure.

MOD-05 — Schedule Write-Back & CPM Guard
Purpose
Update the official schedule safely without breaking CPM logic.
Core Principle
FORGE must feel like an enterprise bridge, not a toy dashboard.
Supported Schedule Formats
`.xer` for Primavera P6, `.xml` for MS Project
Allowed Updates
Only update actuals: Actual Start, Actual Finish, Remaining Duration, % Complete, Progress status, Evidence reference, Last updated timestamp
Must Not Change
Baseline dates unless explicitly approved, Original planned logic, Dependency relationships, Float calculations, Critical path structure
CPM Guard Rules
Rule 1: Dependency Order — If Task B depends on Task A, Task B cannot be completed before Task A is complete.
Rule 2: Out-of-Sequence Detection — Example: Insulation cannot be marked complete before hydro-testing is complete. If invalid: Block auto-commit, Flag logic error, Send to review.
Rule 3: Actuals Only — Do not rewrite the entire schedule. Only apply field actuals.
Write-Back Output
Generate: Updated schedule file, Update diff, Changed task list, Planned vs Actual comparison
Deliverables
- `.xer` parser
- `.xml` parser
- Schedule update service
- Dependency validator
- Actuals writer
- Updated schedule exporter
- Planned vs Actual calculator
Acceptance Criteria
[ ] System parses sample schedule
[ ] Approved update changes actual progress
[ ] Dependencies are checked
[ ] Out-of-order updates are blocked
[ ] Baseline is preserved
[ ] Updated schedule is exportable
[ ] Gantt view reflects the update
[ ] Update does not randomly modify unrelated tasks
Dependencies
MOD-00, MOD-04
Risks
- `.xer` parsing complexity
- Dependency logic errors
- Accidental baseline modification
- Fake-looking schedule updates
Rule
The schedule must mathematically respond to updates.

MOD-06 — Audit & Trust Layer
Purpose
Create tamper-evident proof for every update.
Why It Matters
Contractor billing disputes happen because progress claims lack proof.
FORGE must provide: Who updated, What was updated, When it was updated, Which task was affected, What confidence was found, What evidence exists, Whether it was approved, Whether evidence passed synthetic media screening, Whether extraction was cross-verified.
Audit Block Schema
{
  "log_index": 1,
  "timestamp": "2026-08-28T10:35:00Z",
  "ingestion_id": "string",
  "wbs_activity_id": "CIV-STR-014",
  "action_performed": "Progress updated to 100%",
  "confidence_score": 0.92,
  "approved_by": "manager_id",
  "evidence_reference": "media_id",
  "metadata_status": "verified",
  "cross_check_status": "agreed",
  "ai_generation_risk": "low",
  "previous_hash": "string",
  "current_hash": "string"
}
Metadata Verification
For photos, verify: Original SHA-256 hash, Compressed SHA-256 hash, GPS coordinates, EXIF presence, Capture timestamp, Device ID, ai_generation_risk, c2pa_detected
Synthetic Media Gate
Run local AI-generation screening on every image:
- Camera EXIF signature check
- C2PA / Content Credentials scan
- Local FOSS detector score (DIRE / PatchCraft / ViT)
- Forensic heuristics (dimensions, sensor noise, ELA)
Output ai_generation_risk (low/medium/high). High risk blocks evidence and flags "suspected synthetic media".
Hash Chain Logic
Each audit record stores Previous hash and Current hash. This creates an append-only proof chain.
Important Rule
Do not market this as blockchain. Call it: Append-only audit log, SHA-256 hash chain, Tamper-evident record.
Deliverables
- Audit log table
- Hash chain generator
- Metadata verification service
- Synthetic media screening service
- Evidence linking
- Audit viewer UI
- Audit export
Acceptance Criteria
[ ] Every approved update creates an audit record
[ ] Every rejected update creates an audit record
[ ] Audit log shows confidence
[ ] Audit log shows approver
[ ] Audit log shows evidence
[ ] Audit log shows cross-check status
[ ] Audit log shows synthetic media result
[ ] Hash chain is sequential
[ ] Missing metadata is visible
[ ] Audit record can be viewed from dashboard
Dependencies
MOD-01, MOD-04, MOD-05
Risks
- Audit log becomes too technical
- Metadata verification not demo-friendly
- Hash chain implementation errors
Rule
Audit proof must be simple enough for judges to understand.

MOD-07 — Planner Dashboard & Gantt View
Purpose
Show the result of reconciliation clearly.
Core Screens
Screen 1: Incoming Field Updates — Show: Raw update, Source, Time, Extracted text, Status
Screen 2: Review Tray — Show: Matched task, Confidence, Evidence, OCR vs VLM comparison, Synthetic media result, Approve / Reject, Correct match
Screen 3: Schedule Dashboard — Show: Planned vs Actual, Task status, Delayed tasks, Updated tasks, Critical tasks
Screen 4: Gantt View — Show: Planned bars, Actual progress, Updated dates, Dependencies, Critical path highlight if possible
Screen 5: Audit Log — Show: Update history, Confidence, Approver, Evidence, Hash chain status, Cross-check status
UI Rules
- No hardcoded Gantt bars
- Gantt must update from real data
- Keep dashboard simple
- Avoid too many analytics widgets
- Show confidence clearly
- Show review status clearly
Technology
React, Frappe Gantt, FastAPI backend, REST APIs
Deliverables
- Dashboard layout
- Review tray UI
- Gantt component
- Planned vs Actual view
- Audit viewer
- Live update refresh
Acceptance Criteria
[ ] Dashboard shows field update arrival
[ ] Review tray works
[ ] Approval updates schedule
[ ] Gantt changes after approval
[ ] Planned vs Actual is visible
[ ] Audit log is accessible
[ ] No static fake bars exist
[ ] Demo flow is visible in under 60 seconds
Dependencies
MOD-04, MOD-05, MOD-06
Risks
- UI becomes too complex
- Gantt is not dynamic
- Too many screens distract judges
Rule
The dashboard must prove reconciliation, not decorate the product.

MOD-08 — IVR Offline Fallback
Purpose
Enable updates from remote dead zones where internet is unavailable.
Why It Matters
This is highly relevant for NRL Golaghat and remote expansion zones.
Flow
Supervisor calls FORGE toll-free number
   ↓
Speaks update
   ↓
Telephony system records audio
   ↓
Audio enters Whisper pipeline
   ↓
Same extraction and matching flow continues
Example IVR Update
"Sector B Pier 14 concrete pouring completed."
Technology Options
Twilio, Exotel, Any telephony webhook provider
Deliverables
- IVR number webhook
- Call recording storage
- Audio-to-pipeline connector
- Call source metadata capture
- IVR demo script
Acceptance Criteria
[ ] A phone call can create an update
[ ] Call recording is stored
[ ] Audio enters extraction pipeline
[ ] Update appears in dashboard
[ ] Source is marked as IVR
[ ] Demo works without smartphone internet
Dependencies
MOD-01, MOD-02
Risks
- Telephony setup complexity
- Call quality affects transcription
- Demo becomes too long
Rule
IVR is a powerful differentiator, but core reconciliation must work first.

MOD-09 — Butterfly Effect Engine
Purpose
Show prescriptive micro-rescheduling after a delay.
Priority
Advanced feature. Build only after core reconciliation is stable.
Concept
FORGE should not only report delays. It should suggest corrective actions.
Example
Rain halts Zone A concrete work. FORGE checks CPM impact. FORGE says:
"Rain delays L1 handover by 4 days. Move Crew 3 to Zone B piping now to bypass critical path."
Lightweight Demo Version
For hackathon demo, do not overbuild. Use: Delay event, Affected task, Dependency impact, Simple suggestion.
Deliverables
- Delay event input
- Impact calculation
- Suggestion card
- Dashboard alert
Acceptance Criteria
[ ] Delay event is visible
[ ] Affected task is visible
[ ] Impact on milestone is shown
[ ] Suggested action is shown
[ ] Suggestion does not break CPM
[ ] Feature does not distract from core demo
Dependencies
MOD-05, MOD-07
Risks
- Overcomplicated simulation
- Unrealistic suggestions
- Judges think it is fake
Rule
Keep it simple, believable, and connected to CPM.

MOD-10 — Shadow Schedule
Purpose
Use historical ground-truth data to improve future planning.
Priority
Future / optional feature.
Concept
FORGE learns from actual contractor performance and creates a more realistic future schedule.
Example
Historical data shows Contractor X underestimates piping by 15% in winter. FORGE adjusts future shadow schedule accordingly.
Hackathon Usage
Do not build deeply unless all core modules are strong. Use only as a pitch slide or mock insight.
Deliverables
- Historical variance example
- Shadow schedule mockup
- Future bidding use case
Acceptance Criteria
[ ] Concept is easy to explain
[ ] It uses historical data logically
[ ] It does not distract from core flow
[ ] It is not required for minimum winning demo
Dependencies
Core modules complete
Risks
- Too advanced
- Too speculative
- Takes time from core reconciliation
Rule
Mention only if core flow is already strong.

MOD-11 — Demo Script & Pitch Readiness
Purpose
Convert the technical build into a clear 60-second winning demo.
Demo Flow
Step 1: Field Update — Supervisor sends: "Sector B Pier 14 concrete pouring completed." Or calls IVR from a dead zone.
Step 2: Extraction — FORGE extracts: Zone, Discipline, Component, Action, Status, % Complete. OCR and VLM cross-check agree. Metadata verified. No synthetic media.
Step 3: Matching — FORGE matches to: CIV-STR-014 — Pier 14 Concrete Work. Confidence: 92%.
Step 4: Review — Manager sees: Extracted data, Match reason, Confidence, Cross-check status, Evidence, Metadata status.
Step 5: Approval — Manager clicks: Approve.
Step 6: Schedule Update — Schedule actual progress updates.
Step 7: Planned vs Actual — Dashboard shows: Planned progress, Actual progress, Updated task, Delay impact.
Step 8: Audit Proof — FORGE creates: Timestamp, Approver, Confidence, Evidence, Cross-check status, SHA-256 hash chain entry.
Pitch Opening Rule
Always explain pain first:
"On large infrastructure sites, ground teams report progress using voice notes, slang, photos, and phone calls. Office planners use formal Primavera schedules. Today, junior engineers spend hours manually reconciling these two worlds. This delay hides critical-path slippages and creates billing disputes."
Then explain FORGE.
Deliverables
- 60-second demo script
- Judge-facing storyboard
- One-slide problem statement
- Live demo checklist
- Backup video
- Pitch speaker notes
Acceptance Criteria
[ ] Demo is under 60 seconds
[ ] Problem is explained before technology
[ ] All 8 winning points are visible
[ ] No fake schedule is used
[ ] No overconfident AI claims
[ ] Manager review is visible
[ ] Audit proof is visible
Dependencies
All core modules
Risks
- Demo too technical
- Demo too long
- Team explains architecture before problem
Rule
The demo must feel real, simple, and trustworthy.

7. Build Phases

Phase 1 — Core Reconciliation MVP
Goal
Prove the main winning flow:
Field update → Extraction → Matching → Confidence → Review → Schedule update → Audit
Modules
MOD-00, MOD-01, MOD-02, MOD-03, MOD-04, MOD-05, MOD-06, MOD-07
Exit Criteria
[ ] Text update works
[ ] Photo update works
[ ] Voice update works
[ ] Matching shows confidence
[ ] Manager can approve
[ ] Schedule updates
[ ] Gantt updates
[ ] Audit log is generated

Phase 2 — Field Usability & Offline Readiness
Goal
Make FORGE realistic for remote sites.
Modules
MOD-08, Offline queue placeholder, Better Telegram experience, Metadata capture improvements, Dual-source cross-check, Synthetic media gate
Exit Criteria
[ ] IVR call creates update
[ ] Source type is visible
[ ] Low-bandwidth image upload works
[ ] Missing metadata reduces confidence
[ ] Field input remains simple
[ ] Dual-source cross-check works for image updates
[ ] Disagreement routes to review tray
[ ] AI-generated sample image is flagged/blocked

Phase 3 — Advanced Value
Goal
Add differentiators only after core is stable.
Modules
MOD-09, MOD-10
Exit Criteria
[ ] Butterfly suggestion is believable
[ ] Shadow schedule is explained simply
[ ] Advanced features do not distract from core

8. Recommended Team Allocation

L5 Builder #1 — AI / Backend
Responsibilities: Whisper ASR, PaddleOCR / RapidOCR, VLM cross-check, Structured extraction, ChromaDB matcher, Confidence scoring, Matching explanation
Owns: MOD-02, MOD-03, Part of MOD-04

L5 Builder #2 — Frontend / Field Experience
Responsibilities: Telegram bot, Field upload flow, Dashboard UI, Review tray UI, Gantt integration, IVR webhook
Owns: MOD-01, MOD-07, MOD-08

L6 Architect — System Logic / Trust
Responsibilities: Schedule parsing, CPM validation, Write-back logic, Audit hash chain, Metadata verification, Synthetic media screening, Enterprise safety
Owns: MOD-00, MOD-05, MOD-06, Part of MOD-04

Pitcher / Business Story
Responsibilities: Problem framing, Demo script, NRL use case, Judge-facing explanation, Business value matrix
Owns: MOD-11

9. Milestone Plan

Milestone 1 — Foundation Ready
Target: Project setup and demo data ready.
Deliverables: Repository setup, Sample schedule, Task hierarchy, Demo scenario, Basic API skeleton
Completion Proof: Team can show a believable NRL-style schedule.

Milestone 2 — Extraction Ready
Target: Field update becomes structured JSON.
Deliverables: Whisper transcription, OCR extraction, VLM cross-check, Structured LLM extraction, Extraction confidence
Completion Proof: A voice note becomes structured project data; image cross-check runs.

Milestone 3 — Matching Ready
Target: Structured update matches to schedule task.
Deliverables: Task embeddings, Zone/discipline pruning, Hybrid search, Match explanation
Completion Proof: "Pier 14 concrete pouring" matches the correct Pier 14 civil task.

Milestone 4 — Trust Ready
Target: Confidence and review work.
Deliverables: Confidence score, Review tray, Approve/reject, Metadata-based confidence adjustment, Cross-check comparison view
Completion Proof: Manager can approve or reject an AI suggestion and see OCR vs VLM comparison.

Milestone 5 — Schedule Ready
Target: Approved update changes real schedule.
Deliverables: Schedule parser, CPM guard, Actuals update, Updated schedule export
Completion Proof: Approval changes actual progress and Gantt reflects it.

Milestone 6 — Audit Ready
Target: Every update has proof.
Deliverables: Audit log, Hash chain, Evidence link, Metadata status, Synthetic media result, Cross-check status
Completion Proof: Judges can see who approved what and with what evidence.

Milestone 7 — Demo Ready
Target: 60-second demo is smooth.
Deliverables: Final UI, Demo data, Demo script, Backup flow, Pitch slides
Completion Proof: The team can demonstrate all 8 winning points without confusion.

10. Minimum Winning Experience Checklist
Before final demo, verify:
[ ] A field update arrives
[ ] The system extracts meaningful project data
[ ] The system cross-verifies image extraction (OCR vs VLM)
[ ] The system matches it to a possible schedule task
[ ] The system shows confidence
[ ] A manager can review if needed
[ ] The schedule actual progress updates
[ ] The planned vs actual difference becomes visible
[ ] An audit record is created

11. Red Flag Checklist
Before presenting, confirm none of these exist:
[ ] Schedule bars are static/hardcoded
[ ] AI claims 100% accuracy
[ ] Field input requires WBS code selection
[ ] Demo depends on manual backend intervention
[ ] No confidence score is visible
[ ] No human review step exists
[ ] No audit trail exists
[ ] No metadata verification exists
[ ] AI-generated image accepted as valid field evidence
[ ] Single-source image extraction auto-commits without cross-verification
[ ] VLM output overwrites OCR source of truth
[ ] Team explains technology before problem
[ ] Too many features distract from core flow
[ ] Gantt chart does not respond to updates
[ ] Dependencies can be broken silently
[ ] Update has no evidence link

12. Suggested Repository Structure
forge/
 ├── app/
 │   ├── api/
 │   ├── core/
 │   ├── ingestion/
 │   ├── extraction/
 │   ├── crosscheck/
 │   ├── matcher/
 │   ├── confidence/
 │   ├── schedule/
 │   ├── audit/
 │   └── models/
 ├── frontend/
 │   ├── components/
 │   ├── pages/
 │   ├── gantt/
 │   └── review/
 ├── data/
 │   ├── sample_schedule/
 │   ├── sample_media/
 │   └── demo_scripts/
 ├── docs/
 │   ├── FORGE_MODULE_PLAN.md
 │   ├── WINNING_PRIORITY.md
 │   └── DEMO_SCRIPT.md
 ├── tests/
 ├── scripts/
 └── README.md

13. Final Execution Rule
If any module, screen, or task does not help prove that FORGE can convert messy field updates into trusted schedule progress, postpone it.
FORGE wins through:
- Clear problem understanding
- Strong core reconciliation
- Trusted AI behavior
- Schedule intelligence
- Smooth demo
- Practical enterprise value