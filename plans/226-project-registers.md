# Plan 226 -- project registers (FB-004/005/006, R81) - final shape after Step 0

> Status: PLANNED 2026-11-11. Cycle: field round 2026-11 (ACMP FB-030..032, Jisr FB-001..011),
> release 6.5.0, branch `round/6.5.0`. The round record (evaluation, rulings R81-R89, risks,
> execution order) is [field-round-2026-11-record.md](evidence/field-round-2026-11-record.md).

- `db/migrations/010_registers.sql`: `registers` (`REG-`: title, purpose, standard lifecycle,
  provenance) and `register_entries` (`ENT-`: `register_id`, title, body, lifecycle). No new JSON
  column. The declaration lives under the register's `custom_attributes.fields` (a list of
  `{name, required?, values?, refs?}`), and an entry's values live in its own `custom_attributes`.
  Reason: the content gate grades every other text column, so an allowed value such as `TBD` would
  fail it, and eight server sites already treat `custom_attributes` as JSON. The engine already
  reads keys there (`fenced`, `converted_from`). A real column stays possible later (extension.md:45).
- Index triggers, `ENTITY_TABLES`, `BASELINE_ENTITY_TYPES` as `On-request` (no existing package
  fails G-SET), the prefix list at `check.py:434`. Both prefixes are free in ACMP, the local Jisr copy
  and the four fixtures. They are measured again on Jisr's current text at the checkpoint.
- Write guard in `entity_upsert`, placed on the materialised row so a `substitute` cannot pass it.
  For an entry: an undeclared key, a missing required field, a value outside the declared list
  (223's wording), a `refs` field naming no row. For a register: a malformed declaration.
- A family the package's registry does not know yet is refused with the route (`package_migrate`
  registry-sync). Today that write returns a bare foreign-key text (srv:2401).
- Advisory `register-entries-conform`, emitted only when a register exists.
  `entity_query(register_id=...)` filters entries (the `plugin_skill` precedent).
- Trace: `relates_to` only. A guessed typed relation is the `binds_to` lesson. The review page's
  generic loop skips `register_entries`, and one table per register renders the declared fields
  (one fold per table, `test_export_html:567`).
- Docs: catalog, governance, naming template, `artifact-rules.md` (declare a register, never
  overload DEP/OQ/SEC rows), `extension.md`, `docs/entities.md` (family, lifecycle, decision row),
  `CONTRIBUTING.md:116`, the front door, `package-writes`.
- Design checkpoint (an operator interview, when the Step 0 folder is here): Jisr's three registers
  are replayed through the family on a scratch copy, every refusal counted. Put then: the two
  prefixes, the declaration grammar, and what the Jisr prompt recommends about moving existing rows.
- Tests: the store round-trip, each guard (through `substitute` too), the advisory with its
  population, registry-sync on a 6.4.0 fixture, the unknown-family refusal, the page tables.
- **Check:** the replay's refusal count is put to the operator before the build, then red-first
  tests and `check.py`. **Expected:** schema head 10, tables 44, package rules 31.

## Design checkpoint (2026-11-12, on the second field's export; shapes and counts only)

The export's manifest matched (130 files). Its three registers were measured in memory, and a
draft declaration per register was checked against the real rows by a pure-function guard.

| Register in the field | Stored today as | Rows | Keys | Refused by the baseline guard |
|---|---|---|---|---|
| interview topics | open questions | 292 | 16 | 280 |
| question bank | sections of one document | 292 | 21 | 292 |
| evidence findings | sections of one document | 36 | 13 | 36 |
| source authorizations | dependencies | 2 | 15 | not run (two rows) |

Every refusal came from a reference field or from the meaning of required. Value sets fit.
- Ids are kept joined in one string in five fields, and as prose that names ids in others.
- Two fields point at a topic number of the same register, not at a row id.
- One value set carries prose qualifiers, so it is free text in practice.
- Values are also lists, one mapping (the options of a question), booleans and numbers.
- A key present in every row often holds an empty list.

### Rulings taken at the checkpoint

- **R93 (2026-11-12): a reference field holds one id or a list of ids, and each must name a row.**
  A string of joined ids is not split. Such a field is declared as plain text until the project
  converts it, which is the project's own scope change.
