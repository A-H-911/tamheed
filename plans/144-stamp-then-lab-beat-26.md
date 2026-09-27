# Plan 144: the version stamp, then lab beat 26 + evals

> Maintainer-executed, 2026-09-27. Batch map: [141-145-batch-findings-35.md](141-145-batch-findings-35.md).
> Ruling R19. Evidence: [evidence/lab-continuation-report-144-2026-09-27.md](evidence/lab-continuation-report-144-2026-09-27.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (it writes the recorded fixture) - **DONE**

## Step 1 — the stamp, before the beat

`plugin.json`, the stock guide's title, `artifact-catalog.md`, `server/README.md`, the front door
`SKILL.md`, `README.md` (two places), and the CHANGELOG heading `[5.4.0] - 2026-09-27`. The guide's
final body landed under `"5.4.0"` in `stock-history.json` in the same step.

Measured at the stamp (U2 of the plan): the guide's body differs from the 5.3.0 body in ONE line,
its title. No line was gained or lost.

## Step 2 — the greps before the beat

| Grep | Finding |
|---|---|
| F-10, fixture readers in `tests/` | one: `test_eval_runner.py` reads the fixture's `prompts` folder; the beat deletes no file there |
| F-6, assertions naming what the beat moves | three: the resume block's handoff id, the guide's version, the handoff count |

## Step 3 — beat 26

`lab/scenario.md` item 26. The scratch phase runs FIRST with hard assertions; the fixture is written
only after it held. What fired:

- two sessions in one folder: the same block, equal counts, each line ending with its own
  `session=`;
- the token rule: a newline, a space, a number and an absent id each give `session=-` on one line;
  a forged `source` gives `source=-`;
- the emission: the guide refreshed to 5.4.0, every scan empty, no `skill` key;
- on the fixture: one note, the final handoff LAST, `export_html`, `gate_run` ready,
  `package_verify` green, `package_close`.

The harness removes the operator's own trace variable from every hook run.

## Step 4 — evals

Three assertions re-aimed, two added. The case carries 112 deterministic assertions.

## Owned

The first full gate after the beat was RED on one contract test,
`test_stock_merged_marker_is_verified_against_the_history`. The test built a partial hand-merge
from the NEWEST release of the guide: the previous body plus ONE of the lines the release added.
It assumed every release adds two lines or more. 5.4.0 changes only the guide's title, so that
one line is the whole delta and the engine rightly read `verified: true`. The engine is
unchanged. The test now takes the newest release that added two lines or more, and fails with
a message if none did. Sibling tests were read: none builds a partial merge from the newest
release's delta.

## Validation

| Check | Result |
|---|---|
| The beat, first run | every assertion held in both phases |
| The operator's trace file over the beat's window | five lines before and after; none inside |
| `python check.py`, the variable unset | RED once (the test above), then ALL CHECKS PASSED |
| The fixture's diff | the journal gained two rows; the guide's title; `review.html` where the journal moved |
