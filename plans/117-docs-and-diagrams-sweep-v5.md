# Plan 117: docs + diagrams sweep for v5.0.0

> Reviewer-executed (maintainer-delegated), 2026-09-24. Batch map:
> [112-119-batch-findings-31.md](112-119-batch-findings-31.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: LOW

## Why this matters

Every teaching and repo surface that names the front door, the prompt library, the note's contents, the relation roster or the install route must say what 5.0.0 does.

## What changes

README, server README, generated-structure (tree), handoff.md, governance, quality-gates, artifact-catalog, prompt-templates.md, extension.md (006 beside 005), install.md (plugin route; project enablement; restart after update; the manual route's unverified nesting; "v4 store under 5.x"), SECURITY.md, architecture.md (sequence + an "instruction surfaces" diagram), entities.md, methodology.md, CONTRIBUTING.md, CLAUDE.md layout, CHANGELOG 5.0.0 with the name mapping and `006_carries.sql`.

## Done criteria

- [x] per-behaviour grep ≥ 2 docs
- [x] `python check.py`
- [ ] CI green

## Execution note (2026-09-25)

Fifteen files by a transactional script (one exact match per edit): README.md (the note paragraph,
the bundle tree), docs/architecture.md (the handoff sequence line, the bundle tree, a new
"instruction surfaces" flowchart: ambient note / on-relevance discipline skills / operator-invoked
scenarios / project skills, each with its owner and delivery path), docs/entities.md (plugin skills
vs project skills, the `Obsolete` + `upstreamed_to` retirement recipe), docs/install.md (the plugin
route with the seven + sixteen, project-scope enablement per the docs, the restart after an update,
"a MAJOR that changes the handoff contract, not the store", refresh_stock's v5 semantics, the manual
route's unverified nesting), docs/migrate-from-keystone.md, artifact-catalog.md, generated-structure.md
(the tree), handoff.md (the library paragraph, the flush mechanism corrected, `force`'s scope),
prompt-templates.md (the scenario table by skill name), quality-gates.md (G-INJECT's scan set),
follow-up-prompts and package-readme templates, the server README's `handoff_emit` row, the front
door (migrate mode's guide sentence; the reference index row), SECURITY.md (the plugin's own skills
as static bundle text; the deletion proof). The CHANGELOG 5.0.0 block was started by plan 113 (lint 7)
and already names the mapping and the migration. Coverage: `tamheed:package-writes` 7 files,
`/tamheed:` 15, the leftover semantics 9, the note v5 5, `carries` 25, `006_carries` 5, the moved
front door 7. Left as history, deliberately: lab/scenario.md's beat prose and lab/README.md (records
of what earlier beats measured; beat 22 re-aims the one Pass-bar sentence F-6 names).
