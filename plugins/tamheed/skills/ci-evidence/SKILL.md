---
name: ci-evidence
description: >-
  Use before stating that CI or a deploy is green, red or done; before recording an audit verdict,
  a gate-decision journal entry or a done-claim that rests on a CI run; before predicting whether a
  push or pull request will run jobs; before explaining why a job was skipped; and before listing the
  gates you ran.
---

# CI evidence

**A CI claim is true only for one run, one event and one tree. Name them, or you have not said
anything.**

The failure this prevents is a true observation with the wrong thing attached to it: a colour from one
run given to a different tree, a skip given the cause you happened to see, a gate list that looks
complete. No gate catches these. Every id resolves and every status is right; only the attached claim
is wrong.

---

## The procedure

**1. Cite the run id and the event, never a colour.**
Write `run <id> (push, main) => failure`, not "the merge was green". After a merge, poll the TARGET
branch's run to completion before recording anything that depends on it; a pull request's checks show
the PR-head run and can read all-green while the branch is red.
- *Why:* a PR-head run and a merge-commit run are different runs over identical code, and they can
  disagree. A run id cannot be attributed to the wrong tree; a colour can.
- *Field evidence:* a verdict called the merged tree green while the merge commit's own run concluded
  failure with the backend red.

**2. Decide which event you are reasoning about before predicting whether anything runs.**
On a direct push, a path filter is checked against that push, so a package-only commit may run
nothing. On a pull-request event it is checked against the whole PR diff, so a package-only commit to
a PR that also holds source re-runs every workflow in full.
- *Why:* recording a CI result on the PR that produced it starts a new run and supersedes that result.
  Either record after the merge, or accept the extra cycle on purpose. Both routes cost something; the
  mistake is not knowing there is a choice.
- Do not turn this into "path filters do not work". Both behaviours are correct; they are different
  events. And a direct push that ran no jobs was not scanned; it was skipped.

**3. Never explain a `skipped` job from its condition alone.**
A job with both a condition and a dependency list reports `skipped` when the condition is false AND
when a needed job did not succeed. Check the conclusions of every job it needs on that same run, and
check the condition's inputs directly. Best: find a control run where the needed jobs passed. Write
down what you MEASURED apart from what you INFERRED.
- *Why:* when a status has several causes and you can see only one, you have matched a cause, not
  measured it.

**4. Build a gate list from the CI workflow, not from memory.**
Read the workflow and list its steps, then report against that list, naming each step you did NOT
run ("Coverage: not run"). Run a coverage gate in the build configuration CI uses; a coverage number
belongs to code, tests AND build configuration.
- *Why:* a gate you forgot leaves no trace in a list you wrote yourself.
- *Field evidence:* twenty-nine commits carried a gates line without coverage; run at last, coverage
  failed on eight files, while a debug build had flagged a file that a release build cleared.

**5. Bound and prove any poll loop before backgrounding it.**
Run the predicate once in the foreground and read the value it produces. Bound every loop by an
iteration count and print the raw predicate value at exit. Treat a poller that has gone quiet as
suspect, not as "still running".
- *Why:* an unbounded loop turns an evaluation failure into a silent hang. Three background pollers
  once held an error string, never the zero they waited for, and would have run forever.

## Recording it in the package

The rows are the obligations table's (this project's `CLAUDE.md` note). What this skill adds: the
commit a verdict names is the sha the run tested, on the remote (`tamheed:package-writes` §6), and its
evidence names the run id and event; a `gate-decision` progress entry quotes run id, event and tree
and lists the gates by the workflow's own names, with "not run" beside each one you skipped. Never
journal "CI green" without a run id; the next reader cannot re-derive which tree it was.

---

## What this skill does NOT cover

- **Whether a number or scan means what you think in general** — `tamheed:measurement-evidence`.
- **What a test proves** — `tamheed:test-evidence`.
- **What a record says** — `tamheed:reading-the-record`.
- An automated dependency-update tool's ignore rules and other vendor-specific mechanics — those
  stay with the project that learned them.

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral; this file is the procedure.*
