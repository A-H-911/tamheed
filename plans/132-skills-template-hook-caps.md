# Plan 132: the sixteen and the forty-four rules, the template's pointer, the hook's caps (FB-025, R10–R12, R14)

> Maintainer-executed, 2026-09-26. Batch map: [129-135-batch-findings-33.md](129-135-batch-findings-33.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: LOW (prose in skill files under lint 12; one constant; one template section)

## Why this matters

FB-025: the operator retired all eight project twins behind the plugin's skills, and a pairwise read
found 16 procedural rules the twins lack (measurement-evidence 8, written-claims 6,
reading-the-record 2). The prm-next.md diet filed 113 more carried rules as Proposed lessons; a
classification against the eight skills (every candidate then re-read at the file) found 36 already
covered, 33 project-specific, and 44 generic gaps — R14 absorbs the verified ones, one sentence each.
R10: the AGENTS template shipped a twin of the note's obligations table (the restated shape the scan
reports; ACMP's AGENTS.md had none). R11: the hook printed 25 lines / 2,000 characters while the
skill said "under 40 lines" — a 12-line field handoff was already 1,735 characters. R12: a field
close-out left its handoff commit unbound because nothing said a bind is a `note`.

## What changes

- `resume_hook.py`: `ENTRY_CHARS = 4000` (= `_RESUME_ENTRY_CAP`; the marker now comes from the
  block's own `truncated`). New `test_entry_char_cap_follows_the_resume_block`.
- `session-handoff`: "under 25 lines and 4,000 characters"; the close-out order — status moves
  (feedback, skills: engine transitions that count against `handoff-current`) → handoff LAST →
  commit → `work_bind` (a `note`; the handoff stays current).
- `templates/agent-control.template.md`: the table section becomes a pointer at the tool-owned
  note; the handoff sentence stays. `test_note_obligations_match_agent_control_template` re-aimed
  (no obligation row in the template; the pointer sentence present). `references/handoff.md`.
- FB-025's 16, written from the retired files at ACMP `c85e68d8` (never from the FB's fragments),
  anonymised per lint 12: `measurement-evidence` step 6 (8 rules); `written-claims` step 4 (+ the
  build-time sweep by name: acceptance-criterion exclusions as owed supersessions; the source-tree
  grep) and step 9 (the predicate's members; widening the comment is not fixing the class);
  `reading-the-record` step 7 (constraint-first shortlist; reproduce a bundled property separately).
- The verified generic gaps (plan §5.4): `written-claims` step 8 (the live surface: status,
  negative, hedged count, ordinal, moving list, restored table; commit message vs live file;
  satisfaction judgement in a verdict row; id/commit/digest over a regenerated path), step 5 (a
  ruling falsifies prose that reasons from the old state — grep the id AND the advisory name, ship
  in the ruling's commit, every artefact in one batch), step 1 (attribution); `operator-interview`
  step 2 (absent reason; per-item verdicts), step 6 (re-put only on a moved premise);
  `ci-evidence` step 1 (every workflow; `cancelled`), step 4 (early-stopped job; checkout ≠
  environment; one change at a time), steps 6 (signature) and 7 (recording a red);
  `measurement-evidence` §3 (singular over plural); `test-evidence` §6 (local race fix), §7
  (coverage ≠ calls); `reading-the-record` (what binds is the note's roster); `package-writes` §5
  (unexplained branch), §7 (the shell chain that fails open), §12 (coupled rows: parent/slice
  readiness, requirement ↔ deferred-work statuses, item + DW row together, ACs named on a
  done-claim, placeholder test rows, run the gate never carry its count).
- Docs restating the caps: `docs/install.md` (also E14: the per-plugin opt-out is disabling the
  plugin; `disableAllHooks` kills every hook), `SECURITY.md`, `server/README.md`.

## Sizes after

See the batch record §0 (line counts per skill file; lint 12 green after every file).
