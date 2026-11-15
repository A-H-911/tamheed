# Plan 231 -- acceptance, release 6.5.1, the two field prompts (R116, R117)

> Status: PLANNED 2026-11-15. Cycle: field patch 2026-11, branch `fix/6.5.1`. The record is
> [field-patch-2026-11-record.md](evidence/field-patch-2026-11-record.md).

- **Assurance on copies of both field packages.** The scripts of plan 229 are copied to
  `plans/evidence/scripts-231/assure/`, and each label is read from the bundle's manifest.
  A migration under 6.5.0 and one under 6.5.1 from the same start differ in one field of one
  row. 6.5.1 opens a store that 6.5.0 migrated, with no file moved. 6.5.0 opens a store that
  6.5.1 wrote. The journal file is held, then a later file, on both copies.
- **The stamp.** `stamp_651.py` after `stamp_650.py`: the version on the six surfaces of lint 8,
  the CHANGELOG entry, the stock guide with its history key, the eval pins. The lab fixture
  follows through the engine's own tools (`refresh_lab_651.py`).
- **The briefs.** `plans/briefs/acmp-6.5.1.md`: the plugin alone, no migration. It names the
  seven rows and the optional note (R117). `plans/briefs/jisr-6.5.1.md`: the 6.5.0 brief,
  changed line by line. The facts about the installed release move to 6.5.1. The release
  that carried each fix stays 6.5.0. `jisr-6.5.0.md` says in its first line that it is
  superseded.
- **Rehearsals.** A headless agent runs each brief through the served plugin on a scratch
  repository. Every surprise that it reports goes to the operator before the release question.
- **After the tag.** The plugin going back from 6.5.1 to 6.5.0 is measured in a separate
  configuration folder. No brief quotes an answer for that direction before then.
- **Check:** the gate on both Python versions, CI on eleven jobs, the acceptance script.
  **Expected:** tag `v6.5.1` on a green commit, and two prompts handed to the operator.
