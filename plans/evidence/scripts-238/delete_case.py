"""Plan 238: the delete case, measured. Clone a measure_route.py result, remove
standup_reports.jsonl, draft with an offset, and say whether the draft is a first report RPT-001
while the committed reports/RPT-001.html exists. Scratch only.

    env -u TAMHEED_HOOK_LOG python -I delete_case.py <measured ws> <package dir>
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "plugins/tamheed/server"))
sys.path.insert(0, str(REPO / "plugins/tamheed/db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

src, pkg = Path(sys.argv[1]).resolve(), sys.argv[2]
base = Path(tempfile.mkdtemp(prefix="del238-"))
ws = base / "e"
subprocess.run(["git", "clone", "-q", "-c", "core.autocrlf=false", str(src), str(ws)], check=True)
(ws / pkg / "data" / "standup_reports.jsonl").unlink()
srv.PACKAGE_ROOT = ws
print("OBS open:", srv.package_open(pkg)["ok"])
d = srv.standup_report(utc_offset="+03:00")
print("OBS draft:", d.get("ok"), d.get("report"), "| first:", d.get("first"),
      "| error:", (d.get("error") or "")[:160])
print("OBS committed RPT-001.html exists:", (ws / pkg / "reports" / "RPT-001.html").exists())
srv.standup_report(action="discard")
srv.package_close()
shutil.rmtree(base, ignore_errors=True)
