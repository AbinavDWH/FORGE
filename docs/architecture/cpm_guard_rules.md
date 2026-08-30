# FORGE — Critical Path Method (CPM) Guard Rules

## Purpose
The CPM Guard acts as a mathematical firewall to protect the official enterprise schedule from corrupted, out-of-order, or invalid field updates.

## Guard Principles

1. **Non-Destructive Actuals-Only Write-Back**
   - The engine updates only actual execution fields: `ActualStart`, `ActualFinish`, `PercentComplete`.
   - Planned baseline start/finish dates, baseline durations, float calculations, and CPM dependency networks are strictly preserved.

2. **Finish-to-Start (FS) Dependency Integrity**
   - If Task $B$ depends on Task $A$ ($A \rightarrow B$), Task $B$ cannot begin ($\text{PercentComplete} > 0\%$) or complete ($\text{PercentComplete} = 100\%$) unless Task $A$ is $100\%$ complete.
   - Any update attempting to progress Task $B$ while Task $A < 100\%$ is blocked with a `409 Conflict` (Dependency Violation Error).

3. **Reversible & Auditable Changes**
   - Every schedule write operation produces an audit entry linked to the field evidence and approver.
   - A clean baseline backup (`.xml.backup`) is maintained for audit reconciliation and disaster recovery.

## Example Violation Flow
- **Task A (Predecessor)**: `CIV-STR-013` (Pier 14 Rebar Inspection) — Progress: $0\%$
- **Task B (Target)**: `CIV-STR-014` (Pier 14 Concrete Work) — Proposed Progress: $100\%$
- **Result**: CPM Guard detects that predecessor `CIV-STR-013` is incomplete. Auto-commit is blocked, and the violation is logged and presented in the Manager Review Tray.
