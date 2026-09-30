"""Plan 166's field measurement: on a fresh `git archive` copy of the field package, committed
into a scratch git repository, the 5.8.0 engine's FIRST export (the one-time re-flow) and the
NEXT export after one journal write - `git diff --numstat`, the patch's bytes, the added lines.

Run:  env -u TAMHEED_HOOK_LOG python export_diff.py <scratch dir> <bundle dir (.../plugins/tamheed)>
The field repo path is written below; change it for another project.
"""
# a second export on the ACMP copy after one journal write, with the 5.8.0 engine, in git:
# the real numstat and patch size of (a) the first export (the re-flow) and (b) the next one.
import subprocess, sys, shutil
from pathlib import Path
S = Path(sys.argv[1]); copy = S / "acmp-copy13"; tree = Path(sys.argv[2])
if copy.exists():
    raise SystemExit("copy exists")
copy.mkdir()
subprocess.run(["git", "-C", "C:/Users/ahammo/Repos/acmp", "archive", "HEAD", "tamheed-package"], check=True, stdout=open(S / "acmp13.tar", "wb"))
subprocess.run(["tar", "-x", "-C", str(copy), "-f", str(S / "acmp13.tar")], check=True)
def git(*a): return subprocess.run(["git", "-C", str(copy), *a], capture_output=True, check=True).stdout.decode("utf-8", "replace")
git("init", "-q"); git("add", "-A"); git("-c", "user.email=x@y", "-c", "user.name=x", "commit", "-q", "-m", "field head")
sys.path.insert(0, str(tree / "server")); sys.path.insert(0, str(tree / "db"))
import tamheed_server as srv
srv.PACKAGE_ROOT = copy
assert srv.package_open("tamheed-package")["ok"]
v = srv.package_verify(); print("verify before:", v["verified"], v.get("review_current"), v.get("review_exported_by"))
r = srv.export_html(); assert r["ok"], r
srv.package_close()
git("add", "-A"); git("-c", "user.email=x@y", "-c", "user.name=x", "commit", "-q", "-m", "first export on 5.8.0")
print("first export numstat:", git("diff", "--numstat", "HEAD~1", "HEAD", "--", "tamheed-package/review.html").strip())
print("first export patch bytes:", len(git("diff", "HEAD~1", "HEAD", "--", "tamheed-package/review.html").encode()))
print("csv changed:", git("diff", "--stat", "HEAD~1", "HEAD", "--", "tamheed-package/csv").strip() or "none")
assert srv.package_open("tamheed-package")["ok"]
w = srv.progress_update([{"entry": "a note written on the copy after the first 5.8.0 export, to measure the next export's diff", "actor": "agent:replay"}]); assert w["ok"], w
r = srv.export_html(); assert r["ok"], r
srv.package_close()
git("add", "-A"); git("-c", "user.email=x@y", "-c", "user.name=x", "commit", "-q", "-m", "second export")
print("second export numstat:", git("diff", "--numstat", "HEAD~1", "HEAD", "--", "tamheed-package/review.html").strip())
print("second export patch bytes:", len(git("diff", "HEAD~1", "HEAD", "--", "tamheed-package/review.html").encode()))
p = git("diff", "HEAD~1", "HEAD", "--", "tamheed-package/review.html")
added = [l for l in p.split("\n") if l.startswith("+") and not l.startswith("+++")]
print("second export added lines:", len(added), "added bytes:", sum(len(l.encode()) for l in added), "max line:", max(len(l) for l in added))
