# Lab continuation report — beat 31 (plan 168, v5.8.0)

> 2026-09-30. Harness: the engine's tool functions in-process, the same code path the MCP tools
> call. The scratch phase ran FIRST on a copy that is never committed; the fixture was written
> after it held. The operator's trace variable was removed before the engine was imported. This
> beat runs no hook. The previous engine (the `v5.7.0` tag, `git archive`) ran in its own
> process for the byte check.
> Scripts beside this report: [`scripts-fb026-fb027/`](scripts-fb026-fb027/) (`beat31.py`, its
> output `beat31.out.txt`, `render_with.py`, `bytecheck.py`; the cycle's census scripts and
> their outputs: `records.py`, `records_census.py`, `reselect.py`, `m73_repeated.py`,
> `sim_lines.py`, `export_diff.py`).

## Runs

| Run | Window (UTC) | Result |
|---|---|---|
| 1 | 18:57:06–18:57:09 | every assertion held in both phases |

The operator's trace file held 42 lines before the run and 42 after it.

## Scratch phase (hard assertions)

| Observation | Value |
|---|---|
| `package_verify("package")`, package closed, before any export on this release | `review_current: true`, `review_exported_by: "5.7.0"` |
| The resume block at open | handoff `PE-059`, behind 0 |
| `handoff-repeated` on the fixture's own journal | emitted (population 9 handoffs), **pass**, no entity |
| Three handoffs sharing one line of 57 characters, beside a heading line and a 10-character line | **fail**; entities `["PE-060"]`; the note's detail `line 3 of PE-062 since PE-060 (3 handoffs)`; lines 2 (the heading) and 4 (the short line) not named; no line's text in the note |
| A fourth handoff that re-measured the line and wrote the date | **pass**, no entity |
| The first export on the release, after the four handoffs | the stamp reads `5.8.0`; the store digest unchanged by the export; every `<tr id=` starts its line; no line holds two `</tr>` or two `<path ` |
| The byte check: the 5.7.0 engine's render of the fixture's store (before the handoffs) against the 5.8.0 engine's render of a twin copy, same date | **EQUAL** after the newlines between tags are removed and the stamp replaced (plan 165's one readiness row taken out with its count); 295 → 1,082 lines |
| The twin's `csv/` after the outside render | every file's hash unchanged |
| The two registered descriptions | `progress_update` 333 characters, `audit_record` 325; each names its argument and every key of its constant, under the 2,048 cap |

## The fixture (committed)

| Observation | Value |
|---|---|
| Before the first export | `review_current: true`, `review_exported_by: "5.7.0"` |
| `server_info` after open | `5.8.0` / `007_handoff.sql` / schema 7 |
| The resume block | handoff `PE-059`, behind 0, skill `tamheed:package-writes` |
| `handoff_emit(refresh_stock=true)` | refreshed `["prompts/README.md"]` (the guide reads `tamheed v5.8.0`); every scan empty; the second emit reports `CLAUDE.md` unchanged |
| The note | `PE-060`, quoting the four sentences the evals grep |
| The final handoff, written LAST | `PE-061`; `handoff-current` pass and `handoff-repeated` pass, read after it; the handoff shares no line with the two before it |
| The export | the page re-flows once: 295 → 1,088 lines, `git diff --numstat` `815 22`; its stamp `5.8.0`; its date `2026-09-29` → `2026-09-30` |
| `gate_run` | ready |
| `package_verify()` | `verified: true`, `dirty: []`, `foreign: []`, `review_current: true`, `review_exported_by: "5.8.0"` |
| `package_close` | no `data/.lock` remains |

## The evals

Four assertions re-aimed by script (`handoff=PE-061 behind=0`; `tamheed v5.8.0`; the stamp;
ten handoffs) and four added: `handoff-repeated=pass`; the page's final-handoff row starts a
line (`grep-file` with a needle that begins with a newline); the note's sentence on the rule;
the note's sentence on the page. `python check.py`: ALL CHECKS PASSED, 169 checks.
