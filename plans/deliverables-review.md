# Deliverables review — the Tamheed v2 artifact set

Decision record for plan `plans/006-b7-artifact-set-review.md` (B7). This file is the **input
contract for plan 007 (B2)**; later changes go through a scope-change decision in the v2 flow,
never by silent edits here.

> **APPROVED by maintainer on 2026-07-17** — all rows decided across four interactive review
> rounds (R1 field-evidence seeds, R2 structural merges, R3 keep-batch + derived-as-views,
> R4 taxonomy confirmations) plus the seven pre-approved decisions from the 2026-07-17 interview.
> Zero undecided rows. Plan 007 (B2) is unblocked by this approval.

**Inputs read end to end:** `plugins/tamheed/references/artifact-catalog.md` (63 table rows on disk
vs "~45" in the plan — delta is section-rows and per-kind diagram rows; judged not material),
`plugins/tamheed/references/artifact-rules.md`, and
`generated-samples/support-triage-agent/manifest.json` (`omitted_artifacts[]` = field-usage evidence).

**Legend:** Proposal ∈ keep / merge-into X / drop / restructure / add-new.
Markers: **[PRE-APPROVED]** = maintainer 2026-07-17 interview, skipped in rounds;
**[R*n*]** = decided in interactive round *n* (all rounds completed 2026-07-17).

---

## 1. Charter & scope

| Artifact | v1 class | Proposal | Rationale (≤2 sentences) | v2 entity impact |
|---|---|---|---|---|
| Project charter | Always | **keep [R3]** | Anchor narrative of every package; demo generated and approved it (manifest `00-charter.md`). | Narrative document; hosts the confirmed `kpis` table data. |
| Executive summary | Always | **keep [R3]** | Demo kept it as a separate `01-executive-summary.md`; distinct audience from the charter. | Narrative document. |
| Problem statement | Always (charter §) | **restructure — fold catalog row into the charter row [R2]** | Catalog itself says "within charter template" (catalog L47); a section is not a separate artifact. | None — charter section. |
| Goals / non-goals | Always (charter §) | **restructure — fold into charter row [R2]** | Same: "(within charter template)" (catalog L48); locked at stage 8 stays a charter property. | None — charter section. |
| Scope / out-of-scope | Always (charter §) | **restructure — fold into charter row [R2]** | Same section-row (catalog L49); scope-drift-needs-a-DEC rule carries to v2 unchanged. | None — charter section. |
| Success metrics / KPIs | Always (charter §) | **restructure — fold into charter row; KPI data first-class [R2]** | Section of the charter (catalog L50); the `kpis` **table** is already maintainer-confirmed 2026-07-17. | `kpis` entity (confirmed). |
| Stakeholder register | Conditional | **drop standalone document [PRE-APPROVED]** | Charter's stakeholder table covers it; demo omitted it ("captured in the charter"). | `stakeholders` entity stays first-class (confirmed 2026-07-17) — the document dies, the data lives. |

## 2. Requirements & registers

| Artifact | v1 class | Proposal | Rationale (≤2 sentences) | v2 entity impact |
|---|---|---|---|---|
| Functional requirements (`FR-`) | Always | **keep [R3]** | Core register; every row keeps its `source` (catalog L57). Field evidence (seed 11) says bias to fewer, sharper FRs — see Right-sizing decision below. | `requirements` entity (kind=functional). |
| Non-functional requirements (`NFR-`) | Always | **keep [R3]** | Same register family, same provenance rule (catalog L58). | `requirements` entity (kind=non-functional). |
| Constraint register (`CON-`) | Always | **keep [R3]** | Distinct semantics from requirements (externally imposed); demo populated it. | `constraints` entity. |
| Invariant register (`INV-`) | Conditional | **keep [R3]** | Non-negotiables surfaced early in handoff (catalog L60); demo's AGENTS.md leads with them. | `invariants` entity; referenced by `deferred_work.invariant_at_stake` if seed 8 lands. |
| Assumption register (`ASM-`) | Always | **keep [R3]** | Each row carries `risk_if_wrong` (catalog L61) — cheap, high-value. | `assumptions` entity. |
| Dependency register (`DEP-`) | Conditional | **keep [R3]** | Trigger (external dependencies) worked in the demo — generated with reason. | `dependencies` entity. |
| Open-question register (`OQ-`) | Always | **keep [R3]** | Load-bearing in all three field deployments (seed 11 evidence). | `open_questions` entity. |
| Open-decision register (`DEC-`) | Always | **keep [R3]** | Load-bearing in all three field deployments; status set enforced by G-DEC-STATUS. | `decisions` entity. |

