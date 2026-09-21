# Plans 063–074: the findings_25 batch → v4.9.0 (master record)

> The approved batch plan, verbatim, after a devil's-advocate review. Each numbered plan
> gets its own record before its code is written; this file is the map and the resume point.


Status: **EXECUTED 2026-09-21 and released as v4.9.0** (approved by the maintainer the same
day; per-plan status, SHAs and evidence are in the index rows and the numbered plan records). Everything here came from read-only
inspection, one read-only process probe on this Windows host, one web search, and two advisor
passes. Both repos are untouched since `dc4c5eb` (tamheed) and `9b8b4048` (ACMP).

Scope decided in the interview (unchanged): findings_25's three findings, all four
enhancement groups, a sanctioned unlock tool, v4.9.0 with lab beat 16, executed directly by me.

---

## 1. Weaknesses of the original plan

1. **The liveness model was wrong on Windows, and would have shipped a bug.** I wrote three
   outcomes (`not-running / alive / unobservable`). A probe on this host shows
   `OpenProcess` **succeeds for a process that has already exited** while any handle to it is
   held (exit code 0, not 259). "Handle opened ⇒ alive" would refuse to unlock a dead holder.
   It also showed access-denied (error 5) means *exists but cannot be inspected*, a fourth case.
2. **Wrong clock in the reuse test.** The plan compared process start time with the lock's
   `taken_at`. The sound discriminator is *recorded start ≠ observed start*, both read from the
   process API. The `taken_at` ordering test is only a weaker fallback for legacy locks.
3. **`package_unlock` could have removed a lock it merely could not see.** The plan refused only
   on `alive`. It must also refuse on `unobservable` (other host, access denied, no start time
   on the platform). Otherwise the tool guesses, which is the doctrine it claims to keep.
4. **Unlock then open could load a half-written store.** A writer that died mid-flush leaves
   `data/` unloadable. The plan had no loadability check before removing the lock, and no answer
   for a pre-v4 store that `package_open` refuses.
5. **An unverified "byte-identical fixture" claim in 065.** Removing CSVs for empty tables may
   change the lab fixture. I asserted it would not without measuring.
6. **A test I said would catch a new advisory would not.** The advisory-teaching test uses a
   hard-coded tuple of rule names. Adding a rule leaves it green while its docstring goes false.
7. **071 had no acceptance criterion.** "Adopt portable field rules" is untestable prose.
8. **070 had no false-positive gate.** A prose-id scan over a 13 MB corpus could emit hundreds of
   hits and become a permanently amber, ignored rule. No measurement step, no cap.
9. **Beat 16's dead-pid step had no recipe.** An in-process agent has no dead pid to unlock.
10. **A new capability class was filed as hygiene.** Reading another process's metadata through
    `ctypes` is a SECURITY.md doctrine addition, not a docs sweep item.
11. **Overclaim.** "Every field claim was checked against source" was false; I checked the ones
    the plan builds on. Lesson quotes from ACMP are motivation only and stay unverified.
12. **No second reviewer on destructive code, no continuity plan** for a 12-plan batch in a
    session near its context ceiling, and a flaky-test risk of exactly the kind fixed yesterday.

## 2. Assumptions — confirmed, rejected, unresolved

**Confirmed by direct inspection (not from sub-agents)**
- Stdlib `ctypes` can observe a process on this host: own pid → handle, exit code 259
  (`STILL_ACTIVE`), creation time readable; released dead pid → error 87; pid 4 → error 5.
- `PE_EVENT_TYPES` contains `forced-override`; the roster is DDL-CHECK-mirrored, so no new event
  type without a migration (`tamheed_server.py:274`).
- `packages` has `name, package_version, iteration, go_no_go` (`schema.sql:44-57`).
- `package_verify` loads lock-free and `foreign` is reported without flipping `verified`
  (`:685-700`); the eval `verify` primitive prints `foreign=` by key, so a new `foreign_csv`
  key is safe and must not be folded into `foreign`.
