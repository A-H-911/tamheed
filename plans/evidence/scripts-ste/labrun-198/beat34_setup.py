"""Plan 198, lab beat 34 setup: a scratch copy of the lab fixture, wired for the headless session
in which a real agent drives `package_migrate` (preview, STOP, confirm on the operator's words),
approves the kickoff row, emits, exports and hands off. Nothing is emitted here: the fixture's
v6 note is what the hook reads at session start (a v6 note still resumes under the 6.0 server).
Nothing here touches the fixture.

    env -u TAMHEED_HOOK_LOG python beat34_setup.py <scratch dir>
"""
import json
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server")); sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
FIX = REPO / "evals" / "sample-results" / "lab-tracker"
ws = Path(sys.argv[1]).resolve() / "lab-run-34" / "ws"
assert not ws.exists(), "a fresh scratch folder each run"
shutil.copytree(FIX / "package", ws / "package")
shutil.copytree(FIX / "workspace", ws / "workspace")
(ws / "CLAUDE.md").write_text("# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n",
                              encoding="utf-8", newline="\n")
srv.PACKAGE_ROOT = ws
assert srv.server_info()["version"] == "6.0.0", srv.server_info()["version"]
note_path = ws / "package" / "CLAUDE.md"
note = note_path.read_text(encoding="utf-8") if note_path.exists() else ""
print("OBS note.before:", json.dumps({"exists": note_path.exists(), "v6": "tamheed:note v6" in note,
                                      "v7": "tamheed:note v7" in note}))
print("OBS prompts.folder.before:", sorted(q.name for q in (ws / "package" / "prompts").iterdir()))
o = srv.package_open("package")
assert o["ok"], o
info = srv.server_info()
print("OBS open:", json.dumps({"schema_version": info["schema_version"], "entry_point": info["package"]["entry_point"],
                              "handoff": o["resume"]["handoff"]["id"], "behind": o["resume"]["handoff_behind"]}))
g = srv.gate_run()["gates"]["G-SET"]
print("OBS gset.before.migrate:", json.dumps(g))   # the registry has no `prompt` row yet: vacuous
print("OBS prompt.rows.before:", srv.entity_query("prompt", limit=5)["total"])
c = srv.package_close()
assert c["ok"], c
print("OBS closed; lock:", (ws / "package" / "data" / ".lock").exists())
print("WS", ws)
