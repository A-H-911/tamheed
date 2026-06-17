<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/logo-light.svg">
    <img src="docs/assets/logo.svg" alt="Keystone — the planning keystone that locks execution together" width="360">
  </picture>
</p>

<h1 align="center">Keystone</h1>

<p align="center"><strong>Turn a project description into a validated, traceable, execution-ready planning &amp; handoff package for another agent to implement.</strong></p>

<p align="center">
  <em>Reference design + working skill &middot; v0.1</em> &middot;
  <a href="#license">MIT</a> &middot;
  <a href="ROADMAP.md">Roadmap</a> &middot;
  <a href="skill/SKILL.md">Skill spec</a>
</p>

---

> **NOTE — this is an independent, reusable capability.** Keystone is vendor-, agent-, provider-, and
> stack-neutral, and carries no domain assumptions from any particular project — it is meant to be reused
> on any project. This repository is the home of the Keystone capability itself, not of any project
> Keystone happens to plan.

## What Keystone is

Keystone is a reusable agent **skill** that transforms a long-form project description into a complete,
internally consistent, **execution-ready handoff package**: the planning, research, architecture,
governance, and execution artifacts another agent (for example, a coding agent) needs to implement the
project with discipline. It is the generalized, reusable form of a
**project-inception → R&D-planning → architecture-governance → execution-handoff → repository-initialization**
methodology.

It does not write the project's code. It produces everything an implementing agent needs *before* code:
requirements separated from assumptions, options separated from decisions, a risk register, a phased
roadmap, testable acceptance criteria, a live traceability matrix, a bootstrapped repository, and the
kickoff prompts that hand the work over.

### One principle governs the whole design

> **The skill owns the capability; the slash command is a thin wrapper.**

Every entry point — the `/keystone` command, and any future CLI, API, MCP tool, or UI — only normalizes
input and routes output. None of them re-implement the methodology. All judgment, all 22 workflow stages,
all artifact selection, all quality gates, and all handoff logic live in the **`keystone` skill**. The
command literally contains no methodology (see [`commands/keystone.md`](commands/keystone.md) and the
entry-point contract in [`skill/references/extension.md`](skill/references/extension.md)).

## Capability overview

Given a brief, Keystone runs an **interactive** process (not a single prompt) across 22 stages grouped into
three movements:

- **Understand** — intake, classification, requirement extraction, normalization, ambiguity and
  contradiction detection, clarification, and scope locking.
- **Explore** — research planning, architecture exploration, weighted option comparison, hypotheses,
  POC/experiment planning, decision capture, and risk analysis.
- **Plan &amp; hand off** — execution planning, artifact generation, repository initialization, quality
  validation, execution-agent handoff, update cycles, and a final readiness assessment.

Along the way it produces (as applicable):

- A **project charter** and locked **scope** (goals, non-goals, success metrics).
- Registers for **requirements** (`FR-`/`NFR-`), **constraints** (`CON-`), **invariants** (`INV-`),
  **assumptions** (`ASM-`), **dependencies** (`DEP-`), **open questions** (`OQ-`), and
  **decisions** (`DEC-`).
- A **research plan**, **R&D backlog**, **hypotheses** (`HYP-`), and **experiment/POC** plans.
- **Architecture** documentation, diagrams, **technology comparison** matrices, and
  **Architecture Decision Records** (`ADR-`).
- A **risk register** (`RISK-`) with mitigations.
- A **phased roadmap** (`PH-`), **work breakdown** (`WBS-`), and **milestones** (`MS-`).
- **Acceptance criteria** (`AC-`) and a **test/validation strategy** (`TEST-`).
- A live **requirements → decisions → tasks → tests → risks** traceability matrix.
- The **handoff package**: an initial execution-agent prompt, follow-up prompts (one per phase gate),
  review prompts, a **repository bootstrap**, and a final **execution-readiness report**.

