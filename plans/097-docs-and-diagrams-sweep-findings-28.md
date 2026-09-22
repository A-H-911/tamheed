# Plan 097: Docs and diagrams sweep for the findings_28 batch

> Reviewer-executed (maintainer-delegated), 2026-09-23. Batch map:
> [091-099-batch-findings-28.md](091-099-batch-findings-28.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (prose) - **Planned at**: `9d8e6a1`

## Why this matters

Measured after 092-096 landed, outside `plans/`, the CHANGELOG, tests and code: `occurrences`,
`context=N`, `prompt-ids-resolve`, `type="package"`, `package-guard`, `package_audit`, the glued-match
refusal, the boolean-`true` rule and the page's new sections were documented in zero places; the
advisory count read eighteen (it is nineteen).

## What changed

| File | Change |
|---|---|
| `plugins/tamheed/server/README.md` | `entity_query` (`context`/`occurrences`; the `package` pointer), `entity_upsert` (the header write; the `substitute` item and every refusal; the operator's word is the boolean `true`), `readiness_check` (`prompt-ids-resolve`), `export_html` (the Readiness and Feedback sections, the tag, the mark), `server_info` (the header's write) |
| `references/quality-gates.md` | nineteen advisories; the prompt rule's file population; the page renders the report |
| `references/governance.md` | **new section** "The package header — on the operator's word"; the boolean-`true` rule |
| `docs/architecture.md` | nineteen; the write side gains the `substitute` and header writes, the read side the census and the prompt scan; the review-page sentence names its new sections |
| `docs/entities.md` | the `packages` infrastructure row says how the header is written and guarded |
| `SECURITY.md` | a partial write inherits every guard; the go/no-go verdict is the operator's; the boolean `true` |

Not touched: `docs/workflow.md` — the batch plan named it, but it is the 22-stage model and has
never described the review page; the architecture doc is where the page lives. No diagram
changed: the batch's data flows were drawn in 088 (feedback) and 082 (lessons); the header and
substitute writes are ordinary `entity_upsert` calls on the existing write-side diagram.

## Validation

Per-behavior grep: every new name in >= 2 documents outside `plans/`; no "eighteen" survives;
`check.py lint` green (mermaid included).

## Done criteria

- [x] per-behavior grep clean
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green
