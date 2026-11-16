"""Plan 247: the recorded lab-tracker fixture follows the 6.7.0 stamp through the engine's own
tools, never a hand edit (the pattern of scripts-237/refresh_lab_660.py). No registry sync: the
release adds no family. `handoff_emit(..., refresh_stock=true)` to a scratch target rewrites the
stock guide with the 6.7.0 title line, and `export_html` writes the page with the 6.7.0 meta.
In-process, so `_WIRE_ROOT` is off and nothing is wired into the fixture tree. Run from the
repository root:

    env -u TAMHEED_HOOK_LOG python plans/evidence/scripts-239/refresh_lab_670.py
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
RELEASE = "6.7.0"


def obs(key, value):
    print(f"OBS {key} {json.dumps(value, ensure_ascii=False, default=str)[:600]}")


assert srv.server_info()["version"] == RELEASE, srv.server_info()["version"]
assert srv._WIRE_ROOT is False
FIX = REPO / "evals" / "sample-results" / "lab-tracker"
PKG = FIX / "package"
had_note = (PKG / "CLAUDE.md").exists()
had_root = (FIX / "CLAUDE.md").exists()
srv.PACKAGE_ROOT = FIX
o = srv.package_open("package")
assert o["ok"], o
scratch = Path(tempfile.mkdtemp(prefix="tamheed-247-"))
target = scratch / "target"
target.mkdir()
(target / "CLAUDE.md").write_text("# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n",
                                  encoding="utf-8", newline="\n")
try:
    em = srv.handoff_emit(str(target), refresh_stock=True)
    assert em["ok"], em
    lib = em["prompt_library"]
    obs("emit.library", {k: v for k, v in lib.items() if k in ("written", "refreshed", "unchanged", "leftovers")})
    assert f"tamheed v{RELEASE}" in (PKG / "README.md").read_text(encoding="utf-8")
    ex = srv.export_html()
    assert ex["ok"], ex
    page = (PKG / "review.html").read_text(encoding="utf-8")
    assert f'<meta name="tamheed-version" content="{RELEASE}">' in page[:4096]
    v = srv.package_verify()
    obs("verify", {k: v.get(k) for k in ("verified", "dirty", "foreign", "review_current", "review_exported_by")})
    obs("gate_run.ready", srv.gate_run()["ready"])
finally:
    srv.package_close()
    shutil.rmtree(scratch, ignore_errors=True)
assert not (PKG / "data" / ".lock").exists()
if not had_note and (PKG / "CLAUDE.md").exists():
    (PKG / "CLAUDE.md").unlink()                      # the fixture never tracked the package note
    obs("fixture.package_note_removed", True)
assert (FIX / "CLAUDE.md").exists() == had_root      # nothing wired into the fixture tree
print("REFRESH-247-DONE")
