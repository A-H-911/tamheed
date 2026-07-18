# Tamheed Workflow

This is the human-facing explanation of Tamheed's **22-stage interactive model**: why it is interactive and
staged, how the three phase groups fit together, how documents and decisions move through their lifecycle,
and the philosophy behind the gates. It is the orientation; the **authoritative, operational per-stage spec**
(inputs, activities, outputs, entry/exit criteria, validation, failure handling, human-intervention points,
and artifacts) lives in [`../plugins/tamheed/references/workflow.md`](../plugins/tamheed/references/workflow.md). This document
summarizes and links — it does not re-paste the operational spec.

> See also: [`methodology.md`](methodology.md) (rationale), [`../plugins/tamheed/references/artifact-catalog.md`](../plugins/tamheed/references/artifact-catalog.md)
> (what each stage produces), [`../plugins/tamheed/references/quality-gates.md`](../plugins/tamheed/references/quality-gates.md) (gate
> definitions), and [`../plugins/tamheed/references/governance.md`](../plugins/tamheed/references/governance.md) (statuses and IDs).

## Why interactive, not a single prompt

A project description is almost never complete, consistent, and unambiguous on first contact. It contains
gaps, hidden contradictions, unstated assumptions, and solution choices smuggled in as requirements. A
one-shot generator forced to produce a finished plan from that input has only one way to cope: it invents.
It guesses the missing requirement, silently resolves the contradiction, quietly picks a technology, and
presents the result as if it were grounded. The plan *looks* finished and is quietly wrong.

Tamheed is interactive precisely to refuse that bargain. It pauses where an answer would change the plan and
asks a focused question; everywhere else it records an explicit assumption with its risk-if-wrong and
continues. It treats unresolved questions and rejected alternatives as first-class outputs rather than things
to bury. The human stays in the loop at the points that matter — confirming scope, approving key decisions,
approving the roadmap, approving the handoff, and giving the final go/no-go — and stays out of the
way everywhere else. The result is a plan whose every claim can be traced to a source, a decision, or an
acknowledged assumption.

## Why staged

The work is staged because the dependencies are real. You cannot sensibly compare technologies before you
know the requirements; you cannot lock scope while a blocking contradiction is unresolved; you cannot write a
trustworthy handoff before the package passes its quality gates. Each stage has explicit **entry and exit
criteria**, so the process advances only when the prerequisites genuinely hold. Staging also makes the
process *resumable* and *partial*: because state is persisted, work can stop after intake, resume from the
last completed stage, or re-run a single stage without redoing everything. The invocation modes (`full`,
`intake`, `plan`, `resume`, `stage:<id>`, `update`, `migrate`, `adopt`) are exactly these stop/start points;
they change *where* the workflow runs, never the methodology. See [`../plugins/tamheed/references/modes.md`](../plugins/tamheed/references/modes.md).

## The three phase groups

**Phase A — Understand (stages 1–8).** Establish a faithful, normalized picture of the problem before
proposing any solution. Intake and classify the input; extract requirements verbatim with source spans and
normalize them into identified registers; detect ambiguity, contradictions, and hidden dependencies; clarify
the things that block the plan; and lock scope, goals, non-goals, and success metrics in the charter. Nothing
is invented here — inferences become assumptions, gaps become open questions.

**Phase B — Explore (stages 9–15).** Resolve the uncertainty that blocks decisions, proportionally to the
risk. Plan research against the riskiest unknowns; explore candidate architectures and name the decision
points; compare options on explicit weighted criteria; turn blocking unknowns into falsifiable hypotheses and
minimal experiments/POCs; capture decisions with status, rationale, alternatives, and consequences (promoting
significant ones to ADRs); and analyze risk across technical, dependency, platform, delivery, and compliance
dimensions. Findings, proposals, and approved decisions stay in separate registers.

**Phase C — Plan & hand off (stages 16–22).** Turn understanding and decisions into something an agent can
execute. Produce a gated phased roadmap sliced for delivery and an actionable, testable work breakdown;
generate the selected entity set (trace edges written live as decisions are made); materialize the package
store and write back canonical JSONL for the operator to commit; validate against the quality gates
(`gate_run`); emit the Claude-Code-targeted handoff (`handoff_emit`, injection-screened, installing the
executor-side MCP config); run progress and decision update cycles through the MCP tools; and emit the
final readiness go/no-go from the gate report.

## Document and decision lifecycle

Everything Tamheed produces carries a status, so a reader always knows how much weight it bears. In v2
the status is **three-axis** (ADR-0001): `lifecycle_status` (the flow below), `verdict` (Met/Not-met,
PASS/FAIL — outcomes, not lifecycle), and `disposition` (superseded / accepted-with-deviation / void —
always with the deciding decision reference).

