# Integrity check — is the package trustworthy right now?

Paste this to audit the `package` package without changing anything.

---

Run a read-only integrity check on the `package` Tamheed package:

1. `package_open("package")`, then `gate_run()` — every Critical gate must pass
   (G-REL now FAILS on stored trace edges violating the endpoint rules, no longer
   advisory; `relates_to` is the escape hatch); treat a G-TRACE "passed vacuously"
   warning as a finding, not a pass.
2. Spot-check counts: `entity_query("requirement", limit=1)` and read `total`;
   compare `total` per family against expectations from the roadmap/charter.
3. `trace_query` a sample of MVP requirements — each should reach a decision,
   a work item, and a test; note any that only reach one bucket.
4. Audit honesty: from `gate_run`'s audit_evidence split, list every NARRATED
   verdict (no evidence) — each is the graded party grading itself.
5. Check staleness: compare the freshness line in a fresh `export_html()` against
   `git log -1` — if git is ahead of the package's recorded activity, the package
   is stale; recommend a progress sync.
6. **Cross-check git against the bindings**: `git log --oneline -15` vs the recorded
   `work_bind` refs — list package-relevant commits with no recorded binding (drift;
   recommend the drift-register prompt). Do NOT invent records for them.
7. `readiness_check("package")` — report the blocking/advisory findings as data
   (this run resolves nothing).
8. **Verify any recent repair**: if rows were repaired since the last check (a
   scale recovery, a title restore), re-read the affected `data/*.jsonl` and
   re-derive each expected value independently from its source (the stash, the
   backup) — a repair whose only check is the hand that typed it is unverified.
   Report mismatches as findings; fix nothing in this run.
9. Report: gate verdict, count anomalies, trace gaps, narrated verdicts, staleness,
   unbound commits, readiness blockers, repair-verification mismatches — then
   `package_close()`. Change NOTHING in this run.
