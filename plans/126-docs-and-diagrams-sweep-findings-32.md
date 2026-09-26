# Plan 126: docs + diagrams sweep for v5.1.0 (findings_32)

> Maintainer-executed, 2026-09-26. Batch map: [120-128-batch-findings-32.md](120-128-batch-findings-32.md).

## Status

- **Priority**: P2 - **Effort**: S - **Risk**: LOW (prose and two mermaid diagrams; lint 10 links)

## What changes

Every v5.1 behaviour named in at least two documents: the `handoff` kind and the resume block
(`docs/entities.md` PE section + a flowchart; `docs/architecture.md` §journal paragraph, the
instruction-surfaces flowchart and a resume-surface subsection; `README.md`; `references/state.md`
Resume; `references/workflow.md` stage 21; `references/handoff.md`; `server/README.md`); the hook
(`docs/install.md`, SECURITY.md — plan 123; `server/README.md`; `extension.md` "New hook");
`upstreamed_to` + `lessons-stranded` (`docs/entities.md` skill table; `artifact-catalog.md`;
`governance.md`; `quality-gates.md` — plan 122); the menu contract and the skill hints
(`docs/architecture.md` flowchart; `extension.md` scenario/discipline rows; `docs/methodology.md` if
it counts the skills); the scans (`references/handoff.md`); `plans/README.md` title "(through v5.x)"
and the findings_32 section; CHANGELOG `[Unreleased]` body (the heading lands at the 127 stamp);
`docs/design-decisions.md` §13 D-RESUME; `docs/install.md` upgrade step (5.1.0: schema 7, the
one-time `skills.jsonl` rewrite). The optional ADR-0003 was not written: D-RESUME records the decision
and the batch record the rationale.

## Done criteria

- [ ] `python check.py lint` green (lint 10 links, lint 9 vocabulary)
- [ ] census: every new behaviour in ≥ 2 docs (listed above)
