# Tamheed v5.5.0 — the findings_36 batch: two words, the note's roster on the review page, three sentences

Status: **IN PROGRESS** — index section "Field cycle findings_36" in [README.md](README.md).
Commits: 146 `de49286`, 147 `ac6c96b`. Execution order: 146 → 147 → 148 → 149 → 150.

Read-only evidence this record rests on: ACMP `findings_36.md` (`3071f1f4` → `27f63ae8`), the rows
`LL-112` (edited, then Approved), `DEC-234` (Approved), the journal `PE-1512`..`PE-1522`, the 25
feedback rows (unchanged), the field's `hook-trace.md` and its carried rule on what binds; the
session transcripts under `~/.claude/projects`, read by the three scripts committed under
[`evidence/scripts-findings-36/`](evidence/scripts-findings-36/); Claude Code's plugin loading
reference, the Agent SDK's features page and migration guide, and the hooks reference, fetched
2026-09-27; the approved plan (`~/.claude/plans/pasted-content-id-79cf-acmp-updated-dazzling-kettle.md`,
revision 2 after a devil's-advocate review); the interview rulings R27–R35.

## 0. Measurements

Every count is from one machine. Transcripts are created and pruned, so a count is true at its run.

| # | Measurement | Result |
|---|---|---|
| M1 | Transcripts with a `SessionStart` row, by entrypoint (`m36.py`) | headless command-line 1357 of 1357; interactive 35 of 37 |
| M1b | The two interactive transcripts without one | 11 rows each, five seconds long |
| M1c | SDK-Python transcripts (`m36.py`, `sk36.py`) | one build, 2.1.204. Hook rows of any event: 0 of 644. Carrying a skill listing: 640 of 640 at the second run; naming any plugin: 0. The pattern fires on 1328 of 1328 headless command-line transcripts |
| M2 | SDK-Python sessions in enabling folders while the trace was on | 12, and no trace line at any of their times |
| M4 | `hook_success` rows with stdout and stderr both empty, all transcripts | 0. Session `368cc047` wrote a `silent` line with its own id and has no tamheed row |
| M5 | `server_info` in the maintainer's session before its restart | the MCP server read 5.2.0, two releases behind the install |
| M6 | A typed `/compact` and the summariser's trace line, three controls | typed 02:36:32.155Z, line 02:36:35; typed 17:56:52.436Z, line 17:56:55; typed 03:22:55.281Z, line 03:22:57. Each line is `source=startup` |
| M6b | The field's unattributed line | `/compact` typed at 03:22:42.572Z in the field's session; the line at 03:22:45; no compaction row follows in that transcript, and no summariser transcript persisted |
| M7 | Two sessions in one folder with the same settings | the fresh one (18:31:57Z) ran the 5.4.0 hook. The one started 2026-09-26 compacted at 18:34:16Z and wrote nothing. After its restart it wrote a line carrying its own id (19:37:05Z) |
| M8 | Reloads: the field's count against the maintainer's | 22 in its main transcript, 24 across all. Consistent |
| M9 | Plan 146: the repo's exporter over a copy of the field package at `27f63ae8` (`p146_acmp.py`) | 30 rows in the Approved fold; the ten marked ids equal the ten its note lists; the calibration is caught |
| M10 | `python check.py`, the trace variable unset, plans 146 and 147 | ALL CHECKS PASSED each time; no line in the operator's trace inside a run's window |

## 1. What the field returned (no defect, no feedback row)

Every predicted class P0–P10 held. The `session=` tail told two sessions apart that had printed one
block 75 seconds apart. `LL-112` was edited while Proposed and approved unpinned by a full row;
`DEC-234` retired Q1. Three brief errors. Four misses the field recorded against itself.

## 2. Rulings (R27–R35, binding; R7–R26 stand)

| # | Ruling |
|---|---|
| R27 | v5.5.0 MINOR; no migration. |
| R28 | Three sentences enter the skills: the rule-first statement; the row an approval displaces; discharge where the obligation was made. The self-match lesson is not absorbed. |
| R29 | `review.html` gains a column for the note's roster and an honest fold title. |
| R30 | Trace docs: corrected as measured, plus the transcript cross-check recipe and the silent-run fact. Documented behaviour is cited. |
| R31 | No new result key. The approval hint's cap phrase is unchanged. Its first clause moves under R34. |
| R32 | The stock guide and `governance.md` state the cap. |
| R33 | Lab beat 27 exercises the render cut and the new column. |
| R34 | Two words. **Binds** is the status, the operator's word. **Rendered** is the note's roster. A displaced lesson still binds and is read only by query. |
| R35 | The note's footer says the rows behind it bind too and are not rendered there. |

Not built, on purpose: a new result key; the self-match sentence; a census tool; an entrypoint
field in the trace (R21); a cause for the SDK-Python count; a rename of the
`lessons-superseded-binding` rule; a change to the note's heading; a read of the note on disk by
the exporter; a regenerated `minimal-brief` page.

## 3. Execution

| # | Plan | Status |
|---|---|---|
| 146 | [Two words in the engine, and the roster on the review page](146-two-words-and-the-note-roster.md) | DONE `de49286` |
| 147 | [The two words and three sentences in the skills](147-the-two-words-and-three-sentences.md) | DONE `ac6c96b` |
| 148 | [Docs + diagrams sweep for v5.5.0](148-docs-and-diagrams-sweep-findings-36.md) | DONE — this record's commit |
| 149 | [The version stamp, then lab beat 27 + evals](149-stamp-then-lab-beat-27.md) | PLANNED |
| 150 | [Tag v5.5.0, the brief file, close-out](150-release-v550.md) | PLANNED |

## 4. The 5.4.0 brief's errors, owned, and the maintainer's own

**The brief's, as the field found them.**

- **E1** the D1 correction list named two places and omitted two more that lean on the same error.
- **E3** Q1 "can be corrected by a `correction` entry". Q1 was also a clause of an approved
  decision, which a journal correction does not discharge. The recipe had run clean on the copy.
- **P4** said both `CLAUDE.md` files read `unchanged`. The result is one `unchanged` entry and a
  warning about the root file.

**The maintainer's own, which the field did not report.**

- The roster sentence shipped in 5.2.0 (plan 132) against `governance.md`. No check saw it for
  three releases. The field followed it.
- "Every session in every project where the plugin is ENABLED appends a line": written by the
  5.4.0 sweep as a rule, not a count.
- The 5.4.0 brief's sweep read the field's memory files only, never its decisions or journal. That
  is how Q1's second carrier was missed. It repeats the lesson of the 4.13.0 round.

## 5. Execution notes (owned as they land)

1. Revision 1 of the plan was rejected for a devil's-advocate review. Direct inspection overturned
   four of its statements: that "status binds" was the engine's vocabulary; that 644 SDK-Python
   sessions "ran no SessionStart hook"; that the page could import the server's helper; that goldens
   are regenerated by an existing script.
2. The advisor had ruled "status binds" the engine's words. The maintainer's grep found the skill
   sentence that says the opposite; the advisor withdrew the ruling and the question went to the
   operator.
3. Four interview options carried loose wording: "stops binding"; "`server_info` names the version
   a session loaded" (it names the MCP server's); "beat 27 rewrites the lab fixture's note" (it
   does not: the footer prints only past the roster, and the fixture has one Approved row); and
   revision 1's "no change to the approval hint", which R34's option text narrowed. No ruling
   depended on any of them.
4. Revision 1's U2 said other hooks with empty output leave a transcript row. They had written to
   stderr. No row on the machine has both streams empty.
5. Plan 146's numbers test was planned to read the shipped text. The text lands in plan 147, so the
   boundary test went into 146 and the read-back into 147.
6. A Promoted row needed its own hint sentence: under the new word the shared one would have called
   a never-rendered row rendered. An existing assertion caught the shape before the edit.
