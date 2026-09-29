# Batch findings_39: plans 160–164 → v5.7.0, the closing round

> Maintainer-executed, 2026-09-29. **Status: EXECUTED.** Field source: ACMP `findings_39.md`
> (its session on 5.6.1, `2cf7ab61` → `24e59125`). The design and interview record is the
> maintainer's plan file, revision 3, approved after two devil's-advocate reviews.
> Interviews 2026-09-28 and 2026-09-29: five rulings, R51 to R55.

## 1. What the field returned, and what the review added

The field ran 5.6.1 in an ordinary session. **No defect, no feedback row, no lesson change, no
numbered brief error** (25 feedback rows and 112 lessons, both files absent from its diff). The
four reads of the 5.6.1 brief held, the first export took the `1 1` shape, and Part B landed on
the operator's word (`DEC-237`). Its handoff follows the tense rule 5.6.1 taught.

| # | Finding | Source |
|---|---|---|
| 1 | v5.6.1 shipped its order rule in a docstring and called it the tool's description. A client receives the registered description, the second element of each `TOOLS` entry. The rule reached no session | the maintainer's review; this session's own client |
| 2 | A typed `after_id` dropped three matching rows in silence on 2026-09-11 | `findings_39` §3; reproduced (M40) |
| 3 | The review page has ordered ids by number since plan 057; the query tool ordered them as text | `export_html.py`, read |
| 4 | `progress_update` and `audit_record` dropped unknown keys in silence; no client could see the keys they take | the maintainer's census (M42) |
| 5 | An outside export also writes `csv/` beside the page; the 5.6.1 brief's row left it out | `findings_39` §2 |
| 6 | The count of transcript files moved between every run | `findings_39` §3; M46 |
| 7 | The operator's message named 5.7.0 as the release the field ran. No 5.7.0 existed. The field ran 5.6.1 | the tags, the manifest, the field's report |

## 2. Rulings (binding; R7–R50 stand except where named)

| # | Ruling | The operator's answer |
|---|---|---|
| R51 | `entity_query` sorts and cuts by the page's rule. **R47 is superseded.** R50 stands: no descending read | "The page's order (Recommended)" |
| R52 | `progress_update` and `audit_record` refuse an unknown key by name. "unknown columns" stays as it is | "Unknown keys refused (Recommended)" |
| R53 | ACMP reports only a failure, as a feedback row. No `findings_40` unless a class fails | "Report only a failure (Recommended)" |
| R54 | The leftover worktrees are removed. The local 5.1.0 install record stays | "Remove the worktrees (Recommended)" |
| R55 | Three tools register a short contract. The other sixteen one-liners stay | "Three tools, a short contract (Recommended)" |

Named at the approval and approved with the plan, beyond the interviews: the `csv/` clause; the
census sentence in `measurement-evidence`; a refusal in words for a missing required key and
for an item that is no object; `matched` in the returned rows' order; the selftest's comparison
of descriptions; the front door's exact key names.

## 3. Execution

| Plan | What | Commit |
|---|---|---|
| [160](160-the-pages-order-in-the-query-tool.md) | the page's order in the query tool; the cut; the registered description; the selftest's comparison | `67a537d` |
| [161](161-the-write-tools-refuse-an-unknown-key.md) | the refusal; the two registered descriptions | `2607652` |
| [162](162-teaching-docs-and-the-corrections-of-561.md) | the teaching, the docs, the corrections of 5.6.1, this record | the commit of plan 162 |
| [163](163-stamp-then-lab-beat-30.md) | the stamp, lab beat 30, evals, the evidence scripts | the commit of plan 163 |
| [164](164-release-v570.md) | the replay, the brief, the tag, the housekeeping | the close-out commit |

## 4. Measurements

The transcript counts are as of 2026-09-28T22Z and 2026-09-29T04Z. **The harness sweeps old
session transcripts**, so a later run of the same script reads fewer old files and more new
ones. The script prints the oldest and the newest timestamp it read.
Instruments: `plans/evidence/scripts-findings-39/m39.py` and `suites_wrapped.py`.

