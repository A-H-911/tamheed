"""The rollback drill and a failure in the migration, on scratch COPIES of a real package.

Usage: python -I drill.py <v640 bundle> <v650 bundle> <package dir> <scratch dir>
Prints file names, ids, statuses and counts. No text of a row.
"""
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

old, new, source, scratch = (Path(a) for a in sys.argv[1:5])
name = source.name
here = Path(__file__).parent
IGNORE = shutil.ignore_patterns(".lock", "*.writing", "*.tmp", ".git")


def tree(root: Path) -> dict:
    return {str(p.relative_to(root)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def moved(before: dict, after: dict) -> list:
    return sorted(set(before) ^ set(after) | {k for k in before if k in after and before[k] != after[k]})


def fresh(label: str) -> Path:
    target = scratch / label
    if target.exists():
        shutil.rmtree(target, onerror=lambda f, p, e: (os.chmod(p, stat.S_IWRITE), f(p)))
    shutil.copytree(source, target / name, ignore=IGNORE)
    return target


def run(script: str, bundle: Path, root: Path, *more: str) -> str:
    done = subprocess.run([sys.executable, "-I", "-X", "utf8", str(here / script), str(bundle), str(root), name,
                           *more], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (done.stdout + done.stderr).strip()


def probe(bundle: Path, root: Path) -> dict:
    return json.loads(run("worker.py", bundle, root, "probe").splitlines()[-1])


def restore(root: Path, files: list) -> None:
    """What `git checkout <sha> -- <files>` and `git clean` do: the named files go back to
    the original, and a file that the original does not have is removed."""
    for rel in files:
        origin, target = source.parent / rel, root / rel
        if origin.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origin, target)
        elif target.exists():
            target.unlink()


original = tree(source.parent) if False else {f"{name}/{k}": v for k, v in tree(source).items()
                                               if not k.endswith((".lock", ".writing", ".tmp"))}
baseline = probe(old, fresh("d0-baseline"))
KEYS = ("gates", "blocking_fail", "counts", "edges", "gate_ready", "rules")

print("## 1. Go back straight after the migration")
root = fresh("d1")
print("confirm:", json.loads(run("worker.py", new, root, "confirm").splitlines()[-1]).get("ok"))
changed = moved(original, tree(root))
print("files that the migration moved:", changed)
restore(root, changed)
print("tree equals the original, byte for byte:", tree(root) == original)
back = probe(old, root)
print("6.4.0 opens it:", back.get("open_ok"), "| same results as before the upgrade:",
      all(back.get(k) == baseline.get(k) for k in KEYS))

print("\n## 2. Go back after the upgrade's steps and later 6.5.0 writes")
root = fresh("d2")
run("worker.py", new, root, "confirm")
text = run("exercise.py", new, root)
print("\n".join(line for line in text.splitlines() if line.startswith(("FAIL", "exercise:"))))
changed = moved(original, tree(root))
inside = [c for c in changed if c.startswith(f"{name}/data/")]
outside = [c for c in changed if not c.startswith(f"{name}/data/")]
print("files moved under data/:", len(inside), "| elsewhere:", len(outside))
print("elsewhere, by folder:", sorted({"/".join(c.split("/")[:2 if c.count("/") < 2 else 2]) + "/"
                                       + (c.split("/")[2].split(".")[-1] if c.count("/") >= 2 else "")
                                       for c in outside})[:12])
partial = probe(old, root)
print("6.4.0 on the written store:", partial.get("open_ok"), (partial.get("raised") or "")[:90])
restore(root, changed)
print("tree equals the original after the restore:", tree(root) == original)
back = probe(old, root)
print("6.4.0 opens it:", back.get("open_ok"), "| same results as before the upgrade:",
      all(back.get(k) == baseline.get(k) for k in KEYS))

print("\n## 3. The migration fails in the middle")
root = fresh("d3")
blocked = root / name / "data" / "entity_types.jsonl"
os.chmod(blocked, stat.S_IREAD)
failed = json.loads(run("worker.py", new, root, "confirm").splitlines()[-1])
print("confirm ok:", failed.get("ok"), "| says:", (failed.get("error") or failed.get("raised") or "")[:330])
left = tree(root)
print("files moved by the failed run:", moved(original, left))
print("left behind:", sorted(p.name for p in (root / name / "data").iterdir()
                             if p.name.endswith((".tmp", ".lock", ".writing", ".unflushed"))))
os.chmod(blocked, stat.S_IWRITE)
after = probe(new, root)
print("6.5.0 open after the failure:", after.get("open_ok"), (after.get("open_error") or "")[:160])
retry = json.loads(run("worker.py", new, root, "confirm").splitlines()[-1])
print("confirm again, once the file can be written:", retry.get("ok"),
      (retry.get("error") or "")[:300])
final = probe(new, root)
print("6.5.0 opens it:", final.get("open_ok"), "| same gates as before the upgrade:",
      all(final.get(k) == baseline.get(k) for k in ("gates", "blocking_fail", "edges", "gate_ready")))
