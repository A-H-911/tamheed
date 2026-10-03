---
name: measurement-evidence
user-invocable: false
description: >-
  Use BEFORE trusting or reporting any measurement. That is a scan or grep returning zero, a green
  suite or run, a coverage or performance number, a detector or health check you built. It is also
  a reproduction of a bug, a calibration, or any claim that something is absent, unused, fixed, or
  caused by X. Also
  use when a premise looks untestable, when two sources agree, and when a number you relied on turns
  out to be wrong.
---

# Measurement evidence

A measurement can run, have a subject, return a true number, and still mean something other than
what you are about to claim. Work top to bottom. Each step is usually one command, and the ones near
the top kill the most confident errors.

---

## 1. Before running it: what would a NEGATIVE mean?

Decide this **before** the experiment, not after.

- A negative result may be equally consistent with *the hypothesis is wrong* and with *this
  instrument cannot see the difference*. Then the instrument has no power, and its refutation is a
  coin flip you will read as a refutation. A suspected leak was measured by process working set on a
  machine that never pressured the garbage collector. The unchanged curve meant nothing. Forcing a
  collection and reading the heap bytes retained afterwards refuted one hypothesis and confirmed
  another the same afternoon. Only the instrument changed.
- If **no observation could prove your fix wrong**, it is a mitigation, not a fix. A remedy that
  reduces a *probability* buys an unfalsifiable position. Its own honest caveat is what makes it
  unfalsifiable: every recurrence is attributed to the residual it disclosed. Prefer a remedy that
  removes the **condition** over one that changes the **odds**. Where only the odds are reachable,
  record a deferred-work row and say so.

## 2. Did the instrument have a SUBJECT?

A tool exiting 0 over an empty file set is indistinguishable, at the exit code, from one exiting 0
over a clean set. The empty case is silent by construction.

- **Inject a deliberate fault, confirm the gate FAILS, then remove it.** Prefer the command CI runs
  over a hand-rolled one. CI's is the one whose subject is known-good.
- **A passing mutant is not a result.** A missing test, a mis-targeted file, a filtered test, a stale
  build and a genuinely uncovered branch all give the identical observation. Count twice: prove the
  detector exists (watch the test count move), then require the failure count to move under the mutant.
- **Proving the check RAN is not proving the assertion had anything to look at.** An accessibility
  sweep was proven to run by a real test-count delta. The seed put every item one day outside the
  rendered range. So for weeks the assertion ran over an empty grid and reported clean while the
  violation was serious.
- **A trigger that never fires, one that always fires, and one whose silence you cannot read are the
  same fault.** An empty artefact may come identically from *it ran and saw nothing* and from *it
  never ran*. Then you have no instrument. An instrument must deliver, not just fire, and report on
  itself.
- **A cwd-relative path in a scanner reports a clean tree over ZERO files** when the pipeline runs the
  script from another directory. Resolve paths from the script's own location. Run it the way the
  pipeline runs it, not only from the repository root.
- **A script passed inline through a shell is not the script you wrote.** The shell rewrites escapes
  and reads flags out of quoted text. The mangled instrument returns zero over a set it never read.
  Write the script to a file with the editor and run the file. A zero that contradicts a count you
  already know is a broken instrument, not a finding.

## 3. Is it the RIGHT subject?

Step 2 guards against no subject. This guards against the **wrong** one. The scan runs, the count
moves, and the number is true of a set that excludes the answer.

- **State the denominator out loud and ask what it excludes**: which file types, directories,
  spellings, quoting. Report it with the finding: *"twelve of fourteen paged reads"*, not *"twelve
  uncapped reads"*.
- **A census over a store that something else prunes holds for the day it was taken.** State its
  horizon beside the count: the oldest and the newest item it read. "Never" over such a store
  means "not within the horizon". A count of session records read 685, 673, 667 and 678 on four
  runs in two days. The first three held one and the same count of calls inside them. The
  harness swept old records and wrote new ones between the runs, and nothing in the counts
  said so.
- **A zero is the most dangerous result**, because absence is what people act on. When a scan returns
  zero for something a record claims exists, treat the **scan** as the prime suspect before the record.
- **Choose a control spelled the same way as the term under test**, and **from OUTSIDE the scope you
  are searching.** A control from inside confirms that boundary. It cannot test it. A sweep of five
  registers was properly calibrated and still returned a clean, evidenced, wrong answer. The
  journal was not in the swept scope, and no control chosen from within could reveal that.
- **A HIT on the wrong spelling is worse than a zero and has no control at all.** A substring match on
  a longer name created a whole defect row about the wrong file. A zero prompts a second look. A hit
  does not.
- **A prescribed command is a claim to re-verify, not an authority to quote.** A committed "measure it
  with this command" keeps its authority long after the artifact it measures was rewritten underneath
  it. What catches it is refusing a number that disagrees with something you independently know.
- **A singular argument over a plural result is a clean answer about the wrong subject.** The scoping
  query may return several rows: every active slice, every open item. Run the check on every row it
  returns. A command written for one silently adjudicates one and leaves the rest unasked, and
  nothing downstream says so.
- **A count of what an instrument DID is not a count of what it FOUND.** Two catches and one
  confirmation are three uses of the instrument and two findings. A sentence that carries the three as
  findings carries a wrong number into every artefact that quotes it.
- **An instrument measures the quantity it counts and nothing else.** A scanner's candidate-line count
  is not a render-site count, and a line count is not an instance count. Before stating a different
  quantity, run a different command.
- **A substring proxy removes rows that NAME a thing without covering it**, and keeps for itself the
  judgement the script cannot make. Treat such a rule's output as triage, never as the worklist.
