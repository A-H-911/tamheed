---
name: boundary-semantics
description: Use whenever you are about to change a comparison on a date or numeric boundary (<= vs <, >= vs >) — verify the intended boundary semantics against the spec BEFORE touching the operator.
---

# Boundary semantics before comparison changes

The operator in a boundary comparison is a semantic decision, not a typo. Fixing
it without deciding the semantics can silently flip the boundary the other way.

Before changing any predicate on a date/number boundary:

1. Pin down what the spec says the boundary case means (e.g. is a task due
   TODAY overdue?). If the spec is silent, get the decision recorded — do not
   pick the operator that makes the visible case pass.
2. State the intended inclusive/exclusive semantics explicitly in the
   requirement or in the test name.
3. Add the exact-boundary test case first, and watch it fail against the
   current comparison.
4. Only then fix the comparison to match the decided semantics, and let the
   boundary test prove it.

Followed, boundary fixes land once, with a test that fails if the semantics
regress. Skipped, the comparison gets flipped to whatever makes today's symptom
disappear, re-breaking the opposite boundary later.

Distilled from LL-001 in package `package`.
