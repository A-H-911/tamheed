# Lab continuation report — beat 29 (plan 158, v5.6.1)

> 2026-09-28. Harness: the engine's tool functions in-process, the same code path the MCP tools
> call, and the exporter's `render` called directly for the two dates. The scratch phase ran
> FIRST on a copy that is never committed; the fixture was written after it held. The operator's
> trace variable was removed before the engine was imported. This beat runs no hook.
> Scripts beside this report: [`scripts-findings-38/`](scripts-findings-38/) (`beat29.py`, its
> output `beat29.out.txt`, `m38.py`, `m38.out.txt`).

## Runs

| Run | Window (UTC) | Result |
|---|---|---|
| 1 | 09:50:39–09:50:41 | every assertion held in both phases |

## Scratch phase (hard assertions)

| Observation | Value |
|---|---|
| `package_verify("package")`, package closed, before any export on this release | `review_current: true`, `review_exported_by: "5.6.0"` |
| The first export, before any write | 1 line changed: the stamp, from `5.6.0` to `5.6.1`. The digest did not move |
| The UTC date of that export against the date the page carried | the same, `2026-09-28`. On a later date the assertion expects 2 lines |
| `package_verify` after it | `review_current: true`, `review_exported_by: "5.6.1"` |
| `entity_query("progress-entry", limit=10)`, the journal holding 55 entries | `PE-001` to `PE-010`, the ten lowest |
| The resume block's `last_entries` | `PE-055`, `PE-054`, `PE-053`, the three highest |
| Ids the two reads share | none |
| Before any write: `handoff_behind`, and the ids `handoff-current` names | 0, none |
| After ONE `work-done` entry | `handoff_behind` 1; `handoff-current` names that entry; `entity_query(ids=[...])` reads it back |
| `render` over one store and one fixed report, dates `2999-01-01` and `2999-01-02` | each date occurs once in its page; the pages differ; one page with its date replaced equals the other byte for byte |
| The line that holds the date | 4,653 characters: the whole Readiness section |
| `export_html(output=<a path outside the package>)` | the page written there; the package's `review.html` and 26 `csv/` files keep their hashes |
| `review_current` of the package's own page after that export | `false`: it still lacks the work entry |

## Fixture phase

| Observation | Value |
|---|---|
| `package_verify("package")` before the package was opened | `review_current: true`, `review_exported_by: "5.6.0"` |
| `server_info` | 5.6.1 / `007_handoff.sql` / schema 7 |
| The resume block at open | beat 28's final handoff `PE-055`, `handoff_behind` 0 |
| `handoff_emit(refresh_stock=true)` | `refreshed ["prompts/README.md"]`; every scan empty |
| The guide | reads `tamheed v5.6.1`; one line in, one line out, the title |
| The second emit | reports `CLAUDE.md` unchanged |
| The beat's note and final handoff | `PE-056`, then `PE-057`, the handoff written last |
| `handoff-current` | `pass` |
| `review_current` right after the handoff | `false`: the handoff is a write |
| `export_html`, after the handoff | the page carries the `5.6.1` stamp and names `PE-057` as the latest handoff |
| The page's date before and after | `2026-09-28` both |
| `gate_run` | ready |
| `package_verify` | `verified: true`, `dirty: []`, `foreign: []`, `review_current: true`, `review_exported_by: "5.6.1"` |
| `data/.lock` after `package_close` | gone |

## What the fixture changed

| File | Change |
|---|---|
| `data/progress_entries.jsonl`, `csv/progress_entries.csv` | two entries |
| `prompts/README.md` | the title |
| `review.html` | 15 lines in, 15 out: the digest and the version stamp; the freshness line at the head of each of the eleven sections; the journal and the resume section |

Every section opens with the freshness line, the newest stored timestamp. So any store write
moves one line per section on the next export. The date of the Readiness section is a second,
separate input, and it did not move in this beat.

## Evals

| Change | Count |
|---|---|
| Assertions re-aimed: the latest handoff's id, the guide's version, the page's stamp, the count of handoff entries | 4 |
| Assertions added: three sentences of the beat's note | 3 |
| Checks in the `lab-tracker` case | 123 (120 before) |

## The gate

`python check.py`, the trace variable unset in the command: ALL CHECKS PASSED. Three eval cases
checked, none failed.

## The operator's trace file

Every suite, the beat and the measurement script ran with the variable removed. The file's
line count over the execution is in the batch record.
