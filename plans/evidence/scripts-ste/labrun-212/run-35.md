# Run 35 — lab beat 35 (plan 212): a fresh repository with no CLAUDE.md, wired at the package's birth

One headless conversation on a scratch repository built from the lab seed (`beat35_setup.py`), three
turns, each turn a NEW client process (`labrun_turns.py`, run label `r35`). Every turn is the
operator's words. The package is `lab` under the workspace root; the actor for every write is
`agent:lab-beat-35`. The workspace holds `tracker.py`, `test_tracker.py` and `brief.md`, and no
`CLAUDE.md`. One plain command per tool call. Write no file yourself: the tamheed tools write, and
you read what they wrote.

## T1 — words

Your task this session, on the operator's words. This repository has no `CLAUDE.md`. (1) Confirm it:
list the files at the workspace root. (2) `package_create("lab", "Lab tracker", "rnd", "full")`.
Quote, from the tool's own result, the `wiring` object word for word. (3) Read the workspace root's
`CLAUDE.md` and quote it whole. Read `lab/CLAUDE.md` and quote it whole. (4) One journal entry with
`progress_update`: event_type `handoff`, actor `agent:lab-beat-35`, entry exactly "Resume at: stage 1
(intake). The brief is brief.md at the workspace root; nothing of it is archived yet. Awaiting the
operator: the mode." (5) `package_close`. Final message: the quoted `wiring`, the two files quoted,
the journal id, one line on anything the plugin refused.

## T2 — words

Your task this session, on the operator's words. Before any tool call: quote, word for word, every
line the tamheed SessionStart hook put into your context at the start of this session (the block
that opens "tamheed resume"). If no such block is in your context, say so in one line and stop.
Then: (1) `package_open("lab")`. Quote the result's `wiring` object and the `resume` block's `half`
and `next` values word for word. (2) `package_close`. Final message: the hook's block as quoted, the
`wiring`, `half` and `next` values, one line on anything the plugin refused.

## T3 — words

Your task this session, on the operator's words. After the unlock on my word and `package_open("lab")`:
(1) `entity_upsert` one prompt row: type `prompt`, id `PRT-001`, kind `kickoff`, title "Kickoff",
body "Start with the brief: archive it, then classify.", lifecycle_status `Approved`. The operator's
word for the approval: "The operator approves PRT-001 as the kickoff, 2026-10-08, lab beat 35." Then
`entity_upsert` the package header: type `package`, entry_point `PRT-001`. (2) `handoff_emit` on the
workspace root (the folder holding `CLAUDE.md` and `lab/`). Quote every `warnings` line from the
tool's own result, and the `written` and `unchanged` lists. (3) Read `lab/CLAUDE.md` and report how
many times the text `<!-- tamheed:note` occurs in it, and whether the words "planning half is in
progress" still occur. Read the workspace root's `CLAUDE.md` and quote it whole. (4) `server_info()`:
quote the `resume` block's `half`. (5) Write the handoff LAST, as `tamheed:session-handoff` says; the
actor is `agent:lab-beat-35`. (6) `package_close`. Final message: the quoted warnings and lists, the
two counts, the root file quoted, the `half`, one line on anything the plugin refused.
