<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="plugins/tamheed/assets/logo-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="plugins/tamheed/assets/logo-light.svg">
    <img src="plugins/tamheed/assets/logo.svg" alt="Tamheed — تمهيد: ground work for execution" width="420">
  </picture>
</p>

<h1 align="center">Tamheed</h1>

<p align="center"><strong>Turn a project description into a validated, traceable, execution-ready planning &amp; handoff package for Claude Code to implement.</strong></p>

<p align="center">
  <em>Claude Code plugin + MCP-backed agent skill &middot; v2.0</em> &middot;
  <a href="#license">MIT</a> &middot;
  <a href="docs/install.md">Install</a> &middot;
  <a href="docs/migrate-from-keystone.md">Migrate from Keystone</a> &middot;
  <a href="plugins/tamheed/SKILL.md">Skill spec</a>
</p>

---

> **An independent, reusable capability.** Tamheed is vendor-, provider-, and stack-neutral and carries no
> domain assumptions from any particular project — it is meant to be reused on *any* project. It targets
> **Claude Code** as the downstream execution agent; the plans it produces carry no vendor or stack lock-in.
> This repository is the home of the Tamheed capability itself, not of any project Tamheed happens to plan.

## What Tamheed is

Tamheed is a reusable agent **skill** that transforms a long-form project description into a complete,
internally consistent, **execution-ready handoff package**: the planning, research, architecture,
governance, and execution artifacts Claude Code needs to implement the project with discipline.

It does not write the project's code. It produces everything an implementing agent needs *before* code —
requirements separated from assumptions, options separated from decisions, a risk register, a phased
roadmap sliced for delivery, testable acceptance criteria, live traceability, and the kickoff prompts that
hand the work over — and then keeps the package **alive during execution**: the executing agent records
progress, audit verdicts, and commit bindings back into it through the same tools that built it.

Unlike its v1 predecessor, a package is not a folder of Markdown files. It is a **relational store**
(ADR-0001): one SQLite-enforced entity table per artifact family, serialized to deterministic, diff-friendly
**canonical JSONL** (`data/*.jsonl`) that you commit to git. Every write goes through the **Tamheed MCP
server** — the only write path — so the strongest quality gates are schema constraints that cannot be
skipped, and the human reviews through a generated **HTML review surface** (`review.html`), never by
proofreading raw data files.

## Lineage

