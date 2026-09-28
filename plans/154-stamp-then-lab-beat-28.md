# Plan 154: the version stamp, then lab beat 28 and the evals

> Maintainer-executed, 2026-09-28. Batch map: [151-155-batch-findings-37.md](151-155-batch-findings-37.md).
> Ruling R41. Evidence:
> [evidence/lab-continuation-report-154-2026-09-28.md](evidence/lab-continuation-report-154-2026-09-28.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (it writes the committed fixture) - **DONE**

## Order

1. The stamp, with the stock guide's body under its history key.
2. The greps for assertions the beat moves.
3. The beat: scratch phase first, then the fixture.
4. The evals re-aimed, the scenario item written.
5. The full gate.

## 1. The stamp

| Surface | Change |
|---|---|
| `plugin.json`, the guide's title, `artifact-catalog.md`, `server/README.md`, the front door, `README.md` twice | 5.5.0 → 5.6.0 |
| `CHANGELOG.md` | the heading `## [5.6.0] - 2026-09-28` over the body plan 153 wrote |
| `stock-history.json` | the key `"5.6.0"` holding the guide's body |

The guide changed in its title only: one line in, one line out. The contract test that builds a
partial merge walks back to the newest release that added two lines or more, which is 5.5.0.

## 2. The greps

Three assertions name what the beat moves: the latest handoff's id, the guide's version, and the
count of handoff entries. No test reads the lab fixture's review page.

## 3. The beat

It held on its first run. The scratch phase ran first and the fixture was opened after it.

| Mechanism | Where it was exercised |
|---|---|
| The trace line's version, printed and silent | scratch |
| A bundle with no manifest, the hook as its own process | scratch |
| The key before the first export on the release | scratch, and the fixture before it was opened |
| The first export: the stamp, the digest unchanged, a second export identical | scratch |
| A write after the export, then the export after the write | scratch, and the fixture at its handoff |
| A page another release exported; a stamp that is not a token | scratch |
| The guide's refresh | the fixture |

The fixture's close-out follows plan 152's rule: the note, the handoff, then the export, then
`gate_run` and `package_verify`. The handoff says so of itself: the export and the two checks run
after it, so their results are in the evidence report and not in the entry.

## 4. Evals and the scenario

| Assertion | Change |
|---|---|
| the resume block's handoff | `PE-053` → `PE-055` |
| the guide's version | `tamheed v5.5.0` → `tamheed v5.6.0` |
| the count of handoff entries | 6 → 7 |
| new: the page's version stamp | grep of the lab page |
| new: the beat's note quotes the trace line's opening | grep of the journal |
| new: the beat's note quotes what the keys read before the first export | grep of the journal |
| new: the beat's note quotes the rule of plan 152 | grep of the journal |

`lab-tracker` holds 120 assertions. `lab/scenario.md` gains item 28, and item 25's pass bar,
which describes the 5.3 line, points at it.

The key itself is a tool result, and the evals read files. It is asserted by the contract test
of plan 151 and by the beat's harness.

## Validation

| Check | Result |
|---|---|
| The stamp script | one guide line in, one out; the history key written |
| `python check.py lint` after the stamp | ALL CHECKS PASSED: five stamped surfaces, stock history current |
| Beat 28 | DONE on run 1, 06:01:24Z to 06:01:27Z |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED; 3 cases checked, 0 failed |
| The operator's trace file | its last line is 04:53:14Z; no line inside a run's window |
