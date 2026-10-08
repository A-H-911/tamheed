"""Plan 212, lab beat 35 setup: a fresh repository from the lab seed with NO CLAUDE.md, for the
headless session in which a real agent creates the package (the served process wires the root
and the package file), then a second process whose SessionStart hook must find the package, then
a third that approves a kickoff row and emits. Nothing here touches the lab or the fixtures, and
nothing here writes a CLAUDE.md: that is what the beat measures.

    env -u TAMHEED_HOOK_LOG python beat35_setup.py <scratch dir>
"""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server")); sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ws = Path(sys.argv[1]).resolve() / "lab-run-35" / "ws"
assert not ws.exists(), "a fresh scratch folder each run"
ws.mkdir(parents=True)
for f in ("tracker.py", "test_tracker.py"):
    (ws / f).write_bytes((REPO / "lab" / "seed" / f).read_bytes())
(ws / "brief.md").write_bytes((REPO / "lab" / "brief.md").read_bytes())
subprocess.run(["git", "init", "-q", "."], cwd=ws, check=True)
subprocess.run(["git", "add", "-A"], cwd=ws, check=True)
subprocess.run(["git", "-c", "user.name=lab", "-c", "user.email=lab@example.invalid",
                "commit", "-q", "-m", "seed"], cwd=ws, check=True)
print("OBS files:", sorted(p.name for p in ws.iterdir() if p.name != ".git"))
print("OBS root.CLAUDE.md.exists:", (ws / "CLAUDE.md").exists())
print("OBS root.AGENTS.md.exists:", (ws / "AGENTS.md").exists())
print("OBS in-process.wire_root:", srv._WIRE_ROOT)          # False: this process serves nothing
print("OBS bundle.version:", srv.server_info()["version"])
print("WS", ws)
print(json.dumps({"ws": str(ws)}))
