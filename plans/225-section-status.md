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
