# Plan 223 -- a refused value names what the column takes (FB-002, FB-003, R83)

> Status: PLANNED 2026-11-11. Cycle: field round 2026-11 (ACMP FB-030..032, Jisr FB-001..011),
> release 6.5.0, branch `round/6.5.0`. The round record (evaluation, rulings R81-R89, risks,
> execution order) is [field-round-2026-11-record.md](evidence/field-round-2026-11-record.md).

- `_enum_sets(conn, table)` parses `CHECK (col IN (...))` from `sqlite_master` (never from SQLite's
  message, which differs by build). `_enum_hint(conn, table, cols)` names every bad value of the
  item at once. Appended at five places: the `entity_upsert` except (srv:2392), the trace-edge
  ignore path (srv:2221, an unknown relation gets its vocabulary), `audit_record` (srv:3544, with the
  item index), `progress_update` (srv:3477), the package header (srv:802). The store's CHECK still refuses.
  Measured on the live schema: the parser reads 97 value sets, `Won't-fix` included. The two integer
  sets (`mvp`, `pinned`) carry no text value and are skipped.
- `_AUDIT_RECORD_DESC` and `_PROGRESS_UPDATE_DESC` name their values from constants. A contract
  test ties each constant to the DDL. `package-writes` section 3 and the note's obligation row follow.
- Gate words defined once and taught where a session writes a gate: `governance.md`, `workflow.md`
  Stage 16, `package-writes`, the catalog row, `phase-close`, `release-close-out`, the server
  README, `docs/entities.md`, `content.py`. `review-prompts.template.md:24` says its go / no-go is
  the package verdict (`go_no_go`), not a gate outcome.
- Tests: `test_mcp_contract:3654` stays green (the CHECK text remains). New: two bad audit values
  come back in one refusal with both lists. A gate outcome `No-go` names the four words. An unknown
  relation names the sixteen. The description needles.
- **Check:** red-first tests, `check.py`, the selftest (every description under 2,048 characters).
  **Expected:** one refusal names every bad value of an item, on any SQLite build.
