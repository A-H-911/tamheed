"""The same export files written by 6.4.0 (on the original) and by 6.5.0 (on the migrated
copy): are the rows the same? Counts and key names only.

Usage: python -I compare_exports.py <exports written by 6.4.0> <exports written by 6.5.0>
"""
import json
import sys
from pathlib import Path

a_dir, b_dir = Path(sys.argv[1]), Path(sys.argv[2])
same = differ = 0
added, examples = set(), []
for path in sorted(a_dir.glob("*.json")):
    other = b_dir / path.name
    if not other.is_file():
        examples.append((path.name, "missing under 6.5.0"))
        differ += 1
        continue
    a = json.loads(path.read_text(encoding="utf-8")).get("result") or {}
    b = json.loads(other.read_text(encoding="utf-8")).get("result") or {}
    added |= set(b) - set(a)
    ok = True
    for key in set(a) - {"rows"}:
        if a[key] != b.get(key):
            ok = False
            examples.append((path.name, f"result.{key} differs"))
    ra, rb = a.get("rows"), b.get("rows")
    if isinstance(ra, list):
        if not isinstance(rb, list) or len(ra) != len(rb):
            ok = False
            examples.append((path.name, "row count differs"))
        else:
            for x, y in zip(ra, rb):
                if isinstance(x, dict) and isinstance(y, dict):
                    added |= {f"row.{k}" for k in set(y) - set(x)}
                    if any(x[k] != y.get(k, object()) for k in x):
                        ok = False
                        examples.append((path.name, "a row's value differs"))
                        break
                elif x != y:
                    ok = False
                    break
    same += ok
    differ += not ok
print(f"files with the same rows and the same order under both engines: {same} | differing: {differ}")
print("keys that only 6.5.0 writes:", sorted(added))
print("differences:", examples[:8])
