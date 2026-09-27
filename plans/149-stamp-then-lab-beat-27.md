# Plan 149: the version stamp, then lab beat 27 and the evals

> Maintainer-executed, 2026-09-27. Batch map: [146-150-batch-findings-36.md](146-150-batch-findings-36.md).
> Rulings R27, R32, R33. Evidence:
> [evidence/lab-continuation-report-149-2026-09-27.md](evidence/lab-continuation-report-149-2026-09-27.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (it writes the committed fixture) - **DONE**

## Order

1. The stamp, with the stock guide's final body under its history key.
2. The greps for assertions the beat moves.
3. The beat: scratch phase first, then the fixture.
4. The evals re-aimed, the scenario item written.
5. The full gate.

## 1. The stamp

| Surface | Change |
|---|---|
| `plugin.json`, the guide's title, `artifact-catalog.md`, `server/README.md`, the front door, `README.md` twice | 5.4.0 → 5.5.0 |
| `CHANGELOG.md` | the heading `## [5.5.0] - 2026-09-27` over the body plan 148 wrote |
| The stock guide's lesson sentence | the rule-first clause (R28) and the roster with its cap, in the two words (R32, R34) |
| `stock-history.json` | the key `"5.5.0"` holding the guide's final body |

The guide gained five lines over its 5.4.0 body and lost three. The contract test that builds a
partial merge needs the newest release to add two lines or more; this one does.

## 2. The greps

Three assertions name what the beat moves: the latest handoff's id, the guide's version, the
count of handoff entries. No test reads the fixture's files by path. No assertion counts lessons
or journal entries exactly.

## 3. The beat

Scratch phase, hard assertions, on a copy that is never committed:

- the approval hint in the two words, its cap phrase unchanged;
- two approvals with no emit after them: the page and the note on disk differ, as the page says;
- the cut: a story-first statement renders the story, a rule-first one carries its rule;
- eleven unpinned approvals: the oldest leaves the note, the footer says it binds too, the page
  marks ten, the Approved query returns eleven;
- a pin: rendered whatever its number;
- a low-numbered lesson approved late: never rendered, and it binds.

Then the fixture: the emit with `refresh_stock`, one note, the final handoff last, the export, the
gate, the verify, the close.

**The beat held on its fourth run.** Runs 1 to 3 stopped in the scratch phase, before the fixture
was opened. Two were the harness's own errors: it read `changed_columns` as a list of names, then
expected three changed columns from a row that sent two. The third was the engine refusing an
approval that omitted a stored column; the harness then sent the stored content whole.

## 4. The evals and the scenario

| Assertion | Change |
|---|---|
| The resume block's handoff | re-aimed to the beat's final handoff |
| The guide's version | re-aimed to `tamheed v5.5.0` |
| The count of handoff entries | five to six |
| The roster column on the review page | new |
| The fold's title | new |
| The beat's note quoting the footer | new |
| The guide stating the roster | new |

`lab/scenario.md` gains item 27 before the Pass bar. The Pass bar's list of deliberately-open items
is unchanged: the fixture's Proposed lesson stays Proposed.

## 5. What the fixture does not cover

The fixture has one Approved lesson. The footer never prints there, and the page marks one row.
The footer's end-to-end coverage is the scratch phase and the contract suite.

An interview option had said the beat rewrites the fixture's note. It does not. The batch record
owns the wording.

## Validation

| Check | Result |
|---|---|
| Lints after the stamp | all 13 pass; five stamped surfaces carry 5.5.0; the stock history is current |
| The beat, run 4 | every assertion in both phases |
| The fixture after the beat | `gate_run` ready; `package_verify` verified with `review_current` true; no lock |
| The fixture's page diff | the digest, the freshness stamps, the journal, the resume section, the Lessons fold |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED; the lab case reads 116 assertions |
| The operator's trace file over the beat's and the gate's windows | no line inside any |
