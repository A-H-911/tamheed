---
status: Implemented
version: 1.0.0
updated: 2026-06-17
generation: derived
---

# Acceptance audit

Seeded defect: this audit omits AC-003 (defined in the acceptance criteria), so the
G-PROGRESS coverage check must fail on this package.

| AC | Criterion | Verdict | Evidence |
|---|---|---|---|
| AC-001 | Long URL returns a unique short code. | Met | tests; commit a1b2c3d |
| AC-002 | Known short code redirects to the target. | Met | tests; commit d4e5f6a |

## Summary

- MVP: 2 of 3 audited; one criterion left out on purpose for the fixture.
