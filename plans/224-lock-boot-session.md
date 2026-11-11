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
