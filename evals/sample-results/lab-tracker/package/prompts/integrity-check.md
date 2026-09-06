# Integrity check — is the package trustworthy right now?

Paste this to audit the `package` package without changing anything.

---

Run a read-only integrity check on the `package` Tamheed package:

1. `package_open("package")`, then `package_verify()` — the canonical round-trip
   of the on-disk store: `verified` must be true with `dirty: []` (a named file is a
   non-canonical hand edit or a damaged row), `loadable` true (a false one carries
   the file:line of the damage), `memory_matches_disk` true, and `foreign: []` (a
   file the engine does not own sitting in `data/`). Note the `digest` — it is the
   citable fingerprint of this state (`record=true` journals it, on the operator's
   words only). Then `gate_run()` — every Critical gate must pass (G-REL FAILS on
   stored trace edges violating the endpoint rules; the remedy is a retype in ONE
   `entity_upsert` batch — `retire: true` on the wrong triple + the correct relation,
   `relates_to` only when nothing typed fits — recommend it, do not apply it here);
   treat a G-TRACE "passed vacuously" warning as a finding, not a pass. Report any
   pair carrying BOTH a typed relation and `relates_to` as residue to retire.
2. Spot-check counts: `entity_query("requirement", limit=1)` and read `total`;
   compare `total` per family against expectations from the roadmap/charter. Read
   registers THROUGH the tool: page with `after_id` (the result's `next_after`),
   quote known rows via `ids=[...]`, sweep by keyword via `search=` — never through
   `data/*.jsonl` to dodge a payload cap. Calibrate every keyword sweep with a
   positive control chosen from OUTSIDE the set you are sweeping for — a control
   from inside it proves only that the scan reached the corpus, not that your
   pattern matches the corpus's spelling of the thing you want.
3. `trace_query` a sample of MVP requirements — each should reach a decision,
   a work item, and a test; note any that only reach one bucket.
4. Audit honesty: `gate_run`'s `audit_evidence` reads each ACTIVE AC's LATEST verdict
   (superseded verdicts are history): `narrated_ids` names the graded verdicts with
   no evidence — each is the graded party grading itself; `ungraded_ids` names the
   Pending placeholders nobody has graded — a different, lesser finding. Read both
   sets via `entity_query("audit-verdict", ids=[...])`; older placeholders buried
   under a later verdict surface with `search="Pending"`. Sweep for rulings hiding in CLOSED
   rows too (`entity_query("defect", status="Fixed", search="operator")` and the
   closed `deferred-work` rows): a decision recorded inside a closed defect is
   invisible to every decision-register sweep — report each as a missing `DEC-`.
5. Check staleness: compare the freshness line in a fresh `export_html()` against
   `git log -1` — if git is ahead of the package's recorded activity, the package
   is stale; recommend a progress sync.
6. **Cross-check git against the bindings**: `git log --oneline -15` vs the recorded
   `work_bind` refs — list package-relevant commits with no recorded binding (drift;
   recommend the drift-register prompt). Do NOT invent records for them.
7. `readiness_check("package")` — report the blocking/advisory findings as data
   (this run resolves nothing).
8. **Verify any recent repair**: if rows were repaired since the last check (a
   scale recovery, a title restore), re-read the affected rows in full
   (`entity_query(<type>, ids=[...])` — the tool truncates no field) and re-derive
   each expected value independently from its source (the stash, the backup) — a
   repair whose only check is the hand that typed it is unverified. Report
   mismatches as findings; fix nothing in this run.
9. Report: verify verdict (+ digest), gate verdict, count anomalies, trace gaps and
   edge residue, narrated and ungraded verdicts, buried rulings, staleness, unbound
   commits, readiness blockers, repair-verification mismatches — then
   `package_close()`. Change NOTHING in this run.
