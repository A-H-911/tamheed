# Plan 158: the version stamp, then lab beat 29 and the evals

> Maintainer-executed, 2026-09-28. Batch map: [156-159-batch-findings-38.md](156-159-batch-findings-38.md).
> Evidence:
> [evidence/lab-continuation-report-158-2026-09-28.md](evidence/lab-continuation-report-158-2026-09-28.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (it writes the committed fixture) - **DONE**

## Order

0. Lint 9 read for the history key.
1. The stamp, with the stock guide's body under its history key.
2. The greps for assertions the beat moves.
3. The beat: scratch phase first, then the fixture.
4. The evals re-aimed, the scenario item written.
5. The full gate.

## 0. The history key

Lint 9 asks that the guide's current body be among the history's values. It reads no key. The
version lints match three numbers, and the engine sorts versions by their numbers. A third
number that is not zero passes all of them, and the lint gate said so after the stamp.

## 1. The stamp

| Surface | Change |
|---|---|
| `plugin.json`, the guide's title, `artifact-catalog.md`, `server/README.md`, the front door, `README.md` twice | 5.6.0 → 5.6.1 |
| `CHANGELOG.md` | the heading `## [5.6.1] - 2026-09-28` over the body plan 157 wrote |
| `stock-history.json` | the key `"5.6.1"` holding the guide's body |

The guide changed in its title only: one line in, one line out.

## 2. The greps

Four assertions name what the beat moves: the latest handoff's id, the guide's version, the
page's version stamp, and the count of handoff entries. One test names the lab fixture, and it
reads its prompts folder, not its page.

## 3. The beat

It held on its first run. The scratch phase ran first and the fixture was opened after it.

| What v5.6.1 teaches | Where it was exercised |
|---|---|
| A limited read returns the lowest ids | scratch: ten rows of 55 returned the ten lowest; the resume block named the three highest; no id shared |
| What to read after the handoff | scratch: one work entry; the count read 1, the rule named it, `ids` read it back |
| The page's bytes hold on one date | scratch: two dates over one store and one fixed report; equal after replacing the date |
| The first export after an upgrade | scratch: one line changed, the stamp; the digest unchanged; the export ran on the date the page carried |
| The audit writes nothing into the package | scratch: an export to a path outside the package; 27 files kept their hashes |
| The handoff names what follows it as following | fixture: the final handoff says the export and the checks follow it |

**Two assertions were made able to fail before the run.** The list of `handoff-current` is empty
on the fixture, so the check writes one work entry first. The assertion on the first export
counts one changed line on the page's own date and two on a later one, and it reads the date
from the page.

## 4. The evals and the scenario

Four assertions re-aimed, three added. The `lab-tracker` case holds 123 checks. `lab/scenario.md`
gains item 29; item 28's sentence on a second export gained its condition in plan 157.

## Validation

| Check | Result |
|---|---|
| `python check.py lint` after the stamp | ALL CHECKS PASSED; five surfaces carry v5.6.1; 101 bodies in the stock history |
| Beat 29 | held on run 1, 09:50:39Z to 09:50:41Z |
| `python check.py`, the trace variable unset in the command | ALL CHECKS PASSED; 3 eval cases, none failed |
| `m38.py` | its output is beside it; it prints counts and ids and no field text |