## 3. Research & experiments

| Artifact | v1 class | Proposal | Rationale (≤2 sentences) | v2 entity impact |
|---|---|---|---|---|
| Research plan | Conditional | **keep [R3]** | Demo omitted it with a clean reason ("uncertainty is narrow… EXP-001 cover it") — the trigger works as designed. | Narrative document. |
| R&D backlog | Conditional | **merge into research plan [R2]** | Demo: "a backlog would only restate them" (manifest `rnd-backlog` omission). | None — research plan gains an optional backlog section; `hypotheses`/`experiments`/`pocs` entities carry the data. |
| Hypothesis register (`HYP-`) | Conditional | **keep [R3]** | Falsifiable hypotheses drove the demo's EXP/POC chain. | `hypotheses` entity. |
| Experiment plans (`EXP-`) | Conditional | **keep [R3]** | PASS/FAIL + timebox discipline (catalog L73); demo's PH-2 gate hangs off EXP-001. | `experiments` entity. |
| POC plans + results (`POC-`) | Conditional | **keep [R3]** | Shares the experiment schema in v1 (catalog L74); results append-only. | `pocs` entity (confirmed 2026-07-17). |
| Evaluation framework | Conditional (§) | **restructure — fold row into research-plan / tech-comparison rows [R2]** | Already "a section within research-plan / technology-comparison" (catalog L75). | `comparison_criteria` data shape kept where used. |

## 4. Architecture & decisions

| Artifact | v1 class | Proposal | Rationale (≤2 sentences) | v2 entity impact |
|---|---|---|---|---|
| Architecture document | Conditional | **keep [R3]** | Must cover all MVP requirements (catalog L81); demo generated it. | Narrative document. |
| Context diagram | Conditional | **restructure — collapse into one "diagrams" family row [R2]** | Demo emitted four diagram files under one trigger; kinds are data, not separate artifacts. | `diagrams` rows (kind, class) on the package; extension registry can add kinds. |
| Component diagram | Conditional | **restructure — same collapse [R2]** | Same. | Same. |
| Deployment diagram | On-request | **restructure — same collapse, per-kind class kept [R2]** | Same; On-request class preserved as the kind's default. | Same. |
| Data-flow diagram | On-request | **restructure — same collapse [R2]** | Same. | Same. |
| Integration diagram | Conditional | **restructure — same collapse [R2]** | Same. | Same. |
| Architecture Decision Record (`ADR-`) | Conditional | **keep [R3]** | Immutable-after-approval, supersede-never-rewrite (catalog L87); load-bearing in all three field deployments (seed 11). | `adrs` entity, immutable semantics. |
| Technology comparison matrices | Conditional | **keep [R3]** | Demo omitted with a clean reason ("no live two-option tech choice") — trigger works. | Narrative + `comparison_criteria` data. |
| Technology assessments | Conditional (§) | **restructure — fold into tech-comparison row [R2]** | Already a section of the same file (catalog L89). | None. |

## 5. Risk

| Artifact | v1 class | Proposal | Rationale (≤2 sentences) | v2 entity impact |
|---|---|---|---|---|
| Risk register (`RISK-`) | Always | **keep + restructure — add lifecycle [R1]** | tarseem shipped v1.0.0 with 29 risks still "Draft for approval" and no state model; acmp's RISK- family had zero commit references. | `risks` entity with status ∈ open/mitigated/materialized/retired/accepted, updated during execution sync. |
| Mitigation plan | Always (fields) | **restructure — fold row into risk-register row [R2]** | Already "mitigation fields" within the register (catalog L96). | Fields on `risks`. |

## 6. Planning & execution

