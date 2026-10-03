---
name: operator-interview
user-invocable: false
description: >-
  Use whenever something needs the operator. That is a decision that is theirs, an action only they
  can take, a confirmation, an approval, or a ruling on a register row. A confirmation or an approval
  covers a scope change, a waiver, a forced transition, a lesson, a feedback row, the `go_no_go`
  header field, an unlock. Use it before building any slate, question, option list or recommendation
  for them. Also use before relying on an answer they gave earlier.
---

# Interviewing the operator

**Ask now, ask prepared, ask from the record, and ask again next time.**

When work reaches the edge of the operator's authority, the risk is not a wrong decision. It is a
stall nobody sees, or a question the operator cannot answer from the page in front of them. Or it is
a decision made on a sentence that was never true. None of this is caught by a gate. The report reads as complete
and every id resolves.

## What is theirs alone

Among the Tamheed ceremonies with a STOP, each is an interview. Its word is a JSON boolean or a status
they spoke. `operator_confirm: true` covers a lesson approved or promoted, moved OFF Approved, or its
`superseded_by` repointed while binding. It covers a feedback row confirmed, withdrawn from the bound
set or edited while bound, a `local-tool` row inserted, and the `go_no_go` header field. The other
words: `force: true` on an `Implemented` transition, and a `WVR-` waiver row (they author it, you may
ask for one). Also a scope change's approval before its delta is applied, `package_unlock(confirm=true)`,
`package_migrate(confirm=true)`, `package_adopt(confirm=true)`, and the skill-promotion ceremony's
every step. The boolean is their word from THIS session's interview. It is never a value you supply
because the ceremony expects it, and never carried from an earlier answer.

---

## The procedure

**1. Start the interview immediately.**
The moment a decision or an action is identified as the operator's, ask. Ask in the same turn, not the
next one. Do not report the blocker and wait to be asked. If several decisions are pending, batch
them into one interview. When in doubt whether something is theirs to decide, ask.
- *Why:* waiting turns a two-minute question into an idle turn. It quietly makes a decision of your
  own: the decision not to ask yet.
- *Field evidence:* an agent wrote "this is your call" and waited, several times, until the operator
  had to prompt for the interview.

**2. Do the homework first.**
Before asking, resolve everything you can yourself. Read the code, run the command, take the
measurement, sweep the registers across families for an existing ruling (`tamheed:reading-the-record`).
The operator should be deciding, not researching. Never ask a question whose answer is already in the
repository or the package.
- *Why:* an interview that hands back unresearched options looks like consultation while transferring
  the work.
- **An absent reason is not a reason.** A rejection recorded without one reads like a signal, because a
  rejection usually carries one. That is exactly what makes it worth one question, never an
  inference. Asked once, a twice-rejected item was promoted. Every inference the record offered
  (a concern unstated, work still owed) would have been wrong about finished code.
- **Put verdicts per item.** A batch verdict carries an item through on its neighbours' strength. A
  per-item slate withheld one of eight on a criterion the batch would have passed, twice.

**3. Ask clearly and simply, with examples.**
One decision per question, plain language, and a concrete picture of what each option means in
practice. Where an option carries a risk the operator has not seen, state it inside the option, not
after the answer. Mark ONE option as your recommendation, labelled as yours and with its deciding
reason, unless the operator has turned recommendations off (step 6). A recommendation is a pick
among options. It is never a verdict on a record or an approval. Those stay the operator's words.
- *Why:* the operator decides from the message itself. A vague option is decided on your summary.
  Bare options hand back the one judgement you were placed to make, and the operator then asks for it.
- *Field evidence:* asked with bare options, an operator sent the question back twice (*come back
  with a recommendation*) and then made it standing.

**4. Quote the record, with its id, never the id alone.**
Every entity you cite carries its own text where you cite it. That is its title, the operative field,
its status, and its provenance, plus the id beside it. The operative field is a deferred row's activation
trigger, a decision's clause, an ADR's decision, a requirement's statement, or an acceptance
criterion's given/when/then. Quote it verbatim and generate it (an `entity_export` file, a slate
built from it). Never paraphrase or re-type it by hand. Collapse it if it is long, but keep it on
the page.
- *Why:* an id is a pointer into a store the reader may not have open. Id alone makes them read it
  up. Content alone makes the claim uncheckable. A decision needs both.
