---
name: written-claims
user-invocable: false
description: >-
  Use before writing or merging prose that states a mechanism, a count, a sequence, a scope or a
  done-claim — a progress entry, a WBS done-clause, an audit verdict's evidence, a findings file, a
  memory line, a code comment, an inventory ("every remaining consumer") — and whenever you retract or
  correct a claim you or someone else made.
---

# Written claims

**A sentence can be true today and still mislead: too narrow, stale in its words, or stripped of its
hedges. No gate reads prose — so the checking is yours.**

Every mechanical check works on identifiers, statuses, foreign keys and token patterns. A wrong claim
in prose keeps all four correct: every id resolves, every gate stays green, and the claim travels
attached to real work. `tamheed:reading-the-record` covers reading a record before you cite it. This
skill covers what you WRITE, and keeping it true afterwards.

---

## The procedure

**1. Re-check the words around a number, not only the number.**
When you reuse a sentence's shape, re-derive every claim in it. Do not just refresh the figure. A
fresh number makes the stale words beside it look checked. And when a document carries an ordered
sequence (numbered findings, versioned entries), check the sequence itself for gaps and collisions —
no id sweep looks at an ordinal.
- *Field evidence:* "nine families" was carried out of an older sentence beside a freshly measured
  count; measured, it was fifteen — inside the sentence claiming the check ran clean.

**2. Treat a document's examples and its stated mechanism as two different grades of evidence.**
The examples are observed cases; the mechanism is a fit drawn through them. Use the examples. Before
you apply the rule to a case the examples do not list, check the mechanism against the vendor's
documentation or a two-minute experiment. Reproducing the document's own failure under your variant is
the cheapest check. Advice can be right while its mechanism is false — and the mechanism is what you
generalise from.

**3. When you compress a source row into a done-claim, keep its hedges.**
A summary drops limits first, and a limit is what a done-claim must keep. Re-read the source row to
its end at the moment you act on the derived row, not only when you wrote it. Look for the source's
own words about itself: *undecidable*, *cannot be closed by*, *must not be reported as*. If the
derived row asserts what the source says cannot be asserted, the derived row is wrong.
- *Field evidence:* a work item promised a check that a deferred-work row proved cannot exist; a
  literal check would have reported seventy-seven failures over correct code.

**4. Write an inventory as the sweep that produced it, and sweep dependents, not consumers.**
"Every remaining consumer" is a claim of absence. Write the honest form — "every call site matching
this pattern" — so a reader can see what it could never find. When a value changes where it comes
from, also find what reads it to JUDGE, REPORT or ASSERT: validators, health checks, startup checks,
diagnostic logs, test fixtures. Search the type name and the section name, not the property accesses.

**5. When you retract a claim, grep the shipped diff for the retracted words.**
Take the literal phrase, not the idea. Search the open change and the files it touches: comments,
assertion messages, test names, log strings, docstrings, the package's own rows. Fix every hit in the
same change, or file a defect naming file and lines if it has merged. A pushed commit message must
not be rewritten, so say so in a `correction` progress entry (`corrects` naming the entry it corrects). Then
read the corrected text for any claim about how it was proved; a false mechanism often comes with a
false calibration story.
- *Field evidence:* a progress entry retracted a claim in the register and the pull request body, but
  the merged test still stated it.

**6. A correction is a new entry, never an edit.**
The journal is append-only: `progress_update` with `event_type: correction` and `corrects: <PE-id>`
keeps both the wrong sentence and its retraction on the record. A finding is corrected the same way —
a dated note beside it, never a silent rewrite.

**7. Fix the file; never annotate the pointer.**
When an index line, a memory pointer or a summary points at a file that says something wrong, the fix
goes in the file. A disclaimer bolted onto the pointer — *"superseded, see …"* beside the link while
the file keeps saying the wrong thing — leaves the wrong text in place for every reader who reaches
the file another way, and reads as checked. The same rule for a distilled skill file that carries a
mechanism its source lesson contradicts: correct the mechanism in the file (the operator's hand-edit,
recorded by a `correction` journal entry naming the skill row), not a note in the index that it is
wrong.
- *Field evidence:* an index line carried *"SUPERSEDED by a later decision"* for weeks while the
  file it pointed at kept the superseded rule; readers of the file never saw the index.

---

## What this skill does NOT cover

- **Reading a record before citing it** — `tamheed:reading-the-record`.
- **Whether a measurement means what you think** — `tamheed:measurement-evidence`.
- **A commit message's claims about package writes** — `tamheed:package-writes` (re-read the row first).

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral; this file is the procedure.*
