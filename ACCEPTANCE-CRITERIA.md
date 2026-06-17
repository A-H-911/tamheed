# Keystone — Acceptance Criteria

Acceptance criteria for the **Keystone capability itself** — the skill, the thin command, the templates,
schemas, scripts, and validator — **not** for any project Keystone plans. Each criterion is testable: it
states an observable condition that can be checked by running Keystone on a brief, inspecting the output, or
running `python tests/validate_package.py`.

Criteria use `AC-` identifiers (per [`skill/references/governance.md`](skill/references/governance.md)).
Two tiers:

- **MVP** (`AC-001`…) — the smallest Keystone that is genuinely useful end to end.
- **Full Target** (`AC-101`…) — the complete v1.0-class capability.

Status legend: each AC carries a status of `Proposed` until verified, then `Approved`. All are `Proposed` at
v0.1.

---

## MVP acceptance criteria

The MVP must take a real brief and produce a usable, validated handoff package for a coding agent, with the
"thin command" principle intact.

| ID | Criterion | How to verify (test) |
|---|---|---|
| **AC-001** | Keystone **accepts a long-form brief** — multi-paragraph prose or a file/`@file` path — as input. | Invoke with a several-paragraph brief and with a file path; both are read and processed without reformatting requirements. |
| **AC-002** | It runs the **intake → clarification → scope** sequence: extracts explicit requirements with sources, classifies them, detects ambiguities/contradictions, asks **focused, batched** clarification questions only where the answer changes the plan, and locks scope (goals, non-goals, in/out, success metrics). | Run on a brief with a deliberate gap and a deliberate contradiction; confirm the gap becomes an open question or assumption, the contradiction is surfaced, and a scope section is produced. |
| **AC-003** | It generates the **Always artifact set**: a charter, requirements (`FR-`/`NFR-`), an assumption register (`ASM-`, each with risk-if-wrong), an open-question (`OQ-`) and open-decision (`DEC-`) register, a risk register (`RISK-`), a phased roadmap (`PH-`), acceptance criteria (`AC-`), and a traceability matrix. | Run `--mode full` (or `plan`); confirm each of these artifacts exists in the generated package. |
| **AC-004** | All generated artifacts use **valid identifiers** following the governance scheme (correct prefixes, zero-padded, unique within the package, never reused). | `validate_package.py` reports zero identifier-format or uniqueness violations. |
| **AC-005** | The generated package has a **passing traceability matrix**: every `FR-`/`NFR-` is reachable to at least one decision, task, test, and (where it asserts user-visible behavior) an acceptance criterion. | `validate_package.py` reports the traceability gate as **pass** (no unlinked requirements). |
| **AC-006** | It produces a **handoff initial prompt** (`handoff/initial-prompt.md`) — a first message that an execution agent could act on, pointing at the package and its reading order. | Confirm the file exists, references the charter/scope and key artifacts, and contains no unresolved placeholders. |
| **AC-007** | The **validator runs and reports gates**: invoked against a generated package, it checks identifiers, links, traceability, and the implemented quality gates, prints per-gate pass/fail, and exits non-zero on a critical-gate failure. | `python tests/validate_package.py <package>` on a good package exits 0; on a package with a broken link or unlinked requirement it exits non-zero and names the failing gate. |
| **AC-008** | The **thin command contains no methodology**: `commands/keystone.md` only gathers input, validates invocation syntax, normalizes to the input contract, invokes the skill, and routes output. | Inspect `commands/keystone.md`: it makes no planning decisions, defines no stages, and defers content validation to the skill. |
| **AC-009** | The skill **records assumptions instead of inventing requirements**: where it proceeds without an answer, it writes an `ASM-` (with risk-if-wrong) rather than asserting a requirement. | On a brief with an unspecified detail, confirm the detail appears as an assumption, not as an `FR-`/`NFR-`. |
| **AC-010** | **Proposed decisions are never rendered as approved.** Decisions Keystone authors on its own initiative are `Proposed` until the user approves them. | Inspect the open-decision register after a run with no explicit approval: all Keystone-originated decisions are `Proposed`. |
| **AC-011** | **Plan-only works without a repository.** `--mode plan` / `--no-repo` produces the artifact set and never requires Python/`git`/`gh`. | Run `--no-repo` in an environment without `git`; the package is produced and no repo is written. |
| **AC-012** | The MVP is **vendor/agent/stack-neutral by default**: with no stack specified in the brief, no artifact silently commits to a specific provider, agent, or technology. | Run on a stack-agnostic brief; confirm technology choices appear only as options/open decisions, not as defaults. |

**MVP exit condition:** `AC-001`…`AC-012` all verified `Approved` on at least one real worked example.

---

## Full Target acceptance criteria

The full capability completes the workflow, the artifact catalog, the tooling, and the evidence.

