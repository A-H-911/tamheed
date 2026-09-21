# Plan 064: `package_unlock` - the sanctioned, journaled route out of a dead holder's lock

> Reviewer-executed (maintainer-delegated), 2026-09-21. Batch map:
> [063-074-batch-findings-25.md](063-074-batch-findings-25.md). Depends on plan 063.

## Status

- **Priority**: P1 - **Effort**: M - **Risk**: MEDIUM (a destructive, operator-only tool)
- **Category**: operability + doctrine (findings_25 s1) - **Planned at**: commit `79e8c5b`

## Why this matters

Plan 063 made a lock's holder observable. The operator still had no sanctioned way to act on
"the holder is dead": every field repo deleted `data/.lock` by hand on its own home-grown
liveness test. The maintainer chose (interview, 2026-09-21) to give that act one tool.

## The rule (maintainer-approved)

`package_unlock(name)` REPORTS: the lock, the observation, whether confirm would proceed.
`confirm=true` is operator-words-only, like `force`, and proceeds **only** when the holder was
observed `not-running` or `reused`. It **refuses on `alive` and on `unobservable`** (another host
or pid namespace, access denied, a legacy or garbled lock, a platform that cannot report a start
time): a lock the tool could not see is not a lock it may remove. Manual removal of
`data/.lock` stays the deliberate path for that case. "Operator-words-only" is convention, as
with `force` - nothing mechanical distinguishes an operator's word from an agent's.

Doctrine, flipped: from "the store never removes a lock" to **"the store observes, reports, and
removes a lock only on the operator's word, through one journaled tool."**

## What it does under `confirm=true`

1. Snapshots the lock's bytes, observes the holder, refuses unless `not-running` / `reused`.
2. Proves the on-disk store LOADS (lock-free). A writer that died mid-write leaves `data/`
   broken: refuse, leave the lock, point at git.
3. Re-reads the lock and removes it **only if its bytes still equal the snapshot** - a live
   writer that took the lock while the store was being checked keeps it.
4. Opens the package, appends ONE `forced-override` row (actor `system:package-unlock`) naming
   pid, host, taken_at (length-capped: lock content is a garble-able file) and the observation,
   commits, closes, returns the row id. No new event type, so no schema migration.
5. A pre-v4 store cannot be opened: its lock is removed unjournaled and the result says so.

Refusals in `store.py`, `package_open` and `package_migrate` now name the tool. 19 tools.

## Review round (security + Python reviewers, before commit)

- CRITICAL (found independently by the reviewer and closed before its report landed): the
  removal was unconditional, so two racing unlocks - or an unlock racing a legitimate open -
  could delete a LIVE writer's fresh lock. Closed by the snapshot comparison, with a test that
  swaps the lock mid-check.
- HIGH: `lock.unlink()` could raise (`PermissionError` on Windows). Now an error result.
- HIGH: `finally: package_close()` could raise and mask the outcome. Now reported as
  `close_error`, never raised.
- MEDIUM: lock-derived strings entered the journal uncapped. Capped.
- Residual, accepted and stated: a microsecond window remains between the byte comparison and
  the unlink. Closing it needs OS-level locking the store deliberately does not use; the
  seconds-long window (the store load) is the one that mattered and it is closed.

## Tests (`tests/test_mcp_contract.py`, `V4EngineTest`)

Report mode writes nothing; `alive` and `unobservable` refused with the lock untouched;
`not-running` and `reused` unlock, journal, verify clean and leave nothing open; an unloadable
store is refused; a lock swapped mid-check is never removed; the edges (open here, no lock,
name guard, registered); refusals name the tool. RED before (5 errors + 1 failure), GREEN
after. `--selftest`: `19/19 tools registered`.

## Done criteria

- [x] `python tests/test_mcp_contract.py` -> OK (146)
- [x] `python check.py` -> `ALL CHECKS PASSED`; `--selftest` -> 19/19
- [ ] CI green on Ubuntu and Windows

### Release discipline

No `plugin.json` bump; CHANGELOG under `[Unreleased]`; stamps, stock prompts, goldens untouched.
Docs and the SECURITY.md doctrine sentence land in plan 072.
