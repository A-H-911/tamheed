"""Plan 253: what the 6.8.0 upgrade does to a field package, measured on a scratch git copy of
the field's committed tree, under a chosen bundle (the v6.7.0 tag or this checkout). From
scripts-239/measure_247.py, plus a first-report standup draft whose stored facts are measured.
Prints names, counts and sizes only: no row text.

    env -u TAMHEED_HOOK_LOG python -I measure_253.py <bundle dir> <tree: git repo or .zip> <package dir> <scratch>

A .zip is the field's own export of its committed tree (the Jisr export); it is unpacked into a
new git repository first. A git repository is only read (`git archive HEAD`).
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

bundle, tree, pkg, scratch = (Path(sys.argv[1]).resolve(), Path(sys.argv[2]), sys.argv[3],
                              Path(sys.argv[4]).resolve())
sys.path[:0] = [str(bundle / "server"), str(bundle / "db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

ws = scratch / "ws"
if ws.exists():
    shutil.rmtree(ws)
ws.mkdir(parents=True)
KEEP = ("CLAUDE.md", ".gitignore", ".claude/settings.json")
if tree.suffix == ".zip":
    with zipfile.ZipFile(tree) as z:
        names = [n for n in z.namelist() if n.startswith(pkg + "/") or n in KEEP]
        z.extractall(ws, names)
    head = "zip"
else:
    listed = subprocess.run(["git", "-C", str(tree), "ls-files", *KEEP], capture_output=True,
                            text=True).stdout.split()
    blob = subprocess.run(["git", "-C", str(tree), "archive", "HEAD", pkg, *listed],
                          capture_output=True, check=True).stdout
    tarfile.open(fileobj=io.BytesIO(blob)).extractall(ws)
    head = subprocess.run(["git", "-C", str(tree), "rev-parse", "--short=8", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
for args in (["init", "-q"], ["config", "core.autocrlf", "false"], ["add", "-A"],
             ["-c", "user.name=m", "-c", "user.email=m@x.invalid", "commit", "-qm", "PRE"]):
    subprocess.run(["git", *args], cwd=ws, check=True)


def moved():
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ws,
                         capture_output=True, text=True).stdout.splitlines()
    return [line[3:] for line in out]


def obs(key, value):
    print(f"OBS {key}: {json.dumps(value, default=str)[:600]}")


obs("field head", head)
obs("engine", {k: srv.server_info()[k] for k in ("version", "migrations_head", "schema_version")})
srv.PACKAGE_ROOT = ws
o = srv.package_open(pkg)
obs("open", {"ok": o["ok"], "error": o.get("error")})
g, r = srv.gate_run(), srv.readiness_check("package")
obs("reading", {"gate_ready": g["ready"], "ready": r["ready"],
                "blocking_fail": sorted(x["rule"] for x in r["rules"]
                                        if x["severity"] == "blocking" and x["status"] == "fail")})
obs("moved by the open", moved())
em = srv.handoff_emit(str(ws), refresh_stock=True)
obs("emit", {"ok": em["ok"], "restated": len(em.get("restated_content") or []),
             "library": {k: v for k, v in (em.get("prompt_library") or {}).items()
                         if k in ("refreshed", "unchanged")}})
srv.export_html()
v = srv.package_verify()
obs("verify", {k: v.get(k) for k in ("verified", "dirty", "review_current", "review_exported_by")})
obs("moved by emit and export", moved())
c = srv._CURRENT.conn
obs("reports before the draft", c.execute(
    "SELECT COUNT(*) FROM standup_reports").fetchone()[0])
d = srv.standup_report(utc_offset="+03:00")
obs("draft", {"ok": d.get("ok"), "error": d.get("error"), "kind": d.get("kind"),
              "warnings": len(d.get("warnings") or []),
              "suggest": (d.get("plan_summary") or {}).get("suggest")})
row = c.execute("SELECT id, LENGTH(facts) FROM standup_reports WHERE lifecycle_status = 'Draft'"
                " ORDER BY id DESC LIMIT 1").fetchone()
obs("draft row facts bytes", row)
srv.package_close()
page = ws / pkg / "reports" / "draft.html"
obs("draft page bytes", page.stat().st_size if page.exists() else None)
