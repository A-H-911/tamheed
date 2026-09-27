# Lab continuation report — beat 27 (plan 149, v5.5.0)

> 2026-09-27. Harness: the engine's tool functions in-process, the same code path the MCP tools
> call. The scratch phase ran FIRST on a copy that is never committed; the fixture was written
> after it held. The operator's trace variable was removed before the engine was imported.
> Scripts beside this report: [`scripts-findings-36/`](scripts-findings-36/).

## Runs

| Run | Window (UTC) | Result |
|---|---|---|
| 1 | 20:33:38–20:33:39 | stopped in the scratch phase: the harness compared `changed_columns`, a list of objects, as a list of names |
| 2 | 20:34:05–20:34:07 | stopped in the scratch phase: the harness expected three changed columns; the row sent no `confirmed_at`, so two moved |
| 3 | 20:34:24–20:34:26 | stopped in the scratch phase: the late approval omitted the stored `recorded_at` and the engine refused it as content drift |
| 4 | 20:34:43–20:34:45 | every assertion held in both phases |

Runs 1 to 3 failed before the fixture was opened. `git status` showed no change under `evals/`
after each. Runs 1 and 2 were the harness's errors. Run 3 was the engine refusing a wrong write by
name, which is its job; the scenario item records the rule.

## Scratch phase (hard assertions)

| Observation | Value |
|---|---|
| The note before any new lesson | lists the one Approved lesson; no footer |
| The approval hint | `this lesson binds from this write and is RENDERED only once the always-loaded note is rebuilt - run handoff_emit in this same batch (the note is rebuilt by nothing else); it renders in the note only if pinned or among the 10 newest unpinned Approved rows - pin it to keep it visible` |
| Columns an approval moved | `lifecycle_status`, `confirmed_by` |
| Two approvals, no emit yet | the page marks three rows `rendered`; the note on disk lists one |
| The page's own sentence | `it is what the next handoff_emit renders` |
| A statement that opens with its story | rendered as the story, cut to 177 characters and an ellipsis; its rule is not in the line |
| A statement that opens with its rule | the rule is in the line |
| Eleven unpinned Approved lessons | the note lists the ten highest-numbered; the oldest is absent |
| The footer | `1 more Approved lesson(s) bind too and are not rendered here` |
| The page at eleven | ten rows `rendered`, the oldest `not rendered` |
| The Approved query at eleven | returns eleven |
| The oldest pinned on the operator's word | `pinned` alone changed; first line of the note; eleven lines; no footer |
| A lesson numbered below the ten, approved late | absent from the note; `not rendered` on the page; returned by the Approved query |
| `lessons-note-budget` | `pass` |

## Fixture phase

| Observation | Value |
|---|---|
| `server_info` | 5.5.0 / `007_handoff.sql` / schema 7 |
| The resume block at open | beat 26's final handoff, `handoff_behind` 0 |
| `handoff_emit(refresh_stock=true)` | `refreshed ["prompts/README.md"]`; every scan empty |
| The guide | reads `tamheed v5.5.0` and states the roster |
| The note | lists the one Approved lesson; no footer; the second emit reports it unchanged |
| The beat's note and final handoff | two journal entries, the handoff written last |
| `handoff-current` | `pass` |
| `review.html` | the Approved fold carries `note (rendered at the next emit)`; the one row reads `rendered` |
| `gate_run` | ready |
| `package_verify` | `verified` true, `dirty` [], `foreign` [], `review_current` true |
| The lock after close | gone |

## What the fixture does not cover

The fixture has one Approved lesson. Its note never prints the footer and its page marks one row.
The footer, the push-out, the pin and the late approval are covered end to end by the scratch
phase and by the contract suite, not by the committed fixture or its eval assertions.

## Files the beat changed

| File | Change |
|---|---|
| `package/data/progress_entries.jsonl`, `package/csv/progress_entries.csv` | two entries |
| `package/prompts/README.md` | the 5.5.0 stock guide |
| `package/review.html` | the digest, the freshness stamps, the journal, the resume section, the Lessons section's fold |

`evals/sample-results/minimal-brief/package/review.html` was not touched. It is a record from the
first eval commit, asserted by existence only.
