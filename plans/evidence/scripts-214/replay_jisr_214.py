"""Plan 214: replay the engine over a scratch COPY of the field's own package (the jisr planning
package, tamheed 6.2.0), never over the repository itself. Copies `tamheed-package` to a temp
folder, opens it in-process (`_WIRE_ROOT` off, so nothing is wired into the copy's root), runs
`gate_run` and `readiness_check("package")`, closes, deletes the copy. With the label `head` the
server is HEAD's (`git show`), loaded from a temp copy of the bundle, so the two runs can follow
each other on one working tree. Expected: HEAD fails G-COMPLETE on PE-011 alone, the fixed engine
passes it with G-SET unchanged.

    env -u TAMHEED_HOOK_LOG python plans/evidence/scripts-214/replay_jisr_214.py head
    env -u TAMHEED_HOOK_LOG python plans/evidence/scripts-214/replay_jisr_214.py fixed
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
label = sys.argv[1] if len(sys.argv) > 1 else "run"
tmp = Path(tempfile.mkdtemp(prefix="replay214-"))
bundle = REPO / "plugins" / "tamheed"
if label == "head":
    bundle = tmp / "bundle"
    shutil.copytree(REPO / "plugins" / "tamheed", bundle)
    head = subprocess.run(["git", "show", "HEAD:plugins/tamheed/server/tamheed_server.py"], cwd=REPO,
                          capture_output=True, text=True, encoding="utf-8", check=True).stdout
    (bundle / "server" / "tamheed_server.py").write_text(head, encoding="utf-8", newline="\n")
sys.path.insert(0, str(bundle / "server"))
sys.path.insert(0, str(bundle / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
print(f"[{label}] server module: {Path(srv.__file__).resolve()}")
SRC = Path(r"C:\Users\ahammo\Repos\jisr\tamheed-package")


def names(fails):
    return sorted({str(f.get("id", f)) if isinstance(f, dict) else str(f) for f in fails})


try:
    shutil.copytree(SRC, tmp / "tamheed-package")
    srv.PACKAGE_ROOT = tmp
    out = srv.package_open("tamheed-package")
    if not out.get("ok"):
        print(f"[{label}] open refused on the copy:", json.dumps(out, ensure_ascii=False)[:300])
        print(f"[{label}] unlock on the COPY:", srv.package_unlock("tamheed-package", confirm=True).get("ok"))
        out = srv.package_open("tamheed-package")
    assert out.get("ok"), out
    print(f"[{label}] opened the copy: package {out.get('package')}, wiring {out.get('wiring')},"
          f" half {(out.get('resume') or {}).get('half')}")
    g = srv.gate_run()
    print(f"[{label}] ready={g['ready']}")
    for gate, info in g["gates"].items():
        if gate == "audit_evidence":
            continue
        fails = info.get("failures", [])
        print(f"[{label}] {gate}={info['status']}" + (f" failures={names(fails)}" if fails else ""))
        if gate == "G-COMPLETE":
            for f in fails:
                print(f"[{label}]   {json.dumps(f, ensure_ascii=False)}")
    rules = {r["rule"]: r for r in srv.readiness_check("package")["rules"]}
    co = rules.get("clarifications-open", {})
    print(f"[{label}] clarifications-open={co.get('status')} entities={co.get('entities')}")
    srv.package_close()
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(f"[{label}] copy removed; jisr untouched")
