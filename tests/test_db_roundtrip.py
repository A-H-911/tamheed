"""Round-trip + integrity tests for the v2 package store (plan 007/B2, ADR-0001).

Stdlib unittest only. Covers: JSONL -> SQLite -> JSONL byte identity, FK enforcement,
CHECK enforcement, ADR supersession immutability, the requirement auto-advance trigger,
and the single-writer lockfile.
"""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "plugins" / "tamheed" / "db"))

import store  # noqa: E402  (plugins/tamheed/db/store.py)

ENTITY_TYPES = [
    ("requirement", "Requirement", "FR-", "Always"),
    ("decision", "Decision", "DEC-", "Always"),
    ("adr", "ADR", "ADR-", "Conditional"),
    ("acceptance-criterion", "Acceptance criterion", "AC-", "Always"),
    ("audit-verdict", "Audit verdict", "AV-", "Continuous"),
    ("test", "Test", "TEST-", "Conditional"),
    ("phase", "Phase", "PH-", "Always"),
    ("slice", "Slice", "SL-", "Always"),
    ("invariant", "Invariant", "INV-", "Conditional"),
    ("deferred-work", "Deferred work", "DW-", "Conditional"),
    ("prompt", "Prompt", "PRT-", "Conditional"),   # plan 192 (v6): rows, not files
]


def seed(conn: sqlite3.Connection) -> None:
    """A minimal but relation-rich package: FR -> DEC/ADR/AC/TEST links, phase -> slice."""
    conn.executemany(
        "INSERT INTO entity_types (type_id, label, id_prefix, generation_class)"
        " VALUES (?, ?, ?, ?)",
        ENTITY_TYPES,
    )
    conn.execute(
        "INSERT INTO packages (name, title, profile, mode, package_version, created_at)"
        " VALUES ('demo', 'Demo package', 'ai-agentic', 'full', '2.0.0', '2026-07-17')"
    )
    conn.execute(
        "INSERT INTO requirements (id, kind, title, mvp, lifecycle_status,"
        " source_kind, source_span)"
        " VALUES ('FR-001', 'functional', 'Triage inbound email', 1, 'Approved',"
        " 'brief', 'brief L10-L14')"
    )
    conn.execute(
        "INSERT INTO decisions (id, title, lifecycle_status)"
        " VALUES ('DEC-001', 'Human approval gate', 'Approved')"
    )
    conn.execute(
        "INSERT INTO adrs (id, title, context, decision, consequences, lifecycle_status)"
        " VALUES ('ADR-0001', 'Bounded loop', 'ctx', 'dec', 'cons', 'Approved')"
    )
    conn.execute(
        "INSERT INTO phases (id, title, lifecycle_status) VALUES ('PH-1', 'MVP', 'Approved')"
    )
    conn.execute(
        "INSERT INTO slices (id, title, phase_id) VALUES ('SL-001', 'Ingest', 'PH-1')"
    )
    conn.execute(
        "INSERT INTO acceptance_criteria (id, title, statement, requirement_id, slice_id,"
        " lifecycle_status) VALUES ('AC-001', 'Email triaged', 'given/when/then',"
        " 'FR-001', 'SL-001', 'Approved')"
    )
    conn.execute(
        "INSERT INTO tests (id, title) VALUES ('TEST-001', 'triage e2e')"
    )
    conn.execute(
        "INSERT INTO prompts (id, kind, title, body, phase_id, plugin_skill, lifecycle_status)"
        " VALUES ('PRT-001', 'kickoff', 'Kickoff', 'Read the record first.', 'PH-1',"
        " 'slice-kickoff', 'Approved')"
    )
    conn.executemany(
        "INSERT INTO trace_edges (from_id, to_id, relation) VALUES (?, ?, ?)",
        [
            ("FR-001", "DEC-001", "derives_from"),
            ("AC-001", "FR-001", "verifies"),
            ("TEST-001", "FR-001", "tests"),
            ("SL-001", "FR-001", "implements"),
        ],
    )
    conn.commit()


class RoundTripTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.pkg = Path(self._tmp.name)
        self.data = self.pkg / "data"

    def tearDown(self):
        self._tmp.cleanup()

    def _read_all(self):
        return {p.name: p.read_bytes() for p in sorted(self.data.glob("*.jsonl"))}

    def test_roundtrip_byte_identity(self):
        with store.PackageStore(self.pkg) as s:
            seed(s.conn)
            s.commit()
        first = self._read_all()
        self.assertTrue(first, "seed produced no JSONL files")
        # Reload from text and write back untouched: bytes must be identical.
        with store.PackageStore(self.pkg) as s:
            s.commit()
        self.assertEqual(first, self._read_all())

    def test_canonical_shape(self):
        with store.PackageStore(self.pkg) as s:
            seed(s.conn)
            s.commit()
        raw = (self.data / "requirements.jsonl").read_bytes()
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"\r", raw)
        # entity_index is derived and must never be serialized.
        self.assertFalse((self.data / "entity_index.jsonl").exists())

    def test_fk_violation_raises(self):
        conn = store.connect()
        seed(conn)
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO trace_edges (from_id, to_id, relation)"
                " VALUES ('FR-001', 'FR-999', 'relates_to')"
            )

    def test_check_violation_raises(self):
        conn = store.connect()
        seed(conn)
        # D-U1: 'Draft' is not a legal decision status (G-DEC-STATUS as schema).
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO decisions (id, title, lifecycle_status)"
                " VALUES ('DEC-002', 'x', 'Draft')"
            )

    def test_provenance_not_null(self):
        conn = store.connect()
        seed(conn)
        # G-REQ-SRC as schema: requirements demand source_kind + source_span.
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO requirements (id, kind, title) VALUES ('FR-002', 'functional', 'x')"
            )

    def test_approved_adr_immutable(self):
        conn = store.connect()
        seed(conn)
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute("UPDATE adrs SET decision = 'rewritten' WHERE id = 'ADR-0001'")
        # Supersession path stays open: successor first, then point the old row at it.
        conn.execute(
            "INSERT INTO adrs (id, title, lifecycle_status)"
            " VALUES ('ADR-0002', 'Bounded loop v2', 'Proposed')"
        )
        conn.execute(
            "UPDATE adrs SET superseded_by = 'ADR-0002', lifecycle_status = 'Superseded'"
            " WHERE id = 'ADR-0001'"
        )

    def test_requirement_auto_advance(self):
        conn = store.connect()
        seed(conn)
        conn.execute(
            "INSERT INTO audit_verdicts (id, ac_id, verdict) VALUES ('AV-001', 'AC-001', 'Met')"
        )
        status = conn.execute(
            "SELECT lifecycle_status FROM requirements WHERE id = 'FR-001'"
        ).fetchone()[0]
        self.assertEqual(status, "Implemented")

    def test_gate_views(self):
        conn = store.connect()
        seed(conn)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM g_trace_failures").fetchone()[0], 0)
        conn.execute("DELETE FROM trace_edges WHERE from_id = 'TEST-001'")
        self.assertEqual(
            conn.execute("SELECT id FROM g_trace_failures").fetchall(), [("FR-001",)]
        )

    def test_lockfile_single_writer(self):
        with store.PackageStore(self.pkg):
            with self.assertRaises(store.StoreLockedError):
                store.PackageStore(self.pkg).__enter__()
        # Lock released on exit: reopening succeeds.
        with store.PackageStore(self.pkg):
            pass

    def _lock(self, **holder):
        lock = Path(self.pkg) / "data" / ".lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text(json.dumps(holder), encoding="utf-8")
        return lock

    def test_observe_lock_four_outcomes(self):
        """Plan 063 (findings_25 §1): the store OBSERVES a lock's holder and reports it —
        not-running / reused / alive / unobservable — and never guesses. Fakes drive
        the branches (a real pid would make this flaky); the discriminator for reuse
        is recorded-start != observed-start, both from the process API."""
        here = store.socket.gethostname()
        lock = self._lock(pid=4242, host=here, taken_at="2026-09-19T20:13:02+00:00",
                          started=1000.0)
        obs = lambda probe: store.observe_lock(lock, probe=probe)["outcome"]
        # exact identity wins over the epoch tolerance when the lock recorded a token
        tok = self._lock(pid=4242, host=here, taken_at="2026-09-19T20:13:02+00:00",
                         started=1000.0, identity="win:1")
        run = lambda pid: ("running", 1000.0)
        self.assertEqual(store.observe_lock(tok, probe=run, identity=lambda p: "win:1")
                         ["outcome"], "alive")
        self.assertEqual(store.observe_lock(tok, probe=run, identity=lambda p: "win:2")
                         ["outcome"], "reused")        # same second, different process
        ns = self._lock(pid=4242, host=here, taken_at="2026-09-19T20:13:02+00:00",
                        pidns="pid:[1]")
        self.assertEqual(store.observe_lock(ns, probe=lambda pid: ("not-running", None))
                         ["outcome"], "unobservable")  # another container, never probed
        lock = self._lock(pid=4242, host=here, taken_at="2026-09-19T20:13:02+00:00",
                          started=1000.0)
        self.assertEqual(obs(lambda pid: ("not-running", None)), "not-running")
        self.assertEqual(obs(lambda pid: ("running", 1000.5)), "alive")       # same process
        self.assertEqual(obs(lambda pid: ("running", 5000.0)), "reused")      # pid recycled
        self.assertEqual(obs(lambda pid: ("running", None)), "unobservable")  # no start time
        self.assertEqual(obs(lambda pid: ("unobservable", None)), "unobservable")
        other = self._lock(pid=4242, host="some-other-host", taken_at="2026-09-19T20:13:02+00:00")
        out = store.observe_lock(other, probe=lambda pid: ("not-running", None))
        self.assertEqual(out["outcome"], "unobservable")                      # never probed
        self.assertIn("another host", out["evidence"])

    def test_a_host_rename_inside_one_boot_is_still_this_machine(self):
        """Plan 224 (R88, the field's lock report): a host name can change while the
        machine runs. The boot session bridges that. Nothing else does: a machine made
        from the same image has its own boot, a restart ends the session, and a lock
        written before the marker existed carries none."""
        here = store.socket.gethostname()
        # the lock carries this process's own pid namespace, as a real lock does (on Linux
        # the bridge needs it proven equal - see the container test below)
        base = dict(pid=4242, taken_at="2026-09-19T20:13:02+00:00", started=1000.0,
                    pidns=store._pid_namespace())
        dead = lambda pid: ("not-running", None)
        lock = self._lock(host="old-name.local", boot="boot-A", **base)
        out = store.observe_lock(lock, probe=dead, boot=lambda: "boot-A")
        self.assertEqual(out["outcome"], "not-running")           # observed, so unlockable
        self.assertIn("old-name.local", out["evidence"])          # both names are told
        self.assertIn(here, out["evidence"])
        out = store.observe_lock(lock, probe=lambda pid: ("running", 1000.5),
                                 boot=lambda: "boot-A")
        self.assertEqual(out["outcome"], "alive")                 # a live holder is still seen
        for lock_boot, now_boot in (("boot-A", "boot-B"),         # a restart, or another machine
                                    (None, "boot-A"),             # a lock from before 6.5.0
                                    ("boot-A", None)):            # a platform with no marker
            holder = dict(base, host="old-name.local")
            if lock_boot:
                holder["boot"] = lock_boot
            probed = []
            out = store.observe_lock(self._lock(**holder),
                                     probe=lambda pid: probed.append(pid) or ("not-running", None),
                                     boot=lambda b=now_boot: b)
            self.assertEqual(out["outcome"], "unobservable", (lock_boot, now_boot))
            self.assertIn("another host", out["evidence"])
            self.assertEqual(probed, [])                          # never probed
        # the same host name never asks for the marker: that path is unchanged
        out = store.observe_lock(self._lock(host=here, **base), probe=dead,
                                 boot=lambda: self.fail("the marker was read"))
        self.assertEqual(out["outcome"], "not-running")

    def test_containers_that_share_a_boot_are_not_bridged_without_a_proven_namespace(self):
        """Plan 224 (review): containers on one Linux host share the kernel's boot id. The
        bridge there needs the pid namespace recorded AND equal, or a pid that this
        container cannot see would read as not-running while its writer lives."""
        base = dict(pid=4242, host="other-container", boot="boot-A", started=1000.0,
                    taken_at="2026-09-19T20:13:02+00:00")
        probed = []
        dead = lambda pid: probed.append(pid) or ("not-running", None)
        real_platform, real_ns = store.sys.platform, store._pid_namespace
        self.addCleanup(setattr, store.sys, "platform", real_platform)
        self.addCleanup(setattr, store, "_pid_namespace", real_ns)
        store.sys.platform = "linux"
        store._pid_namespace = lambda: "pid:[1]"
        for pidns in (None, "pid:[2]"):                           # none recorded, or another
            holder = dict(base) if pidns is None else dict(base, pidns=pidns)
            out = store.observe_lock(self._lock(**holder), probe=dead, boot=lambda: "boot-A")
            self.assertEqual(out["outcome"], "unobservable", pidns)
        self.assertEqual(probed, [])                              # never probed
        out = store.observe_lock(self._lock(**dict(base, pidns="pid:[1]")), probe=dead,
                                 boot=lambda: "boot-A")
        self.assertEqual(out["outcome"], "not-running")           # proven the same: bridged

    def test_the_lock_records_the_boot_session_and_has_one_writer(self):
        """Plan 224: the store and package_migrate write the SAME payload (lock_payload), and
        the boot marker is the same in two processes of one boot, or absent in both."""
        payload = store.lock_payload()
        self.assertEqual(set(payload), {"pid", "host", "taken_at", "started", "identity",
                                        "pidns", "boot"})
        self.assertEqual(payload["boot"], store.boot_session())
        with store.PackageStore(self.pkg):
            held = json.loads((Path(self.pkg) / "data" / ".lock").read_text(encoding="utf-8"))
        self.assertEqual(set(held), set(payload))
        other = subprocess.run(
            [sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]);"
             " import store; print(store.boot_session())", str(Path(store.__file__).parent)],
            capture_output=True, text=True)
        self.assertEqual(other.stdout.strip(), str(store.boot_session()))
        if sys.platform.startswith("linux"):
            self.assertTrue(store.boot_session())                 # the kernel always has one
            # recorded for the reasoning in plan 224: the initial pid namespace has one
            # constant id on every Linux host, so this check alone tells no two hosts apart
            self.assertRegex(store._pid_namespace(), r"^pid:\[\d+\]$")
        if sys.platform == "win32":
            self.assertIsNone(store.boot_session())               # no marker a user can read

    def test_macos_reads_a_start_time_through_the_seam(self):
        """Plan 224b (R86): macOS had no start time, so a running pid was always
        unobservable and a reused pid could not be told from the writer. The calls were
        measured on the field's Mac first (macOS 27.2, arm64): proc_pidinfo flavour 3 fills
        the 136-byte proc_bsdinfo, and answers errno 3 for no such pid and errno 1 for
        another user's. This drives the branches on every platform. The real calls run on
        the macOS CI legs (the next test)."""
        self.addCleanup(setattr, store.sys, "platform", store.sys.platform)
        self.addCleanup(setattr, store, "_darwin_bsdinfo", store._darwin_bsdinfo)
        self.addCleanup(setattr, store.os, "kill", store.os.kill)
        store.sys.platform = "darwin"
        store.os.kill = lambda pid, sig: self.fail("the liveness fallback ran")
        store._darwin_bsdinfo = lambda pid: ("running", (1000, 500000))
        self.assertEqual(store.process_start_time(4242), ("running", 1000.5))
        self.assertEqual(store.process_identity(4242), "mac:1000:500000")   # exact, no float
        # gone needs two signals: the library found no process AND the kernel agrees
        store._darwin_bsdinfo = lambda pid: ("not-running", None)
        store.os.kill = lambda pid, sig: None                 # the kernel still has it
        self.assertEqual(store.process_start_time(4242), ("unobservable", None))

        def no_such(pid, sig):
            raise ProcessLookupError()

        store.os.kill = no_such
        self.assertEqual(store.process_start_time(4242), ("not-running", None))
        self.assertIsNone(store.process_identity(4242))
        store.os.kill = lambda pid, sig: self.fail("the liveness fallback ran")
        store._darwin_bsdinfo = lambda pid: ("unobservable", None)             # another user's pid
        self.assertEqual(store.process_start_time(4242), ("unobservable", None))

        def broken(pid):
            raise OSError("no libproc")

        # the library fails: the old liveness probe still answers, with no start time
        store._darwin_bsdinfo = broken
        store.os.kill = lambda pid, sig: None
        self.assertEqual(store.process_start_time(4242), ("running", None))
        self.assertIsNone(store.process_identity(4242))

    def test_the_macos_library_answer_is_mapped_safely(self):
        """Plan 224b (review): the mapping from the library call to a state, on every
        platform, through a stand-in library. Only the full struct means running. Only
        "no such process" means gone. Every other answer is unobservable."""
        import ctypes
        import errno

        class Lib:
            def __init__(self, returned, err, sec=0, usec=0):
                self.returned, self.err, self.sec, self.usec = returned, err, sec, usec

            def proc_pidinfo(self, pid, flavor, arg, buf, size):
                assert (flavor, arg, size) == (3, 0, 136)
                raw = (self.sec.to_bytes(8, sys.byteorder)
                       + self.usec.to_bytes(8, sys.byteorder))
                for i, byte in enumerate(raw):
                    buf[120 + i] = byte
                ctypes.set_errno(self.err)
                return self.returned

        self.addCleanup(setattr, store, "_LIBPROC", store._LIBPROC)
        for lib, expected in (
                (Lib(136, 0, 1794445618, 789145), ("running", (1794445618, 789145))),
                (Lib(0, errno.ESRCH), ("not-running", None)),       # no such process
                (Lib(0, errno.EPERM), ("unobservable", None)),      # another user's process
                (Lib(96, 0), ("unobservable", None)),               # a short struct
                (Lib(-1, errno.EINVAL), ("unobservable", None))):
            store._LIBPROC = lib
            self.assertEqual(store._darwin_bsdinfo(4242), expected, (lib.returned, lib.err))

    @unittest.skipUnless(sys.platform == "darwin", "the real macOS calls run on the macOS CI legs")
    def test_macos_real_calls(self):
        """Plan 224b: the three system calls on a real macOS."""
        import time
        state, started = store.process_start_time(os.getpid())
        self.assertEqual(state, "running")
        self.assertIsInstance(started, float)
        self.assertLess(abs(started - time.time()), 6 * 3600)        # this process is young
        token = store.process_identity(os.getpid())
        self.assertRegex(token, r"^mac:\d+:\d+$")
        self.assertEqual(token, store.process_identity(os.getpid()))  # fixed at creation
        self.assertRegex(store.boot_session(), r"^mac:[0-9A-Fa-f-]{36}$")
        self.assertEqual(store.process_start_time(4194000)[0], "not-running")   # no such pid
        self.assertIn(store.process_start_time(1)[0], ("unobservable", "running"))  # launchd
        with store.PackageStore(self.pkg):                           # a live holder reads alive
            with self.assertRaises(store.StoreLockedError) as ctx:
                store.PackageStore(self.pkg).__enter__()
        self.assertIn("observed: alive", str(ctx.exception))

    def test_observe_lock_legacy_lock_falls_back_to_ordering(self):
        """A lock without a recorded start (pre-4.9.0, or a legacy bare pid) can only be
        judged by ordering: a process that started AFTER the lock was taken is not the
        writer (the field's VS Code case). Weaker than identity, and labelled so."""
        here = store.socket.gethostname()
        lock = self._lock(pid=71948, host=here, taken_at="2026-08-04T01:51:50+00:00")
        taken = datetime(2026, 8, 4, 1, 51, 50, tzinfo=timezone.utc).timestamp()
        late = store.observe_lock(lock, probe=lambda pid: ("running", taken + 8.5 * 3600))
        self.assertEqual(late["outcome"], "reused")
        self.assertIn("ordering", late["evidence"])
        early = store.observe_lock(lock, probe=lambda pid: ("running", taken - 60))
        self.assertEqual(early["outcome"], "alive")
        lock.write_text("71948", encoding="utf-8")                            # bare-int lock
        self.assertEqual(store.observe_lock(
            lock, probe=lambda pid: ("not-running", None))["outcome"], "unobservable")

    def test_a_garbled_pid_is_unobservable_and_the_refusal_never_raises(self):
        """Security review of plan 063: JSON accepts Infinity (int() overflows), bool is
        an int, and a huge pid truncates modulo 2**32 on Windows onto an unrelated live
        process. None may be probed, and none may mask the StoreLockedError."""
        for bad in (float("inf"), True, -1, 0, 2 ** 40, "4242", 4242.0, None):
            self.assertEqual(store.process_start_time(bad), ("unobservable", None), bad)
        lock = Path(self.pkg) / "data" / ".lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text('{"pid": Infinity, "host": "%s"}' % store.socket.gethostname(),
                        encoding="utf-8")
        with self.assertRaises(store.StoreLockedError) as ctx:
            store.PackageStore(self.pkg).__enter__()
        self.assertIn("observed: unobservable", str(ctx.exception))

    def test_process_probe_on_real_processes(self):
        """The real probe, on the two cases that cannot flake: this process is running
        with an observable-or-absent start, and a finished child whose handle is
        released is never reported as the same running process."""
        state, _ = store.process_start_time(os.getpid())
        self.assertEqual(state, "running")
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        try:
            pid = child.pid
            self.assertEqual(store.process_start_time(pid)[0], "running")
            alive_token = store.process_identity(pid)
        finally:
            child.kill()
            child.wait()
        # the handle is still held here: on Windows the dead process still OPENS, and
        # only its exit code says it is gone - the case the probe was written for
        self.assertEqual(store.process_start_time(pid)[0], "not-running")
        del child
        # whatever owns that pid now (nothing, or a recycled process) is NOT the child
        if alive_token is not None:
            self.assertNotEqual(store.process_identity(pid), alive_token)

    def test_lock_records_the_writers_start_and_refusal_reports_the_observation(self):
        with store.PackageStore(self.pkg):
            held = json.loads((Path(self.pkg) / "data" / ".lock").read_text(encoding="utf-8"))
            self.assertIn("started", held)
            with self.assertRaises(store.StoreLockedError) as ctx:
                store.PackageStore(self.pkg).__enter__()
        self.assertIn("observed:", str(ctx.exception))
        # it is us: `alive` wherever the platform reports a start time, and an honest
        # `unobservable` where it cannot - never `not-running` or `reused`
        expected = ("alive" if store.process_start_time(os.getpid())[1] is not None
                    else "unobservable")
        self.assertIn(f"observed: {expected}", str(ctx.exception))


    # ---- plan 217 (ACMP's FB-029): the flush writes only what changed, atomically ----

    def _recording_replace(self, fail_on=None, fail_times=0):
        """A stand-in for store._replace: records every target name, and raises
        OSError(22) `fail_times` times (forever when fail_times is None) for targets
        whose name contains `fail_on`."""
        import os as _os
        calls = []
        state = {"left": fail_times}

        def fake(src, dst):
            calls.append(Path(dst).name)
            if fail_on and fail_on in Path(dst).name and (state["left"] is None or state["left"] > 0):
                if state["left"] is not None:
                    state["left"] -= 1
                raise OSError(22, "Invalid argument", str(dst))
            return _os.replace(src, dst)
        return fake, calls

    def test_commit_writes_only_the_changed_files(self):
        from unittest import mock
        with store.PackageStore(self.pkg) as s:
            seed(s.conn)
            s.commit()
            fake, calls = self._recording_replace()
            s.conn.execute("UPDATE requirements SET title = 'Triage inbound mail' WHERE id = 'FR-001'")
            s.conn.execute("DELETE FROM prompts")
            with mock.patch.object(store, "_replace", fake), mock.patch.object(store, "_sleep", lambda _s: None):
                report = s.commit()
            self.assertEqual(calls, ["requirements.jsonl"])          # one changed file, one write
            self.assertEqual(report["written"], ["requirements.jsonl"])
            self.assertEqual(report["removed"], ["prompts.jsonl"])    # the now-empty table's file goes
            self.assertFalse((self.data / "prompts.jsonl").exists())
            self.assertNotIn("prompts.jsonl", s._fingerprints)
            self.assertIn("decisions.jsonl", report["unchanged"])
            self.assertEqual(report["retried"], [])

    def test_transient_os_error_is_retried_and_reported(self):
        from unittest import mock
        with store.PackageStore(self.pkg) as s:
            seed(s.conn)
            s.commit()
            fake, calls = self._recording_replace(fail_on="requirements", fail_times=1)
            s.conn.execute("UPDATE requirements SET title = 'again' WHERE id = 'FR-001'")
            with mock.patch.object(store, "_replace", fake), mock.patch.object(store, "_sleep", lambda _s: None):
                report = s.commit()
            self.assertEqual(report["written"], ["requirements.jsonl"])
            self.assertEqual(report["retried"], ["requirements.jsonl"])
            self.assertEqual(calls.count("requirements.jsonl"), 2)
            self.assertEqual(list(self.data.glob("*.writing")), [])

    def test_partial_flush_names_what_landed_and_never_trips_the_guard(self):
        """FB-029: a flush that fails on one file after others landed. The error names the
        written, the failed and the pending files; the SQLite state is committed; the written
        files' fingerprints are current, so the NEXT commit is not refused as a stale tree and
        it writes the failed file."""
        from unittest import mock
        with store.PackageStore(self.pkg) as s:
            seed(s.conn)
            s.commit()
            s.conn.execute("UPDATE decisions SET title = 'Human gate, approved' WHERE id = 'DEC-001'")
            s.conn.execute("UPDATE requirements SET title = 'Triage mail' WHERE id = 'FR-001'")
            fake, calls = self._recording_replace(fail_on="requirements", fail_times=None)
            with mock.patch.object(store, "_replace", fake), mock.patch.object(store, "_sleep", lambda _s: None):
                with self.assertRaises(store.StoreFlushError) as ctx:
                    s.commit()
            exc = ctx.exception
            self.assertEqual(exc.failed["file"], "requirements.jsonl")
            self.assertEqual(exc.failed["errno"], 22)
            self.assertEqual(calls.count("requirements.jsonl"), 5)   # five attempts, then the error
            self.assertEqual(sorted(exc.written + [exc.failed["file"]] + exc.pending),
                             sorted(set(exc.written + [exc.failed["file"]] + exc.pending)))
            self.assertIn("requirements.jsonl", str(exc))
            self.assertIn("decisions.jsonl", exc.written + exc.pending)
            # the batch is committed in memory ...
            row = s.conn.execute("SELECT title FROM requirements WHERE id = 'FR-001'").fetchone()
            self.assertEqual(row[0], "Triage mail")
            # ... the written files' fingerprints follow the bytes on disk ...
            for name in exc.written:
                self.assertEqual(s._fingerprints[name],
                                 __import__("hashlib").sha256((self.data / name).read_bytes()).hexdigest())
            self.assertEqual(list(self.data.glob("*.writing")), [])  # no temp left behind
            # ... and the next commit is NOT a stale-tree refusal: it writes the failed file
            # and every file the failed flush never reached, nothing else
            report = s.commit()
            self.assertEqual(sorted(report["written"]), sorted(["requirements.jsonl"] + exc.pending))
        with store.PackageStore(self.pkg) as s2:
            row = s2.conn.execute("SELECT title FROM requirements WHERE id = 'FR-001'").fetchone()
            self.assertEqual(row[0], "Triage mail")


    @unittest.skipIf(sys.platform == "win32", "symlinks need a privilege on Windows; CI runs this on Ubuntu")
    def test_write_temp_never_follows_a_planted_symlink(self):
        """Plan 217 review (the 212 class): a symlink planted at `<table>.jsonl.writing` must not
        carry the store's bytes to its target. The temp is created anew with O_EXCL."""
        victim = Path(self._tmp.name) / "victim.txt"
        victim.write_bytes(b"untouched")
        with store.PackageStore(self.pkg) as s:
            seed(s.conn)
            s.commit()
            planted = self.data / "requirements.jsonl.writing"
            planted.symlink_to(victim)
            s.conn.execute("UPDATE requirements SET title = 'planted?' WHERE id = 'FR-001'")
            s.commit()
        self.assertEqual(victim.read_bytes(), b"untouched")
        self.assertIn(b"planted?", (self.data / "requirements.jsonl").read_bytes())
        self.assertFalse(planted.exists() or planted.is_symlink())

    def test_lock_error_names_holder(self):
        """Plan 025 (C31/D): the lock says WHO and SINCE WHEN — a bare PID invited an
        unsound liveness check (PID reuse); legacy bare-int locks still describe."""
        import os as _os
        with store.PackageStore(self.pkg):
            with self.assertRaises(store.StoreLockedError) as ctx:
                store.PackageStore(self.pkg).__enter__()
            self.assertIn(f"pid {_os.getpid()}", str(ctx.exception))
            self.assertIn("since", str(ctx.exception))
        legacy = Path(self.pkg) / "data" / ".lock"
        legacy.write_text("71948", encoding="utf-8")     # pre-2.7.0 bare-PID lock
        try:
            with self.assertRaises(store.StoreLockedError) as ctx:
                store.PackageStore(self.pkg).__enter__()
            self.assertIn("pid 71948", str(ctx.exception))
        finally:
            legacy.unlink()

    def test_commit_refuses_stale_tree(self):
        """Plan 025 (C31/C1): data/ moved underneath the session (git checkout, a
        second writer) -> StoreStaleError naming the file; disk state preserved."""
        with store.PackageStore(self.pkg) as s:
            seed(s.conn)
            s.commit()                                    # baseline fingerprints
            path = Path(self.pkg) / "data" / "requirements.jsonl"
            external = path.read_text(encoding="utf-8") + "\n"
            path.write_text(external, encoding="utf-8")   # the tree moves underneath
            s.conn.execute("UPDATE requirements SET title = 'clobber?' WHERE id = 'FR-001'")
            with self.assertRaises(store.StoreStaleError) as ctx:
                s.commit()
            self.assertIn("requirements.jsonl", str(ctx.exception))
            self.assertEqual(path.read_text(encoding="utf-8"), external)  # not clobbered
        # a fresh session reconciles: reopening reads the disk truth and can commit
        norm = external.rstrip("\n") + "\n"               # canonical load ignores blanks
        with store.PackageStore(self.pkg) as s2:
            s2.commit()
        self.assertEqual((Path(self.pkg) / "data" / "requirements.jsonl")
                         .read_text(encoding="utf-8"), norm)


if __name__ == "__main__":
    unittest.main(verbosity=2)
