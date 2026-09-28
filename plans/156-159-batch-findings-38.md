# Tamheed v5.6.1 — the findings_38 batch: what a limited read returns, and the page's date

Status: **IN PROGRESS** — index section "Field cycle findings_38" in [README.md](README.md).
Commits: 156 `1be1305`. Execution order: 156 → 157 → 158 → 159.

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

Every count is from one machine and true at its run.

| # | Measurement | Result |
|---|---|---|
| M17 | The maintainer's session, its trace line before its restart, 2026-09-28 08:12:23Z | `source=compact lines=0 chars=0 status=silent session=61baf644-…`: no `version=` |
| M18 | A new process in the same folder, 145 s earlier | `version=5.6.0 source=startup … status=silent` |
| M27 | The same session after its restart, 09:14:43Z | `version=5.6.0 source=resume … session=61baf644-…`; `server_info` read `5.4.0` before and `5.6.0` after |
| M21 | The hook's block in the field's transcript, one row | three copies: 19 lines / 3,395 chars; 20 / 3,396 with a trailing newline; one wrapped for the model. The first equals the trace line |
| M22 | The `lab-tracker` eval case | 120 checks before this batch |
| M23 | The field journal, "unbound" and its kin | 33 hits in 1,540 entries; none reports an audit that flagged a close-out commit; two handoffs say the final bind commit "stays unbound by construction" |
| M24 | The engine's order (`ORDER BY id LIMIT 10`) over the lab's journal ids, in memory | the first ten are the ten lowest; the three newest are 45 rows further on; every id is 6 wide |
| M25 | The same over the field's journal ids | the ten lowest of 1,540; ids are 6 and 7 wide |
| M26 | The field's transcripts on the maintainer's machine | 685 files in 6 project folders, subagent files included; 1,335 `entity_query` calls, 2026-08-29 to 2026-09-28; **0** reads of the journal or the verdicts without `id`, `ids`, `search`, `after_id` or `status`. Older transcripts are not on disk |
| M28 | Sentences on the page's clock and bytes in live text | 10 sites read; 6 reworded, 4 left as the bare word "deterministic", 3 left as true of their own function |
| M29 | The date on the lab's review page | one occurrence, on a line of 4,647 characters that holds the whole Readiness section |
| M30 | Text-ordered reads in the engine besides `entity_query` | 11, each a list of ids; none carries a `LIMIT`, none chooses rows by the order |

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
| [157](157-the-pages-date-and-docs-sweep-findings-38.md) | the date test; six sentences reworded; the docs sweep; this record | — |
| [158](158-stamp-then-lab-beat-29.md) | the stamp, lab beat 29, evals | — |
| [159](159-release-v561.md) | the replay, the sweep, the brief, the tag | — |

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
