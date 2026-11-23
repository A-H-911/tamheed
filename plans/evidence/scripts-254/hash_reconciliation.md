# Plan 254: hash tables, checked 2026-11-23 (after the second interview)

`sha256sum -c` on every table:

| Table | Written | Result |
|---|---|---|
| `freeze_254.sha256` (v2.2, `cd014dc1`) | 04:27:43Z | all OK except `watch_254.py` |
| `analyze_254.sha256` | 04:28:30Z, before any v2.2 row | OK |
| `ab_freeze_v3.sha256` | 17:48:46Z, before scored v3 sessions | OK except `ab_254.py` |
| `ab_freeze_v4.sha256` | 18:25:04Z, before the v4 pilot | current |
| `posthoc.sha256` | after the results (post hoc by label) | OK |

**The two mismatches, both explained:**
- `watch_254.py`: changed after v2.2 only to move the snapshots, which list file names in the operator's home,
  out of the repository (`G254_SNAPS`, default a private folder). An instrument path, not a rule.
- `ab_254.py`: changed after v3 for v4 (post hoc, critic Y1): skills on with `Skill` allowed, transcripts to a
  private folder, Graphify calls counted by command name. The v3 results were scored by the v3 version
  (`results/ab.summary.json`).

`freeze_254.md` briefly failed too: a note about the A/B tasks had been appended after the hash. The note now
lives in `freeze_254_v3.md`, and `freeze_254.md` again matches its v2.2 hash byte for byte.

**Scrubbed before the commit (operator's word, 2026-11-23):** paths naming the operator's Windows user folder were
replaced in `readers/X2.report.txt` and `results/testA.v21-discarded.log` (with `<user>`), and `meter_254.py`,
`handback_254.py` and `watch_254.py` now derive their folders instead of naming them. These edits change those
files' hashes against `freeze_254.sha256` (v2.2); no rule, input or result changed. `readers/S1.meter.json` was
re-written by the check that the meter still finds its transcripts (same numbers).
