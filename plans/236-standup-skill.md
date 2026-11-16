# Plan 236 -- the `/tamheed:standup` skill (SR31, SR32, SR33, SR34)

> Status: DONE 2026-11-16 on `feat/standup-report`. Record: [standup-2026-11-record.md](evidence/standup-2026-11-record.md).

`plugins/tamheed/skills/standup/SKILL.md`, a scenario skill (`disable-model-invocation: true`,
`argument-hint: "[package] [since: date or RPT id]"`) that reads its bound prompt rows. Steps:
open and read the resume block; offer `/tamheed:progress-sync` when the store looks behind; draft
the facts (the first report asks the offset); write the narrative under `tamheed:plain-english`
with the default colour rule (an argued exception carries its reason, a non-green colour a road
to green); draft with the narrative and fix refusals; show the chat summary and the absolute
path and open the browser (headless: the path only); ask record, revise or discard with the
operator's words; record; export `review.html`; propose one commit and run it on a yes; close.
The merge repair: two draft lines, remove one; two recorded rows for one `pe_to`, keep the one
whose page is committed and set the other to `Superseded`, then open and verify.

- Also: the "Which skill, when" row in `prompts/README.md` with its `stock-history.json` append,
  `workflow.md` stage 21, `package-writes`, skill prose in both languages, the pins (28 skills,
  18 scenarios, 17 bound-row scenarios).
- **Check:** a dry run of the steps on a scratch lab copy before the text is written; lints 9,
  12 and 14. **Expected:** the dry run records RPT-001 on the copy.

## As built (2026-11-16)

- `skills/standup/SKILL.md`: the ten steps, a correction, and the fix for a store that a merge
  broke. Lints 9, 12 and 14 pass.
- **The dry run on a scratch lab copy** (`plans` scratch, in process): registry-sync, facts, a
  narrative, the record and `export_html` gave `RPT-001.html` with `live_match` true. It found
  that the lab's rule colour was red only because `acs-met` fails while two checks are not Met.
  The 5 package-scope blocking rules test whether the package can CLOSE, and they fail during
  normal work. The operator ruled (SR51): they are not a colour input. The page lists them under
  "Not ready to close yet". Red is an open critical or high defect. The lab now reads amber,
  for its overdue question.
- **Counts and pins:** 28 skills, 18 scenarios, 17 skills that read bound rows. The Arabic text
  had said 25 and sixteen; both languages now say 28 and eighteen. Prose counts
  in the READMEs, `docs/`, the references and the front door.
- The "Which skill, when" row in the stock guide, with its body appended to
  `stock-history.json` under 6.6.0 in the same commit. `workflow.md` stage 21 and
  `package-writes` name the tool.
- **Check:** `check.py` on 3.13 and 3.10 and with deprecations as errors.
