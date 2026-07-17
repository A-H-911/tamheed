# Extension points

Tamheed is designed to grow as new projects reveal new reusable patterns — **without editing core
logic**. Everything below is additive: register a new entry, drop in a file or migration; don't fork
the workflow.

## What you can extend

| Extension | How | Where |
|---|---|---|
| New artifact family (entity type) | An `entity_types` registry row (type id, label, ID prefix, generation class) + an **append-only** DDL migration for its table + a catalog row + a selection trigger. | `../db/migrations/NNN_*.sql`, `artifact-catalog.md`, `artifact-rules.md` |
| New attribute on an existing family | Prefer `custom_attributes` (JSON) for experiments; promote to a real column via a migration once proven. | `../db/migrations/` |
| New section template | Add a `.template.md`; reference it from the catalog. | `../templates/` |
| New quality gate | Coverage tier: a SQL view + a `gate_run` row. Content tier: a scan/judgment rule. Referential tier: a constraint in a migration. | `../db/migrations/`, `quality-gates.md` |
| New project-type profile | Add a profile that biases selection + research depth. | `artifact-rules.md`, `research-depth.md` |
| New diagram kind | Extend the `diagrams.kind` CHECK via a migration + a generation note. | `../db/migrations/`, `generated-structure.md` |
| New trace relation | Extend the `trace_edges.relation` CHECK via a migration. | `../db/migrations/` |
| New entry point | Build a thin wrapper that normalizes input and routes output to THIS skill. | a CLI / API / UI wrapper (in Claude Code the skill itself is the entry point) |

Never edit `001_init.sql` after it ships — migrations are append-only, mirroring the
supersede-don't-edit governance rule.

## Entry-point contract

Any new entry point (another slash command, a CLI, an API endpoint, a UI) MUST:

1. Accept user input + optional parameters and normalize them to the skill's contract (a mode +
   profile + package dir).
2. Invoke this skill — never re-implement intake, clarification, artifact selection, generation,
   gates, or handoff.
3. Route or link the skill's output back to the user.
4. Contain no methodology and no business logic. (Mirrors safeguard 12 / G-CMD-THIN.)

The **MCP server is not an entry point** under this contract — it is the mechanical half of the
capability itself (ADR-0001's doctrinal note): the only write path into a package, the successor of
the v1 validator. The thin-wrapper rule governs things that *invoke* the methodology, not the store
that enforces it. The server's tool surface is itself a public contract: additive = MINOR,
breaking = MAJOR + migration note.

## Compatibility

Additive changes (new entity type / template / gate / profile / diagram kind) are MINOR. Changing an
existing table's required columns, the identifier scheme, or the handoff contract is MAJOR and needs a
migration note (`governance.md`). Keep older packages loadable: a v2 package authored under a prior
MINOR version must load into a newer schema (missing new columns default NULL; never repurpose a
column).