| Artifact | v1 class | Proposal | Rationale (≤2 sentences) | v2 entity impact |
|---|---|---|---|---|
| Phased roadmap (`PH-`) | Always | **keep + restructure — two-level phase→slice [R1]** | Every field project invented finer granularity under PH- (acmp P1–P19 slice ladder; Marid ran on WBS; tarseem on spikes); slices are what branches/PRs/ACs bind to. | `phases` + first-class `slices` entities; WBS items relate to slices. |
| Work breakdown (`WBS-`) | Conditional | **keep [R3]** | Heavily used in Marid, unused in acmp — keep Conditional, right-size per profile (seed 11). | `wbs_items` entity. |
| Milestones (`MS-`) | Conditional | **merge into roadmap [PRE-APPROVED]** | Demo: milestones "captured inline in planning/roadmap.md; a separate file would duplicate." | MS- data lives inline on `phases`/roadmap; no standalone document. |
| Execution backlog | Conditional | **restructure — a query over `wbs_items`, not a stored artifact [PRE-APPROVED]** | Demo: "a separate backlog adds no operational value at this size"; the backlog IS a view. | View/query; no entity, no file. |
| Deferred-work / tech-debt register | Conditional | **restructure — promote to first-class register [R1]** | ALL THREE field projects hand-rolled one outside the ID scheme (acmp D-01..22 — its most active governance surface; Marid's 11-item register with severity + invariant-at-stake; tarseem TD- + backlog.md). | `deferred_work` entity (severity, activation trigger, invariant-at-stake FK, status incl. Won't-do); gets an ID prefix in the scheme. |
| Definition of Ready | Conditional | **merge into "execution gates" [PRE-APPROVED]** | Three thin Conditional docs; demo omitted all three with one shared reason. | Part of `execution_gates`. |
| Definition of Done | Conditional | **merge into "execution gates" [PRE-APPROVED]** | Same. | Part of `execution_gates`. |
| Checkpoints (review/approval gates) | Conditional | **merge into "execution gates" [PRE-APPROVED]** | Same. | Part of `execution_gates`. |
| Defect log | — (new) | **add-new, Conditional [PRE-APPROVED]** | v1 handoff follow-up prompts already imply defect tracking; make it first-class. | `defects` entity. |
| Phase-exit report | — (new) | **add-new [PRE-APPROVED]** | Same evidence base — situational prompts mention phase-exit summaries. | Derived per phase gate. |

## 7. Validation & traceability

| Artifact | v1 class | Proposal | Rationale (≤2 sentences) | v2 entity impact |
|---|---|---|---|---|
| Acceptance criteria (`AC-`) | Always | **keep [R3]** | Immutable-after-approval retained; field evidence (near-zero AC commit refs) argues for fewer, sharper ACs — see Right-sizing. | `acceptance_criteria` entity. |
| Acceptance audit | Derived / Conditional | **promote to Always during execution [PRE-APPROVED]** | The v2 execution-tracking loop is central (progress sync in `update` mode); today Conditional. | Verdicts (Met/Partial/Not-met/Pending) as data tied to `acceptance_criteria`; feeds G-PROGRESS. |
| Test strategy (`TEST-`) | Conditional | **keep [R3]** | Trigger (non-trivial NFRs / handoff) worked in the demo. | `tests` entity (confirmed 2026-07-17). |
| Validation strategy | Conditional (§) | **restructure — fold row into test-strategy row [R2]** | Already "(validation-approach section)" of the same file (catalog L118). | None. |
| Traceability matrix | Derived (Always) | **restructure — derived view; file is a regenerated export [R3]** | Catalog already says derived-regenerate (L119); in v2 the relations ARE the store, so the matrix is a query rendered at handoff/sync. G-TRACE checks unchanged. | No entity — a query over the requirement→decision→work→test→risk→AC relations. |

## 8. Progress

| Artifact | v1 class | Proposal | Rationale (≤2 sentences) | v2 entity impact |
|---|---|---|---|---|
| Progress log | Continuous | **keep [R3]** | Append-only journal is the raw record the rest derives from (catalog L125). | `progress_events` entity, append-only. |
| Status report | Derived / Continuous | **restructure — derived view; file is a regenerated export [R3]** | Already derived-regenerate each cycle (catalog L126); same treatment as traceability matrix. | No entity — query over progress + audit data. |

## 9. Handoff

| Artifact | v1 class | Proposal | Rationale (≤2 sentences) | v2 entity impact |
|---|---|---|---|---|
| Handoff instructions (overview) | Always | **keep [R3]** | Orientation surface for the executing agent. | Narrative document. |
| Initial prompt | Always | **keep [R3]** | "Orient + one bounded task + approval gate" (catalog L133) is the handoff contract. | Narrative document. |
| Follow-up prompts | Conditional | **keep [R3]** | One per phase gate + situational (catalog L134); demo generated them. | Narrative document. |
| Review prompts | Conditional | **keep [R3]** | Audit / readiness-recheck / PR review (catalog L135); demo generated them. | Narrative document. |
| Handoff manifest | Always | **merge into package manifest [R2]** | Two machine-owned manifests in one package; v2's relational state makes a second manifest redundant — demo's `manifest.json` already carries entry point, go/no-go, gated items. | Handoff fields (entry point, go/no-go, gated items) become sections of `manifest.json` / state. |
| Final execution-readiness report | Always | **keep [R3]** | Stage-22 go/no-go on Critical gates (catalog L137); derived-regenerate. | Derived from gate results data. |

