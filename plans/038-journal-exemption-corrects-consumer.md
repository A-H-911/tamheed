# Plan 038 (B34): findings_21 — the journal exemption + corrects' first consumer — v4.4.2

## Status

**DONE (2026-08-20)** — `python check.py` fully green, `--selftest` green. Version
stamped **v4.4.2** (PATCH — gate-scope fixes + a viewer consumer; no schema change,
no new tool). *Release only on the maintainer's explicit words.*

## What this was

findings_21 (evidence **C42**): a content gate over an append-only journal had no
repair path. The operator's note explaining which tokens G-COMPLETE screens became
the only row breaking it — permanently (upsert refused, no delete, the suggested
correction path inert: `corrects` was written and displayed but never read).
`gate_run` red forever; DEF-093 High; a written convention training readers to
skim a red gate. The report's reproduction quality (the real screen over 16903
cells, both controls, "please do not read this as a request to loosen the screen")
set the program's bar.

Maintainer-locked: exempt the journal report columns + give `corrects` its
consumer in the viewer (the corrects-join alternative declined — dead under
exemption, unreachable for the evidence twin, a self-service mute vector);
redaction DEFERRED to the first field need (recorded).

## What shipped

1. **G-COMPLETE exemptions**: `progress_entries.entry` + `audit_verdicts.evidence`
   join custom_attributes (the C14 reasoning extended — a report of what happened
   is never "unfinished"; the untested evidence twin now test-pinned), and the
   scan skips Superseded/Obsolete rows — **the DA round's trap-class completion**:
   immutable-after-approval content was the third instance, where supersession
   left the old row failing forever. Live entity prose stays fully screened;
   G-INJECT untouched.
2. **`matched` in every placeholder failure** (§3) — the failure names WHAT, and
   the screen is documented where an agent meets it (entity_upsert's docstring
   with the backtick escape; progress_update/audit_record's exemption notes; the
   G-COMPLETE teaching row; the prompts README standing rules).
3. **`corrects`' first consumer** (§2): review.html moves corrected entries into
   a collapsed "Corrected entries (superseded)" fold annotated with the
   corrector; corrections stay in the timeline; chains compose per-row.
4. Also: the prompts README's harness bullet caught carrying the pre-036
   ITERATION line (no lessons_pending) — synced.

## Verification

check.py green end-to-end (111 contract + 33 viewer tests incl. the new
journal-exemption/matched/supersession-repairs battery and the fold test; all
lints incl. the roster append); `--selftest`. The ACMP shape re-proven in-test: a
journal row with bare markers passes while a live entity row fails naming the
token, and superseding the entity row makes the gate green again.

## Left open

Redaction (`progress_redact`) — deferred, recorded in plans/README future
options. ACMP-side: upgrade → the gate goes green with zero data changes →
DEF-093 closes on the operator's words → the kickoff warning convention retires.
