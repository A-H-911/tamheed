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

## As built (2026-11-12, branch `round/6.5.0`)

- `_ENUM_CHECK_RE`, `_enum_sets(conn, table)` and `_enum_hint(conn, table, cols)` in the server.
  The hint is appended at the five sites the plan names. `audit_record` and `progress_update` also
  name the failing item (`verdicts[1]`, `entries[1]`) and say the batch was not applied.
- `_VERDICT_VALUES` feeds `_AUDIT_RECORD_DESC`. `_PROGRESS_UPDATE_DESC` lists the eight kinds a
  caller may write (the journal kinds minus the four the server appends).
- The CLAUDE.md note's audit row names the two value sets. `package-writes` section 3 has a
  bullet for value sets, the gate words included.
- The four gate words are defined in `governance.md` (a new section), and taught in `workflow.md`
  Stage 16, `phase-close`, `release-close-out`, the catalog row, `docs/entities.md` and the
  guide's `event.gate-decision` prose in English and Arabic. `review-prompts.template.md` says its
  go / no-go is the package verdict, not a gate outcome.

## Validation

- Red first: two tests failed before the engine change (the bare SQLite text, and no
  `_enum_sets`). After it the contract suite runs 236 tests, all green. The older assertion that
  the store's CHECK text is still present (`progress_update` with a bad kind) holds unchanged.
- One refusal now names both bad values of an audit item, with both sets. A gate outcome `No-go`
  is answered with the four words. A relation outside the vocabulary is answered with the sixteen.
  A defect status outside its set shows `Won't-fix` whole. A failure that is no value-set failure
  gains no words.
- `python check.py`: ALL CHECKS PASSED. Lint 14 found one long sentence in `docs/entities.md`
  first. It was split. The selftest registers 19/19 tools, the longest description 558 characters.
- Reviews, folded in before the commit. The advisor and an independent code review each found
  the same flaw: the header column `mode` has a compound CHECK (a value list OR `stage:*`), and the
  first parser read its list as a value set, so a legal `stage:3` could be named as bad. The
  parser now balances the parentheses of each CHECK and reads only one that is a value set and
  nothing else. It reads 94 sets on the live schema. A test walks every table and holds each
  set to a real column with text values.
- The sites as built differ from the plan body. The header write gained no hint: its only value
  set is the compound one, and `profile` is frozen there. `package_create` gained one instead: a
  profile outside its set was answered with the bare SQLite text (found by the advisor probe).
  So the hint is at five sites: the `entity_upsert` item, the ignore path, `audit_record`,
  `progress_update`, and `package_create`.
- The review also found that a value that is no text (a number for `verdict`) gained no hint. It
  does now, and an absent value is never named. Both are asserted.
- Four teaching sites were missing after the first pass and are in: the governance template (a
  generated package reads it), the phase-exit prompt in the follow-up template, the front door,
  and the server README row of `audit_record`.
- Final state: 236 contract tests green, `python check.py` ALL CHECKS PASSED, the selftest 19/19
  with the longest description at 558 characters. Python 3.10 is proven by CI only.
