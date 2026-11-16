# Plan 237 -- acceptance, release 6.6.0, the two field briefs (SR27, SR28)

> Status: PLANNED. Record: [standup-2026-11-record.md](evidence/standup-2026-11-record.md).

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
