# Plan 232 -- the standup-report family, store half (SR9, SR23, SR24, SR29, SR46)

> Status: DONE 2026-11-16 on branch `feat/standup-report` (commit below). Program record and
> rulings: [standup-2026-11-record.md](evidence/standup-2026-11-record.md). ADR:
> `docs/adr/adr-0003-standup-reports-are-stored-records.md`.

- **First, a measurement** on scratch copies of five ACMP revisions: a daily row of the approved
  shape is 14.8-20.8 KB, over the plan's 15 KB stop line. The operator kept the shape and set
  the limit at 25 KB (SR48). The first report is ~506 KB, under its 1 MB line.
- **Migration 011.** `standup_reports` (`RPT-`, On-request): kind, Draft/Approved/Superseded,
  base and supersedes (self references), checkpoint, `pe_to`/`av_to`, `ended_at`, `utc_offset`,
  `state_digest`, `state_delta`, `facts`, `narrative`, `rule_colour`, `colour`, recorder,
  words, time. A row-local CHECK: a recorded row carries a narrative, a colour and the
  operator's word. Partial unique indexes: one draft, one recorded daily report per `pe_to`.
  Triggers: the index pair, immutability (only Approved -> Superseded, `last_referenced` stays
  writable), a draft moves only to Approved, only a draft is removed.
- **Server.** Registry rows; `_REPORT_COLUMNS` and the prose-id exemption for the family;
  `entity_upsert` refuses it; a default `entity_query` read leaves out `state_delta` and
  `facts` (the description says so); `package_open` returns a refusal that names the file and
  line when the store refuses a row, where it raised before.
- **Store.** `load` names the file and line of a row that a constraint refuses.
- **Review page.** The family's table leaves out its JSON columns and the operator's words.
- **Docs.** ADR-0003, one line in ADR-0001, the catalog (family row, file row, views note),
  governance (identifier row and a lifecycle section), the naming template, `docs/entities.md`,
  `CLAUDE.md`, the CHANGELOG under Unreleased, lint 12's prefix list, guide prose for 23 ids in
  both languages and the table/family/migration counts. The guide's line citations re-aimed
  with `shift_221.py` (none unmapped).
- **Tests.** `StandupFamilyTest` (10): registry, class and head; the trigger names every column;
  immutability and draft moves; one draft and one chain link (an override sits outside); a
  merged store with two drafts is refused with `standup_reports.jsonl:2` and holds no lock;
  the upsert refusal; the lean default read; no grading and no prose-id scan; the review page
  without the payload; registry-sync teaches the family to an older package.
  Pins moved: schema 10 -> 11, head 011, tables 44 -> 45.
- **Review (a code-review agent, then fixed):** a blank narrative passed the record CHECK (now trimmed); a report could be superseded with no successor, which emptied its chain link (trigger `trg_standup_reports_successor`); `search` and `context` read the payload a default read leaves out (now excluded); the load refusal named the standup skill for every foreign-key failure (now only for its file). Each has a test.
- **Check:** `python check.py` green on Python 3.13, on 3.10 (uv's 3.10.19), and with
  `PYTHONWARNINGS=error::DeprecationWarning`.