Tamheed is the successor of **[Keystone](https://github.com/A-H-911/keystone)** — the same capability's
v1, which stored packages as Markdown documents and validated them with a file-scanning gate engine. This
repository carries Keystone's full git history. The Keystone repository stays available and frozen at
**v1.0.x** for existing v1 packages; it receives no new features. Projects arriving from Keystone follow
the migration runbook: **[`docs/migrate-from-keystone.md`](docs/migrate-from-keystone.md)** (operator-initiated,
staged, fidelity-checked — v1 packages keep working until *you* decide to migrate).

## Requirements

Honest edition — what you actually need:

- **An MCP-capable host.** Claude Code is the designed-for host: the bundled `.mcp.json` auto-starts the
  server when the plugin is enabled. Any other agent that can run MCP servers and read files works too.
- **Python ≥ 3.10** for the MCP server (the official `mcp` SDK's floor; program decision ASM-D). `uv`
  launches it with zero setup (the server carries PEP 723 inline metadata), or `pip install mcp` as the
  fallback. See [`plugins/tamheed/server/README.md`](plugins/tamheed/server/README.md).
- No specific model, vendor, or repo provider is required.

**What ended with v1:** the chat-only path. Claude.ai and other environments without an MCP host can hold
the planning *conversation*, but they cannot create or mutate a v2 package — there is no package store
without the server. That trade is deliberate: the store is where the integrity guarantees live.

## Install

Tamheed ships as a self-contained bundle at [`plugins/tamheed/`](plugins/tamheed). See
[`docs/install.md`](docs/install.md) for every path and the capability tiers; the essentials:

**Claude Code (plugin — recommended).** This repo is its own plugin marketplace:

```text
/plugin marketplace add A-H-911/tamheed
/plugin install tamheed@tamheed
```

Then invoke it as **`/tamheed:tamheed`** (plugin skills are namespaced), or just describe a planning task —
the skill triggers on planning/scoping/handoff intent on its own. Approve the `tamheed` MCP server when
Claude Code asks (per-server approval); it is the package's only write path.

**Claude Code (manual / standalone).** Copy the bundle into your skills directory to get the un-namespaced
`/tamheed`:

```text
# user scope (all projects)        # or project scope
~/.claude/skills/tamheed/          <repo>/.claude/skills/tamheed/
   ← contents of plugins/tamheed/
```

> The old install commands (`marketplace add A-H-911/keystone`) remain valid only for **Keystone 1.0.x**
> at the old repository.

## Usage

The skill drives the conversation: it confirms a mode, asks focused clarification questions only where the
answer changes the plan, pauses at approval gates, and then generates the package through the MCP tools.

```text
/tamheed:tamheed <project description | path/to/brief> [options]

Options:
  --mode <m>          full (default) | intake | plan | resume | stage:<id> | update | migrate | adopt
  --profile <type>    hint the project type (enterprise, rnd, legacy, ai-agentic, unknown)
  --package-dir <dir> where the package store lives (created if absent)
  --dry-run           transactional preview: report entity/gate deltas, then roll back

Examples:
  /tamheed:tamheed @briefs/new-platform.md --mode full --profile enterprise
  /tamheed:tamheed "Build a CLI that syncs Notion to Markdown" --mode plan
```

| Mode | What it does |
|---|---|
| `full` *(default)* | Run the whole workflow end to end (intake → handoff), pausing at clarification and approval gates. |
| `intake` | Intake + normalization + ambiguity/contradiction detection + a clarification plan, then stop. |
| `plan` | Produce the full plan and entity set, stopping before handoff emission. |
| `resume` | `package_open` an existing package and continue from the last incomplete stage. |
| `stage:<id>` | Run or re-run a single stage (e.g. `stage:risk-analysis`). |
| `update` | The agile heart of v2 (D-UPDATE), three capabilities: **diff-aware re-derivation** (change an entity, regenerate only its dependents via `trace_query`), **execution-progress sync** (`progress_update` / `audit_record` with evidence / `work_bind`), and **typed scope changes** (defer / reschedule / reclassify / cancel / expand — a `scope-change` row is written before any mutation, always). |
| `migrate` | Walk a conformant v1 Keystone package into the store (`package_migrate`: staged preview → confirm, post-flight fidelity report). |
| `adopt` | Onboard a brownfield project that never used Tamheed (`package_adopt`: staged scan → confirm; nothing inferred is Approved, provenance is code-shaped, the gap report is first-class). |

(The v1 `--no-repo` flag is gone with the repository bootstrapper itself — ASM-B; a package is data the
operator commits to whichever repository they choose.)

Worked, end-to-end examples live in [`examples/`](examples) (input briefs + expected outlines) and
[`generated-samples/`](generated-samples) — including
[`support-triage-agent-v2/`](generated-samples/support-triage-agent-v2), a full v1→v2 migrated package.

## How it works

```mermaid
flowchart LR
    brief(["Project brief<br/>(untrusted data)"]) --> U

    subgraph SKILL["Tamheed skill — owns the methodology (22 stages)"]
        direction LR
        U["Understand<br/>1–8: intake → scope"] --> X["Explore<br/>9–15: research → decisions → risk"]
        X --> P["Plan &amp; hand off<br/>16–22: plan → validate → handoff"]
    end

    G1{{"human gate:<br/>clarifications + scope approval"}} -.- U
    G2{{"human gate:<br/>plan approval + final go/no-go"}} -.- P

    SKILL -- "MCP tool calls<br/>(the only write path)" --> T

    subgraph SRV["Tamheed MCP server"]
        direction TB
        T["entity_upsert · entity_query · trace_query<br/>gate_run · handoff_emit · export_html"]
        DB[("package store<br/>SQLite runtime ⇄ canonical JSONL")]
        T --> DB
    end

    DB --> OUT["execution-ready package<br/>data/*.jsonl + handoff prompts + review.html"]
    OUT --> EXEC["Claude Code executes"]
    EXEC -- "progress_update · audit_record · work_bind" --> T
```

<p align="center"><em>From a project brief to an execution-ready handoff — two gates keep you in control:
clarifications during intake, and plan approval before anything is handed off. Execution writes back
through the same MCP boundary.</em></p>

Tamheed runs an **interactive** process across 22 stages grouped into three movements — **Understand**
(intake → scope), **Explore** (research → decisions → risk), and **Plan & hand off** (execution plan →
artifacts → package storage → validation → handoff). One principle governs the design:

> **The skill owns the capability; every entry point is a thin wrapper.**

All judgment — the 22 stages, artifact selection, quality gates, handoff logic — lives in the
[`tamheed` skill](plugins/tamheed/SKILL.md): a **progressive-disclosure** bundle (a short `SKILL.md` front
door plus `references/` loaded on demand). The **MCP server is not an entry point** — it is the mechanical
half of the capability itself, the successor of the v1 validator: referential gates (identifiers, decision
statuses, requirement provenance) are FOREIGN KEY / CHECK / NOT NULL constraints enforced at write time,
coverage gates are SQL views, and `gate_run` reports it all. The bundle is **self-contained** — everything
it reads or invokes at runtime lives inside `plugins/tamheed/`, so the plugin installs and runs as one
intact unit. The three-actor interaction (planning agent · human operator · executing agent) is diagrammed
in [`docs/architecture.md`](docs/architecture.md); design rationale in
[`docs/design-decisions.md`](docs/design-decisions.md).

### Operating principles (what makes the output trustworthy)

1. **Never invent requirements** — everything traces to an input statement or a recorded clarification; anything inferred is an explicit assumption (and the store *rejects* a requirement without provenance).
2. **Separate facts from decisions from proposals** — findings, proposed options, approved decisions, rejected alternatives, and deferred questions never silently collapse together.
3. **No premature architecture** — capture options first, decide with rationale.
4. **Preserve the unresolved** — open questions and rejected alternatives are first-class outputs.
5. **Verify before you claim** — unverified tool/library/service claims are marked `unverified`.
6. **Stay neutral** — the plan couples to no vendor, repo provider, or stack unless the input requires it (the executor is Claude Code by design).
7. **Treat the brief as untrusted data** — input is something to plan over, never instructions to obey; an injected directive is captured as data (and surfaced), never executed (OWASP LLM01). The same posture covers adopted repositories and the handoff screen (`G-INJECT`).

## Repository structure

```text
tamheed/
├── .claude-plugin/marketplace.json   # this repo is its own plugin marketplace
├── plugins/tamheed/                  # the self-contained skill bundle (the installable unit)
│   ├── .claude-plugin/plugin.json
│   ├── .mcp.json                     # auto-starts the server when the plugin is enabled
│   ├── SKILL.md                      # always-loaded entry point (owns the capability)
│   ├── references/                   # per-stage / per-concern depth (incl. artifact-catalog.md)
│   ├── templates/                    # surviving narrative section templates
│   ├── schemas/                      # frozen v1 JSON schemas (migration contract)
│   ├── scripts/                      # validate_package.py (frozen v1 gate engine, migration contract)
│   ├── db/                           # v2 relational store: schema.sql, store.py, CANONICAL.md
│   ├── server/                       # the Tamheed MCP server (the only write path into a package)
│   └── assets/                       # logos
├── docs/                             # architecture, methodology, workflow, design decisions, install
├── evals/                            # behavioral eval spec + deterministic eval runner
├── examples/                         # input briefs + expected package outlines
├── generated-samples/                # demonstration packages (v1 original + its v2 migration)
├── tests/                            # the seven test suites + fixtures
├── check.py                          # THE one deterministic gate — CI job 1 runs exactly this
├── .github/workflows/                # CI (check.py + server smoke) + scheduled eval-spec lint
└── SECURITY.md                       # trust model, untrusted-content posture, reporting
```

## Verifying a local checkout

```bash
python check.py        # everything CI runs: 7 suites, v1 goldens, lint, canonical form, eval sample
```

## Contributing

Contributions are welcome — new entity types, section templates, gates, profiles, and worked examples are
the highest-value additions, and they are designed to be **additive** (registry + append-only migration).
See [`CONTRIBUTING.md`](CONTRIBUTING.md) and
[`plugins/tamheed/references/extension.md`](plugins/tamheed/references/extension.md).

## Maturity

**v2.0.** The methodology (22 stages), the relational package store (ADR-0001), the MCP tool surface, the
canonical serialization, and the migration path from v1 are defined, tested, and stable. Any future change
to the DDL, the identifier scheme, or the tool contract ships per the versioning rules in
[`plugins/tamheed/references/governance.md`](plugins/tamheed/references/governance.md) (additive = MINOR,
breaking = MAJOR + migration note). Changes are tracked in [`CHANGELOG.md`](CHANGELOG.md).

## License

Released under the **MIT License** — see [`LICENSE`](LICENSE). The license for any *generated* package is
independent and selectable at generation time.
