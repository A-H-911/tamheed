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

## The brief rehearsals (`scripts-263/rehearse_690.py`, 5.62 USD)

Each field's brief ran headless on a scratch copy, under a scripted operator: the restart path (a
6.8.0 session, then a 6.9.0 session) and the updated-first path (a 6.9.0 session with no PRE file).

| Run | Cost | Result |
|---|---|---|
| ACMP, 6.8.0 turn | 0.58 USD | PRE written, stopped at the restart, nothing committed |
| ACMP, 6.9.0 turn | 1.05 USD | five classes held. Two commits: the guide and the review page, then FB-034 to FB-037 Resolved |
| ACMP, updated first | 1.13 USD | PRE from the update time, marked `updated first`. Five classes held, two commits |
| Jisr, 6.8.0 turn | 0.58 USD | PRE written, stopped at the restart, nothing committed |
| Jisr, 6.9.0 turn | 1.05 USD | five classes held. Two commits, the seven rows Resolved |
| Jisr, updated first | 1.23 USD | PRE from the update time, marked `updated first`. Five classes held, two commits |

The round's agent runs cost 8.86 USD of the 10 USD cap (3.24 for the lab runs of plan 262).

The rehearsals corrected the briefs before publication:

- Jisr's seven rows are `Reported` on `f0d6f636`, not `Confirmed`. The brief says so.
- The review page was exported before the rows were written, so it lagged the store. Both briefs
  now export it again after the rows and commit it with them.
- Both briefs now end the session with a `handoff` entry.

Not measured by the rehearsals: the plugin record. The scratch copies load the plugin from a local
folder, so `claude plugin list --json` holds no record for them, and the update time came from the
scripted operator. A local folder also writes `.mcp.json`, which both briefs say to remove.

## The security review before the tag (plan 263b)

`ecc:security-reviewer` reviewed plans 258-261 on main (`bfa58cb`). It found one MEDIUM and four LOW
issues. The operator ruled to fix all five before the tag:

| # | Finding | Fix |
|---|---|---|
| F1 | MEDIUM: a `merge_attributes` patch nested about 900 levels raised out of the tool and left the batch open | the depth bound runs before the recursive key check |
| F2 | LOW: a declaration refused a write that retires a row as it is | such a write is not judged, as for a register entry |
| F3 | LOW: a declaration had no depth bound, and it kept extra keys | the depth bound, and only `fields` is stored |
| F4 | LOW: stored values were echoed in full | cut at 120 characters |
| F5 | LOW, from before 6.9.0: `System:` passed the check of the engine's namespace | the check ignores case and spaces |

The maintainer's own pass of plan 260 had said that the patch's recursion was caught. That held for
two of the three functions, not for the key check.
