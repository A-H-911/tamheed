---
name: operator-interview
user-invocable: false
description: >-
  Use whenever something needs the operator — a decision that is theirs, an action only they can take,
  a confirmation or an approval (a scope change, a waiver, a forced transition, a lesson, a feedback
  row, the `go_no_go` header field, an unlock), a ruling on a register row — and before building any
  slate, question, option list or recommendation for them. Also use before relying on an answer they
  gave earlier.
---

# Interviewing the operator

**Ask now, ask prepared, ask from the record — and ask again next time.**

When work reaches the edge of the operator's authority, the risk is not a wrong decision. It is a
stall nobody sees, a question the operator cannot answer from the page in front of them, or a decision
made on a sentence that was never true. None of this is caught by a gate: the report reads as complete
and every id resolves.

## What is theirs alone

Among the Tamheed ceremonies with a STOP, each is an interview and its word is a JSON boolean or a
status they spoke: `operator_confirm: true` (a lesson approved or promoted, moved OFF Approved, or its
`superseded_by` repointed while binding; a feedback row confirmed, withdrawn from the bound set or
edited while bound; a `local-tool` row inserted; the `go_no_go` header field), `force: true` on an
`Implemented` transition, a `WVR-` waiver row (they author it; you may ask for one), a scope change's
approval before its delta is applied, `package_unlock(confirm=true)`, `package_migrate(confirm=true)`,
`package_adopt(confirm=true)`, and the skill-promotion ceremony's every step. The boolean is their word from THIS session's interview — never a value you
supply because the ceremony expects it, never carried from an earlier answer.

---

## The procedure

**1. Start the interview immediately.**
The moment a decision or an action is identified as the operator's, ask — in the same turn, not the
next one. Do not report the blocker and wait to be asked. If several decisions are pending, batch
them into one interview. When in doubt whether something is theirs to decide, ask.
- *Why:* waiting turns a two-minute question into an idle turn, and quietly makes a decision of your
  own — the decision not to ask yet.
- *Field evidence:* an agent wrote "this is your call" and waited, several times, until the operator
  had to prompt for the interview.

**2. Do the homework first.**
Before asking, resolve everything you can yourself: read the code, run the command, take the
measurement, sweep the registers across families for an existing ruling (`tamheed:reading-the-record`).
The operator should be deciding, not researching. Never ask a question whose answer is already in the
repository or the package.
- *Why:* an interview that hands back unresearched options looks like consultation while transferring
  the work.

**3. Ask clearly and simply, with examples.**
One decision per question, plain language, and a concrete picture of what each option means in
practice. Where an option carries a risk the operator has not seen, state it inside the option, not
after the answer. Give a recommendation when the operator asks for one, and mark it as yours.
- *Why:* the operator decides from the message itself; a vague option gets decided on your summary.

**4. Quote the record, with its id — never the id alone.**
Every entity you cite carries its own text where you cite it: title, the operative field (a deferred
row's activation trigger, a decision's clause, an ADR's decision, a requirement's statement, an
acceptance criterion's given/when/then), its status, and its provenance — plus the id beside it.
Quote it verbatim and generate it (an `entity_export` file, a slate built from it); never paraphrase
or re-type it by hand. Collapse it if it is long, but keep it on the page.
- *Why:* an id is a pointer into a store the reader may not have open. Id alone makes them fetch it;
  content alone makes the claim uncheckable. A decision needs both.
- *Test:* could a reader who has never opened the package adjudicate every question using only this
  artifact? If not, it is not finished.
- *Field evidence:* a slate for fifty-three deferred-work rows named about forty entities by id alone,
  and the operator refused the interview: do not just mention an id and expect me to check it.

**5. Check your own sentences — the prose and the options are not verified.**
Quoted blocks can be generated and byte-checked. Everything you write around them — the framing, the
trade-off, the reason an option is expensive, and every option in a question — is your own claim, and
it reads as trustworthy because everything beside it is exact.
- Label it where it appears: `my reading`, `my recommendation`, `not measured`.
- Treat every `only`, `never`, `cannot`, `always` and `the single` as a request to measure: run the
  check now, or strike the word. State the weakest premise the argument needs; delete the ones it
  does not need.
- A sentence saying something cannot be done, or is blocked or expensive, must name the attempt that
  showed it — or say no attempt was made.
- Before offering an option, run the command that proves its premise: does the file exist, is the
  branch there, is the run still queryable. Distrust *we still have*, *it is already there* and *that
  is cheap* about anything you have not listed in this session.
- *Why:* a wrong sentence in a decision artifact is read at the moment of deciding, by the one person
  who cannot check it.
- *Field evidence:* an option offered to take a file "we still have locally"; the operator chose it,
  and the file had already been deleted.

**6. Never bank an earlier answer.**
Run the interview every time. An answer is scoped to the decision it came with; it is evidence of what
was true then, never consent for now. Do not carry it forward as a default, a starting position or a
shortcut. If a record must keep a past answer, label it HISTORY and say in the same place that the
next session asks again. Honour a ceremony's STOPs in the record as well as in your actions.
- *Why:* a banked answer silently turns a decision into a default, and the record then shows an
  interview that only appeared to happen.
- *Field evidence:* after the operator declined a promotion ceremony, their two answers were journaled
  "so the interview is not re-run from scratch"; the operator rejected the entry — *always you must
  interview me* — and a correction followed.

---

## What you cannot see

**A permission prompt never appears in a tool result.** When the operator reports one, you can only
infer its cause from their timing — four rounds of inference once failed where one word from them
succeeded. Ask the operator to name the tool the prompt shows, and read any rule-validation warning
the harness prints, before touching a permission setting. The prompts in front of deletion, pushing,
merging and re-running a pipeline are the operator's last checkpoint before the actions the decision
register spends most of its words governing: they are not faults to configure away.

**Before anything destructive or outward, ask first — in words, not by attempting it.** Removing a
lock, deleting a file another session may need, a force flag, a push, a rewrite of history, a stock
refresh that deletes files: the interview precedes the attempt, with the exact command and what it
destroys. An attempt that a prompt blocks looks, from your side, identical to one that ran.

## What this skill does NOT cover

- **Where a session stopped, for the next one** — `tamheed:session-handoff` (re-put an unanswered
  interview verbatim there; never reconstruct it).
- **How to read and sweep the records before citing them** — `tamheed:reading-the-record`.
- **What to record after the ruling** — the obligations table in this project's `CLAUDE.md` note.
- **Whether to include a recommendation at all** — follow what the operator asks for in that round.

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral; this file is the procedure.*
