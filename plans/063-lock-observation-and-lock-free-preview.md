# Plan 063: The lock can be observed, and the migrate preview runs without it

> Reviewer-executed (maintainer-delegated), 2026-09-21. Part of the findings_25 batch; the
> approved batch plan is [063-074-batch-findings-25.md](063-074-batch-findings-25.md).

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (cross-platform process observation)
- **Depends on**: none - **Category**: operability (findings_25 s1)
- **Planned at**: commit `d21ec99`

## Why this matters

findings_25 s1: after an upgrade the holder of `data/.lock` is already dead, the guide's only
instruction ("`package_close()` in whichever session holds the lock") has nothing to act on, and
the first tool an operator reaches for - the read-only `package_migrate` preview - refused on
the writer lock before it would diagnose anything. Each field repo invented its own liveness
test; ACMP's exists because a bare-pid check once named a live VS Code process that had
recycled the pid.

## What changed

- `db/store.py`: `process_start_time(pid)` observes a pid with the stdlib only - Windows
  `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)` + `GetExitCodeProcess` + `GetProcessTimes`;
  Linux `/proc/<pid>/stat` + `btime`; other POSIX `os.kill(pid, 0)` for liveness only. It spawns
  nothing and signals nothing. **`os.kill(pid, 0)` never runs on Windows (it terminates the
  process there).** Measured on Windows before writing it: a process that has already exited
  still OPENS while any handle to it is held, so a handle proves nothing - only exit code
  `STILL_ACTIVE` does; access denied means the process exists but cannot be inspected.
- `observe_lock(lock_path, probe=...)` returns one of four outcomes with its evidence:
  `not-running`, `reused`, `alive`, `unobservable`. Reuse is decided by **identity** (the start
  time the lock recorded differs from the one observed, 2 s tolerance); for a lock that
  recorded none it falls back to **ordering** (the process started after `taken_at`), labelled
  as the weaker test. Another host, a legacy bare-pid lock, access denied, or a platform that
  cannot report a start time are all `unobservable` - never "assumed dead".
- The lock JSON gains `started` (the writer's own start, epoch seconds).
- Every lock refusal now ends `; observed: <outcome> - <evidence>`.
- `package_migrate`: the `O_EXCL` acquisition moved under `confirm`. The preview reads the
  on-disk state and says when it read under a held lock. The "nothing to migrate" answer keeps
  its error shape (contract unchanged) and now says it is the expected answer on a current store.

## Tests

`tests/test_db_roundtrip.py`: four outcomes driven by injected probes (a real pid would flake);
the legacy-lock ordering fallback incl. the field's 8.5-hour VS Code case; the real probe on
this process and on a finished child; the lock records `started` and the refusal reports the
observation. `tests/test_mcp_contract.py`: preview under a held lock answers, `confirm=true`
still refuses. RED before the change (3 errors + 2 failures), GREEN after.

## Review round (security + Python reviewers, before commit)

- HIGH: a lock with `"pid": Infinity` raised `OverflowError` through the refusal path and
  masked `StoreLockedError`. Now: only a real, bounded `int` is probed (bool, float, str,
  0, negatives and out-of-range values are `unobservable`; a huge pid truncates modulo 2**32
  in a DWORD and would have landed on an unrelated live process), and `_describe_lock` can
  never raise.
- HIGH: a naive or pre-epoch `taken_at` raised `OSError` in the ordering fallback. Caught.
- MEDIUM, dangerous direction: a wall-clock step on Linux moves `btime` and could read the
  same process as `reused`. The lock now also records an exact identity token (Windows
  creation FILETIME; Linux boot id + start ticks), compared exactly; the epoch tolerance is
  the fallback for locks without one.
- MEDIUM, dangerous direction: containers sharing a hostname do not share pids. The lock
  records the pid namespace; a different one is `unobservable`, never probed.
- kernel32 is bound once; a process that vanishes mid-read is `not-running`; the
  real-process test now kills a live child and asserts the held-handle case reads
  `not-running` and that its identity token is gone.
- Accepted limitation, documented: Windows exit code 259 is ambiguous with a process that
  really exited 259 - it reads as `alive`, the safe direction.

## Done criteria

- [x] `python tests/test_db_roundtrip.py` and `python tests/test_mcp_contract.py` -> OK
- [x] `python check.py` -> `ALL CHECKS PASSED`
- [ ] CI green on Ubuntu **and** Windows (the only cross-platform proof)

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts, goldens untouched.
