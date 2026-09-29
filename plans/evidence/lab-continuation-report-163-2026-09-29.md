# Lab continuation report — beat 30 (plan 163, v5.7.0)

> 2026-09-29. Harness: the engine's tool functions in-process, the same code path the MCP tools
> call. The scratch phase ran FIRST on a copy that is never committed; the fixture was written
> after it held. The operator's trace variable was removed before the engine was imported. This
> beat runs no hook.
> Scripts beside this report: [`scripts-findings-39/`](scripts-findings-39/) (`beat30.py`, its
> output `beat30.out.txt`, `m39.py`, `m39.out.txt`, `suites_wrapped.py`,
> `suites_wrapped.out.txt`).

## Runs

| Run | Window (UTC) | Result |
|---|---|---|
| 1 | 05:20:45–05:20:47 | stopped in the scratch phase, on an assertion of the harness. The fixture was not touched |
| 2 | 05:21:29–05:21:32 | every assertion held in both phases |

**What run 1 showed.** The first export changed two lines, as expected on a later UTC date. The
harness then asserted that the second line changed in its date only, by replacing the old date
in the old line and comparing. It replaced every occurrence. The line is 4,647 characters, the
whole Readiness section, and holds the same date elsewhere as a stored value. A character
comparison of the two pages showed two differences and no more: the stamp and the date the page
states. The engine was right and the assertion was wrong. It now replaces the date only where
the page states it, and first asserts that place occurs once.

## Scratch phase (hard assertions)

| Observation | Value |
|---|---|
| `package_verify("package")`, package closed, before any export on this release | `review_current: true`, `review_exported_by: "5.6.1"` |
| The first export, before any write | 2 lines changed: the stamp, from `5.6.1` to `5.7.0`, and the date the page states. The digest did not move |
| The UTC date of that export against the date the page carried | `2026-09-29` against `2026-09-28` |
| Any other line of the page | unchanged: the page held the id order already |
| `package_verify` after it | `review_current: true`, `review_exported_by: "5.7.0"` |
| The lab's risk ids before the beat wrote any | all of one width, so a check on them would pass under either order |
| After `RISK-998` and `RISK-1000` were written: `entity_query("risk")` | the family in number order, which is not its text order |
| `after_id="RISK-998"` | `RISK-1000`. The same ids compared as text return nothing |
| `after_id="RISK-999"`, a bound that names no row | `RISK-1000` |
| A walk at `limit=2` | complete, in the order of the unlimited read |
| `entity_query("progress-entry", limit=10)` | `PE-001` to `PE-010`, none of them among the resume block's `last_entries` |
| Seven items the two journal tools do not take | each refused in words, none with the database's raw text |
| `summary` sent for `entry` | refused naming `summary` and the seven keys the tool takes |
| `custom_attributes` on `progress_update` | refused by name |
| A missing `entry`; a missing `verdict` | refused naming the key |
| The journal's and the verdicts' counts, and the digest, over the seven refusals | unchanged |
| The registered descriptions of the two tools | each names every key of its constant and fits the cap |
| `export_html(output=<a path outside the package>)` | the page written there with `csv/` beside it, 26 files, the same names as the package's; the outside page equals the package's byte for byte |
| The package's `review.html` and its 26 `csv/` files over that export | each keeps the hash it had |

## Fixture phase

| Observation | Value |
|---|---|
| `package_verify("package")` before the package was opened | `review_current: true`, `review_exported_by: "5.6.1"` |
| `server_info` | 5.7.0 / `007_handoff.sql` / schema 7 |
| The resume block at open | beat 29's final handoff `PE-057`, `handoff_behind` 0 |
| `handoff_emit(refresh_stock=true)` | `refreshed ["prompts/README.md"]`; every scan empty |
| The guide | reads `tamheed v5.7.0`; one line in, one line out, the title |
| The second emit | reports `CLAUDE.md` unchanged |
| The beat's note and final handoff | `PE-058`, then `PE-059`, the handoff written last |
| `handoff-current` | `pass` |
| `review_current` right after the handoff | `false`: the handoff is a write |
| `export_html`, after the handoff | the page carries the `5.7.0` stamp and names `PE-059` as the latest handoff |
| The page's date before and after | `2026-09-28`, then `2026-09-29` |
| `gate_run` | ready |
| `package_verify` | `verified: true`, `dirty: []`, `foreign: []`, `review_current: true`, `review_exported_by: "5.7.0"` |
| `data/.lock` after `package_close` | gone |

## What the fixture changed

| File | Change |
|---|---|
| `data/progress_entries.jsonl`, `csv/progress_entries.csv` | two entries |
| `prompts/README.md` | the title |
| `review.html` | 15 lines in, 15 out, each classified: the digest; the version stamp; eleven lines that carry a section's freshness; the line of the Readiness section, which carries the date it states; one line that holds the new handoff |

No other file of the fixture changed. The five committed export envelopes keep their bytes:
every id of the lab is of one width, so no family's order moved.

## Evals

| Change | Count |
|---|---|
| Assertions re-aimed: the latest handoff's id, the guide's version, the page's stamp, the count of handoff entries | 4 |
| Assertions added: three sentences of the beat's note | 3 |
| Assertions that name the page's date | none in the evals or the suites, so none needed a re-aim |
| Checks in the `lab-tracker` case | 126 (123 before) |

## The gate

`python check.py`, the trace variable unset in the command: ALL CHECKS PASSED. Three eval cases
checked, none failed.

## The operator's trace file

Every suite, the beat and the measurement scripts ran with the variable removed. The file held
31 lines before the first run of this execution and 31 after each run since.
