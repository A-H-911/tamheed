# Plan 006 (B7): Deliverables review — decide the v2 artifact set (USER APPROVAL GATE)

> **Executor instructions**: This is a DESIGN plan. Its deliverable is a decision document the
> **maintainer approves before plan 007 (B2) may start**. Do not modify any existing repo file
> except to add the deliverable. Present the proposal to the maintainer and STOP for approval —
> approval here is a hard gate, not a formality.
>
> **Drift check (run first)**: you must be working in the **tamheed repository** (plan 005
> bootstrapped it; Track B executes there). Confirm `plugins/tamheed/references/artifact-catalog.md`
> exists in your working tree. If the bundle is still `plugins/keystone/` or you are in the old
> keystone repo, plan 005 has not landed / wrong repo — STOP.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: LOW (paper only)
- **Depends on**: plans/005-b1-rename-to-tamheed.md
- **Category**: direction / design
- **Planned at**: commit `0e055f6`, 2026-07-11

## Why this matters

Plan 007 (B2) turns every package deliverable into relational entities. Modeling is expensive to
redo, so the artifact set must be *decided* before it is *modeled* — otherwise v1's inventory gets
entity-modeled by inertia, including artifacts the maintainer would have merged or dropped. The
maintainer explicitly requested this review: "for the package deliverables, I want to review them
and suggest enhancements/enrichments/adding/removing/updating."

## Current state

- The authoritative v1 catalog: `plugins/tamheed/references/artifact-catalog.md` (~45 artifact
  rows across Understand/Research/Architecture/Risk/Planning/Validation/Progress/Handoff groups,
  each with ID prefix, location, generation class Always/Conditional/Derived/On-request,
  lifecycle note, template, schema).
- The Always class (16 entries): `plugins/tamheed/references/required-artifacts.json` mirrors
  `artifact-rules.md`'s "Always" section.
- Selection logic: `plugins/tamheed/references/artifact-rules.md` (profiles bias selection).
- Real-world usage evidence: `generated-samples/support-triage-agent/manifest.json` — its
  `omitted_artifacts[]` reasons are *evidence of which artifacts real packages skip* (e.g.
  milestones "captured inline in roadmap", stakeholder register "captured in the charter",
  execution backlog "adds no operational value at this size").

## Deliverable

One new file: `plans/deliverables-review.md` (lives next to the plans; it is a decision record,
not a plan). For EVERY artifact in the catalog, one row:

| Artifact | v1 class | Proposal (keep / merge-into X / drop / restructure / add-new) | Rationale (≤2 sentences) | v2 entity impact |

**PRE-APPROVED by maintainer 2026-07-17** (interactive interview) — these seven rows enter the
review table as decided; the review rounds SKIP them:

1. **Merge milestones into roadmap** — the demo already records milestones inline
   (`omitted_artifacts`: "captured inline in planning/roadmap.md").
2. **Drop the standalone stakeholder register** — charter's stakeholder table covers it; demo
   omitted it too. (Note: the STK- *entities* keep a first-class table per plan 007 — the
   document dies, the data lives.)
3. **Formalize a defect log** — the v1 handoff follow-up prompts already imply defect tracking;
   make it a first-class Conditional artifact (entity: `defects`).
4. **Formalize a phase-exit report** — same evidence base (situational prompts mention
   phase-exit summaries).
5. **Promote acceptance-audit to Always during execution** — today Conditional; in v2 the
   execution-tracking loop is central (progress sync in `update` mode).
6. **Merge Definition-of-Ready / Definition-of-Done / checkpoints** into a single
   "execution gates" artifact — three thin Conditional docs in v1; demo omitted all three with
   one shared reason.
7. **Re-examine `execution/backlog.md`** — decided: the backlog IS a query over `wbs_items` —
   a view, not a stored artifact.

**FIELD-EVIDENCE SEEDS (2026-07-17)** — from forensic analysis of three real Keystone
deployments (acmp, opencode/"Marid", tarseem); present these in the review rounds WITH their
evidence:

8. **First-class deferred-work / tech-debt register** — ALL THREE projects hand-rolled one
   outside the ID scheme (acmp `D-01..22` — its most active governance surface; Marid's
   11-item deferred-work register with severity + invariant-at-stake; tarseem `TD-` +
   backlog.md). The strongest convergent signal in the corpus. Entity: `deferred_work`
   (severity, activation trigger, invariant-at-stake FK, status incl. Won't-do).
9. **Two-level roadmap: phase → slice** — every project invented finer execution granularity
   under the PH- phases (acmp's P1–P19 "build-slice ladder"; Marid ran on WBS; tarseem on
   spikes). Slices are what branches/PRs/ACs actually bind to.
10. **Risk register gains a lifecycle** — tarseem shipped v1.0.0 with 29 risks still stamped
    "Draft for approval" and no open/mitigated/materialized/retired state; acmp's RISK- family
    had zero commit references.
11. **Per-register right-sizing, evidence-based** — commit-reference data per repo (present it,
    don't prescribe: WBS heavily used in Marid, unused in acmp; FR/AC near-zero commit
    references in all three while ADR/DEC/OQ were load-bearing).

Also cover: which artifacts become **narrative documents** (charter, exec summary, architecture)
vs **register entities**; the **profile taxonomy** (maintainer 2026-07-17: v1's five profiles —
enterprise, rnd, legacy, ai-agentic, unknown — carry as-is; one review round confirms or amends);
and note that `tests`/`kpis`/`pocs`/`stakeholders` tables are already confirmed (maintainer
2026-07-17) — no review needed there.

**Presentation format (maintainer 2026-07-17): interactive taps rounds** — batched multi-select
questions, pre-approved rows skipped, decisions recorded live into `plans/deliverables-review.md`.

## Steps

1. Read the catalog + artifact-rules + demo manifest end to end; build the full table.
2. Mark each row keep/merge/drop/restructure with rationale grounded in catalog text or demo
   evidence (cite the line).
3. Present the table to the maintainer (in-session or as the committed file) — collect
   approve/modify per row.
4. Record the approved set in `plans/deliverables-review.md` with an "APPROVED by maintainer on
   <date>" header, and update this plan's row + plan 007's "Depends on" note in `plans/README.md`.

**Verify**: the file exists, every catalog artifact appears exactly once, every row carries a
maintainer decision (no "TBD" rows — that is a G-COMPLETE-style standard applied to ourselves).

## Done criteria

- [ ] `plans/deliverables-review.md` exists, covers 100% of catalog rows, zero undecided rows
- [ ] Header records explicit maintainer approval + date
- [ ] `plans/README.md` rows updated (this plan DONE; 007 unblocked)

## STOP conditions

- Maintainer approval not obtained — plan 007 must NOT start.
- The catalog on disk diverges materially from the ~45-row structure described above.

## Maintenance notes

- This decision record is the input contract for plan 007; if the set changes later, it changes
  through a scope-change decision in the v2 flow, not by editing this file silently.
