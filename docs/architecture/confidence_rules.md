# FORGE — Confidence Scoring & 3-Tier Routing Rules

## Base Confidence Formula

$$\text{Base Score} = (0.6 \times \text{Matcher Score} + 0.4 \times \text{Extraction Confidence}) \times 100$$

## Confidence Adjustments

| Trigger / Condition | Adjustment / Action |
|---|---|
| Match score $> 0.85$ | $+5$ points |
| Clear photo evidence present | $+3$ points |
| Missing GPS coordinates | $-5$ points |
| Missing camera EXIF metadata | $-5$ points |
| Payload hash mismatch | $-15$ points |
| Out-of-order dependency detected | $-10$ points |
| OCR and VLM agree on all key fields | $+8$ points |
| VLM unavailable (`single_source` mode) | $-3$ points |
| Partial cross-check mismatch on non-critical field | Cap score at $84\%$ (forces manager review) |
| Critical mismatch (status, % complete, component) | Cap score at $60\%$ (flagged in review tray) |
| Medium AI generation risk | Cap score at $84\%$ (forces manager review) |
| High AI generation risk | Cap score at $30\%$, block evidence, mark **BLOCKED: suspected synthetic media** |

## 3-Tier Routing Matrix

| Final Confidence Score | Routing Destination | System Action |
|---|---|---|
| **$\ge 85\%$** | Auto-Commit | Runs CPM Guard check $\rightarrow$ Updates schedule actuals $\rightarrow$ Generates audit record |
| **$50\% - 84\%$** | Manager Review Tray | Pushes to Planner Review Tray with full explanation, OCR/VLM comparison, and 1-click commit |
| **$< 50\%$** | Unplanned / Manual | Flags update as low confidence, requiring manual assignment or field verification |
