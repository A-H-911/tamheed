# Keystone Workflow

This is the human-facing explanation of Keystone's **22-stage interactive model**: why it is interactive and
staged, how the three phase groups fit together, how documents and decisions move through their lifecycle,
and the philosophy behind the gates. It is the orientation; the **authoritative, operational per-stage spec**
(inputs, activities, outputs, entry/exit criteria, validation, failure handling, human-intervention points,
and artifacts) lives in [`../plugins/keystone/references/workflow.md`](../plugins/keystone/references/workflow.md). This document
summarizes and links — it does not re-paste the operational spec.

> See also: [`methodology.md`](methodology.md) (rationale), [`../plugins/keystone/references/artifact-catalog.md`](../plugins/keystone/references/artifact-catalog.md)
> (what each stage produces), [`../plugins/keystone/references/quality-gates.md`](../plugins/keystone/references/quality-gates.md) (gate
> definitions), and [`../plugins/keystone/references/governance.md`](../plugins/keystone/references/governance.md) (statuses and IDs).

## Why interactive, not a single prompt

A project description is almost never complete, consistent, and unambiguous on first contact. It contains
gaps, hidden contradictions, unstated assumptions, and solution choices smuggled in as requirements. A
one-shot generator forced to produce a finished plan from that input has only one way to cope: it invents.
It guesses the missing requirement, silently resolves the contradiction, quietly picks a technology, and
presents the result as if it were grounded. The plan *looks* finished and is quietly wrong.

Keystone is interactive precisely to refuse that bargain. It pauses where an answer would change the plan and
asks a focused question; everywhere else it records an explicit assumption with its risk-if-wrong and
continues. It treats unresolved questions and rejected alternatives as first-class outputs rather than things
to bury. The human stays in the loop at the points that matter — confirming scope, approving key decisions,
approving the roadmap, authorizing repository creation, and giving the final go/no-go — and stays out of the
way everywhere else. The result is a plan whose every claim can be traced to a source, a decision, or an
acknowledged assumption.

## Why staged

The work is staged because the dependencies are real. You cannot sensibly compare technologies before you
know the requirements; you cannot lock scope while a blocking contradiction is unresolved; you cannot write a
trustworthy handoff before the package passes its quality gates. Each stage has explicit **entry and exit
criteria**, so the process advances only when the prerequisites genuinely hold. Staging also makes the
process *resumable* and *partial*: because state is persisted, work can stop after intake, resume from the
last completed stage, or re-run a single stage without redoing everything. The invocation modes (`full`,
`intake`, `plan`, `resume`, `stage:<id>`, `update`) are exactly these stop/start points; they change *where*
the workflow runs, never the methodology. See [`../plugins/keystone/references/modes.md`](../plugins/keystone/references/modes.md).

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
execute. Produce a gated phased roadmap and an actionable, testable work breakdown; generate the selected
artifact set and build the traceability matrix; optionally bootstrap a repository (dry-run by default);
validate against the quality gates; assemble the Claude-Code-targeted handoff package; run progress and decision
update cycles; and emit the final execution-readiness go/no-go.

## Document and decision lifecycle

Everything Keystone produces carries a status, so a reader always knows how much weight it bears.

**Documents and register rows** move through:
`Draft → Proposed → Approved → Implemented`, with side exits to `Rejected`, `Deferred` (which can return to
`Proposed`), and `Superseded → Obsolete`. Only **Approved** items constrain execution. *Draft* is being
written; *Proposed* is offered to the human and is the default for anything Keystone authored on its own
initiative; *Approved* has been accepted; *Rejected* is declined but kept with its reason; *Deferred* is
postponed with a trigger; *Superseded* points to its successor; *Implemented* is realized in the execution
repo; *Obsolete* is retained for history only.