**Documents and register rows** move through:
`Draft → Proposed → Approved → Implemented`, with side exits to `Rejected`, `Deferred` (which can return to
`Proposed`), and `Superseded → Obsolete`. Only **Approved** items constrain execution. *Draft* is being
written; *Proposed* is offered to the human and is the default for anything Tamheed authored on its own
initiative; *Approved* has been accepted; *Rejected* is declined but kept with its reason; *Deferred* is
postponed with a trigger; *Superseded* points to its successor; *Implemented* is realized in the execution
repo; *Obsolete* is retained for history only.

**Decisions** use a deliberately narrow status set — exactly **Proposed, Approved, Rejected, Superseded,
Deferred** (+ terminal `Implemented`). A Proposed decision is never rendered as if Approved; that is a core
safeguard — and in v2 it is a CHECK constraint: a `Draft` decision is literally unrepresentable in the
store. **Immutable-after-approval** artifacts (ADRs, approved acceptance criteria) are never edited in
meaning — they are superseded by a new item. **Derived** artifacts (the traceability matrix, the readiness
report, roadmap rollups) are regenerated from their sources, never hand-edited. Full status semantics,
identifiers, versioning, and supersession rules: [`../plugins/tamheed/references/governance.md`](../plugins/tamheed/references/governance.md).

## Gate philosophy: critical vs warn, loops as discipline

Gates are how Tamheed decides whether it has earned the right to advance or to declare a package
execution-ready. They come in two severities. **Critical** gates block readiness — a package with a failing
critical gate is *not ready*, full stop, and the report says so rather than papering over it. **Warn** gates
surface issues that should be seen but do not block; a Warn gate may be passed by recording an accepted,
attributed exception. A package is execution-ready only when every Critical gate passes and every Warn gate
is passing or carries a recorded exception. The full gate list and severities are in
[`../plugins/tamheed/references/quality-gates.md`](../plugins/tamheed/references/quality-gates.md).

**Loops are discipline, not failure.** Clarification (stage 7), decision capture (stage 14), and validation
(stage 19) routinely send the process back upstream — a contradiction surfaces late, an experiment refutes a
hypothesis, a gate catches an unlinked requirement. Returning to an earlier stage is the system working as
intended, not a defect. The one rule is that the *reason* for looping is recorded (a note or a `DEC-`) so the
trail stays intact. **Do not skip a gate to look finished** — a plan that looks complete but hides an
unresolved contradiction or an unsourced requirement is exactly the failure mode Tamheed exists to prevent
— and for the referential tier the store refuses the write outright.

## Human-intervention points

The human is asked to act at a small number of high-leverage gates, marked in the per-stage spec. In order,
they are: confirm the request scope/mode (stage 1) and the project profile (stage 2); answer the batched
clarification questions (stage 7, the primary clarification point); approve the locked scope (stage 8);
confirm research depth and experiment budgets for large efforts (stages 9, 13); approve key decisions (stage
14); confirm risk appetite (stage 15); approve the roadmap (stage 16); commit the materialized package data
(stage 18 — the operator owns the repository); review non-critical warnings (stage 19); approve the handoff
(stage 20); approve material changes during update cycles (stage 21); and give the final go/no-go (stage
22). Tamheed never passes an approval gate on the user's behalf.

## Stage summary

A compact index of all 22 stages. **Per-stage operational detail (In · Do · Out · Enter · Exit · Validate ·
Fail · Human · Artifacts) is in [`../plugins/tamheed/references/workflow.md`](../plugins/tamheed/references/workflow.md)** — this table
does not replace it. Gate IDs reference [`../plugins/tamheed/references/quality-gates.md`](../plugins/tamheed/references/quality-gates.md);
✅ in the Gate column marks a human approval point.

### Phase A — Understand

