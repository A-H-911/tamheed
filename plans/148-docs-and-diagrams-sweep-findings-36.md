# Plan 148: docs and diagrams sweep for v5.5.0

> Maintainer-executed, 2026-09-27. Batch map: [146-150-batch-findings-36.md](146-150-batch-findings-36.md).
> Field source: ACMP `findings_36.md` (§0.1, §0.3, §2, B4), rulings R30, R32, R34.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What was false, and how it is known

| Sentence | Where | Why it is false |
|---|---|---|
| "Every session in every project where the plugin is ENABLED appends a line" | `docs/install.md`, written by the 5.4.0 sweep | sessions a tool started through the Agent SDK's Python entry wrote none (M2), and a session started before an upgrade keeps the hook it loaded (M7) |
| "The hook prints in every session" | `design-decisions.md` §16 | the same |
| "One separate observation, not a mechanism" about what a reload does to the hook | `design-decisions.md` §16, `install.md` | it is documented behaviour (the plugin loading reference) |
| "Only Approved lessons render into the note" | `methodology.md`, `entities.md`, `artifact-catalog.md`, `README.md` | the note renders a roster of them, and the rest bind too (R34) |

**The instrument behind the SDK sentence.** The field read "ran no SessionStart hook" from the
absence of a SessionStart row. Those transcripts hold no hook row of any event, so the absence is
the instrument's limit. The trace shares the blind spot: its variable comes from settings such a
session may not load. A third instrument with another mechanism settles what can be settled: the
listing the harness gave the model.

| Measurement, every transcript on one machine (`sk36.py`, `m36.py`) | Result |
|---|---|
| SDK-Python transcripts carrying a skill listing | 640 of 640, one build (2.1.204) |
| Of those, naming any plugin's skill or tool | 0 |
| Headless command-line transcripts naming a plugin | 1328 of 1328 (the calibration: the pattern fires) |
| SDK-Python transcripts holding a hook row of any event | 0 |
| `hook_success` rows with stdout and stderr both empty, all transcripts | 0 |
| Session `368cc047`: a `silent` trace line carrying its id | no tamheed row in its transcript |

The counts move: transcripts are created and pruned. The first run read 644 SDK-Python transcripts,
the second 640. The docs say "over six hundred".

## What changed

| File | Change |
|---|---|
| `docs/install.md`, the trace paragraph | who writes a line, as a count with its scope; the caller's choice named and no cause stated; a running session keeps the version it loaded (cited); the transcript cross-check; a silent run leaves no row; the old sentence named as a rule that was not a count |
| `docs/install.md`, the reload paragraph | what a reload switches is cited; that it fires no `SessionStart` stays measured |
| `SECURITY.md`, `server/README.md` | the qualifier: a session runs the hook when it loaded the plugin |
| `docs/design-decisions.md` | three dated corrections, beside D-RENDER-HINT, D-HEADLESS-PRINT and D-RELOAD-MEASURED; §17 with seven decisions for the nine rulings |
| `docs/entities.md` | the lesson section defines the two words; the state diagram's approval edge; the rule-first sentence; the review page's column |
| `docs/architecture.md` | the hook's note in the resume sequence diagram; the review page paragraph; a v5.5 paragraph |
| `docs/methodology.md` | the lessons paragraph uses the two words |
| `artifact-catalog.md`, the lesson row | the roster's rule and the rule-first clause; its stamp moves in plan 149 |
| `README.md` | the lessons sentence and the trace clause |
| `CHANGELOG.md` | the `[Unreleased]` body, the three changed strings named first |
| `plans/README.md`, the batch record | the findings_36 section; the record with its measurements |

Not in this plan: the stock prompt guide. Its sentences land in plan 149 with the history key.

## Validation

| Check | Result |
|---|---|
| Greps for `every session in every`, `rendered into the`, `render into the`, outside `.claude/`, `plans/` and the stock history | what remains: the guide (plan 149), the CHANGELOG and the design record describing the old text, the exporter's comment and two test lines |
| Lint 13 over the swept docs | passes; the three corrections quote the old text inside blockquotes |
| Lint 10 (bundle links) | passes |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED |
