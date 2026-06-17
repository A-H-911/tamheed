---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Hypothesis Register — <project-name>

<!-- A hypothesis is a falsifiable statement we can test to resolve an uncertainty. Each must name the
     signal that would CONFIRM it and the signal that would REFUTE it, so the test is decisive.
     Identified HYP-NNN (governance.md). Generation class: Conditional (genuine technical uncertainty).
     Lives at: research/hypothesis-register.md. Tested by EXP-/POC-. -->

## Conventions

- **Hypothesis** — a single falsifiable claim ("<approach> achieves <property> under <condition>").
- **confirm_signal** — the observation that would confirm it.
- **refute_signal** — the observation that would refute it.
- **Tested by** — the `EXP-`/`POC-` that produces the signal.
- **Result** — Confirmed | Refuted | Inconclusive | (untested).
- **Status** — Draft | Proposed | Approved | Deferred | Superseded | Obsolete.

## Hypotheses

| ID | Hypothesis | confirm_signal | refute_signal | Tested by | Result | Status |
|---|---|---|---|---|---|---|
| HYP-001 | <approach> meets <threshold> under <load>. | <measured value within budget> | <value exceeds budget> | EXP-001 | untested | Proposed |
| HYP-002 | <library/category> supports <capability> without <cost>. | <feature works in spike> | <missing / blocked> | POC-001 | untested | Proposed |
| HYP-003 | <claim> | <confirm> | <refute> | EXP-002 | untested | Draft |

<!-- When a hypothesis resolves, record the result here AND feed it into the decision it informs
     (DEC-/ADR-) and any risk it changes (RISK-). A refuted hypothesis is a valuable, kept result. -->
