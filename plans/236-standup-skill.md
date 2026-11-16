# Plan 236 -- the `/tamheed:standup` skill (SR31, SR32, SR33, SR34)

> Status: PLANNED. Record: [standup-2026-11-record.md](evidence/standup-2026-11-record.md).

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
