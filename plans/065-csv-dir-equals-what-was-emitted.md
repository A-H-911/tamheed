# Plan 065: `csv/` is exactly what `export_html` emits

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [063-074-batch-findings-25.md](063-074-batch-findings-25.md). Run last among the code plans so
> any fixture regeneration would happen once.

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: MEDIUM (the exporter now DELETES files)
- **Category**: derived-output integrity (findings_25 s2) - **Planned at**: commit `2e2d9e5`

## Why this matters

findings_25 s2: `csv/prompts.csv` - 92 rows for a table the 3.0.0 migration converted away - sat
in a fully tool-owned directory for two months, and `package_verify` returned `foreign: []`
truthfully, because its foreign check covers `data/` only. Reading the exporter showed the class
was wider than reported: the per-table loop skips an empty table with a bare `continue`, so ANY
table that becomes empty kept its stale CSV forever.

## What changed

- `export_html`: after emitting, every `csv/*.csv` it did not just emit is either **removed**
  (reported under `csv.removed`) or **reported** under `csv.unowned` and left alone. A file is
  removed only when ALL hold: it sits in the PACKAGE's own `csv/` (a caller-chosen `output`
  directory is not the engine's - report only); it is a regular file, not a symlink; and its
  first line equals the header this exporter writes for a table of that name (current tables'
  column lists, plus `_RETIRED_CSV_HEADERS` for `prompts`). Name matching is case-folded.
- `package_verify` gains `foreign_csv` (names in `csv/` that are not `<table>.csv`), reported
  like `foreign`: it never flips `verified`.

## Measured (the approval's open assumption)

A scratch re-export of the lab fixture with the new exporter: 25 CSVs `unchanged`, `removed: []`,
`unowned: []`, `csv/` and `review.html` byte-identical to the committed fixture. No fixture churn.

## Review round (security + Python reviewers, before commit)

- CRITICAL: header equality alone is not ownership - headers are the fixed schema, identical in
  every tamheed package, so with `output=` pointed at a shared directory a second package's export
  would delete the first package's CSVs. Closed: deletion is confined to the package's own `csv/`
  (found independently and fixed before the report landed; tested with OUR header in THEIR dir).
- HIGH: on a case-insensitive filesystem a pre-existing `Defects.CSV` IS the file just emitted as
  `defects.csv`; an exact-name test missed it and the header match would have deleted what was
  just written. Closed by case-folding, with a test that holds on both OSes.
- MEDIUM: a failing directory scan could turn a successful export into an exception. Now
  `csv.cleanup_error`, never raised.
- MEDIUM (Python reviewer): the expected header was a hand-built join; it is now produced
  by the same `csv.writer` that emits the file, so the two cannot drift. `foreign_csv`
  deliberately lists EVERY entry in `csv/` that is not `<table>.csv` (subdirectories
  included), mirroring `foreign` for `data/`: the directory is tool-owned.
- Checked safe: no path reaches `unlink` that is not a dirent of `csv/`; a symlink is never
  followed for deletion (and is now not even read); a directory named `x.csv`, a BOM or a CRLF
  first line all fall to `unowned`.

## Tests

`test_csv_dir_is_exactly_what_export_html_emits`: an emptied table's CSV and the retired
`prompts.csv` are removed; an operator's `notes.csv` and a file with OUR name but THEIR header
survive and are reported; `package_verify` names the foreign files and stays `verified`; a second
export settles; a case-variant of a live table's file survives; nothing is deleted in a
caller-chosen output directory. RED (KeyError) before, GREEN after.

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (154)
- [x] `python check.py` -> `ALL CHECKS PASSED`; lab fixture byte-identical on re-export
- [ ] CI green on Ubuntu and Windows (case sensitivity differs between them)

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts, goldens untouched.
