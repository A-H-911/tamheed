"""Plan 246: the way back after a withdrawal. The working-tree engine records two reports and
withdraws the newest. Then the real 6.6.0 (from its tag) opens the store, checks it, and drafts:
which id does it take? Scratch only. Prints verdicts and ids.

    env -u TAMHEED_HOOK_LOG python -I wayback_246.py
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
sys.path[:0] = [str(R / "plugins/tamheed/server"), str(R / "plugins/tamheed/db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

base = Path(tempfile.mkdtemp(prefix="wayback246-"))
old = base / "b660"
tarfile.open(fileobj=io.BytesIO(subprocess.run(
    ["git", "-C", str(R), "archive", "v6.6.0", "plugins/tamheed"], capture_output=True).stdout)
).extractall(old)
work = base / "ws"
work.mkdir()
srv.PACKAGE_ROOT = work
assert srv.package_create("pkg", "Pkg", "rnd")["ok"]
words = {"headline": "The export works.", "did": "We finished the export.", "challenges": "None.",
         "next": "We start the import.", "colour": "green"}
confirm = {"operator_confirm": True, "by": "human:op", "words": "record it", "colour": "green"}
for _ in range(2):
    assert srv.standup_report(utc_offset="+03:00")["ok"]
    assert srv.standup_report(narrative=words)["ok"]
    assert srv.standup_report(action="record", confirm=confirm)["ok"]
out = srv.standup_report(action="withdraw", report="RPT-002",
                         confirm={"operator_confirm": True, "by": "human:op", "words": "back"})
print("OBS 6.7.0 withdraw:", out.get("ok"), out.get("report"), out.get("error"))
srv.package_close()
probe = (f"import sys, json\nsys.path[:0] = [r'{old / 'plugins/tamheed/server'}',"
         f" r'{old / 'plugins/tamheed/db'}']\nimport tamheed_server as srv\n"
         f"srv.PACKAGE_ROOT = __import__('pathlib').Path(r'{work}')\n"
         "o = srv.package_open('pkg'); v = srv.package_verify() if o['ok'] else {}\n"
         "d = srv.standup_report() if o['ok'] else {}\n"
         "print(json.dumps({'version': srv.server_info()['version'], 'open': o['ok'],"
         " 'error': o.get('error'), 'verified': v.get('verified'), 'dirty': v.get('dirty'),"
         " 'draft': d.get('report'), 'draft_error': d.get('error')}))\n"
         "srv.package_close() if o['ok'] else None\n")
r = subprocess.run([sys.executable, "-I", "-c", probe], capture_output=True, text=True,
                   env={"SYSTEMROOT": os.environ.get("SYSTEMROOT", "")})
print("OBS 6.6.0 on the store:", r.stdout.strip() or r.stderr[-600:])
shutil.rmtree(base, ignore_errors=True)
