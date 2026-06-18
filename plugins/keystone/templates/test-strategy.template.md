---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Test Strategy — <project-name>

<!-- How quality is verified: levels of testing, what each covers, and the specific test/validation
     items (TEST-NNN) that exercise requirements and acceptance criteria.
     Identified TEST-NNN (governance.md). Generation class: Conditional (non-trivial NFRs / requested).
     Lives at: validation/test-strategy.md. Every MVP FR-/NFR- must reach >=1 TEST- (gate G-TRACE). -->

## Approach

<!-- The testing philosophy and levels in scope, each with what it covers and tooling (tech-neutral
     where possible). Add/remove levels by project need. -->

| Level | Covers | Tooling (category) | In scope? |
|---|---|---|---|
| Unit | <component-internal logic> | <test runner> | Yes |
| Integration | <contracts between components> | <runner / harness> | Yes |
| End-to-end | <user-visible flows> | <e2e harness> | <Yes/No> |
| Non-functional | <perf / security / reliability per NFR-> | <load / scan tooling> | <Yes/No> |
| Regression / golden | <invariants e.g. determinism INV-001> | <golden-file diff> | <Yes/No> |

## Test items

<!-- One row per TEST-. Link what it verifies so the traceability matrix can connect TEST -> FR/NFR/AC. -->

| ID | What it verifies | Level | Verifies (FR/NFR/AC/INV) | Status |
|---|---|---|---|---|
| TEST-001 | <behavior> | Unit | FR-001, AC-001 | Proposed |
| TEST-002 | <threshold under load> | Non-functional | NFR-001, AC-002 | Proposed |
| TEST-003 | <invariant holds> | Regression | INV-001 | Draft |

## Environments and data

- **Reference environment:** <pinned runtime/versions used for measurable NFR checks>.
- **Test data:** <fixtures / golden files / synthetic data approach>.

## Coverage and exit

- **Coverage target:** <e.g. critical paths covered; % if meaningful>.
- **CI gates:** <which tests must pass to merge / to exit a phase>.
- **Definition of done linkage:** see [definition of done](../execution/definition-of-done.md).
