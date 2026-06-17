# Clarifications — repostat

The brief is small and internally consistent. Only a few points actually change the plan, so they
are batched into one round rather than asked piecemeal. Items that do not change scope (e.g. the
exact column order of the stdout table) are left to execution and not asked here.

## Clarification batch (asked together)

1. **Which export formats are in the MVP, versus later?** The brief lists JSON, CSV, and Markdown
   but is unsure if all three are needed to be "usable."
   Answer ([given]): JSON is the only MVP export; stdout table is MVP; CSV and Markdown move to the
   second phase. Captured as ASM-001.

2. **Is there a target runtime / packaging preference, or is that open?** The brief is tech-neutral
   ("compiled or interpreted, don't care") but a runtime has to be picked to build.
   Answer (assumed): No preference stated; assume a single interpreted CLI distributed as one
   installable package, runtime version pinned at bootstrap. Recorded as an assumption, **not** a
   requirement, so it can be revisited. Captured as ASM-002.

3. **What is "too big" — what repository size must the tool handle within an acceptable wait?**
   The brief mentions one repo with deep history but gives no number.
   Answer (assumed): target a repository of up to ~50,000 commits, producing the default report in
   roughly ≤10 seconds on commodity hardware; larger repos may run slower but must still complete.
   Captured as ASM-003 and drives NFR-002.

4. **How should the two-emails-are-one-person problem be handled in the MVP?**
   Answer ([given]): out of scope for MVP. Authors are keyed by raw committer email in v1; an
   identity-merging strategy is deferred (see DEC- in `readiness.md`). RISK-002 tracks the
   readability impact in the meantime.

5. **Are date-range and branch filters in scope for the first usable version?**
   Answer ([given]): "nice to have," not MVP. Defaults to all-history on the current branch (HEAD);
   filters are a later enhancement and do not block the MVP. No new assumption needed.

## Assumptions recorded

| ID | Assumption | Basis | Risk if wrong | Status |
|---|---|---|---|---|
| ASM-001 | MVP exports = JSON only + stdout table; CSV and Markdown are Phase PH-2. | Clarification Q1 ([given]); "JSON for sure," CSV/Markdown "nice to also get." | Low — if CSV/Markdown are needed sooner, PH-2 is pulled forward; the report model (ADR-0001) already makes formats additive. | Proposed |
| ASM-002 | A single interpreted CLI, distributed as one installable package, runtime version pinned at bootstrap. No specific language mandated by the user. | Clarification Q2 (assumed); brief is explicitly tech-neutral. | Low–Med — a different runtime/packaging choice changes the bootstrap and Prerequisites but not the requirements or invariants. Revisit before repo bootstrap. | Proposed |
| ASM-003 | Performance target: ~50,000-commit repository, default report in ≤10 s on commodity hardware; larger repos still complete. | Clarification Q3 (assumed); brief wants "reasonably fast" on a "deep history" repo, no number given. | Med — if real repos are far larger, NFR-002 and RISK-001 mitigations (streaming, caching) gain priority. | Proposed |

A note on contradictions: **no hard contradictions were found** between the brief, the clarifications,
and the recorded assumptions. The only soft tension — wanting three export formats but an unclear MVP —
is resolved by ASM-001 (phasing) rather than by dropping any format. Scope can be locked.
