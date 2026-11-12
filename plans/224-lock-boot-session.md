# Plan 224 -- the lock survives a host rename inside one boot (FB-001, R86, R88, R89) - two commits

> Status: PLANNED 2026-11-11. Cycle: field round 2026-11 (ACMP FB-030..032, Jisr FB-001..011),
> release 6.5.0, branch `round/6.5.0`. The round record (evaluation, rulings R81-R89, risks,
> execution order) is [field-round-2026-11-record.md](evidence/field-round-2026-11-record.md).

224a (now, needs nothing from Step 0): the Linux boot id, the migrate lock with its staging guard, the
live-holder hint. 224b (after Step 0's two probe files): the macOS boot session and the macOS start
time, built only on calls the probe showed working. A call that failed there goes to the operator first.
- `store.boot_session()`: Linux reads `/proc/sys/kernel/random/boot_id` (already read at
  store.py:164). macOS reads `kern.bootsessionuuid` through ctypes. Windows returns `None`: no marker
  a standard user can read was found (pid 4 measured `unobservable`), and a Windows rename needs a
  restart. Stdlib, no subprocess, `None` on any failure. No hardware id is read or stored.
- `store.lock_payload()` writes the lock and adds `boot`. `PackageStore.__enter__` (store.py:511) and
  `package_migrate` (srv:4914, today an empty file) both use it.
- `observe_lock` (store.py:203): on a host-name mismatch, a lock whose `boot` equals this boot
  session continues to the namespace check and the pid probe, and the evidence names both host
  names. Every other mismatch stays `unobservable`: a lock with no `boot` (written before 6.5.0), a
  different boot (a restart, or another machine), Windows.
- `package_unlock` (srv:5303): refuses while any `data/*.jsonl.tmp` exists, naming the files and
  the git reconcile (R89). For an `alive` holder the report and the refusal say to end that process
  first (the leftover server of the row's `also_seen` note).
- macOS start time: `proc_pidinfo(PROC_PIDTBSDINFO)` through ctypes libproc. Any failure falls back
  to today's `os.kill`. `process_identity` gains a `mac:` token.
- Limits, stated in the docs and in both prompts: new locks only, not across a restart, not on
  Windows, and a lock held on another machine stays a manual removal.
- Docs: `server/README.md:107`, `prompts/README.md:108` (stock, so its history key at the stamp),
  `package-writes` section 10, `orient-resume:45`, `tamheed/SKILL.md:226`, `db/CANONICAL.md:53`,
  `state.md:64`, `package-readme.template.md:55`, `SECURITY.md:79` (the macOS calls).
- Tests (seams `probe=`, `identity=`, new `boot=`): the same boot with another host name and a dead
  pid reads `not-running`. A different boot, a lock with no `boot`, and a platform with no marker
  stay `unobservable` (`test_db_roundtrip:231` holds). A staging file refuses the unlock by name. A
  crashed migrate with no staging file is unlockable. `boot_session()` is equal in two processes on
  the Ubuntu and macOS legs. One Ubuntu test records the pid-namespace value.
- **Check:** the red-first tests, `check.py` on the three OS legs. **Expected:** the outcomes above,
  and no change at all for a lock that names another machine.

## As built: 224a (2026-11-12, branch `round/6.5.0`)

- `store.boot_session()` (Linux: the kernel boot id. Every other platform: none yet) and
  `store.lock_payload()`, the one writer of the lock object for the store and for
  `package_migrate`.
- `observe_lock(..., boot=None)`: a host-name mismatch is bridged only when the lock and this
  machine hold the same boot session. The rest of the observation moved into `_observe_holder`
  unchanged, and the evidence of a bridged case names both host names.
- `package_unlock`: `staged` in the report, a refusal while `data/*.jsonl.tmp` exists, and the
  remedy for an `alive` holder in the note and in the refusal. Its registered description says
  that it refuses while staging files remain.
- Docs: the server README row, `db/CANONICAL.md` (the lock object, and the unlock route in place
  of the older by-hand wording), `package-writes` section 10, `SECURITY.md`, the guide prose of
  `package_unlock` in English and Arabic.
- Owed to the release stamp (plan 229): the stock guide `prompts/README.md` names the lock
  outcomes. Its body is pinned by `stock-history.json`, so it changes with its history key.
- Owed to 224b (after the field probe): the macOS boot session and the macOS start time.

## Validation of 224a

- Red first: five tests failed before the change (two in the store suite, three in the contract
  suite). After it and the reviews the store suite runs 23 tests and the contract suite 240, all
  green.
- The bridged case: the same boot, another host name and a dead pid read `not-running`, and a
  live pid reads `alive`. A different boot, a lock with no marker and a platform with no marker
  stay `unobservable`, and the pid is never probed in those cases. A lock on the same host name
  never reads the marker.
- The migrate lock holds the holder object while the migration runs, and is released after.
  A staging file refuses the unlock by name. With the file gone the same lock is removed.
- `python check.py`: ALL CHECKS PASSED. The selftest registers 19/19 tools. One guide line cite
  into the rewritten unlock report was re-aimed by hand.
- CI before this commit: plan 223 at `a47293a`, run 43129682604, green on eleven jobs.
- Reviews, folded in before the commit. The security reviewer agent was refused by a hook: this
  branch differs from `main` on the CI workflow file, and that hook does not dispatch from such
  a checkout. The hook was not bypassed. The general code reviewer ran with the security brief.
- Found by the maintainer during the review: containers on one Linux host share the kernel, so
  they share its boot id. On Linux the bridge now also needs the pid namespace recorded in the
  lock and equal to this one. A lock that recorded none is not bridged. A test pins both cases.
- Found by the review, fixed: the migration restore removed every table file before it copied
  the backup in, so a restore that stopped left a partial table set with no staging file. It
  stages first now, and falls back to a copy when a rename fails (the restore often runs because
  a rename failed). The migrate lock is written inside the `try`, so a failed write still closes
  and removes the lock. The host string in the bridged evidence is capped at 80 characters.
- The bridged evidence states what was observed (the same boot session, and on Linux the same pid
  namespace). It draws no conclusion about why the names differ.
- Verified in the source: the journal row of an unlock caps the evidence at 300 characters, and
  every half-swapped state of a migration leaves at least one `*.jsonl.tmp` file.
- A stated limit, put to the operator at the commit: two machines restored from ONE MEMORY
  SNAPSHOT share the boot id, as they share every pid. If one of them is then renamed and its
  copy of the writer is killed, the bridge reads a live writer on the other machine as
  not-running. The same limit already holds today for two such machines that keep one host name.
- The bridge has never run on a real system here: this machine is Windows, where no boot marker
  exists. The Ubuntu CI legs run the Linux path. The macOS path is 224b.

## Rulings taken at the review

- **R91 (2026-11-12): the bridge stays as built, with its limit stated.** The maintainer had told
  the operator that a clone has its own boot session. That holds for a machine built from a disk
  image and fails for two machines restored from one memory snapshot. Put again with that
  correction, the operator kept the bridge. The limit is written in `boot_session`, in
  `SECURITY.md` and in both field prompts.
- **R92 (2026-11-12): the code reviewer with a security brief reviews the rest of the round.**
  Plan 227 gets a second independent pass. The refusing hook stays untouched.

## As built: 224b (2026-11-12, after the field probe)

- The probe ran on the field machine first (macOS 27.2, arm64, Python 3.13.4), twice, as two
  processes. Every call worked: `proc_pidinfo` flavour 3 returned 136 for the caller and its
  parent, with the same start for the same pid in both runs. It returned 0 with errno 3 for a
  missing pid and 0 with errno 1 for pid 1. The struct is 136 bytes. `kern.bootsessionuuid` read
  37 bytes with the same hash in both runs.
- `_darwin_bsdinfo(pid)` in the store: stdlib ctypes, no subprocess, no signal. `process_start_time`
  uses it on macOS and falls back to the old liveness probe when the library call raises.
  `process_identity` returns `mac:<seconds>:<microseconds>`, read whole and never through a float.
- `boot_session()` reads `kern.bootsessionuuid` on macOS.
- So on macOS a live holder reads `alive`, a reused pid is told from the writer, and a host name
  that changed inside one boot is bridged. Before, a running pid there was always `unobservable`.
- Docs: `SECURITY.md` (the macOS calls), the server README row, the `boot_session` docstring.

## Validation of 224b

- A seam test drives every macOS branch on all platforms (running, not-running, another user's
  pid, and a failed library call that falls back). A second test makes the real calls and runs
  only on macOS, so the macOS CI legs are its first run. The store suite runs 25 tests here, two
  skipped (the symlink test and the real macOS test).
- `python check.py`: ALL CHECKS PASSED on this machine.
- CI before this commit: plan 225 at `524c9b8`, run 43135043872, green on eleven jobs.
- The field proof is the upgrade prompt: it reads a live holder as `alive` on the field machine.
- Review of 224b, folded in: approved, no critical or high finding. The struct offsets match the
  layout of `proc_bsdinfo`, and the errno pattern is right. Two hardening steps were added. A
  macOS process is called gone only on TWO signals: the library found none, and the kernel
  agrees (`os.kill(pid, 0)`, which sends no signal there). And the mapping from the library call
  to a state is tested on every platform through a stand-in library: only the full struct means
  running, only no-such-process means gone, every other answer is unobservable. The store suite
  runs 26 tests here.
- Stated, not changed: the two libraries are found as they were in the field probe
  (`find_library`). Loading them by a fixed path was proposed, and it is unmeasured on that machine.
- A lock written on macOS before this release recorded no start. For a live holder of such a lock
  the engine falls back to ordering against the lock time, as Linux does for old locks.
