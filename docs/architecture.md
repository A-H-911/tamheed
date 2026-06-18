# Keystone Architecture

This document describes how Keystone is *structured* so it can be invoked many ways without ever duplicating
its logic. One principle governs everything here:

> **The skill owns the capability; the slash command only invokes it.**

Every entry point — `/keystone`, a CLI, an HTTP API, an MCP server, a UI — is a thin wrapper that normalizes
input and routes output. None of them re-implement the methodology. This is not a style preference; it is
safeguard 12, checked by gate G-CMD-THIN. See [`skill/references/extension.md`](skill/references/extension.md)
for the enforceable entry-point contract and [`skill/references/safeguards.md`](skill/references/safeguards.md)
for the safeguard list.

> See also: [`METHODOLOGY.md`](METHODOLOGY.md) (what the capability is), [`WORKFLOW.md`](WORKFLOW.md) (the
> staged process), [`ARTIFACT-CATALOG.md`](ARTIFACT-CATALOG.md) (what it produces), and
> [`skill/references/governance.md`](skill/references/governance.md) (versioning rules cited below).

## 1. The layering

```
            ┌───────────────────────────────────────────────────────────┐
   ENTRY    │  /keystone   CLI    HTTP API    MCP tool    UI   (future)   │   thin wrappers
   POINTS   │     │         │         │           │        │              │   NO methodology
            └─────┴────┬────┴────┬────┴─────┬─────┴────┬───┴──────────────┘
                       │         │          │          │
                       ▼         ▼          ▼          ▼
              normalize to the input contract  +  a mode
                       │
                       ▼
            ┌───────────────────────────────────────────────────────────┐
   SKILL    │  keystone skill  —  THE CAPABILITY (single source of truth)│
            │  SKILL.md  +  references/  (workflow, governance, gates,   │
            │  intake, clarification, artifact-rules, traceability,      │
            │  handoff, prompt-templates, repo-init, state, extension…)  │
            └─────────────────────────┬─────────────────────────────────┘
                                       │ consumes (vendored at build)
                       ┌───────────────┴───────────────┐
                       ▼                                ▼
            ┌────────────────────┐          ┌────────────────────────┐
   SHARED   │  templates/        │          │  schemas/              │
   ASSETS   │  blank artifact    │          │  input / state /       │
            │  forms (repo-root) │          │  registers / handoff   │
            └────────────────────┘          └────────────────────────┘
                                       │
                                       ▼
            ┌───────────────────────────────────────────────────────────┐
   OUTPUT   │  a generated <project-package>/  +  optional target repo   │
            └───────────────────────────────────────────────────────────┘
```

The dependency arrow points one way: **entry points depend on the skill; the skill depends on the shared
assets; nothing depends on a particular entry point.** Add a new wrapper and the skill is untouched.

## 2. Skill directory structure

The skill is the authoritative implementation. It is a progressive-disclosure bundle: a short `SKILL.md`
front door plus a `references/` directory loaded on demand, so the runtime reads a reference only when it
reaches the matching part of the work.

```
skill/
├── SKILL.md                 # front door: principles, modes, the 22-stage map, reference index
└── references/
    ├── workflow.md          # authoritative per-stage spec (the 22 stages)
    ├── modes.md             # invocation modes (full/intake/plan/resume/stage/update)
    ├── intake.md            # parsing + normalizing input
    ├── clarification.md     # gap/contradiction detection + question protocol
    ├── research-depth.md    # sizing research to genuine uncertainty
    ├── artifact-rules.md    # which artifacts to generate (selection logic)
    ├── traceability.md      # building + checking the traceability matrix
    ├── governance.md        # identifiers, statuses, versioning, cross-refs
    ├── quality-gates.md     # completeness/consistency/readiness gates
    ├── safeguards.md        # anti-patterns + their controls
    ├── handoff.md           # assembling the execution-agent handoff
    ├── prompt-templates.md  # initial / follow-up / review prompt forms
    ├── repo-init.md         # running the repository bootstrap safely
    ├── generated-structure.md  # the layout of a generated package
    ├── state.md             # persisting, resuming, updating state
    └── extension.md         # adding capabilities without touching core logic
```

When packaged to run standalone, the skill also carries vendored copies of `templates/` and `schemas/`
(see §8). The skill contains **no** entry-point parsing and **no** single project's content — it is pure
methodology.

## 3. Command directory structure

The slash command is a thin entry point and nothing more.

```
commands/
└── keystone.md              # front-matter (description, argument-hint) + the 5-step wrapper:
                             #  1 gather input  2 validate invocation syntax only
                             #  3 normalize to the input contract + mode
                             #  4 invoke the keystone skill  5 route output
```

