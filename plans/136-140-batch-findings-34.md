# Tamheed v5.3.0 — the findings_34 batch: no defect, two instruments, one hint, the residue

Status: **EXECUTED — v5.3.0 tagged on the release commit (this record's commit; CI green),
2026-09-27** — index section "Field cycle findings_34" in [README.md](README.md). Commits: 136
`b8e1f7c`, 137 `dbd81e1`, 138 `5b9d2ec`, 139 `87bdb1d`; 140 = the close-out commit that carries this
record, the brief and the index — the tag sits on it. Execution order 136 → 137 → 138 → 139 → 140
(136/137 have no dependency; 138 needs both; 139 needs 138; 140 all).

Read-only evidence this record rests on: ACMP `findings_34.md` (`9a801428` → `e88b051b`), the rows
`FB-023`–`FB-025` (Resolved 5.2.0), `LL-099`–`LL-111` (Approved 2026-09-27, none pinned), the journal
`PE-1474`..`PE-1500`, the two hook captures (`resume-hook-2026-09-27.txt`, `compact-hook-0.txt`), the
classification `classify-all.json` (113 rules, 95 quotes verified by the field), the 17 candidate rule
blocks re-read in `.claude/memory/prm-next-carried-rules.md`, the ACMP session's own plan; the engine at
every line cited in the approved plan (`~/.claude/plans/pasted-content-id-79cf-acmp-updated-dazzling-
kettle.md`, the design + interview record, revised after a devil's-advocate review); the Claude Code
docs (`plugins/cli-reference`, the CHANGELOG — fetched and grepped 2026-09-27; four GitHub issues on
the reload route's context handling, adjacent reports); the interview rulings R15–R18.

## 0. Measurements (the plan's §5.1)

| # | Measurement | Result |
|---|---|---|
| M1 | `store.observe_lock` over a lock naming a dead pid, on this Windows host | `not-running` in < 6 ms (pid 4,000,000: 5.8 ms; pid 2^31: 0.2 ms); an out-of-range pid (2^33) → `unobservable`, no exception; the System pid → `unobservable` (access denied) |
| M2 | ACMP replay on the final bundle over a read-only copy at `e88b051b` (`acmp_replay2.py`) | every 5.2 class held: `resume` `PE-1498` / behind 0 / `open_feedback []`; `handoff_emit` every scan empty, no `skill`, root unchanged, `diverged_stale_stock` README 5.2.0 (the copy rebuilt the note once — the copy artefact of last cycle); `handoff-current` pass (364), `lessons-stranded` pass (75 promoted lessons), `lessons-confirmed` and `feedback-unanswered` pass; `entity_query` keys `count, next_after, ok, rows, skill, total`; the FB-023 replay 38/62 `{4.2.1: 2, 4.5.0: 18, 4.6.0: 18}`. **New:** `package_open` → `lock.observed alive`, `held by this session`; the hook after a compaction printed `PE-1498` whole (17 lines, 2,563 chars, no marker) and the trace wrote `source=compact lines=17 chars=2563 status=printed` with none of the entry's text; a lock naming the field's own dead pid 48276 → `holder observed not-running — package_unlock(confirm=true) on the operator's word`, the lock file untouched |
| M3 | Lab beat 25 (plan 139) | every class held on the second run (the first run's phase B lacked the pointer emit that writes the note the hook reads — owned in plan 139); evidence `evidence/lab-continuation-report-139-2026-09-27.md` |
| M4 | `uv run … --selftest` on the final bundle | `mcp sdk: ok (1.28.1) — 19/19 tools registered` |

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
| 138 | [Docs + diagrams sweep](138-docs-and-diagrams-sweep-findings-34.md) | DONE `5b9d2ec` |
| 139 | [The version stamp, then lab beat 25 + evals](139-stamp-then-lab-beat-25.md) | DONE `87bdb1d` |
| 140 | [Tag v5.3.0, the brief file, close-out](140-release-v530.md) | DONE — the release commit; tag `v5.3.0` |

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
`measurement-evidence` §2; an inline `python -c` was mangled twice more in this session; (3) plan 139's
first run stopped in phase B (no pointer emit before the hook) after phase A had written the fixture —
restored from git and re-run whole; (4) the advisor's review of the brief and this record BEFORE the
close-out commit (plan 140 step 2) found the render hint's `pinned` fallback UNTESTED (the test had
wrapped it in `if flip["ok"]`) and, once tested deterministically, WRONG: the write's pre-image
selects only the sent columns, so a partial row that omits `pinned` read as unpinned. The hint now
reads the stored value directly; the test sends a partial approval of a pinned row and asserts
`pinned rows always render`. Fixed in the close-out commit, before the tag — the reason the review
moved ahead of the commit this cycle; (5) the same review added the trace's CONTROL to the brief and
`install.md` (read the reload's "no line" only after a compaction has written one) and made the
brief's trim count explicit (thirteen index lines for twelve rules; `CI-3 1860` trim-or-keep).
