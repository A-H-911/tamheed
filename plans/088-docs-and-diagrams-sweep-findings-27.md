# Plan 088: Docs and diagrams sweep for the findings_27 batch

> Reviewer-executed (maintainer-delegated), 2026-09-22. Batch map:
> [085-090-batch-findings-27.md](085-090-batch-findings-27.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (prose and two diagrams) - **Planned at**: `91b6592`

## Why this matters

Measured after 085-087 landed, outside `plans/`, the CHANGELOG, tests and code: `feedback-guard`,
`feedback_audit`, `lesson_audit`, the `system:` reservation, the cut-list clause, the classification
order and the `scoped` discriminator were documented in zero or one place each. The maintainer's
mid-review note: the sweep runs after the checks, and the full test pass follows it.

## What changed

| File | Change |
|---|---|
| `plugins/tamheed/server/README.md` | `entity_upsert` (by-hand retirement journaled; the feedback guards, bound set, drift rule), `readiness_check` (`_`, order, cut clause, `scoped`), `progress_update` (`system:` refused on both caller paths), `handoff_emit` (the two feedback warnings, ids only) |
| `references/quality-gates.md` | the three-list semantics, the underscore rule, `scoped` as the tell |
| `references/governance.md` | the by-hand exit is journaled; **new section** "Feedback and local tools - on the operator's word" after the lifecycle section |
| `references/extension.md` | `005_feedback.sql` as the newest whole-family worked example, with the full footprint |
| `docs/architecture.md` | **new diagram**: the feedback data flow (agent -> package -> operator -> export -> findings -> maintainer; the local tool confirmed before it exists) |
| `docs/entities.md` | the lesson diagram's by-hand edge says journaled (`lesson_audit`); the feedback diagram carries `feedback_audit`, the journaled withdrawal, the migration name and the prose-id exemption |
| `SECURITY.md` | the engine's actor namespace; what leaves the package leaves on the operator's word; the four bypasses closed before commit |
| `README.md` | tool table: a feedback row exists on the operator's word |

## Validation

Per-behavior grep over tracked files outside `plans/`, `CHANGELOG.md`, tests and code: every new
name in >= 2 documents; `git grep -i "at rest is legal"` empty; `check.py lint` green (mermaid
blocks included). Applied transactionally; one section landed at the wrong anchor and was moved
(recorded here so the pattern is not repeated: check the heading order before choosing an anchor).

## Done criteria

- [x] per-behavior grep clean (>= 2 docs each)
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green
