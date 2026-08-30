FORGE — Winning Priority Only

Problem Statement: SIH26122
Project Name: FORGE
Focus: Real-Time Actual Progress Tracking — Planning-to-Execution Bridge
Purpose of this file: This file contains only winning priorities and quality rules.
It is not an implementation plan. The actual plan will be created only after this is approved.

1. Main Winning Goal
FORGE must clearly prove one thing:
Messy, informal ground-site updates can be converted into trusted, real-time project schedule progress without breaking the official schedule logic.
The judges must understand:
- The problem is real.
- The solution is practical.
- The system saves manual effort.
- The system is trustworthy.
- The system can work with real project schedules.
- The solution is demo-ready.

2. What Must Be Excellent

A. Field Update Capture
The project must make it very easy for a site person to report progress.
It should feel simple, fast, and natural.
The system should accept informal field input such as:
Voice notes, Short text messages, Site photos, Daily notes, Simple field reports, IVR phone calls.
The system must not force the site user to understand formal WBS codes, project management terms, or complex forms.
Winning quality:
A site supervisor should be able to say something informal like:
"Pier 14 concrete pouring completed."
And the system should understand the meaning without requiring exact schedule language.

B. Understanding Informal Language
FORGE must show that it can understand construction and infrastructure language.
It should handle: Trade terms, Site slang, Mixed language, Short incomplete sentences, Voice-based updates, Handwritten or scanned notes.
The system should extract useful meaning from the update, such as:
Location / zone, Discipline, Activity, Asset or component, Progress percentage, Completion status, Time of work.
Winning quality:
The system should convert informal field language into structured project information.

C. Matching Field Update to Correct Schedule Task
The project must show intelligent mapping between field updates and schedule tasks.
This is one of the most important winning areas.
The system should not blindly search all tasks. It should intelligently narrow down the possible task using context such as:
Zone, Discipline, Activity type, Component, Timeline, Similar previous updates.
Winning quality:
If the field update is:
"Shuttering removed at Pier 14."
The system should match it to the correct civil activity related to Pier 14, not to an unrelated piping or electrical task.

D. Confidence and Human Control
The system must not appear overconfident.
It should show different confidence levels:
High confidence: automatic update, Medium confidence: manager review, Low confidence: manual handling or unplanned activity.
This is very important for trust.
Cross-Verification:
Where possible, image-based extraction should be verified by two independent sources
(deterministic OCR and a vision-language verifier).
If the two disagree, confidence drops and a human decides.
Winning quality:
Judges should feel that FORGE does not randomly change the schedule.
It knows when it is confident and when it needs human approval.
Judges should feel that FORGE does not trust a single AI blindly.
It cross-checks evidence and escalates disagreement to humans.

E. Schedule Update Without Breaking Logic
FORGE must show respect for schedule logic.
It should update actual progress without damaging:
Dependencies, Task sequence, Planned dates, Critical path logic, Remaining work, Baseline comparison.
The system must not look like a simple database that randomly stores progress.
Winning quality:
The system should feel like a bridge to enterprise project scheduling, not a replacement toy dashboard.

F. Clear Planned vs Actual Visibility
The project must clearly show the difference between:
Planned progress, Actual progress, Delayed tasks, Updated tasks, Critical path impact.
This should be visually clear.
Winning quality:
A judge should instantly see:
"This task was planned here, but actual progress changed it."
The difference must be obvious within seconds.

G. Trust and Proof
FORGE must show that updates are not silently changed or manipulated.
The system should provide proof of:
Who updated, What was updated, When it was updated, Which task was affected, What confidence level was found, What evidence exists, Whether the update was approved.
Evidence Integrity:
The system should verify image metadata (GPS, EXIF, hashes) and screen photos for AI-generated or synthetic media before they can be used as billing evidence.
Winning quality:
The system should feel auditable and reliable for a large organization like Oil India Limited.

H. Demo Smoothness
The demo must be simple and powerful.
The judges should see a clear flow:
1. Field person gives informal update.
2. System understands it.
3. System cross-verifies image extraction.
4. System matches it to a schedule task.
5. System shows confidence.
6. Manager approves if needed.
7. Schedule actual progress updates.
8. Planned vs actual becomes visible.
9. Audit proof is generated.
Winning quality:
The demo should be understandable in under 60 seconds.

3. What Should NOT Be in the Project

A. No Fake Gantt Chart
The project must not use a hardcoded or fake schedule view.
If the schedule is shown, it must respond to updates.
Not acceptable: Static bars, Fake progress, Manual UI changes during demo, Schedule that does not reflect actual update logic.

B. No Over-Feature Loading
Do not add too many features that distract from the core problem.
Avoid building too much of: Fancy analytics, Too many dashboards, Generic chatbot, Login systems with unnecessary complexity, Multiple unrelated modules, Heavy administrative panels.
The core problem must win first.

C. No Generic AI Claims
Do not present the AI as magical.
Avoid claims like: "100% accurate", "Fully automatic with no errors", "Replaces project planners", "Works with any schedule perfectly".
The project should feel realistic, controlled, and trustworthy.

D. No Complex Field Input
The field user experience must not become complicated.
Avoid: Long forms, Mandatory WBS selection, Too many dropdowns, Technical task coding, Heavy file uploads from field users, Confusing approval steps for site workers.
Field input must remain simple.

