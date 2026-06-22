# Selected artifact set — claims-portal-modernization

This is a **legacy-modernization profile**. It is risk- and migration-heavy (a live, regulated system being re-platformed slice by slice), architecturally significant (a new routing seam / facade and a data-synchronization strategy are introduced), and compliance-bearing (regulatory data retention and audit-trail continuity). The artifact set is therefore weighted toward invariants, dependencies, architecture/ADRs, risk, a phased migration roadmap, and compliance evidence — and is deliberately light on cost modeling and greenfield product discovery.

## Always (generated)

These are produced for every Keystone package regardless of profile:

- Charter (`00-charter.md`)
- Executive summary (`01-executive-summary.md`)
- Functional requirements (`requirements/functional.md`)
- Non-functional requirements (`requirements/non-functional.md`)
- Constraint register (`requirements/constraint-register.md`)
- Assumption register (`decisions/assumption-register.md`)
- Open-question register (`decisions/open-question-register.md`)
- Open-decision register (`decisions/open-decision-register.md`)
- Risk register (`risks/risk-register.md`)
- Phased roadmap (`planning/roadmap.md`)
- Acceptance criteria (`validation/acceptance-criteria.md`)
- Traceability matrix (`validation/traceability-matrix.md`)
- Handoff initial prompt (`handoff/initial-prompt.md`)
- Execution-readiness report (`handoff/execution-readiness-report.md`)
- Manifest (`manifest.json`)
- README (`README.md`)

## Conditional (triggered)

| Trigger | Add | Why |
|---------|-----|-----|
| Hard data-preservation + audit-continuity obligations | **Invariant register** (`requirements/invariant-register.md`) | Zero data loss and an append-only, queryable audit trail across cutover are non-negotiable system properties, not mere requirements — they must be stated as invariants and traced into ADRs and acceptance criteria. |
| Live downstream integrations that must keep working | **Dependency register** (`requirements/dependency-register.md`) | Policy system (read) and payments gateway are external couplings whose behavior must be preserved as traffic shifts; the retention schedule is a compliance dependency. |
| New architectural seam introduced (facade + routing + data strategy) | **Architecture doc + ADRs + diagrams** (`architecture/`, `adrs/`, `architecture/diagrams/`) | The strangler facade, per-slice routing, and data-sync strategy are architecturally significant and irreversible-ish; they need recorded decisions and context/component/deployment/data-flow/integration views. |
| ≥2 viable approaches for facade routing and for data sync | **Technology comparison** (`architecture/technology-comparison.md`) | More than one credible option exists for the routing seam and for keeping legacy/new data consistent; options must be compared on parity, rollback, and operational risk before committing. |
| Cross-team effort (engineering, platform, compliance) | **Stakeholder register + work-breakdown + milestones** (`planning/`) | Multiple teams and a sign-off gate (compliance) require explicit ownership, decomposition, and dated milestones. |
| Parity and performance must be demonstrably met | **Test strategy + NFR thresholds** (`validation/test-strategy.md`, NFR section) | Migrated slices must prove behavioral parity with legacy and hit performance targets; this needs an explicit strategy (parity harness, shadow comparison, rollback drills). |
| Regulatory retention + audit obligations | **Compliance constraints + validation evidence plan** | Retention and audit integrity must be validated and evidenced for compliance sign-off, not asserted. |
| Long migration horizon (multi-phase, months) | **Progress log + status cadence + checkpoints** (`progress/`, `execution/checkpoints.md`) | A multi-phase migration needs a running log, a reporting cadence, and explicit phase-gate checkpoints. |
| Handoff to an execution agent | **Repo bootstrap + follow-up/review prompts + DoR/DoD** (`scripts/`, `handoff/`, `execution/definition-of-ready.md`, `execution/definition-of-done.md`) | The package is executed by Claude Code; it needs an init script, staged prompts, and explicit ready/done gates. |
| One de-risking spike needed before write-path migration | **Research plan + R&D backlog + hypothesis register + one experiment** (`research/`, `experiments/`) | The dual-read/reconciliation consistency assumption (HYP-001) must be validated by spike EXP-001 before PH-2; kept deliberately light (one spike, not a research program). |

**Kept minimal:** A deep cost/TCO model is **on-request only** — this engagement is sequencing- and risk-driven, not budget-defense-driven. Greenfield product-discovery artifacts (personas, market analysis) are omitted as not applicable to a modernization of an existing, in-use system.

Omissions and the reasons for them are recorded in `manifest.json`.