- *Test:* could a reader who has never opened the package adjudicate every question using only this
  artifact? If not, it is not finished.
- *Field evidence:* a slate for fifty-three deferred-work rows named about forty entities by id alone.
  The operator refused the interview: do not just mention an id and expect me to check it.

**5. Check your own sentences. The prose and the options are not verified.**
Quoted blocks can be generated and byte-checked. Everything you write around them is your own
claim: the framing, the trade-off, the reason an option is expensive, and every option in a question.
It reads as trustworthy because everything beside it is exact.
- Label it where it appears: `my reading`, `my recommendation`, `not measured`.
- Treat every `only`, `never`, `cannot`, `always` and `the single` as a request to measure. Run the
  check now, or strike the word. State the weakest premise the argument needs. Remove the ones it
  does not need.
- A sentence saying something cannot be done, or is blocked or expensive, must name the attempt that
  showed it, or say no attempt was made.
- Before offering an option, run the command that proves its premise: does the file exist, is the
  branch there, is the run still queryable. Distrust *we still have*, *it is already there* and *that
  is cheap* about anything you have not listed in this session.
- *Why:* a wrong sentence in a decision artifact is read at the moment of deciding, by the one person
  who cannot check it.
- *Field evidence:* an option offered to take a file "we still have locally". The operator chose it,
  and the file had already been removed.

**6. Never bank an earlier answer.**
Run the interview every time. An answer is scoped to the decision it came with. It is evidence of what
was true then, never consent for now. Do not carry it on as a default, a starting position or a
shortcut. If a record must keep a past answer, label it HISTORY and say in the same place that the
next session asks again. Honour a ceremony's STOPs in the record as well as in your actions.
- *Why:* a banked answer silently turns a decision into a default. The record then shows an
  interview that only appeared to happen.
- *Field evidence:* after the operator rejected a promotion ceremony, their two answers were journaled
  "so the interview is not re-run from scratch". The operator rejected the entry (*always you must
  interview me*) and a correction followed.
- **Asking again is about consent for a NEW action. It is not a licence to re-open a settled ruling.**
  Re-put a ruling only when its premise has moved, and name the moved premise when you do. Re-asking
  one whose premise stands is re-litigating. A route ruled once was re-asked when its premise changed
  and held. That was legitimate. Asking a third time with nothing changed would not have been.
- **A standing instruction about HOW to ask is not a banked answer.** The operator may rule on the
  form of the interview: always recommend, never recommend, have the options reviewed first. Record
  it as a decision row in their own words and follow it until they replace it. It governs the
  asking, never the answer. Carried only in memory, such a rule drifts. One was cited for weeks to a
  decision whose text never stated it. Three later decisions and two memory files cited it, each
  copying the citation before it.

---

## What you cannot see

**A permission prompt never appears in a tool result.** When the operator reports one, you can only
infer its cause from their timing. Four rounds of inference once failed where one word from them
succeeded. Ask the operator to name the tool the prompt shows, and read any rule-validation warning
the harness prints, before touching a permission setting. The prompts in front of deletion, pushing,
merging and re-running a pipeline are the operator's last checkpoint. They stand before the actions
the decision register spends most of its words governing. They are not faults to configure away.

**Before anything destructive or outward, ask first, in words, not by attempting it.** That is
removing a lock, removing a file another session may need, a force flag, or a push. It is also a
rewrite of history, or a stock refresh that removes files. The interview precedes the attempt, with the exact command and
what it destroys. An attempt that a prompt blocks looks, from your side, identical to one that ran.

**For an act that is NOT destructive, a prompt-by-design and a forbidden act look identical too.** An
untried action and a blocked one leave the same trace: none. The only way to learn which it is is to
try it and let the operator answer. Never generalise one refusal into a boundary on what you can do,
and never write such a boundary into a record untested. No sweep finds a false claim about your own
capabilities.

## What this skill does NOT cover

- **Where a session stopped, for the next one**: `tamheed:session-handoff` (re-put an unanswered
  interview verbatim there, never reconstruct it).
- **How to read and sweep the records before citing them**: `tamheed:reading-the-record`.
- **What to record after the ruling**: the obligations table in this project's `CLAUDE.md` note.

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral. This file is the procedure.*
