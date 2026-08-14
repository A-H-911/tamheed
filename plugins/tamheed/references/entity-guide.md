# Entity Guide — the operator card (tamheed v4.1.0)

One row per entity family: when you need it and the one rule that keeps it honest.
Columns and constraints: `../db/schema.sql` (the single source of data shape). Families,
classes, purposes: `artifact-catalog.md`. Identifiers and statuses: `governance.md`.
The full per-entity study — rationale, design decisions, cost-of-omission — lives in the
repo's `docs/entities.md` (not shipped in this bundle).

## The families

| Family | Prefix | When you need it | The one rule to remember |
|---|---|---|---|
| requirement | `FR-`/`NFR-` | Always — the contract everything serves | `source_kind`+`source_span` are NOT NULL (G-REQ-SRC); unsourced = demote to assumption |
| constraint | `CON-` | An imposed limit the design cannot negotiate | It is not a requirement — it was never optional |
| invariant | `INV-` | A property that must NEVER break | Say HOW in `enforcement`, or it is a wish |
| assumption | `ASM-` | The moment you catch yourself inferring | Give it `risk_if_wrong` + `validation_date`; assumptions decay |
| dependency | `DEP-` | The plan waits on something external | Name the `owner` or it is a hope |
| open-question | `OQ-` | Any ambiguity — never assume | Cite it in prose as `[NEEDS-CLARIFICATION: OQ-NNN]`; a dead cite fails G-COMPLETE |
| glossary-term | `GT-` | On request, jargon-heavy domains | One GT- beats three OQ-s about the same word |
| decision | `DEC-` | ANY decision — scope, vendor, priority, process | Born Proposed (no Draft); only Approved decisions constrain execution |
| adr | `ADR-` | The one-way doors (hard to reverse, broad blast radius) | Immutable after approval — supersede, never edit; write `confirmation` |
| risk | `RISK-` | Always — the register with a pulse | Not handled until `discharged_by` names the AC/test that retires it |
| hypothesis | `HYP-` | An unknown blocking a decision | `metric` + `threshold` BEFORE the experiment runs |
| experiment / poc | `EXP-`/`POC-` | Settling a hypothesis / proving a build approach | Verdict is Validated/Invalidated/Inconclusive — not Pass/Fail |
| test | `TEST-` | Planned verification, before code exists | Every MVP requirement must reach ≥1 test (G-TRACE) |
| kpi | `KPI-` | Success metrics for the charter | A goal without `measure`+`target` is a mood |
| stakeholder | `STK-` | Who cares and why | Label column is `title`; as an edge source, `relates_to`-only |
| acceptance-criterion | `AC-` | Always — the done-contract | Bind to a requirement AND a slice; immutable after approval; cancel = disposition `void`, never fake Not-met |
| audit-verdict | `AV-` | Every time an AC is judged | Verdicts APPEND — the latest wins; carry `evidence`, `verified_by`, `against_commit` |
| phase | `PH-` | Always — the roadmap's chapters | Implemented is a guarded transition; `force` needs the operator's words |
| slice | `SL-` | The unit branches/PRs/ACs bind to | `Review` = claimed, `Implemented` = verified; Review counts as OPEN |
| milestone | `MS-` | A dated roadmap label, nothing more | It never gates — a milestone that gates is an execution-gate |
| wbs-item | `WBS-` | The work breakdown; the backlog is `v_backlog` | Review stays on the backlog — only Implemented leaves it |
| execution-plan | `EP-` | Per-slice how-to that survives the session | Get it Approved before building from it |
| execution-gate | `GATE-` | A human judgment point (DoR/DoD/checkpoint/approval) | Prose a HUMAN evaluates — surfaced as `human_required`; outcome Go/Hold/Redirect/Kill |
| convention | `CONV-` | A durable rule the executor must honor | State it once here, not in every prompt |
| defect | `DEF-` | Every found bug — including flaky tests | Open critical/high BLOCK readiness; medium/low advise; set `found_in` or it is invisible to scoped readiness |
| deferred-work | `DW-` | Consciously postponed work | Severity + `activation_trigger` + `invariant_at_stake` — "later" needs a when |
| scope-change | `SC-` | The plan and reality diverge | SC- row FIRST (with `decision_ref`); Merged only after the deltas land in the plan rows |
| waiver | `WVR-` | A readiness rule must be excepted | Operator-only `approver` — never the working agent; reported as waived, never silent |
| progress-entry | `PE-` | The execution journal | Typed events, append-only; fix mistakes with a `correction` entry via `corrects` |
| narrative-document / section | `DOC-`/`SEC-` | Charter-class prose humans read | Prose complements rows — approvals live on rows, not in paragraphs |
| diagram | `DIA-` | Context/component/integration/deployment/data-flow | Mermaid source in `body`; kind set is CHECK-enforced |

## The lifecycle in 10 lines

1. Everything starts `Draft` (decisions start `Proposed` — Draft is unrepresentable there).
2. `Proposed` = offered to the human; the default for anything tamheed authored itself.
3. `Approved` = the human accepted it. Only Approved items constrain execution.
4. `Rejected` and `Deferred` are kept — rejected alternatives are evidence.
5. `Review` (wbs-items/slices only) = done-CLAIMED. It counts as OPEN everywhere.
6. `Implemented` = done-VERIFIED, past the readiness rules (guarded transition).
7. `Superseded` → `Obsolete` close the tail; the old row stays, pointing at its successor.
8. Domain sets: defects Open→Fixed/Won't-fix; deferred-work Open→Done/Won't-do;
   scope-changes Proposed→Approved→Merged.
9. Verdicts are a separate axis: Met/Partial/Not-met/Pending (audits),
   Pass/Fail/Pending (tests), Validated/Invalidated/Inconclusive/Pending (experiments).
10. Disposition is the third axis (superseded / accepted-with-deviation / void) and always
    carries `disposition_reason_ref`.

## The claimed-vs-verified rule

An agent saying "done" is a claim, not a fact. Set the slice/wbs-item to `Review`, record
`audit_record` verdicts with `evidence`, `verified_by`, `verification_method`, and
`against_commit`, then let `readiness_check` clear the transition to `Implemented`. A Met
without evidence is narrated, not evidenced — and verdicts append, so an old Met never
survives a newer Not-met.

## The drift rule

Never edit the plan to match reality without a record. `scope-change` row first (Proposed,
with its authorizing `decision_ref`), typed delta edges (`scope_adds` / `scope_modifies` /
`scope_removes`) naming the affected rows, operator approval, THEN apply the row changes
via `entity_upsert`, THEN set the SC- to `Merged`. Approved-never-Merged trips the
`scope-changes-merged` advisory.

## The waiver rule

A blocked readiness rule has exactly three exits: fix the failing entity, disposition it
with a reason, or a `WVR-` waiver. Waivers are operator-approved only — `approver` is an
operator identity, never the working agent — scoped (prefer `applies_to` per entity over
whole-rule), justified, and expiring. The readiness report shows them as `waived`, never
silently green; expired waivers are surfaced and ignored.

## The marker rule

Never assume. Where prose is ambiguous, write `[NEEDS-CLARIFICATION: OQ-NNN]` in place and
create the OQ with `owner` + `due_by`. G-COMPLETE validates every marker: citing a live,
unresolved OQ is legal; no id, a dangling id, or a resolved cite is an unfinished-marker
failure. Resolve the OQ, then remove the marker (`clarifications-open` counts the rest).
