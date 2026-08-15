# Plan 034 (B30): findings_18 — the hollow-pass fix + customization-lag visibility (v4.2.1)

## Status

**DONE (2026-08-15)** — all four phases executed, `python check.py` fully green,
`--selftest` green. Version stamped **v4.2.1** (PATCH — a rule-honesty fix, a report
enrichment, teaching; no schema change). *Release (push + GitHub release) happens only
on the maintainer's explicit words — this line records execution, not publication.*

## What this was

findings_18 (evidence **C39**, `plans/evidence/acmp-field-report-18-2026-08-15.md`) —
the ACMP run of 4.2.0. The findings_17 repairs all verified closed in the data (OQ
amber 72→1 exactly [OQ-074]; scale 23/23 from the stash; titles recovered; zero stash
loss). Two findings and one operator lesson:

- **§3 (the tamheed defect):** `risk-liveness` had passed HOLLOW — its na guard
  covered `owner` only, so a universally-unpopulated scale made the high-predicate
  unfireable and the empty result read as health. The moment the operator populated
  the scale, the rule fired for the first time and named six real exposures.
- **§2 (the structural gap):** customizing a stock prompt silently and permanently
  opts it out of `refresh_stock`; ACMP's three customized prompts lag their moving
  stock with no visibility.
- **§1 (the operator's own catch):** a by-hand transcription of a correctly generated
  repair payload corrupted RISK-012; their independent post-write verifier caught it
  in one line. The sharpened doctrine: paste, never re-type; end every multi-row
  repair with an independent re-derivation.

Interview locked: Option A (report field + warning, no marker convention), 4.2.1
PATCH, teaching incl. the integrity-check step. The devil's-advocate round added the
candidate-row scoping on the guard, the pi_na message precedence, the
scratch-package test isolation, the exact consumer list for the shape change
(verified by key-name AND warning-string greps), and the `risk_state` NOT NULL
verification that completed the sweep claim.

## What shipped

1. **The guard** (`tamheed_server.py`): `pi_na` — 0 of N open/materialized risks with
   probability or impact set → `discriminating: false` + `indeterminate`, note naming
   the scale and governance.md; scoped to the rule's candidate rows; takes message
   precedence over the owner note. One staged contract test pins all four cases
   (hollow → indeterminate; retired-scale-doesn't-mask; one high row → fail naming
   it; populated medium/low → clean discriminating pass).
2. **The lag surface**: `diverged_customized` entries are now
   `{"file", "stock_last_changed"}` (semver-sorted newest history key; None without
   history — degrades honest); the CUSTOMISED warning names the moved files with the
   honest conditional and keeps the two test-pinned phrases verbatim. Both shape
   assertions and the warning test updated.
3. **Teaching (C39)**: catalog + prompts/README repair doctrine gains both new halves;
   prompts/README states the opt-out warning + the hand-merge path; integrity-check
   gains step 8 (verify any recent repair by independent re-derivation; fix nothing);
   register-liveness names the scale prerequisite. Three roster appends under 4.2.1.

## Verification

`python check.py` green end-to-end (100 contract tests incl. the new staged
hollow-pass test and the two updated shape tests; all 11 lints incl. roster currency;
canonical; evals); `uv run … --selftest` green.

## Left open (operator-side, returned in the close-out prompt)

DW-027 close · DW-026 build-or-carry · OQ-074 · owners for the SIX risk-liveness rows
(the rule's first real firing sharpened findings_17's twelve down to six) · the 20
unbound ACs · the slice-review hand-merge call (the new lag warning names it) · the
STILL-OPEN plan-033 acceptance line: confirming the entities.md diagrams render on
GitHub.
