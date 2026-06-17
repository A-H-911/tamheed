# Keystone — Implementation Plan

How to build **Keystone** itself: the capability that turns a project description into a validated,
traceable, execution-ready planning and handoff package. This document compares implementation approaches
and recommends one. It is about *implementing Keystone*, not about any project Keystone plans.

> Keystone is an independent, reusable capability. The implementation must stay vendor-, agent-, provider-,
> and stack-neutral.

---

## 1. What we are building

Keystone is best built as an **integrated combination** of seven cooperating components, not a single
artifact:

1. **A reusable agent skill** — the authoritative implementation: methodology, the 22-stage workflow,
   judgment, artifact selection, gates, and handoff logic (`skill/SKILL.md` + `skill/references/*`).
2. **A thin slash-command entry point** — `/keystone`; normalizes invocation and routes output, nothing more
   (`commands/keystone.md`).
3. **A prompt + template package** — blank artifact forms and prompt templates the skill fills in
   (`templates/`, plus prompt templates referenced from `skill/references/prompt-templates.md`).
4. **A script-driven project generator** — deterministic repository bootstrap that creates a usable repo
   (`scripts/init_skill_repo.py`).
5. **Machine-readable schemas** — single source of truth for data shapes: input, state, handoff manifest,
   and structured register fields (`schemas/`).
6. **Automated validators** — mechanical checks for identifiers, link integrity, traceability, and quality
   gates (`tests/validate_package.py`).
7. **Repo-bootstrap tooling** — the operational layer (dry-run, idempotency, optional remote) wrapping
   component 4.

The design question is **how the judgment and the mechanics divide between an LLM-driven skill and
deterministic code** — which the approach comparison below answers.

---

## 2. Guiding constraint

One principle constrains every option:

> **The skill owns the capability; the command (and any other entry point) only invokes it.**

Whatever the implementation, the methodology must live in exactly one place (the skill), entry points must
contain no methodology and no business logic, and deterministic helpers must be *invoked by* the skill
rather than *replacing* its judgment. This is enforced by the entry-point contract in
[`skill/references/extension.md`](skill/references/extension.md) and safeguard `G-CMD-THIN`.

---

## 3. Approaches compared

### Approach A — Pure-prompt skill only

Everything (including repo creation and validation) is performed by the LLM following prompt instructions;
no executable scripts. Templates and schemas exist only as text the model reads.

- **Maintainability** — Medium. One place to edit, but deterministic chores (repo scaffolding, traceability
  checks) are re-derived by the model every run, so behavior drifts and is hard to pin down.
- **Portability** — High. Runs anywhere an agent reads/writes files; zero runtime dependencies.
- **Extensibility** — Medium. Easy to add prose; hard to guarantee a new gate is *actually* enforced without
  a mechanical check.
- **Effort** — Low to start, but rework-heavy: the same deterministic logic is re-specified in prose and
  still produces non-repeatable output.
- **Key weakness** — No reproducibility for the steps that *must* be reproducible. Validation is
  "the model says it passed," which is exactly the kind of unverified claim Keystone's own safeguards forbid.

### Approach B — Skill + deterministic scripts (hybrid) — **RECOMMENDED**

The skill remains the single authoritative implementation for all judgment; **deterministic, repeatable
steps** (repository initialization, package validation against schemas, traceability/identifier checks) are
delegated to small, well-tested scripts that the skill invokes. Templates and schemas are the shared,
single-source-of-truth substrate both rely on.

- **Maintainability** — High. Judgment in one place (the skill); mechanics in tested code; schemas keep the
  two honest. Each kind of change has an obvious home.
- **Portability** — High. The skill runs in any file-capable agent; scripts need only Python 3.9+ (and `git`
  / `gh` only for *optional* remote creation). Degrades to plan-only where Python is unavailable.
- **Extensibility** — High. Additive registries (templates, schemas, gates, profiles, entry points) plus the
  ability to back a new mechanical gate with a real check in the validator.
- **Effort** — Medium. More upfront than A, but the deterministic parts are written once and stop drifting,
  which lowers total cost across many projects.
- **Key strength** — Reproducible where it matters (repo init, validation) and flexible where it matters
  (intake, clarification, architecture, decisions), while fully preserving "the skill owns the capability."

### Approach C — Full standalone application / service

A hosted application or service (API/UI/orchestrator) that embeds the planning logic in conventional code,
with the LLM as one subordinate call among many.

- **Maintainability** — Low to Medium. Largest surface: server, deployment, state store, auth, versioned
  API. Methodology risks being duplicated between code and prompts.
- **Portability** — Low. Now coupled to a runtime/host/provider — the opposite of the neutrality requirement;
  no longer "drops into any agent."
- **Extensibility** — Medium. Powerful but heavyweight; every extension is a code change and a deploy.
- **Effort** — High. Months of platform work before the methodology is even exercised.
- **Key weakness** — Violates the neutrality and "thin wrapper" goals, and over-builds for v0.1. A service
  can come later *as an entry point* over the skill, never as a replacement for it.

### Scorecard

| Criterion | A · Pure-prompt | **B · Hybrid (recommended)** | C · Standalone app/service |
|---|---|---|---|
| Maintainability | Medium | **High** | Low–Medium |
| Portability | High | **High** | Low |
| Extensibility | Medium | **High** | Medium |
| Effort (to v0.1) | Low | **Medium** | High |
| Reproducibility of deterministic steps | Low | **High** | High |
| Preserves "skill owns the capability" | Yes | **Yes** | At risk |
| Vendor/agent/stack neutrality | High | **High** | Low |

