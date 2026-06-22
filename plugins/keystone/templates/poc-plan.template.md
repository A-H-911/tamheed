---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
id: POC-NNN
---

# POC-NNN — <proof-of-concept title>

<!-- A proof-of-concept demonstrates that an approach is FEASIBLE end-to-end (vs an experiment, which
     measures one variable). Throwaway by default — its output is a go/no-go and learnings, not
     production code. One POC per file. Identified POC-NNN (governance.md).
     Generation class: Conditional (genuine technical uncertainty). Lives at: pocs/. -->

## Goal / feasibility question

<!-- The "can we …?" this POC answers, and what it unblocks. -->
Show that <approach> can <achieve outcome> end-to-end. Informs `DEC-00x`; tests `HYP-00x`.

## Scope

<!-- The thin slice to build — just enough to prove the risky part. State what is deliberately faked,
     stubbed, or omitted so the POC stays small. -->
- **Build:** <the minimal vertical slice>
- **Fake / stub:** <what is not real in the POC>
- **Out of scope:** <what this POC will not show>

## Success criteria (PASS / FAIL)

- **PASS if:** <the feasibility is demonstrated, e.g. the slice runs and produces <X>>.
- **FAIL if:** <blocker encountered, e.g. <capability> not achievable within timebox>.

## Method / steps

1. <setup, pinned versions>
2. <steps to build the slice>
3. <how feasibility is demonstrated>

## Timebox

<e.g. 2 days; stop and decide go/no-go regardless>

## Result

- **Outcome:** <GO | NO-GO | Inconclusive>
- **Evidence / demo:** <links, screenshots, artifact>
- **Learnings:** <what we now know; new risks RISK-00x>
- **Surprises / caveats:** <what was unexpected; the limits of what this POC actually proves>
- **Implications carried forward:** <what later phases must do because of this result>
- **Disposition of POC code:** <discard | extract learnings | seed for PH-1>
- **Date run:** <YYYY-MM-DD>