- **R94 (2026-11-12): the prefixes are `REG-` and `ENT-`.** Both occur nowhere in either field
  package or in the four fixtures. `REC-` occurs in the first field's text.

### What the measurement changes in the design

- `required` means the key is present and not null. An empty list, `false` and `0` are values.
- A value set applies to a text value. A list, a mapping, a number or a boolean in a field with
  no declared set is accepted as it is.
- The field prompt says plainly that the existing rows do not pass a strict declaration as they
  stand, and what a conversion would have to do.

## As built (2026-11-12)

- `db/migrations/010_registers.sql`: `registers` (`REG-`) and `register_entries` (`ENT-`), their
  index triggers, one index on `register_id`. Both families are On-request in
  `BASELINE_ENTITY_TYPES`, so no existing package fails G-SET. Schema head 10, 44 tables, 39 types.
- The declaration is the list under the register's `custom_attributes.fields`. The helpers are
  `_attrs`, `_declaration_error`, `_entry_problems` (a pure function), `_KnownIds`,
  `_register_fields`, `_register_write_error` and `_nonconforming_entries`.
- The guard sits in `entity_upsert` after a `substitute` is materialised. A column that the item
  omits is read from the stored row, so a partial write is judged as a full row is.
- `required` means the key is present and not null. A value set applies to a text value. A
  reference is one id or a list of ids (R93). One refusal names every cause.
- A family that the package's registry does not know is refused with the route: the foreign-key
  text now names the family and `package_migrate`.
- Advisory `register-entries-conform`, emitted only when a register exists. It reads live entries
  against the CURRENT declaration, names the cause per entry under `problems`, and carries its
  population. Package rules: 31.
- `entity_query(register_id=...)` for `register-entry` rows only, echoed under `query`.
- The review page: the generic loop skips `register_entries`. Each register that has entries
  renders one fold whose columns are the declared fields. A key that the declaration no longer
  names shows under `(undeclared)`. The family keeps one anchor and its CSV link.
- `package_migrate`'s sync message now names a table that is written once in full for a new
  column. It said only that the sync is a pure append.
- Teaching: catalog rows, governance rows and a section, the naming template, artifact rules,
  package-writes section 7c, register-liveness item 23, quality-gates, the front door, the server
  README, `docs/entities.md`, the repository's identifier scheme. Scripts under
  `plans/evidence/scripts-226/` wrote the prose, and a second run of each changes nothing.
- Guide: EN and AR prose for 13 new ids. Two stated counts were corrected: 44 tables and 39
  families. A third was stale since v6.0.0: the guide said six migrations, and there are nine.
- A write that retires a STORED entry AS IT IS is not judged, so an entry that no longer fits can
  be retired. Every other write is judged: one that keeps the entry live, one that changes a
  value or the register while it retires, and a row born retired. A register with no entry reads
  `indeterminate`, as every empty family does (the rule is registered through `measured`).
- A declared field never takes the name of an entry column. A test ties the reserved names to
  the live schema.
- Lint 12's id pattern (`check.py`) gained `REG` and `ENT`, so a skill body never carries a
  field package's register ids.
- Not built: a typed trace relation for entries (`relates_to` and `supersedes` hold), and a
  rule language over fields.
- Deferred to plan 229: the fixtures learn the two families at the release stamp, with the lab
  beat that writes a register. An idle open and close of every fixture moves no file today.

## Validation (2026-11-12)

- `python check.py` passes: 255 contract tests (thirteen new for this plan), 48 page tests (one new).
- Mutation check: with the write guard switched off, five of the register tests fail. With the
  advisory blinded, one fails.
- Selftest: 19 of 19 tools, longest description 672 characters.
- Field replay on fresh scratch copies of both packages, through the real handlers:

| Step | First field | Second field |
|---|---|---|
| The first register write before the sync | refused, names `package_migrate` | the same |
| `package_migrate` preview | two families, one column | the same |
| Files moved by the confirm | `document_sections`, `entity_types`, `progress_entries` | the same |
| `package_verify` right after | verified | verified |
| Files moved by the next close | none | none |
| Gates before and after | equal | equal |

- The second field's three registers through the family, as stored (620 rows):

