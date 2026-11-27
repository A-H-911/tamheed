# Plan 263: the field replays and the way back, measured (2026-11-27)

Scratch copies only: ACMP's committed tree at `812c01c9` (`git archive`, because its `data/.lock`
is live) and Jisr's branch tip `f0d6f636` (`feature/sl-008-workshops`, a GitHub tarball read with
`gh api`, two commits after the feedback commit `aafc7dd`). The originals were never opened. The
bundles: `git archive v6.8.0` and the stamped 6.9.0 tree. Scripts: `scripts-263/measure_263.py`
and `scripts-263/wayback_263.py`. Counts and names only.

## The replays

| Probe | ACMP 6.8.0 | ACMP 6.9.0 | Jisr 6.8.0 | Jisr 6.9.0 |
|---|---|---|---|---|
| open | ok | ok | ok | ok |
| files moved by the open | none | none | none | none |
| `gate_run` ready | true | true | false | false |
| `readiness_check` ready | true | true | false | false |
| blocking rules that fail | none | none | acs-met, adrs-approved, risks-discharged | the same three |
| package rules | 29 | 29 | 31 | 31 |
| `risks-discharged` | pass, 0 listed | pass, 0 listed | fail, 18 listed | fail, 18 listed, candidate RISK-013 (AC-004, latest Met) |
| `declared-attributes` | absent | absent (nothing declared) | absent | absent |
| slates read (of the slates with a record) | none | none | 14 of 15 | 14 of 15 |
| questions put again | — | — | 0 | 0 |
| stock guide on emit | refreshed | refreshed | unchanged (already 6.8.0) | refreshed |
| `package_verify` after emit and export | verified, clean | verified, clean | verified, clean | verified, clean |

The one slate not read has no answers file (`poc-points-sample`): the same under both bundles.
The changed rows that some Jisr slates report are rows that changed after their export, the same
under both bundles.

## The way back to 6.8.0

A package written by 6.9.0 (a family's declaration, a row changed by `merge_attributes`, a slate
with `show_recommendations`, a slate with a detail of 17,114 characters, each answered), then
opened by 6.8.0:

| Step under 6.8.0 | Outcome |
|---|---|
| `package_open` | ok |
| `package_verify` | verified, clean |
| read of the merged row | its `custom_attributes` as merged |
| a write of a value outside the declared set | accepted: 6.8.0 does not read a declaration |
| `slate_read` of the keyed slate | refused: "the slate has unknown key(s) ['show_recommendations']" |
| `slate_read` of the long slate | refused: "`detail` holds 17114 characters (the cap is 8000)" |
| `slate_export` of the long slate | refused, with the same cap |
| `package_verify` after the 6.8.0 write | verified, clean |

So the plugin goes back alone. A slate that uses a 6.9.0 key or a text over 8000 characters stays
6.9.0's. A declaration is ignored by 6.8.0, and 6.9.0's advisory lists any row that 6.8.0 wrote
outside the set.
