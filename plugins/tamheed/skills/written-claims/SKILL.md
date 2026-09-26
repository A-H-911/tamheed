---
name: written-claims
user-invocable: false
description: >-
  Use before writing or merging prose that states a mechanism, a count, a sequence, a scope, a
  status or a done-claim — a progress entry, a WBS done-clause, an audit verdict's evidence, a
  findings file, a memory line, a kickoff prompt or any other file a session reads before acting, a
  code comment, an inventory ("every remaining consumer") — and whenever you retract or correct a
  claim you or someone else made, or record a ruling that changes what earlier prose assumed.
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
no id sweep looks at an ordinal. Re-derive attributions too: a claim credited to the wrong record
sends a reader to a place where nothing is amiss, which is worse than a wrong count — a count merely
disagrees with the list beneath it.
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
- **When you build what the record said did not exist, sweep for the old claim by the thing's NAME,
  at build time.** Sentences describing the old world carry no id of the row that changes them. At
  scoping, read every acceptance criterion bound to the requirement and treat an exclusion or
  *because* clause naming the thing as a supersession owed in that same scope change. Before the
  change merges, grep the SOURCE tree — not only the package — for the name and for absence shapes
  (*no surface*, *never*, *not yet*, *does not exist*), and fix what the change made false in the
  same change.
- *Field evidence:* a picker shipped while a source file still said no surface offered one, and the
  criterion bound to it still gave the old reason.

**5. When you retract a claim, grep the shipped diff for the retracted words.**
Take the literal phrase, not the idea. Search the open change and the files it touches: comments,
assertion messages, test names, log strings, docstrings, the package's own rows. Fix every hit in the
same change, or file a defect naming file and lines if it has merged. A pushed commit message must
not be rewritten, so say so in a `correction` progress entry (`corrects` naming the entry it corrects). Then
read the corrected text for any claim about how it was proved; a false mechanism often comes with a
false calibration story.
- *Field evidence:* a progress entry retracted a claim in the register and the pull request body, but
  the merged test still stated it.
- **A ruling falsifies prose that REASONS from the old state without naming it.** When a row is
  closed, re-decided or moved, grep its id AND the advisory and register names built on it, and read
  what each hit CONCLUDES rather than what it asserts — nine sentences went false when one defect
  closed, and none of them named its status. Ship the fix in the ruling's own commit: the window
  between a ruling and its write-up is where the falsified sentence gets committed, and it is widest
  when the work is going well. Every artefact a decision touches moves in the same batch; the one
  you skip is the one the next session reads.

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

**8. A live surface carries the command, not the answer.**
In a file a session reads before acting — a kickoff prompt, an operating note, a memory index — a
lifecycle status, a negative (*has not started*), a count with a disclaimer beside it, an ordinal
(*the fourth time*), a list of a moving queue, or a table rebuilt from the store is a status with no
timestamp: true when written, false on the next write, and read as current. Delete the answer and
keep the command that measures it; name the list instead of counting it; re-derive a table when it
is needed, never restore it; describe nothing an operator edits between sessions. A commit message is
a dated record and may say what was decided; the same sentence in a live file is stale — what makes
prose stale is not the sentence but whether the artefact claims to describe NOW.
- A judgement that a requirement is satisfied belongs in a verdict row, never in a code comment
  where no register view can see it.
- Cite an id, a commit or a digest, never a regenerated file's path: a reused path is a pointer that
  silently re-aims at new content.
- *Field evidence:* a kickoff prompt grew to 3,600 lines of carried counts, statuses and "your
  verdict" tails, and one hundred and twenty-seven of its sentences read as restated register
  content; the rules survived the diet, the answers did not.

**9. Read the predicate a scope claim describes, and list its members.**
When you fix an instance and write down why, the last step is to read the guard, glob or
registration that decides the scope — the `or`s, what resolves, what a glob anchors on — then fix
every member, or name in the comment the members you did not fix and why. A true but narrow comment
is confirmed by every check anyone runs. Widening the comment is not the same as fixing the class;
do not record it as if it were.
- *Field evidence:* a comment warned about one kind of write while the predicate below it covered a
  second, and two of those writes were silently lost.

---

## What this skill does NOT cover

- **Reading a record before citing it** — `tamheed:reading-the-record`.
- **Whether a measurement means what you think** — `tamheed:measurement-evidence`.
- **A commit message's claims about package writes** — `tamheed:package-writes` (re-read the row first).

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral; this file is the procedure.*
