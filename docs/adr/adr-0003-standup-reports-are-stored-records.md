---
status: Approved
date: 2026-11-16
id: ADR-0003
supersedes: ADR-0001 (partially — the "never stored snapshots" clause, for standup reports only)
superseded_by: none
---

# ADR-0003 — Standup reports are stored records

## Status

Approved (maintainer, 2026-11-16 — an eleven-round interview, a devil's-advocate review, and
49 rulings filed as SR1–SR49 in `plans/README.md`; plans 232–237, release 6.6.0).

## Context

The operator asked for a standup report on demand. It covers the window from the latest
recorded report to now and answers three questions: what we did, the challenges and
decisions, and what we expect to do next. The operator, the team and a manager read it in 5 to
10 minutes.

ADR-0001 §2 (C1) says: "traceability matrix, status report, execution backlog … are SQL views —
never stored snapshots. Files rendered from them are exports." A view cannot answer "what
changed since the last report", because the store keeps current state only:

- Only the journal (`PE-`) and the verdicts (`AV-`) carry server-assigned, increasing ids and
  times. Every other family keeps its current status and no history.
- Most status moves are never journaled. Measured on the lab-tracker fixture: 47 rows moved
  past Draft, Proposed or Open, 29 have no journal row about them, and 15 are named in no
  journal text at all.
- Rows change their wording without a status move. Measured in the first field's history
  (9–15 Nov 2026): 0 to 15 such rows a day.

A standup report must also stay as it was said, and the operator records it in their own words.
That is a record, not a derived view.

## Decision

1. **A new family**, `standup-report` (`RPT-`, table `standup_reports`, migration 011),
   On-request. The `standup_report` tool writes it, and `entity_upsert` refuses it.
2. **Deltas, checkpoints and replay.** The state of a package is one value per row: its status
   and a 12-hex fingerprint of its content. The fingerprint skips null values and
   `last_referenced`. Each report row stores only the changes of its window (`state_delta`),
   with each table's column list. The first report, and every 30th recorded daily report, is a
   checkpoint that stores the full state. The state at any report is a replay from the latest
   checkpoint.
3. **Every link is checked.** Each row stores the digest of the state its draft saw. Replay
   compares each link with its digest, and the first mismatch names the report. On a broken
   link the next report is a checkpoint, and its page says that the changes across the broken
   links are unknown. A stored delta is never edited.
4. **The window end is fixed at the draft.** Recording checks that the replay plus the row's
   delta gives the digest the draft saw. Rows that moved after the draft are reported, never
   refused: they belong to the next window.
5. **Facts are frozen at the draft.** The row keeps what its page prints: ids and titles, at
   most 30 items per list (the first report keeps every item). The page
   `reports/RPT-NNN.html` is the export of its row, and it is committed.
6. **Draft → Approved → Superseded.** Recording takes the operator's word (`operator_confirm`,
   who, and what they said). The words are stored in the row only: the journal note names the report and who recorded it, and no page prints them. Approved and
   Superseded rows are immutable, by a trigger. A correction is a new row over the same window:
   it copies the window, the delta and the facts, and only its words differ.
7. **Overrides stay outside the chain.** A report that starts at an earlier date or report is
   recorded with kind `override`. It never starts the next window, and the replay never reads
   it.

## Scope of supersession (what of ADR-0001 survives)

Only C1's "never stored snapshots" sentence is superseded, and only for this family. The
traceability matrix, the backlog, the readiness report, the phase-exit report, the identifier
counts, the artifact membership and `v_status_report` stay SQL views. `review.html` stays a
derived export. Everything else in ADR-0001 survives.

## Consequences

- **Size** (measured on the first field's data): a daily row is 15 to 21 KB, about 6 MB a year
  at a daily cadence. The first report is about 0.5 MB once, and a checkpoint about 60 to 120 KB.
  The field's whole store was 13 MB at the time.
- **Limits.** The report sees new rows, status moves and content fingerprints. It never sees
  work nobody synced into the store, or a commit nobody bound. The page says so.
- **A column a release adds** changes no fingerprint while its values are null. A table whose
  column list changed has its edit tracking paused for one report, with a note.
- **A correction fixes words, not facts**, because it copies the frozen facts.
- **A git merge** that leaves two drafts, or two recorded reports for one window, fails the load
  on a unique index. The `standup` skill names the manual repair.

## Alternatives rejected

- **A full snapshot in every row:** about 33 KB per report and about 12 MB a year on the first
  field, loaded on every open.
- **A status-history table written by every writer:** a MAJOR change that touches every write
  path, and past moves would still be lost.
- **A view over the journal:** it misses every move that nobody journaled (29 of 47 in the lab).
- **A sidecar state file per report:** the same growth in git, and a deleted file breaks the
  next diff.

## Confirmation

`tests/test_standup.py` (state, diff and apply, replay with per-link checks, checkpoints, the
window, the page and its word budget) and the standup tests in `tests/test_mcp_contract.py`
(the trigger names every column, the load refuses two drafts and two chain links, the upsert
refusal, the lean default read, the record checks). The plan-237 rehearsal records three
reports, a correction and an override with a real agent.