- Eval assertions use `gates/count/grep-*/verify` primitives only; none pins per-rule readiness
  keys, `server_info`, query or export result shapes.
- The export envelope lacks `partial` (`:834-836`); `package_migrate` takes `O_EXCL` before the
  preview; `export_html` skips empty tables with a bare `continue`; every write flushes through
  `_commit()`; `search` is an escaped substring over all TEXT columns (`:1271`).
- The emitted note's cheat-sheet lists 11 routine tools. `package_unlock` will **not** be added
  there (operator-only, not a routine tool).
- Non-lab eval fixtures' prompt copies were last touched at v4.0.0; no release refreshes them.
- Lab fixture: 25 CSVs for 27 JSONL files (the two non-entity tables), so no orphan is expected.

**Rejected**
- Tri-state liveness; "handle opened ⇒ alive"; start time compared with `taken_at` as the
  primary test; "`unobservable` may be unlocked with confirm"; "the amber-families test fails on
  a new advisory"; "`search` is fuzzy"; "approved lessons leave the note silently"; "JSONL is
  written back at `package_close`" (tamheed's own `docs/workflow.md` says so and is wrong).

**Unresolved — each has a measurement step in §5**
- Whether 065 changes the lab fixture's `csv/`.
- The false-positive rate of the prose-id scan on a real corpus.
- Whether the Linux `/proc` path and the Windows path agree in CI (only the matrix can show it).
- Whether any fixture text pins `lessons-confirmed` wording (grep before 069).

## 3. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Unlock removes a live writer's lock | Four outcomes; `confirm=true` proceeds **only** on `not-running` or `reused`; refuses on `alive` and on `unobservable`, naming what was not observed and the manual path |
| Exited-but-handle-held process read as alive | `GetExitCodeProcess != STILL_ACTIVE` ⇒ `not-running` |
| Linux start time collides across reboots | Record an absolute epoch start (`btime` + ticks/HZ), compare with a 2 s tolerance |
| `os.kill(pid, 0)` kills the process on Windows | Never called on Windows; platform branch is explicit and test-pinned |
| Unlock opens a half-written store | Lock-free load first; `loadable: false` ⇒ refuse, "reconcile via git first". Pre-v4 store ⇒ lock removed, `journaled: false` with the reason |
| Flaky tests from real pids | Observation function is injectable; branch tests use fakes. Real-process tests: own pid must be `alive`; a finished child with its handle released must be `not-running` or `reused` |
| CSV deletion removes an operator's file | Only `csv/<stem>.csv` where stem is a current table now empty, or a known retired table; anything else is reported as `unowned`, never touched |
| Prose-id advisory is noisy and ignored | Measure first on the lab fixture and on ACMP's tool-written exports; **STOP and interview if more than 5 hits per 1,000 rows are false**; entity list capped with a count; scan values not JSON keys; skip code fences, Superseded/Obsolete rows and the append-only journal |
| A new advisory flips a fixture verdict | Advisory never blocks; `python check.py evals` re-run after 069 and 070 and named in each record |
| Stock prompt edits rot | One `assertIn` needle per edit in the teaching-surface tests; `4.9.0` history key in the same commit |
| Additive result keys break a consumer | Top-level only, never per-row; export stays deterministic, no timestamp |
| Destructive code reviewed by its author only | `python-reviewer` and `security-reviewer` agents on 063, 064, 065 before commit, plus the advisor |
| Session compaction mid-batch | Every plan record is written to `plans/` **before** its code; index rows carry `IN PROGRESS`; memory updated at each milestone |
| Cross-platform failure stalls the batch | 063/064 go first; a platform whose probe fails degrades to `unobservable` rather than blocking the release |

## 4. Changes made and why

1. **Four-outcome observation with recorded start time** (`not-running`, `reused`, `alive`,
   `unobservable`). Reason: the probe and published practice.
