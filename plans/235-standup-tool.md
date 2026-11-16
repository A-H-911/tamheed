# Plan 235 -- the `standup_report` tool, the resume line, the docs (SR6, SR20, SR22, SR26, SR30, SR47)

> Status: DONE 2026-11-16 on `feat/standup-report`. Record: [standup-2026-11-record.md](evidence/standup-2026-11-record.md).

- **SR47 first, red:** a handoff id like `PE-1x` written through `entity_upsert`, then
  `package_open`. If it raises, `int(id[3:])` at the resume block and the `handoff-current`
  rule reads the SQL number; if it does not, the item is dropped and recorded.
- **The tool** `standup_report(action="draft", narrative=None, start=None, utc_offset=None,
  supersede=None, confirm=None)`: draft (facts), draft with a narrative (checks, page), record
  (the operator's word, the digest check, `reports/RPT-NNN.html`, one transaction with the
  journal note signed `system:standup-report` that names the report and the recorder, never
  the words), discard. A test pins that the words reach neither the journal nor any page. Every refusal of the approved plan.
  Its description at most 2,048 characters; `GROUPS["staged"]`; `TOOL_EFFECTS`; four figures.
- **Resume block and hook:** one line naming the last recorded report, silent without one.
- **Docs:** the server and root README tool rows, `SECURITY.md` (the page's trust model, the
  operator's word, immutability), `docs/architecture.md`, `references/generated-structure.md`
  (`reports/`), tool and parameter prose in both languages, pins 21 -> 22 tools.
- **Check:** the contract tests of the approved plan (window fixed at draft, the first report
  asks the offset, re-draft and discard, the record's word checks, the note row moves no
  handoff count, immutability with work_bind still stamping, a correction keeps the window and
  the delta, drift refused, moves after the draft reported, a checkpoint every 30th report, a
  forced re-baseline, the resume line, the description cap); the selftest 22/22;
  `build.py --check`. **Expected:** green; SR47 fixed or recorded as not reproduced.

## As built (2026-11-16)

- **SR47 reproduced and worse than reported:** a `PE-1x` handoff made `package_open` raise
  and leave the lock behind, and `readiness_check` raise. The red test came first. A grep found
  a third site in `package_migrate`. `_pe_num_of` reads the number by SQL, as the order does.
- **The tool:** `standup_report` with draft (facts), draft with a narrative, record, discard,
  and every refusal of the plan. The record writes the page, then in one transaction moves a
  corrected report to Superseded, records the draft and journals a note signed
  `system:standup-report` that names the report and the recorder, never the words.
- **Resume block and hook:** `standup` names the last recorded daily report, and the hook
  prints one line, silent without one.
- **Docs:** both README tool rows, `SECURITY.md`, `docs/architecture.md`,
  `generated-structure.md` (`reports/`), the guide (group `staged`, effects, tool and 6
  parameter texts in both languages, 22 tools).
- **Review (a code-review agent):** a flush failure after an applied commit deleted the
  recorded page (it now keeps it); a report whose base was corrected could not be corrected
  (a base is resolved by its place in the chain now, `at_place`). Both have tests.
- **On a scratch copy of the first field's package:** registry-sync, the first report drafted,
  worded and recorded (`live_match` true), page 462 KB with 2,280 visible words (exempt), row
  502 KB. The facts call returns 58 KB to the agent on that first report.
- **Check:** contract tests (13 for the tool, 1 for SR47, 1 hook test); the selftest 22/22;
  `check.py` on 3.13 and 3.10 and with deprecations as errors.
