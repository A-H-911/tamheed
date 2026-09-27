# Plan 138: docs and diagrams sweep for v5.3.0

> Maintainer-executed, 2026-09-27. Batch map: [136-140-batch-findings-34.md](136-140-batch-findings-34.md).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What was swept, and why (the field's E-list and the two new behaviours)

| Surface | Change |
|---|---|
| `docs/install.md` (Upgrading) | `/reload-plugins` is documented now (fetched 2026-09-27) and quoted; `/reload-skills` still is not; the `/plugin` panel runs the reload on close; a reload that adds/removes an MCP server is refused without `--force`. **The hook on a reload is not a mechanism**: one delivery (5.1.0), two non-deliveries (5.2.0), every restart and compaction delivered — a session restart is the route the block arrives by every time; the trace tells a hook that did not run from one whose output was not delivered. The reload route's context handling is reported inconsistent (claude-code #61485, #87514, #37862, #63028 — adjacent reports, not this defect's cause). The stdout cap is undocumented but exists (changelog 2.1.283: oversized outputs saved to a file); 3,615 chars measured whole. |
| `docs/architecture.md` | The resume sequence diagram: the hook's lock line carries the observation; a `TAMHEED_HOOK_LOG` note; `_resume_block` names `observed` (own lock: alive, no probe). The lock-lifecycle state diagram: `process restart` as a cause; the resume block and the hook carry the observation on the next session. The paragraph after the sequence: v5.3 in one sentence each. E3: "every successful `entity_query` result". |
| `docs/design-decisions.md` | §15: D-LOCK-OBSERVED, D-HOOK-LOG, D-RENDER-HINT, D-RESIDUE; the without-a-diagram list (E3, classes only, the Q1 protocol). E3 in §14. |
| `references/handoff.md` | The Lessons section: the fill is the 10 highest-numbered; approving BINDS, rendering needs pinned or the fill; the approval's `next` says which (E2). |
| `README.md` | The resume sentence gains the observed lock and the trace. |
| `CHANGELOG.md` | `[Unreleased]` carries the 5.3.0 body (Added / Changed); the heading is stamped in 139. |
| Front door `skills/tamheed/SKILL.md` | "the lock holder and what the store observed about it"; E3. |
| `plans/README.md` | Section "Field cycle findings_34 — plans 136–140 → v5.3.0". |
| `prompts/README.md:64` | "every `entity_query` result" — a STOCK body: lands with the `5.3.0` history key in 139 (lesson 1 of the 5.2.0 cycle), not here. |

Untouched on purpose: `references/quality-gates.md` (no rule changed), `docs/entities.md` (no entity
change), `references/governance.md` (no new actor), `server/README.md` and `SECURITY.md` (done in 136/137).

## Census (every new behaviour named in ≥ 2 docs)

- The observed lock: `server/README.md`, `install.md`, `SECURITY.md`, `architecture.md`, `design-decisions.md`, `README.md`, front door.
- The trace: `server/README.md`, `install.md`, `SECURITY.md`, `architecture.md`, `design-decisions.md`, `README.md`.
- The render hint: `references/handoff.md`, `design-decisions.md`, `CHANGELOG.md`.
- E3: `server/README.md`, `architecture.md`, `design-decisions.md`, front door (the stock guide in 139).

## Validation

`python check.py` green (lint 10 links over the new section and §15).
