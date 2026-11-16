# Plan 235 -- the `standup_report` tool, the resume line, the docs (SR6, SR20, SR22, SR26, SR30, SR47)

> Status: PLANNED. Record: [standup-2026-11-record.md](evidence/standup-2026-11-record.md).

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