E. No Blind Schedule Writing
The system must not directly modify schedule data without confidence checks.
Avoid: Automatic updates with no review option, Silent schedule changes, Broken dependencies, Out-of-order task completion, Missing evidence for updates.

F. No Unclear Problem Explanation
The team must not spend too much time explaining technology before explaining the problem.
Judges must first understand:
Why reconciliation is painful, Why manual mapping is slow, Why schedule visibility is delayed, Why billing disputes happen.
Technology explanation comes after the problem.

4. Winning Priority Order
All decisions must follow this priority order.

Priority 1 — Core Reconciliation Flow
This is the most important part.
The project must show: Field update received, Meaning extracted, Task matched, Progress updated, Result visible.
If this is weak, the project will not win.

Priority 2 — Trust and Control
The project must show: Confidence score, Human review, Audit trail, Approval flow, Evidence visibility, Metadata verification, Cross-verification, Synthetic media screening.
This makes the solution feel enterprise-ready.

Priority 3 — Schedule Intelligence
The project must show: Task dependencies are respected, Out-of-order work is flagged, Planned vs actual is clear, Critical path impact is visible.
This separates FORGE from a normal progress tracker.

Priority 4 — Field Usability
The system must feel easy for ground staff.
Focus on: Simple input, Fast reporting, Less typing, Natural language, Mobile-friendly experience, Offline-tolerance, IVR fallback.

Priority 5 — Advanced Value Features
These are useful but not more important than the core flow.
Examples: Weather correlation, Conflict detection, Daily progress report, Historical variance, Evidence storage, Advanced analytics.
Use these only if the core flow is already strong.

5. What Judges Must Feel
After the demo, judges should feel:

This problem is real.
- Site teams report informally.
- Planners use formal schedules.
- Manual reconciliation is slow.

This solution is useful.
- It reduces manual mapping.
- It gives faster progress visibility.
- It improves trust.

This solution is practical.
- It does not replace planners.
- It supports planners.
- It allows human review.

This solution is intelligent.
- It understands field language.
- It matches tasks contextually.
- It knows its confidence limit.
- It cross-verifies image extraction with two independent AI sources and escalates disagreement to humans.

This solution is trustworthy.
- It verifies image metadata and screens for AI-generated media.
- It creates tamper-evident audit proof.

This solution is enterprise-ready.
- It respects schedule logic.
- It creates audit proof.
- It can fit into real project management workflows.

6. Quality Bar for Each Core Feature

Field Input
Should be: Fast, Natural, Low effort, Mobile-friendly, Offline-tolerant, Easy to demonstrate.
Should not be: Long form filling, Technical coding selection, Confusing navigation, Dependent on perfect internet.

AI Extraction
Should be: Structured, Explainable, Limited to useful project fields, Easy to verify, Clear in the UI, Cross-verified where possible (OCR vs VLM agreement visible).
Should not be: Random text generation, Hidden magic, Overconfident, Unverifiable, Single-source blind trust on image evidence, Silent auto-resolution of extraction disagreements.

Task Matching
Should be: Context-aware, Ranked by confidence, Limited by discipline and zone, Reviewable by manager, Transparent.
Should not be: Full-text blind search, Random task selection, No confidence score, No correction option.

Schedule Update
Should be: Non-destructive, Logic-aware, Visible, Reversible or auditable, Compareable with baseline.
Should not be: Breaking dependencies, Changing planned baseline incorrectly, Hiding what changed, Looking like a fake chart.

Audit Proof
Should be: Simple to understand, Timestamped, User-linked, Task-linked, Evidence-linked, Tamper-aware, Cross-check-aware, Synthetic-media-aware.
Should not be: Hidden logs only developers understand, Overcomplicated blockchain-style claims unless clearly useful, Fake security statements, Missing approval trail.

7. Red Flags That Can Reduce Winning Chance
The project should avoid these red flags:
- Demo depends on too many manual backend steps
- AI mapping looks random
- No clear link between field update and schedule task
- Schedule view is fake
- No confidence or review mechanism
- No audit trail
- Too much focus on buzzwords
- Too many features but weak core
- Problem statement not clearly connected to solution
- Team cannot explain the workflow simply
- System feels impossible to deploy in real projects
- No respect for schedule dependencies
- No clear planned vs actual comparison
- AI-generated image accepted as valid field evidence
- Single-source image extraction auto-commits without cross-verification
- VLM output overwrites OCR source of truth

8. Minimum Winning Experience
At minimum, the project must convincingly show:
1. A field update arrives.
2. The system extracts meaningful project data.
3. The system cross-verifies image extraction (OCR vs VLM).
4. The system matches it to a possible schedule task.
5. The system shows confidence.
6. A manager can review if needed.
7. The schedule actual progress updates.
8. The planned vs actual difference becomes visible.
9. An audit record is created.
If these things are clear, the project has a strong chance.

9. What Will Be Done Later
The following things will be created only after this priority document is approved:
Actual implementation plan, Task breakdown, Module division, UI flow details, Data design, Demo script finalization, Pitch deck content, README, Testing plan, Team work allocation.
This file is only for deciding what matters most for winning.

10. Final Rule
If any feature, screen, or idea does not help prove that FORGE can convert messy field updates into trusted schedule progress, it should be postponed.
The project must win through:
- Clear problem understanding
- Strong core reconciliation
- Trusted AI behavior
- Schedule intelligence
- Smooth demo
- Practical enterprise value