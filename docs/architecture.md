# Keystone architecture

How Keystone is *structured* so it can be invoked many ways without ever duplicating its logic. One principle
governs everything:

> **The skill owns the capability; every entry point is a thin wrapper.**

A slash invocation, a CLI, an HTTP API, an MCP server, a UI — each only normalizes input and routes output;
none re-implements the methodology. This is enforceable (gate **G-CMD-THIN**); the contract lives in
[`../plugins/tamheed/references/extension.md`](../plugins/tamheed/references/extension.md). See also
[`design-decisions.md`](design-decisions.md), [`methodology.md`](methodology.md) (what the capability is),
[`workflow.md`](workflow.md) (the staged process), and the in-bundle artifact catalog at
[`../plugins/tamheed/references/artifact-catalog.md`](../plugins/tamheed/references/artifact-catalog.md).

## 1. Layering

```
   ENTRY POINTS   slash · CLI · HTTP API · MCP · UI        (thin wrappers, NO methodology)
                        │  normalize to the input contract + a mode
                        ▼
   SKILL          the keystone skill — THE CAPABILITY (single source of truth)
                  SKILL.md + references/ (workflow, governance, gates, intake, clarification,
                  artifact-rules, traceability, handoff, prompt-templates, state, extension…)
                        │  reads, in the same bundle:
                        ▼
   BUNDLED ASSETS templates/ (blank forms) · schemas/ (data shapes) · scripts/ (bootstrap + validator)
                        │
                        ▼
   OUTPUT         a generated <project-package>/  (+ optional target repo)
```

The dependency arrow points one way: entry points depend on the skill; the skill depends only on assets
bundled *with it*; nothing depends on a particular entry point. Add a wrapper and the skill is untouched.

## 2. Distribution: a self-contained plugin

Keystone is packaged as a **Claude Code plugin**, and the repository doubles as its own **marketplace**:

```
keystone/
├── .claude-plugin/marketplace.json        # repo = marketplace; lists the one plugin
└── plugins/tamheed/                       # THE PLUGIN — the self-contained skill bundle
    ├── .claude-plugin/plugin.json
    ├── SKILL.md                            # always-loaded front door (owns the capability)
    ├── references/                         # on-demand depth + artifact-catalog.md
    ├── templates/   schemas/               # single sources of truth for forms / data shapes
    ├── scripts/                            # validate_package.py (frozen v1 gate engine)
    ├── db/                                 # v2 store: schema.sql + store.py + CANONICAL.md
    ├── server/                             # Tamheed MCP server (only write path into a package)
    └── assets/                             # logos
```

**Self-containment is a hard requirement, not a preference.** Claude Code copies the plugin directory to a
cache on install, so anything the skill reads or invokes at runtime must live inside `plugins/tamheed/` with
zero outward references. This replaces the earlier "single source at repo root + vendor step" model (which
had no build and left references dangling once installed). The same bundle is therefore also usable as a
standalone Agent Skill or a manual copy into a skills directory. Human-facing docs (`docs/`, this file) are
*not* part of the bundle and may link into it, but the bundle never links out.

## 3. The entry-point ↔ skill interface

A normalized request in, a routed package out. An entry point validates only invocation *syntax*; **content**
validation (is this a real, coherent project?) is the skill's job.

**Input contract** — whatever the user gave is mapped to one shape the skill understands, governed by
`schemas/project-input.schema.json`:

```json
{
  "description": "…raw project prose…",   // OR "brief_path": "path/to/brief.md"
  "mode": "full | intake | plan | resume | update | stage:<id>",   // optional; skill infers + confirms
  "profile": "enterprise | rnd | legacy | ai-agentic | …",         // optional hint
  "package_dir": "…", "repo": { … }, "flags": { "dry_run": false, "no_repo": false }
}
```

If `mode` is omitted, the skill infers and **confirms** it — never guesses silently.

**Output contract** — the skill returns either a completed package (linking the charter, execution-readiness
report, and handoff initial prompt) or a pause at a gate (clarification batch, or an approval gate: scope,
decisions, roadmap, repo creation, handoff, final go/no-go). The handoff conforms to
`schemas/handoff-package.schema.json`; run state persists to `keystone-state.json`
(`schemas/keystone-state.schema.json`) so `resume`/`update` reload instead of re-asking.

Whatever sits on top — slash invocation, CLI, API, MCP, UI — converges on the *same* skill.

## 4. Error handling

Errors are handled at the layer that owns them. A **wrapper** fails *fast and loud* on bad invocation
(unknown flag, empty input → print help and stop); it never interprets project content. The **skill** fails
*safe and recorded* on process problems, via the workflow's per-stage failure conditions rather than by
crashing: empty input → ask; too-thin input → proceed under an `unknown` profile + raise an `OQ-`; unsourced
requirement → demote to an `ASM-` or raise an `OQ-` (never a silent requirement); unresolved hard
contradiction → blocked from scope lock; user unavailable → proceed under explicit recorded assumptions and
mark the package *provisional*; critical gate failure → loop back, never report "ready"; missing git / dirty
target at repo init → report and stop, never overwrite without `--force`.

## 5. Versioning

Semver `MAJOR.MINOR.PATCH`, with the boundary defined by contract compatibility:

- **MINOR (additive):** new artifact types, templates, schemas, optional fields, quality gates, profiles,
  diagram kinds, entry points. Existing packages keep working; the validator degrades gracefully.
- **MAJOR (breaking):** a change to an existing schema's required fields, the identifier scheme, or the
  handoff contract — ships with a migration note (see
  [`../plugins/tamheed/references/governance.md`](../plugins/tamheed/references/governance.md)).
- **PATCH:** fixes that change neither contracts nor user-visible behavior.

Immutable-after-approval artifacts (ADRs, approved acceptance criteria) are superseded, never rewritten.
The plugin's own version lives in `plugins/tamheed/.claude-plugin/plugin.json` and the marketplace entry;
notable changes are recorded in [`../CHANGELOG.md`](../CHANGELOG.md).
