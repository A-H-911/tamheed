"""Plan 248, setup: a scratch workspace for the loop rehearsal, built from the lab fixture.

The fixture keeps only the package. Its code is the lab seed, which still has the two planted
bugs that the package records as fixed (DEF-001, DEF-002), and lacks the history command and the
CSV export that the package records as Implemented (WBS-2, WBS-4). This script writes code that
matches the package (L2, L5), proves every test green, wires the project note, and makes the
setup commit a BOUND commit, so the loop's drift check finds nothing to register.

    env -u TAMHEED_HOOK_LOG python -I setup_248.py <scratch folder> [<workspace name>]

Each run builds its own workspace, so the note names that folder and its C1 is bound there.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(REPO / "plugins/tamheed/server"), str(REPO / "plugins/tamheed/db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402


def _rm(path) -> None:
    """rmtree that clears the read-only bit git sets on its object files (Windows)."""
    import stat

    def again(fn, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        fn(p)
    shutil.rmtree(path, onerror=again)

TRACKER = '''"""tick: a tiny task tracker (the lab project, as its package records it)."""
import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path

DB = Path("tasks.json")


def load() -> list[dict]:
    return json.loads(DB.read_text()) if DB.exists() else []


def save(tasks: list[dict]) -> None:
    DB.write_text(json.dumps(tasks, indent=2))


def add(title: str, due: str | None) -> dict:
    tasks = load()
    task = {"id": len(tasks) + 1, "title": title, "due": due, "done": None,
            "added": datetime.now().isoformat(timespec="seconds")}
    tasks.append(task)
    save(tasks)
    return task


def overdue(task: dict, today: date | None = None) -> bool:
    """A task is overdue the day AFTER its due date (DEF-001 fixed: due today is not overdue)."""
    if not task["due"] or task["done"]:
        return False
    return date.fromisoformat(task["due"]) < (today or date.today())


def done(task_id: int) -> dict | None:
    tasks = load()
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = datetime.now().isoformat(timespec="seconds")
            save(tasks)
            return task
    return None


def history(task_id: int) -> list[str] | None:
    """When the task was added and, if it is done, when (WBS-2, AC-001)."""
    for task in load():
        if task["id"] == task_id:
            lines = [f"#{task['id']} {task['title']}", f"  added: {task['added']}"]
            if task["done"]:
                lines.append(f"  done: {task['done']}")
            return lines
    return None


def export(path: Path | None = None) -> Path:
    """One CSV row per task, open and done, beside tasks.json (WBS-4, AC-005)."""
    out = path or DB.with_name("tasks.csv")
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "title", "due", "done"])
        for task in load():
            writer.writerow([task["id"], task["title"], task["due"] or "", task["done"] or ""])
    return out


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        # DEF-003 (open, low): the typo is carried, as the package records it.
        print("tick: a tiny task trakcer\\n"
              "  add <title> [--due YYYY-MM-DD]\\n  list\\n  done <id>\\n  history <id>\\n  export")
        return 0
    cmd, *rest = argv
    if cmd == "add":
        due = rest[rest.index("--due") + 1] if "--due" in rest else None
        title = " ".join(a for a in rest if a != "--due" and a != due)
        task = add(title, due)
        print(f"added #{task['id']}: {task['title']}")
    elif cmd == "list":
        for task in load():
            if task["done"]:
                continue
            flag = " (OVERDUE)" if overdue(task) else ""
            print(f"#{task['id']} {task['title']}{flag}")
    elif cmd == "done":
        task = done(int(rest[0]))
        print(f"done #{rest[0]}" if task else f"no task #{rest[0]}")
    elif cmd == "history":
        lines = history(int(rest[0]))
        print("\\n".join(lines) if lines else f"no task #{rest[0]}")
    elif cmd == "export":
        print(f"wrote {export()}")
    else:
        print(f"unknown command: {cmd}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''

TESTS = '''"""Tests for tick (the lab project)."""
import csv
import os
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

import tracker


class InTempDir(unittest.TestCase):
    def setUp(self):
        self._old = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        os.chdir(self._tmp.name)

    def tearDown(self):
        os.chdir(self._old)
        self._tmp.cleanup()


class OverdueTest(unittest.TestCase):
    def test_past_due_is_overdue(self):
        task = {"due": "2020-01-01", "done": None}
        self.assertTrue(tracker.overdue(task, today=date(2026, 1, 1)))

    def test_no_due_date_never_overdue(self):
        self.assertFalse(tracker.overdue({"due": None, "done": None}))

    def test_due_today_is_not_overdue(self):          # AC-002, DEF-001
        task = {"due": "2026-06-01", "done": None}
        self.assertFalse(tracker.overdue(task, today=date(2026, 6, 1)))


class AddedTimestampTest(InTempDir):
    def test_added_timestamp_is_a_valid_time(self):    # DEF-002: no wall-clock race
        task = tracker.add("write report", None)
        datetime.fromisoformat(task["added"])


class RoundTripTest(InTempDir):
    def test_add_list_done_history(self):               # AC-001
        task = tracker.add("write report", "2026-09-01")
        self.assertEqual(tracker.load()[0]["title"], "write report")
        tracker.done(task["id"])
        lines = tracker.history(task["id"])
        self.assertTrue(lines[1].startswith("  added: "))
        self.assertTrue(lines[2].startswith("  done: "))
        self.assertIsNone(tracker.history(99))


class ExportTest(InTempDir):
    def test_one_row_per_task_beside_tasks_json(self):  # AC-005
        tracker.add("one", None)
        tracker.done(tracker.add("two", "2026-01-01")["id"])
        out = tracker.export()
        self.assertEqual(out, Path("tasks.csv"))
        rows = list(csv.reader(out.open(encoding="utf-8")))
        self.assertEqual(rows[0], ["id", "title", "due", "done"])     # AC-006: the header
        self.assertEqual(len(rows), 3)


if __name__ == "__main__":
    unittest.main()
'''


def git(ws, *args) -> str:
    return subprocess.run(["git", *args], cwd=ws, capture_output=True, text=True,
                          check=True).stdout.strip()


def reading() -> dict:
    g, r = srv.gate_run(), srv.readiness_check("package")
    return {"gate_ready": g["ready"], "ready": r["ready"],
            "rules": {x["rule"]: x["status"] for x in r["rules"]}}


def main() -> None:
    scratch = Path(sys.argv[1]).resolve()
    ws = scratch / (sys.argv[2] if len(sys.argv) > 2 else "base")
    if ws.exists():
        _rm(ws)
    ws.mkdir(parents=True)
    fix = REPO / "evals/sample-results/lab-tracker/package"
    shutil.copytree(fix, ws / "package", ignore=shutil.ignore_patterns(".lock", "CLAUDE.md"))
    (ws / "tracker.py").write_text(TRACKER, encoding="utf-8", newline="\n")
    (ws / "test_tracker.py").write_text(TESTS, encoding="utf-8", newline="\n")
    (ws / ".gitignore").write_text("tasks.json\ntasks.csv\n__pycache__/\n", encoding="utf-8",
                                   newline="\n")
    t = subprocess.run([sys.executable, "-m", "unittest", "-q"], cwd=ws, capture_output=True,
                       text=True)
    print("OBS tests:", t.returncode, (t.stderr.strip().splitlines() or [""])[-1])
    assert t.returncode == 0, t.stderr

    # the fixture's own reading, on a throwaway copy, against this workspace's reading
    tmp = scratch / "fixture-reading"
    if tmp.exists():
        _rm(tmp)
    shutil.copytree(fix, tmp / "package", ignore=shutil.ignore_patterns(".lock"))
    srv.PACKAGE_ROOT = tmp
    assert srv.package_open("package")["ok"]
    before = reading()
    srv.package_close()
    _rm(tmp)

    srv.PACKAGE_ROOT = ws
    assert srv.package_open("package")["ok"]
    em = srv.handoff_emit(str(ws))
    print("OBS emit:", em["ok"], "| restated:", len(em.get("restated_content") or []))
    srv.package_close()
    (ws / ".mcp.json").unlink(missing_ok=True)       # a local-folder artifact, never a field file

    for args in (["init", "-q"], ["config", "core.autocrlf", "false"],
                 ["config", "user.name", "lab operator"],
                 ["config", "user.email", "lab@example.invalid"], ["add", "-A"],
                 ["commit", "-qm", "lab tracker: the code of SL-001 to SL-003, and its package"]):
        git(ws, *args)
    c1 = git(ws, "rev-parse", "HEAD")
    assert srv.package_open("package")["ok"]
    bind = srv.work_bind(c1, ["WBS-1", "WBS-2", "WBS-3", "WBS-4"],
                         note="the rehearsal's setup commit: the code that SL-001 to SL-003 built")
    print("OBS bind:", bind.get("ok"), bind.get("error"))
    after = reading()
    srv.package_close()
    git(ws, "add", "-A")
    git(ws, "commit", "-qm", "tamheed: bind the setup commit")
    changed = {k: (before["rules"].get(k), v) for k, v in after["rules"].items()
               if before["rules"].get(k) != v}
    print("OBS reading fixture -> workspace:", before["gate_ready"], before["ready"], "->",
          after["gate_ready"], after["ready"], "| rules changed:", changed or "none")
    print("OBS commits:", git(ws, "log", "--oneline").splitlines())
    print("OBS status clean:", git(ws, "status", "--porcelain") == "")
    (scratch / f"baseline-{ws.name}.json").write_text(json.dumps({"c1": c1, "reading": after}, indent=1),
                                           encoding="utf-8")


if __name__ == "__main__":
    main()
