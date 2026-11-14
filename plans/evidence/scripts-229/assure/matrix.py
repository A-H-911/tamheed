"""The compatibility matrix of the 6.5.0 field assurance, on scratch COPIES of a real package.

{6.4.0 code, 6.5.0 code} x {store as it is, migrated store} x {idle open and close, one write}.
Each cell runs in its own process. The whole copied tree is hashed before and after, so a file
that moves is named. Prints names of files, ids, statuses and counts. No text of a row.

Usage: python -I matrix.py <v640 bundle> <v650 bundle> <package dir> <scratch dir>
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

old, new, source, scratch = (Path(a) for a in sys.argv[1:5])
name = source.name
worker = Path(__file__).with_name("worker.py")


def tree(root: Path) -> dict:
    return {str(p.relative_to(root)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def diff(before: dict, after: dict) -> dict:
    return {"added": sorted(set(after) - set(before)), "removed": sorted(set(before) - set(after)),
            "changed": sorted(k for k in before if k in after and before[k] != after[k])}


def copy(label: str, origin: Path) -> Path:
    target = scratch / label
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(origin, target / name,
                    ignore=shutil.ignore_patterns(".lock", "*.writing", "*.tmp", ".git"))
    return target


def run(bundle: Path, root: Path, action: str) -> dict:
    done = subprocess.run([sys.executable, "-I", str(worker), str(bundle), str(root), name, action],
                          capture_output=True, text=True, encoding="utf-8")
    line = (done.stdout.strip().splitlines() or ["{}"])[-1]
    try:
        return json.loads(line)
    except ValueError:
        return {"unreadable": (done.stdout + done.stderr)[-400:]}


def cell(label: str, bundle: Path, origin: Path, action: str) -> tuple[dict, Path]:
    root = copy(label, origin)
    before = tree(root)
    result = run(bundle, root, action)
    moved = diff(before, tree(root))
    short = {k: (v if len(v) <= 6 else v[:6] + [f"... +{len(v) - 6}"]) for k, v in moved.items() if v}
    keep = {k: result.get(k) for k in ("version", "open_ok", "open_error", "write_ok", "write_error",
                                       "ok", "error", "report", "backup", "gate_ready", "rules",
                                       "blocking_fail", "verify", "close_ok", "close_error", "raised",
                                       "unreadable") if result.get(k) not in (None, "", [], {})}
    print(f"\n## {label}\n{json.dumps(keep, sort_keys=True)[:900]}\nfiles moved: {json.dumps(short)[:700]}")
    return result, root


base = source
b0, _ = cell("1-v640-idle-on-original", old, base, "probe")
n0, _ = cell("2-v650-idle-on-original", new, base, "probe")
cell("3-v650-write-on-original", new, base, "write")
cell("4-v650-preview-on-original", new, base, "preview")
mig, migrated = cell("5-v650-confirm", new, base, "confirm")
store = migrated / name
m1, _ = cell("6-v650-idle-on-migrated", new, store, "probe")
cell("7-v650-write-on-migrated", new, store, "write")
o1, _ = cell("8-v640-idle-on-migrated", old, store, "probe")
o2, after_old_write = cell("9-v640-write-on-migrated", old, store, "write")
cell("10-v650-idle-after-a-v640-write", new, after_old_write / name, "probe")

print("\n## comparisons")
for key in ("gates", "blocking_fail", "counts", "edges", "gate_ready"):
    same = b0.get(key) == m1.get(key)
    extra = ""
    if not same and isinstance(b0.get(key), dict):
        extra = " | differs at: " + json.dumps({k: [b0[key].get(k), (m1.get(key) or {}).get(k)]
                                               for k in set(b0[key]) | set(m1.get(key) or {})
                                               if b0[key].get(k) != (m1.get(key) or {}).get(k)})[:400]
    print(f"6.4.0 on the original vs 6.5.0 on the migrated store, {key}: "
          f"{'same' if same else 'DIFFERENT'}{extra}")
print("rules:", b0.get("rules"), "->", m1.get("rules"), "| advisory not passing:",
      b0.get("advisory_fail"), "->", m1.get("advisory_fail"))