- **EVERY item differing is as suspect as none differing.** A compare may report a whole tree changed
  against a tree you have other reason to believe identical. Then it measured the TRANSPORT (line
  endings a checkout rewrote, an encoding, a path prefix) and not the content. Normalise what the
  transport rewrites, prove the compare still catches a one-byte change, then read the result. Every
  file of an installed tree, images included, once read as changed. Each file's size gap equalled
  its count of carriage returns.

## 4. Two sources agree?

- **Ask what MECHANISM they share, not how different the tooling looks.** Two independently written
  scanners returned the same sites across the same files. Both were blind to the same fifth of
  the surface, because both keyed on the same token in the same position. Change the subject, not the
  sophistication. Prefer an instrument whose subject is an enumerable population (assert the count)
  over one whose subject is a pattern.
- **Superficial difference is not independence.** A different runner, orchestrator or machine is not
  independence if both paths load the same artefact. But the relationship is asymmetric. Two
  non-independent observations are weak evidence about *where* a fault lives and **strong** evidence
  that a change to their shared component worked.
- **A match on VALUE is necessary and never sufficient when another producer can write the same
  value.** A log line equal to your replay to the character proves WHAT was written, never WHO wrote
  it. A background process started in the same place writes the identical line. Take the identity
  from an instrument that carries one, and put it in the line when the line is yours to change. *No
  other process ran* is a control you can keep only over processes you start. A verdict about an
  operator's session was read from a line a background session had written in the same folder. It
  reached a journal entry, a report and a memory file before the run's own control exposed it.

## 5. After the number is in your hand

- **A measurement that runs AFTER the action it should gate is a report, not a control.** In a chained
  command the number prints, is correct, and changes nothing. You read it after the push has already
  happened. Make the action **conditional** on the measurement, and the same number becomes a gate.
- **Correcting a number does not correct what was concluded from it.** Those conclusions stay where
  they were written, detached from the evidence. They read exactly like conclusions drawn from the
  corrected value. Sweep for what was inferred from the old one and re-derive it, or mark it as
  resting on a superseded measurement (`tamheed:written-claims`).
- **Record the variables you are HOLDING, not just the one you are varying.** An investigation varied
  command shape exhaustively across three sessions and never recorded which paths the commands read.
  The paths were the cause. One controlled pair settled it in two commands.

## 6. Cause, control and classification

The step most often skipped by people who did steps 2–5 properly.

- **A positive control proves the instrument FIRES. It cannot prove the trigger's quantity is the
  fault's symptom.** A stall watchdog was mutation-checked ten of ten, through a seam built so the
  control could exist. Its trigger measured whether the process was scheduled. When the fault came,
  that quantity never left its healthy value while every request burned its whole ceiling. No
  threshold on it could ever have fired. Ask what the trigger measures, and whether the fault moves it.
- **Ask what you CHANGED in order to observe this, and whether the environment the claim governs
  has it.** A build logger was calibrated against a throwaway image with a verbosity flag added
  precisely to see its output. It shipped into a pipeline that lacked the flag. The act of observing
  supplied the missing link, so the instrument passed its own test in the one place the fault could
  not occur. Prefer a channel the target environment already uses.
- **One calibration licences one check.** Checks that share a parser, a loader or a key extractor do
  not share trustworthiness. Each embodies its own claim about what correct looks like and needs its
  own oracle. The oracle is independent, because re-reading your own code finds nothing: the code did
  exactly what you wrote.
- **A reproduction CONFIRMS. Only an intervention EXPLAINS.** Recreating a failure on demand proves
  that something in what you changed is sufficient, and silently credits whichever change you were
  already watching. List everything the setup changed, not what you meant to change. Vary ONE
  thing, and predict the outcome before running it. Treat the FIX as the real experiment: a fix that
  fails under the true failing precondition falsifies the mechanism.
- **A root-path tool names A path, never THE cause.** Removing the named, plausible suspect may
  change nothing while the enumeration of roots cannot end. Then the retention is structural, and
  that inability to end is itself the tell.
- **Classify from source, never from an attribute, a register row or a filename.** Three proxies in
  one session each said "built" while correcting the previous one. The sharpest case was a routed,
  well-commented, EMPTY shell whose own header said nothing was drawn. Check both directions, and
  check that the instrument can discriminate at all.
- **A layer no test can reach is not a gap in the tests. It is a property of the composition, and
  it worsens as protection improves.** When an earlier layer refuses the whole population a later
  layer exists to refuse, the later one cannot be exercised from outside. Assert it at its own
  boundary and give each layer a distinguishable signature. Three tests asserting the same refusal
  read as rigour while testing whichever layer runs first, and keep passing if any one is removed.
- **When a new instrument disagrees with an old one, both hypotheses predict the observation.** The
  new one miscounts, or the old one credited what it should not have. Shrink the disagreement to ONE
  artefact small enough to adjudicate by hand. Read per-item output rather than a percentage, and read
  the disputed item yourself.

## When a premise looks untestable

Before recording a premise as untestable, list your instruments. Ask whether every one of them is an
OUTPUT you are comparing against another output. If so, the *producer* of at least one output is a
further instrument, and it is usually cheaper than either comparison. The producer is source code, a
schema, a generator, a migration. A premise carried for weeks as unverifiable was settled in one
command by reading the code that wrote the output. When a record states that something cannot be tested, treat that as a
claim to check rather than a fact to inherit.

---

## What this skill does NOT cover

- **Not** how to write or structure tests. `tamheed:test-evidence` covers what a test proves.
- **Not** how to read CI runs: `tamheed:ci-evidence`.
- **Not** how to write to the package, quote records for a decision, or run an operator interview:
  `tamheed:package-writes`, `tamheed:reading-the-record`, `tamheed:operator-interview`.

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral. This file is the procedure.*
