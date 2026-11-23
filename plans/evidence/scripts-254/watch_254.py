"""Plan 254: a fixed watch list outside the scratch folder, hashed before and after each step.

    python -I watch_254.py snap <name>        writes snapshots/<name>.json beside this script
    python -I watch_254.py diff <a> <b>       prints what changed between two snapshots

Folders are hashed file by file (name, size, sha256). Missing paths are recorded as missing.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

HOME = Path.home()
REPO = Path(__file__).resolve().parents[3]
WATCH = [HOME / ".claude" / n for n in ("CLAUDE.md", "settings.json", "settings.local.json", "skills", "commands",
                                         "agents", "hooks")] + [
    HOME / ".claude" / "plugins" / "installed_plugins.json", HOME / ".claude" / "plugins" / "known_marketplaces.json",
    HOME / ".cache" / "graphify-queries.log", HOME / ".cache" / "graphify", HOME / ".graphify", HOME / ".local" / "bin",
    HOME / "AppData" / "Roaming" / "uv" / "tools" / "graphifyy", HOME / ".gitconfig", HOME / ".config" / "git",
    # ~/.codex holds a running app's own databases (they changed in a control run with nothing running),
    # so only the files an installer writes are watched there.
    HOME / ".agents", HOME / ".gemini", HOME / ".cursor", HOME / ".kiro", HOME / ".pi",
    *(HOME / ".codex" / n for n in ("AGENTS.md", "config.toml", "hooks.json", "skills", "prompts")),
    REPO / ".git" / "config", REPO / ".git" / "hooks", REPO / ".claude" / "settings.json", REPO / ".gitattributes",
    REPO / ".gitignore", REPO / "CLAUDE.md", REPO / "AGENTS.md", REPO / "graphify-out", REPO / ".graphify",
]
# The snapshots list file names under the operator's home, so they never live in the (public) repository:
# G254_SNAPS names a private folder (by default one under the operator's ~/.claude, outside any repository).
SNAPS = Path(os.environ.get("G254_SNAPS", str(Path.home() / ".claude" / "plans" / "graphify-254-private" / "snapshots")))


def digest(p: Path) -> str:
    h = hashlib.sha256()
    try:
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except OSError as exc:  # a file another program holds locked: record that, not a hash
        return f"unreadable:{exc.errno}"
    return h.hexdigest()


def snap(name: str) -> None:
    out: dict[str, str] = {}
    for root in WATCH:
        if not root.exists():
            out[str(root)] = "missing"
        elif root.is_file():
            out[str(root)] = f"{root.stat().st_size}:{digest(root)}"
        else:
            files = [p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
            out[str(root)] = f"dir:{len(files)}"
            for p in files:
                out[str(p)] = f"{p.stat().st_size}:{digest(p)}"
    SNAPS.mkdir(exist_ok=True)
    (SNAPS / f"{name}.json").write_text(json.dumps(out, indent=0, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{name}: {len(out)} entries")


def diff(a: str, b: str) -> None:
    x = json.loads((SNAPS / f"{a}.json").read_text(encoding="utf-8"))
    y = json.loads((SNAPS / f"{b}.json").read_text(encoding="utf-8"))
    changed = [(k, x.get(k), y.get(k)) for k in sorted(set(x) | set(y)) if x.get(k) != y.get(k)]
    for k, old, new in changed:
        print(f"CHANGED {k}: {old} -> {new}")
    print(f"{len(changed)} change(s) between {a} and {b}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"snap": lambda: snap(sys.argv[2]), "diff": lambda: diff(sys.argv[2], sys.argv[3])}[sys.argv[1]]()
