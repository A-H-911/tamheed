# Keystone Methodology

This document is the human-facing rationale for *what* Keystone does and *why*. It generalizes a single,
concrete inception → R&D → architecture-governance → execution-handoff effort into a reusable, vendor-neutral
methodology. The operational "how" lives in the skill's references; this file summarizes and links to them so
the two never drift apart or duplicate each other.

> **Reading map.** For the staged process see [`workflow.md`](workflow.md) and the authoritative per-stage
> spec [`../plugins/keystone/references/workflow.md`](../plugins/keystone/references/workflow.md). For every artifact's class, location,
> and lifecycle see [`../plugins/keystone/references/artifact-catalog.md`](../plugins/keystone/references/artifact-catalog.md). For the skill/command layering see
> [`architecture.md`](architecture.md). For identifiers, statuses, and versioning see
> [`../plugins/keystone/references/governance.md`](../plugins/keystone/references/governance.md).

## 1. What the methodology is

Keystone is a repeatable way to turn a *project description* into a *validated, traceable, execution-ready
planning and handoff package* that **another agent** can pick up and implement with discipline. It is not a
code generator and not a project tracker. It is the disciplined front half of a project: understand the
problem, resolve the unknowns that block decisions, govern the significant choices, plan the work, and hand
it off cleanly — leaving an auditable trail from every need to its evidence.

The methodology rests on one governing principle and a set of operating principles that make its output
trustworthy. The governing principle is architectural: **the skill owns the capability; entry points are thin
wrappers.** The operating principles are epistemic: never invent requirements; separate facts from decisions
from proposals; surface assumptions instead of burying them; no premature architecture; preserve the
unresolved; verify before you claim; and prefer operationally useful artifacts over ceremonial ones. The
full, enforced list is in [`../plugins/keystone/SKILL.md`](../plugins/keystone/SKILL.md) (operating principles) and
[`../plugins/keystone/references/safeguards.md`](../plugins/keystone/references/safeguards.md) (each anti-pattern paired with its
control).

### Neutrality

