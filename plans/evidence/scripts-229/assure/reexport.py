"""Every export file of a field package, written again by 6.5.0 on a migrated COPY, and
compared with the file that 6.4.0 wrote. Counts and key names only.

Usage: python -I reexport.py <v650 bundle> <migrated root> <package name> <out dir>
"""
import collections
import json
import shutil
import sys
from pathlib import Path

bundle, root, name, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
sys.path.insert(0, str(bundle / "server"))
sys.path.insert(0, str(bundle / "db"))
import tamheed_server as srv  # noqa: E402

srv.PACKAGE_ROOT = root
exports = root / name / "exports"
if out.exists():
    shutil.rmtree(out)
shutil.copytree(exports, out / "old")
assert srv.package_open(name)["ok"]
notes = collections.Counter()
new_keys, lost_keys, row_changes = set(), set(), []
for path in sorted((out / "old").glob("*.json")):
    old = json.loads(path.read_text(encoding="utf-8"))
    head = old.get("tamheed_export") or {}
    tool, args = head.get("tool"), head.get("args") or {}
    if not tool:
        notes["no tool recorded"] += 1
        continue
    res = srv.entity_export(path=path.name, tool=tool, args=args)
    if not res.get("ok"):
        notes["refused"] += 1
        print("refused:", path.name, (res.get("error") or "")[:160])
        continue
    notes["written again"] += 1
    new = json.loads((exports / path.name).read_text(encoding="utf-8"))
    a, b = old.get("result") or {}, new.get("result") or {}
    new_keys |= set(b) - set(a)
    lost_keys |= set(a) - set(b)
    ra, rb = a.get("rows"), b.get("rows")
    if isinstance(ra, list) and isinstance(rb, list):
        by = {r.get("id"): r for r in rb if isinstance(r, dict)}
        gone = [r.get("id") for r in ra if isinstance(r, dict) and r.get("id") not in by]
        moved = added_cols = 0
        for r in ra:
            n = by.get(r.get("id")) if isinstance(r, dict) else None
            if n is None:
                continue
            extra = set(n) - set(r)
            added_cols += bool(extra)
            new_keys |= {f"row.{k}" for k in extra}
            lost_keys |= {f"row.{k}" for k in set(r) - set(n)}
            if any(r[k] != n.get(k) for k in r if k != "last_referenced"):
                moved += 1
        if gone or moved or len(rb) != len(ra):
            row_changes.append((path.name, len(ra), len(rb), len(gone), moved))
srv.package_close()
print("export files:", dict(notes))
print("keys that 6.5.0 adds:", sorted(new_keys))
print("keys that 6.5.0 drops:", sorted(lost_keys))
print("files whose rows differ in a value, or in number (name, old, new, gone, changed):",
      row_changes[:10])