## 10. Governance & repository

| Artifact | v1 class | Proposal | Rationale (≤2 sentences) | v2 entity impact |
|---|---|---|---|---|
| Repository bootstrap script | Conditional | **keep [R3]** | Dry-run-capable, idempotent, never-overwrite (catalog L143); repo-requested trigger works. | Emitted tool, not an entity. |
| Contribution doc | Conditional | **keep [R3]** | Multi-contributor trigger; demo inherited it rather than duplicating — correct behavior. | Narrative document. |
| Governance doc | Conditional | **keep [R3]** | Same trigger and behavior. | Narrative document. |
| Naming conventions | Conditional | **keep [R3]** | Same. | Narrative document. |
| Documentation templates | On-request | **keep [R3]** | Only when the user asks — cheapest possible class. | None. |
| Review / approval gates (definitions) | Always (definitions) | **merge into "execution gates" [R3]** | Lives in `execution/checkpoints.md` + readiness report (catalog L148); the pre-approved DoR/DoD/checkpoints merge naturally absorbs it. Readiness report keeps applying the gates at stage 22. | Part of `execution_gates`. |

## 11. Package-level

| Artifact | v1 class | Proposal | Rationale (≤2 sentences) | v2 entity impact |
|---|---|---|---|---|
| Package README | Always | **keep [R3]** | Consumption + reading order for the agent (catalog L154). | Narrative document. |
| Agent-control surface (`CLAUDE.md`+`AGENTS.md`) | Derived / Conditional | **keep [R3]** | The ambient control surface Claude Code auto-loads (catalog L155); renders/links registers, never a second copy. | Derived — rendered from invariants/constraints/phase data. |
| Package manifest | Always | **keep [R3]** | Machine-owned inventory incl. omission reasons — the G-SET substrate. | Machine-owned; absorbs handoff manifest if that merge lands. |
| Normalized state (`keystone-state.json`) | Always | **restructure — replaced by the v2 relational store [R3]** | v1's machine-owned resume/update state is exactly what plan 007 turns into entities; no parallel JSON state file. | The entire v2 data model replaces this file (plan 007 owns schema + storage form / DDL). |

---

## Cross-cutting decisions

### Field-evidence seeds (presented with evidence, R1)

- **Seed 8 — deferred-work register: ADOPTED [R1]** — promote to first-class with the full
  `deferred_work` entity (severity, activation trigger, invariant-at-stake FK, status incl. Won't-do);
  ID prefix added to the scheme. Always at handoff / long execution horizon.
- **Seed 9 — phase→slice roadmap: ADOPTED [R1]** — `phases` + first-class `slices` entity; slices are
  the unit branches/PRs/ACs bind to; WBS items relate to slices.
- **Seed 10 — risk lifecycle: ADOPTED [R1]** — `risks.status ∈ open/mitigated/materialized/retired/
  accepted`, updated during execution sync; risks stop being write-only.
- **Seed 11 — per-register right-sizing: ADOPTED as selection guidance [R1]** — v2 artifact-rules bias
  registers by evidence (fewer/sharper FR+AC, rich DEC/OQ/ADR, WBS per profile); no register dropped.
  Evidence: WBS heavily used in Marid, unused in acmp; FR/AC near-zero commit references in all three
  deployments; ADR/DEC/OQ load-bearing everywhere.

### Narrative documents vs register entities — **APPROVED [R4]**

**Narrative documents** (prose, versioned-on-change): charter, executive summary, architecture doc,
research plan, tech comparison, handoff overview/prompts, README, governance docs, agent-control
surface.
**Register entities** (relational, plan 007): everything carrying an ID prefix — FR/NFR/CON/INV/ASM/
DEP/OQ/DEC/HYP/EXP/POC/ADR/RISK/KPI/STK/PH/WBS/AC/TEST — plus new `deferred_work`, `defects`,
`execution_gates`, `slices`.
**Derived views** (queries with regenerated file exports): traceability matrix, status report,
execution backlog, readiness report, phase-exit report, acceptance-audit rendering.

### Profile taxonomy — **CONFIRMED [R4]**

v1's five profiles — **enterprise, rnd, legacy, ai-agentic, unknown** — carry into v2 as-is.
Selection rules (including the new right-sizing guidance from seed 11) key off them.

### Already confirmed — no review round

`tests`, `kpis`, `pocs`, `stakeholders` tables confirmed by maintainer 2026-07-17.
