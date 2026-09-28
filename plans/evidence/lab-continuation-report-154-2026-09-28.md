# Lab continuation report — beat 28 (plan 154, v5.6.0)

> 2026-09-28. Harness: the engine's tool functions in-process, the same code path the MCP tools
> call; the hook in-process, and once as its own process from a copy of the bundle. The scratch
> phase ran FIRST on a copy that is never committed; the fixture was written after it held. The
> operator's trace variable was removed before the engine was imported, and the beat's own hook
> runs wrote to a trace file inside the scratch folder.
> Scripts beside this report: [`scripts-findings-37/`](scripts-findings-37/) (`beat28.py`, its
> output `beat28.out.txt`, `m37.py`, `m37.out.txt`).

## Runs

| Run | Window (UTC) | Result |
|---|---|---|
| 1 | 06:01:24–06:01:27 | every assertion held in both phases |

## Scratch phase (hard assertions)

| Observation | Value |
|---|---|
| `package_verify("package")`, package closed, before any export on this release | `review_current: true`, `review_exported_by: null` |
| The page it read | exported by 5.5.0 at beat 27: the digest stamp in its head, no version stamp |
| The hook on a project with the note, `source=compact` | `version=5.6.0 source=compact lines=7 chars=1152 status=printed session=<the id sent>` |
| That line's counts against the printed block | equal: 7 lines, 1,152 characters |
| The block's first line | names no version |
| The hook on an empty folder, `source=startup` | `version=5.6.0 source=startup lines=0 chars=0 status=silent session=<the id sent>` |
| A copy of the bundle without `.claude-plugin/`, its hook run as its own process | exit 0, nothing printed, exactly one line: `version=- source=resume lines=0 chars=0 status=silent session=<the id sent>` |
| The first export | the page rewritten; the digest unchanged; `<meta name="tamheed-version" content="5.6.0">` in the head, before the title |
| `package_verify` after it | `review_current: true`, `review_exported_by: "5.6.0"` |
| A second export | byte-identical |
| A journal write after the export | `review_current: false`, `review_exported_by: "5.6.0"` |
| The export after that write | `review_current: true` |
| A page stamped `5.5.0` | `review_current: true`, `review_exported_by: "5.5.0"` |
| A stamp that is not a plain token | `review_exported_by: null` |

## Fixture phase

| Observation | Value |
|---|---|
| `package_verify("package")` before the package was opened | `review_current: true`, `review_exported_by: null` |
| `server_info` | 5.6.0 / `007_handoff.sql` / schema 7 |
| The resume block at open | beat 27's final handoff `PE-053`, `handoff_behind` 0 |
| `handoff_emit(refresh_stock=true)` | `refreshed ["prompts/README.md"]`; every scan empty |
| The guide | reads `tamheed v5.6.0`; one line in, one line out, the title |
| The second emit | reports `CLAUDE.md` unchanged |
| The beat's note and final handoff | `PE-054`, then `PE-055`, the handoff written last |
| `handoff-current` | `pass` |
| `review_current` right after the handoff | `false`: the handoff is a write |
| `export_html`, after the handoff | the page carries the version stamp and names `PE-055` as the latest handoff |
| `gate_run` | ready |
| `package_verify` | `verified: true`, `dirty: []`, `foreign: []`, `review_current: true`, `review_exported_by: "5.6.0"` |
| `data/.lock` after `package_close` | gone |

## What the fixture changed

| File | Change |
|---|---|
| `data/progress_entries.jsonl`, `csv/progress_entries.csv` | two entries |
| `prompts/README.md` | the title |
| `review.html` | 15 lines in, 14 out: the version stamp, the digest, the journal and the resume section |

## What the beat does not cover

- **A session that kept the old hook.** The beat runs one hook, this release's. A line with no
  `version=` is what a hook older than 5.6.0 writes; the contract suite does not run an old hook
  either. The field's trace is the instrument.
- **A bind.** The lab commits nothing, so the order bind, export, commit is shown only as its
  mechanism: a write makes the page stale, and the next export makes it current.
- **`minimal-brief/review.html`.** Untouched. It carries no version stamp and reads `null`.

## The operator's trace file

16 lines when the cycle's first read was taken and 16 at the close, the last at 04:53:14Z. Every
suite, beat and gate of this batch ran after 05:39Z. No line falls inside a run's window.

> **Corrected 2026-09-28, in the close-out commit.** This section first read "12 lines at the
> batch's start and 16 now; the four new ones are the field's and the maintainer's own sessions".
> Twelve was the count at the end of the previous cycle. The file held 16 before this batch ran
> anything. The conclusion did not move; the premise was wrong. The advisor caught it.
