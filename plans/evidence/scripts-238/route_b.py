"""Plan 238, route B after the tag: the plugin forward (6.5.1 -> 6.6.0) and back (#v6.5.1), in a
SEPARATE configuration folder (CLAUDE_CONFIG_DIR) and a scratch repository. The machine's own plugin
records are hashed before and after; they must not move.

    python route_b.py <scratch>
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

scratch = Path(sys.argv[1]).resolve() / "route-b"
if scratch.exists():
    shutil.rmtree(scratch)
cfg, repo = scratch / "cfg", scratch / "repo"
cfg.mkdir(parents=True)
repo.mkdir()
subprocess.run(["git", "init", "-q"], cwd=repo)
real = Path.home() / ".claude" / "plugins"


def digest_real():
    h = hashlib.sha256()
    for name in ("known_marketplaces.json", "installed_plugins.json"):
        p = real / name
        h.update(p.read_bytes() if p.exists() else b"-")
    return h.hexdigest()[:16]


env = dict(os.environ, CLAUDE_CONFIG_DIR=str(cfg))
env.pop("TAMHEED_HOOK_LOG", None)
CLAUDE = shutil.which("claude") or "claude"


def run(*args):
    r = subprocess.run([CLAUDE, "plugin", *args], cwd=repo, env=env, capture_output=True, text=True)
    out = " ".join((r.stdout + r.stderr).split())
    print(f"OBS $ claude plugin {' '.join(args)} -> [{r.returncode}] {out[:240]}")
    return out


def version():
    out = subprocess.run([CLAUDE, "plugin", "list", "--json"], cwd=repo, env=env,
                         capture_output=True, text=True).stdout
    try:
        rows = json.loads(out)
        rows = rows if isinstance(rows, list) else rows.get("plugins", [])
        return [(r.get("version"), r.get("scope")) for r in rows if "tamheed" in json.dumps(r)]
    except ValueError:
        return out[:200]


def settings():
    p = repo / ".claude" / "settings.json"
    if not p.exists():
        return None
    m = json.loads(p.read_text(encoding="utf-8")).get("extraKnownMarketplaces", {}).get("tamheed", {})
    return m.get("source")


before = digest_real()
print("OBS real records before:", before)
run("marketplace", "add", "A-H-911/tamheed#v6.5.1", "--scope", "project")
run("install", "tamheed@tamheed", "--scope", "project")
print("OBS start:", version(), "| settings source:", settings())
# a pinned repository: does an update move it?
run("marketplace", "update", "tamheed")
run("update", "tamheed@tamheed", "--scope", "project")
print("OBS pinned, after update:", version(), "| settings source:", settings())
# forward: follow releases again, then the two update commands
run("marketplace", "add", "A-H-911/tamheed", "--scope", "project")
run("marketplace", "update", "tamheed")
run("update", "tamheed@tamheed", "--scope", "project")
print("OBS forward:", version(), "| settings source:", settings())
# back: the pin, then the two update commands
run("marketplace", "add", "A-H-911/tamheed#v6.5.1", "--scope", "project")
run("marketplace", "update", "tamheed")
run("update", "tamheed@tamheed", "--scope", "project")
print("OBS back:", version(), "| settings source:", settings())
after = digest_real()
print("OBS real records after:", after, "| unchanged:", before == after)
