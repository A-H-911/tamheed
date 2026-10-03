---
name: reading-the-record
user-invocable: false
description: >-
  Use before asserting what a requirement, decision, ADR, acceptance criterion or any register row
  says. Use before offering the operator an option, before calling a status, count or figure stale,
  and before measuring anything a requirement specifies. More generally, use it whenever you are
  about to write or act on a claim ABOUT a record you have not just read. That includes a claim that
  no record exists, which no keyword sweep can find.
---

# Reading the record

**Read the record. Not your memory of it, not a summary of it, not a tool's header describing it.**

The failure this prevents is not misreading. It is *not reading*: asserting what a row says from a
recollection that was once true. Or asserting it from prose that describes the row rather than being
it. The
assertion is usually plausible, often nearly right, and nothing mechanical catches it. Every id
resolves, every gate stays green, and the claim travels attached to real work.

An id is a pointer, not a reference. `G-IDS` checks foreign keys, not ids in prose. A green
`prose-ids-resolve` means every id RESOLVES, not that the sentence about it is true.

---

## When this fires

- You are about to write "the requirement says…", "no decision covers…", "nothing specifies…".
- You are about to put an option in front of the operator.
- You are about to call a status, a count or a figure stale, wrong or lagging.
- You are about to measure something a requirement specifies. The conditions are in the requirement's
  own text, and they bound what a valid measurement looks like.
- A committed tool told you what has already been decided, in a header, a docstring or a refusal.

## The procedure

**1. Name the record that would have to exist for your claim to be true.**
A decision, an ADR, a progress entry, a requirement id. If you cannot name one, your claim is
unsourced. Say so explicitly rather than letting it set the scope of the work.

**2. Go and read it: the field, not a description of it, and not a search over it.**
Read the row (`entity_query(type, id=…)`) and read the column you are making a claim about. A
substring search across a row can match text preserved in `custom_attributes` (historical wording is
often kept there on purpose). So a search reports the old text as present and reads as though an
amendment failed. *The field is the instrument. The search over the row is not.* Read the store
through the tools, never with a regular expression over its JSON-lines files. A pattern that stops at
the first closing brace loses every row whose free-text attributes hold a nested object. It does not
undercount. It DROPS the rows that would have changed the answer.

**3. Sweep with two keys, not one.**
- By identifier (`search=<id>`): finds rows that name the thing you changed.
- By keyword and by shape: finds rows that discuss it without ever citing its id. An id-only sweep
  is a scan with no subject when the two rows never name each other.

**4. Sweep the surfaces your default sweep skips.**
- **Closed rows.** Fixed, Won't-fix and Duplicate defects, and Done or Won't-do deferred-work rows,
  are an *unindexed decision store*. Operator rulings are recorded inside them where no
  decision-register sweep will find them.
- **Progress entries.** The reason a status is what it is often lives only as prose in the append-only
  journal. No register view surfaces it (`search` with `context` is the instrument).
- **The ADR's own text.** When an ADR names the rows it will amend, that list *is* the instrument. A
  row on the list without the pointer is still asserting superseded text. A row quoting the same
  subject but absent from the list was never considered at all.
- **Across families, before framing an interview.** A ruling on a defect may live in a decision, an
  acceptance criterion, a scope change or a journal entry. Frame no question from the row alone.

**5. For an absence claim, sweep on the shape of a denial.**
"Nothing does X" has no keyword. Key on the shape instead: `no `, `none`, `nothing`, `names no`,
`not scheduled`, `deliberately`, `standing`, `exists`. Read what each hit DENIES, asking whether
your work just filled that gap. A sweep keyed on what changed finds sentences about the change. Only
this second sweep finds sentences asserting that nothing did.

**6. Read the hits. Do not count them.**
Tense is invisible to a regex. *"Needed an operator decision"* followed by *"DECIDED"* is history,
not an open question.

