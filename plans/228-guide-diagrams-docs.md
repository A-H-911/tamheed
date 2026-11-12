# Plan 228 -- the guide, its diagrams, the docs sweep

> Status: PLANNED 2026-11-11. Cycle: field round 2026-11 (ACMP FB-030..032, Jisr FB-001..011),
> release 6.5.0, branch `round/6.5.0`. The round record (evaluation, rulings R81-R89, risks,
> execution order) is [field-round-2026-11-record.md](evidence/field-round-2026-11-record.md).

- `docs/guide/content.py` EN+AR for every new id `build.py --missing` names: the `trace_query` and
  `entity_query` parameters, two tools and their parameters, two families and their columns, one
  rule, one review section, the section status set, the new suite.
- `docs/guide/diagrams.py`: D2 (tool pills, 19 to 21), D4 (a package on disk gains `slates/`), the
  per-family and per-tool file figures for the new families and tools, the `fx-` figures of
  `trace_query`, `package_unlock` and `entity_upsert`, the gate figures' line references. The
  geometry lint is the bar, on both language copies. Captures follow `scripts-219/capture_219.py`.
- `docs/entities.md` (two family sections with lifecycle diagrams, the gate words, the section
  status), `docs/architecture.md`, `docs/workflow.md`, `docs/install.md` (the live-package note),
  the three READMEs by content, `tests/README.md`, and the repository's own `CLAUDE.md` (the
  identifier scheme, the layout, the gate and tool facts).

## As built (2026-11-12)

Most of this plan's first scope was done inside the plans that moved each fact, because the gate
needs the guide's prose before it passes. Plans 221 to 227 each added their guide prose in both
languages, their effects figures, their counts and their teaching. What was left, and is here:

- The review page's readiness table names the legs that a requirement misses, beside its id.
  The page showed the ids alone. One test.
- The guide's figure of a package on disk gains `slates/`, with its phrase in both languages.
  The geometry lint passes on both copies.
- `README.md`: a paragraph on what is new in v6.5, the `trace_query` row, a row for the two
  slate tools, and the server line of the structure tree.
- `docs/architecture.md`: the two slate tools in the tool list, and two short paragraphs on the
  interview page and on registers.
- `CLAUDE.md`: the layout names the interview page's three files.
- `plans/evidence/scripts-228/docs_228.py` wrote the README, architecture and layout edits. A
  second run changes nothing.

Left to plan 229, by design: the stock operator guide (`prompts/README.md`) changes only with
its history key at the stamp, and the version surfaces move at the stamp.

## Validation (2026-11-12)

- `python check.py` passes on Python 3.13 and on Python 3.10. The page suite runs 49 tests.
- The guide holds 1,570 content ids, and none lacks a string.