Identifiers, lifecycle statuses, versioning, and cross-reference rules are uniform across every artifact —
see [`skill/references/governance.md`](skill/references/governance.md). Statuses run
`Draft → Proposed → Approved / Rejected / Superseded / Deferred → Implemented`, and a *proposed* decision is
never rendered as *approved* — that separation is a core safeguard.

### Operating principles (what makes the output trustworthy)

1. **Never invent requirements** — every requirement traces to an input statement or a recorded
   clarification; anything inferred is an explicit assumption.
2. **Separate facts from decisions from proposals** — findings, proposed options, approved decisions,
   rejected alternatives, and deferred questions never silently collapse together.
3. **Surface assumptions; don't bury them.**
4. **No premature architecture** — capture options first, decide with rationale.
5. **Preserve the unresolved** — open questions and rejected alternatives are first-class outputs.
6. **Verify before you claim** — unverified tool/library/service claims are marked `unverified`.
7. **Executable over abstract; useful over ceremonial** — an artifact is generated only when it earns its
   keep.
8. **Stay neutral** — no coupling to one agent, vendor, repo provider, or stack unless the input requires it.

## How the skill is architected

Keystone is a **progressive-disclosure skill**. [`skill/SKILL.md`](skill/SKILL.md) is the always-loaded
entry point: it states the principle, the operating safeguards, the invocation modes, and a one-line map of
the 22 stages. The depth lives in `skill/references/*`, loaded only when the work reaches the matching part:

- `workflow.md` — the authoritative per-stage spec (inputs, activities, outputs, entry/exit criteria, gates).
- `intake.md`, `clarification.md`, `research-depth.md` — how to parse input, ask focused questions, and size
  research to genuine uncertainty.
- `artifact-rules.md`, `traceability.md`, `governance.md`, `quality-gates.md` — what to generate, how to keep
  it linked, how to name it, and how to validate it.
- `handoff.md`, `prompt-templates.md`, `repo-init.md` — assembling the handoff and bootstrapping a repo.
- `generated-structure.md`, `state.md`, `extension.md` — the output layout, resume/update state, and how to
  extend Keystone without editing core logic.

Forms and data shapes have single sources of truth: blank **templates** in `templates/` and machine-readable
**schemas** in `schemas/`. Deterministic, repeatable steps (repository init, package validation) are handled
by **scripts** (e.g. `scripts/init_skill_repo.py`, `tests/validate_package.py`) that the skill *invokes* —
the skill stays authoritative for judgment, the scripts stay authoritative for mechanics. See
[`IMPLEMENTATION-PLAN.md`](IMPLEMENTATION-PLAN.md) for why this hybrid is the chosen approach.

### `/keystone` is only a thin wrapper

The [`commands/keystone.md`](commands/keystone.md) command does exactly four things: gather input
(string or file/`@file`), validate **invocation syntax only**, normalize into the skill's input contract,
invoke the `keystone` skill, and route the skill's output (or its pending questions) back to the user. It
makes **no planning decisions** and contains **no methodology**. Any new entry point must obey the same
contract.

## Supported use cases

Reach for Keystone whenever you want to:

- **Plan, scope, or "inception" a new project** from a brief or a pasted spec.
- Run an **R&D, architecture, or design mission** and de-risk a large build *before* coding.
- Produce a **project charter** or an **execution plan / package**.
- **Compare technology options** against explicit, weighted criteria and record the verdict as an ADR.
- **Prepare a handoff** — a bootstrapped repo plus kickoff prompts — to hand work to a coding agent.
- **Resume or update** an existing planning package as decisions land and progress is made.

It triggers on phrases like *"plan this project"*, *"turn this idea into a plan"*, *"scope this out"*,
*"design before we build"*, *"prepare a handoff"*, *"kickoff prompt for another agent"*, *"project charter"*,
*"execution-ready package"*, or *"R&D plan"* — even if the word "Keystone" is never said.

## Installation

Keystone is distributed as an **agent skill** (with a thin slash command) that drops into any agent with
file read/write. The repository bootstrap script needs **Python 3.9+**; optional remote repo creation needs
`git` and the GitHub CLI (`gh`). No specific model, vendor, or repo provider is required.

