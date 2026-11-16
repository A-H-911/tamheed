"""Plan 247: replay a field package under the real 6.6.0 (from its tag) and under this branch,
on throwaway copies, and print what differs. Scratch only, never the original. Prints rule
names, counts and ids only, never row text.

    env -u TAMHEED_HOOK_LOG python -I replay_247.py <package parent folder> <package dir>
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

R = Path(__file__).resolve().parents[3]
src, pkg = Path(sys.argv[1]).resolve(), sys.argv[2]
base = Path(tempfile.mkdtemp(prefix="replay247-"))
old = base / "b660"
tarfile.open(fileobj=io.BytesIO(subprocess.run(
    ["git", "-C", str(R), "archive", "v6.6.0", "plugins/tamheed"], capture_output=True).stdout)
).extractall(old)

PROBE = r"""
import sys, json, collections
sys.path[:0] = [BUNDLE + '/plugins/tamheed/server', BUNDLE + '/plugins/tamheed/db']
import tamheed_server as srv
import standup_facts as F
srv.PACKAGE_ROOT = __import__('pathlib').Path(WS)
o = srv.package_open(PKG)
if not o['ok']:
    print(json.dumps({'open': False, 'error': o.get('error')})); raise SystemExit
g = srv.gate_run()
r = srv.readiness_check('package')
conn = srv._CURRENT.conn
prompts = conn.execute("SELECT id, kind, body FROM prompts WHERE lifecycle_status = 'Approved'").fetchall()
restated = collections.Counter()
for pid, kind, body in prompts:
    try:
        found = srv._restated_findings(pid + '.body', str(body or '').splitlines(), claims=kind == 'kickoff')
    except TypeError:                     # 6.6.0 has no claims argument
        found = srv._restated_findings(pid + '.body', str(body or '').splitlines())
    restated.update(f['kind'] + ('/labeled' if f.get('labeled') else '') for f in found)
blocked = sorted({b['id'] for b in F.blocked(conn)})
out = {'open': True, 'version': srv.server_info()['version'],
       'gates': {k: (v.get('status', v.get('pass')) if isinstance(v, dict) else v) for k, v in g['gates'].items()},
       'ready': r['ready'],
       'rules': {x['rule']: [x['severity'], x['status'], len(x.get('entities') or [])] for x in r['rules']},
       'restated': dict(restated), 'blocked': blocked,
       'lifted': dict(F.lifted(conn)) if hasattr(F, 'lifted') else None}
srv.package_close()
print(json.dumps(out))
"""


def run(bundle: Path, label: str) -> dict:
    ws = base / label
    shutil.copytree(src / pkg, ws / pkg, ignore=shutil.ignore_patterns(".lock"))
    code = (f"BUNDLE = r'{bundle}'\nWS = r'{ws}'\nPKG = '{pkg}'\n") + PROBE
    r = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True,
                       env={"SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
                            "PYTHONIOENCODING": "utf-8"})
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        return {"open": False, "error": (r.stderr or r.stdout)[-500:]}


a, b = run(old, "v660"), run(R, "v670")
print("OBS versions:", a.get("version"), "->", b.get("version"), "| open:", a.get("open"), b.get("open"),
      "|", a.get("error") or "", b.get("error") or "")
if a.get("open") and b.get("open"):
    print("OBS gates changed:", {k: (a["gates"].get(k), v) for k, v in b["gates"].items()
                                  if a["gates"].get(k) != v} or "none")
    print("OBS ready:", a["ready"], "->", b["ready"])
    rules = {k: (a["rules"].get(k), v) for k, v in b["rules"].items() if a["rules"].get(k) != v}
    rules.update({k: (v, None) for k, v in a["rules"].items() if k not in b["rules"]})
    print("OBS rules changed:", rules or "none")
    print("OBS restated:", a["restated"], "->", b["restated"])
    print("OBS blocked list:", a["blocked"], "->", b["blocked"])
    print("OBS free to start (6.7.0):", b["lifted"])
shutil.rmtree(base, ignore_errors=True)