**Decisions** use a deliberately narrow status set — exactly **Proposed, Approved, Rejected, Superseded,
Deferred**. A Proposed decision is never rendered as if Approved; that is a core safeguard, checked
mechanically. **Immutable-after-approval** artifacts (ADRs, approved acceptance criteria) are never edited in
meaning — they are superseded by a new item. **Derived** artifacts (the traceability matrix, the readiness
report, roadmap rollups) are regenerated from their sources, never hand-edited. Full status semantics,
identifiers, versioning, and supersession rules: [`../plugins/keystone/references/governance.md`](../plugins/keystone/references/governance.md).

## Gate philosophy: critical vs warn, loops as discipline

Gates are how Keystone decides whether it has earned the right to advance or to declare a package
execution-ready. They come in two severities. **Critical** gates block readiness — a package with a failing
critical gate is *not ready*, full stop, and the report says so rather than papering over it. **Warn** gates
surface issues that should be seen but do not block; a Warn gate may be passed by recording an accepted,
attributed exception. A package is execution-ready only when every Critical gate passes and every Warn gate
is passing or carries a recorded exception. The full gate list and severities are in
[`../plugins/keystone/references/quality-gates.md`](../plugins/keystone/references/quality-gates.md).

**Loops are discipline, not failure.** Clarification (stage 7), decision capture (stage 14), and validation
(stage 19) routinely send the process back upstream — a contradiction surfaces late, an experiment refutes a
hypothesis, a gate catches an unlinked requirement. Returning to an earlier stage is the system working as
intended, not a defect. The one rule is that the *reason* for looping is recorded (a note or a `DEC-`) so the
trail stays intact. **Do not skip a gate to look finished** — a plan that looks complete but hides an
unresolved contradiction or an unsourced requirement is exactly the failure mode Keystone exists to prevent.

## Human-intervention points

The human is asked to act at a small number of high-leverage gates, marked in the per-stage spec. In order,
they are: confirm the request scope/mode (stage 1) and the project profile (stage 2); answer the batched
clarification questions (stage 7, the primary clarification point); approve the locked scope (stage 8);
confirm research depth and experiment budgets for large efforts (stages 9, 13); approve key decisions (stage
14); confirm risk appetite (stage 15); approve the roadmap (stage 16); authorize actual repository
creation/push (stage 18); review non-critical warnings (stage 19); approve the handoff (stage 20); approve
material changes during update cycles (stage 21); and give the final go/no-go (stage 22). Keystone never
passes an approval gate on the user's behalf.

## Stage summary

A compact index of all 22 stages. **Per-stage operational detail (In · Do · Out · Enter · Exit · Validate ·
Fail · Human · Artifacts) is in [`../plugins/keystone/references/workflow.md`](../plugins/keystone/references/workflow.md)** — this table
does not replace it. Gate IDs reference [`../plugins/keystone/references/quality-gates.md`](../plugins/keystone/references/quality-gates.md);
✅ in the Gate column marks a human approval point.

### Phase A — Understand

| # | Name | Purpose | Key outputs | Gate |
|---|---|---|---|---|
| 1 | Intake | Capture raw input with provenance; attach to state | `keystone-state.json` seeded; archived input | Confirm request scope/mode ✅ |
| 2 | Initial classification | Classify project type, size, risk; pick a profile that biases selection + research depth | `project_profile` in state | Confirm/adjust profile ✅ |
| 3 | Requirement extraction | Extract candidate requirements **verbatim** with source spans; tag FR/NFR/CON/preference | Draft requirement candidates | Every requirement-bearing span extracted or marked out-of-scope |
| 4 | Requirement normalization | Assign IDs, dedupe, split compounds, classify, prioritize (MVP/Full) | Requirement registers (Draft) | G-REQ-SRC; unique IDs |
| 5 | Ambiguity detection | Find vague terms, undefined quantities, unclear actors, missing acceptance | Ambiguity list → candidate `OQ-` | Each ambiguity becomes `OQ-` or `ASM-` |
| 6 | Contradiction & dependency detection | Detect conflicts, hidden dependencies, premature solution decisions in the brief | Contradiction list, `DEP-`, flagged premature decisions | G-CONFLICT (no unresolved hard conflict past scope) |
| 7 | Clarification | Batch focused questions where the answer changes the plan; else record `ASM-` | Answered `OQ-`, new `ASM-`, updated requirements | **Primary clarification point** ✅ |
| 8 | Scope definition | Lock goals, non-goals, in/out-of-scope, success metrics; write the charter | `00-charter.md` (Proposed) | Approve scope ✅ |