**As a skill / plugin.** Place the `skill/` directory where your agent loads skills, and the `commands/`
entry point where it loads slash commands. For Claude Code:

```text
# project-scoped
<your-repo>/.claude/skills/keystone/      ← contents of this repo's skill/
<your-repo>/.claude/commands/keystone.md  ← this repo's commands/keystone.md

# or user-scoped (available across projects)
~/.claude/skills/keystone/
~/.claude/commands/keystone.md
```

The skill ships with its `references/`, and references `../templates/` and `../schemas/`. When you package
Keystone to run standalone, vendor those two directories in via the build step described in `ARCHITECTURE.md`.

**Invoke it.** Either run the slash command, or simply describe a planning task — the skill's description is
written to trigger on planning/scoping/handoff intent on its own.

## Usage

The skill drives the conversation: it confirms a mode, asks focused clarification questions only where the
answer changes the plan, pauses at approval gates, and then generates the package.

### Slash-command examples

```text
/keystone <project description | path/to/brief> [options]

Options:
  --mode <m>          full (default) | intake | plan | resume | update | stage:<id>
  --profile <type>    hint the project type (e.g. enterprise, rnd, legacy, ai-agentic)
  --package-dir <dir> where to write the generated package
  --no-repo           plan only; do not initialize a repository
  --owner <o>         repo owner/org (repo init)
  --visibility        private | public (repo init)
  --license <id>      SPDX id for the generated repo (e.g. MIT, Apache-2.0)
  --dry-run           show what would be created without writing a repository

Examples:
  /keystone @briefs/new-platform.md --mode full --profile enterprise
  /keystone "Build a CLI that syncs Notion to Markdown" --mode plan
  /keystone --mode resume --package-dir ./packages/new-platform
```

### Invocation modes

| Mode | What it does |
|---|---|
| `full` *(default)* | Run the whole workflow end to end (intake → handoff), pausing at clarification and approval gates. |
| `intake` | Intake + normalization + ambiguity/contradiction detection + a clarification plan, then stop. |
| `plan` (dry-run) | Produce the plan and artifact set without writing a repository. |
| `resume` | Reload an existing package's state and continue from the last completed stage. |
| `stage:<id>` | Run or re-run a single stage (e.g. `stage:risk-analysis`). |
| `update` | Apply new decisions/progress to an existing package and refresh derived artifacts. |

### Example input

A short brief is enough to start; Keystone records gaps as open questions and fills them through interaction.

```text
Build a CLI that keeps a folder of Markdown notes in sync with a Notion workspace.
Two-way sync, conflict detection, runs on macOS and Linux, offline-friendly. Solo
maintainer, open-source, must be easy to install. Not sure yet whether to use the
official Notion API or a community library, and how to handle rate limits.
```

### Example output

From that brief, `--mode full` would produce a package whose shape is defined in
[`skill/references/generated-structure.md`](skill/references/generated-structure.md) — a charter, the
requirement/decision registers (with the API-vs-library choice captured as an **open decision** and an ADR
once resolved), a risk register, a phased roadmap, acceptance criteria, a traceability matrix, a
bootstrapped repo, and the handoff `initial-prompt.md`. Worked, end-to-end examples live in:

- [`examples/`](examples/) — input briefs paired with the expected package outline.
- [`generated-samples/`](generated-samples/) — full generated packages for demonstration (the *only* place
  generated output lives inside this source tree).

## Repository structure

