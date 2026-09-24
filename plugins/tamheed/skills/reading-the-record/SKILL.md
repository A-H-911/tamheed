---
name: reading-the-record
description: >-
  Use before asserting what a requirement, decision, ADR, acceptance criterion or any register row
  says; before offering the operator an option; before calling a status, count or figure stale; and
  before measuring anything a requirement specifies. More generally, whenever you are about to write
  or act on a claim ABOUT a record you have not just read — including a claim that no record exists,
  which no keyword sweep can find.
---

# Reading the record

**Read the record. Not your memory of it, not a summary of it, not a tool's header describing it.**

The failure this prevents is not misreading. It is *not reading* — asserting what a row says from a
recollection that was once true, or from prose that describes the row rather than being it. The
assertion is usually plausible, often nearly right, and nothing mechanical catches it: every id
resolves, every gate stays green, and the claim travels attached to real work.

An id is a pointer, not a reference: `G-IDS` checks foreign keys, not ids in prose. A green
`prose-ids-resolve` means every id RESOLVES — not that the sentence about it is true.

---

## When this fires

- You are about to write "the requirement says…", "no decision covers…", "nothing specifies…".
- You are about to put an option in front of the operator.
- You are about to call a status, a count or a figure stale, wrong or lagging.
- You are about to measure something a requirement specifies — the conditions are in the requirement's
  own text, and they bound what a valid measurement looks like.
- A committed tool told you what has already been decided, in a header, a docstring or a refusal.

## The procedure

**1. Name the record that would have to exist for your claim to be true.**
A decision, an ADR, a progress entry, a requirement id. If you cannot name one, your claim is
unsourced — say so explicitly rather than letting it set the scope of the work.

**2. Go and read it — the field, not a description of it, and not a search over it.**
Fetch the row (`entity_query(type, id=…)`) and read the column you are making a claim about. A
substring search across a row can match text preserved in `custom_attributes` (historical wording is
often kept there on purpose), so a search reports the old text as present and reads as though an
amendment failed. *The field is the instrument; the search over the row is not.*

**3. Sweep with two keys, not one.**
- By identifier (`search=<id>`) — finds rows that name the thing you changed.
- By keyword and by shape — finds rows that discuss it without ever citing its id. An id-only sweep
  is a scan with no subject when the two rows never name each other.

**4. Sweep the surfaces your default sweep skips.**
- **Closed rows.** Fixed, Won't-fix and Duplicate defects, and Done or Won't-do deferred-work rows, are an
  *unindexed decision store*: operator rulings get recorded inside them where no decision-register
  sweep will find them.
- **Progress entries.** The reason a status is what it is often lives only as prose in the append-only
  journal that no register view surfaces (`search` with `context` is the instrument).
- **The ADR's own text.** When an ADR names the rows it will amend, that list *is* the instrument: a
  row on the list without the pointer is still asserting superseded text, and a row quoting the same
  subject but absent from the list was never considered at all.
- **Across families, before framing an interview.** A ruling on a defect may live in a decision, an
  acceptance criterion, a scope change or a journal entry; frame no question from the row alone.

**5. For an absence claim, sweep on the shape of a denial.**
"Nothing does X" has no keyword. Key on the shape instead — `no `, `none`, `nothing`, `names no`,
`not scheduled`, `deliberately`, `standing`, `exists` — and read what each hit DENIES, asking whether
your work just filled that gap. A sweep keyed on what changed finds sentences about the change; only
this second sweep finds sentences asserting that nothing did.

**6. Read the hits; do not count them.**
Tense is invisible to a regex. *"Needed an operator decision"* followed by *"DECIDED"* is history,
not an open question.

---

## Before you call something stale

Ask **"what would this be if the ruling had been obeyed perfectly?"** If that equals what you
measured, the row is right and the drift is in your reading.

- **A status may be load-bearing rather than lagging.** Uniformity across a natural group is the
  signature of a decision. Check whether any store constraint keys on that status — immutability, a
  CHECK, a trigger, a foreign key — before "repairing" it.
- **A fix-forward ruling deliberately freezes a historical figure** while the total grows, so the
  row's number stays correct while the ratio it appears in goes wrong.
- **Weight by reversibility.** An irreversible flip made on an unverified cause cannot be undone.
- **A ruling can outlive its application.** A decision clause that activates or closes a row does
  nothing to the row; nothing mechanical compares a clause to the status it names. A row that still
  reads Open days after its ruling is a row a human has to move — that is why open rows stay listed.

## Before you measure

A requirement's own text carries the conditions a valid measurement must satisfy — the network, the
scale, the cache state, the subject. **Read them first, and check the mechanism it names actually
exists in the code.** If the named trigger, mechanism or event is absent, stop: you have found a
defect, and the measurement you were about to take would either be meaningless or would quietly time
a different event and produce a number that passes. Measuring outside the stated conditions produces
a figure that supports neither a pass nor a fail — worse than no measurement, because it looks like one.

---

## What this skill does NOT cover

- **Whether a number you gathered means what you think** — `tamheed:measurement-evidence`.
- **Git and package sequencing** — `tamheed:package-writes`.
- **How to WRITE a record** — the obligations table in this project's `CLAUDE.md` note.
- **Operator interview conduct** — `tamheed:operator-interview`. This skill stops at the homework
  that must precede the question.

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral; this file is the procedure.*