### Phase B — Explore

| # | Name | Purpose | Key outputs | Gate |
|---|---|---|---|---|
| 9 | Research planning | Size research to genuine uncertainty; target the riskiest unknowns | Research plan, R&D backlog | Confirm depth for large efforts ✅; effort proportional to risk |
| 10 | Architecture exploration | Explore candidate architectures/components; name decision points; draft diagrams | Architecture draft + diagrams | Architecture covers all MVP requirements |
| 11 | Option comparison | Compare options on **explicit weighted criteria**; keep losers | Technology-comparison matrices | Criteria stated before scoring; claims cited or `unverified` |
| 12 | Hypothesis definition | State falsifiable hypotheses with confirm/refute signals | Hypothesis register (`HYP-`) | Each blocking unknown has a hypothesis or a decision |
| 13 | POC & experiment planning | Plan minimal experiments/POCs with PASS/FAIL + timebox | `EXP-`/`POC-` plans | Approve experiment budget for costly POCs ✅ |
| 14 | Decision capture | Record decisions with status, rationale, alternatives, consequences; promote to ADRs | Decisions + ADRs | G-DEC-STATUS; approve key decisions ✅; losers retained |
| 15 | Risk analysis | Enumerate + score risks; write mitigations; tag MVP/Full | Risk register (`RISK-`) | G-RISK; confirm risk appetite ✅ |

### Phase C — Plan & hand off

| # | Name | Purpose | Key outputs | Gate |
|---|---|---|---|---|
| 16 | Execution planning | Phased roadmap, work breakdown, milestones, DoR/DoD, checkpoints | `planning/`, `execution/` | G-EXEC (phases gated; leaf items actionable+testable); approve roadmap ✅ |
| 17 | Artifact generation | Generate the selected artifact set from templates; build the traceability matrix | The populated package | G-COMPLETE, G-TRACE, G-IDS (no stubs) |
| 18 | Repository initialization | Bootstrap the target repo (dry-run default; never overwrite without `--force`) | Initialized repo or dry-run report | Approve actual creation/push ✅; clean target or `--force` |
| 19 | Quality validation | Run all quality gates via the validators | Validation report | All **Critical** gates pass; review warnings ✅ |
| 20 | Execution-agent handoff | Assemble handoff; write initial + follow-up + review prompts; produce manifest | `handoff/` | G-HANDOFF (prompts reference real artifacts; Claude-Code-appropriate); approve handoff ✅ |
| 21 | Progress & decision update cycles | Record progress; update decision statuses; re-derive dependent artifacts; bump versions | `progress/`, updated registers | G-TRACE re-passes; approve material changes ✅ |
| 22 | Final readiness assessment | Run the readiness checklist; summarize gates, open items, residual risk; state go/no-go | `execution-readiness-report.md` | No Critical gate failing; final go/no-go ✅ |

## Where this document stops

This is orientation and philosophy. For exactly what each stage consumes and produces and how it validates,
read [`../plugins/keystone/references/workflow.md`](../plugins/keystone/references/workflow.md). For which artifacts a stage may emit and
their generation classes, read [`../plugins/keystone/references/artifact-catalog.md`](../plugins/keystone/references/artifact-catalog.md). For the gate definitions and
severities, read [`../plugins/keystone/references/quality-gates.md`](../plugins/keystone/references/quality-gates.md).
