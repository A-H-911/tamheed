# Plan 221 -- the read names every link (FB-030, FB-032, FB-009)

> Status: PLANNED 2026-11-11. Cycle: field round 2026-11 (ACMP FB-030..032, Jisr FB-001..011),
> release 6.5.0, branch `round/6.5.0`. The round record (evaluation, rulings R81-R89, risks,
> execution order) is [field-round-2026-11-record.md](evidence/field-round-2026-11-record.md).

- `trace_query(entity_id=None, direction="both", relation=None, type=None, limit=None)` (srv:2611).
  With `entity_id`: one entity, as today. Without it: every edge, or one family's with `type`.
  `ORDER BY from_id, to_id, relation`. Result: `edges`, `count`, `total`, `column_links`
  (grouped: `{"table.column": [[from, to], ...]}`), `column_count`, `column_total`, `columns_read`,
  `columns_skipped`, `query`. `limit` caps each list. A given `relation` leaves `column_links` empty.
  Measured cost of the default on ACMP's largest slice: 6.0 KB (249 links), against 17.5 KB as flat triples.
- Column links come from `PRAGMA foreign_key_list` over the id-keyed tables (the call srv:2406
  already makes), so a new FK column is read with no code change. The journal's columns are skipped
  and named in `columns_skipped` (measured on ACMP: 740 journal rows name PH-7, against 157 other links).
  The derivation was run on ACMP's rows before this plan was written: FR-166 returns AC-184 by
  `acceptance_criteria.requirement_id`, SL-043 returns its 39 criteria among 249 links, and the whole
  store holds 2,422 column links over 45 columns beside 1,928 edges.
- An unknown `relation` and an id no row has still answer ok and empty, as today, and now carry a
  `warning` that names the cause (a mistyped name read as "no links" is the class of ACMP's LL-149).
  No existing answer becomes a refusal. An unknown `type` is refused, and `type` is new.
- `entity_query`: `query` echoes every argument the call passed. The `trace-edge` refusal points at the bulk form.
- `entity_export` (srv:1710): `partial` also reads `column_count < column_total`.
- Teaching, the fields' two lessons upstreamed as facts: a link lives in ONE place (an edge or a
  column), and a census names which it read. `traceability.md`, `integrity-check` step 3 (a census
  in one call, exported for a script), `slice-review:22`, `slice-kickoff:27`, `modes.md:50`,
  `package-writes:105`, the server README row, `TOOLS["trace_query"][1]`.
- Tests: re-aim `test_mcp_contract` 506, 2535, 3743. New: the bulk read equals the table, in order,
  twice byte-identical through `entity_export`. A criterion linked by column alone appears under
  `column_links` (the FB-032 case, red first). A slice returns its criteria. The journal is skipped
  and named. `limit` sets `partial`. The two warnings and the `type` refusal. `query` on parallel-shaped calls.
- **Check:** red-first tests, `check.py`, and the read replayed on a scratch copy of ACMP.
  **Expected:** `trace_query("FR-166")` shows AC-184, an export of every link is byte-identical
  twice, and no existing call returns less than it did.

## As built (2026-11-11, branch `round/6.5.0`)

- `_fk_columns`, `_column_links` and the rewritten `trace_query` in the server. `entity_query` and
  `trace_query` echo their arguments under `query`. `entity_export` reads `partial` from either list.
- The registered description `_TRACE_QUERY_DESC`. The `trace-edge` refusal names the bulk form.
- Teaching: `traceability.md`, `modes.md`, the server README row, and the skills
  `integrity-check`, `slice-review`, `slice-kickoff`, `package-writes`.
- The guide: two new parameter ids in English and Arabic, the tool and entity-id prose re-aimed,
  the line cites moved by `plans/evidence/scripts-221/shift_221.py` (two re-aimed by hand: the
  rewritten function has no equal block to map).

## Validation

- Red first: seven tests failed before the engine change (two failures, four errors, one re-aim).
  After it and the two reviews the contract suite runs 228 tests (222 before), all green.
- `python check.py`: ALL CHECKS PASSED. Lint 14 found two long sentences in the new prose first.
  Both were split.
- Replay through the real handlers on a scratch copy of the first field package (never the live
  one): `trace_query("FR-166")` returns AC-184 under `acceptance_criteria.requirement_id`.
  `trace_query("SL-043")` returns 249 column links, 39 of them criteria, in 7.8 KB. An export of
  every link holds 1,928 edges and is byte-identical on a second run. A relation outside the
  vocabulary answers empty with a warning that names the sixteen.
- The macOS baseline that the round needed first: CI run 43080522933 on `1f15d98`, eleven jobs,
  every job green, both macOS legs among them, with no engine change on the branch.
- Reviews, folded in before the commit. The advisor: `type="trace-edge"` was answered as an
  unknown type (the false statement plan 025 forbids), and the export note named `after_id` and
  "3 of 3 rows" when only the column links were cut. Both fixed, each with an assertion. An
  independent code and security review: no critical or high finding. Every value is a bound
  parameter, and table and column names come from the registry or the schema. Its findings: the
  echo carried the clamped `limit` (now the caller's own value), and six behaviours had no
  assertion (direction and family for column links, a self-referencing column, `limit` 0 and
  negative, the echoed arguments, a direct cut). All six are asserted now.
- `uv run plugins/tamheed/server/tamheed_server.py --selftest`: 19/19 tools registered, the
  longest description 558 characters. Python 3.10 is proven only by CI: no 3.10 interpreter is
  on the maintainer machine.
