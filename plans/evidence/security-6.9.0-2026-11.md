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
