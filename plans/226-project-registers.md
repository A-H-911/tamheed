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
