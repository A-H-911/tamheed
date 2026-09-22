# Plan 093: `prompt-ids-resolve` — the project's prompt files, scanned like rows

> Reviewer-executed (maintainer-delegated), 2026-09-22. Batch map:
> [091-099-batch-findings-28.md](091-099-batch-findings-28.md).

## Status

- **Priority**: P1 (the field ranked it first) - **Effort**: S - **Risk**: LOW (advisory; never blocks)
- **Planned at**: `a8e5f8a`

## Why this matters (ACMP's `FB-002`)

`prose-ids-resolve` scans rows. The kickoff prompt - 7,000 lines at ACMP, the prose a session reads
BEFORE it runs any tool - was scanned by nothing, and the field's only checker read the JSONL and
was deleted for it. A phantom in a row was caught; the same phantom in the prompt was invisible.

## What changed

- `_id_universe` and `_classify_id_hits` extracted from `_scan_prose_ids` (unchanged behavior), so
  rows and files share one classifier.
- `_scan_prompt_ids(conn, pkg_dir, name)`: every `<package>/prompts/*.md` that is NOT byte-equal to
  any stock body in `stock-history.json` (any release; `{package}` substituted) or the current
  bundle - the maintainer's prose is never the project's citation; customised and project-authored
  files are scanned; entities `prompts/<file>:<line> -> <id>`.
- The advisory `prompt-ids-resolve` beside `prose-ids-resolve`: the same three lists, each capped
  with the "showing N of M" clause; `population: {table: "prompts/*.md", rows: <files>, scoped: false,
  unit: "files"}` - the uniform shape (ACMP's census reads `population.rows` on every rule); zero
  scanned files -> `indeterminate` set explicitly, never through the omission lookup.
- **A code span may wrap a line in a prose file** (CommonMark), and a stock prompt does
  (`skill-promote.md:31-32`). Row text keeps the one-line rule (`_INLINE_CODE_RE`); prompt files are
  stripped with `_INLINE_CODE_WRAPPING_RE` over the whole file, then hits are labelled by line.

## Measurement that changed the plan

The batch plan said to backtick a bare `LL-007` in `skill-promote.md`. Re-measured with the wrapping
rule: it already sits inside a two-line code span, and the seventeen stock prompts hold ZERO bare
phantoms against the lab fixture. My first census stripped code per line and miscounted. No stock
body changes in this plan; ACMP's copies do not lag.

## Tests

`test_prompt_ids_resolve_scans_the_projects_prompt_files_not_stock`: stock-only folder ->
`indeterminate` with `rows: 0`; a project prompt with a bare phantom fails on it, a backticked
history id lands in `in_code_spans`, `SEC-8` in `not_well_formed`, `KPI-17_score` nowhere; a
stale-stock file (an older release's body) is not scanned; backticking the phantom flips the rule
to `pass` with the id still visible. RED (`KeyError`) before, GREEN after; suite 168.

## Done criteria

- [x] contract suite OK (168)
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green
