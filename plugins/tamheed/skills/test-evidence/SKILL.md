---
name: test-evidence
user-invocable: false
description: >-
  Use BEFORE writing a test for a refusal, guard, limit, absence or error path. Use before recording
  a Met verdict whose evidence is a passing test or suite. Use before accepting that an existing test
  proves what its name claims. That includes when a suite is green, and when a test asserts something
  did NOT happen. It includes when the subject is a size, timeout or permission limit, and when a test
  shares a host, database or global with others.
---

# Test evidence

A test can run, assert a true thing, and pass, while proving nothing about the code you wrote. An
`audit_record` verdict of `Met` with `verification_method: auto-test` is only as strong as one
answer. **What did this test actually exercise, and from where did it look?**

Work top to bottom. Each step is cheap. Steps 1–3 catch the failures that reach users.

## 1. Would it fail against the defect it claims to prevent?

Remove or invert the guard and re-run. If the test still passes, it is not testing your guard.

**And if it fails, ask whose behaviour made it fail.** An assertion can be live, load-bearing in
appearance, and satisfied entirely by framework code you did not write. A wrapper added so a hung
dependency fails fast asserted a timeout exception. The framework already threw that exception.
The assertion would have gone green with the whole guard removed.

- The work may IMPROVE an existing failure rather than create one. Think of a timeout that already
  fires but says nothing useful, or an exception that already throws without context. Then the
  difference is
  the entire deliverable, so assert the difference.
- Asserting on an exception TYPE feels more rigorous than asserting on its message. It is often the
  inherited half. A type assertion that can never fail spuriously can never fail usefully.

## 2. Are you asserting on the artefact the recipient reads?

A status code proves the refusal HAPPENED. Only the payload proves it is USEFUL, and a green suite
reports those identically.

When a refusal, warning or diagnostic exists to TELL somebody something, **assert at the outermost
boundary you can reach**. That is the response body on the wire, the rendered page, the log line as
written, never the object the producer threw. Two instances months apart had the same shape. A handler
computed the missing setting names perfectly and the wire carried an empty error list. A domain
refusal carried an instruction and the wire carried a bare conflict title. Both had green unit tests
asserting the right strings on the exception's message. **No assertion on the producer's side can see
the gap between the object thrown and the bytes serialised.**

Keep the cheaper inner test if one exists. Never let it stand as the evidence for the clause.

## 3. Is the assertion NEGATIVE?

*Nothing was received. Nothing threw. No rows were written.* These hold identically whether the code
ran and correctly did nothing, **or never ran at all.** Framework scheduling usually decides that
distinction. It is an implementation detail that changes between versions, so a negative test can
be silently emptied by an upgrade and stay green forever.

Pair every negative assertion with an instrument that measures **execution**, not outcome. That is
a call count, a counter that only increments when the mechanism fires, or a positive control in the
same test.

## 4. Did the test CONSTRUCT its subject, or SELECT it?

A test may pick its subject out of mutable shared state: a live register, a seeded database,
whatever row happens to match. Such a test's meaning changes when somebody does ordinary work.
**The dangerous outcome is not the failure, it is the pass.** A promotion, a status flip or an added
row substitutes a different subject. The code still runs and the assertion is now about something
that was never under test. Construct the subject in the test.

## 5. Does the test's environment ENFORCE the thing under test?

A test proves a behaviour only on a host that implements it. Two measured shapes:

- **An in-process test harness that does not enforce the production server's request limits.** An
  endpoint ran under the production server's default body cap while the application's configured cap
  was larger. Every test through the harness passed. No user could upload the size the configuration
  promised. A size, timeout or connection limit is proved only against the server that enforces it.
- **An in-memory database stand-in with no transaction to leave uncommitted.** A raw save through the
  real host's dependency scope opened the transaction that only the request pipeline commits. So it
  wrote **nothing** and reported success. The idiom is correct everywhere it appears and unsafe the
  moment the host points at the real database.

Ask of any limit, constraint or transactional guarantee: **has this ever run against the thing that
enforces it?** The failure presents at the wrong layer. A discarded write surfaces as a not-found that
reads like a routing fault. The seeding call that caused it is the one line that reported success.

**A migration's verdict comes from executing it, never from building.** A solution that builds clean
and formats clean can still fail most of its tests at runtime. One did, twice, for unrelated causes a
stricter framework version refuses. A build is a claim about compilation only.

## 6. Can this test damage the ones after it?

A test that times out **never reaches its cleanup**. So any global it installed (a stubbed clock, a
patched module, an intercepted transport) survives into every test after it. The wreckage reads as
pre-existing breakage in code you did not touch. Sixteen of twenty-three tests failed across unrelated
features, and every one of those failures was the new test's.

- Run the single new test in ISOLATION to separate your failures from the file's.
- Prefer an approach that cannot leak (real timers plus polling) over one that needs cleanup.
- A control proven against one implementation says nothing about the next. **Re-run the control
  whenever the thing it is a control FOR changes**, not only when something looks wrong.
- **A fix for a race that passes locally proves nothing.** The local machine wins the race every
  time, so only a loaded runner can see it. A stop that cancels before it awaits is not a join. Make
  the fix deterministic by construction (await the body itself), never by timing.

## 7. Reading the numbers around the test

- **A per-file coverage floor is a ratio, and a refactor moves the denominator.** A file can drop
  under the floor without one new untested line. Adding well-tested code beside a real gap raises
  the percentage and silently carries the gap back over the threshold.
- **A re-run is not a second sample of the question you asked.** A suite re-asks every assertion it
  contains, so a latent timing- or environment-dependent defect can surface on any draw. The cost of a
  re-run is bounded. Its value is not bounded by the question that prompted it. This does not license
  re-running a red to see if it passes. Where a project rule forbids that, the rule wins.
- **Coverage proves a line ran under test, never that production code calls it.** A method can be
  fully covered and never invoked outside its own test. Coverage catches unread state, not an
  uncalled method.

## Recording the verdict

The verdict row is the obligations table's (this project's `CLAUDE.md` note). What this skill adds:
`evidence` names the test and the run it passed in. `auto-test` is honest only when steps 1–3 hold.
The commit it was verified against is a sha on the remote (`tamheed:package-writes` §6). A verdict
whose evidence is "the suite is green" names no subject.

---

## What this skill does NOT cover

- Whether a measurement, scan or CI result means what you are about to claim:
  `tamheed:measurement-evidence`, `tamheed:ci-evidence`.
- Whether a record says what you are about to assert it says: `tamheed:reading-the-record`.
- Deciding what to test, coverage targets, or test naming. This skill is only about whether a test
  that exists proves what it appears to prove.

---

*Adapted from a prior project's operator-confirmed lessons (2026). The instances are illustrative,
anonymised and stack-neutral. This file is the procedure.*
