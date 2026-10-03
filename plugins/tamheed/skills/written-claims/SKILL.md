---
name: written-claims
user-invocable: false
description: >-
  Use before writing or merging prose that states a mechanism, a count, a sequence, a scope, a
  status or a done-claim. That is a progress entry, a WBS done-clause, an audit verdict's evidence, a
  findings file, a memory line, or a kickoff prompt. It is also any other file a session reads before
  acting, a code comment, an inventory ("every remaining consumer"). Use it whenever you retract or correct a
  claim you or someone else made, or record a ruling that changes what earlier prose assumed.
---

# Written claims

**A sentence can be true today and still mislead: too narrow, stale in its words, or stripped of its
hedges. No gate reads prose, so the checking is yours.**

Every mechanical check works on identifiers, statuses, foreign keys and token patterns. A wrong claim
in prose keeps all four correct: every id resolves, every gate stays green, and the claim travels
attached to real work. `tamheed:reading-the-record` covers reading a record before you cite it. This
skill covers what you WRITE, and keeping it true afterwards. `tamheed:plain-english` covers the form
of the sentence: one meaning, one way to parse it.

---

## The procedure

**1. Re-check the words around a number, not only the number.**
When you reuse a sentence's shape, re-derive every claim in it. Do not just refresh the figure. A
fresh number makes the stale words beside it look checked. When a document carries an ordered
sequence (numbered findings, versioned entries), check the sequence itself for gaps and collisions.
No id sweep looks at an ordinal. Re-derive attributions too. A claim credited to the wrong record
sends a reader to a place where nothing is amiss, which is worse than a wrong count. A count merely
disagrees with the list beneath it.
- *Field evidence:* "nine families" was carried out of an older sentence beside a freshly measured
  count. Measured, it was fifteen, inside the sentence claiming the check ran clean.

**2. Treat a document's examples and its stated mechanism as two different grades of evidence.**
The examples are observed cases. The mechanism is a fit drawn through them. Use the examples. Before
you apply the rule to a case the examples do not list, check the mechanism against the vendor's
documentation or a two-minute experiment. Reproducing the document's own failure under your variant is
the cheapest check. Advice can be right while its mechanism is false, and the mechanism is what you
generalise from.

**3. When you compress a source row into a done-claim, keep its hedges.**
A summary drops limits first, and a limit is what a done-claim must keep. Re-read the source row to
its end at the moment you act on the derived row, not only when you wrote it. Look for the source's
own words about itself: *undecidable*, *cannot be closed by*, *must not be reported as*. If the
derived row asserts what the source says cannot be asserted, the derived row is wrong.
- *Field evidence:* a work item promised a check that a deferred-work row proved cannot exist. A
  literal check would have reported seventy-seven failures over correct code.

**4. Write an inventory as the sweep that made it, and sweep dependents, not consumers.**
"Every remaining consumer" is a claim of absence. Write the honest form, "every call site matching
this pattern", so a reader can see what it could never find. When a value changes where it comes
from, also find what reads it to JUDGE, REPORT or ASSERT. Those readers are validators, health checks,
startup checks, diagnostic logs, test fixtures. Search the type name and the section name, not the property accesses.
- **When you build what the record said did not exist, sweep for the old claim by the thing's NAME,
  at build time.** Sentences describing the old world carry no id of the row that changes them. At
  scoping, read every acceptance criterion bound to the requirement. Treat an exclusion or *because*
  clause naming the thing as a supersession owed in that same scope change. Before the change
  merges, grep the SOURCE tree, not only the package, for the name. Grep it for absence shapes too
  (*no surface*, *never*, *not yet*, *does not exist*). Fix what the change made false in the same change.
- *Field evidence:* a picker shipped while a source file still said no surface offered one. The
  criterion bound to it still gave the old reason.

**5. When you retract a claim, grep the shipped diff for the retracted words.**
Take the literal phrase, not the idea. Search the open change and the files it touches: comments,
assertion messages, test names, log strings, docstrings, the package's own rows. Fix every hit in the
same change, or file a defect naming file and lines if it has merged. A pushed commit message must
not be rewritten, so say so in a `correction` progress entry (`corrects` naming the entry it
corrects). Then read the corrected text for any claim about how it was proved. A false mechanism
often comes with a false calibration story.
- *Field evidence:* a progress entry retracted a claim in the register and the pull request body, but
  the merged test still stated it.
