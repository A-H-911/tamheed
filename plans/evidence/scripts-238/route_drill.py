"""Plan 238: the way back, drilled with git itself on clones of a measure_route.py result (scratch
only). PRE is the result's first commit. 6.6.0 runs in this process; 6.5.1 (from the tag) runs in
a subprocess. Prints file names, counts and verdicts only.

    env -u TAMHEED_HOOK_LOG python route_drill.py <measured ws> <package dir>
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "plugins/tamheed/server"))
sys.path.insert(0, str(REPO / "plugins/tamheed/db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

src, pkg = Path(sys.argv[1]).resolve(), sys.argv[2]
base = Path(tempfile.mkdtemp(prefix="drill238-"))
old = base / "b651"
tarfile.open(fileobj=io.BytesIO(subprocess.run(
    ["git", "-C", str(REPO), "archive", "v6.5.1", "plugins/tamheed"], capture_output=True).stdout)
).extractall(old)


def git(ws, *a):
    return subprocess.run(["git", *a], cwd=ws, capture_output=True, text=True).stdout.strip()


def clone(name):
    ws = base / name
    subprocess.run(["git", "clone", "-q", "-c", "core.autocrlf=false", str(src), str(ws)], check=True)
    return ws


def under651(ws, code):
    probe = (f"import sys, json\nsys.path.insert(0, r'{old / 'plugins/tamheed/server'}')\n"
             f"sys.path.insert(0, r'{old / 'plugins/tamheed/db'}')\nimport tamheed_server as srv\n"
             f"srv.PACKAGE_ROOT = __import__('pathlib').Path(r'{ws}')\n" + code)
    r = subprocess.run([sys.executable, "-I", "-c", probe], capture_output=True, text=True,
                       env={"SYSTEMROOT": os.environ.get("SYSTEMROOT", "")})
    return (r.stdout.strip() or r.stderr[-400:])


GATES = ("o = srv.package_open('%s'); r = srv.readiness_check('package') if o['ok'] else {}\n"
         "print(json.dumps({'open': o['ok'], 'ready': r.get('ready'), 'blocking': sorted(x['rule']"
         " for x in r.get('rules', []) if x['severity'] == 'blocking' and x['status'] == 'fail')}))\n"
         "srv.package_close() if o['ok'] else None\n" % pkg)


def equal_pre(ws, pre):
    diff = git(ws, "diff", "--stat", pre, "--", pkg)
    untracked = git(ws, "status", "--porcelain", "--untracked-files=all", "--", pkg)
    ignored = git(ws, "status", "--porcelain", "--ignored", "--", pkg)
    return {"diff_vs_pre": diff or "none", "status": untracked or "clean",
            "ignored": [x for x in ignored.splitlines() if x.startswith("!!")]}


pre = git(src, "rev-list", "--max-parents=0", "HEAD")
print("OBS PRE:", pre[:8], "| 6.5.1 at PRE:", under651(src, GATES) if False else "(read below)")

# (a) before the sync commit: run the sync, then checkout the data
a = clone("a")
subprocess.run(["git", "checkout", "-q", pre], cwd=a)
srv.PACKAGE_ROOT = a
srv.package_migrate(pkg, confirm=True)
print("OBS a.moved:", git(a, "status", "--porcelain").splitlines())
git(a, "checkout", "--", f"{pkg}/data")
print("OBS a.after checkout:", equal_pre(a, pre), "| 6.5.1:", under651(a, GATES))

# (b) after the commits, with a live Draft row and draft.html
b = clone("b")
srv.PACKAGE_ROOT = b
assert srv.package_open(pkg)["ok"]
d = srv.standup_report()
srv.package_close()
print("OBS b.draft:", d.get("ok"), d.get("report"), "| files:", git(b, "status", "--porcelain", "--ignored").splitlines())
git(b, "restore", f"--source={pre}", "--staged", "--worktree", "--", pkg)
print("OBS b.after restore:", equal_pre(b, pre))
print("OBS b.clean -nd:", git(b, "clean", "-nd", "--", pkg).splitlines())
git(b, "clean", "-fd", "--", pkg)
print("OBS b.after clean -fd:", equal_pre(b, pre))
print("OBS b.clean -ndX:", git(b, "clean", "-ndX", "--", pkg).splitlines())
print("OBS b.6.5.1:", under651(b, GATES))

# (c) revert
c = clone("c")
git(c, "-c", "user.name=m", "-c", "user.email=m@x.invalid", "revert", "--no-edit", f"{pre}..HEAD")
print("OBS c.after revert:", equal_pre(c, pre), "| 6.5.1:", under651(c, GATES))

# (d) the plugin alone, the data kept: a write, an export, close, reopen under 6.5.1
p = clone("p")
before = (p / pkg / "data" / "standup_reports.jsonl").read_bytes()
code = ("o = srv.package_open('%s'); w = srv.progress_update([{'entry': 'a note under 6.5.1',"
        " 'event_type': 'note', 'actor': 'agent:m'}]); e = srv.export_html(); srv.package_close()\n"
        "o2 = srv.package_open('%s'); v = srv.package_verify(); srv.package_close()\n"
        "print(json.dumps({'open': o['ok'], 'write': w['ok'], 'export': e['ok'], 'reopen': o2['ok'],"
        " 'dirty': v.get('dirty'), 'foreign': v.get('foreign')}))\n" % (pkg, pkg))
print("OBS p.6.5.1 write+export:", under651(p, code))
print("OBS p.standup_reports.jsonl unchanged:", before == (p / pkg / "data" / "standup_reports.jsonl").read_bytes(),
      "| csv/standup_reports.csv still there:", (p / pkg / "csv" / "standup_reports.csv").exists(),
      "| moved:", git(p, "status", "--porcelain").splitlines())
srv.PACKAGE_ROOT = p
assert srv.package_open(pkg)["ok"]
fwd = srv.standup_report()
print("OBS p.forward to 6.6.0:", fwd.get("ok"), fwd.get("report"), fwd.get("kind"), "| window:",
      fwd.get("window"), "| error:", (fwd.get("error") or "")[:120])
srv.standup_report(action="discard")
srv.package_close()

# (e) the delete case: remove standup_reports.jsonl, then draft under 6.6.0
e = clone("e")
(e / pkg / "data" / "standup_reports.jsonl").unlink()
srv.PACKAGE_ROOT = e
assert srv.package_open(pkg)["ok"]
again = srv.standup_report()
print("OBS e.after delete, next draft:", again.get("report"), "| first:", again.get("first"),
      "| committed RPT-001.html exists:", (e / pkg / "reports" / "RPT-001.html").exists())
srv.standup_report(action="discard")
srv.package_close()
shutil.rmtree(base, ignore_errors=True)
