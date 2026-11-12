# Plan 225 -- a section can be retired (FB-011, R85)

> Status: PLANNED 2026-11-11. Cycle: field round 2026-11 (ACMP FB-030..032, Jisr FB-001..011),
> release 6.5.0, branch `round/6.5.0`. The round record (evaluation, rulings R81-R89, risks,
> execution order) is [field-round-2026-11-record.md](evidence/field-round-2026-11-record.md).

- `db/migrations/009_section_status.sql`: `ALTER TABLE document_sections ADD COLUMN
  lifecycle_status TEXT CHECK (lifecycle_status IN ('Superseded','Obsolete'))`. Empty means live.
  Nullable by necessity: `store.load` binds an explicit NULL for a column an old row lacks (store.py:372).
- Two scans read sections (`_graded_text` srv:641, `_scan_prose_ids` srv:457). Both select live rows
  with a literal that drops a NULL status. One NULL-safe constant replaces every copy of that
  literal. Measured on an in-memory schema (SQLite 3.50.4): after the `ALTER`, the literal keeps no
  live section and the NULL-safe form keeps them all. The added CHECK is in `sqlite_master`, so 223's hint reads it.
- `entity_query("document-section", status=...)` changes from a refusal to a filter that selects
  retired sections. A live section has no status, so no status value selects it. The description says so.
- Retire recipe (taught in `governance.md`, `package-writes`): the status, plus a `supersedes` edge
  from the kept section. The review page's section register shows the status (sections render only
  there, export_html.py:786). No row leaves the store, which keeps `SECURITY.md:150` true.
- Upgrade path: in a field package the column arrives inside 226's registry-sync preview
  (`columns_added`), and the confirm rewrites `document_sections.jsonl` once. If 226 leaves the
  release, no sync opens (srv:5061). The prompt then names the silent rewrite at the first close and
  runs that close before any `package_verify`, which reads the file as `dirty` until then.
- Tests: `test_store_migrations`, the schema head pins (`test_mcp_contract:244, 3239`), a live
  section is still graded, a retired one leaves both scans, the status filter. Goldens regenerated
  by script (the eval fixture pins `verified=True`, evals/evals.json:857).
- **Check:** red-first tests, `check.py`, and `git diff --stat` on the fixtures shows only
  `document_sections.jsonl` files. **Expected:** schema head 9, every fixture verifies clean.

## As built (2026-11-12, branch `round/6.5.0`)

- `db/migrations/009_section_status.sql`: one nullable column, appended.
- `_LIVE_ROWS` in the server, in place of all six copies of the live-row literal (three generic
  scans and three reads of prompt rows).
- The registered description of `entity_query` says that `status` returns retired sections for
  that family, and that `query` echoes the arguments (owed from plan 221).
- `CHANGELOG.md` gains an `[Unreleased]` section that names the migration (lint 7). The release
  stamp turns it into the 6.5.0 entry.
- Teaching: `governance.md` (supersession), `package-writes` section 7b, the catalog row,
  `docs/entities.md`, and the guide sentence that counted seven families with their own status
  set (eight now), in English and Arabic.
- Pins moved: schema head 8 to 9 in the contract suite, and in two resume-hook assertions that
  the plan had not named.

## Validation

- Red first: the migration test and the behaviour test failed before the change. After it the
  contract suite runs 241 tests and the migration suite 12, all green.
- A live section with a placeholder still fails the content gate, and its dangling id is still
  read. Retired, it leaves both scans, its id resolves, and `status=` finds it. A status outside
  the two words is refused with the set (plan 223).
- Fixtures: the demo sample and the three eval packages each rewrote `document_sections.jsonl`
  once, through the engine (an open and a close). No other fixture file moved. The first run of
  the demo-sample test did the rewrite itself and failed once on its bytes-unchanged assertion,
  which is the one-time rewrite the plan names.
- Replay through the real handlers on scratch copies of both field packages, the second from
  the export of 2026-11-12. On each: the package opens, `package_verify` names
  `document_sections.jsonl` as dirty until the first close, the close rewrites that file only,
  and the next verify is clean. Every gate keeps the status it had under 6.4.0 (the second
  field's G-PROGRESS failed before and fails the same way). The first field holds 633 sections,
  the second 486.
- `python check.py`: ALL CHECKS PASSED. The selftest registers 19/19 tools.
- CI before this commit: plan 224a at `1e1d8c5`, run 43132347892, green on eleven jobs. That run
  was the first to execute the Linux boot-session path.
- Reviews, folded in before the commit. An independent code review: no critical, high or medium
  finding. It swept every read of `lifecycle_status` in the bundle and the guide generator, and
  found no other NULL-unsafe read that can run over sections. Its low findings and the advisor's
  are pinned by one more test: the status shows on the review page and in the CSV, it survives a
  close and a reopen, `Obsolete` leaves the scans too, an omitted key keeps the status, an
  explicit null un-retires and the write names the column, and a file written before the column
  existed loads, reads dirty until the first close, and is clean after it.
- Stated, not changed (the review, low): retiring a section of an Approved document needs no
  word and writes no journal row, as a section edit never did. A `supersedes` edge between
  sections of two documents is accepted. `status=` cannot select live sections.
- The governance template carries the retire rule too (a generated package reads that copy).
- The fixture rewrite is `plans/evidence/scripts-225/rewrite_fixtures_225.py`. Run twice, the
  second run changes nothing.
- The export manifest of 2026-11-12 was checked first: 130 files listed, 130 matched.
- Final state: 242 contract tests green, `python check.py` ALL CHECKS PASSED.
