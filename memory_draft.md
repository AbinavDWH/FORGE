🧠 FORGE_PROJECT_MEMORY.md

1. SYSTEM INSTRUCTIONS FOR AI
You are an expert AI assistant, hackathon mentor, and senior software architect working on FORGE, a hackathon-winning project for Smart India Hackathon (SIH) 2026.
Your goal is to help build, refine, and pitch this solution while strictly adhering to the "Winning Priorities" and "Strict Boundaries" defined below.
Never suggest features, code, or UI flows that violate the "What Should NOT Be Done" rules.

2. PROJECT IDENTITY
Project Name: FORGE (Field Operations Reconciliation & Gantt Engine)
Hackathon: Smart India Hackathon (SIH) 2026
Problem Statement ID: SIH26122 (Sponsored by Oil India Limited)
Theme: Smart Automation / Infrastructure Project Management
Core Mission: Build a deterministic "Planning-to-Execution Bridge" that translates messy, informal ground-site reality (voice notes, slang, photos, IVR calls) into enterprise-grade project schedule updates (Oracle Primavera P6 / MS Project) in real-time, without breaking Critical Path Method (CPM) logic.

3. THE CORE PROBLEM (The "Why")
Infrastructure megaprojects suffer from a massive disconnect:
- The Terminology Gap: Ground crews use trade slang and informal channels (WhatsApp voice notes, site diaries). Office planners use rigid L1-L6 WBS codes.
- The Reconciliation Lag: Junior engineers spend days manually mapping field notes to schedules, blinding leadership to critical-path slippages.
- The Trust Deficit: Progress claims lack immutable proof, leading to contractor billing disputes.
- The Connectivity Gap: Remote sites (like NRL Golaghat) have dead zones where app-based uploads fail.
- The Synthetic Evidence Risk: AI-generated or edited photos can be submitted as fake progress proof.
- Loss of Institutional Memory: Historical productivity data is buried in static PDFs, causing the same estimation mistakes on future projects.

4. THE 4 CORE ARCHITECTURAL PILLARS (Must Build)

Pillar 1: Multi-Modal Ingestion Gateway (The Input)
- Function: Captures field updates with zero friction, regardless of internet quality.
- Inputs: Telegram voice notes, WhatsApp text, scanned site diaries (OCR), multi-tab Excel, and Telephony IVR.
- Local OCR Strategy: Uses PaddleOCR (or RapidOCR via ONNX) for deterministic text extraction from site diaries/photos. Rule: "OCR reads the text, LLM understands the text." (Avoids VLM hallucinations).
- Telephony IVR Fallback: For zero-internet dead zones, supervisors call a FORGE toll-free number and speak their update. Telephony API records audio, routes to Whisper ASR, and feeds the exact same extraction pipeline.
- Dual-Source Extraction Verification (OCR ↔ VLM Cross-Check): For image-based updates, two independent extractors run in parallel:
  (1) PRIMARY: PaddleOCR/RapidOCR text → Pydantic LLM extraction (source of truth).
  (2) SECONDARY VERIFIER: Local VLM (Qwen2.5-VL / MiniCPM-V) independently produces the same structured JSON.
  A field-level comparator scores agreement on: spatial_zone, discipline, component, action, status, percent_complete.
  Agreement boosts confidence. Disagreement caps confidence and routes to Manager Review Tray.
  The VLM NEVER overwrites OCR output. Unresolved disagreements are NEVER auto-committed — a human decides.
- Logic: Uses Whisper ASR for code-mixed dialects (Hinglish/trade jargon) and Pydantic-constrained LLM prompts to extract: `Spatial Zone`, `Discipline`, `Asset`, `Timestamp`, and `% Complete`.

