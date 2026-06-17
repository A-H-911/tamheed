# Follow-up prompt — Phase PH-2 gate (support-triage-agent)

## Resume context

Phase **PH-1 is complete and approved**. Assisted triage is live: every email is ingested, classified, grounded against the knowledge base, and presented for human approval, and **no reply is sent without approval** (INV-001). A **full audit trace exists per email** (INV-004). The **EXP-001 confidence-calibration spike has PASSED** — measured accuracy meets the NFR-001 bar and a confidence threshold isolates a low-risk subset at acceptable error — so **ADR-0004 is now Approved**. As a result, **auto-send is enabled ONLY for the whitelisted low-risk categories named in that approved decision.** Every other category still requires human approval.

## PH-2 goal

Add **confidence-based routing** and **guarded auto-send** for the approved whitelist of low-risk categories, while every safety invariant other than the narrowly-relaxed INV-001 remains fully in force.

## Bounded tasks (execute in order, pause for review after each)

**Task 1 — Confidence-based routing (ADR-0004, FR-005).** Implement routing/escalation by classification confidence and category sensitivity.
- PASS: low-confidence or sensitive-category emails escalate to a human queue; high-confidence whitelisted items are marked auto-send-eligible.
- PASS: thresholds match the EXP-001-validated calibration.
- FAIL: any sensitive category routed to auto-send, or any threshold not traceable to EXP-001.

**Task 2 — Guarded auto-send for the approved whitelist (FR-008).** Enable auto-send strictly for the explicitly whitelisted low-risk categories from the approved ADR-0004.
- PASS: auto-send fires **only** for categories named in the approved decision; everything else still routes for human approval (INV-001 preserved outside the whitelist).
- PASS: a **kill-switch** disables auto-send instantly, and **per-category error monitoring** is wired with an alert when measured error exceeds the bar.
- FAIL: auto-send on any non-whitelisted category, any ungrounded auto-sent reply (INV-002), or a missing/untested kill-switch.

**Task 3 — Expanded audit & monitoring dashboards.** Extend the audit trail and add operational dashboards.
- PASS: auto-sent replies carry the same full decision trace as approved ones (INV-004), distinguishable as auto-sent.
- PASS: dashboards surface per-category accuracy/error, deflection (KPI-001), handling-time saved (KPI-002), and reply quality (KPI-003).
- FAIL: any auto-sent reply without a complete audit trace.

## Invariants still in force

- **INV-002** (never fabricate — ground every claim or defer), **INV-003** (no PII leaves the trust boundary), **INV-004** (every action logged with rationale), and **INV-005** (tool allow-list + cost/iteration cap) remain **absolute and unchanged**, including for auto-sent replies.
- **INV-001** is **relaxed ONLY** for the explicitly whitelisted low-risk categories named in the approved ADR-0004. For every other category, no reply is sent without human approval.

## PH-2 exit gate

All three tasks PASS; measured per-category error for each whitelisted category stays under the agreed bar in production monitoring; the kill-switch has been tested end-to-end; INV-002/INV-003/INV-004/INV-005 confirmed to hold for auto-sent traffic. On pass, proceed to PH-3 planning (broaden categories + ongoing quality monitoring).
