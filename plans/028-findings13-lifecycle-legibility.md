# Plan 028 (B24): findings_13 follow-ups — prompt lifecycle, readiness discrimination, flow legibility

## Status

**DONE (2026-08-13)** — three code phases + close-out, `check.py` green at every
boundary (~218 tests); released as **v3.1.0** (MINOR — new advisory surfaces, viewer
behavior, warning shapes, the library README; **no schema migration**). Evidence: the
thirteenth ACMP field report (`evidence/acmp-field-report-13-2026-08-13.md`, **C34**) —
the v3.0.0 acceptance run: "the MAJOR landed clean", and `readiness_check` caught a
prematurely-closed slice (SL-004, four never-evidenced ACs) that seven passing gates
structurally could not see. Plan preceded by the maintainer's prm-naming/overlap probe
(all converted files read and measured: ~50-70% restated generic workflow interleaved
with unique project knowledge — kills auto-delete AND auto-replace), a devil's-advocate
round, and two explicit interview rounds; full record in the approved plan file.

## What shipped

1. **Prompt lifecycle signals (§2 + the prm question)**: leftover `handoff/prm-*.md`
   warnings became per-file verdicts by content compare ("copy — safe to delete" vs
   "NOT a copy — MOVE it"; the blanket delete would have destroyed a live prompt);
   converted legacy prompts get a standing, self-clearing per-KIND curation hint
   (`converted_prompts` in every handoff_emit; clears on provenance-header removal —
   rename does NOT clear; the same hints ship at conversion in `curation`); the C22
   restated-state detectors now cover package prompt files (advisory — a converted
   prompt's hard-coded audit tally had drifted factually wrong); project-prompt NAMING
   guidance (purpose-named kebab-case; `prm-NNN-*` = audit identifiers, not a pattern).
2. **Operator User Guide** (maintainer ask): `prompts/README.md` ships INSIDE the stock
   library (library 14 → 15, managed like every stock file) — which prompt for which
   situation, the semi-auto day loop, the fully-auto loop-iteration/loop-guard pairing
   with the `ITERATION:` machine contract, naming/curation rules; the CLAUDE.md note
   points at it ("start with prompts/README.md").
3. **Readiness discrimination (§4)**: rules keyed on a column NULL for EVERY row of its
   type carry `discriminating: false` + a note ("0 of N rows have <col> set — cannot
   discriminate"); severity NOT downgraded (maintainer-locked, twice). Slice/phase
   `defects-closed` reports how many open defects have no `found_in` and are invisible
   to that scope (the DEF-057 blind spot) — without the flag (partial still counts).
4. **Flow legibility (§5)**: hover-isolate via CSS `:has()` in BOTH svgs (hidden `.hl`
   incident-edge copies per node group; zero JS; graceful degradation); isolated fold
   breaks down per family with isolated REQUIREMENTS sorted first + ⚠-prefixed; the
   flow lead names how many requirements the view cannot draw (they were exactly the
   unverified ones the picture hid).
5. **`requirements_unwired` (§7), BOTH surfaces**: gate_run advisory + package-scope
   readiness advisory rule (`requirements-wired`) for execution-created requirements
   with zero trace edges (the FR-156..159 class); drift-register + progress-sync gain
   the wire-in-the-same-session step (work_bind stamps commits, it does not wire
   traceability).

## Verification

`check.py` green each phase (~218 tests; 12 new/updated across the two suites).
Determinism, fold-count, and hostile-content invariants re-verified over the reworked
svgs. **Acceptance (maintainer): the next ACMP run on 3.1.0** — the converted_prompts
hints + restated-tally finding fire on the real prm files, the per-file leftover
verdicts match the operator's own §2 triage, hover-isolate answers "what connects to
what", requirements_unwired lists FR-156..159 until wired, and the §6 drift verdict
finally gets its clean unprompted session.

## Deferred / rejected (recorded)

- Auto-deleting/renaming/rewriting converted prompt files (preserve-and-signal is the
  doctrine; the section-matching cleanup helper was offered and declined).
- Auto-downgrading undiscriminating blocking rules (offered; maintainer kept blocking).
- Content-similarity overlap detection (precise-detector doctrine).
- Stale-lock auto-reclaim (§1 proved the operator-side two-discriminator check; PID
  reuse keeps it unsound).
- A drift verdict (§6) — needs the clean session, riding in the acceptance prompt.