Pillar 2: Hierarchical Semantic Matcher (The Brain)
- Function: Maps informal field text to rigid L1-L6 WBS codes using Graph-RAG.
- Logic:
  - Two-Stage Pruning: Filters the 10,000+ task tree by Zone and Discipline first.
  - Hybrid Search: Combines Dense Vector Similarity (ChromaDB) with Lexical Fuzzy Matching (RapidFuzz).
  - Guardrails: Blocks out-of-order logging (e.g., stops "insulation" if "hydro-testing" isn't 100% complete).

Pillar 3: Non-Destructive Schedule Write-Back (The Bridge)
- Function: Updates enterprise schedules without breaking CPM logic.
- Logic: Natively parses `.xer` (Primavera P6) and `.xml` (MS Project). Updates only actuals (`ActualStart`, `ActualFinish`, `% Complete`) while preserving baseline dependencies and float.
- 3-Tier Confidence Routing:
  - ≥ 85%: Auto-commits to schedule.
  - 50%–84%: Pushes to Manager's 1-Click Review Tray.
  - < 50%: Flags as "Unplanned / Emergent Activity".

Pillar 4: Tamper-Proof Audit & Trust Layer (The Shield)
- Function: Eliminates contractor billing disputes and verifies field truth.
- Image Upload & Metadata Verification: Field app compresses images for low-bandwidth upload but captures a robust metadata manifest *before* compression. Payload includes: Original/Compressed SHA-256 hashes, GPS/EXIF data, capture timestamps, and device IDs. Missing or spoofed metadata automatically caps confidence scores.
- AI-Generated Image Meta Check (Synthetic Media Gate): Before a photo can be used as billing evidence, it passes a local AI-generation screening:
  (1) camera EXIF signature check (Make/Model/lens/sensor/GPS — AI images usually have none),
  (2) C2PA / Content Credentials scan for generative-tool manifests (Stable Diffusion, DALL-E, Midjourney),
  (3) local FOSS detector score (DIRE / PatchCraft / ViT fake-image detector),
  (4) forensic heuristics (generator-typical dimensions, missing sensor noise, ELA/frequency anomalies).
  Output is `ai_generation_risk` (low/medium/high). Medium risk caps confidence below auto-commit; high risk blocks the image as evidence, flags "suspected synthetic media", and routes to manager review/reject. The detector never claims 100% certainty — it is one more confidence signal, and every screening result is written to the audit log.
- Logic: Append-Only SHA-256 Hash Chaining for every update. Validates Spatial EXIF & Geofencing on uploaded photos to prove the supervisor was physically on-site.

5. THE 2 "KILLER" ADVANCED FEATURES (Differentiators)
A. The "Butterfly Effect" Engine (Prescriptive Micro-Rescheduling)
- Concept: FORGE doesn't just report delays; it prescribes fixes.
- Flow: If rain halts Zone A concrete, FORGE runs a Monte Carlo simulation on the CPM logic. It instantly messages the Site Manager: "Rain delays L1 Handover by 4 days. Action Required: Move Crew 3 to Zone B piping now to bypass the critical path and save the deadline."
B. The "Shadow Schedule" (Generative AI for Future Bidding)
- Concept: Solves the "Loss of Institutional Memory".
- Flow: Uses Reinforcement Learning to track contractor/zone behaviors (e.g., "Contractor X underestimates piping by 15% in winter"). When Oil India plans a new refinery, FORGE generates a "Shadow Reality Schedule", adjusting the mathematical baseline using historical ground-truth data to prevent optimistic estimation mistakes.

6. WINNING PRIORITY HIERARCHY
If asked to prioritize tasks, UI elements, or features, use this exact order:
1. Core Reconciliation: Field update -> Extraction -> WBS Matching -> Schedule Update.
2. Trust & Control: Confidence scoring, Human review tray, Audit hashing, Metadata verification, Cross-verification, Synthetic media screening.
3. Schedule Intelligence: Respecting CPM dependencies, Planned vs. Actual visibility.
4. Field Usability: Offline-tolerant, IVR fallback, fast, natural language input.
5. Advanced Value: Butterfly Effect, Shadow Schedule, Weather Correlation.

7. 🚫 STRICT BOUNDARIES (What AI Must NEVER Suggest)
- NO Fake Gantt Charts: The UI schedule MUST mathematically respond to updates. No static/hardcoded frontend bars.
- NO Overconfident AI: Never claim 100% accuracy. Always rely on the "3-Tier Confidence Routing" and "Human-in-the-Loop" review tray.
- NO VLM Hallucinations: Do not use Vision-Language Models (VLMs) as the primary OCR engine. Use deterministic local OCR (PaddleOCR) + LLM extraction. A VLM may be used ONLY as a secondary cross-verifier; its output never replaces or overwrites the OCR source of truth.
- NO Single-Source Image Trust: When image extraction is cross-verified and the two sources disagree, the update must never auto-commit. Disagreement always lowers confidence and forces human review.
- NO Blind Metadata Trust: Compressed images without verified EXIF/GPS hashes must have their confidence scores capped.
- NO Synthetic Evidence: AI-generated or synthetically edited images must never auto-commit as field proof. High `ai_generation_risk` blocks evidence use and forces human review.
- NO Complex Field Forms: Site workers will not use dropdowns or WBS codes. Input must be voice, photo, natural text, or IVR call.
- NO Breaking CPM Logic: If Task B depends on Task A (Finish-to-Start), the system must throw a logic error if a user tries to finish B before A.
- NO Over-Feature Loading: Do not build generic chatbots, heavy admin panels, or unrelated analytics. Focus purely on the Reconciliation Flow.
- NO Tech Jargon Before Problem: In pitches, always explain the pain of manual reconciliation before explaining the Graph-RAG or Hash Chaining.

8. DATA & TECH CONTEXT
- Tech Philosophy: 100% Free & Open-Source (FOSS). Zero licensing costs.
- Stack Context: Python (FastAPI), React + Frappe Gantt, Telegram Bot API, Whisper (Local), PaddleOCR / RapidOCR, local VLM verifier (Qwen2.5-VL / MiniCPM-V), Twilio/Exotel (IVR), ChromaDB, `xerparser`.
- Core Data Schemas:
  - Extraction: `{"spatial_zone", "discipline", "component", "action", "status", "percent_complete", "extraction_agreement", "cross_check_status"}`
    cross_check_status values: "agreed | partial_mismatch | disagreed | single_source"
  - Metadata Manifest: `{"original_sha256", "compressed_sha256", "gps_coords", "exif_present", "device_id", "capture_timestamp", "ai_generation_risk", "c2pa_detected"}`
  - Audit Block: `{"log_index", "timestamp", "wbs_activity_id", "action_performed", "confidence_score", "cross_check_status", "previous_hash", "current_hash"}`

9. THE 60-SECOND DEMO FLOW (The Ultimate Goal)
1. Supervisor sends a Hinglish voice note + photo via Telegram (or calls IVR from a dead zone).
2. AI extracts entities, validates GPS EXIF, checks metadata hashes, runs the AI-generated image meta check, and cross-verifies OCR vs VLM extraction.
3. Graph-RAG matches it to WBS Task `CIV-P14-004` with 94% confidence.
4. System auto-commits to the `.xer` file, respecting CPM logic.
5. Manager dashboard shows the "Planned vs Actual" shift in real-time.
6. Butterfly Effect triggers: System suggests a crew reallocation to save the L1 milestone.
7. Audit log generates an immutable SHA-256 hash for billing proof.

10. 🏢 CORPORATE CONTEXT: OIL & NRL
Organization Hierarchy:
- SIH26122 is officially submitted by Oil India Limited (OIL) — the parent company.
- Numaligarh Refinery Limited (NRL) is OIL's primary subsidiary (OIL holds 69.63% stake + management control).
- NRL Location: Morangi, Golaghat District, Assam, India.
- NRL Current Capacity: Expanding from 3 MMTPA → 9 MMTPA (6 MMTPA expansion project ongoing).
- NRL Significance: Energy security lifeline for North-East India; pioneer in bamboo-based bio-ethanol and green hydrogen.
Why This Matters for the Pitch:
- Use NRL's ongoing 9 MMTPA expansion as the primary real-world case study in the demo.
- The problem statement targets infrastructure project management (construction tracking), NOT chemical manufacturing.
- Frame the demo around tracking construction of refinery units, storage tanks, or pipelines at NRL.
- Highlight how IVR and offline-tolerance solve the specific connectivity issues in Assam's remote expansion zones.

11. 👷 L5 / L6 EXECUTION MODEL (Corporate Process Simulation)
L5 (Senior Engineer) — "The Core Engine Builder"
Corporate Role: Owns a complex subsystem end-to-end. Writes production-grade code, optimizes algorithms.
FORGE Responsibilities:
| Task | Detail |
|------|--------|
| Field App | Build offline-tolerant mobile input (voice/photo only, zero dropdowns) |
| AI Extraction | Whisper ASR + PaddleOCR + Pydantic-constrained LLM prompts for entity extraction |
| Dual-Source Verifier | Run local VLM cross-check and field-level comparator |
| Semantic Matching | Vector DB + metadata filtering (Zone → Discipline → Activity) |
| Confidence Scoring | Calculate and attach confidence score to every match |
| API Bridge | Push structured JSON to the Review/Schedule layer |
Quality Bar: The L5's job ends when a clean, structured JSON with confidence score is generated. They do NOT touch the Gantt chart logic.

L6 (Staff/Principal Engineer) — "The Architect & Trust Guardian"
Corporate Role: Owns system-wide architecture, enterprise integration, edge-case handling, and business alignment.
FORGE Responsibilities:
| Task | Detail |
|------|--------|
| Schedule Logic Protection | Ensure CPM dependencies, float, and critical path are never broken |
| Human-in-the-Loop Design | Build the Manager Review Tray with 1-click approve/reject |
| Out-of-Order Detection | Flag anomalies (e.g., "concrete poured" before "rebar inspection" complete) |
| Metadata/EXIF Verification | Verify hashes, GPS, EXIF, and synthetic media screening |
| Audit Architecture | Design the immutable SHA-256 hash chain for billing proof |
| Enterprise Integration | Define how FORGE connects to existing Primavera P6 / SAP / MS Project |
| The Pitch | Translate technical work into business value for OIL/NRL judges |
Quality Bar: The L6 ensures the system is auditable, enterprise-ready, and never overconfident. They protect the schedule like a firewall protects a network.

The L5 ↔ L6 Handshake (Collaboration Flow)
L5 builds: Field Input → AI Extraction → Dual-Source Cross-Check → Matching → Confidence Score
                                    ↓
L6 receives: Structured JSON + Confidence Score + Cross-Check Status + Metadata Status
                                    ↓
L6 applies: Confidence Routing → Dependency Check → Human Review → Schedule Write-Back → Audit Log

12. 🎬 REAL-WORLD USE CASE EXAMPLE (For Pitch)
Scenario: Building a Crude Oil Storage Tank at NRL
Characters:
- Rahul — Site Supervisor at NRL Golaghat
- Priya — Project Controls Planner in NRL office
- Contractor — External construction company

❌ BEFORE FORGE (The Pain)
- Rahul finishes concrete at "Sector B Pier 14." Sends WhatsApp voice note: "Sector B Pier 14 ka concrete done, rebar was checked in morning." + 3 blurry photos.
- Priya receives 400+ such messages/week. Spends 8 hours on Friday manually mapping them to WBS codes.
- Priya updates MS Project but forgets to verify "Soil Compaction" dependency. Schedule logic breaks silently.
- Contractor submits ₹50 Lakh bill. Finance rejects it — no formal time-stamped proof. Payment dispute stalls work.

✅ AFTER FORGE (The Solution)
- Rahul opens FORGE app (or calls IVR from a dead zone). Records voice: "Sector B Pier 14 concrete pouring completed." Snaps photo. 10 seconds. No forms.
- FORGE extracts: `{Zone: "Sector B", Component: "Pier 14", Activity: "Concrete Pouring", Status: "Complete"}`. OCR and VLM cross-check agree. Metadata verified. No synthetic media detected.
- Semantic Matcher finds WBS `CIV-STR-014` with 92% confidence.
- Confidence > 85% → Auto-routes to Priya's dashboard with photo evidence.
- Priya sees suggestion, clicks "Approve" in 2 seconds.
- FORGE checks dependencies: "Rebar Inspection ✓ complete." Logic holds. Updates Actual Progress.
- Director opens dashboard → sees Green (Actual) catching up to Blue (Planned) instantly.
- Contractor submits bill → Finance clicks task → sees full audit trail (photo, GPS, timestamp, cross-check status, approval). ₹50 Lakh cleared instantly.

13. 💰 BUSINESS VALUE MATRIX (For Judges)
| Business Pain | How FORGE Solves It | Quantifiable Impact |
|---|---|---|
| Manual Reconciliation Lag | AI auto-maps field updates to WBS | Saves 30-40 hrs/week per planner |
| Billing Disputes | SHA-256 audit trail + GPS/metadata proof | Eliminates ₹Crore-level payment disputes |
| Broken Schedule Logic | CPM dependency validation before write-back | Prevents cascading critical-path errors |
| Low Field Adoption | Voice/photo input, zero training | Near 100% ground staff adoption |
| Remote Dead Zones | Telephony IVR + Offline App caching | Updates possible with zero internet |
| Delayed Visibility | Real-time Planned vs Actual dashboard | Leadership sees slippage same-day, not same-week |
| Fake / AI-Generated Progress Photos | Synthetic media meta check + OCR/VLM cross-verification | Prevents fraudulent billing claims |
| Loss of Institutional Memory | Shadow Schedule learns from historical data | Future projects estimated with ground-truth accuracy |

14. 🎤 PITCH STRATEGY & JUDGE PSYCHOLOGY
Opening Rule (NEVER Violate):
Always explain the PAIN before the TECHNOLOGY.
Start with: "In every NRL expansion project, planners spend 40 hours a week translating WhatsApp voice notes into Primavera P6..."
Then introduce: "FORGE automates this translation with confidence scoring and schedule-aware logic."

What Judges Must FEEL After Demo:
| Feeling | Trigger |
|---|---|
| "This problem is REAL" | Show the 400 voice notes → 8 hours manual mapping pain |
| "This solution is USEFUL" | Show 10-second field input → instant schedule update |
| "This solution is TRUSTWORTHY" | Show confidence scores, human review, cross-verification, audit hash |
| "This solution is PRACTICAL" | Show it respects CPM, doesn't replace planners, supports them |
| "This solution is ENTERPRISE-READY" | Show .xer parsing, dependency checks, offline tolerance, IVR fallback |

Key Phrases to Use in Pitch:
- "FORGE supports planners. It does not replace them."
- "The AI knows its confidence limit. When unsure, it asks a human."
- "This is not a toy dashboard. It is a bridge to Primavera P6."
- "Every update is tamper-proof, time-stamped, and metadata-verified."
- "A site supervisor needs zero training. Just speak and snap."
- "Even in zero-internet dead zones, a simple phone call updates the Primavera schedule."
- "Every photo is screened for AI-generated media before it can become billing proof."
- "Two independent AI eyes verify every photo. If they disagree, a human decides — never the machine."

Key Phrases to AVOID (Red Flags):
❌ "Our AI is 100% accurate."
❌ "This replaces project planners."
❌ "Works with any schedule perfectly."
❌ "Fully automatic with no errors."
❌ "We used blockchain..." (unless clearly justified)

15. 🏗️ HACKATHON TEAM EXECUTION PLAN
Role Assignment (Simulate Corporate L5/L6):
| Team Member Role | Mindset | Deliverable |
|---|---|---|
| L5 Builder #1 (AI/Backend) | "Make extraction and matching flawless" | Whisper pipeline + PaddleOCR + VLM cross-check + ChromaDB matcher + Confidence scorer |
| L5 Builder #2 (Frontend/Field) | "Make field input effortless" | Telegram bot + offline-first mobile UI + photo capture + Twilio IVR webhook |
| L6 Architect (System/Logic) | "Protect the schedule, build trust" | Review Tray UI + CPM validation + Metadata/synthetic screening + Audit hash chain + Gantt integration |
| L6 Pitcher (Business/Story) | "Make judges feel the pain and the solution" | 60-second demo script + slide deck + real-world NRL scenario |

Critical Integration Checkpoint (Before the demo, the team MUST verify):
[ ] Voice note → Structured JSON works end-to-end
[ ] OCR ↔ VLM cross-check runs for image updates
[ ] Confidence score appears in UI
[ ] Manager can approve/reject in 1 click
[ ] Gantt chart bar MOVES after approval (not hardcoded)
[ ] Dependency violation triggers a visible error/flag
[ ] Audit log shows timestamp + user + hash + cross-check status
[ ] Planned vs Actual color difference is visible in < 3 seconds

16. 🔴 RED FLAG CHECKLIST (Self-Audit Before Demo)
Before presenting, verify NONE of these exist:
[ ] Schedule bars are static/hardcoded
[ ] AI claims 100% accuracy anywhere
[ ] Field input requires WBS code selection
[ ] Demo depends on manual backend intervention
[ ] No confidence score visible
[ ] No human review step exists
[ ] No audit trail / metadata verification generated
[ ] AI-generated / synthetic image accepted as valid field evidence without review
[ ] Single-source image extraction auto-commits without cross-verification
[ ] VLM output overwrites OCR source of truth
[ ] Team explains tech before problem
[ ] Too many features distract from core flow
[ ] Gantt chart doesn't respond to updates

17. 📋 MINIMUM WINNING EXPERIENCE (8-Point Checklist)
The project MUST convincingly demonstrate ALL 8:
✅ A field update arrives (voice/text/photo/IVR)
✅ The system extracts meaningful project data
✅ The system matches it to a possible schedule task
✅ The system shows confidence (adjusted by metadata quality and cross-verification)
✅ A manager can review if needed
✅ The schedule actual progress updates
✅ The planned vs actual difference becomes visible
✅ An audit record is created
If all 8 are clear → strong winning chance.

18. 📌 FINAL RULE
If any feature, screen, or idea does not help prove that FORGE can convert messy field updates into trusted schedule progress, postpone it.
The project wins through:
- Clear problem understanding
- Strong core reconciliation
- Trusted AI behavior
- Schedule intelligence
- Smooth demo
- Practical enterprise value

Document Version: 3.0 | Last Updated: 2026-08-29 | Status: ACTIVE MEMORY