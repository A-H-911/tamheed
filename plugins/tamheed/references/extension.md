# Extension points

Tamheed is designed to grow as new projects reveal new reusable patterns — **without editing core
logic**. Everything below is additive: register an entry, drop in a migration; don't fork the
workflow. The biggest case (a whole new artifact family) starts a **new migration-chain entry** on
the v4 baseline — `../db/migrations/002_lessons.sql` (the lessons family, plan 035) is the LIVE
worked example of exactly this chain: table + trigger pair + immutability trigger + a relation-CHECK
extension, registered end to end; `../db/migrations/003_skills.sql` (the skill family + the lesson
`Promoted` state, plan 036) continues the same chain. `glossary_terms` (itself a baseline table since v4) remains the
worked example of the SHAPE: the table + trigger pair + the two registry entries — the contributor
walkthrough in the repo's contributing guide retraces it step by step.

## How migrations reach the runtime

`schema.sql` is the **frozen, byte-identical twin** of `db/migrations/001_init.sql` — `check.py`
enforces the identity. All later DDL is an **append-only** migration (`migrations/NNN_*.sql`,
NNN ≥ 002), applied by the store's connection factory in lexical order on every load. Never edit
`001_init.sql`, `schema.sql`, or any shipped migration — mirroring the supersede-don't-edit
governance rule.

## What you can extend

| Extension | How | Where |
|---|---|---|
| New artifact family (entity type) | An append-only DDL migration (the table — TEXT PK in the governed ID scheme, `custom_attributes` + `last_referenced` columns — plus the `entity_index` trigger pair) **and the two in-code registry entries**: `ENTITY_TABLES` (tool routing) + `BASELINE_ENTITY_TYPES` (the registry row seeded at `package_create`: type id, label, ID prefix, generation class). The viewer renders the new family automatically (its Registers section iterates `ENTITY_TABLES`); `check.py`'s lint gate fails until registry ↔ table map ↔ DDL agree. Add a catalog row + a selection trigger for the prose surfaces. | `../db/migrations/NNN_*.sql`, `../server/tamheed_server.py`, `artifact-catalog.md`, `artifact-rules.md` |
| New attribute on an existing family | Prefer `custom_attributes` (JSON) for experiments; promote to a real column via a migration once proven. | `../db/migrations/` |
| New section template | Add a `.template.md`; reference it from the catalog. | `../templates/` |
| New scenario prompt (emitted library) | Add a `.md` beside the existing sixteen; `{package}` is the only substitution; it is emitted into `<package>/prompts/` by migrate/adopt/handoff automatically. | `../prompts/` |
| New quality gate | Coverage tier: a SQL view (via a migration) + a `gate_run` row. Content tier: a scan/judgment rule. Referential tier: a constraint in a migration. | `../db/migrations/`, `quality-gates.md`, `../server/tamheed_server.py` |
| New project-type profile | Add a profile that biases selection + research depth (the `packages.profile` CHECK gains the value via a migration). | `artifact-rules.md`, `research-depth.md`, `../db/migrations/` |
| New diagram kind | Extend the `diagrams.kind` CHECK via a migration + a generation note. | `../db/migrations/`, `generated-structure.md` |
| New trace relation | Extend the `trace_edges.relation` CHECK via a migration. | `../db/migrations/` |
| New entry point | Build a thin wrapper that normalizes input and routes output to THIS skill. | a CLI / API / UI wrapper (in Claude Code the skill itself is the entry point) |

New identifier prefixes live **on the registry row** (`id_prefix`) and in the new table's CHECK —
there is no separate central pattern list. Registering a family means all three together: the DDL
migration, `ENTITY_TABLES`, and `BASELINE_ENTITY_TYPES`; `check.py`'s sync lints catch a partial add.

**Existing packages and new families.** A package's own `entity_types` registry is seeded when the
package is created (or migrated), so a package that predates an extension does not know the new
family: writing a row of the new type into it fails loud on the registry FK. That is intentional
fail-closed behavior — teaching an old package a new family is a deliberate operator action, never a
silent side effect of upgrading Tamheed. The action is `package_migrate`'s staged **registry-sync**
mode: on a v4 store missing baseline entity types, the preview reports `mode: "registry-sync"` +
`entity_types_added`, and confirm appends the registry rows — a pure append, no backup taken; an
up-to-date v4 store still refuses.

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

Mirrors `governance.md` versioning: **MINOR = additive** (new artifacts/fields, no break) — a new
entity type, template, gate, profile, diagram kind, or entry point. **MAJOR = breaking change to
schemas, identifiers, or the handoff contract; ship a migration note** — changing an existing
table's columns or constraints, the identifier scheme, or the MCP tool surface. Keep older packages
loadable: a package authored under a prior MINOR version of the same MAJOR must load into a newer
schema (missing new columns default NULL; a missing `.jsonl` file is an empty table; never repurpose
a column). Across a MAJOR the doctrine is explicit migration: `package_open` refuses an older store;
`package_migrate` converts it.