2. **`confirm=true` refuses on `unobservable`.** Reason: §1.3. The manual removal path stays
   documented for that case.
3. **Loadability pre-check and a pre-v4 branch in `package_unlock`.** Reason: §1.4.
4. **065 moved to the end of the code plans, with a before/after `diff -rq csv/`.** Reason: §1.5;
   any fixture regeneration happens once, by tool, and is disclosed.
5. **070 edits the test tuple as well as the playbook, scans values not keys, and gains a
   measured false-positive gate.** Reason: §1.6, §1.8.
6. **071 lists its needles.** Reason: §1.7.
7. **073 carries the dead-pid recipe** (a child process writes the lock with its own pid and
   start, then exits). Reason: §1.9.
8. **SECURITY.md gets a doctrine sentence**: the server reads process metadata for lock
   observation, spawns nothing, signals nothing. Reason: §1.10.
9. **Second reviewers, plan-records-first, injectable observation.** Reason: §1.12.
10. **Wording**: "retires ACMP's family map" became "makes it unnecessary if they adopt it".

**Researched findings (separate from my reasoning).** Projects that hit PID-reuse lock bugs
converge on one remedy: record the holder's process start time beside the pid, compare on
check, and degrade to conservative refusal where the platform cannot observe it, never to
"assume dead". Cleanup should remove only the exact stale file and stop for a human when any
validation fails. Sources:
[withastro/astro PR 17671](https://github.com/withastro/astro/pull/17671),
[OpenViking issue 4210](https://github.com/volcengine/OpenViking/issues/4210),
[Wingman issue 293](https://github.com/vedantnimbarte/Wingman/issues/293),
[jcodemunch-mcp issue 728](https://github.com/jgravelle/jcodemunch-mcp/issues/728),
[hunch PR 351](https://github.com/davesheffer/hunch/pull/351),
[QLockFile](https://stuff.mit.edu/afs/athena.mit.edu/software/texmaker_v5.0.2/qt57/doc/qtcore/qlockfile.html).
I used one targeted search rather than a full deep-research run, because the question was
narrow and the local probe answered the platform-specific half directly.

## 5. Refined execution plan

Constraints for every plan: stdlib only, no subprocess in the engine, no schema migration,
additive top-level result keys, bundle never links out, no `plugin.json` bump until 074,
CHANGELOG under `[Unreleased]`, goldens regenerated by tool only. Stock prompts may change only
in 070 and 071, each with its `4.9.0` key in `stock-history.json` in the same commit.

Per-plan loop: write the plan record → RED test → GREEN → `python check.py` → reviewers (where
listed) → advisor → commit → push → CI 9/9. Status update at least every three minutes.

| # | Plan | Validation point → expected output |
|---|---|---|
| 063 | Lock records `started`; `store.observe_lock()` four outcomes; every refusal reports it; `package_migrate` preview lock-free (`O_EXCL` only under `confirm`) | Fake-driven tests for all four outcomes + legacy bare-pid lock + other host; real own-pid = `alive`; preview under a held lock returns a report; `confirm=true` still refused. CI green on Ubuntu **and** Windows |
| 064 | `package_unlock(name, confirm=false)`; refusal texts name it; journals `forced-override` | Report mode writes nothing (`git status` clean); `alive` and `unobservable` refused; dead holder → lock gone, one journal row, `package_verify` verified, nothing left open; unloadable store refused; `--selftest` prints 19/19 |
| 066 | `server_info` `package` block; `detail=true` adds `entity_types`, `relation_rules` | Stored name readable with a package open; default payload unchanged otherwise |
| 067 | Export envelope carries `count/total/partial`; `package_verify(expect=)` → `matches_expected` | Two exports of one state byte-identical; short export shows `partial: true` in the file |
| 068 | `entity_query` → `omitted_columns`, `matched`; lesson approve/pin → `next` hint | Keys are siblings of `rows`; row dicts unchanged (asserted) |
| 069 | `population` on every readiness rule; `lessons-confirmed` `indeterminate` at zero lessons | Grep fixtures for pinned wording first; `python check.py evals` green; `ready` unchanged on all three fixtures |
| 070 | `prose-ids-resolve` advisory; playbook + the test tuple + `4.9.0` key | **Measure first**: hits on the lab fixture must be 0 or each explained; false-positive rate on ACMP's exports under the §3 threshold, else STOP |
| 071 | Stock prompts adopt field rules | Needles: "show the record with its id", "ask every time", "every gate is row-level", "which words of the trigger", "search finds candidates", `package_unlock` in `orient-resume.md`. Lint 9 and 9b green |
| 065 | `csv/` equals what `export_html` emits; `package_verify.foreign_csv` | `diff -rq csv/` on a scratch re-export before and after; an operator's `notes.csv` survives and is reported |
| 072 | Docs and diagrams sweep after code lands | `docs/workflow.md` write-back arrow moved to every write; new lock-lifecycle diagram in `docs/architecture.md`; install guide gains the dead-holder branch and "restart or `/reload-plugins`"; server README 19 tools; SKILL; SECURITY doctrine sentence; flush contract stated once; `git grep` finds no surviving "never guesses / remove the stale lock deliberately" line |
| — | Acceptance pass | Scratch black-box script, one section per plan, **each check first shown to fail on `dc4c5eb`**; `python check.py`; `--selftest`; `PYTHONWARNINGS=error::DeprecationWarning` run |
| 073 | Lab beat 16, agent-driven in-process (the beat-14/15 procedure) | Beats incl. the child-process dead-pid unlock, own-pid unlock refused, preview under lock, a planted dangling id caught then resolved, `population`, `omitted_columns`, `matched`, export `partial`, `expect=`, emptied-table CSV removed, `detail=true`, `refresh_stock` to 4.9.0. New `evals.json` assertions; verbatim report under `plans/evidence/` |
| 074 | Release v4.9.0 (plan-058 recipe) | Lints 4, 5, 8, 9 green; annotated tag; CI green on the tagged commit; memory updated |

**Recorded, not built** (index, one reason line each): patch/append and implicit `if_match` on
upserts; column-fidelity profiling; stale-derived-artifact flag; `acs-met` respecting Deferred;
`diverged_customized` without an emit; multi-family atomic export; note-budget policy;
claim-versus-store checks on prose and commit messages.

**Relay to ACMP in the final report:** stamp closed findings_12 §D.3, findings_19 §3, the
`_next_id` note and the root-vs-package `handoff_emit` contradiction; 62 pinned against 37
rendered lines is Promoted lessons leaving the note by design; their PowerShell lock snippet
still parses the legacy bare-pid format.

## 6. Approval checkpoint

Nothing has been executed. Approving authorizes plans 063–074 as written above, with commits,
pushes and the `v4.9.0` tag on `main` under the standing git delegation. By approving you are
explicitly agreeing to these points, which are the ones that change tamheed's behavior or doctrine:

1. **The unlock rule.** `package_unlock(confirm=true)` removes a lock only when the holder is
   observed `not-running` or `reused`. It refuses on `alive` and on `unobservable` (another
   host, access denied, a platform that cannot report start time). Manual removal stays the
   documented path for those cases.
2. **The doctrine flip.** "The store never removes a lock" becomes "the store observes, reports,
   and removes a lock only on the operator's word through one journaled tool."
3. **A new capability in SECURITY.md.** The server reads process metadata through `ctypes` and
   `/proc`. It still spawns nothing and signals nothing.
4. **`export_html` deletes files**, limited to `csv/` entries for empty or retired tables.
5. **A new advisory on every package** (`prose-ids-resolve`), gated on a measured
   false-positive rate, with a STOP and an interview if it is too noisy.
6. **Stock prompts change** in 070 and 071, so ACMP's two customised prompts will lag again.
7. **MINOR release v4.9.0** with lab beat 16.

Approve as written, or tell me which of the seven to change.
