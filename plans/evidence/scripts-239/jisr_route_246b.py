"""Plan 246b (R144): the field's own case on a throwaway copy of its package. Its newest report is
a correction of its first one. One withdrawal takes both, and a fresh first report is drafted
from today. Prints ids and list items only, never row text.

    env -u TAMHEED_HOOK_LOG python -I jisr_route_246b.py <package parent folder> <package dir>
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

R = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(R / "plugins/tamheed/server"), str(R / "plugins/tamheed/db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

src, pkg = Path(sys.argv[1]).resolve(), sys.argv[2]
work = Path(tempfile.mkdtemp(prefix="route246b-"))
shutil.copytree(src / pkg, work / pkg, ignore=shutil.ignore_patterns(".lock"))
srv.PACKAGE_ROOT = work
assert srv.package_open(pkg)["ok"]
rows = srv._CURRENT.conn.execute("SELECT id, lifecycle_status, supersedes FROM standup_reports"
                                 " ORDER BY id").fetchall()
print("OBS reports before:", rows)
newest = [r[0] for r in rows if r[1] == "Approved"][-1]
out = srv.standup_report(action="withdraw", report=newest,
                         confirm={"operator_confirm": True, "by": "human:op", "words": "start again"})
print("OBS withdraw:", out.get("ok"), out.get("reports"), out.get("error"))
again = srv.standup_report(utc_offset="+03:00")
blocked = [(i["id"], i.get("note")) for i in again.get("facts", {}).get("challenges", {})
           .get("blocked_work", {}).get("items", [])] if again.get("ok") else again.get("error")
print("OBS fresh draft:", again.get("report"), "first:", again.get("first"), "| blocked work:", blocked)
srv.standup_report(action="discard")
srv.package_close()
shutil.rmtree(work, ignore_errors=True)
