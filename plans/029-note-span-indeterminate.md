# Plan 029 (B25): findings_14 fixes — tool-owned note span, honest force, indeterminate readiness

## Status

**DONE (2026-08-14)** — two code changes + close-out, `check.py` green (~221 tests);
released as **v3.2.0** (MINOR — the note-span contract change and the new
`indeterminate` status value are observable behavior; **no schema migration**).
Evidence: the fourteenth ACMP field report
(`evidence/acmp-field-report-14-2026-08-14.md`, **C35**) — the v3.1.0 acceptance:
every §2/§4/§5 recommendation verified working, two real defects, one design nit.
All forks locked by maintainer interview (rebuild+warning; indeterminate
non-blocking; no force scoping; 3.2.0).

## What shipped

1. **N1 — the note span is TOOL-OWNED** (the stale-warning-block precedent): the
   `<!-- tamheed:note v2 -->` span is rebuilt on EVERY `handoff_emit` — no force, no
   `diverged` bookkeeping; `CLAUDE.md` lands in `written` when the content moved, and
   a hand edit inside the markers is overwritten WITH a warning ("keep operator
   content OUTSIDE the markers"). The v3.1.0 code contradicted its own warning text
   ("self-updates thereafter") AND coupled the note update to a prompt-clobbering
   force — the operator quoted the code back at us. Content outside the markers is
   never touched (test-proven).
2. **N2 — force means one thing**: overwrite ALL diverged stock prompt files
   (+ `.mcp.json`). The destructive coupling dissolved with N1; force scoping was
   offered and declined. New guidance warning when stock divergences exist: the two
   divergence kinds (operator customisation vs template-moved-on) are
   indistinguishable without history; **per-file template acceptance = delete the
   file and re-emit** — a zero-machinery path that already existed, now named.
3. **N3 — `indeterminate` status**: a readiness rule with `discriminating: false`
   whose query found nothing reads `indeterminate`, never `pass` ("cannot measure" ≠
   "verified clean"). `ready` and the transition guard trip only on real `fail`
   (maintainer decision — non-blocking); the loud all-null-fail case
   (`risks-discharged` firing on every risk) stays `fail`.
4. Close-out: evidence C35 (header records: OUR acceptance prompt's OQ-flag
   expectation was wrong — the tool discriminated correctly on 5/76; the ⚠-first
   isolated-requirement ordering the operator couldn't field-verify is mechanically
   verified in-repo); docs (handoff.md span contract, server README, quality-gates
   status vocabulary); CHANGELOG `[3.2.0]`; plugin.json. 3 tests rewritten/new.

## Verification

`check.py` green (~221 tests). The rewritten note test proves: identical → unchanged
+ no warning; hand-edit inside markers → rebuilt without force + warning + outside
content preserved; never diverges. **Acceptance (maintainer): the next ACMP run on
3.2.0** — `handoff_emit` updates the note to current content with zero force and zero
prompt clobbering, the stock-divergence warning names the per-file path, slice
readiness reads `indeterminate` where it read a false green — and the §6 drift
session finally runs against a current note.

## Deferred / rejected (recorded)

- `force="note"` / per-file force scoping — declined at interview; the motivating
  coupling dissolved and delete+re-emit covers per-file acceptance.
- Blocking on indeterminate — declined at interview; amber, not red.
- Carried to the ACMP prompt (no tamheed change): §2 converted-prompt curation + the
  README verdict; the §6 clean unprompted drift session.