This methodology captures patterns that recur across disciplined research-and-design and execution-handoff
work, deliberately stripped of everything project-, vendor-, and stack-specific. **Keystone is
project-neutral.** It is not tied to any particular project, repository provider, or technology stack.
Where this document needs an example, the example is anonymized and generic (e.g. "a CLI that syncs notes to
Markdown," "an enterprise data platform").

## 2. The separations the methodology enforces

Most of Keystone's value is in keeping things that look similar from collapsing into each other. Three
separations matter most.

### 2.1 Project-specific content vs reusable methodology

| Project-specific (lives in a *generated package*) | Reusable methodology (lives in the *Keystone source*) |
|---|---|
| The actual requirements, constraints, invariants, risks of one project | The registers and identifier scheme those facts are recorded in |
| The chosen architecture and technology decisions | The decision-capture process and ADR format |
| The phased roadmap and work breakdown for this build | The planning technique that produces gated, testable phases |
| The handoff prompts for this specific executor | The Claude-Code-targeted prompt templates they are written from |
| The repository that gets bootstrapped | The dry-run-capable, idempotent bootstrap mechanism |

The rule of thumb: **a decision belongs in a package; the way decisions are made belongs in the skill.** A
technology choice, a scope boundary, or a risk score is never baked into Keystone — those are outputs.
Stack-agnosticism is a safeguard, not a preference (safeguard 15).

### 2.2 Mandatory vs optional vs context-dependent artifacts

Keystone generates **by need, not ceremony**. Every artifact carries a *generation class* that says when it
is produced. The classes are: **Always** (every package), **Conditional** (a trigger such as project
profile, size, risk, or regulatory context holds), **On-request** (only when asked), **Continuous** (created
early, refreshed each update cycle), and **Derived** (computed from other artifacts, never hand-authored).
The selection logic is in [`../plugins/keystone/references/artifact-rules.md`](../plugins/keystone/references/artifact-rules.md); the
full per-artifact mapping is in [`../plugins/keystone/references/artifact-catalog.md`](../plugins/keystone/references/artifact-catalog.md). The anti-bloat rule is
explicit: if an artifact would only restate another, derive or link instead; if a section has no
project-specific content, omit it rather than emit a placeholder (safeguard 11).

### 2.3 Execution-agent instructions vs skill-implementation concerns vs entry-point concerns

These three audiences are routinely confused, so Keystone keeps them in separate places:

| Concern | Audience | Where it lives | Must NOT contain |
|---|---|---|---|
| **Execution-agent instructions** | Claude Code (the downstream executor) | the generated package's `handoff/` prompts + the artifacts they reference | Keystone's internal process; planner-only context |
| **Skill-implementation concerns** | Keystone itself (the methodology author/runtime) | `../plugins/keystone/SKILL.md` + `../plugins/keystone/references/` | a specific project's content; entry-point parsing |
| **Slash-command / entry-point concerns** | the wrapper that launches Keystone (`/keystone`, a CLI, an API, an MCP tool, a UI) | external entry points (CLI/API/MCP/UI) | any methodology or planning logic (safeguard 12) |

The handoff prompts are written for **Claude Code** as the executor, using its native affordances where they
help (safeguard 13); the *plan's* technology choices stay vendor-neutral (safeguard 15). The entry point only normalizes input, picks a mode,
invokes the skill, and routes output — it makes no planning decisions. See
[`../plugins/keystone/references/handoff.md`](../plugins/keystone/references/handoff.md) and
[`../plugins/keystone/references/extension.md`](../plugins/keystone/references/extension.md).

## 3. The extracted patterns

The methodology is a small set of patterns that recur across serious projects, made explicit and repeatable.

**Verbatim-then-normalize.** Requirements are first extracted *verbatim* with source spans, then normalized
into identified register rows. Meaning is never paraphrased away during extraction; classification (
functional / non-functional / constraint / preference) and prioritization (MVP / Full) happen afterward.
This is what makes "never invent a requirement" enforceable: every `FR-`/`NFR-` traces to a source span or a
recorded clarification.

**Register-per-entity-family.** Each kind of fact gets its own register with its own identifier prefix:
requirements, constraints, invariants, assumptions, dependencies, open questions, open decisions, risks,
hypotheses. Keeping them apart is what prevents a research finding from silently becoming a decision, or a
proposal from being read as approved.

**Status-bearing everything.** Every register row and standalone document carries a lifecycle status, so a
reader always knows whether something is offered, accepted, declined, postponed, or replaced. Decisions in
particular are never rendered as approved until a human approves them.

**Decide-with-evidence, keep-the-losers.** Options are compared against *explicit, weighted criteria* stated
before scoring; the front-runner becomes a decision with rationale, alternatives, and consequences; rejected
options stay on record as evidence. Significant, hard-to-reverse choices are promoted to ADRs.

**Uncertainty-proportional R&D.** Research and experimentation are sized to *genuine* uncertainty, not to a
fixed template. A blocking unknown gets a falsifiable hypothesis and a minimal experiment or POC with
explicit PASS/FAIL criteria and a timebox; a well-understood area gets none.

**Gated, testable planning.** The plan is a phased roadmap where each phase has a goal, scope, deliverables,
a validation method, its risks, and explicit exit criteria; the work breakdown decomposes until leaf items
are independently actionable and testable. Abstract phases are decomposed, not shipped.

**End-to-end traceability.** A single matrix links requirement → decision → task → test → risk → acceptance
criterion, so an implementer can navigate from any need to its evidence and back. Unlinked MVP requirements
are a gate failure, not a silent omission. See [`../plugins/keystone/references/traceability.md`](../plugins/keystone/references/traceability.md).

**Clean handoff with bounded first step.** The executor receives a self-contained orientation, the
invariants up front, and *one* bounded first task that ends at an approval gate — never "build the whole
thing." Prompts reference artifacts rather than restating them, keeping the package the single source of
truth.

**Safe repository bootstrap.** Repository initialization is dry-run-capable, idempotent, and never overwrites
without an explicit `--force`; it refuses a dirty target unless told otherwise, and remote creation is an
optional, provider-neutral step.

## 4. Workflows

Keystone runs as an **interactive, staged process — not a single prompt.** The 22 stages are grouped into
three phases: **Understand** (intake, classification, requirement extraction and normalization, ambiguity and
contradiction detection, clarification, scope), **Explore** (research planning, architecture exploration,
option comparison, hypotheses, POC/experiment planning, decision capture, risk analysis), and **Plan & hand
off** (execution planning, artifact generation, repository initialization, quality validation, handoff,
update cycles, final readiness). Each stage has entry/exit criteria, validation, failure handling, and marked
human-intervention points. Returning to an earlier stage is normal discipline, not failure — but the reason
is recorded so the trail stays intact.

The methodology supports several **invocation modes** that change only where the workflow starts and stops,
never the methodology itself: `full` (end to end), `intake` (understand + surface gaps), `plan` (full plan,
no repository), `resume`, `stage:<id>`, and `update`. See
[`../plugins/keystone/references/modes.md`](../plugins/keystone/references/modes.md). State is persisted to `keystone-state.json` so work
can resume and update without re-asking; see [`../plugins/keystone/references/state.md`](../plugins/keystone/references/state.md).

The why-it-is-interactive argument and the compact stage table are in [`workflow.md`](workflow.md); the
authoritative per-stage spec is [`../plugins/keystone/references/workflow.md`](../plugins/keystone/references/workflow.md). This document
does not repeat either.

## 5. Decision processes

Decisions are first-class and tracked through an explicit, narrow status set: **Proposed, Approved, Rejected,
Superseded, Deferred** (decision statuses are exactly these — never more). Anything Keystone authors on its
own initiative defaults to *Proposed* and may not be rendered as *Approved* until a human or an authorized
gate accepts it. Only Approved items constrain execution.

Two tiers exist. A lightweight decision (`DEC-`) lives in the open-decision register. When a decision is
*architecturally significant* — hard to reverse, with a broad blast radius — it is **promoted** to an
Architecture Decision Record (`ADR-NNNN`), and the promotion link (`DEC-007 → ADR-0003`) is recorded so it is
never lost. ADRs are immutable after approval: to change one, supersede it with a new ADR rather than editing
its meaning. The decision-capture activity (stage 14) records status, rationale, alternatives, and
consequences, and refuses to record a decision with no rationale. Full identifier, status, and supersession
rules: [`../plugins/keystone/references/governance.md`](../plugins/keystone/references/governance.md).

## 6. Validation steps

Validation is gate-based. Gates verify the package is complete, consistent, traceable, and executable before
handoff. **Critical** gates block readiness; **Warn** gates surface issues without blocking. A package is
*execution-ready* only when every Critical gate passes and every Warn gate is passing or carries a recorded,
accepted exception. The gate set (e.g. requirement-has-source, identifier integrity, decision-has-status,
full traceability, completeness/no-stubs, no unresolved hard contradiction, executable plan, clean
Claude-Code-targeted handoff, no silently-unanswered blocking question) is defined in
[`../plugins/keystone/references/quality-gates.md`](../plugins/keystone/references/quality-gates.md). Mechanical gates are checked by a
validator; judgment gates are performed and recorded with evidence. The gate philosophy — critical vs warn,
and loops as discipline rather than failure — is explained in [`workflow.md`](workflow.md). Keystone never
reports "ready" while a Critical gate fails.

## 7. Planning techniques

Planning produces a **phased roadmap** (`PH-`) where each phase carries goal, scope, deliverables, validation
method, risks, and exit criteria; a **work breakdown** (`WBS-`) decomposed until leaf items are independently
actionable and testable; **milestones** (`MS-`); and the execution scaffolding — backlog, **Definition of
Ready**, **Definition of Done**, and in-flight **checkpoints** (review/approval gates). The MVP path is
sequenced explicitly and gated, so the executor always knows the minimal coherent deliverable and where each
phase ends. Abstract phases are decomposed before the plan is accepted (safeguard 10 / gate G-EXEC).

## 8. Architecture-governance mechanisms

Architecture is explored *before* it is locked. Candidate architectures and components are drafted, decision
points are named, and diagrams (context, component, deployment, data-flow, integration) are produced *only
where a diagram adds understanding a paragraph cannot*. Options at each decision point are compared on
explicit weighted criteria with cited or `unverified`-tagged claims. The recommended architecture must cover
every MVP requirement; a requirement no architecture satisfies raises a risk and an open question rather than
being quietly dropped. Significant choices become ADRs. **No premature architecture** is a hard rule: no
technology or design is Approved while its deciding open question is open and no covering assumption exists
(safeguard 3). The recommended architecture, component model, contracts, and comparison verdicts are recorded
in the package's `architecture/` directory and governed by the same status and versioning rules as everything
else.

## 9. R&D practices

Research is planned in proportion to risk ([`../plugins/keystone/references/research-depth.md`](../plugins/keystone/references/research-depth.md)),
targeting the riskiest unknowns first and timeboxing to avoid unbounded investigation. The chain is
deliberate: an unknown that blocks a decision becomes a **falsifiable hypothesis** (`HYP-`) with the signal
that would confirm or refute it; that hypothesis gets a **minimal experiment or POC** (`EXP-`/`POC-`) with
explicit PASS/FAIL criteria and a timebox; the result feeds **decision capture**. Findings live in
`research/` and never silently become decisions — a finding becomes a decision only through an explicit
decision row (safeguard 6). An evaluation/comparison framework with weighted criteria governs how options and
experiment outcomes are judged.

## 10. Execution-agent handoff mechanisms

The handoff package is the contract between planner and executor. It contains an **initial prompt**
(self-contained orientation + invariants up front + one bounded first task ending at an approval gate),
**follow-up prompts** (one per phase gate, plus situational prompts such as fresh-session refresher,
invariant audit, and deviation-ADR), **review prompts** (audit against invariants, re-run readiness, review a
PR), a **handoff manifest** (artifacts, versions, entry points, invariants, MVP definition, prerequisites),
and the **execution-readiness report**. The principles — Claude-Code-targeted, reference don't restate, bounded
steps with gates, invariants and prerequisites explicit — are in
[`../plugins/keystone/references/handoff.md`](../plugins/keystone/references/handoff.md), with prompt forms in
[`../plugins/keystone/references/prompt-templates.md`](../plugins/keystone/references/prompt-templates.md). The handoff is what lets
**Claude Code**, with no access to the planning conversation, start implementing with no missing context.

## 11. Repository-initialization practices

When a target repository is wanted, Keystone bootstraps a usable initial repo: folder skeleton, baseline
files, README and logo, license, ADR and documentation directories, changelog, version, an initial commit,
and an optional remote with push. The bootstrap is **dry-run by default**, **idempotent**, and **never
overwrites without `--force`**; it refuses a dirty target unless explicitly told otherwise (safeguard 16).
Repository logic is provider-neutral — local git always, remote creation an optional and swappable step
(safeguard 14). Operational detail: [`../plugins/keystone/references/repo-init.md`](../plugins/keystone/references/repo-init.md).

## 12. Extraction traceability

Each reusable Keystone mechanism generalizes a concrete practice that recurs in disciplined R&D → handoff
work. The table below maps the practice (in generic phrasing) to the mechanism it becomes — the right column
is what ships; the left column is the recurring practice it generalizes.

| Observed practice (generic phrasing) | Generalized Keystone mechanism |
|---|---|
| A design mission that resolved numbered open decisions before any building began | Stage-gated workflow with an explicit **open-decision register** (`DEC-`) and a scope-lock gate; nothing is built while a blocking question is open |
| Numbered open *questions* tracked separately from decisions and answers | **Open-question register** (`OQ-`) distinct from decisions, surfaced in the readiness report and never silently closed |
| Recording "we are assuming X because the answer isn't available yet" | **Assumption register** (`ASM-`) with `risk_if_wrong`; the control for proceeding without an answer (safeguard 2) |
| ADRs written for the significant, hard-to-reverse choices | **ADR mechanism** (`ADR-NNNN`), immutable-after-approval, with `DEC-`→ADR promotion recorded |
| Comparing tools/approaches in a weighted table before choosing | **Technology-comparison matrices** with explicit weighted criteria stated before scoring; losers retained |
| Spiking risky unknowns with small throwaway experiments | **Hypothesis → experiment/POC** chain (`HYP-`/`EXP-`/`POC-`) with PASS/FAIL + timebox, sized to genuine uncertainty |
| A phased plan where each phase had to "finish" before the next | **Phased roadmap** (`PH-`) with per-phase exit criteria + gated **work breakdown** (`WBS-`) |
| A risk list with impact, likelihood, and what we'd do about it | **Risk register** (`RISK-`) with impact·likelihood scoring, mitigations, triggers, and MVP/Full tagging |
| A spreadsheet linking requirements to where they were satisfied and tested | **Traceability matrix** (derived): requirement → decision → task → test → risk → acceptance criterion |
| A handoff folder with kickoff prompts for the implementing agent | **Handoff package** with initial / follow-up / review prompts, Claude-Code-targeted, referencing real artifacts |
| A script that set up the repo skeleton, license, and first commit | **Repository bootstrap** (`init_skill_repo.py`): dry-run-capable, idempotent, never-overwrite, provider-neutral remote |
| "Definition of done" agreed up front so quality wasn't argued later | **Definition of Ready / Definition of Done** + checkpoints in `execution/` |
| A final "are we actually ready to build?" review | **Execution-readiness report** gated on all Critical quality gates (stage 22) |
| The capability invoked the same way regardless of who triggered it | **Skill-owns-capability** principle: thin entry points normalize input and invoke the one skill (safeguard 12) |

## 13. Where this document stops

This file is rationale and generalization. It intentionally does **not** restate the per-stage operational
spec, the full identifier tables, the gate definitions, or the artifact catalog rows — those are single
sources of truth elsewhere, linked above. When the methodology evolves, the additive extension contract in
[`../plugins/keystone/references/extension.md`](../plugins/keystone/references/extension.md) governs how new artifact types, templates,
schemas, gates, profiles, diagram kinds, and entry points are added without editing core logic.
