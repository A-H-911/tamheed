# Follow-up prompts — support-triage-agent

One prompt per phase gate, plus situational prompts. Each resumes from the prior phase's exit criteria and
restates the invariants still in force. Reference artifacts by path.

---

## PH-2 gate — Calibration, confidence routing, gated auto-send

**Resume context.** Phase PH-1 is complete and approved: assisted triage is live, a human approves every
send, and a full audit trace exists per email (`AC-005`). The calibration experiment has run:
**`EXP-001` = PASS**, so `DEC-004` / `ADR-0004` is now **Approved**, and auto-send is enabled **only** for
the low-risk categories named in that approved decision.

**Goal.** Add confidence-based routing and guarded auto-send for the approved whitelist.

**Bounded tasks (each with PASS/FAIL):**
1. Implement confidence-threshold routing per `ADR-0004` (`WBS-6.1`).
   PASS: low-confidence and sensitive categories always escalate to a human (`FR-005`); routing matches
   the calibrated policy on the eval set.
2. Enable auto-send strictly for the approved whitelist, with a kill-switch and per-category error
   monitoring (`WBS-6.2`, `FR-008`).
   PASS: only whitelisted categories auto-send; all others still route for approval; the kill-switch halts
   auto-send on demand and is tested.
3. Expand audit/monitoring dashboards for per-category error and cost.
   PASS: per-category error and cost are observable from the audit trail (`INV-004`).

**Invariants still in force.** `INV-002`, `INV-003`, `INV-004`, `INV-005` hold unconditionally;
`INV-001` is narrowed **only** for the whitelisted categories in the approved decision — everything else
still requires human approval.

**Exit gate.** Measured per-category error stays under the agreed bar; kill-switch verified;
`KPI-001`/`KPI-002` trending to target. **Pause for review.**

> If `EXP-001` had **failed**: do not start PH-2. Record the result, keep the PH-1 supervised system
> (`INV-001` for all categories), and produce the documented recommendation instead.

---

## Situational prompts

- **Fresh-session refresher.** "Re-read `00-charter.md`, `requirements/invariant-register.md`, and
  `planning/roadmap.md`; summarize the current phase, the invariants in force, and the next bounded task
  before doing anything."
- **Invariant audit.** See [`review-prompts.md`](review-prompts.md).
- **Deviation ADR.** "You need to deviate from the plan at `<file:line>`. Stop. Draft a new ADR
  (`adr-000N-…`) capturing context/decision/alternatives/consequences, mark it Proposed, and wait for
  approval before implementing."
- **Bug triage.** "A defect was found in `<area>`. Reproduce it, identify which `FR-`/`INV-` it touches,
  add a failing `TEST-`, fix, and confirm no invariant regressed."
- **Status report.** "Summarize progress against `planning/roadmap.md` and `planning/work-breakdown.md`:
  WBS items done/in-progress/blocked, gate status, and any new risks."
