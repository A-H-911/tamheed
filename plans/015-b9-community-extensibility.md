# Plan 015 (B9): Community extensibility — the v2 extension mechanism and CONTRIBUTING refresh

> **Executor instructions**: Design + docs plan with one mechanical proof. STOP conditions are
> binding.
>
> **Drift check (run first)**: plans 007 (entity_types registry + migrations dir) and 014 (docs
> current) landed. Missing → STOP.

## Status

- **Priority**: P3
- **Effort**: M
- **Risk**: LOW
- **Depends on**: plans/007, 013, 014
- **Category**: dx / direction
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

The maintainer wants Tamheed "expandable with the open source community." v1's extension story
(`references/extension.md`) was file-shaped: add a template + a catalog row + a schema. In v2 the
same additive philosophy must map onto the database world — a new artifact type without forking
the workflow — and `CONTRIBUTING.md` must onboard a stranger into a repo that now has a DB layer,
an MCP server, and a check script.

## Current state

- `plugins/tamheed/references/extension.md` — v1 registries table (new artifact/template/schema/
  gate/profile/diagram/entry-point) + the thin-wrapper entry-point contract (KEEP that contract —
  it survives v2 per the plan-007 ADR's doctrine note).
- `CONTRIBUTING.md` — v1 setup (Python 3.9+, validator self-test, "no build step"), invariants
  list, additive-change rules. Largely obsolete in mechanics, still right in spirit.
- Plan 007 delivered the mechanism this plan documents: `entity_types` registry rows,
  `custom_attributes`, append-only `plugins/tamheed/db/migrations/NNN_*.sql`.
- Plan 013 delivered `check.py` (incl. registry↔DDL sync gate) — the contributor's one command.

## Deliverables

1. **Rewritten `references/extension.md`**: the v2 extension table —
   - new artifact type = `entity_types` row + `migrations/NNN_*.sql` + a viewer section
     registration (plan 012's registry) + (if narrative) a section template = **MINOR**;
   - new profile = registry row biasing selection = MINOR;
   - new gate = SQL view + `gate_run` registration (coverage) or content-check registration = MINOR;
   - changing an existing table's columns/constraints, the ID scheme, or the tool surface =
     **MAJOR** + migration note (mirrors `governance.md` versioning);
   - entry-point contract kept verbatim from v1 (thin wrappers; the MCP server is capability, not
     wrapper).
2. **Rewritten `CONTRIBUTING.md`**: v2 dev setup (clone → `python check.py`; server work needs
   `uv` or `pip install mcp` — the ONLY dependency, per D-U3 CI itself stays stdlib), the
   walkthrough "add an artifact type end-to-end" (registry row → migration → viewer section →
   check.py green), test conventions (stdlib unittest, suites registered in check.py), the
   invariants to preserve (bundle self-containment; supersede-don't-edit; additive-first;
   untrusted-content posture), and a good-first-issue taxonomy (new artifact types, new profiles,
   viewer sections, eval cases, adopt-mode extraction heuristics).
3. **The mechanical proof**: a worked example executed for real —
   `plugins/tamheed/db/migrations/002_example_glossary.sql` adding a minimal `glossary_terms`
   entity type (term, definition, source_span) + its registry row + viewer section + one test —
   then the walkthrough in CONTRIBUTING documents exactly what was done. (If the maintainer
   prefers zero example baggage in-tree, flag before executing: the alternative is a
   `docs/examples/extension-walkthrough.md` transcript and reverting the migration — ask ONCE at
   plan start.)

## Commands

`python check.py` → exit 0 (including registry↔DDL sync with the new type);
`python tests/test_export_html.py` → exit 0 (new section renders).

## Scope

**In scope**: the three deliverables + `plans/README.md`. **Out of scope**: a plugin/extension
marketplace (future direction), GitHub issue templates/labels config (operator's call),
any tool-surface change.

## Steps

1. Rewrite `extension.md` (deliverable 1).
2. Ask the maintainer the deliverable-3 question (in-tree example vs transcript) — ONE question.
3. Execute the walkthrough per the answer; capture every command.
4. Rewrite `CONTRIBUTING.md` around the captured walkthrough.

**Verify** per Commands after 3–4.

## Done criteria

- [ ] extension.md describes only mechanisms that exist (each claim traceable to a plan-007/012/013
      artifact)
- [ ] CONTRIBUTING walkthrough reproduces green on a clean clone (test it: fresh checkout, follow
      it literally)
- [ ] check.py green; `plans/README.md` updated
- [ ] MAJOR/MINOR rules stated and consistent with governance.md

## STOP conditions

- The walkthrough exposes a gap in the plan-007 mechanism (e.g. a new type needs code edits
  beyond registry+migration+viewer) — report; that's a design defect to fix at the source, not
  to paper over in docs.

## Maintenance notes

- The registry↔DDL sync gate in check.py is what keeps community additions honest — never exempt
  example/extension types from it.
- Reviewer scrutiny: that MINOR-vs-MAJOR boundaries here match `references/governance.md` word
  for word.