Its instructions explicitly forbid methodology: *"Never duplicate or summarize the methodology here, and
never make planning decisions in this wrapper. If you feel the urge to add logic, it belongs in the skill."*
That is the architecture stated in the artifact itself.

## 4. The command ↔ skill interface

The interface is a normalized request in, a routed package out. The wrapper does input *syntax* validation
only; **content** validation (is this a real, coherent project?) is the skill's job.

### Input contract (normalized request)

The wrapper maps whatever the user gave it to a single shape the skill understands. Conceptually:

```json
{
  "description": "…raw project prose…",        // OR
  "brief_path": "path/to/brief.md",            // one of description | brief_path
  "mode": "full | intake | plan | resume | update | stage:<id>",   // optional; skill infers + confirms if absent
  "profile": "enterprise | rnd | legacy | ai-agentic | …",         // optional hint
  "package_dir": "where to write the generated package",           // optional
  "repo": { "create": true, "owner": "…", "visibility": "private|public",
            "license": "MIT|Apache-2.0|…", "default_branch": "main" },
  "flags": { "dry_run": false, "no_repo": false }
}
```

The structured form is governed by `schemas/project-input.schema.json`. If `mode` is omitted, the wrapper
leaves it unset so the skill infers and **confirms** it — the wrapper never guesses the mode silently.

### Output contract (routed result)

The skill returns either a completed package or a pause at a gate. The wrapper surfaces, without
reinterpreting:

- the generated package directory and the key artifacts (charter, execution-readiness report, handoff
  initial prompt), linked for the user;
- any **questions** the skill is waiting on (clarification batch) or any **approval gate** it has paused at
  (scope, decisions, roadmap, repo creation, handoff, final go/no-go);
- for repo initialization, the dry-run report or the created-repo result.

The handoff itself conforms to `schemas/handoff-package.schema.json`; normalized run state is persisted to
`keystone-state.json` (`schemas/keystone-state.schema.json`) so a later `resume`/`update` reloads instead of
re-asking.

### Invocation flow

```
 user ──$ARGUMENTS──▶ /keystone (wrapper)
                         │ 1. gather input (prose | @file | path)
                         │ 2. validate invocation SYNTAX only (flag values)
                         │ 3. normalize → { input contract } + mode?
                         ▼
                     keystone skill  ── reads SKILL.md, then references on demand
                         │ runs the 22 stages (Understand → Explore → Plan & hand off)
                         │ pauses at human gates ◀───── asks user ─────▶ resumes
                         │ generates artifacts from templates/, fills schemas/
                         ▼
                     generated <project-package>/  (+ optional target repo)
                         │
                         ▼
                     wrapper routes output ──▶ user (links + pending questions/gates)
```

Crucially, the box that "runs the 22 stages" is the **same skill** no matter which entry point sits above it.
A CLI, an API call, an MCP tool, or a UI button all converge on that one box.

## 5. Error-handling behavior

Errors are handled at the layer that owns them, and the two layers own different errors.

**Wrapper-level (syntax/invocation).** The wrapper validates only that recognized flags have valid values
(e.g. `--mode` ∈ the allowed set, `--visibility` ∈ private|public). On a bad flag or empty input, it prints
the help block and stops. It does not attempt to interpret or repair project content.

**Skill-level (content/process).** Everything else is the skill's responsibility and is handled through the
workflow's per-stage *failure conditions* rather than by crashing:

- **Empty/unreadable input** → ask for input (stage 1 fail path).
- **Too-thin-to-classify input** → proceed with an `unknown` profile and raise an `OQ-` (stage 2).
- **Unsourced requirement** → demote to an `ASM-` or raise an `OQ-`; it never becomes a silent requirement
  (stage 4 / gate G-REQ-SRC).
- **Unresolved hard contradiction** → blocked from passing scope lock (gate G-CONFLICT).
- **User unavailable for clarification** → proceed under explicit recorded assumptions and mark the package
  **provisional** (stage 7).
- **Critical quality-gate failure** → loop back to the owning stage; never report "ready" (stages 19/22).
- **Missing git / dirty target at repo init** → report and stop; never overwrite without `--force` (stage 18
  / safeguard 16).
- **Handoff prompt references a missing artifact** → fail G-HANDOFF and fix before shipping.

The principle: a wrapper fails *fast and loud* on bad invocation; the skill fails *safe and recorded* on
process problems, preferring an explicit assumption, open question, or gate failure over a silent guess.

## 6. Configuration files

