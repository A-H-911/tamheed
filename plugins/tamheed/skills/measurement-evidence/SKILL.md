---
name: measurement-evidence
user-invocable: false
description: >-
  Use BEFORE trusting or reporting any measurement — a scan or grep returning zero, a green suite or
  run, a coverage or performance number, a detector or health check you built, a reproduction of a
  bug, a calibration, or any claim that something is absent, unused, fixed, or caused by X. Also use
  when a premise looks untestable, when two sources agree, and when a number you relied on turns out to
  be wrong.
---

# Measurement evidence

A measurement can run, have a subject, return a true number, and still mean something other than
what you are about to claim. Work top to bottom. Each step is usually one command, and the ones near
the top kill the most confident errors.

---

## 1. Before running it: what would a NEGATIVE mean?

Decide this **before** the experiment, not after.

- If a negative result is equally consistent with *the hypothesis is wrong* and with *this instrument
  cannot see the difference*, the instrument has no power and its refutation is a coin flip you will
  read as a refutation. A suspected leak was measured by process working set on a machine that never
  pressured the garbage collector — the unchanged curve meant nothing; forcing a collection and reading
  the heap bytes retained afterwards refuted one hypothesis and confirmed another the same afternoon.
  Only the instrument changed.
- If **no observation could prove your fix wrong**, it is a mitigation, not a fix. A remedy that
  reduces a *probability* buys an unfalsifiable position, and its own honest caveat is what makes it
  unfalsifiable: every recurrence gets attributed to the residual it disclosed. Prefer a remedy that
  removes the **condition** over one that changes the **odds**; where only the odds are reachable,
  record a deferred-work row and say so.

## 2. Did the instrument have a SUBJECT?

A tool exiting 0 over an empty file set is indistinguishable, at the exit code, from one exiting 0
over a clean set — and the empty case is silent by construction.

- **Inject a deliberate fault, confirm the gate FAILS, then remove it.** Prefer the command CI runs
  over a hand-rolled one; CI's is the one whose subject is known-good.
- **A passing mutant is not a result.** A missing test, a mis-targeted file, a filtered test, a stale
  build and a genuinely uncovered branch all produce the identical observation. Count twice: prove the
  detector exists (watch the test count move), then require the failure count to move under the mutant.
- **Proving the check RAN is not proving the assertion had anything to look at.** An accessibility
  sweep was proven to run by a real test-count delta; the seed put every item one day outside the
  rendered range, so for weeks the assertion ran over an empty grid and reported clean while the
  violation was serious.
- **A trigger that never fires, one that always fires, and one whose silence you cannot read are the
  same fault.** If an empty artefact is produced identically by *it ran and saw nothing* and by *it
  never ran*, you have no instrument. An instrument must deliver, not just fire — and report on itself.

## 3. Is it the RIGHT subject?

Step 2 guards against no subject. This guards against the **wrong** one — the scan runs, the count
moves, and the number is true of a set that excludes the answer.

- **State the denominator out loud and ask what it excludes**: which file types, directories,
  spellings, quoting. Report it with the finding — *"twelve of fourteen paged reads"*, not *"twelve
  uncapped reads"*.
- **A zero is the most dangerous result**, because absence is what people act on. When a scan returns
  zero for something a record claims exists, treat the **scan** as the prime suspect before the record.
- **Choose a control spelled the same way as the term under test**, and **from OUTSIDE the scope you
  are searching.** A control from inside confirms that boundary; it cannot test it. A sweep of five
  registers was properly calibrated and still returned a clean, evidenced, wrong answer, because the
  journal was not in the swept scope and no control chosen from within could reveal that.
- **A HIT on the wrong spelling is worse than a zero and has no control at all.** A substring match on
  a longer name produced a whole defect row about the wrong file. A zero prompts a second look; a hit
  does not.
- **A prescribed command is a claim to re-verify, not an authority to quote.** A committed "measure it
  with this command" keeps its authority long after the artifact it measures was rewritten underneath
  it. What catches it is refusing a number that disagrees with something you independently know.

## 4. Two sources agree?

- **Ask what MECHANISM they share, not how different the tooling looks.** Two independently written
  scanners returned the same sites across the same files — and both were blind to the same fifth of
  the surface, because both keyed on the same token in the same position. Change the subject, not the
  sophistication: prefer an instrument whose subject is an enumerable population (assert the count)
  over one whose subject is a pattern.
- **Superficial difference is not independence.** A different runner, orchestrator or machine is not
  independence if both paths load the same artefact. But the relationship is asymmetric: two
  non-independent observations are weak evidence about *where* a fault lives and **strong** evidence
  that a change to their shared component worked.

## 5. After the number is in your hand

- **A measurement that runs AFTER the action it should gate is a report, not a control.** In a chained
  command the number prints, is correct, and changes nothing — you read it after the push has already
  happened. Make the action **conditional** on the measurement, and the same number becomes a gate.
- **Correcting a number does not correct what was concluded from it.** Those conclusions stay where
  they were written, detached from the evidence, reading exactly like conclusions drawn from the
  corrected value. Sweep for what was inferred from the old one and re-derive it, or mark it as
  resting on a superseded measurement (`tamheed:written-claims`).
- **Record the variables you are HOLDING, not just the one you are varying.** An investigation varied
  command shape exhaustively across three sessions and never recorded which paths the commands read —
  and the paths were the cause. One controlled pair settled it in two commands.

## When a premise looks untestable

Before recording a premise as untestable, list your instruments and ask whether every one of them is
an OUTPUT you are comparing against another output. If so, the *producer* of at least one output is a
further instrument and is usually cheaper than either comparison — source code, a schema, a generator,
a migration. A premise carried for weeks as unverifiable was settled in one command by reading the
code that produced the output. When a record states that something cannot be tested, treat that as a
claim to check rather than a fact to inherit.

---

## What this skill does NOT cover

- **Not** how to write or structure tests — `tamheed:test-evidence` covers what a test proves.
- **Not** how to read CI runs — `tamheed:ci-evidence`.
- **Not** how to write to the package, quote records for a decision, or run an operator interview —
  `tamheed:package-writes`, `tamheed:reading-the-record`, `tamheed:operator-interview`.

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral; this file is the procedure.*