---

## 4. Recommendation

**Adopt Approach B — the skill + deterministic scripts hybrid.**

- The **skill is authoritative for judgment**: intake, classification, clarification, scope, research depth,
  architecture exploration, option comparison, decisions, risk analysis, artifact selection, and handoff
  authoring all live in `skill/SKILL.md` + `skill/references/*`.
- **Scripts handle deterministic, repeatable steps** so they are fast, testable, and identical every run:
  - `scripts/init_skill_repo.py` — repository bootstrap (folders, baseline files, README + logo, license,
    ADR/doc dirs, changelog, version, initial commit, optional remote). Dry-run-capable, idempotent, never
    overwrites without `--force`.
  - `tests/validate_package.py` — the validator: identifier conventions, cross-reference/link integrity,
    traceability completeness, and quality-gate results.
- **Templates and schemas are the shared substrate.** `templates/` holds blank forms; `schemas/` holds data
  shapes (input, state, handoff manifest, structured register fields). Both the skill and the scripts read
  them, which keeps generation and validation aligned to one source of truth.
- **The command stays thin.** `/keystone` (and any future CLI/API/MCP/UI) only normalizes input to the
  skill's input contract and routes output. No methodology, no planning decisions, ever.

This delivers reproducibility where correctness must be mechanical (repo init, validation) and flexibility
where the work is genuinely judgment-bound (everything else), at v0.1-appropriate effort, without coupling
to any vendor or stack.

### Why not A or C

- **Not A**, because "the model asserts the gates passed" is precisely the unverified claim Keystone's own
  safeguards prohibit; deterministic steps must be reproducible and checkable.
- **Not C**, because a service couples Keystone to a runtime and host, breaking neutrality and the thin-entry
  principle, and massively over-builds for the current maturity. If a service is ever wanted, build it as a
  thin entry point *over* the skill (per the entry-point contract), not as a re-implementation.

---

## 5. Component responsibility table

| Component | Owns / is authoritative for | Must NOT | Source of truth | Primary location |
|---|---|---|---|---|
| **Skill** (`keystone`) | The whole capability: methodology, 22-stage workflow, judgment, artifact selection, gate evaluation, handoff authoring | Hard-code one vendor/agent/stack; duplicate template or schema content inline | The methodology | `skill/SKILL.md`, `skill/references/*` |
| **Slash command** (`/keystone`) | Gather input, validate *invocation syntax only*, normalize to the input contract, invoke the skill, route output | Contain any methodology or make any planning decision | — (delegates entirely) | `commands/keystone.md` |
| **Templates** | The exact shape/wording of each blank artifact and prompt | Contain project-specific content | Artifact forms | `templates/` |
| **Schemas** | Machine-readable data shapes (input, state, handoff manifest, register fields) | Drift from what the scripts and skill assume | Data shapes | `schemas/` |
| **Generator script** | Deterministic repository bootstrap (folders, baseline files, license, version, initial commit, optional remote) | Make planning decisions; overwrite without `--force`; require a specific provider | Repo-init mechanics | `scripts/init_skill_repo.py` |
| **Validator** | Mechanical checks: identifiers, links, traceability completeness, quality-gate pass/fail | Invent requirements or "pass" without evidence | Gate enforcement | `tests/validate_package.py` |
| **Repo-bootstrap tooling** | Operational guarantees around the generator: dry-run, idempotency, optional remote via `git`/`gh` | Be a hard dependency for plan-only runs | Bootstrap operations | `scripts/`, `skill/references/repo-init.md` |
| **Docs / specs** | Human-facing rationale and catalogs | Become a second source of methodology that can drift from the skill | Human-facing explanation | `METHODOLOGY.md`, `WORKFLOW.md`, `ARTIFACT-CATALOG.md`, `ARCHITECTURE.md` |

---

## 6. Build sequence (summary)

The full phased plan is in [`ROADMAP.md`](ROADMAP.md); the capability's own acceptance criteria are in
[`ACCEPTANCE-CRITERIA.md`](ACCEPTANCE-CRITERIA.md). In brief: extract the methodology, define the skill
architecture and artifact catalog, build templates and schemas, ship the thin command, add the deterministic
generator and validator, brand and document, then add worked examples, packaging, versioning, and a release —
each phase gated by testable exit criteria.

---

## 7. Risks and mitigations (implementation-level)

| Risk | Mitigation |
|---|---|
| Methodology leaks into the command or a future entry point | Enforce the entry-point contract and gate `G-CMD-THIN`; the validator/review flags any logic in wrappers. |
| Templates/schemas and script behavior drift apart | Single source of truth in `templates/` + `schemas/`; the validator checks generated packages against the schemas in CI. |
| Python unavailable in the host agent | Scripts power only deterministic steps; the skill degrades to `plan`/`--no-repo` so planning still works. |
| Over-engineering toward a service (Approach C) | Anchor on B for v0.1; any service is added later strictly as a thin entry point over the skill. |
| Non-reproducible "it passed" validation | Mechanical gates are executed by `validate_package.py`, not asserted by the model. |