**7. A premise you inherited is a claim, not a fact. Check it against the thing itself.**
Take a carried evaluation ("done, do not redo"). Or take a capability judged present or absent from
one file, or a risk described as the price of a change. Every number in it can be right and the premise still
wrong. It was checked against the wrong thing, and nothing downstream fails to tell you.
- *A carried pick.* When a choice must satisfy a hard constraint (a security policy, a sandbox, an
  offline install, a target runtime, a licence), find that constraint. Ask whether the pick was
  ever run against it. Order the shortlist by that constraint FIRST. Order by size, dependency count
  or freshness only among the candidates that pass it. Registry metadata ranks packages that all
  work and says nothing about which ones do. If the pick was never run against the constraint, run
  the smallest thing that exercises it before you build on it. Run it on every candidate in one run,
  not only the pick. Testing only the pick concludes "the technique is impossible here" when it was
  the pick that failed.
- *A capability judged from one class.* Read its base types and look for a sibling that already
  solves the problem before declaring a field or a behaviour absent. The file you read is only its
  own declaration. An unused parameter is a question, not evidence.
- *A cost carried as inherent.* Name the expensive thing and the property you are about to lose.
  Then ask whether the expensive thing creates the property or only bundles it. If it is
  only bundled, rebuild it separately instead of redesigning everything that depended on it. A
  thirty-line reset kept every test on empty tables where the plan had been to rework each one. Work
  spread across every consumer to keep one property is the tell that the property has one owner.
An ADR's amend list is the same instrument (step 4). Check it against every row that quotes the
subject, not only the rows it names.

**Read what is RENDERED from the note, and what BINDS from the store.** A lesson binds by its
status, from the write that approves it. The emitted `CLAUDE.md` note renders a roster of them:
every pinned Approved row and a capped fill of the highest-numbered unpinned ones. Only the
emit rebuilds it. So an Approved lesson is rendered by no note until that emit has run, and one
outside the roster is read only by query. Do not infer that a session has READ a lesson from its
register status or from a list in a file. Do not infer it from a decision's text that names the
lesson. Do not infer that a
lesson stopped binding because the note no longer lists it.
- *Field evidence:* an approved, pinned lesson reached no session for two days because the emit
  ran in a later batch. A lesson pushed out of the roster by a newer approval was recorded
  as no longer binding, which the operator had never said.

---

## Before you call something stale

Ask: **what would this be if the ruling had been obeyed perfectly?** If that equals what you
measured, the row is right and the drift is in your reading.

- **A status may be load-bearing rather than lagging.** Uniformity across a natural group is the
  signature of a decision. Check whether any store constraint keys on that status (immutability, a
  CHECK, a trigger, a foreign key) before "correcting" it.
- **A fix-forward ruling deliberately freezes a historical figure** while the total grows. The
  row's number stays correct while the ratio it appears in goes wrong.
- **Weight by reversibility.** An irreversible flip made on an unverified cause cannot be undone.
- **A ruling can outlive its application.** A decision clause that activates or closes a row does
  nothing to the row. Nothing mechanical compares a clause to the status it names. A row that still
  reads Open days after its ruling is a row a human has to move. That is why open rows stay listed.

## Before you measure

A requirement's own text carries the conditions a valid measurement must satisfy: the network, the
scale, the cache state, the subject. **Read them first, and check the mechanism it names actually
exists in the code.** If the named trigger, mechanism or event is absent, stop. You have found a
defect. The measurement you were about to take would either be meaningless or would quietly time
a different event and give a number that passes. Measuring outside the stated conditions gives
a figure that supports neither a pass nor a fail. That is worse than no measurement, because it
looks like one.

---

## What this skill does NOT cover

- **Whether a number you gathered means what you think**: `tamheed:measurement-evidence`.
- **Git and package sequencing**: `tamheed:package-writes`.
- **How to WRITE a record**: the obligations table in this project's `CLAUDE.md` note.
- **Operator interview conduct**: `tamheed:operator-interview`. This skill stops at the homework
  that must precede the question.

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral. This file is the procedure.*
