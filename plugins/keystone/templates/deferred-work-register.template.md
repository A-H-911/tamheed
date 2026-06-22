---
status: Draft
version: 0.1.0
updated: <YYYY-MM-DD>
owner: <name-or-role>
---

# Deferred-Work & Tech-Debt Register — <project-name>

<!-- A durable, findable index of known-but-not-yet-done work: deferred scope and accepted tech debt, each
     actionable enough that a future session can pick it up cold. This is TRACKING, not a contract — the
     approved plan lives in the roadmap/registers; architecture decisions in the ADRs. Distinct from
     execution/backlog.md (forward work derived from the WBS): this register is known-not-done / debt taken
     on purpose. Generation class: Conditional (long execution horizon / handoff).
     Lives at: execution/deferred-work-register.md. -->

## Conventions

- **#** — a stable local number for the entry (this register defines no governed identifier prefix).
- **Severity** — Low / Med / High (correctness, security, or visual/UX impact — not mere tidiness).
- **Invariant at stake** — the `INV-` (or quality bar) this touches, if any.
- **Status** — Open · In progress · Done (move to a dated note) · Won't do (record why).

## Entries

| # | Item | Severity | Invariant at stake | Proposed (additive) fix | Acceptance / guards | Status |
|---|---|---|---|---|---|---|
| 1 | <known coupling / shortcut taken> | Low | <INV-00x or —> | <smallest behavior-preserving change> | <test/guard that proves it closed> | Open |
| 2 | <missing edge-case handling> | Med | <—> | <the fix> | <regression test> | Open |

## Deferred scope (tracked elsewhere — index only)

<!-- Out-of-current-scope work recorded in its canonical place; listed here so this register is the single
     index of "known not-yet-done". -->
- <feature> — deferred to <PH-x / a future version>; see <roadmap / `DEC-00x` / `RISK-00x`>.
