# Plan 030 (B26): findings_15 follow-up — the README indexes the folder; the README contract

## Status

**DONE (2026-08-14)** — docs + one lint + close-out, `check.py` green (~221 tests, 8
lints); released as **v3.2.1** (PATCH — documentation + a lint; no code behavior, no
schema). Evidence: the fifteenth ACMP field report
(`evidence/acmp-field-report-15-2026-08-14.md`, **C36**) — the v3.2.0 acceptance: all
three findings_14 negatives fixed and verified; the curation done; **instruction
transfer proven** for the obligations note (a delegated agent, told nothing, cited the
package's own ids and named every obligation) with autonomous discharge honestly left
to the one remaining instrument — a genuinely fresh primary session. Plan preceded by
an interview (4 locks) and a devil's-advocate round that grew the README sweep from ~8
to ~11 verified-stale spots.

## What shipped

1. **prompts/README.md** (the one tamheed defect in C36): a closing table row so a
   table-scanner discovers project prompts ("any other .md here — operator-authored,
   purpose-named; read the folder"), and a **"One session at a time"** section — the
   single-writer lock, what a refusal names (pid/host/taken_at), and the
   field-validated two-discriminator stale-lock check (live pid that plausibly IS an
   agent session AND started before `taken_at`); never auto-clear.
2. **Root README.md — full v3 sweep** (11 spots, each verified stale by direct read):
   badge v2.0→v3.2.1; the "five prompts" paragraph → prompts-as-files + the 15-file
   library + folder guide; the handoff paragraph → the v3.2 note-span/force contract,
   obligations table, transition guard, typed relations; the review.html paragraph →
   flow view, hover-isolate (with the `:has()` caveat), readiness panel; tools table
   + `readiness_check`; the mermaid OUT node ("handoff prompts" → "prompts/");
   repo-structure tree gains `prompts/` and `db/migrations/`; seven/7 suites → ten;
   Maturity → v3.x with the field-hardening lineage and the README contract.
3. **server/README.md**: version line ("documents the tool surface as of v3.2.1").
4. **The README contract, lint-enforced** (maintainer standing instruction): check.py
   lint #8 — all three READMEs must contain the current plugin version string; a
   release that skips one fails the gate (the version-sync-lint precedent).
   Deliberate side effect (interview-locked): the versioned prompts/README diverges
   package copies each release — that IS the guide-update delivery signal via the
   documented delete+re-emit path.
5. Recorded, not planned: DEF-064 + the value-level i18n guard (ACMP-side); lock
   mechanics unchanged (the no-auto-reclaim doctrine keeps proving itself); the
   fresh-session drift instrument (operator-side, rides in the ACMP prompt).

## Verification

`check.py` green (lint 8 live — the release could not have shipped with a stale
README). Three new README test needles. Sweep verification: every rewritten sentence
cross-checked against CHANGELOG 3.0.0–3.2.1 + source; no claims past shipped behavior.
**Acceptance (maintainer): the next ACMP run on 3.2.1** — delete `prompts/README.md`
+ re-emit (the per-file template-acceptance path, first real field use), confirm the
folder row + lock section render, then the genuinely fresh primary-session drift test
(the ONLY remaining open verdict). → **Acceptance MET (findings_16/C37, same day):
steps 1–2 clean — the per-file path field-proven, both additions render, the lock
section judged faithful. Zero defects; close-out only, no release.**

## Deferred (post-acceptance, findings_16)

- **Lock-section wording** (ships with the next release; C37 phrasing note, not a
  defect): "Only when both say stale, delete" is stricter than the logic requires —
  rewrite to "delete when EITHER discriminator proves staleness (identity failure =
  pid reuse; ordering failure = the process cannot be the holder); keep the lock only
  when both checks pass." The current wording errs toward not-deleting — safe
  meanwhile.
- §6 drift discharge: the interactive fresh session remains the only valid
  instrument (headless permission modes block the tool path; delegated agents
  correctly defer) — operator-side, no tamheed change.
