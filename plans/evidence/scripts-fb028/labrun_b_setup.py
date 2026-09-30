"""Plan 172, Run B setup: a scratch copy of the lab fixture, wired for headless sessions.
In-process through the engine (the same functions the MCP tools call): copy the fixture, write
the project note, emit the handoff (the CLAUDE.md note the hook reads at every session start),
remove the emitted standalone `.mcp.json` (W152: the session's server is the `--plugin-dir`
bundle; a second server on the same package would race for the lock), close.

    env -u TAMHEED_HOOK_LOG python labrun_b_setup.py <scratch dir>
"""
import json
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server")); sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

FIX = REPO / "evals" / "sample-results" / "lab-tracker"
ws = Path(sys.argv[1]).resolve() / "lab-run-B" / "ws"
assert not ws.exists(), "a fresh scratch folder each run"
shutil.copytree(FIX / "package", ws / "package")
shutil.copytree(FIX / "workspace", ws / "workspace")
srv.PACKAGE_ROOT = ws
o = srv.package_open("package")
assert o["ok"], o
print("OBS open.resume:", json.dumps({"handoff": o["resume"]["handoff"]["id"],
                                     "behind": o["resume"]["handoff_behind"]}))
(ws / "CLAUDE.md").write_text("# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n",
                              encoding="utf-8", newline="\n")
em = srv.handoff_emit(str(ws))
assert em["ok"], em
print("OBS emit:", json.dumps({k: em.get(k) for k in ("note", "mcp_json", "install_mode")})[:300])
mcp = ws / ".mcp.json"
print("OBS mcp_json_removed:", mcp.exists()); mcp.unlink(missing_ok=True)
c = srv.package_close()
assert c["ok"], c
print("OBS closed; lock:", (ws / "package" / "data" / ".lock").exists())
print("WS", ws)
