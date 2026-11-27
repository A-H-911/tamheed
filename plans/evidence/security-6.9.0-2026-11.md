# The 6.9.0 round: the security passes (plans 258-261)

The review-council plugin's guard blocks every agent named `security-reviewer` while this branch's
`CLAUDE.md` and `.github/workflows/ci.yaml` differ from main. Beat 257 changed both. The operator
ruled on 2026-11-27: the maintainer does the security pass of each beat from the checklist below and
writes it here. After main is fast-forwarded, the `ecc:security-reviewer` agent reviews 258-261
together, before the tag, and a finding is fixed before the tag.

The checklist, for each beat:

1. SQL. Is every name in a query (table, column) taken from the code's own maps or from
   `PRAGMA table_info`, and every value bound with `?`?
2. Echoed data. What stored text does a new result or refusal return, and is it bounded?
3. Guards. Can a combination of item keys pass a write that a guard refused before?
4. Cost. Is a new query bounded by one table and one item?
5. Words that teach. Does a new text on an always-loaded surface (the note, a tool description)
   claim more than the engine does?

## Beat 258: the column lists, `create: true`, the `write` marker

| Check | Finding |
|---|---|
| SQL | `_create_error` interpolates `table` (from `ENTITY_TABLES`), `key` (`"id"` or `_NON_ID_TABLES`) and the literal `title`. The key value, the edge triple and the GLOB pattern are bound. The GLOB pattern is built from the family's registry prefix, not from the caller. `_next_id` takes the same names. No caller text reaches a query string |
| Echoed data | A `create` refusal returns the existing row's title, cut at 120 characters. The caller can read the same title with `entity_query`, so nothing new is exposed. The column lists are the schema's names, not data |
| Guards | `create` only adds refusals. `create: false` is treated as absent at all four sites (the filter, the retire branch, the substitute keys, the header). With `create: true` the existence test runs before the other guards, and a row that does not exist goes on through every guard unchanged (the lab replay: a new scope change was then refused on its NOT NULL `decision_ref`) |
| Cost | Two indexed lookups and one GLOB scan of one family, per `create` item |
| Words | The note row and the description say the flag is opt-in, and that a write without it updates a row with the same id. That matches the engine |

No finding.

## Beat 259: `sha256: true`

| Check | Finding |
|---|---|
| SQL | `_written_hashes` interpolates `table` (from `ENTITY_TABLES`), the key columns (fixed tuples) and column names. The names are the item's own columns, which the unknown-column check has already matched to the table, or a substitute's columns, which `_materialize_substitute` has matched. They are filtered again by `PRAGMA table_info`. Every value is bound |
| Echoed data | The hashes are of text that the caller has just sent. Nothing new leaves the store |
| Guards | The key writes nothing. It is read after the item's write, inside the batch. A batch that fails later is rolled back whole and returns `ok: false`, `applied: 0` and "batch rolled back". Its items keep their per-item keys, as `changed_columns` always has, so a hash there describes a write that was undone. The batch fields say so |
| Cost | One indexed SELECT for each item that asks |
| Words | Section 2 says the hash is of the text as stored, that an object sent for `custom_attributes` is stored as JSON that the server writes, and what `expect_unchanged` proves. That matches the engine |

No finding.

## Beat 260: `merge_attributes`

| Check | Finding |
|---|---|
| SQL | `_materialize_merge` interpolates `table` (from `ENTITY_TABLES`) and the names from `_columns(table)`. The id is bound |
| Echoed data | The result's `merged` lists the caller's own keys. No refusal returns stored text |
| Guards | A merge materializes the whole stored row and sends it down the ordinary path, as `substitute` does, so every guard and trigger judges it. A merge that changes nothing returns before the guards and writes nothing, so there is nothing to guard. It answers only whether the stored object already equals the merge, which the caller can read anyway. `create`, a substitute, a retire, the header and the journal each refuse a merge by name |
| Cost | The patch is bounded by `_JSON_MAX_DEPTH` (its recursion is caught) and by the size of the call. One indexed SELECT for each item |
| Words | Section 1 says a substitute inside a value works and a result that breaks the JSON is refused. That matches `_materialize_substitute` |

No finding.

## Beat 261: a family's declaration

| Check | Finding |
|---|---|
| SQL | `_write_entity_type` binds the type id and the value. `_declared_breaches` interpolates a table from `ENTITY_TABLES`, never the stored type id, and `_LIVE_ROWS` (a constant) |
| Echoed data | A refusal names the declared field, the value the caller sent and the set, all from the caller's own write or the declaration. The advisory names row ids and causes, capped at 50 rows |
| Guards | The declaration needs the operator's JSON `true` (`_operator_word`), and the engine journals it as `system:declaration` in the item's savepoint. A caller cannot write a `system:` actor. The check at write only adds refusals. A write that does not set `custom_attributes` is never judged, so a declaration cannot lock an old row. `required` is never enforced at write. The four families with their own rules take no declaration |
| Cost | One indexed SELECT for each item of a declared family. The advisory reads every live row of each declared family once, and checks a reference with one indexed lookup |
| Words | The governance section, the ADR and SECURITY.md say the operator's word, the journal, the free undeclared keys and the advisory-only `required`. That matches the engine. `package_migrate`'s registry sync only appends missing types (`:5846`, read, not tested), so it keeps a declaration |

No finding.
