---
status: Approved
date: 2026-11-27
id: ADR-0007
supersedes: none
superseded_by: none
---

# ADR-0007 — A family can declare fields of its rows' custom_attributes

## Status

Approved (operator, 2026-11-27: rulings R156, R163 and R165 in
`plans/256-field-round-6.9.0.md`. Plan 261, release 6.9.0).

## Context

A project put a key of its own, a `layer`, on about a thousand rows of built-in families. The
store checked no value of it, so a mistyped value passed, and no rule listed the rows that lacked
the key. Only a register could declare fields, and a register holds a record type of its own,
not the rows of a built-in family. The header's `custom_attributes` is frozen. Each family's
registry row has a `custom_attributes` column, and nothing wrote it.

## Decision

- A family's registry row declares fields of its rows' `custom_attributes`, in the register
  grammar: `name`, `required`, `values`, `refs`.
- An `entity-type` item of `entity_upsert` writes the declaration. It lands only on the
  operator's word, and the engine journals it. Only `custom_attributes` is writable.
- A write that SETS `custom_attributes` is checked: sent by the caller, named by a substitute,
  or changed by a merge. A value outside the set and a reference to no row are refused. A key
  the declaration does not name stays free.
- `required` is never enforced at write. The advisory `declared-attributes` lists the rows that
  lack a required key or break the declaration.
- Registers, register entries, the journal and standup reports take no declaration.

## Consequences

- No migration: the column was in the schema since v4.
- A declaration can come after the rows. An old row stays writable until a write sets its
  `custom_attributes`, and the advisory lists it meanwhile.
- 6.8.0 does not read a declaration. It opens a package that holds one and checks nothing.
- The parked plan keeps ADR-0006 (R163).
