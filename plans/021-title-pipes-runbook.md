# Plan 021 (B17): Title resolution, escaped pipes, emit-scan closure

## Status

**DONE (2026-07-23)** — three phases, `check.py` green at every boundary; released as
**v2.5.0**. Evidence: the fifth ACMP field report (`evidence/acmp-field-report-5-2026-07-23.md`)
— the calmest of the cycle: the §7 re-populate+swap on v2.4.0 needed **zero blind repairs**,
revived `v_phase_exit` (51/41 + 9/9), and confirmed the fidelity-ledger direction "measurably
worked." Cluster **C26**. This report is also plan 020's acceptance evidence (8 of 11 §D
classes fixed outright, 2 disclosed, 1 now closed here).

Adversarial review round 5: B1's reported mechanism was wrong (column-order scanning, not a
missing alias — the suggested fix was a no-op) and the draft plan itself would have shipped a
regression (a Title column displacing a Statement column in long-form text — the D-0 class
reborn); both corrected pre-approval. Golden delta verified EMPTY post-change, as enumerated.

## What shipped (per phase, one commit each)

1. **Migrate fixes (C26/B1/B3 + §A residuals)** — two-pass title resolution (exact
   Title/Name column wins; long-form text resolved independently of the title column;
   id-shaped titles trigger the degenerate rescue); escaped in-cell pipes via sentinel
   substitution around the frozen parser (rows never shear); deferred-work v1 Status carried
   onto the DW enum (the recurring truth-up is gone); phase prose-status sections match by
   heading id OR phase title; migration-v1.md quirk 19 (incl. B2's shape-not-loss note and
   B7's status_map-replay caution); 5 tests; golden delta empty.
2. **Emit-scan closure + bundled runbook (C26/B4/B5/B6)** — diverged PRM rows' would-be
   bodies are scanned and reported marked "(not emitted: diverged)" (the promised signal now
   always fires; no double-reporting); `references/migration-runbook.md` ships in the bundle
   (staged run → cutover → §7 re-populate + the reverse-engineered swap mechanics + the
   force-re-emit-after-swap note), fixing the standing self-containment violation
   (migration-v1.md pointed outward; bundle-wide sweep found no others); SKILL index row;
   docs mirror updated; 1 test.
3. **Evidence + release** — findings_5 archived with the mechanism-correction header; C26;
   plans/README row + alignment record; CHANGELOG `[2.5.0]` + plugin.json (version-sync
   lint); tag v2.5.0.

## Verification

`check.py` green throughout (~172 tests, 6 new). Golden delta script empty after Phase 1
(STOP rule satisfied without regen). **Acceptance (maintainer): next ACMP touchpoint** — a
future re-populate shows Title-column epic titles, unsheared FR-100/107, carried DW statuses,
prose-resolved PH-0/PH-1; `handoff_emit` on the live repo reports the stale PRM-row findings
with the diverged marker without touching hand-authored files.

## Rejected (do not re-audit)

B7 semantic defaults for project-specific words (status_map replay + grouped ledger is the
designed path) · WBS leaf phase inheritance (disclosed via column_starvation) · auto-forcing
name-only library divergence (safe-by-default wins; runbook note instead) · packages.name
rename tool (cosmetic by verified design) · slice supersession helper for the 14 re-Approved
ACs (operator-accepted).
