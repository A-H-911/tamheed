# Handoff prompt templates

Operational guidance for writing the project's prompt **rows**. Since v6 (plan 196) a prompt is a
`prompt` row of the package (`PRT-`) with a `kind`. A `kickoff` is the one row the header's
`entry_point` names. A `phase` row is one per phase gate, with `phase_id` set. A `situational`
row is bound by `plugin_skill` to the bundled scenario skill that reads it. The operator approves a row before an
agent reads it, and Approved rows are edited in place. `handoff_emit` G-INJECT- and stale-scans
every Approved row. The three shapes below are the **bodies** of those rows. Blank fill-in forms
live in `../templates/initial-prompt.template.md`, `follow-up-prompts.template.md` and
`review-prompts.template.md`. Write prompts for Claude Code (CLI/IDE) and reference real entity
ids. Keep the plan's technology choices vendor-neutral. Use Claude Code affordances (plan mode,
TodoWrite, subagents, a code-review pass) where they help, named as capabilities, not hard
dependencies.

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

One per phase gate. Each has a resume context ("Phase <N-1> is complete and approved. Its exit criteria
were …"), the phase goal, the bounded tasks with pass/fail, the invariants still in force, and the
exit gate. Plus situational prompts: fallback-invocation, fresh-session refresher, invariant audit,
engine/dependency upgrade + baseline regen, bug triage, release prep, deviation ADR, status report.

## Review prompts — shape

Prompts that make Claude Code (or a human) check work against the plan, with a code-review pass (for
example `/code-review`) where available. The shapes are an invariant audit ("verify the implementation
honors `INV-001..INV-00n`, report violations with file:line"), a readiness recheck ("re-run the quality
gates against the current repo"), and a PR review against acceptance criteria.

## The scenario skills (plan 018, grown in plan 027, skills since v5, plan 116)

Distinct from the project prompts above: seventeen operator-invoked scenario skills ship in the bundle
(`../skills/<name>/SKILL.md`, `disable-model-invocation`). They are invoked as `/tamheed:<name>`, with an
argument naming another package, and are updated with the plugin, never emitted per project. Only the
operator guide (`<package>/README.md`) is still emitted, `{package}` substituted, by `package_create`,
`package_migrate`, `package_adopt`, and `handoff_emit`. It is the authoritative situation map. This
file teaches AUTHORING project prompts:

| Skill | Scenario |
|---|---|
| `orient-resume` | Re-orient after a session clear/compaction: tools + git-history cross-check against `work_bind` records. Unreferenced commits are classified by `git show --name-only` (package-only writes cannot cite themselves) |
| `package-onboarding` | A cold agent meets the package from zero: charter → invariants → roadmap → state → obligations |
| `slice-kickoff` | Start the next open slice plan-first (STOP for approval, then AC-first execution) |
| `progress-sync` | Record completed work: progress entries, bindings, evidenced verdicts, typed scope changes |
| `defect-triage` | A bug surfaced: `DEF-` row BEFORE the fix, then fix/audit/bind/close the loop |
| `drift-register` | Work happened unrecorded: classify everything into DEF-/DW-/SC-first + progress/bindings. A commit whose whole content is a package write is unbound by rule, never an orphan |
| `slice-review` | Slice completion: `entity_export` the ACs first (a committed slate quotes the file), audit ACs with evidence, bind commits, `readiness_check("slice")`, stop at the gate |
| `phase-close` | Phase exit: phase-scope readiness blocking-clean, milestones, human GATE- confirmations, the guarded transition |
| `release-close-out` | Package-scope readiness blocking-clean, human gates recorded, notes, bind, export, close |
| `replan-deferred` | Deferred-work triggers review: SC- first, activate, wire edges, STOP on new scope |
| `skill-promote` | Operator-run promotion interview: cluster Approved lessons → name/trigger/edge-cases/level → operator approves content → write the `SKILL.md` → `SKL-` row + `Promoted` flips (`operator_confirm`) |
| `register-liveness` | Readiness advisories piling up: the amber-list sweep, run on a cadence (incl. `amends` merges, Merged-last, and the note-budget promotion candidates) |
| `integrity-check` | Read-only audit: `package_verify` (the canonical round-trip, foreign files, digest), gates, counts, trace spot-checks, narrated + ungraded verdicts by id, rulings buried in closed rows. Also staleness (an export to a path outside the repository) + source-touching commits with no binding. It reads through the tool (`after_id`/`ids`/`search`), never the files |
| `generate-report` | Export + how to read `review.html` (nav, folded tables, freshness) |
| `loop-iteration` | Fully-auto: ONE unattended pass ending in the machine-parseable `ITERATION:` block |
| `loop-guard` | Fully-auto: the stop conditions. Scope decisions and forced transitions always need a human |
| `ste-rewrite` | Rewrite the record's prose into plain English, batch by batch (STOP per batch, immutable rows superseded, v5.9) |

They are trusted bundle content with no package-derived text, linted by check.py (lint 12:
well-formed, stack-neutral, no field identifiers, no `{package}` placeholder). The guide follows the
managed-emission sync model in `handoff.md`: re-emit refreshes, hand edits are detected and
refused, nothing is silently clobbered. A retired 4.x scenario file left in `<package>/prompts/` is
named by `handoff_emit` and removed by `refresh_stock=true` only when byte-equal to a shipped
release. Project prompt rows are operator-approved: never managed-refreshed, only screened.

## Wiring rules

- Replace every placeholder. A shipped prompt with an unfilled `<…>` is a G-HANDOFF failure.
- Reference entities by id (`FR-012`, `SL-003`). The package is the source of truth, and
  `prompt-ids-resolve` names every id in a prompt row that resolves to no entity.
- List invariant IDs explicitly. Do not paraphrase them loosely.
- State the stop/approval gate in every step that makes a meaningful change.
