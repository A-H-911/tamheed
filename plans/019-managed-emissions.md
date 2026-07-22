# Plan 019 (B15): Managed emissions, ledger ergonomics, viewer consistency

## Status

**DONE (2026-07-22)** — four phases + release executed with `check.py` green at every
boundary; released as **v2.3.0**. Evidence: the third ACMP field report (the v2.2.0
re-migration — a clean regression pass, verdict "Ship it", zero repair loops; archived at
`evidence/acmp-field-report-3-2026-07-22.md`), clusters **C20** (emission lifecycle),
**C21** (ledger ergonomics + viewer consistency), **C22** (agent-control drift doctrine).
This report is also plan 018's acceptance evidence (every 2.1.0 finding fixed-and-verified
on real data).

Maintainer decisions (2026-07-22): no-status-column families default Approved + ledger
(DEC stays Proposed — governance invariant found in adversarial review) · viewer folds ALL
tables closed (exception, flagged and approved: gap/screening warn cards stay visible) ·
divergence policy = refuse + `force=true` · tripwire warns WITH suggested rewrites.
Adversarial review round 3 overturned a sub-agent classification: ACMP's agent-control files
restate registers in the GOOD form (labeled snapshots with references beside them) — the
tripwire distinguishes `unlabeled` from `labeled-snapshot` accordingly.

## What shipped (per phase, one commit each)

1. **Migrate ledger ergonomics (C21)** — no-status-column registers default to Approved
   (weak-def parity; DEC excluded) with the `status_defaulted` per-(file, family) ledger;
   grouped `status_coerced_groups` and `title_fallbacks` (the operator decision unit is the
   group — ACMP: 21 rows → 6 decisions, 131 fallbacks → 3 groups); `status_coerced_basis`
   annotation; contract rows for compound `status_map` keys and progress-log mapping.
   Golden regen: exactly the six pre-enumerated families
   (stakeholders/milestones/dependencies/invariants/risks/tests) Draft→Approved.
2. **Viewer uniform folding (C21)** — `_fold` helper; EVERY table closed `<details>` with
   count summaries ("1 row" singular): register families, package identity, coverage
   matrix, edge dump, AC×verdicts, progress log, scope changes. Gaps warn-cards never fold
   (they exist to be SEEN). Threshold logic removed.
3. **Managed emissions + drift tripwire (C20/C22)** — `_managed_emit`
   (emitted/unchanged/diverged; memoryless; refuse-without-force) over handoff prompts, the
   scenario library, and `.mcp.json`; the stale-v1 warning in a self-retracting marker
   block (re-run emit = standing cutover verifier); `restated_content` tripwire (≥3
   consecutive id-led lines or an audit tally) with `unlabeled` vs `labeled-snapshot`
   kinds and family-templated suggestions; forward-slash paths.
4. **Docs & evidence** — three-prompt-surface sync model (`handoff.md` + README +
   prompt-templates); "reference, don't restate" doctrine (+ state-once for
   AGENTS↔CLAUDE); `db/CANONICAL.md` byte-stability guarantee ("did anything change? is a
   `git status` question" — field-proven); SKILL migrate walkthrough uses the grouped
   confirmation; this evidence archive + alignment record.
5. **Release v2.3.0** — plugin.json + CHANGELOG (version-sync lint), tag.

## Verification

`check.py` green at every boundary (~150 tests incl. 11 new); Phase-1 golden diff matched
the pre-enumerated six-family list exactly (STOP rule untriggered). Release note: pre-2.3.0
stale-warning blockquotes (emitted without markers) need one hand removal. **Acceptance
(maintainer): the next ACMP `handoff_emit`** — everything `unchanged`, no stale warnings,
`restated_content` reporting only `labeled-snapshot` findings on the well-authored blocks,
hand-edited files refused.

## Rejected (do not re-audit)

Sidecar hash manifest for divergence provenance (state creep — memoryless refuse suffices) ·
cross-file AGENTS↔CLAUDE dedup detection (doctrine text) · DB-generating the AGENTS.md
project-state block (`agents_emit` — recorded future option) · synthesizing PE rows from v1
progress logs · DB-backing the scenario library.
