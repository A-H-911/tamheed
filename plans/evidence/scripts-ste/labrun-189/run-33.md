# Run 33 — the scratch phase of lab beat 33 (plan 189): `/tamheed:ste-rewrite` by a real agent

One headless conversation on a scratch copy of the fixture (`beat33_setup.py`), two turns, each
turn a NEW client process (`labrun_turns.py`, run label `r33`). The first turn is the slash command
typed by the harness operator; the second is the operator's words, opening with the standing
preamble from `run-words.md`. The package is `package` under the workspace; the actor for every
write is `agent:lab-beat-33`. Nothing of this run is written to the fixture.

## T1 — `/tamheed:ste-rewrite package`

## T2 — words

{PREAMBLE}

Your task this session, on the operator's words, continuing the `/tamheed:ste-rewrite` run you
started. Your Q0: (a). The operator's word: "Approved: an Approved row of a family with no
supersession column (FR, NFR, ASM, DEC) is rewritten in place and stays Approved when the change
is punctuation or a sentence split, with expect_unchanged on every column you do not touch, lab
beat 33." (1) Apply exactly ONE such in-place rewrite: batch 1 row 5, `ASM-001.statement`, as you
proposed it. (2) Apply exactly ONE supersession: batch 1 rows 2-4, ADR-0001 superseded by
ADR-0002 as you proposed it. Then approve ADR-0002 on this word of the operator: "The operator
confirms ADR-0002 as written, 2026-10-04, lab beat 33." Skip every other row of batch 1. Skip
AC-002, LL-004 and LL-001 as you proposed. (3) Re-run `readiness_check("package")` and quote,
from the tool's own result, the `prose-plain-english` counts before and after and the
`adrs-approved` status. (4) Write the handoff LAST, as `tamheed:session-handoff` says; the actor
is `agent:lab-beat-33`. (5) `package_close`. Final message: the ids you wrote, in order; the two
counts; one line on anything the plugin refused.