| File | Owner | Role |
|---|---|---|
| `commands/keystone.md` front-matter | wrapper | `description`, `argument-hint` for the entry point |
| `schemas/project-input.schema.json` | shared | the input contract the wrapper normalizes to |
| `schemas/keystone-state.schema.json` | shared | shape of `keystone-state.json` (resume/update state) |
| `schemas/handoff-package.schema.json` | shared | shape of the handoff manifest |
| `schemas/*.schema.json` (registers, experiment, manifest, …) | shared | structured shapes for generated artifacts |
| `keystone-state.json` (in a package) | generated | machine-owned run state; not hand-edited |
| `manifest.json` (in a package) | generated | artifacts present, versions, generation metadata, omission reasons |

Project-type **profiles** (which bias artifact selection and research depth) and the **registries** of
artifact types, templates, schemas, gates, diagram kinds, and entry points are configuration *of the
methodology* and live with the skill's references, not in any wrapper — see
[`skill/references/artifact-rules.md`](skill/references/artifact-rules.md),
[`skill/references/research-depth.md`](skill/references/research-depth.md), and
[`skill/references/extension.md`](skill/references/extension.md).

## 7. Entry points and how future ones reuse the same skill

`/keystone` is the first entry point; it is deliberately replaceable and duplicable. Any future entry point —
another slash command, a CLI, an HTTP API, an MCP server, or a UI — reuses the **same** skill by normalizing
its input to the skill's contract (`schemas/project-input.schema.json` + a mode), invoking the skill, and
routing the output back — carrying no methodology or business logic of its own.

The enforceable contract a conforming entry point MUST satisfy, and the worked table of how each wrapper
kind (slash command, CLI, HTTP API, MCP server, UI) maps to it, live in
[`skill/references/extension.md`](skill/references/extension.md) — the single source of truth, not restated
here. The check is mechanical: gate **G-CMD-THIN** flags any entry point that smuggles methodology in.

## 8. Packaging and portability

`templates/` and `schemas/` are **repo-root single sources of truth**. The skill *consumes* them but does not
own a second copy during development. To ship the skill so it runs standalone (without the surrounding repo),
a **build/vendor step copies `templates/` and `schemas/` into a self-contained skill bundle**, so the bundle
carries everything it needs:

```
  REPO (development, single source of truth)        STANDALONE SKILL BUNDLE (after vendor step)
  ─────────────────────────────────────────        ───────────────────────────────────────────
  keystone/                                          keystone-skill/
  ├── skill/SKILL.md + references/        ──copy──▶  ├── SKILL.md + references/
  ├── templates/   ◀── single source ─────vendor──▶  ├── templates/   (vendored copy)
  ├── schemas/     ◀── single source ─────vendor──▶  ├── schemas/     (vendored copy)
  ├── commands/keystone.md                           └── (no repo-root specs needed at runtime)
  └── METHODOLOGY / WORKFLOW / ARTIFACT-CATALOG / ARCHITECTURE  (human-facing, not vendored)
```

Editing forms or data shapes is done **once**, at the repo root; the vendor step re-syncs the bundle. This
keeps the running skill portable while avoiding two diverging copies during development. The human-facing
specs (this file and its siblings) are documentation and are not vendored into the runtime bundle. Repository
logic stays provider-neutral — local git always, remote creation an optional, swappable step — so portability
is not tied to any one host (safeguards 14–16).

## 9. Version-compatibility rules

Keystone versions with semver `MAJOR.MINOR.PATCH`, and the boundary between MINOR and MAJOR is defined by
*compatibility of the contracts above*:

- **MINOR (additive, non-breaking).** New artifact types, new templates, new schemas, new optional fields,
  new quality gates, new project-type profiles, new diagram kinds, new entry points. Existing packages keep
  working; the validator degrades gracefully on a package authored under a prior MINOR version.
- **MAJOR (breaking).** A change to an existing schema's required fields, to the identifier scheme, or to the
  handoff contract. A MAJOR release **ships a migration note** describing how to bring older packages
  forward.
- **PATCH.** Fixes that change neither contracts nor behavior in a user-visible way.

Generated documents additionally carry their own front-matter `version` (semver or `vN`) bumped on material
change; immutable-after-approval artifacts (ADRs, approved acceptance criteria) are superseded rather than
edited. The authoritative versioning and supersession rules are in
[`skill/references/governance.md`](skill/references/governance.md), and the additive-vs-breaking boundary is
restated in [`skill/references/extension.md`](skill/references/extension.md).

## 10. The principle, enforced

To close where we began, the architecture exists to make one sentence true and verifiable:

> **The skill owns the capability; the slash command only invokes it.**

It is enforced three ways: (1) the wrapper's own instructions forbid methodology and planning decisions; (2)
the entry-point contract requires every wrapper to normalize-and-invoke with no business logic; and (3) gate
**G-CMD-THIN** mechanically flags any entry point that smuggles methodology in. New capabilities are added by
the additive extension contract — register an entry, drop in a file — never by forking the workflow into a
wrapper.
