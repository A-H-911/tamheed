# Plan 237 -- acceptance, release 6.6.0, the two field briefs (SR27, SR28)

> Status: DONE 2026-11-16. Released as `b08c19c` on `main` (CI run 43850413052 green on eleven jobs), tag `v6.6.0`. Record: [standup-2026-11-record.md](evidence/standup-2026-11-record.md).

- **Headless rehearsal** (`plans/evidence/scripts-237/`) on a scratch lab copy, the operator's
  answers scripted and said to be scripted: a first report recorded; a driver adds work (a
  journal entry, a task to Review, a Met and a Not-met verdict, a bind, a defect, a reworded
  requirement); a second report; its correction; an override from the first report's date; a
  third daily report.
- **The checker:** the chain and the statuses; the replay equals every digest; the third base is
  the correction, not the override; the reworded requirement is listed as edited; no
  `transition` rows and no handoff count moved; every page at most 2,000 visible words (the
  first exempt), the content policy, no script, no operator words; at most 3 draft calls per
  report; `package_verify` passes; an idle close leaves zero diff.
- **Release:** the fixture refresh (registry-sync and one report), the 6.6.0 stamp (plugin.json,
  CHANGELOG, the lint-8 surfaces, `index.html`), the ACMP and Jisr-dev briefs (update, then
  `package_migrate` preview and confirm, then the first `/tamheed:standup`), each rehearsed
  headless on a scratch clone; the index rows; CI green on every job.
- **Expected:** the rehearsal and the checker green; both briefs pass on their clones; no tag
  until the operator says go.

## As built so far (2026-11-16)

- **The rehearsal** with a real headless agent: five reports (a first, a daily, a correction, an
  override, a third daily), the checker green, 3.20 USD. The record:
  [standup-rehearsal-237.md](evidence/standup-rehearsal-237.md).
- **The stamp** (`scripts-237/stamp_660.py`): 6.6.0 on every lint-8 surface, the CHANGELOG
  entry (MINOR, with the field route: update, `package_migrate` preview and confirm, then
  `handoff_emit(refresh_stock=true)` and `export_html()`), the stock guide's body under 6.6.0,
  the eval pins.
- **The lab fixture** (`scripts-237/refresh_lab_660.py`): a registry-sync taught it the
  `standup-report` family and also the two register families of 6.5.0, which its 6.5.0 refresh
  had not added. It verifies clean under 6.6.0 and reads ready.
- **Check:** `check.py` on 3.13 and 3.10 and with deprecations as errors; the selftest 22/22.
- **The way back** to 6.5.1, measured on both field copies, found that the record's journal note
  named the report as a foreign-key subject, so 6.5.1 could not load the store. Fixed in
  `b08c19c`: the note names the report in its attributes only.
- **The briefs** `plans/briefs/acmp-6.6.0.md` and `jisr-6.6.0.md`, measured and rehearsed by a
  headless agent: every class held. The record is
  [standup-rehearsal-237.md](evidence/standup-rehearsal-237.md).
- **Release:** CI on the branch (run 43849737555, after a run that stayed queued) and on `main`
  (run 43850413052) green on eleven jobs; `main` fast-forwarded to `b08c19c`; tag `v6.6.0` on
  the operator's go, given before the CI.
