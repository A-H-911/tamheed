# Handoff prompt templates

Operational guidance for writing the project prompt **files** (v3, plan 027: prompts are plain
`.md` in `<package>/prompts/`, never database rows — any non-stock filename marks a project
prompt; `handoff_emit` G-INJECT- and stale-scans every file). **Naming (plan 028): project
prompts are purpose-named kebab-case like the stock library — `kickoff.md`,
`phase3-resume.md`. The `prm-NNN-<kind>.md` names on converted legacy prompts are conversion
audit identifiers, not a pattern to imitate; the tool never renames — renames are the
operator's, git keeps history.** Blank fill-in forms live in
`../templates/initial-prompt.template.md`, `follow-up-prompts.template.md`, and
`review-prompts.template.md`. Write prompts for Claude Code (CLI/IDE) and reference real entity ids;
keep the plan's technology choices vendor-neutral. Use Claude Code affordances — plan mode,
TodoWrite, subagents, a code-review pass — where they help, named as capabilities, not hard dependencies.

## Initial prompt — shape

```
This repo contains the APPROVED plan for <project>. You are starting implementation.
<one-paragraph orientation: what the project is, where the plan lives, that decisions are final>.

Step 1 — Orientation (use plan mode; no code): read <list the few key plan docs>. Then give me:
(a) a ≤1-page summary of what you'll build and the invariants you must respect [list INV- ids];
(b) your execution plan for Phase <PH-1> with file layout and pass/fail per task.
STOP and wait for my approval.

Step 2 — <first bounded task> (after approval): <one concrete deliverable with pass/fail>; track the backlog with TodoWrite. Pause for review.

Rules: respect the invariants; pin versions; record deviations as ADRs; don't expand scope beyond Phase 1.
Prerequisites: <runtimes/accounts/versions>.
```

The initial prompt must (1) orient, (2) give one bounded task, (3) stop at an approval gate. It never
authorizes building the whole system at once.

## Follow-up prompts — shape

One per phase gate. Each: resume context ("Phase <N-1> is complete and approved; its exit criteria were
…"), the phase goal, the bounded tasks with pass/fail, the invariants still in force, and the exit gate.
Plus situational prompts: fallback-invocation, fresh-session refresher, invariant audit, engine/dependency
upgrade + baseline regen, bug triage, release prep, deviation ADR, status report.

## Review prompts — shape

Prompts that make Claude Code (or a human) check work against the plan — a code-review pass (e.g.
`/code-review`) where available: invariant audit ("verify the
implementation honors `INV-001..INV-00n`; report violations with file:line"), readiness recheck ("re-run
the quality gates against the current repo"), and PR review against acceptance criteria.

## The scenario skills (plan 018, grown in plan 027; skills since v5, plan 116)

Distinct from the project prompts above: sixteen operator-invoked scenario skills ship in the bundle
(`../skills/<name>/SKILL.md`, `disable-model-invocation`; invoked as `/tamheed:<name>`, an argument
naming another package) and are updated with the plugin — never emitted per project. Only the
operator guide (`prompts/README.md`) is still emitted, `{package}` substituted, by `package_create`,
`package_migrate`, `package_adopt`, and `handoff_emit`; it is the authoritative situation map. This
file teaches AUTHORING project prompts:

| Skill | Scenario |
|---|---|
| `orient-resume` | Re-orient after a session clear/compaction — tools + git-history cross-check against `work_bind` records (unreferenced commits classified by `git show --name-only`: package-only writes cannot cite themselves) |
| `package-onboarding` | A cold agent meets the package from zero: charter → invariants → roadmap → state → obligations |
| `slice-kickoff` | Start the next open slice plan-first (STOP for approval, then AC-first execution) |
| `progress-sync` | Record completed work: progress entries, bindings, evidenced verdicts, typed scope changes |
| `defect-triage` | A bug surfaced: `DEF-` row BEFORE the fix, then fix/audit/bind/close the loop |
| `drift-register` | Work happened unrecorded: classify everything into DEF-/DW-/SC-first + progress/bindings |
| `slice-review` | Slice completion: `entity_export` the ACs first (a committed slate quotes the file), audit ACs with evidence, bind commits, `readiness_check("slice")`, stop at the gate |
| `phase-close` | Phase exit: phase-scope readiness blocking-clean, milestones, human GATE- confirmations, the guarded transition |
| `release-close-out` | Package-scope readiness blocking-clean, human gates recorded, export, notes, close |
| `replan-deferred` | Deferred-work triggers review: SC- first, activate, wire edges, STOP on new scope |
| `skill-promote` | Operator-run promotion interview: cluster Approved lessons → name/trigger/edge-cases/level → operator approves content → write the `SKILL.md` → `SKL-` row + `Promoted` flips (`operator_confirm`) |
| `register-liveness` | Readiness advisories piling up — the amber-list sweep, run on a cadence (incl. `amends` merges, Merged-last, and the note-budget promotion candidates) |
| `integrity-check` | Read-only audit: `package_verify` (the canonical round-trip, foreign files, digest), gates, counts, trace spot-checks, narrated + ungraded verdicts by id, rulings buried in closed rows, staleness + unbound commits — reads through the tool (`after_id`/`ids`/`search`), never the files |
| `generate-report` | Export + how to read `review.html` (nav, folded tables, freshness) |
| `loop-iteration` | Fully-auto: ONE unattended pass ending in the machine-parseable `ITERATION:` block |
| `loop-guard` | Fully-auto: the stop conditions — scope decisions and forced transitions always need a human |

They are trusted bundle content with no package-derived text, linted by check.py (lint 12:
well-formed, stack-neutral, no field identifiers, no `{package}` placeholder). The guide follows the
managed-emission sync model in `handoff.md`: re-emit refreshes, hand edits are detected and
refused, nothing is silently clobbered; a retired 4.x scenario file left in `<package>/prompts/` is
named by `handoff_emit` and deleted by `refresh_stock=true` only when byte-equal to a shipped
release. Project prompt files are operator-owned — never managed-refreshed, only screened.

## Wiring rules

- Replace every placeholder; a shipped prompt with an unfilled `<…>` is a G-HANDOFF failure.
- Reference entities by id (`FR-012`, `SL-003`) — the package is the source of truth; any
  file path a prompt names must exist (the stale scan flags dead relative links).
- List invariant IDs explicitly; don't paraphrase them loosely.
- State the stop/approval gate in every step that produces meaningful change.