| # | Name | Purpose | Key outputs | Gate |
|---|---|---|---|---|
| 1 | Intake | Capture raw input with provenance; attach to the package | `package_create` — the package row seeded; archived input | Confirm request scope/mode ✅ |
| 2 | Initial classification | Classify project type, size, risk; pick a profile that biases selection + research depth | `profile` on the package row | Confirm/adjust profile ✅ |
| 3 | Requirement extraction | Extract candidate requirements **verbatim** with source spans; tag FR/NFR/CON/preference | Draft requirement candidates | Every requirement-bearing span extracted or marked out-of-scope |
| 4 | Requirement normalization | Assign IDs, dedupe, split compounds, classify, prioritize (MVP/Full) | `requirement` rows (Draft) | G-REQ-SRC + G-IDS enforced at write time (schema) |
| 5 | Ambiguity detection | Find vague terms, undefined quantities, unclear actors, missing acceptance | Ambiguity list → candidate `OQ-` | Each ambiguity becomes `OQ-` or `ASM-` |
| 6 | Contradiction & dependency detection | Detect conflicts, hidden dependencies, premature solution decisions in the brief | Contradiction list, `DEP-`, flagged premature decisions | G-CONFLICT (no unresolved hard conflict past scope) |
| 7 | Clarification | Batch focused questions where the answer changes the plan; else record `ASM-` | Answered `OQ-`, new `ASM-`, updated requirements | **Primary clarification point** ✅ |
| 8 | Scope definition | Lock goals, non-goals, in/out-of-scope, success metrics; write the charter | Charter as `narrative-document` + sections (Proposed); `kpi`/`stakeholder` rows | Approve scope ✅ |

### Phase B — Explore

| # | Name | Purpose | Key outputs | Gate |
|---|---|---|---|---|
| 9 | Research planning | Size research to genuine uncertainty; target the riskiest unknowns | Research plan, R&D backlog | Confirm depth for large efforts ✅; effort proportional to risk |
| 10 | Architecture exploration | Explore candidate architectures/components; name decision points; draft diagrams | Architecture draft + diagrams | Architecture covers all MVP requirements |
| 11 | Option comparison | Compare options on **explicit weighted criteria**; keep losers | Technology-comparison matrices | Criteria stated before scoring; claims cited or `unverified` |
| 12 | Hypothesis definition | State falsifiable hypotheses with confirm/refute signals | Hypothesis register (`HYP-`) | Each blocking unknown has a hypothesis or a decision |
| 13 | POC & experiment planning | Plan minimal experiments/POCs with PASS/FAIL + timebox | `EXP-`/`POC-` plans | Approve experiment budget for costly POCs ✅ |
| 14 | Decision capture | Record decisions with status, rationale, alternatives, consequences; promote to ADRs | `decision` + `adr` rows (promotion link recorded) | G-DEC-STATUS enforced at write time; approve key decisions ✅; losers retained |
| 15 | Risk analysis | Enumerate + score risks; write mitigations; tag MVP/Full | Risk register (`RISK-`) | G-RISK; confirm risk appetite ✅ |

### Phase C — Plan & hand off

| # | Name | Purpose | Key outputs | Gate |
|---|---|---|---|---|
| 16 | Execution planning | Phased roadmap → slices, work breakdown, milestones, execution gates, per-slice plans, conventions | `phase`/`slice`/`wbs-item`/`milestone`/`execution-gate`/`execution-plan`/`convention` rows | G-EXEC (phases sliced; leaf items actionable+testable); approve roadmap ✅ |
| 17 | Artifact generation | Populate the selected entity families + narrative sections; trace edges written live | The populated package store | G-COMPLETE, G-TRACE (no stubs; every MVP requirement linked) |
| 18 | Package storage initialization | Materialize the store; write back canonical JSONL (`package_close`) | `data/*.jsonl` for the operator to commit | Operator commits the package data ✅ (no repo scaffolding — removed in v2, ASM-B) |
| 19 | Quality validation | `gate_run`: coverage views + content scan (referential tier already held at write time) | Gate report; `omission` rows for absent Always families | All **Critical** gates pass; review warnings ✅ |
| 20 | Execution-agent handoff | `prompt` rows; `handoff_emit` screens (G-INJECT), writes prompts + executor-side MCP config | `handoff/` in the target project + `.mcp.json` + `CLAUDE.md` note | G-HANDOFF + G-INJECT; approve handoff ✅ |
| 21 | Progress & decision update cycles | `progress_update` / `audit_record` (evidence refs) / `work_bind`; typed scope changes bump the iteration | Progress entries, audit verdicts, `scope-change` rows | Cascades fire in-transaction; G-PROGRESS; approve material changes ✅ |
| 22 | Final readiness assessment | `gate_run` again; summarize gates, open items, residual risk; state go/no-go | Readiness verdict (from the gate report; `go_no_go` on the package row) | No Critical gate failing; final go/no-go ✅ |

## Where this document stops

This is orientation and philosophy. For exactly what each stage consumes and produces and how it validates,
read [`../plugins/tamheed/references/workflow.md`](../plugins/tamheed/references/workflow.md). For which artifacts a stage may emit and
their generation classes, read [`../plugins/tamheed/references/artifact-catalog.md`](../plugins/tamheed/references/artifact-catalog.md). For the gate definitions and
severities, read [`../plugins/tamheed/references/quality-gates.md`](../plugins/tamheed/references/quality-gates.md).