```text
keystone/
├── README.md                     # this file
├── IMPLEMENTATION-PLAN.md        # how Keystone is built (approach comparison + recommendation)
├── ACCEPTANCE-CRITERIA.md        # acceptance criteria for the Keystone capability itself
├── ROADMAP.md                    # phased implementation roadmap
├── NAMING-OPTIONS.md             # naming analysis + the decision to use "Keystone"
├── LICENSE                       # MIT
├── CONTRIBUTING.md               # contribution guidance (added during the docs phase)
├── METHODOLOGY.md                # human-facing methodology rationale
├── WORKFLOW.md                   # human-facing walkthrough of the 22 stages
├── ARTIFACT-CATALOG.md           # every artifact type, its trigger, and its template
├── ARCHITECTURE.md               # how the skill, scripts, templates, and schemas fit together
├── skill/
│   ├── SKILL.md                  # always-loaded skill entry point (owns the capability)
│   └── references/               # per-stage and per-concern depth, loaded on demand
│       ├── workflow.md  modes.md  intake.md  clarification.md  research-depth.md
│       ├── artifact-rules.md  traceability.md  governance.md  quality-gates.md
│       ├── safeguards.md  handoff.md  prompt-templates.md  repo-init.md
│       └── generated-structure.md  state.md  extension.md
├── commands/
│   └── keystone.md               # the thin /keystone wrapper (no methodology)
├── templates/                    # blank artifact forms (single source of truth)
├── schemas/                      # machine-readable JSON schemas (input, state, handoff, registers)
├── scripts/
│   └── init_skill_repo.py        # deterministic repository bootstrap (dry-run-capable, idempotent)
├── tests/
│   └── validate_package.py       # validator: checks identifiers, traceability, and quality gates
├── examples/                     # input briefs + expected package outlines
├── generated-samples/            # full demonstration packages (only generated output in-tree)
└── docs/
    └── assets/                   # logo.svg, logo-light.svg, logo-dark.svg, icon.svg
```

## Development

1. **Clone** the repository.
2. Install **Python 3.9+** (the only hard dependency, for the bootstrap and validator scripts). For optional
   remote repo creation, install `git` and the GitHub CLI (`gh`).
3. **Edit where the capability lives.** Methodology and judgment go in `skill/SKILL.md` and
   `skill/references/*`; never add logic to `commands/keystone.md`.
4. **Extend additively.** Add artifact types, templates, schemas, quality gates, project-type profiles,
   diagram kinds, and entry points via the registries documented in
   [`skill/references/extension.md`](skill/references/extension.md) — register a new entry and drop in a
   file; do not fork the workflow.
5. **Keep the sources of truth singular.** Forms live in `templates/`; data shapes live in `schemas/`. Keep
   the script behavior and the schemas in sync.

## Testing

A generated package is validated by the bundled validator, which checks identifier conventions, link
integrity, the traceability matrix, and the quality gates:

```bash
python tests/validate_package.py <path-to-generated-package>
```

It reports each gate as pass/fail and exits non-zero if a critical gate fails. The `scripts/init_skill_repo.py`
bootstrap is `--dry-run`-capable and idempotent, so it can be exercised safely in CI without writing a repo.

## Contributing

Contributions are welcome — new artifact types, templates, schemas, gates, profiles, and worked examples are
the highest-value additions, and they are designed to be **additive**. Please follow the entry-point and
extension contracts so the principle *"the skill owns the capability"* stays intact. See
[`CONTRIBUTING.md`](CONTRIBUTING.md) (added during the documentation phase) for the workflow and review
expectations.

## Roadmap

The phased plan — from methodology extraction through skill architecture, artifacts, templates, schemas, the
slash-command wrapper, the repository generator, branding, the validation framework, tests, examples,
documentation, packaging, versioning, release, and continuous evolution — is in
[`ROADMAP.md`](ROADMAP.md). Acceptance criteria for the capability itself are in
[`ACCEPTANCE-CRITERIA.md`](ACCEPTANCE-CRITERIA.md).

## Maturity

**Reference design + working skill — v0.1.** The methodology, skill specification, governance model, and
generated-package structure are defined and usable; templates, schemas, scripts, the validator, worked
examples, and packaging are being filled in along the roadmap. Schemas, identifiers, and the handoff
contract may still change before v1.0; such changes ship with a migration note per the versioning rules in
[`skill/references/governance.md`](skill/references/governance.md).

## License

Released under the **MIT License** (configurable for downstream use) — see [`LICENSE`](LICENSE). The license
for any *generated* repository is independent and selectable at generation time via `--license`.
