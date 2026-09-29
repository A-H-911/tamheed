# Plan 163: the version stamp, then lab beat 30 and the evals

> Maintainer-executed, 2026-09-29. Batch map: [160-164-batch-findings-39.md](160-164-batch-findings-39.md).
> Evidence: [evidence/lab-continuation-report-163-2026-09-29.md](evidence/lab-continuation-report-163-2026-09-29.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## The order of the steps

The stamp lands before the beat, with the guide's history key in the same step. A fixture
refreshed to a body the history does not hold would read as customised.

| Step | What | Result |
|---|---|---|
| 0 | Lint 9 takes a `"5.7.0"` history key | yes: 17 files, 102 bodies |
| 1 | The stamp: `plugin.json`, the guide's title, `artifact-catalog.md`, `server/README.md`, the front door, `README.md` twice, the changelog's heading | 8 files, 11 lines in, 8 out |
| 1 | The guide against the body of 5.6.1 | one line in, one out: the title |
| 2 | Assertions that name the release, the latest handoff or the page's date, in the evals and the suites | four in the evals, re-aimed; none names the page's date |
| 2 | Fixture files the beat deletes | none |
| 3 | Beat 30 | held on its second run; the first stopped in the scratch phase on an assertion of the harness |
| 4 | The evals | 4 re-aimed, 3 added, 126 checks |

## What the beat fires

| Mechanism | On the scratch copy |
|---|---|
| The order (plan 160) | two risks of two widths written first; a typed bound returns the row after it by number, where the same ids as text return nothing; a bound that names no row; a complete walk; a limited read of the journal still returns the lowest ids |
| The refusals (plan 161) | seven items the two journal tools do not take, each refused in words; the counts and the digest hold |
| The descriptions (plans 160, 161) | each of the two tools names every key of its constant, under the cap |
| The audit's export (plan 162) | `csv/` beside the page at an outside path; the package's files keep their hashes |
| The first export on the release | the stamp and the stated date move, and no other line |

## The assertion that was wrong

The first run stopped where the harness compared the page's date line before and after. It had
replaced every occurrence of the old date in a line of 4,647 characters, and that line holds the
same date as a stored value too. The pages differed in the stamp and the stated date only. The
assertion now replaces the date where the page states it, and asserts that place occurs once.

**The lesson is last round's, met again:** a check on a long line must name the one place it
means.

## What was made able to fail before the run

| Assertion | Why it could have proved nothing | What the beat does |
|---|---|---|
| The order of a family | every id of the lab is of one width, so both orders agree | writes ids of two widths first, and asserts the two orders differ |
| The first export's line count | it depends on the UTC date | reads the date from the page and expects one line or two |
| The refusal | a refused write and a dropped key both return without a new row | asserts `ok` is false, the message names the key, and the raw database text is absent |

## Validation

| Check | Result |
|---|---|
| `python check.py lint` after the stamp | ALL CHECKS PASSED; 5 surfaces carry v5.7.0; the manifest equals the changelog's newest release |
| Beat 30, run 2 | every assertion held in both phases, 05:21:29Z to 05:21:32Z |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED; three eval cases checked, none failed |
| The fixture's diff | four files: the journal and its CSV, the guide's title, the page |
| The fixture's page | 15 lines in, 15 out, each classified in the evidence report |
| The operator's trace file | 31 lines before and after |