| Declaration | Topics (292) | Bank (292) | Findings (36) |
|---|---|---|---|
| Strict: every id-bearing field a reference | 280 refused | 264 refused | 36 refused |
| Fitted: joined ids kept as plain text | 0 refused | 0 refused | 0 refused |

  Every strict refusal was a reference that names no row. With the fitted declarations all 620
  entries were written, the rule passed over 620 rows, the gates did not move, and the store
  verified after a close. The review page rendered three register folds and no script.
- Finding for the second field's prompt: its rows move into the family without a value change.
  A field becomes a reference only after the project converts its joined ids to lists.

## Review (2026-11-12)

- The advisor found a regression before the commit. The registry-route text was added to every
  foreign-key refusal of a type with no registry row. An edge to a missing id and an omission
  for an unknown type were told to run `package_migrate`. Measured, then restricted to the types
  that the baseline registry names. A test pins the absence on three unrelated refusals.
- A hand-edited declaration crashed the review page (a set that is no list, then `fields` as a
  number). The write guard, the rule and the page now read a stored declaration defensively. A
  test loads six malformed shapes from the file.
- Design choices of the maintainer, put to the operator with the commit question. `required`
  means present and not null. A value set applies to text only. A retiring write is not judged.
  A field never takes the name of an entry column.
- Cost of the guard, measured on the second field's scratch copy: 40.5 ms for an entry written
  alone, 41.7 ms with the guard switched off, 0.2 ms per entry in one batch of 300.
- The code reviewer (a security brief, R92) approved with notes: no critical or high finding,
  and no way found to store a live entry that its declaration refuses. I ran each of its
  reproductions before I used it. What they showed, and what changed:
  - THREE defects OLDER than this plan, in `entity_upsert`, for every family. Each reproduced on
    a plain constraint.
    1. A row with no `id` was stored with a NULL key, and `readiness_check` and `export_html`
       then raised. Now a text key is required at the top of the item loop.
    2. A list sent as a key raised at the first lookup, the batch savepoint stayed open, and the
       earlier items of that refused batch were committed by the next write. Now
       `_no_half_batch` rolls the open transaction back when any exception escapes the tool,
       then raises it again. A list in a foreign-key column is a per-item refusal that names
       the column: it raised inside the error handler before.
    3. A `custom_attributes` value 1,500 levels deep was stored, and `readiness_check` and
       `export_html` then raised. Now a write refuses a value deeper than 32 levels, and a
       file that already holds one is read: `_json_values` walks with its own stack, and the
       page shows a marker in place of the value.
  - The other three writers were measured, not assumed. `progress_update`, `audit_record` and
    `work_bind` each refuse a list where text belongs, store nothing and leave no transaction
    open. Only `entity_upsert` had the leak.
  - Measured in both field packages: no row has a key that is not text, and the deepest stored
    value nests 4 levels in the first and 8 in the second. The new refusals touch no stored row.
  - The two new id columns are `NOT NULL` in the migration.
  - The retire door was narrowed to its purpose (above). A row born retired with refused values
    landed before.
  - `_attrs` refuses a key written twice, a non-finite number and a text nested too deep.
  - A refusal caps the undeclared keys that it lists at five, as it caps the references.
  - The page's extra column is headed `(undeclared)`, apart from a field of that name.
  - The sync message names the rewritten table on both branches (an operator-precedence slip).
  - `_RETIRED_STATUSES` is the one definition behind `_LIVE_ROWS` and the retire door.
- Not changed, and why: the rule's population counts every entry of the family, retired ones
  included. A scoped count would read a family of retired entries as a pass over zero rows.
- After the fixes: every reproduction returns a refusal, both field replays hold (620 of 620
  with the fitted declarations), the selftest registers 19 of 19 tools.
- Owed to CI: the branch that reads a `RecursionError` from the JSON parser runs first on the
  Python 3.10 leg. Here (3.13) the parser reads 1,500 levels, and the depth check refuses them.
- Scope, stated to the operator with the commit question: the three older defects are outside
  the register family. They ride in this commit because the review of this plan found them and
  the entry guard added lookups of the same kind. A split into two commits was offered.

## Rulings at the commit (2026-11-12)

- **R97**: the four grammar rules stand (`required`, value sets on text, reserved names, the
  narrow retire door).
- **R98**: moving the second field's rows is put in its prompt at the release (plan 229), with
  the strict and fitted measurement and the maintainer's recommendation.
- **R99**: one commit carries the registers and the three older write-path fixes.
