# Plan 165: `handoff-repeated` — the lines a handoff carried unread

> Maintainer-executed, 2026-09-30. Batch map: [165-169-batch-fb026-fb027.md](165-169-batch-fb026-fb027.md).
> Source: the field's `FB-027` (question, Confirmed 2026-09-29), ruling R56.

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What the field reported (FB-027)

- A handoff line marked `carried, not re-measured` travelled through eight handoffs after the
  operator had answered it (a 2026-09-24 ruling, carried 2026-09-26 to 2026-09-29). A second
  line tracked a ruling that could never be executed, and the re-measurement was a code read
  that no handoff made.
- The skill's rule was followed: each line carried the mark. The mark moved the re-measurement
  onto the next reader, and each session read the mark as permission to carry again. The
  project's own pre-interview sweep caught both.
- The question: should a carried line name its source and last-measured date, and should
  something flag a line carried unchanged past N handoffs?

## The replay (M73, `plans/evidence/scripts-fb026-fb027/m73_repeated.py`)

Over the field's 18 handoffs, cut at each handoff in turn, through the engine's own helper:
the rule fires on 6 of 18, naming 1–5 lines each. The 13-verdicts line is named at the
third handoff (2026-09-27, two days before the field's sweep), again at the fourth, and once
more three handoffs after the mark was added — three of the eight positions it travelled,
because its punctuation moved twice and each move reset the count. The MTG line is named
twice of eleven. On the latest handoff the rule passes.

## The ruling (R56)

`readiness_check` gains one advisory; `session-handoff` teaches source, date and a one-handoff
mark (plan 167). No hook change, no resume-block change, no store change.

## What changed

| File | Before | After |
|---|---|---|
| `tamheed_server.py`, `_HANDOFF_REPEATED_AT = 3`, `_HANDOFF_LINE_MIN = 20` | — | the calibration, from one project's 18 handoffs |
| `_repeated_handoff_lines(conn)` | — | the lines of the latest handoff that stood word for word (whitespace collapsed) through the handoffs before it, three deep or more: `[(line_no, since_id, depth)]`, and the handoff count. Headings (ending with `:`) and lines under 20 characters are not read. Line numbers are 1-based over `str.splitlines()`, the hook's numbering; a blank line keeps its number |
| `_readiness_report`, package scope, after `handoff-current` | — | `handoff-repeated`, advisory, emitted once the journal holds three handoffs. Entities: the handoff each named line first stood in, deduplicated, in journal order. Note: the rule and the remedy; `extra`: `lines 5, 6 of PE-1542 since PE-1473 (7 handoffs)`. Population: `progress_entries`, rows = handoffs |
| `skills/register-liveness/SKILL.md` | 21 steps | step 20 is the rule's row; the close step is 22 |
| `tests/test_mcp_contract.py` | — | the rule absent under three handoffs; fail with the first handoff's id and the line number at three; a heading and a short line never count; a blank line keeps the numbering; the verdict untouched; a reworded line passes; several lines sharing a first handoff name it once, in order. The rule-name list of the liveness test gains the name |

## What the rule reads and what it does not

- Wording, never truth: a reworded line resets the count. Said in the note and the skill.
- Handoff entries only, never their correction chain: a retracted line that is still repeated
  counts.
- Ids and integers only reach the output: no line of an entry is written anywhere.

## Why the name

`deferred-work-carried` already means a `carries` trace edge to an Activated deferred row.
The rule does not borrow the mark's word either: it reads repetition, and says so.

## Validation

- The two new tests red, then green; the liveness-name test red, then green.
- `python check.py`: ALL CHECKS PASSED.
- M73 through the engine's helper equals the planning replay's independent script, line for line.
- `ecc:python-reviewer` and `ecc:security-reviewer` on the diff, each finding checked by
  reading or running before it was acted on:
  - MEDIUM (both): the helper re-parsed every earlier handoff once per line of the latest.
    Fixed: every entry is parsed once and read to `_RESUME_ENTRY_CAP` characters, the
    resume block's own cap, so the journal's size bounds the cost.
  - LOW (security): `int(id[3:])` would raise on `PE-1x`, which the store's `GLOB 'PE-[0-9]*'`
    admits and `_next_id` never mints. Fixed: the entities are ordered by depth, no parse.
  - LOW (python): the note said "as the hook prints them"; the hook prints 25 lines. Reworded.
  - Test gaps named and closed: a run with a gap (handoffs 1, 2, 4) does not fire; an empty
    handoff breaks a run; other journal kinds between handoffs are not read; no line text
    reaches the note; two `since` ids come in journal order past `PE-9`. The `break` → `continue`
    mutation was run: the gap test fails on it, as it should.
  - A wrong step of mine during the review: a `git checkout --` of the server file, meant
    for the mutation, reverted the plan's edits; they were re-applied from this record and
    the tests and M73 re-run equal.