- **A ruling falsifies prose that REASONS from the old state without naming it.** When a row is
  closed, re-decided or moved, grep its id AND the advisory and register names built on it. Read
  what each hit CONCLUDES rather than what it asserts. Nine sentences went false when one defect
  closed, and none of them named its status. Ship the fix in the ruling's own commit. The window
  between a ruling and its write-up is where the falsified sentence lands, and it is widest
  when the work is going well. Every artefact a decision touches moves in the same batch. The one
  you skip is the one the next session reads.
- **An obligation is discharged in the family that made it.** A thing owed can be carried by a
  handoff line, a decision's clause and a memory sentence at once. A journal correction answers
  the handoff and leaves an approved decision clause owing. Before you choose the write, sweep
  the decisions, the journal and the latest handoff for the obligation. Retire a decision's
  clause by a decision row. A dry-run proves the write LANDS. It cannot prove the write
  discharges what the record says is owed.
  - *Field evidence:* a retired question was to be corrected on the handoff that named it, a
    recipe that had run clean on a copy. The same question stood as a clause of an approved
    ruling, and only a new ruling discharged it.
- **A ruling that changes what a word means is swept by the word, not by the phrasings you
  expect.** Grep the word's every form, word-bounded, and read each hit. A list of phrasings
  misses the negated one. Sweep every file a session reads before acting (the kickoff prompts,
  the operating notes, the memory files) beside the registers. A dated record keeps its text.
  ONE reading rule in a decision row says how the old word reads now and names the rows it
  covers. A live file is reworded in the same change.
  - *Field evidence:* a sweep built from five phrasings of the old sense passed a memory line
    that negated the verb. It never opened the kickoff prompt every session reads. Fourteen
    dated rows were then covered by one reading rule instead of fourteen corrections.

**6. A correction is a new entry, never an edit.**
The journal is append-only. `progress_update` with `event_type: correction` and `corrects: <PE-id>`
keeps both the wrong sentence and its retraction on the record. A finding is corrected the same way:
a dated note beside it, never a silent rewrite.

**7. Fix the file. Never annotate the pointer.**
When an index line, a memory pointer or a summary points at a file that says something wrong, the fix
goes in the file. A disclaimer bolted onto the pointer is *"superseded, see …"* beside the link
while the file keeps saying the wrong thing. It leaves the wrong text in place for every reader who
reaches the file another way, and it reads as checked. The same rule holds for a distilled skill file
that carries a mechanism its source lesson contradicts. Correct the mechanism in the file, not in a
note in the index that says it is wrong. The correction is the operator's hand-edit, recorded by a
`correction` journal entry naming the skill row.
- *Field evidence:* an index line carried *"SUPERSEDED by a later decision"* for weeks while the
  file it pointed at kept the superseded rule. Readers of the file never saw the index.

**8. A live surface carries the command, not the answer.**
A file a session reads before acting is a kickoff prompt, an operating note, a memory index. In it,
a lifecycle status, a negative (*has not started*) or a count with a disclaimer beside it is a status
with no timestamp. So is an ordinal (*the fourth time*), a list of a moving queue, or a table rebuilt
from the store. Such a status is true when written, false on the next write, and read as current. Remove the answer
and keep the command that measures it. Name the list instead of counting it. Re-derive a table when
it is needed, never restore it. Describe nothing an operator edits between sessions. A commit message
is a dated record and may say what was decided. The same sentence in a live file is stale. What makes
prose stale is not the sentence but whether the artefact claims to describe NOW.
- A judgement that a requirement is satisfied belongs in a verdict row, never in a code comment
  where no register view can see it.
- Cite an id, a commit or a digest, never a regenerated file's path. A reused path is a pointer that
  silently re-aims at new content.
- *Field evidence:* a kickoff prompt grew to 3,600 lines of carried counts, statuses and "your
  verdict" tails. One hundred and twenty-seven of its sentences read as restated register
  content. The rules survived the diet, the answers did not.

**9. Read the predicate a scope claim describes, and list its members.**
When you fix an instance and write down why, the last step is to read the guard, glob or
registration that decides the scope. Read the `or`s, what resolves, what a glob anchors on. Then fix
every member, or name in the comment the members you did not fix and why. A true but narrow comment
is confirmed by every check anyone runs. Widening the comment is not the same as fixing the class.
Do not record it as if it were.
- *Field evidence:* a comment warned about one kind of write while the predicate below it covered a
  second. Two of those writes were silently lost.

---

## What this skill does NOT cover

- **Reading a record before citing it**: `tamheed:reading-the-record`.
- **Whether a measurement means what you think**: `tamheed:measurement-evidence`.
- **A commit message's claims about package writes**: `tamheed:package-writes` (re-read the row first).
- **The form of the sentence** (one instruction, the actor named, no semicolon, one word per meaning):
  `tamheed:plain-english`.

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral. This file is the procedure.*
