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
