# Standup report program -- the record (plans 232-237, release 6.6.0)

The operator asked on 2026-11-15 for a daily status report on demand: from the latest report to
now, answering what we did, the challenges and decisions, and what we expect to do next, read
by a human in 5 to 10 minutes. An eleven-round interview, two advisor passes and a
devil's-advocate review on the operator's request produced the rulings below (SR1-SR49). The
approved plan is revision 2 of the session plan; ADR-0003 holds the store decision.

## Measurements (2026-11-15/16)

| What | Value | How |
|---|---|---|
| Status moves never journaled | lab-tracker: 47 rows past Draft/Proposed/Open, 29 with no journal row naming them, 15 named in no journal text | a read of the fixture's JSONL |
| Text-only edits in the first field | 0-15 rows a day, 9-15 Nov (10 Nov: 8 requirements, 3 constraints) | ACMP git history, status + content fingerprint per row, day by day |
| The 15 Nov "633 edits" | all one key: `lifecycle_status` absent -> null (the 6.5.0 column) | a diff of `document_sections` across the two revisions |
| Size of the first field | ~3,640 entity rows, 13 MB store | row counts |
| Daily row (approved shape: 30 items, 100-char titles) | 14.8-20.8 KB, about 6.2 MB a year | `measure_232.py` on scratch copies of five ACMP revisions |
| First report | ~506 KB (state 121 KB, facts 381 KB) | the same script |
| `RPT-` collisions | 0 in ACMP, Jisr-dev (37 files), the Jisr export (39), the fixtures, generated-samples, lab | grep over the JSONL |
| Reading rate | 238 wpm for English non-fiction, most adults 175-300 (Brysbaert 2019, J. Mem. Lang. 109:104047, abstract read first-hand) | -- |
| zoneinfo in the server env on Windows | unusable: `TZPATH` empty, `tzdata` only global, no `mcp` dependency needs it | probes |

## Rulings (operator)

| # | Ruling |
|---|---|
| SR1-3 | Readers: operator, team, manager. An HTML file in the package. English |
| SR4 | Hybrid: the engine builds the fact sections; the agent writes a headline and three summaries, citing ids |
| SR5 | The first window starts at package birth (a start date only when one is known) |
| SR6 | Draft, then record; the window end is fixed at the draft |
| SR7 | Optional start: a date (snapped to the last recorded daily report on or before it) or an RPT id |
| SR8 | A fixed UTC offset on each row; the first report asks; later reports reuse it |
| SR9 | ADR-0003 supersedes ADR-0001's "never stored snapshots" clause for this family |
| SR10, SR13 | Snapshot diff by deltas and replay. Record checks replay + delta = the state the draft saw. Moves after the draft are reported, never refused |
| SR11 | The name: standup report, `/tamheed:standup` |
| SR12, SR39 | The first report is exempt from the budget and is a full catch-up, folded |
| SR14 | Override reports: kind `override`, recorded, never the next start, never replayed |
| SR15, SR38, SR42 | 2,000 visible words; the engine part at most 1,400; a narrative over its share only warns (re-confirmed against the reading rate) |
| SR16 | Plain words and a glossary; ids as small references |
| SR17 | Decisions made, decisions pending, waivers and scope changes; a top "Needs from you" block |
| SR18 | Next = the engine's open-work list + the agent's plan, labelled as a plan |
| SR19 | Challenges = defects, risks, failed checks and escalations, blockers |
| SR20, SR36 | Refuse an id no row holds, a strict plain-English hard finding, instruction-shaped text. Real ids beyond the page are allowed |
| SR21, SR34, SR45 | The agent proposes the colour by the default rule; the operator confirms; the page shows the rule colour when it differs; a non-green colour needs a road to green |
| SR22, SR43 | Recording needs the operator's words, mechanically; the words are stored in the row only; the journal note names the report and the recorder, never the words; no page prints them (a side review, 2026-11-16) |
| SR23 | A recorded report is immutable; a correction supersedes it over the same window |
| SR24 | One live draft; drafting again replaces it; a discard removes it |
| SR25 | `reports/RPT-NNN.html` committed; `reports/draft.html` ignored by git |
| SR26 | The resume block and the hook name the last report in one line |
| SR27 | Tests: contract, goldens and the word budget, a headless lab rehearsal |
| SR28 | 6.6.0 MINOR; plans 232-237; ACMP and Jisr briefs rehearsed headless |
| SR29-30 | Prefix `RPT-`; one staged tool `standup_report` (21 -> 22 tools) |
| SR31 | Offer `/tamheed:progress-sync` when the store looks behind |
| SR32 | After record: export `review.html`, propose one commit, run it on a yes |
| SR33 | Draft review: a chat summary, the absolute path, and the browser (headless: the path only) |
| SR35 | At a glance: counts and the active phase's progress (Review never counts as done) |
| SR37 | Commits bound in the window: a folded list under What we did |
| SR40 | Text edits tracked by a content fingerprint; a folded "Edited (status unchanged)" list |
| SR41 | Facts frozen as ids and titles (at most 100 characters), at most 30 per list (the first report uncapped) |
| SR44 | A checkpoint every 30th recorded daily report; per-link verification; a forced re-baseline on a broken link |
| SR46 | `entity_query` on this family leaves out `state_delta` and `facts` unless `columns` names them |
| SR47 | The `PE-1x` crash is fixed if a red test reproduces it |
| SR48 | The measured daily row (14.8-20.8 KB) is accepted as approved; the size limit is 25 KB a daily row (2026-11-16) |
| SR49 | The report row keeps the operator's exact words (committed in `data/`), like lessons and feedback; the journal note and every page leave them out (2026-11-16) |

## Research (sourced, accessed 2026-11-16)

Brysbaert 2019 (reading rate, above). The Scrum Guide 2020 has no three questions; the Daily
Scrum inspects progress and plans the next day. AR 25-50 puts the bottom line up front. The UK
IPA delivery-confidence guide joins criteria with judgement and rates the current trajectory
(snippet only). APM: define RAG criteria per project (snippet only). Microsoft's event-sourcing
pattern: snapshots every N events, upcasters on schema change. Veeam: a corrupt increment drops
that point and every later one. The deep-research skill was not used; a research agent searched
and fetched pages, and the Brysbaert figure was checked first-hand.
