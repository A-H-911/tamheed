# Governance: identifiers, statuses, versioning, cross-references

This is the single source of truth for how every Tamheed entity is named, identified,
versioned, and linked. Apply it uniformly — consistent identifiers are what make traceability
and the handoff trustworthy.

## Identifier scheme

Each identifier is a stable prefix + zero-padded number, unique within a package and never
reused (retire, don't recycle). Every entity lives in its `data/<table>.jsonl` family
(see `artifact-catalog.md`).

| Entity | ID format | Family (table) |
|---|---|---|
| Functional requirement | `FR-NNN` | requirements |
| Non-functional requirement | `NFR-NNN` | requirements |
| Constraint | `CON-NNN` | constraints |
| Invariant (non-negotiable) | `INV-NNN` | invariants |
| Assumption | `ASM-NNN` | assumptions |
| Dependency | `DEP-NNN` | dependencies |
| Open question | `OQ-NNN` | open_questions |
| Decision (any project decision) | `DEC-NNN` | decisions |
| Architecture Decision Record | `ADR-NNNN` (exactly 4 digits) | adrs |
| Risk | `RISK-NNN` | risks |
| Hypothesis | `HYP-NNN` | hypotheses |
| Experiment / POC | `EXP-NNN` / `POC-NNN` | experiments / pocs |
| Success metric / KPI | `KPI-NNN` | kpis |
| Stakeholder | `STK-NNN` | stakeholders |
| Phase | `PH-N` | phases |
| Milestone (roadmap label) | `MS-NNN` | milestones |
| Slice (vertical increment) | `SL-NNN` | slices |
| Work item (WBS) | `WBS-N[.N[.N]]` (group `WBS-N`, leaf `WBS-N.N`) | wbs_items |
| Acceptance criterion | `AC-NNN` | acceptance_criteria |
| Test / validation item | `TEST-NNN` | tests |
| Audit verdict | `AV-NNN` | audit_verdicts (append-only) |
| Progress entry | `PE-NNN` | progress_entries (append-only, typed) |
| Defect | `DEF-NNN` | defects |
| Deferred work | `DW-NNN` | deferred_work |
| Execution gate | `GATE-NNN` | execution_gates |
| Execution plan | `EP-NNN` | execution_plans (per slice) |
| Convention | `CONV-NNN` | conventions |
| Scope change | `SC-NNN` | scope_changes |
| Waiver (v4) | `WVR-NNN` | waivers |
| Narrative document / section | `DOC-NNN` / `SEC-NNN` | narrative_documents / document_sections |
| Diagram | `DIA-NNN` | diagrams |
| Glossary term | `GT-NNN` | glossary_terms |
| Lesson | `LL-NNN` | lessons |

Retired prefixes: `PRM-` (v3 — prompts became files under `<package>/prompts/`; ids of that
shape in a converted package are conversion-audit provenance, not entities).

**`DEC` vs `ADR` — the promotion rule (v4, plan 031).** Use `DEC-` for ANY decision. Promote
to an `ADR-NNNN` when the **one-way-door test** says yes: hard to reverse (a week of
refactoring, not a config flip), broad blast radius (structure, a critical -ility,
dependencies, interfaces, or construction techniques — Nygard's five), or the same question
keeps being re-debated. Record the promotion (`decisions.promoted_to = ADR-0003`) so the link
is never lost. ADRs are immutable after approval and carry `confirmation` — how compliance
will be verified. The `decisions-look-architectural` readiness advisory flags DECs that work
items implement, or that touch invariants/constraints, but were never promoted.

## Lifecycle statuses

Every status-bearing row carries `lifecycle_status` (the column name is uniform in v4 —
the three-axis doctrine below is why it is not just `status`).

```
Draft → Proposed → Approved → Implemented
                 ↘ Rejected
                 ↘ Deferred  (→ back to Proposed later)
        Approved/Implemented → Superseded (by a newer item) → Obsolete
```

- **Draft** — being written; not yet offered for approval.
- **Proposed** — offered to the human. The default for anything Tamheed authored on its own
  initiative.
- **Approved** — the human (or an authorized gate) accepted it. **Only Approved items
  constrain execution.**
- **Rejected** — considered and declined; kept with the reason (rejected alternatives are
  evidence).
- **Deferred** — postponed with a trigger/condition for revisiting.
- **Review** *(v4; wbs-items and slices only)* — **done-CLAIMED**: the agent asserts the work
  is complete but verification has not confirmed it. Counts as OPEN in every readiness
  closed-set; only the guarded transition to Implemented closes work.
- **Implemented** — done-VERIFIED: realized in the execution repo and past the readiness
  rules (phase/slice transitions to Implemented are guarded; `force` requires the operator's
  explicit words and leaves a forced-override audit event).
- **Superseded** — replaced; row points to its successor (`superseded_by`).
- **Obsolete** — retained for history, excluded from active views.

**Decision statuses** are exactly: Proposed, Approved, Rejected, Superseded, Deferred,
Implemented — `Draft` is unrepresentable on a decision row (CHECK-enforced). Never render a
Proposed decision as if Approved — this is a core safeguard.

**Lesson statuses** (v4.3) are exactly: Proposed, Approved, Rejected, Superseded, Obsolete —
no Draft (a lesson is born Proposed, awaiting the operator's interview) and no Deferred
(an undecided lesson keeps nagging via the `lessons-confirmed` advisory; Rejected is the
decided-no, kept as evidence). **Only operator-Approved lessons bind future sessions**
(rendered into the CLAUDE.md note, pinned lessons always). Approved lesson CONTENT is
immutable — supersede, never edit; `pinned`, the lifecycle transition, and `superseded_by`
stay operator-mutable (curation and closure are not content edits).

**Domain lifecycles** (same column name, domain vocabularies — CHECK-enforced):

| Family | `lifecycle_status` values |
|---|---|
| defect | Open, In-progress, Fixed, Won't-fix, Duplicate |
| deferred-work | Open, Activated, Scheduled, Done, Won't-do |
| scope-change | Proposed, Approved, **Merged** (deltas applied to the plan rows) |

**Three-axis status (ADR-0001, revised plan 031).** Lifecycle, verdict, and disposition are
independent columns:

- `lifecycle_status` — the sets above.
- `verdict` — **Met/Partial/Not-met/Pending** for audit verdicts;
  **Validated/Invalidated/Inconclusive/Pending** for experiments/POCs (a hypothesis verdict);
  **Pass/Fail/Pending** for tests. Domain sets are deliberate — a test result and a
  hypothesis outcome are different judgments.
- `disposition` ∈ {superseded, accepted-with-deviation, void} — always with a
  `disposition_reason_ref` to the deciding decision/ADR. A cancelled criterion is *void*,
  not *Not-met*.
- Risks additionally carry `risk_state` ∈ {open, mitigated, materialized, retired, accepted}
  with `discharged_by` naming the AC/test that retires the risk.
- **The risk scale (v4, plan 033):** `probability` = the judged likelihood the risk
  materializes; `impact` = the severity if it does — both on the `high/medium/low`
  enum. The enum IS the scale; there is no numeric tier behind it.

**Audit verdicts carry their evidence chain (v4):** `evidence` (what proves it),
`verified_by` (human/agent/ci), `verification_method` (auto-test/manual/inspection),
`against_commit` (what state it was judged against). A Met without evidence is *narrated*,
not *evidenced* — gate_run counts the split.

## The ambiguity marker (v4)

Never assume. Where prose is ambiguous, write `[NEEDS-CLARIFICATION: OQ-NNN]` in place and
create the OQ (with owner + due_by). G-COMPLETE validates markers: one citing an existing,
unresolved OQ is legal; a marker with no id, a dangling id, or a resolved cite is an
unfinished-marker failure. The `clarifications-open` advisory counts live markers.

## Versioning

- **Package / skill version:** semver `MAJOR.MINOR.PATCH`. MINOR = additive. MAJOR =
  breaking change to the store shape, identifiers, or the handoff contract; ships with an
  explicit migration (`package_migrate` — `package_open` refuses older stores).
- **Document rows:** narrative documents carry `lifecycle_status`; material change bumps it
  back through Proposed.
- **Immutable-after-approval** (ADRs incl. `confirmation`, approved acceptance criteria):
  never edit in place — supersede. Typos yes, meaning no (trigger-enforced).
- **Derived artifacts** (views, review.html, CSVs, the CLAUDE.md note span) are regenerated,
  never hand-edited.

## Cross-reference rules

- Reference any entity by its ID in running text: "mitigated by `RISK-012`", "per `DEC-004`".
- A row that exists because of another records the link as a **typed trace edge**
  (`derives_from`, `implements`, `verifies`, `tests`, `mitigates`, `discharges`,
  `blocked_by`, `satisfies`, `supersedes`, `scope_adds`/`scope_modifies`/`scope_removes`,
  `learned_from` — a lesson names what taught it: defect, decision, risk, slice,
  wbs-item, or progress-entry),
  not only in prose. `relates_to` is the documented untyped escape hatch. Endpoint types are
  enforced at write time and by the **blocking G-REL gate**.
- Every MVP `FR-/NFR-` must be reachable to ≥1 decision, ≥1 work item, and ≥1 test (G-TRACE);
  a requirement with zero edges trips the `requirements-wired` advisory.
- Waivers and gates point at entities via their own `applies_to` column, not edges.

## Supersession & deprecation

- Superseding creates a new ID and sets `superseded_by`/a `supersedes` edge; the old item
  stays (status Superseded) so history and rationale survive.
- Deprecating marks an item Obsolete with a one-line reason; downstream references are
  updated or explicitly noted as historical.
