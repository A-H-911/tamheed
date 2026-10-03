# Plan 190: the ACMP brief for 5.9.0

> Maintainer-executed, 2026-10-04. Batch map: [176-191-batch-ste.md](176-191-batch-ste.md).
> Source: R20 (the brief's classes and its STOP), R53 (no report unless a class fails), R9 (the
> brief owns the class-5 change: the note changes to v6), R45 (the rewrite skill's path for Approved
> rows), the memory rule that every recipe of a brief runs on a `git archive` copy first.

## Status
- **Priority**: P1 - **Effort**: M - **Risk**: LOW-MEDIUM (a brief under the strict rules; the replay on the field copy) - **DONE 2026-10-04** (the commit this ledger lands in, after the operator's review)

## Scope

1. `plans/briefs/acmp-5.9.0.md`, written in plain English under the strict rules, rostered by explicit
   path in `check.py` `_STE_SURFACES` (`_ste_scope` admits a rostered file under an exempt prefix).
   Classes: the update and the client-restart route (carried from 5.8.1's O21/O22). No migration,
   `schema_version` 7. `handoff_emit(refresh_stock=true)`: the stock README refreshed to the 5.9.0
   body, the note rebuilt as v6 (this brief owns class 5 of 5.8.1: "the note changes in no string" no
   longer holds). `export_html`: meta 5.9.0. `readiness_check`: `prose-plain-english` advisory with its
   counts, `ready` unchanged. `ste-clean` over the project's prompt folder. The two skills:
   `tamheed:plain-english` in context, `/tamheed:ste-rewrite` in the menu, `GT-` rows extend the
   vocabulary, R45's path for Approved rows. The STOP: ACMP's operator chooses whether to run the
   rewrite. No report unless a class fails (R53).
2. Every prescribed read and write rehearsed on a `git archive` copy of ACMP first; the numbers in the
   brief are the copy's.
3. `tests/test_check_lints.py` `test_current_brief_is_in_the_roster`: a `;` appended to the 5.9.0 brief
   is caught by lint 14; the 5.8.1 brief is not scanned.
4. The guide's release recipe gains step 9, "roster the new brief's path in lint 14" (EN + AR);
   `index.html` rebuilt.

## The replay (`plans/evidence/scripts-ste/acmp_replay10.py`, the copy at `8b7d8bd1`)

| Class | On the copy |
|---|---|
| 1 `server_info` | `5.9.0` / `007_handoff.sql` / `7` |
| 2 `package_verify` before any write | `verified`, `review_current true`, `review_exported_by "5.8.1"`, `dirty []` (the field's tree held uncommitted changes to three JSONL files, outside the archive) |
| 3 `readiness_check` | `ready false` (`acs-met`, the field's own), 24 advisories; `prose-plain-english` fail: 2,342 semicolons, 3,602 long sentences, 631 vocabulary, 1 marketing adjective, 1,290 texts, 1,146 named, 50 shown; the note ends with the skill cue |
| 4 `handoff_emit(refresh_stock=true)` | `refreshed ["prompts/README.md"]`, `retired []`, `customised null`; the guide's first line carries 5.9.0 and names nine discipline skills; the note v5 → v6, 41 lines before and after, 14 changed, first sentence names the package, names `tamheed:plain-english`; the copy's standalone server also wrote `.mcp.json` (a plugin-hosted one writes none) |
| 5 `export_html` | numstat 5 / 4, 10,929 patch bytes, longest added line 2,512, `csv/` unchanged, `review_current true`, `review_exported_by "5.9.0"`; the rule's counts unchanged by the emit |
| 6 the hook | over the v6 note after `compact`: exit 0, 21 lines, 2,212 chars, `version=5.9.0 source=compact`; over the same v6 note at `startup`: 20 lines, 2,056 chars; over an untouched v5 note at `startup`: 20 lines, 2,056 chars. The extra line is the event's, not the note's (the advisor's read caught the first framing) |
| 7 the wire | `entity_query` 387, `progress_update` 333, `audit_record` 325, `handoff_emit` 155, each equal to `TOOLS[name][1]`; against v5.8.1, 8 of the 19 descriptions changed in text (the three contract ones among them, at equal lengths) and 11 are unchanged |
| `ste-clean` | before the emit exit 1, 73 hard on the 5.8.1 guide; after, exit 0; four project files skipped by name |

## Kept as-is
- The brief's blockquote follows the rules too (R42). Its numbers are the copy's, never the field's text.
- No write to the field's record is prescribed. The STOP is the operator's and "no answer is also an answer".

## Validation
- Red: the roster entry before the brief exists; the new lint test before the scope tweak.
- Green: `python check.py`; the brief strict-clean; the replay's observations in the ledger.

## Rulings taken at the review (2026-10-04)

- Approved and committed as staged.
- R47: the STOP carries the maintainer's recommendation, marked: `GT-` rows first, then Draft and
  Proposed rows, immutable rows only on opt-in.
- R48: O23 records its second half, the first gap a real agent found that a scripted beat could not.
