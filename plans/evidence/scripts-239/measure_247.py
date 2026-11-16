"""Plan 247: what the 6.7.0 upgrade does to a field package, measured on a scratch git copy of
the field's committed tree (`git archive`, so the field repository is only read). Under this
branch it opens the package, reads the gates and readiness, refreshes the stock guide, exports
the review page, verifies, and lists the files that moved. Prints names and counts only.

    env -u TAMHEED_HOOK_LOG python -I measure_247.py <field repo> <package dir> <scratch>
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

R = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(R / "plugins/tamheed/server"), str(R / "plugins/tamheed/db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

field, pkg, scratch = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]).resolve()
ws = scratch / "ws"
if ws.exists():
    shutil.rmtree(ws)
ws.mkdir(parents=True)
listed = subprocess.run(["git", "-C", str(field), "ls-files", "CLAUDE.md", ".gitignore",
                         ".claude/settings.json"], capture_output=True, text=True).stdout.split()
tarfile.open(fileobj=io.BytesIO(subprocess.run(["git", "-C", str(field), "archive", "HEAD", pkg,
                                                *listed], capture_output=True).stdout)).extractall(ws)
for args in (["init", "-q"], ["config", "core.autocrlf", "false"], ["add", "-A"],
             ["-c", "user.name=m", "-c", "user.email=m@x.invalid", "commit", "-qm", "PRE"]):
    subprocess.run(["git", *args], cwd=ws, check=True)
head = subprocess.run(["git", "-C", str(field), "rev-parse", "--short=8", "HEAD"],
                      capture_output=True, text=True).stdout.strip()


def moved():
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ws,
                         capture_output=True, text=True).stdout.splitlines()
    return [line[3:] for line in out]


def obs(key, value):
    print(f"OBS {key}: {json.dumps(value, default=str)[:500]}")


obs("field head", head)
obs("engine", {k: srv.server_info()[k] for k in ("version", "migrations_head", "schema_version")})
srv.PACKAGE_ROOT = ws
o = srv.package_open(pkg)
obs("open", {"ok": o["ok"], "error": o.get("error")})
g, r = srv.gate_run(), srv.readiness_check("package")
obs("reading", {"gate_ready": g["ready"], "ready": r["ready"],
                "blocking_fail": sorted(x["rule"] for x in r["rules"]
                                        if x["severity"] == "blocking" and x["status"] == "fail"),
                "blocks_lifted": next((x["status"] for x in r["rules"]
                                       if x["rule"] == "blocks-lifted"), "not emitted")})
obs("moved by the open", moved())
em = srv.handoff_emit(str(ws), refresh_stock=True)
obs("emit", {"ok": em["ok"], "restated": len(em.get("restated_content") or []),
             "library": {k: v for k, v in (em.get("prompt_library") or {}).items()
                         if k in ("refreshed", "unchanged")}})
ex = srv.export_html()
v = srv.package_verify()
obs("verify", {k: v.get(k) for k in ("verified", "dirty", "review_current", "review_exported_by")})
srv.package_close()
obs("moved by emit and export", moved())
