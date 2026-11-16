"""Plan 237: the way back. The real 6.5.1 code (from the tag, `git archive`) opens a store that
6.6.0 migrated and wrote (a recorded standup report among it), reads the gates, and closes. Run on
the scratch results of measure_briefs_660.py, never on a field folder.

    env -u TAMHEED_HOOK_LOG python wayback_660.py <scratch ws> <package dir>
"""
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ws, pkg = Path(sys.argv[1]).resolve(), sys.argv[2]
old = Path(tempfile.mkdtemp(prefix="tamheed-651-"))
blob = subprocess.run(["git", "-C", str(REPO), "archive", "v6.5.1", "plugins/tamheed"],
                      capture_output=True).stdout
tarfile.open(fileobj=io.BytesIO(blob)).extractall(old)
probe = f'''
import json, sys
sys.path.insert(0, r"{old / 'plugins/tamheed/server'}"); sys.path.insert(0, r"{old / 'plugins/tamheed/db'}")
import tamheed_server as srv
srv.PACKAGE_ROOT = __import__("pathlib").Path(r"{ws}")
o = srv.package_open("{pkg}")
out = {{"version": srv.server_info()["version"], "open": o["ok"], "error": (o.get("error") or "")[:200]}}
if o["ok"]:
    g = srv.gate_run(); r = srv.readiness_check("package")
    out.update(ready_gates=g.get("ready"), ready=r.get("ready"),
               blocking_fail=sorted(x["rule"] for x in r["rules"] if x["severity"] == "blocking"
                                    and x["status"] == "fail"),
               verify={{k: srv.package_verify().get(k) for k in ("verified", "dirty", "foreign")}})
    srv.package_close()
print(json.dumps(out))
'''
res = subprocess.run([sys.executable, "-I", "-c", probe], capture_output=True, text=True,
                     env={"PATH": "", "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", "")})
print("OBS 6.5.1:", res.stdout.strip()[:600] or res.stderr[-600:])
moved = subprocess.run(["git", "status", "--porcelain"], cwd=ws, capture_output=True,
                       text=True).stdout.split("\n")
print("OBS moved by 6.5.1 (open, read, close):", [m for m in moved if m.strip()])
