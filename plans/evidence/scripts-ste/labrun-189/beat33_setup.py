"""Plan 189, lab beat 33 setup: a scratch copy of the lab fixture, wired for the headless
`/tamheed:ste-rewrite` session (the beat's scratch phase). In-process through the engine: copy the
fixture, write the project note, emit the handoff with refresh_stock (the 5.9.0 guide and the v6
note the hook reads at session start), remove the emitted standalone `.mcp.json` (the session's
server is the `--plugin-dir` bundle), close. Nothing here touches the fixture.

    env -u TAMHEED_HOOK_LOG python beat33_setup.py <scratch dir>
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

FIX = REPO / "evals" / "sample-results" / "lab-tracker"
ws = Path(sys.argv[1]).resolve() / "lab-run-33" / "ws"
assert not ws.exists(), "a fresh scratch folder each run"
shutil.copytree(FIX / "package", ws / "package")
shutil.copytree(FIX / "workspace", ws / "workspace")
srv.PACKAGE_ROOT = ws
assert srv.server_info()["version"] == "5.9.0", srv.server_info()["version"]
o = srv.package_open("package")
assert o["ok"], o
print("OBS open.resume:", json.dumps({"handoff": o["resume"]["handoff"]["id"],
                                     "behind": o["resume"]["handoff_behind"]}))
rule = next(r for r in srv.readiness_check("package")["rules"] if r["rule"] == "prose-plain-english")
print("OBS prose-plain-english.before:", json.dumps({k: rule.get(k) for k in ("status", "counts", "population")})[:600])
print("OBS prose-plain-english.entities:", json.dumps(rule.get("entities"))[:1500])
(ws / "CLAUDE.md").write_text("# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n",
                              encoding="utf-8", newline="\n")
em = srv.handoff_emit(str(ws), refresh_stock=True)
assert em["ok"], em
print("OBS emit:", json.dumps({"refreshed": em["prompt_library"]["refreshed"], "install_mode": em.get("install_mode")})[:300])
note = (ws / "package" / "CLAUDE.md").read_text(encoding="utf-8")
print("OBS note.marker:", "tamheed:note v6" in note, "| first sentence:",
      next((l for l in note.splitlines() if "Tamheed package for this project" in l), "")[:120])
mcp = ws / ".mcp.json"
print("OBS mcp_json_removed:", mcp.exists()); mcp.unlink(missing_ok=True)
c = srv.package_close()
assert c["ok"], c
print("OBS closed; lock:", (ws / "package" / "data" / ".lock").exists())
print("WS", ws)
