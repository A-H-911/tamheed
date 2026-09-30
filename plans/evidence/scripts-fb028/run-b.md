# Run B — four short headless sessions on a copy of the fixture (plan 172, R60, W150)

Each session (B1–B4) is its own conversation; each turn is a NEW client process (`labrun_turns.py`,
run labels `b1`…`b4`). A session's first turn is the slash command `/tamheed:orient-resume
package` (the operator-only skill, typed by the harness operator); its task is the second turn,
a `--resume` opening with the standing preamble from `run-words.md`. B4 has a third turn for
`/tamheed:register-liveness package` before its task. The package is `package` under the
workspace; the actor for every write is `agent:lab-run-B`.

## B1-T1 — `/tamheed:orient-resume package`

## B1-T2 — words

{PREAMBLE}

Your task this session, on the operator's words: (1) propose ONE feedback row about the Tamheed
plugin from your own experience of this session so far — `kind: "question"`, a title and a detail
that state what you actually met, `plugin_version` from `server_info` — then move it to
`Confirmed` on this word of the operator: "Confirmed: the feedback row you proposed, on the
operator's word, lab run B1." (2) Put ONE question to the operator, exactly this one, and do not
answer it yourself: "Should the lab tracker's export write UTF-8 with a BOM for Excel?" Record it
as an open question row (`OQ-`, owner `operator`, `due_by` one month from today) and carry it in
the handoff as awaiting the operator. (3) Write the handoff LAST, as `tamheed:session-handoff`
says. (4) `package_close`. Final message: the ids you wrote, in order, and one line on anything
the plugin refused.

## B2-T1 — `/tamheed:orient-resume package`

## B2-T2 — words

{PREAMBLE}

Your task this session, on the operator's words: (1) one journal note (`progress_update`,
`event_type: "note"`) saying what the resume block showed you and whether the previous handoff's
lines were still true. (2) A plain `handoff_emit` into this workspace (target `.`, no
`refresh_stock`) and its report quoted in one line. (3) Write the handoff LAST, as
`tamheed:session-handoff` says; the operator's question from the previous session is still
unanswered. (4) `package_close`. Final message: the ids you wrote, in order.

## B3-T1 — `/tamheed:orient-resume package`

## B3-T2 — words

{PREAMBLE}

Your task this session, on the operator's words: (1) propose ONE lesson row (`LL-`) from what
the sessions before you recorded in the journal — a lesson about working a Tamheed package
headless — written `Proposed`; then approve it as the skill and the engine require, on this word
of the operator: "Confirmed: the lesson you proposed, on the operator's word, lab run B3." (2)
Write the handoff LAST, as `tamheed:session-handoff` says; the operator's question is still
unanswered. (3) `package_close`. Final message: the ids you wrote, in order, and the lesson's
lifecycle status as the engine returned it.

## B4-T1 — `/tamheed:orient-resume package`

## B4-T2 — `/tamheed:register-liveness package`

## B4-T3 — words

{PREAMBLE}

Your task this session, on the operator's words: (1) `readiness_check("package")` and quote
every advisory that is not clean, `handoff-repeated` among them with what it names. (2) Act on
what `handoff-repeated` names exactly as `tamheed:session-handoff` says — re-measure each named
line at its source and say what you found; the operator gives no answer to the planted question.
(3) `export_html`, then `package_verify` and quote `review_current` and `review_exported_by`.
(4) Write the handoff LAST, as `tamheed:session-handoff` says. (5) `package_close`. Final
message: what `handoff-repeated` named, what you did with each line, and the verify keys.
