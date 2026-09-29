# Tamheed v5.6.1 — the findings_38 batch: what a limited read returns, and the page's date

Status: **EXECUTED — v5.6.1 tagged on the release commit (this record's commit; CI green),
2026-09-28** — index section "Field cycle findings_38" in [README.md](README.md). Commits: 156
`1be1305`, 157 `1b3ce75`, 158 `e6fe055`; 159 = the close-out commit that carries this record, the
brief and the index. Execution order: 156 → 157 → 158 → 159.

Read-only evidence this record rests on: ACMP `findings_38.md` (`66ad54c4` → `2cf7ab61`), the row
`DEC-236` (Approved), the journal `PE-1532`..`PE-1540`, the 25 feedback rows and 112 lessons
(unchanged), four memory files of the field's; the field's transcripts on the maintainer's
machine and the operator's trace file, read by the script committed under
[`evidence/scripts-findings-38/`](evidence/scripts-findings-38/) with its output beside it; the
Semantic Versioning specification, the Pro Git chapter on packfiles and the Reproducible Builds
page on `SOURCE_DATE_EPOCH`, fetched 2026-09-28; the approved plan
(`~/.claude/plans/pasted-content-id-79cf-acmp-updated-dazzling-kettle.md`, revision 3 after a
devil's-advocate review); the interview rulings R46–R50.

**Review.** Five `advisor` calls before the approval. The first, after orientation, gave the
slate the first interview's options came from. The second failed, and the first interview was put
without it: those option sets were not re-checked between drafting and showing. The third reviewed
draft 1 after the answers and returned eight points. The fourth checked the second interview's
options before they were shown. The fifth reviewed revision 3 and returned two checks that could
change the plan and six sharpenings; all were acted on before the approval. No sub-agent was used.

## 0. Measurements

Every count is from one machine and true at its run. M24 to M26, M29 and M30 are printed by
`m38.py`, run after lab beat 29; its output is `m38.out.txt`.

| # | Measurement | Result |
|---|---|---|
| M17 | The maintainer's session, its trace line before its restart, 2026-09-28 08:12:23Z | `source=compact lines=0 chars=0 status=silent session=61baf644-…`: no `version=` |
| M18 | A new process in the same folder, 145 s earlier | `version=5.6.0 source=startup … status=silent` |
| M27 | The same session after its restart, 09:14:43Z | `version=5.6.0 source=resume … session=61baf644-…`; `server_info` read `5.4.0` before and `5.6.0` after |
| M21 | The hook's block in the field's transcript, one row | three copies: 19 lines / 3,395 chars; 20 / 3,396 with a trailing newline; one wrapped for the model. The first equals the trace line |
| M22 | The `lab-tracker` eval case | 120 checks before this batch |
| M23 | The field journal, "unbound" and its kin | 33 hits in 1,540 entries; none reports an audit that flagged a close-out commit; two handoffs say the final bind commit "stays unbound by construction" |
| M24 | The engine's order (`ORDER BY id LIMIT 10`) over the lab's journal ids, in memory | the first ten are the ten lowest of 57; they share no id with the three newest; every id is 6 wide |
| M25 | The same over the field's journal ids | the ten lowest of 1,540; they share no id with the three newest; ids are 6 and 7 wide |
| M26 | The field's transcripts on the maintainer's machine | 673 files in 6 project folders at the script's run, subagent files included (685 at the first count, taken during the plan's review before the session's restart: twelve files left the disk between the two, and the count of calls did not move); 1,335 `entity_query` calls, 2026-08-29 to 2026-09-28; **0** reads of the journal or the verdicts without `id`, `ids`, `search`, `after_id` or `status`. Older transcripts are not on disk |
| M28 | Sentences on the page's clock and bytes in live text | 10 sites read; 6 reworded, 4 left as the bare word "deterministic", 3 left as true of their own function |
| M29 | The date on the lab's review page | one occurrence, on a line of 4,647 characters that holds the whole Readiness section |
| M30 | Text-ordered reads in the engine | 15 lines: 4 inside `entity_query`, 2 of them with its `LIMIT`; 11 elsewhere, each a list of ids, none with a `LIMIT`, none choosing rows by the order |
| M31 | Lab beat 29 (plan 158), [the report](evidence/lab-continuation-report-158-2026-09-28.md) | held on its first run, the scratch phase first. Ten rows of 55 returned the ten lowest ids while the resume block named the three highest. One work entry past the handoff: the count read 1, the rule named it, `ids` read it back. Two dates over one store: equal after replacing the date. The first export changed one line, the stamp, on the date the page carried. An export outside the package left 27 files with their hashes |
| M32 | `python check.py`, the trace variable unset, plans 156 to 158 | ALL CHECKS PASSED each time |
| M33 | The field replay on the final bundle over a copy at `2cf7ab61` (`acmp_replay6.py`) | every class held. Before the first export the keys read `review_current` true and `review_exported_by` `5.6.0`; the export, on the date the page carried, changed one line, the stamp, with the digest and the page's size unchanged; a read limited to ten rows returned the ten lowest ids of 1,540, none of them among the resume block's last entries; an export outside the package left the page unchanged; the hook's line opened `version=5.6.1` |
| M34 | The sweep by word on the copy | 102 live files and three register families; 33 hits, every one read; one sentence is in the brief |
| M35 | The hook's block over an untouched copy, by source | a compaction: 20 lines, 3,451 characters; the field's own `resume` lines at the same head read 19 and 3,295. The difference is the compaction's opening sentence, 155 characters and its line feed |
| M36 | `uv run … --selftest` on the final bundle | `mcp sdk: ok (1.28.1) — 19/19 tools registered` |
| M37 | The operator's trace file over the execution | 26 lines when the plan's review read it, before the approval, and 26 after the replay: no line was added. Its last line is at 09:15:15Z; the first full gate of this batch ended at 09:38:59Z |

M17, M18 and M27 settle, on one session id, what the 5.6.0 brief predicted for a process it
could not control: a session that has not reloaded writes the old shape, and the new one after.

## 1. What the field returned (no defect, no feedback row, no numbered brief error)

P0 to P12 held. P13 was not exercised for the third round: no lesson was Proposed and none was
manufactured. The field's control, a compaction after the install and before the reload, wrote a
line with no `version=` while a new process wrote `version=5.6.0`.

- **A condition the brief lacked.** The field wrote "the UTC date is still 2026-09-28" into its
  own prediction for the first export: the page states the date its Readiness section was
  evaluated on.
- **An instrument's limit.** "No script on disk parses a trace line" was true of the
  maintainer's `git archive` copy. The field holds one parser in an ignored folder; it reads the
  timestamp by position, which the new field does not move.
- **A misuse the field classed as its own.** An id typed into `after_id` as "from this entry on".
- **Two sentences its advisor corrected** in the handoff draft: one called a step done and
  remaining, one said a branch was pushed through commits not yet made.
- **The review page's weight, measured and ruled by the operator in the field** (`DEC-236` d4):
  a push sends the page as a delta (1.08 KiB for a one-line change, 10.64 KiB for a session's
  change); the page's history is 533 versions, 51 MiB of a 72 MiB pack; opened sometimes, every
  section read; not a cost today, no feedback row. The 5.6.0 rulings R42 and R45 are discharged
  by that row. Nothing is built, and the design record carries no paragraph on it (R48).
- **About Claude Code:** an update writes the old folder's marker within milliseconds; a
  marketplace update replaced the clone; a transcript's hook row names the hook's status
  message and no path.

## 2. Rulings (R46–R50, binding; R7–R45 stand)

| # | Ruling | The operator's answer |
|---|---|---|
| R46 | The three audit lists point at one rule. `package-writes` §9 names the close-out's last commit. No lint. | "Point the three lists at one rule (Recommended)" |
| R47 | `after_id`: teaching. The engine is unchanged. | "One teaching sentence (Recommended)" |
| R48 | Three corrections land: the page's date with one test; `install.md`; the `session-handoff` sentence. The design-record paragraph on the page's weight is declined. | three of four options selected |
| R49 | ACMP takes the release at the start of its next ordinary session. | "Release; the brief rides with DEF-218 (Recommended)" |
| R50 | Recent rows: teaching only. No `newest` parameter. | "Teaching only, point at the resume block (Recommended)" |

Named at the approval and approved with the plan: the number 5.6.1; one sentence in
`entity_query`'s docstring; `integrity-check`'s export to a path outside the repository.

## 3. Execution

| Plan | What | Commit |
|---|---|---|
| [156](156-what-a-limited-read-returns-and-the-unbound-commit.md) | the order rule in the tool's description and in `package-writes`; three lists on the unbound commit; the audit's export; the handoff's tense | `1be1305` |
| [157](157-the-pages-date-and-docs-sweep-findings-38.md) | the date test; six sentences reworded; the docs sweep; this record | `1b3ce75` |
| [158](158-stamp-then-lab-beat-29.md) | the stamp, lab beat 29, evals | `e6fe055` |
| [159](159-release-v561.md) | the replay, the sweep, the brief, the tag | the close-out commit |

> **Correction, 2026-09-29 (findings_39, O13).** The row of plan 156 says the order rule
> went into "the tool's description". It went into `entity_query`'s docstring. The server
> registers the second element of each `TOOLS` entry as the description, and a docstring
> reaches no client, so that sentence reached no session. The skills and the templates did.
> The design plan of this batch, in its weakness W63 and at its approval, called the
> docstring "the text every client shows"; that was false. Corrected in v5.7.0, plan 160:
> [160-164-batch-findings-39.md](160-164-batch-findings-39.md).

## 4. Errors owned

| # | Error | Age | Where it is corrected |
|---|---|---|---|
| O1 | The 5.6.0 brief's class for the first export omitted the UTC date. The field supplied it | 5.6.0 brief | the 5.6.1 brief |
| O2 | Four sentences promise the page's bytes from the store's state alone | since 2026-09-23 | plan 157 |
| O3 | "None on disk" rested on an instrument blind to ignored files | 5.6.0 brief | the 5.6.1 brief |
| O4 | The example for a line with no `version=` was a process nobody controlled | 5.6.0 brief | the 5.6.1 brief quotes M17 and M27 |
| O5 | A skill's "step 5" was cited where the steps are bold paragraphs | 5.6.0 brief | skills are cited by heading text |
| O6 | "The journal from `PE-1500` on", with no method named | 5.6.0 brief | the 5.6.1 brief names the method |
| O7 | The 5.6.0 order rule shipped without a sweep of the lists that read binds | 5.6.0 | plan 156 |
| O8 | Three teaching lines call a limited read "the last recorded activity" | 2026-07-22 | plan 156 |
| O9 | `integrity-check` rewrites the committed page in a read-only run | older than 5.6.0 | plan 156 |

**In this round's own plan**, found by the maintainer's review and by the advisor before the
approval: "three texts" where ten sites stood (W58); a test that would have proved less than
its sentence (W59); "`entity_query` alone orders by text", false for eleven other reads (W60); a
transcript count without subagent files or a date range (W61); `audit_evidence` described as
listing each criterion's latest verdict, which it does not (W74); a hand-made method for the
newest rows of any family, cut as speculative (W75); a list called uncapped that is capped at
50 (W76); a provenance line that claimed an advisor call which had failed (W47); an interview
header that called 5.7.0 the repo's rule (W48).

## 5. Execution notes (owned as they land)

1. **The date test pins behaviour that exists**, so it had no failing run before an edit. Its
   calibration is in the assertion itself: it fails when the two pages are equal and fails when
   any byte but the date differs.
2. **The docstring's test failed first**, on the missing phrase, and passed after the edit.
3. **Beat 29 held on its first run.** Two of its assertions had been made able to fail before
   the run: the list of `handoff-current` is empty on the fixture, so the check writes one work
   entry first; the first export's line count depends on the UTC date, so the check reads the
   date from the page.
4. **The first copy command of the replay failed** on a Windows-style path handed to `tar`. It
   stopped before anything ran. The second, with the same path in the shell's own form, ran.
5. **The measurement script first held a folder name of the maintainer's machine.** It is an
   argument now, and the output was regenerated.
6. **The count of transcript files moved between two runs**, 685 and then 673, with the count
   of calls unchanged. The record states both and does not explain the twelve: nothing on
   disk says why they left.
7. **A discrepancy read before it was written down.** The replay's block read 20 lines where
   the field's trace reads 19 at the same head. A second, untouched copy settled it: the
   field's lines are `resume` lines, and a compaction's block carries one sentence more (M35).
8. **The advisor's review before the close-out commit returned two points, both acted on.**
   The brief's class for an export after a write left out the digest's line, which a write
   moves; the beat's own diff shows it. And this record gave the interval between two counts
   as "about two hours", a guess; it now says when the first count was taken.
9. **This record and plan 159 say "CI green" and "tagged" before either exists**, as the
   close-out records before them did. If CI is red, a new commit corrects the record and the
   tag lands on that commit.