| ID | Criterion | How to verify (test) |
|---|---|---|
| **AC-101** | **All 22 stages** are implemented and driveable end to end (Understand 1–8, Explore 9–15, Plan & hand off 16–22), each honoring its entry/exit criteria and gates. | Run `--mode full` to completion on a non-trivial brief; confirm each stage's outputs appear and no gate is skipped to "look finished." |
| **AC-102** | **Resume** works: `--mode resume` reloads `keystone-state.json`, reconciles human edits, and continues from the last completed stage without re-asking answered questions. | Stop a run mid-way, edit an artifact by hand, resume; confirm it continues correctly and respects the edit. |
| **AC-103** | **Update** works: `--mode update` applies new decisions/progress, re-derives dependent artifacts, and bumps versions per the governance rules. | Approve a previously-proposed decision via update; confirm the traceability matrix, roadmap rollups, and readiness report regenerate and versions bump. |
| **AC-104** | **All conditional artifacts** are supported and emitted only when their selection trigger fires (ADRs, technology-comparison matrices, hypotheses, experiment/POC plans, diagrams, milestones, definition-of-ready/done, etc.) — and empty/stub artifacts are never emitted. | Run on a brief that triggers ADRs and a tech comparison, and a tiny brief that should collapse to the minimal set; confirm the right artifacts appear in each and no empty directories are created. |
| **AC-105** | **Repository bootstrap creates a usable repo.** `scripts/init_skill_repo.py` produces folders, baseline files, README + logo, license, ADR/doc dirs, changelog, version, and an initial commit; it is dry-run-capable, idempotent, and never overwrites without `--force`. | Run the bootstrap into a temp dir (and `--dry-run`); confirm a usable repo, a clean idempotent re-run, and that `--dry-run` writes nothing. |
| **AC-106** | **All quality gates are implemented** and enforced by the validator (completeness, identifier integrity, link integrity, traceability, decision-status correctness, "no unverified claim asserted as fact," readiness). | `validate_package.py` exercises every gate listed in `quality-gates.md`; each is reachable and reported. |
| **AC-107** | **At least 5 worked examples** exist, each an input brief plus its generated package, covering distinct project types (e.g. greenfield app, R&D mission, legacy/migration, AI-agentic, library/CLI). | `examples/` and `generated-samples/` contain 5 distinct cases; each generated package passes `validate_package.py`. |
| **AC-108** | **Provider/agent/stack neutrality holds across the whole capability**: nothing in the skill, scripts, templates, or schemas hard-codes a single vendor, agent, repo provider, or tech stack as mandatory. | Review plus a grep-style check across `skill/`, `scripts/`, `templates/`, `schemas/`; the only provider-specific items are optional (e.g. `gh` for remote creation). |
| **AC-109** | **Extension points are documented and usable**: a new artifact type, template, schema, quality gate, project-type profile, diagram kind, or entry point can be added additively per `extension.md` without editing core workflow logic. | Follow `extension.md` to add a trivial new artifact type end to end (template + catalog row + selection trigger + optional schema); confirm it generates without changing the workflow. |
| **AC-110** | **The handoff package is complete and schema-valid**: initial prompt, follow-up prompts (one per phase gate), review prompts, a handoff manifest conforming to `handoff-package.schema.json`, and an execution-readiness report. | Inspect `handoff/`; validate the manifest against its schema; confirm one follow-up prompt per `PH-`. |
| **AC-111** | **State and schemas are authoritative and consistent**: `keystone-state.json` validates against `keystone-state.schema.json`, input validates against `project-input.schema.json`, and a package authored under a prior MINOR version still validates (graceful degradation). | Validate state and input instances against their schemas; run the validator against an older-version sample and confirm it degrades gracefully. |
| **AC-112** | **Readiness is honest**: the final readiness report declares "ready" only when no critical gate fails, and clearly lists any open questions, deferred items, and rejected alternatives that survive. | Force a critical gate failure; confirm the report does **not** say ready and the failure is named. |
| **AC-113** | **Documentation and packaging are complete**: `README.md`, `CONTRIBUTING.md`, `METHODOLOGY.md`, `WORKFLOW.md`, `ARTIFACT-CATALOG.md`, and `ARCHITECTURE.md` exist and agree with the skill; Keystone installs as a skill/plugin per the README; logo assets resolve at `docs/assets/`. | Follow the README install steps in a clean agent; confirm the skill loads, the command is available, and the logo references resolve. |
| **AC-114** | **Versioning discipline holds**: semver is applied to the skill/package; breaking changes to schemas, identifiers, or the handoff contract ship a migration note; immutable-after-approval artifacts (ADRs, approved ACs) are superseded, not edited in place. | Inspect version metadata and a supersession example; confirm a migration note accompanies any MAJOR change. |

**Full Target exit condition:** `AC-101`…`AC-114` all verified `Approved`, with the 5 worked examples each
passing `validate_package.py`.

---

## Traceability note

These acceptance criteria are the test backbone for Keystone's own development. The roadmap in
[`ROADMAP.md`](ROADMAP.md) maps each phase's exit criteria to the `AC-` IDs above, so every phase can be
checked against concrete, runnable conditions rather than narrative completeness.
