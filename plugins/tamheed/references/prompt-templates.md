# Handoff prompt templates

Operational guidance for writing the three prompt kinds. Blank fill-in forms live in
`../templates/initial-prompt.template.md`, `follow-up-prompts.template.md`, and
`review-prompts.template.md`. Write prompts for Claude Code (CLI/IDE) and reference real artifacts by
path; keep the plan's technology choices vendor-neutral. Use Claude Code affordances — plan mode,
TodoWrite, subagents, a code-review pass — where they help, named as capabilities, not hard dependencies.

## Initial prompt — shape

```
This repo contains the APPROVED plan for <project>. You are starting implementation.
<one-paragraph orientation: what the project is, where the plan lives, that decisions are final>.

Step 1 — Orientation (use plan mode; no code): read <list the few key plan docs>. Then give me:
(a) a ≤1-page summary of what you'll build and the invariants you must respect [list INV- ids];
(b) your execution plan for Phase <PH-1> with file layout and PASS/FAIL per task.
STOP and wait for my approval.

Step 2 — <first bounded task> (after approval): <one concrete deliverable with PASS/FAIL>; track the backlog with TodoWrite. Pause for review.

Rules: respect the invariants; pin versions; record deviations as ADRs; don't expand scope beyond Phase 1.
Prerequisites: <runtimes/accounts/versions>.
```

The initial prompt must (1) orient, (2) give one bounded task, (3) stop at an approval gate. It never
authorizes building the whole system at once.

## Follow-up prompts — shape

One per phase gate. Each: resume context ("Phase <N-1> is complete and approved; its exit criteria were
…"), the phase goal, the bounded tasks with PASS/FAIL, the invariants still in force, and the exit gate.
Plus situational prompts: fallback-invocation, fresh-session refresher, invariant audit, engine/dependency
upgrade + baseline regen, bug triage, release prep, deviation ADR, status report.

## Review prompts — shape

Prompts that make Claude Code (or a human) check work against the plan — a code-review pass (e.g.
`/code-review`) where available: invariant audit ("verify the
implementation honors `INV-001..INV-00n`; report violations with file:line"), readiness recheck ("re-run
the quality gates against the current repo"), and PR review against acceptance criteria.

## The emitted scenario library (plan 018)

Distinct from the three PRM- kinds above: five ready-to-paste operator prompts ship in the
bundle (`../prompts/`) and are emitted verbatim (only `{package}` substituted) into
`<package>/prompts/` by `package_migrate`, `package_adopt`, and `handoff_emit`:

| File | Scenario |
|---|---|
| `orient-resume.md` | Re-orient after a session clear/compaction — tools + git-history cross-check against `work_bind` records |
| `progress-sync.md` | Record completed work: progress entries, bindings, evidenced verdicts, typed scope changes |
| `integrity-check.md` | Read-only audit: gates, count totals, trace spot-checks, narrated verdicts, staleness vs git |
| `generate-report.md` | Export + how to read `review.html` (nav, folded tables, freshness) |
| `slice-review.md` | Slice/phase completion: audit ACs with evidence, bind commits, close out, stop at the gate |

They are package artifacts for the *operator and executing agent*, not PRM- rows — no
G-INJECT screening needed (trusted bundle content, no package-derived text).

## Wiring rules

- Replace every placeholder; a shipped prompt with an unfilled `<…>` is a G-HANDOFF failure.
- Reference artifacts by relative path that exists in the package.
- List invariant IDs explicitly; don't paraphrase them loosely.
- State the stop/approval gate in every step that produces meaningful change.
