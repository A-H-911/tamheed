# Plan 133: the v5.2.0 docs and diagrams sweep

> Maintainer-executed, 2026-09-26. Batch map: [129-135-batch-findings-33.md](129-135-batch-findings-33.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (prose; lint 10 links; lint 8 stamps land in 134)

## What changed, and where each v5.2 behaviour is named (the census — every behaviour in ≥ 2 docs)

| Behaviour | Named in |
|---|---|
| `stock_merged` verifies the whole declared body, `missing_by_release` | `references/handoff.md`, `server/README.md`, `docs/design-decisions.md` §14, CHANGELOG, `prompts/README.md` (134, with its history key) |
| The stale-warning block beside the note; generic text; byte-clean strip | `references/handoff.md`, `server/README.md`, `docs/design-decisions.md` §14, CHANGELOG |
| `entity_query` / `handoff_emit` cues; the export file never carries one | `server/README.md`, `docs/architecture.md` (the RES node + the resume sequence), `docs/design-decisions.md` §14, `README.md`, CHANGELOG, the front door |
| `system:skill-guard` | `server/README.md`, `references/governance.md`, `docs/entities.md` (the `upstreamed_to` row), `docs/architecture.md`, `SECURITY.md`, `docs/design-decisions.md` §14, `README.md`, CHANGELOG |
| `lessons-stranded` population = Promoted lessons; `handoff-current` counts engine transitions | `references/quality-gates.md`, `server/README.md`, CHANGELOG |
| Hook caps 25 lines / 4,000 chars | `docs/install.md`, `SECURITY.md`, `server/README.md`, `skills/session-handoff`, CHANGELOG |
| The template points at the note's table | `references/handoff.md`, `templates/agent-control.template.md`, CHANGELOG |
| E2 first store WRITE; 5.2.0 no migration | `docs/install.md` |
| E5 the scans run over every `prompts/*.md`; `id-dense` at the paragraph's first line | `references/handoff.md` |
| E14 the per-plugin opt-out; `disableAllHooks` kills every hook | `docs/install.md`, `SECURITY.md` |
| Reload: `/reload-plugins` + `/reload-skills` measured, undocumented; the hook fires on reload | `docs/install.md` |

Diagrams: `docs/architecture.md` — the RES node lists the two new cues; the resume sequence diagram
gains `entity_query` → rows + cue, `handoff_emit` → scans + cue, and the `system:skill-guard` row.
`docs/entities.md` has no skills diagram (the guard is in the `upstreamed_to` row and in
`governance.md`); the PE flowchart's `handoff-current` node is unchanged (engine transitions were
always counted; the docs now say so).

`docs/design-decisions.md` §14 records the four rulings (D-STOCK-BODY, D-STALE-HOME, D-CUES-2,
D-SKILL-GUARD) and the five decided without a diagram. `plans/README.md` gains the findings_33
section; the batch record carries §0's measurements.

Not touched: `evals/README.md` (no new `pkg_check` vocabulary), `references/state.md` and
`workflow.md` (they describe the resume surface, unchanged in shape), `docs/methodology.md`.
