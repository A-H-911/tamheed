"""Plan 172, Run A2 setup: the operator's move of the planned package INTO the executor repo.
The plugin's server resolves the package under the project directory (`--package-dir
${CLAUDE_PROJECT_DIR}`), so a package left in the planner workspace is unreachable from the
executor's session; the field's layout is the package inside the project repo (ACMP). In-process:
move `plan/lab-tracker` to `exec/lab-tracker`, re-emit the note from its new root (the note's
package path follows), remove the standalone `.mcp.json` (W152), close, commit the package and
the note in the executor repo as the handoff commit (`against_commit` needs real shas).

    env -u TAMHEED_HOOK_LOG python labrun_a2_setup.py <scratch dir>
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server")); sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

root = Path(sys.argv[1]).resolve() / "lab-run-A"
plan, ex = root / "plan", root / "exec"
assert (plan / "lab-tracker" / "data").exists() and not (ex / "lab-tracker").exists()
shutil.move(str(plan / "lab-tracker"), str(ex / "lab-tracker"))
srv.PACKAGE_ROOT = ex
o = srv.package_open("lab-tracker")
assert o["ok"], o
print("OBS open.resume:", json.dumps({"handoff": (o["resume"]["handoff"] or {}).get("id"),
                                     "behind": o["resume"]["handoff_behind"]}))
em = srv.handoff_emit(str(ex))
assert em["ok"], em
note = (ex / "CLAUDE.md").read_text(encoding="utf-8")
print("OBS note names exec root:", str(ex) in note)
(ex / ".mcp.json").unlink()
c = srv.package_close()
assert c["ok"], c
g = ["git", "-C", str(ex), "-c", "user.name=lab", "-c", "user.email=lab@example.invalid"]
subprocess.run(g + ["add", "-A"], check=True)
subprocess.run(g + ["commit", "-q", "-m", "handoff: the lab-tracker package and the Tamheed note received"], check=True)
print("OBS handoff commit:", subprocess.run(g + ["rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip())
