# Plan 137: the residue — thirteen sentences from twelve partial rules, and E3's wording

> Maintainer-executed, 2026-09-27. Batch map: [136-140-batch-findings-34.md](136-140-batch-findings-34.md).
> Field source: ACMP `findings_34.md` B0 (the re-read classification: 26 partial rules with verified
> quotes) and its E3/E6; ruling R18 (absorb all twelve generic remainders).

## Status

- **Priority**: P1 - **Effort**: S - **Risk**: LOW - **DONE**

## What the field showed

ACMP's re-read of the 113 carried rules against the eight 5.2.0 discipline skills (95 quotes verified
byte-for-byte) found 26 partial rules. Twelve of them carry a remainder that is generic — no project
id, no stack — and that no skill stated (verified here by grep over all eight files before writing).
Every remainder was re-read at the rule's own text in ACMP's memory file, never from the classifier's
summary.

## What entered which skill (one sentence each; lint 12 green after every file)

| Rule (anchor) | Remainder | Skill, place |
|---|---|---|
| TECH-2 1914 | a cwd-relative scanner path reports clean over zero files; resolve from the script, run as the pipeline runs it | `measurement-evidence` §2 |
| CI-3 1860 (script half; ACMP miss 3; this session's own inline-script mangling) | a script passed inline through a shell is rewritten; write the file, run the file | `measurement-evidence` §2 |
| PROSE-1 1352 | a count of what an instrument DID is not a count of what it FOUND | `measurement-evidence` §3 |
| PROSE-3 1128 | an instrument measures the quantity it counts; a different quantity needs a different command | `measurement-evidence` §3 |
| PKG-2 1542 | a substring proxy removes rows that name without covering; its output is triage | `measurement-evidence` §3 |
| TECH-2 856 / 2649 | read the store through the tools; a regex over a JSON-lines row deletes rows | `reading-the-record` step 2 |
| CI-2 1886 | a watch command reports success on an unfinished run; poll to completed; a transport failure is unknown | `ci-evidence` step 1 |
| CI-3 475 | judge what a queue's green exercised per item; each dependency update on its own evidence | `ci-evidence` step 4 |
| CI-3 1860 (message half) | a multi-line message reaches a command only from a file; a flag inside a quoted message can be read as the command's own | `package-writes` §7 |
| PKG-1 101 | an advisory failure is normal; a blocking failure is a real finding; never soften a defect to clear it | `package-writes` §11 |
| PKG-1 1560 | a due-date liveness field going red is the control working; never clear a date to restore the amber | `package-writes` §11 |
| TECH-3 2453 | a migration's verdict comes from executing, never from building | `test-evidence` §5 |
| OPS-1 516 | for a non-destructive act a prompt-by-design and a forbidden act look identical; try it, let the operator answer; never generalise one refusal | `operator-interview` "What you cannot see" |

Not absorbed (project-only after reading): PROSE-1 2154, PROSE-2 2860, PROSE-3 511, PKG-3 3201,
OPS-1 2734, CI-2 2892, PKG-1 89 (its kickoff checklist is package-writes §3's tool), PKG-1 1936,
TECH-1 1679/1646, TECH-2 1028, TECH-3 2223/2265 — and the 34 project rules.

## E3 (docs only)

`server/README.md`: `entity_query`'s cue rides every SUCCESSFUL result (`count: 0` included); a usage
error carries none. The engine is unchanged: "no such record" is an empty success, which is where the
cue matters; an error return is the caller's misuse.

## Validation

`python check.py lint` after every file; `python check.py` green (ALL CHECKS PASSED) before the commit.
Skill sizes after: measurement-evidence 180, reading-the-record 144, ci-evidence 121, package-writes
219, test-evidence 136, operator-interview 144 lines — all under lint 12's 500.
