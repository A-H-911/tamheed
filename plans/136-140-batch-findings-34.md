# Tamheed v5.3.0 — the findings_34 batch: no defect, two instruments, one hint, the residue

Status: **IN PROGRESS 2026-09-27** — index section "Field cycle findings_34" in [README.md](README.md).
Commits: 136 `b8e1f7c`, 137 `dbd81e1`, 138 (this record's first commit), 139, 140 = the close-out
commit that carries this record (EXECUTED), the brief and the index — the tag sits on it. Execution
order 136 → 137 → 138 → 139 → 140 (136/137 have no dependency; 138 needs both; 139 needs 138; 140 all).

Read-only evidence this record rests on: ACMP `findings_34.md` (`9a801428` → `e88b051b`), the rows
`FB-023`–`FB-025` (Resolved 5.2.0), `LL-099`–`LL-111` (Approved 2026-09-27, none pinned), the journal
`PE-1474`..`PE-1500`, the two hook captures (`resume-hook-2026-09-27.txt`, `compact-hook-0.txt`), the
classification `classify-all.json` (113 rules, 95 quotes verified by the field), the 17 candidate rule
blocks re-read in `.claude/memory/prm-next-carried-rules.md`, the ACMP session's own plan; the engine at
every line cited in the approved plan (`~/.claude/plans/pasted-content-id-79cf-acmp-updated-dazzling-
kettle.md`, the design + interview record, revised after a devil's-advocate review); the Claude Code
docs (`plugins/cli-reference`, the CHANGELOG — fetched and grepped 2026-09-27); the interview rulings
R15–R18.

## 0. Measurements (the plan's §5.1)

| # | Measurement | Result |
|---|---|---|
| M1 | `store.observe_lock` over a lock naming a dead pid, on this Windows host | `not-running` in < 6 ms (pid 4,000,000: 5.8 ms; pid 2^31: 0.2 ms); an out-of-range pid (2^33) → `unobservable`, no exception; the System pid → `unobservable` (access denied) |
| M2 | ACMP replay on the final bundle (plan 139) | — (recorded when run) |

## 1. What the field returned (no defect)

P0–P6, P8, P9 held; P7 and P10 legitimately not exercised; `FB-023`–`025` Resolved; the thirteen carried
lessons Approved after 39 verified trims; `95841b0d`/`30a33887` bound; the compact hook delivered
`PE-1498` byte-identical. Seven brief errors (E1–E7), one contested docs claim (the hook on a plugin
reload: delivered once on 5.1.0, not delivered twice on 5.2.0, delivered on every restart and
compaction), one friction (a dead lock holder the block named but did not observe), the generic
residue of 26 partial carried rules, and a Q1 that could not discriminate (the brief had announced the
cues).

## 2. Rulings (R15–R18, binding)

| # | Ruling |
|---|---|
| R15 | v5.3.0, MINOR; no migration (`schema_version` 7). |
| R16 | The resume block carries `lock.observed` + `lock.evidence` through the plan-064 seam; the hook prints it; a lock held by this session reads `alive` with no probe. |
| R17 | An opt-in hook trace: `TAMHEED_HOOK_LOG` naming an EXISTING file gets one counts-only line per run. |
| R18 | All twelve generic remainders of the partial rules enter the skills, one sentence each. |

## 3. Execution

| # | Plan | Status |
|---|---|---|
| 136 | [The observed lock, the render hint, the hook trace](136-observed-lock-render-hint-hook-log.md) | DONE `b8e1f7c` |
| 137 | [The residue: thirteen sentences, and E3](137-residue-sentences-and-e3.md) | DONE `dbd81e1` |
| 138 | [Docs + diagrams sweep](138-docs-and-diagrams-sweep-findings-34.md) | DONE |
| 139 | [The version stamp, then lab beat 25 + evals](139-stamp-then-lab-beat-25.md) | PLANNED |
| 140 | [Tag v5.3.0, the brief file, close-out](140-release-v530.md) | PLANNED |

## 4. The 5.2.0 brief's errors, owned (E1–E7)

E1 "nothing to do" on files the rulings falsified (four live sentences); E2 "binds and renders" (the
note renders pinned + the 10 newest unpinned); E3 "every result" (error returns carry no cue); E4 "21
lines" (a count from my copy; the field read 19 — unexplained, and the brief now carries no counts);
E5 P4 omitted `diverged_stale_stock`; E6 "one partial" (two); E7 the classifier's 36 covered / 33
project-specific (re-read: 11 / 26 / 32 — the brief warned; the field measured the warning).

Execution notes (owned as they land): (1) plan 136's contract tests first re-created a package the
class's setUp had already opened, and promoted a lesson without a skill row — both the test's
mistakes, fixed at the test; (2) plan 138's sweep failed once as a shell heredoc ("unexpected EOF")
and ran from a file written by the editor — the very rule plan 137 had just written into
`measurement-evidence` §2.
