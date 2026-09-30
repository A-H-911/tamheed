# The operator's words for the real-agent lab runs (plan 172, R60)

The only words the harness operator (the maintainer, driving the runs by hand) may give a headless
agent, in the prompts or in a `--resume` turn. Anything an agent asks that no line here answers is
answered "not scripted; record it as an open question to the operator and continue" — and the
question is quoted in the acceptance report. At most three resumes per session.

## Standing preamble for every `--resume` turn

> The MCP server restarted between turns (each turn is a new client process). The package is
> closed and its lock names the previous turn's process. On my word: `package_unlock` with
> `confirm: true`, then `package_open`, then continue from where your last report stopped.

## Run A1 — planning (scenario items 1–5)

- Charter, executive summary, requirement rows, phase plan, slices, acceptance criteria and
  tests: **approved as written**, on the operator's word given here in advance.
- The recurring-tasks ambiguity: **do not resolve it.** Record the `OQ-` with owner
  `operator` and `due_by` one month from today; mark the requirement `[NEEDS-CLARIFICATION: OQ-NNN]`.
- The storage fork: file-on-disk stays a `DEC-`; the persisted record's schema is load-bearing —
  promote that to an `ADR-`. **Confirmation words for the ADR:** "The operator confirms the
  persisted-record schema ADR as written, 2026-10-01, lab run A1."
- The `ready` gate: "operator confirms the seed tests were triaged" — `human_required`. The
  `approval` gate: "operator approves the phase for execution" — `human_required`.
- Hand off into the executor workspace the prompt names, then `package_close`.

## Run A2 — execution (scenario items 6–9)

- **The scope change (item 7):** "Approved: take on `tick export --csv` as SC-001, apply the rows
  it names, set it Merged." (given only after the agent has STOPPED with the SC- row Proposed)
- **The waiver (item 8):** "Approved: WVR- for the help-text typo defect, terms: stays open until
  the next release, reviewed by the operator; expires 2026-12-31."
- **The forced transition (item 8):** "Force it: move SL-002 to Implemented with `force: true`,
  operator's words 'force SL-002 Implemented, lab run A2, the unverified criteria are accepted as
  the operator's risk'." (given only after the guard has REFUSED once)
- The gates (item 9): "`ready`: outcome pass, the seed tests were triaged (DEF rows exist).
  `approval`: outcome pass, the operator approves."

## Run B — four short sessions on a copy of the fixture

- B1's feedback row: "Confirmed: the feedback row you proposed, on the operator's word, lab run B1."
- **The planted question, B1 (never answered in B2–B4):** the prompt asks the agent to put ONE
  question to the operator — "Should the lab tracker's export write UTF-8 with a BOM for Excel?" —
  and to carry it in the handoff as awaiting the operator. No later turn answers it.
- B3's lesson: "Confirmed: the lesson you proposed, on the operator's word, lab run B3."
- B4: "Act on what `handoff-repeated` names as `tamheed:session-handoff` says; the operator gives
  no answer to the planted question."