| # | What | Result |
|---|---|---|
| M38 | The field's tamheed calls on disk, 2026-08-29 to 2026-09-28 | 5,226 calls in 678 files; every result paired; 251 refusals or errors |
| M39 | Refusals per day | 5 to 22 a day until 2026-09-21; 1 to 8 a day since |
| M40 | The 2026-09-11 read, re-run over the field's journal as of that minute, with the engine's own statements | 31 rows matched. The text cut returned `PE-954`, `PE-997`. The number cut adds `PE-1033`, `PE-1037`, `PE-1054` |
| M41 | Field families where text order and the page's order differ | 2 of 27: the journal and the work items |
| M42 | The field's journal and verdict writes | 453 journal items written, 19 refused; 43 verdict items written, 9 refused; 1 written with a key the tool dropped (`custom_attributes`, 2026-09-07); 2 `NOT NULL … entry` errors (2026-09-03, 2026-09-28) |
| M43 | Call sites of the two tools in this repo, by pattern | 72 read; 0 carry an unknown key. The pattern reads inline arguments only; M58 is the second method |
| M44 | The page's rule as order and cut, over the field package | 27 families; each walks complete at limit 7, and the engine's order equals an independent key written in Python |
| M45 | "unknown columns" | 44 refusals of `entity_query`, the last on 2026-09-21; 24 refused items of `entity_upsert`, the last on 2026-09-20 |
| M46 | The oldest field transcript on disk | 2026-08-29T10:48Z, read at 2026-09-28T22:14Z: 30 days and 11 hours. No retention setting in either settings file |
| M47 | The operator's trace file | 31 lines at the start of the execution |
| M48 | Fixture families whose order moves under the page's rule | 0, over `evals/sample-results`, `generated-samples` and `lab` |
| M50 | Readers of `binds` in the engine | 0. One writer, `work_bind` |
| M51 | Sites that speak of paging or the order | 28 hits read; 6 reworded, 11 read and left as true, 3 that hold no claim on the order, 1 dated note |
| M52 | The field's live files and registers at `24e59125` | no sentence is made false. `DEC-237`'s rationale says "text order": an Approved row's history |
| M53 | A feedback row's steps | `Proposed` by the agent; `Confirmed` only with `operator_confirm` and `confirmed_by`; then `Reported`, then `Resolved` |
| M54 | The leftovers under `.claude/worktrees/` | three registered worktrees: clean, unlocked, no branch on the remote, `git cherry` prints `-` for each; four more folders, empty |
| M55 | The page's rule over 28 adversarial strings, on a scratch table | the cut equals the rest of the order at every position. A committed test since plan 160 |
| M56 | Tools that take caller objects | `entity_upsert`, `progress_update`, `audit_record` |
| M57 | Docstring lengths | `entity_upsert` 3,381 characters; every other under 1,800. No client receives them |
| M58 | The ten suites, run with both tools wrapped | before plan 161: 323 tests, 56 calls, no unknown key. After it: 329 tests, none failing, 54 and 17 calls; the keys outside the lists are the seven cases of the new test |
| M59 | Field ids that carry more than one number | the work items alone: 221 of 261 |
| M60 | How the field's four generators walk exported rows, by their matching lines | by id, sorted by their own numeric comparator; one walks deferred work in file order, a family whose order does not move |
| M61 | One page of 100 on the field's journal of 1,546 entries | 0.6 ms under the page's cut; 0.03 ms under the text cut. A full walk at `limit=100`: 12 ms; 2 ms. A bound of a million characters: 2 ms |
| M62 | The registered descriptions | 387, 311 and 300 characters. All 19 as the SDK lists them equal the registry, on SDK 1.28.1 under `uv run` and on 1.27.2 in this machine's plain Python |

### 4.1 Every `after_id` call the field made, replayed under both cuts (W113)

The transcripts behind this table will be swept, the earliest near 2026-10-07. The table keeps
the classes. It holds no field text: a search word filtered the rows and is not shown.

The field made 83 calls with `after_id`, over 13 families. On 74 the text cut and the page's
cut return the same rows. 14 of the 83 read the journal, which is the field's own count. The
nine where the cuts part:

| Date | Family | Bound | Limit | Searched | Rows, text cut | Rows, page's cut | The text cut dropped | It over-reached by |
|---|---|---|---|---|---|---|---|---|
| 2026-09-11 | journal | `PE-950` | 3 | yes | 2 | 3 | `PE-1033` | 0 |
| 2026-09-15 | work items | `WBS-39.99` | 200 | yes | 72 | 59 | — | 13 |
| 2026-09-17 | journal | `PE-1204` | 12 | no | 12 | 4 | `PE-1329` | 9 |
| 2026-09-23 | journal | `PE-1345` | 10 | no | 10 | 5 | — | 5 |
| 2026-09-27 | journal | `PE-1500` | 100 | no | 100 | 5 | — | 95 |
| 2026-09-27 | journal | `PE-1495` | 100 | yes | 8 | 2 | — | 6 |
| 2026-09-28 | journal | `PE-1499` | 100 | yes | 100 | 15 | — | 85 |
| 2026-09-28 | journal | `PE-1499` | 100 | yes | 62 | 5 | — | 57 |
| 2026-09-28 | journal | `PE-999` | 5 | yes | 0 | 5 | five, from `PE-1033` | 0 |

**The method and its limit.** Each call is replayed over the rows the field's head holds that
are no younger than the call, with the call's own search, status and limit. The independent
cut is Python's, never the engine's. A row written after the call and dated before it would
show as a row the call could have seen; the row of 2026-09-17 may be such a case, and the
record does not settle it.

## 5. Researched, separate from the maintainer's reasoning

