"""The 6.5.1 field assurance on scratch COPIES of a real package (plan 231).

Usage: python -I replay.py <package dir> <scratch dir> <old bundle> <released bundle> <new bundle>

`old` is the release that the field left (6.4.0), `released` is 6.5.0, `new` is the candidate.
Each label below is read from the bundle's own manifest, with the bundle's folder beside it.
The package folder is copied for each cell and never written. Prints file names, ids, column
names, times and counts. No text of a row.
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

source, scratch = Path(sys.argv[1]), Path(sys.argv[2])
old, rel, new = (Path(a) for a in sys.argv[3:6])
name = source.name
worker = Path(__file__).with_name("worker.py")
TIME = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
KEYS = ("gates", "blocking_fail", "counts", "edges", "gate_ready", "rules")


def label(bundle: Path) -> str:
    version = json.loads((bundle / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    return f"{version} ({bundle.parents[1].name})"


def tree(root: Path) -> dict:
    return {str(p.relative_to(root)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and p.name != ".lock"}


def moved(before: dict, after: dict) -> list:
    return sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))


def copy(tag: str, origin: Path) -> Path:
    target = scratch / tag
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(origin, target / name,
                    ignore=shutil.ignore_patterns(".lock", "*.writing", "*.tmp", ".git"))
    return target


def run(bundle: Path, root: Path, action: str) -> dict:
    done = subprocess.run([sys.executable, "-I", str(worker), str(bundle), str(root), name, action],
                          capture_output=True, text=True, encoding="utf-8")
    try:
        return json.loads((done.stdout.strip().splitlines() or ["{}"])[-1])
    except ValueError:
        return {"unreadable": (done.stdout + done.stderr)[-300:]}


def journal(root: Path) -> list:
    path = root / name / "data" / "progress_entries.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sync_rows(root: Path, known: set) -> list:
    """(id, actor, has a time) for each migration row whose id the source does not hold. The
    file is in id order as text, so a new row is not always the last line."""
    return [(r["id"], r.get("actor"), bool(TIME.match(str(r.get("occurred_at")))))
            for r in journal(root) if r["id"] not in known and r.get("actor") == "system:migrate"]


print(f"old = {label(old)} | released = {label(rel)} | new = {label(new)} | package folder `{name}`")
rows_before = {r["id"] for r in journal(source.parent)}

print("\n## A. One start, migrated by the released bundle and by the new bundle")
a, b = copy("a-released", source), copy("b-new", source)
start = tree(a)
ra, rb = run(rel, a, "confirm"), run(new, b, "confirm")
ta, tb = tree(a), tree(b)
print("confirm ok:", ra.get("ok"), rb.get("ok"), "| files that each moved:", moved(start, ta), moved(start, tb))
print("files that differ between the two results:", moved(ta, tb))
ja, jb = journal(a), journal(b)
differ = [(x["id"], sorted(k for k in x if x[k] != y[k])) for x, y in zip(ja, jb) if x != y]
print("journal rows:", len(ja), len(jb), "| rows that differ, with their columns:", differ)
print("the migration row under each bundle (id, actor, has a time):",
      sync_rows(a, rows_before), sync_rows(b, rows_before))

print("\n## B. The new bundle on the store that the released bundle migrated")
before = tree(a)
idle = run(new, a, "probe")
print("idle open and close:", idle.get("open_ok"), "| files moved:", moved(before, tree(a)))
again = run(new, a, "preview")
print("package_migrate preview:", again.get("ok"), "|", again.get("error", "")[:150])

print("\n## C. The released bundle on the store that the new bundle migrated")
before = tree(b)
back = run(rel, b, "probe")
print("idle open and close:", back.get("open_ok"), back.get("open_error", "")[:120],
      "| files moved:", moved(before, tree(b)))
print("same gates, blocking rules, counts, edges and rule count as the new bundle on store A:",
      all(back.get(k) == idle.get(k) for k in KEYS))
wrote = run(new, b, "write")
after_write = run(rel, b, "probe")
print("after one write by the new bundle, the released bundle opens it:", wrote.get("write_ok"),
      after_write.get("open_ok"), after_write.get("raised", "")[:120])

print("\n## D. The old bundle on the store that the new bundle migrated")
d = copy("d-new", source)
run(new, d, "confirm")
before = tree(d)
refused = run(old, d, "probe")
print("opens:", refused.get("open_ok"), "| says:", (refused.get("raised") or refused.get("open_error") or "")[:110],
      "| files moved:", moved(before, tree(d)))

print("\n## E. The journal's file is held during the sync (new bundle)")
e = copy("e-journal-held", source)
before = tree(e)
stopped = run(new, e, "held:progress_entries.jsonl")
print("confirm ok:", stopped.get("ok"), "| says:", stopped.get("error", "")[:90])
print("files moved by the stopped run:", moved(before, tree(e)),
      "| staging files left:", sorted(p.name for p in (e / name / "data").glob("*.tmp")))
retry = run(new, e, "confirm")
print("second run ok:", retry.get("ok"), retry.get("error", "")[:90],
      "| migration rows (id, actor, has a time):", sync_rows(e, rows_before))
print("the same case under the released bundle, second run:",
      (lambda f: (run(rel, f, "held:progress_entries.jsonl").get("ok"),
                  run(rel, f, "confirm").get("error", "")[:60]))(copy("e-released", source)))

print("\n## F. A later file is held during the sync (new bundle)")
f = copy("f-later-held", source)
before = tree(f)
stopped = run(new, f, "held:entity_types.jsonl")
print("confirm ok:", stopped.get("ok"), "| says:", stopped.get("error", "")[:200])
print("files moved by the stopped run:", moved(before, tree(f)),
      "| staging files left:", sorted(p.name for p in (f / name / "data").glob("*.tmp")))
retry = run(new, f, "confirm")
final = run(new, f, "probe")
print("second run ok:", retry.get("ok"), retry.get("error", "")[:90],
      "| migration rows (id, actor, has a time):", sync_rows(f, rows_before))
print("opens, with the gates and counts of store A apart from the journal:", final.get("open_ok"),
      all(final.get(k) == idle.get(k) for k in ("gates", "blocking_fail", "edges", "gate_ready")),
      "| journal rows more than store A:",
      final.get("counts", {}).get("progress_entries", 0) - idle.get("counts", {}).get("progress_entries", 0))

print("\n## G. The session-start hook on the package before its migration")
for tag, bundle in (("released", rel), ("new", new)):
    h = copy(f"g-hook-{tag}", source)
    (h / "CLAUDE.md").write_text(
        "# Project\n\n## Tamheed progress tracking\n<!-- tamheed:note v7 -->\n\n"
        f"The Tamheed package for this project is `{name}` (under `{h.as_posix()}`).\n"
        "<!-- /tamheed:note -->\n", encoding="utf-8")
    before = tree(h)
    hook = run(bundle, h, "hook")
    print(f"{tag}: lines {hook.get('count')} | files moved: {moved(before, tree(h))}")
    for line in hook.get("lines") or [hook.get("raised")]:
        print("   ", line)
