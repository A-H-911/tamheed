---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Acceptance Criteria — <project-name>

<!-- The conditions under which work is ACCEPTED. Split into MVP (must hold to ship the minimal viable
     product) and Full target. Each criterion must be TESTABLE — phrased so PASS/FAIL is unambiguous.
     Identified AC-NNN (governance.md). Generation class: Always. Lives at:
     validation/acceptance-criteria.md. Approved acceptance criteria are immutable (supersede, don't
     rewrite). Every behavior-bearing FR-/NFR- must reach >=1 AC- (gate G-TRACE). -->

## Conventions

- **Criterion** — testable; prefer Given/When/Then or a clear measurable assertion.
- **Verifies** — the `FR-/NFR-/KPI-` it accepts.
- **Tested by** — the `TEST-` that exercises it (where automated).
- **Tier** — MVP or Full. **Status** — Draft | Proposed | Approved | Implemented | Deferred | Superseded.
- **Evidence** *(optional)* — once verified, the proof: `TEST-`/commit/CI/golden. The authoritative live
  verdict×evidence record is the derived [acceptance audit](acceptance-audit.md); this column is an
  optional mirror, and the criterion text stays immutable after approval.

## MVP acceptance criteria

| ID | Criterion | Verifies | Tested by | Status | Evidence |
|---|---|---|---|---|---|
| AC-001 | Given <context>, when <action>, then <observable result>. | FR-001 | TEST-001 | Proposed | — |
| AC-002 | <operation> meets <measurable threshold> under <condition>. | NFR-001 | TEST-002 | Proposed | — |
| AC-003 | <testable assertion> | FR-003, KPI-001 | TEST-003 | Draft | — |

## Full-target acceptance criteria

| ID | Criterion | Verifies | Tested by | Status | Evidence |
|---|---|---|---|---|---|
| AC-010 | <testable assertion for full scope> | FR-010 | TEST-010 | Proposed | — |
| AC-011 | <testable assertion> | NFR-002 | TEST-011 | Draft | — |

<!-- A criterion that cannot be tested is not an acceptance criterion — rewrite it until PASS/FAIL is
     decidable. Keep MVP criteria minimal and decisive. -->