| Source | What it states |
|---|---|
| Claude Code documentation, `code.claude.com/docs/en/mcp` | "Claude Code truncates each tool description and each server's instructions at 2,048 characters by default. Keep them concise, and put critical details near the start." |
| SQLite, Row Values, `sqlite.org/rowvalue.html` | "A more efficient approach is to remember the last entry currently displayed and then use a row value comparison in the WHERE clause" |
| Winand, Use The Index, Luke, `use-the-index-luke.com/sql/partial-results/fetch-next-page` | "Paging requires a deterministic sort order." |
| SQLite, SQL Language Expressions, `sqlite.org/lang_expr.html` | "the longest possible prefix of the value that can be interpreted as an integer number is extracted from the TEXT value and the remainder ignored." "If there is no prefix that can be interpreted as an integer number, the result of the conversion is 0." |
| RFC 9413, Maintaining Robust Protocols | "Tolerating unexpected input instead conceals problems, making it harder, if not impossible, to fix them later." |
| The vendor's tracker, issue 62476 | "cleanupPeriodDays defaults to 30, causing Claude Code to silently delete ~/.claude/projects//.jsonl files older than 30 days on startup." A user's report. **The vendor's own sentence was not located** |

## 6. Errors owned

| # | Error | Age | Where it is corrected |
|---|---|---|---|
| O10 | The 5.6.1 brief's row on an outside export omitted `csv/` | 5.6.1 | the 5.7.0 brief; plan 162 |
| O11 | The maintainer's census counted any read with `after_id` as safe and never looked inside the class | 5.6.1 | §4.1 of this record |
| O12 | The maintainer recommended teaching only for `after_id`, and recorded number order as rejected, one round before the field measured a silent drop. The page had held the rule since plan 057 | 5.6.1 | plan 160; the design record §20 |
| O13 | "The rule stands in the tool's description." It stood in a docstring no client receives. Two approval records called the docstring "the text every client shows", and the test pinned the wrong text | 5.6.1. The belief is older: the changelog credits a docstring with teaching in 4.4.2, 4.5.0 and 4.7.0, and the one-line descriptions date from the server's first commit (`eb9f252`, 2026-07-17) | plans 160, 161, 162 |
| O14 | The front door named a journal key loosely, and the engine dropped whatever was sent under a wrong name | older than 5.0.0 | plans 161, 162 |
| O15 | In this round's own plans: revision 1 repeated O13; revision 2 called a pattern search a census of callers, and said no committed byte moves of a release that reorders an exported file | this round | the plan's weaknesses W92, W105, W107 |

## 7. Execution notes (owned as they land)

1. **Every new test failed first, for its own reason.** Plan 160: five tests. Plan 161: two,
   and a third case added after the review.
2. **One line changed outside plan 160.** The read of the engine diff found a comment's
   alignment one space short at `_PROMPT_MAX_LINES`. It was restored before the commit. A
   reviewer found the same line afterwards.
3. **"Equal" was seen before it was written.** One description as the SDK lists it was printed
   beside its registry entry, and then all 19 were compared, on two versions of the SDK.
4. **The reviews were checked, not obeyed.** Four reviewer reports, two per engine plan.
   - One finding was half right: two docstrings said every local gate holds the description
     claim. The suite does run the selftest, and this machine's Python has the SDK. It holds
     only where the SDK is installed. The docstrings state the condition now, and the existing
     selftest test asserts the real listing when the SDK is present.
   - One finding was reproduced and fixed: an explicit null `event_type` still came back as
     the database's raw text.
   - One cost was unmeasured in the review and measured here (M61).
   - One detail of a review was wrong: it named a test that does not exist. Nothing rested on it.
5. **An instrument of the maintainer's was wrong, and its disagreement with the gate showed
   it.** `suites_wrapped.py` first counted keys with `Counter.update(item)`, which adds a
   dictionary's values. It raised inside the wrapper and reported 23 failing tests while the
   gate was green. It counts each key by name now.
6. **A plan number written from memory was wrong.** The record of plan 161 first said
   `entity_upsert` had refused unknown columns "since plan 041". The history says since the
   server's first commit. Corrected before the commit.
7. **Lint 12 refused two sentences of plan 162.** Each carried an id as an example. The
   plan's unresolved question U13 had named the risk.
8. **The census's count of "unknown columns" was loose at first.** It read 69, then 58 when
   the script was written down, because the two counts cut the result text differently. The
   script now counts the two tools apart: 44 and 24.
9. **This record says "CI green" and "tagged" before either exists**, as the close-out records
   before it did. If CI is red, a new commit corrects the record and the tag waits.

## 8. What was not built, and why

| Not built | Why |
|---|---|
| A descending read | R50 stands. The resume block names the three newest journal entries, and a typed `after_id` reads from any entry on |
| Full natural order | declined at the interview. Only an id's first number counts, on the page and in the tool |
| The valid set in "unknown columns" | R52. No such refusal in the field since 2026-09-21 |
| Contracts for the other sixteen tools | R55 |
| Server instructions | a field the server has never set |
| A typed item schema | the contract suite runs without the SDK, so the gate would test nothing of that refusal |
| Number order in the eleven id lists of the readiness rules | each names ids and none chooses rows |
| A rule on empty entries | the store accepts one today, and no ruling asked |
| Removal of the local 5.1.0 install record | R54 |
