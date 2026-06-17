# Quality gates

Gates verify the package is complete, consistent, traceable, and executable before handoff. **Critical**
gates block readiness; **Warn** gates surface issues but don't block. Many are checked mechanically by
`../tests/validate_package.py`; the rest are judgment checks you perform.

| Gate | Severity | Checks | Mechanical? |
|---|---|---|---|
| G-REQ-SRC | Critical | Every `FR-/NFR-` has a `source`. | Yes |
| G-IDS | Critical | Identifiers match `governance.md` format; unique; no dangling cross-refs. | Yes |
| G-DEC-STATUS | Critical | Every decision/ADR has an explicit status from the allowed set. | Yes |
| G-TRACE | Critical | Every MVP `FR-/NFR-` reaches ≥1 decision, ≥1 task, ≥1 test; behavior-bearing ones reach an `AC-`. | Yes |
| G-COMPLETE | Critical | Every artifact in the selected set exists and is non-stub (no "TODO"/empty sections). | Yes |
| G-CONFLICT | Critical | No unresolved hard contradiction remains past scope lock. | Partly |
| G-EXEC | Critical | Each phase has deliverables + exit criteria; leaf WBS items are actionable + testable. | Partly |
| G-HANDOFF | Critical | Handoff prompts reference only existing artifacts; agent-neutral; no dangling instructions. | Partly |
| G-OQ | Critical | No **blocking** open question is silently unanswered; open ones are listed as accepted-open. | Partly |
| G-ASM-VISIBLE | Warn | Assumptions consumed by stages are recorded with `risk_if_wrong`. | Partly |
| G-CLAIM | Warn | Capability claims in Approved artifacts are cited or tagged `unverified`. | No |
| G-RISK | Warn | High-impact requirements/decisions have a risk view. | Partly |
| G-COUPLING | Warn | No needless coupling to one agent/provider/stack (see safeguards 13–15). | No |
| G-BLOAT | Warn | No artifact merely restates another; no empty placeholders. | Partly |
| G-CMD-THIN | Warn | The slash command contains no methodology/business logic. | Partly |

## Running gates

- Stage 19 runs the full set; Stage 22 re-confirms criticals for the readiness report.
- Mechanical gates: `python ../tests/validate_package.py <package-dir>` → JSON + human report with per-gate
  pass/fail and the offending IDs/paths.
- Judgment gates: perform the check and record the verdict in the validation report with evidence.

## Readiness rule

A package is **execution-ready** only when every Critical gate passes and every Warn gate is either passing
or has an accepted, recorded exception. The readiness report lists each gate, its result, and (for any
exception) who accepted it and why. Never report "ready" with a Critical gate failing.
