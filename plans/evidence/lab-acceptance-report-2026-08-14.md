# Lab acceptance report — v4.0.0 (plan 031, 2026-08-14)

> The execution agent's report from the first run of `lab/scenario.md`, archived
> **verbatim** below the header (the evidence doctrine: superseded, never edited).
> Context: planning phases 1–5 were driven by the release engineer through the real
> handlers (all 8 gates green, the `[NEEDS-CLARIFICATION: OQ-001]` marker legally in
> place); phases 6–9 were driven by a REAL agent (`actor: agent:lab-exec`) calling the
> handlers itself through a CLI shim over the seed code in a scratch workspace. The
> resulting package is the `lab-tracker` eval fixture (11 deterministic assertions, all
> green). Triage of the four agent-reported findings is recorded in
> `plans/031-v4-entity-model.md` (finding 1 — no type roster in unknown-type errors —
> was FIXED in-release; 2–3 recorded cosmetic/doc'd; 4 is by design and kept).
> **Honesty limit** (lab/README.md): this run proves the mechanisms FIRE under a real
> agent; autonomous drift discharge remains provable only by an interactive fresh
> session.

---

## Tamheed v4 lab acceptance run — "tick" — execution report

### Numbered tool-call log (shim calls + key outcomes)

1. `entity_query {"type":"slice"}` — orient — ok (SL-001, SL-002)
2. `entity_query` execution-plan / acceptance-criterion / wbs-item — orient — ok (EP-001, AC-001..003, WBS-1..3)
3. `entity_query {"type":"defect"}` — ok (empty); `{"type":"risk"}` — ok (RISK-001); `{"type":"gate"}` — **error** "unknown entity type 'gate'"
4. `entity_query {"type":"test"}` — ok (TEST-001, TEST-002); `{"type":"quality-gate"}` — **error** "unknown entity type 'quality-gate'" (correct name found by reading schema.sql: `execution-gate`)
5. `entity_query {"type":"execution-gate"}` — ok (GATE-001, GATE-002); `readiness_check SL-002` — ok (not ready: acs-met AC-002/AC-003, wbs-done WBS-1/WBS-3)
6. `entity_upsert` DEF-001 Open — register bug BEFORE fixing — ok
7. `entity_upsert` DEF-003 Open + DEF-001 Fixed + DEF-002 Fixed (DEF-002 registered Open first in its own call) — ok ×3
8. `progress_update` work-done DEF-001, DEF-002 — ok (PE-001, PE-002)
9. `audit_record` AC-002 Met — ok (AV-001)
10. `entity_upsert` RISK-001 full row, risk_state mitigated, discharged_by AC-002 — ok
11. `audit_record` AC-001 Met — ok (AV-002)
12. `progress_update` work-done WBS-2 — ok (PE-003)
13. `entity_upsert` WBS-1/2/3 → Review — ok ×3
14. `entity_upsert` SC-001 Proposed — ok — **STOP** → operator approval (scripted)
15. `entity_upsert` SC-001 → Approved (on operator's words, before applying) — ok
16. `entity_upsert` FR-007 + edges SC-001—scope_adds→FR-007, SL-001—implements→FR-007, TEST-001—tests→FR-007 — ok ×4 (edges return `"id": null`)
17. `progress_update` work-done FR-007 — ok (PE-004)
18. `entity_upsert` SC-001 → Merged — ok
19. `readiness_check SL-001` — ok (only WBS-2 open)
20. `entity_upsert` WBS-2 → Implemented — ok
21. `entity_upsert` slice SL-001 → Implemented — ok (guard passed, no force needed)
22. `progress_update` transition SL-001 — ok (PE-005)
23. `entity_upsert` WVR-001 (operator's exact terms) — ok
24. `audit_record` AC-003 Not-met — ok (AV-003)
25. `entity_upsert` WBS-1/WBS-3 → Implemented — ok
26. `entity_upsert` slice SL-002 → Implemented WITHOUT force — **refused as expected** (text below)
27. `entity_upsert` slice SL-002 → Implemented with `"force": true` — ok, `forced: true`, `forced_audit: "PE-006"`
28. `entity_upsert` GATE-001/GATE-002 outcome Go — ok
29. `progress_update` gate-decision ×2 — ok (PE-007, PE-008)
30. `gate_run` — ok; `readiness_check package` — ok; `export_html` — ok

All progress_update entries carried `actor: "agent:lab-exec"`.

### Step-16 exact refusal text (verbatim)

```
readiness: SL-002 cannot transition to Implemented — acs-met: AC-003 — resolve the blockers, or re-run this item with "force": true after EXPLICIT operator confirmation
```

(Wrapped in batch error: `batch rolled back — one or more items violated constraints`, exit 1.)

### Step-17 forced result

`forced: true`, **forced_audit: PE-006** (landed before the gate-decision entries PE-007/PE-008).

### Final verdicts

- **gate_run: `ready: true`** — all mechanical gates pass (G-IDS 49 ids clean, G-DEC-STATUS, G-REQ-SRC, G-TRACE, G-SET, G-PROGRESS, G-COMPLETE, G-REL all pass; audit_evidence 3 evidenced / 0 narrated).
- **readiness_check package: `ready: false`** — blocking fail on `acs-met: AC-003` (latest verdict Not-met). `defects-minor` shows **status "waived"** with DEF-003 → WVR-001 honored. Advisory fails: `open-questions-resolved` (OQ-001, non-discriminating) and `clarifications-open` (FR-006 → OQ-001) — both pre-existing, untouched per the no-unscripted-writes contract.
- The two verdicts diverge by design: gate_run is mechanical integrity; readiness is lifecycle done-ness. The waiver covers the *defect* rule, not the *AC* rule — a package carrying a Not-met AC can never read package-ready without its own force/waiver path. Reported, not "fixed".
- `export_html` → `lab-run\lab-tracker\review.html`, 79,223 bytes, 11 CSVs emitted.

### Judgments made

- **DEF-001 severity high** — mis-flags tasks due today in core `list` output; the team named date logic their past pain. High (not critical: no data loss). Note: high blocks `defects-closed`, so I made sure its Fixed upsert landed before the close attempt — the refusal correctly named only acs-met.
- **DEF-002 severity low** — test-only, zero product impact; as written it compared two local `now()` strings and never called `tracker.add()` at all, i.e. it tested nothing. **Quarantine approach: rewrite, not skip** — new `test_added_timestamp_is_recent` drives the real `add()` against a temp DB and asserts a ≤5s tolerance window; `# DEF-002` referenced in the comment. Old test not deleted silently — replaced with the deterministic version recording why.
- **DEF-003 severity low** — cosmetic typo, left unfixed per script; stays Open under WVR-001.
- AC-002 evidence recorded "4 tests green" (true at recording time); suite grew to 5 at AC-001 and 6 after the export test — verdicts are append-only so I did not amend.
- Export test had no AC — none created (script says fine); FR-007 wired via edges instead.

### Surprises / misbehavior (the point of the run)

1. **Entity type discovery is unforgiving**: both `gate` and `quality-gate` were rejected with "unknown entity type" and the error lists no valid types — I had to read `schema.sql` to find `execution-gate`. A type roster in the error would save a round-trip.
2. **Trace-edge upserts return `"id": null`** in the items array — correct (composite PK) but reads like a failure at a glance.
3. **`force` goes inside the entity row**, not top-level on the call — the refusal text does say "re-run this item", which hints at it, but it's easy to guess wrong.
4. The flaky clock test **passed** on my one observed run — registered DEF-002 anyway from reading the source (flaky by construction, two `now()` reads).
5. The waiver/AC asymmetry (finding above): WVR-001 silences `defects-minor` but not `acs-met` for the same underlying typo — coherent design, but means package-level `ready: true` is unreachable in this scenario by construction.
6. Everything else behaved exactly as documented: the SL-001 guard passed cleanly without force, the SL-002 guard refused with the precise blocking rule, and the forced transition self-audited as a PE- row.

Code deliverables (all in the exec workspace): `tracker.py` (strict-`<` overdue fix, `history`, `export_csv`, help lists all commands, typo intact per waiver), `test_tracker.py` — 6/6 green, tempdir-safe.
