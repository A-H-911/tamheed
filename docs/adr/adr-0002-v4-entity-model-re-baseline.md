---
status: Approved
date: 2026-08-14
id: ADR-0002
supersedes: ADR-0001 (partially — see Scope of supersession)
superseded_by: none
---

# ADR-0002 — The v4 entity-model re-baseline

## Status

Approved (maintainer, 2026-08-14 — fifteen decisions locked across five interview
rounds; plan 031). Recorded retrospectively at the plan-033 documentation audit, which
found the repo's biggest schema change had no ADR.

## Context

ADR-0001 established the v2 relational store: entities as SQLite-enforced rows,
canonical JSONL, the MCP server as the only write path, three-axis status, the frozen
v1 contract kept as the migration source. Two majors of field hardening (seventeen
ACMP field reports) exposed what the v2/v3 model could not express: an agent's *claim*
of done was indistinguishable from *verified* done; a gate with no waiver path was
bypassed informally; drift records never reconciled into the plan; the progress
journal was untyped prose; relation typing was advisory for stored data; registers
rotted because nothing nagged; and the v1 machinery being "frozen, kept for migration"
had become dead weight nobody could safely ingest through anyway. External research
(29148/EARS, MADR 4.x, PMI/ISO-31000 practice, RAID logs, the Google flaky-test
doctrine, stage-gate G/H/R/K, and the claimed-vs-verified consensus across
spec-kit/Kiro/Taskmaster/Ralph/OpenSpec) converged on the same gaps.

## Decision

Re-baseline the store as **v4** (the full decision table with rationale:
`docs/entities.md` §2; the release record: CHANGELOG `[4.0.0]`):

- `schema.sql` IS the v4 DDL (the migration chain reset; v2/v3 lineage lives in the
  migrate tool, not stacked ALTERs).
- **Claimed vs verified**: `Review` (done-claimed, wbs-items/slices, counts OPEN
  everywhere) vs `Implemented` (done-verified, readiness-guarded); audit verdicts
  carry the evidence chain (`verified_by`, `verification_method`, `against_commit`).
- **Gate hardening**: severity-thresholded defect blocking; operator-only `WVR-`
  waivers (reported `waived`, never silent, expiring); `Go/Hold/Redirect/Kill` gate
  outcomes; the relation sweep becomes the blocking **G-REL** gate.
- **Drift deltas**: scope changes live Proposed → Approved → `Merged`, with typed
  `scope_adds`/`scope_modifies`/`scope_removes` edges — reconciliation checkable,
  never automatic.
- **Typed journal**: past-tense `event_type` + `subject_id` + `actor` + compensating
  `corrects` events; journals are never edited.
- **Ambiguity as data**: `[NEEDS-CLARIFICATION: OQ-NNN]` markers, G-COMPLETE-validated
  against live open questions.
- **DEC/ADR stay two tiers** with the one-way-door promotion rule and the MADR
  `confirmation` field; milestones demote to roadmap labels; lightweight enrichment
  with liveness advisories instead of full standard column sets.
- **v1 ingestion retired**; migration is explicit (`package_open` refuses pre-v4
  stores; `package_migrate` is staged, previewed, backed up).

## Scope of supersession (what of ADR-0001 survives)

The v2 store doctrine SURVIVES and remains binding: canonical JSONL, the single write
path, derived-never-stored views, immutability-by-trigger, the three-axis status
model. What ADR-0001 says about the `prompts` table, the milestone lifecycle, and the
"v1 templates/schemas frozen as the migration source contract" is superseded by this
record.

## Consequences

Positive: an agent cannot self-certify done; gates have a legal escape valve;
approved drift must land in the plan rows; the journal is mechanically
cross-checkable; every v4 package starts relation-clean. Costs: every golden and
fixture regenerated; live packages must migrate explicitly (ACMP did, findings_17:
clean first-try); the teaching surface had to be re-swept — and its rot drove the
plan-033 lint expansion.

## Confirmation

`python check.py` is the fitness function: the suites pin the claimed-vs-verified,
waiver, drift, journal, marker, and G-REL semantics; the sync lints pin the registry ↔
catalog ↔ DDL ↔ teaching surfaces; the migration suite pins the v3→v4 transform
byte-deterministically; the lab package (`evals/sample-results/lab-tracker`) re-proves
every mechanism against a recorded agent run on each release.
