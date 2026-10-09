# Plan 214 -- one text for both G-COMPLETE scans (the field's FB-001)

> Status: DONE 2026-10-09 UTC (maintainer-executed, the operator's word at the review). Field cycle jisr-01. Released by plan 215
> as 6.2.1 (PATCH). Evidence: `plans/evidence/jisr-field-report-01-2026-10-09.md` (FB-001 and
> LL-001 verbatim, the hook print, the gate replay).

## What the field saw

The `jisr` package (planning half, born under 6.1.0, opened under 6.2.0 on 2026-10-08) fails
G-COMPLETE on `PE-011` alone. PE-011 is a work-done journal entry that quotes, in prose, the
`[NEEDS-CLARIFICATION: OQ-019]` marker it had just removed from FR-016 when OQ-019 was Deferred in
the same batch. The journal is append-only (`expect_unchanged` and `entity_upsert` refuse PE rows),
so no repair exists from the package: PE-014 (a `correction`) explains the quotation, handoff PE-018
carries the standing failure, FB-001 (Confirmed, then Reported) names the expected fix, LL-001
(Approved) tells the field's own sessions to describe a marker and never quote it.

## The defect, read in the server

G-COMPLETE has two scanners over the same tables with the same row filter (plan 046 made the
`Superseded`/`Obsolete` filter match). They read different text:

| | the placeholder loop in `gate_run` (L2651-2674 at HEAD) | `_scan_markers` (L622-659 at HEAD) |
|---|---|---|
| column skips | `custom_attributes` + `_EXEMPT` (`progress_entries.entry`, `audit_verdicts.evidence`) | `custom_attributes` only |
| code spans | `_strip_code` before the match (D-017-4) | none |
| rows | `lifecycle_status NOT IN ('Superseded','Obsolete')` | the same |

Plan 046's maintenance note ruled the class in advance: "Two scanners, one rule: any future 'which
rows does G-COMPLETE read' change must be applied to both." The second difference was live on this
repository's own data: `generated-samples/support-triage-agent-v2` reported `G-COMPLETE fail` on
`PRT-002.body` ("marker cites no OQ id") because the prompt quotes `` `[NEEDS-CLARIFICATION: OQ-NNN]` ``
inside backticks. No eval or test pinned the demo's gates, so it failed unseen since the prompt rows
landed in v6.0.0. The guide's `gate.G-COMPLETE` sentence ("Code spans are stripped first ... Exempt:
`custom_attributes`, journal entries, verdict evidence, Superseded and Obsolete rows") and the FAQ's
answer ("Wrap the token in backticks") already promised the behaviour for the whole gate.

## The decision

**One shared text source, both loops iterate it.** `_REPORT_COLUMNS` (the former local `_EXEMPT`)
becomes a module constant beside `_PROSE_ID_EXEMPT_TABLES`. `_graded_text(conn)` yields
`(row_id, column, text)` over every `ENTITY_TABLES` table: the TEXT columns minus `custom_attributes`
and the report columns, the `Superseded`/`Obsolete` filter when the table has `lifecycle_status`,
code spans stripped by `_strip_code`, empty values skipped. `_scan_markers` and the placeholder loop
read it and keep their result shapes. Both `_scan_markers` callers follow: `gate_run` and the
`clarifications-open` advisory (a quoted or journaled valid marker is no longer an open
clarification, plan 046's deferred release-note line).

**FB-001's second option, rejected on two grounds.** "Scan journal entries only when newer than the
cited question's resolution": `open_questions` carries no resolution timestamp (`resolution`,
`resolved_by`, `lifecycle_status`, no `resolved_at`), so the rule needs a schema change, not a
PATCH; and PE-011 was written after OQ-019's deferral in the same batch, so the rule would still read
it and still fail forever.

**LL-001 upstream.** Not adopted as a prohibition: after the fix the journal cannot fail the gate, so
"never quote a marker in the journal" would be a rule with no mechanism behind it. The fact lands as
one bullet in `skills/package-writes/SKILL.md` (the skill the hook names before the first write,
where the journal-tools bullet lives): both scans skip `entry` and `evidence`, and elsewhere a marker
is quoted inside backticks. `session-handoff` gets nothing. LL-001 stays the field's row.

**Monotone.** Both changes only remove matches (skipped columns, stripped spans). A package that
passes today cannot start failing. The three pinned tests (the journal exempt from placeholders and
supersession repairing; a dangling cite failing; a superseded marker as history with the live row
still failing) prove the gate still bites where it should.

## The jisr acceptance of 6.2.0 (the operator's second ask, measured 2026-10-09)

The root `CLAUDE.md` is the stub byte for byte, the package's `CLAUDE.md` holds the planning note,
`AGENTS.md` is absent by the 212 design (the stub imports one only when the operator writes it), no
lock is held, and the hook printed the resume block for handoff PE-018 with the planning `next`. The
jisr session log records the same open from the other side. Applied in full, nothing to repair.
Observed in jisr and not ours to change: its `README.md` and `README.txt` name `--package-dir
./planning` and files that are not in the tree, while the package lives at `tamheed-package/`.

## Rulings taken at the review

- **R71 (2026-10-09, the planning checkpoint): full parity.** Both scans read one text: the report
  columns leave the marker check and code spans are stripped before it. The field asked only for the
  journal exemption; the demo sample proved the same defect on this repository's own data.
- **R72 (2026-10-09, the commit review): trim the field's words from the evidence.** The evidence
  file keeps the field's two rows and the hook's own lines. The project's title, the handoff's body
  and the session id stay in the field: this repository is public, the field's is private. Two
  postures that moved during execution were disclosed in the same question: the skills lint refused
  a field identifier in `package-writes` (reworded), and the five gate figures were recaptured.

## Validation

- **Red first.** `test_marker_quoted_in_journal_or_code_span_is_a_quotation` failed on HEAD's
  engine with three G-COMPLETE failures at once: `CON-020.statement` "OQ-099 does not exist" (the
  backticked marker), `AV-001.evidence` and `PE-001.entry` "OQ-001 is resolved — remove the marker"
  (the journal and the verdict evidence). `test_demo_sample_passes_g_complete` failed on
  `PRT-002.body` "marker cites no OQ id". Both green after the engine change, with the three pinned
  tests (`test_g_complete_journal_exemption_and_matched`, `test_marker_validity_in_g_complete`,
  `test_marker_on_superseded_row_is_history_not_a_failure`) and the code-span placeholder test green
  beside them.
- **The replay over a scratch copy of the field's package** (`scripts-214/replay_jisr_214.py`, the
  HEAD run loads HEAD's server from a temp bundle copy). HEAD: `G-COMPLETE=fail failures=['PE-011']`,
  `{"id": "PE-011", "column": "entry", "marker": "OQ-019 is resolved — remove the marker"}`. Fixed:
  `G-COMPLETE=pass`. Both runs: `ready=False`, `G-SET=fail` on acceptance-criterion, phase and prompt
  (as handoff PE-018 says), every other gate pass, `clarifications-open=fail` over the same 18 live
  markers. jisr before and after: 55 untracked entries, no lock, nothing written.
- **The demo sample** (`evals/pkg_check.py gates generated-samples/support-triage-agent-v2`):
  `G-COMPLETE=fail` on `PRT-002.body` before, `G-COMPLETE=pass` and `ready=True` after.
- **The guide.** `shift_214.py`: every citation re-aimed by the HEAD-to-working-copy line map, one
  unmapped (`L2652`, the hand comment on a deleted line, re-aimed by hand to `L2659 ... through
  _graded_text`). `GATE_HOW` G-COMPLETE 2684 -> 2672, `VACUOUS` 2631/2640 -> 2643/2652, the guide
  test's pins 2622/1950/1951/2225 -> 2634/1962/1963/2237. `docs/guide/build.py`: 1,546 ids, 724
  figure files, `--check` fresh, `--missing` 0. `index.html` unchanged (the line text lives in the
  SVGs): 20 gate-figure files changed (five gates x EN/AR x light/dark). `capture_214.py`: 20 PNGs
  under `plans/evidence/captures-214/`.
- **Pins.** `pins-214.md`: 9 pinned phrases over the three strict files; `pins_missing.py`: 0.
- **Lint.** `check.py lint` caught one line: the skills lint (plan 114) refuses a field identifier
  in a skill ("FB-001"); reworded to "the field's defect report, plan 214". Then clean.
- **The gate.** `python check.py`: ALL CHECKS PASSED (the three eval cases pass, 0 failed, 6 skipped;
  `lint: teaching surface (61 files) speaks only engine vocabulary`). `git status --porcelain` after
  the gate: the intended files only, no fixture moved.
- **The selftest.** `uv run plugins/tamheed/server/tamheed_server.py --selftest`: 19/19 tools,
  longest description 387 characters (no description changed).
- **Suites** (measured after the gate): `tests/test_mcp_contract.py` `Ran 220 tests ... OK
  (skipped=1)` (218 before the beat, two new); `tests/test_user_guide.py` `Ran 16 tests ... OK`.
- **The engine diff** (`git diff --stat`): `tamheed_server.py` 53 insertions, 65 deletions. The
  two loops' own table, column and filter code left with their comments; the helper carries them once.
