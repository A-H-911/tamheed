# Plan 036 (B32): findings_19 + the confirm guard + lesson→skill promotion — v4.4.0

## Status

**DONE (2026-08-15)** — all seven phases executed, `python check.py` fully green,
`--selftest` green. Version stamped **v4.4.0** (MINOR — migration 003 is additive;
no break). *Release (push + GitHub release) happens only on the maintainer's
explicit words — this line records execution, not publication.*

## What this was

findings_19 (evidence **C40**) — the lesson feature's first field use — plus the
maintainer's second major lessons capability, locked across two interview rounds, a
clarification (the level question + the ECC research order), advisor, and the
devil's-advocate round (whose real catch: a guard covering only *transitions* is
trivially bypassable by inserting a row born Approved — the shipped guard covers
every landing path including birth).

The findings: §1 the v1-note classifier keyed on a bare heading and advised
deleting the section carrying the `@tamheed-package/CLAUDE.md` import — destructive
advice wrapped in a success-shaped no-op ("the tool's own hollow pass"); §2 the
lessons immutability trigger fired one write too late — the approval write itself
re-sends every content column unguarded; §3 FK failures named nothing.

The capabilities: (1) never-auto-confirm, MECHANICAL — even in auto mode; (2)
lesson→skill promotion in an interactive operator interview, project-level
(default) or user-level.

## What shipped

1. **The confirm guard** (closes findings_19 §2 as a side effect): entity_upsert
   refuses any write landing a lesson in Approved/Promoted from a different state
   — including birth — without `"operator_confirm": true`; the transition write
   must be byte-identical on content (drift refused naming the columns); approval
   requires `confirmed_by` on that write (the DDL-only rule, now enforced and
   stated); promotion requires stored-Approved + a real SKL- row; the server
   appends the typed `lesson-confirmed`/`lesson-promoted` event (actor
   system:lesson-guard) in the same transaction. Loops never carry the flag;
   the ITERATION line gains trailing `lessons_pending=<n>`.
2. **Migration `003_skills.sql`**: the `skill` family (SKL-, On-request, metadata
   only — the body lives solely in the written SKILL.md, operator-owned; level
   project|user default project; born Approved; superseded_by); lessons recreated
   (lifecycle gains Promoted; `promoted_to` FK; the immutability trigger's WHEN
   extends to Promoted + the promoted_to-freeze clause); progress_entries
   recreated (the two new event types). Ordering: skills before lessons (the FK).
3. **The promotion ceremony**: `skill-promote.md` (17th stock file) — cluster
   candidates → the operator interview (name, trigger, edge cases, THE LEVEL —
   asked every time, default project; pinned candidates warned about full
   graduation) → content approval → the agent writes the file → SKL- row +
   guarded Promoted flips. **Full graduation** (the maintainer's explicit choice,
   made with the missing-skill-on-clone trade surfaced): Promoted lessons leave
   the note; the "Skills distilled from lessons" line names each with its level
   and survives even when every lesson has graduated.
4. **findings_19 §1**: marker-based classification; the pointer pattern (heading +
   import line → the span rebuilds in the PACKAGE's CLAUDE.md, root untouched,
   both full paths named); true-v1 warning keeps full path + current wording.
   **§3**: FK failures name column, value, and referenced table.
5. **Surfaces**: viewer Promoted subsection + skills register + lane; catalog/
   governance/docs swept (the three-generation memory arc: episodic PE- →
   declarative LL- → procedural SKL-, per Soar/Voyager/ECC); register-liveness
   step 14 teaches the enforced flow; loop-guard's standing rule.
6. **The lab, beat 11** (real agent): the second registry-sync, the guard refusing
   VERBATIM ("a lesson binds future sessions only on the OPERATOR's words…never in
   unattended mode"), the scripted promotion interview with the level default, the
   project-level SKILL.md landing in the lab workspace, LL-001's statement GONE
   from the note with the skills line present, the server's `lesson-promoted`
   event (PE-012, actor system:lesson-guard) — and **the lab caught the eval spec
   AGAIN**: the 4.3.0 "≥1 Approved lesson" assertion became impossible once the
   only Approved lesson graduated (exactly the conformance class the 035 catch
   taught, from the other side). Fixed with the `nonempty-any` pkg_check
   primitive (evidence over state: `confirmed_by` survives graduation); both
   catches recorded in the assertion's check text. All 17 lab assertions green.

## Verification

`python check.py` green end-to-end (~16 new/extended tests incl. the guard
battery, the classifier trio, FK parity, migration 003, the graduation render);
the eval-spec lint replicated locally; `--selftest`; the lab agent's report as the
real-agent proof.

## Left open (operator-side, in the delivery prompt)

ACMP: upgrade → the second staged registry-sync (the skill type) → their natural
promotion candidate is LL-001 (paste-don't-retype) via the skill-promote interview
— level project recommended; their three customized prompts still lag (named by
the emission warning; hand-merge). The GitHub diagram-render confirmation now
covers the 036 diagram additions too.
