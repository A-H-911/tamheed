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

## The stock scenario library (plan 018, grown in plan 027)

Distinct from the project prompts above: sixteen files — fifteen ready-to-paste operator scenario
prompts plus the folder README — ship in the bundle (`../prompts/`) and are emitted verbatim (only
`{package}` substituted) into `<package>/prompts/` by `package_create`, `package_migrate`,
`package_adopt`, and `handoff_emit`. The authoritative per-file guide is the emitted
`prompts/README.md`; this file teaches AUTHORING project prompts:

| File | Scenario |
|---|---|
| `orient-resume.md` | Re-orient after a session clear/compaction — tools + git-history cross-check against `work_bind` records |
| `package-onboarding.md` | A cold agent meets the package from zero: charter → invariants → roadmap → state → obligations |
| `slice-kickoff.md` | Start the next open slice plan-first (STOP for approval, then AC-first execution) |
| `progress-sync.md` | Record completed work: progress entries, bindings, evidenced verdicts, typed scope changes |
| `defect-triage.md` | A bug surfaced: `DEF-` row BEFORE the fix, then fix/audit/bind/close the loop |
| `drift-register.md` | Work happened unrecorded: classify everything into DEF-/DW-/SC-first + progress/bindings |
| `slice-review.md` | Slice completion: audit ACs with evidence, bind commits, `readiness_check("slice")`, stop at the gate |
| `phase-close.md` | Phase exit: phase-scope readiness blocking-clean, milestones, human GATE- confirmations, the guarded transition |
| `release-close-out.md` | Package-scope readiness blocking-clean, human gates recorded, export, notes, close |
| `replan-deferred.md` | Deferred-work triggers review: SC- first, activate, wire edges, STOP on new scope |
| `register-liveness.md` | Readiness advisories piling up — the amber-list sweep, run on a cadence |
| `integrity-check.md` | Read-only audit: gates, counts, trace spot-checks, narrated verdicts, staleness + unbound commits |
| `generate-report.md` | Export + how to read `review.html` (nav, folded tables, freshness) |
| `loop-iteration.md` | Fully-auto: ONE unattended pass ending in the machine-parseable `ITERATION:` block |
| `loop-guard.md` | Fully-auto: the stop conditions — scope decisions and forced transitions always need a human |

They are trusted bundle content with no package-derived text; the relocated G-INJECT screen
scans them anyway at `handoff_emit` (tamper detection is free). Stock files follow the
managed-emission sync model in `handoff.md`: re-emit refreshes, hand edits are detected and
refused, nothing is silently clobbered. Project prompt files are operator-owned — never
managed-refreshed, only screened.

## Wiring rules

- Replace every placeholder; a shipped prompt with an unfilled `<…>` is a G-HANDOFF failure.
- Reference entities by id (`FR-012`, `SL-003`) — the package is the source of truth; any
  file path a prompt names must exist (the stale scan flags dead relative links).
- List invariant IDs explicitly; don't paraphrase them loosely.
- State the stop/approval gate in every step that produces meaningful change.
