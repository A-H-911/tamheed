# Plan 237 -- the standup rehearsal with a real headless agent (2026-11-16)

A scratch copy of the lab-tracker fixture, the working-tree bundle through `--plugin-dir`, Claude
Code 2.1.325, Opus 5.5, `--setting-sources ""`, `--permission-mode dontAsk`. The harness is
`plans/evidence/scripts-fb028/labrun.py`; the workspace, the work between reports and the checker
are `plans/evidence/scripts-237/rehearse_237.py`. The operator's answers were scripted, and each
prompt says so. Six sessions, ten turns, 3.20 USD.

| Report | What the agent did |
|---|---|
| RPT-001 (first) | Asked whether the store was behind (it named the setup commit that no bind names) and asked for the UTC offset, writing nothing. On the answers: drafted, was refused once for a sentence over 25 words, split it, shortened a headline over its share, recorded amber (an overdue question), exported `review.html`, closed. It warned that `data/` commits the operator's words. |
| RPT-002 (second) | Saw the work added between reports: a journal entry, a Met and a Not-met verdict, a bind, a high defect, a reworded requirement. It noticed that the bind names a commit (`abc1234`) that is not in the history. Recorded red (the high defect). The harness lost the session id for this turn, so it ran as a NEW session without the skill: the agent recorded correctly from the tool's description alone, and it skipped the `review.html` export (a skill step) and named the operator `human:operator`. |
| RPT-003 (correction of RPT-002) | Took the correction route from the skill: the same window, the same facts, new words. RPT-002 moved to Superseded. |
| RPT-004 (override from RPT-001) | `/tamheed:standup package RPT-001` made an override. Recorded; it is outside the chain. |
| RPT-005 (third daily) | Its base is RPT-003, the correction, not the override. Recorded red. |

**The checker** (`rehearse_237.py check`): no failures.
- The chain RPT-001 → RPT-003 → RPT-005 replays, and every recorded report verifies.
- Visible words: 583 to 754 on the daily pages, 1,267 on the first (exempt).
- No script and no outward link on any page. The operator's words are on no page and in no
  journal row.
- The standup journal rows are notes only. The reworded requirement is listed as edited.
- `package_verify` passes.

**Not measured:** the number of draft calls per report. The transcripts show at most two
narrative attaches on any report (one refusal on RPT-001).

**Lessons for the harness:** read the session id from the run folder, never through a path that
the shell rewrites (`/c/...` against Windows Python). A failed lookup silently starts a new
session.

## The field briefs, measured and rehearsed (2026-11-16)

**Measured** (`scripts-237/measure_briefs_660.py`, `wayback_660.py`) on a scratch export of ACMP's
commit `208c7f2e` and on a copy of Jisr's export of 2026-11-12. The route held on both: the
registry-sync, the stock guide, a first report recorded with `live_match` true, `package_verify`
clean. **The way back found a fault before the release:** the record's journal note named the
report as its `subject_id`, a foreign key that 6.5.1 cannot resolve, so 6.5.1 refused to load a
store with a recorded report. The note now names the report in its attributes only. After that,
6.5.1 opens both stores, reads the same gates and moves no file. Its `package_verify` names
`standup_reports.jsonl` dirty, and removing that file gives a clean verify.

**Rehearsed** by a headless agent on a scratch repository of each field, the bundle loaded:

| | ACMP (`acmp-6.6.0.md`) | Jisr (`jisr-6.6.0.md` with `jisr-6.5.1.md`) |
|---|---|---|
| Sessions, cost | 2, 1.98 USD | 1, 1.78 USD |
| Result | Every class held. It stopped once at a root `.mcp.json` and filed a row, as the brief said: the rehearsal's own artifact (the bundle loads from a local folder). The brief now says so, and the row was rejected on the scripted word | Every class held, every STOP held, no feedback row resolved without the word |
| The report | RPT-001 green. The narrative check refused two ids that the agent had made up | RPT-001 amber (10 high risks, 1 overdue question), the three release rules listed |
| Folded into the briefs | sizes as ranges (the commit moved), `reports/.gitignore`, the csv files of the written tables | the same |
