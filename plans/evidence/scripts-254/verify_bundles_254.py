"""Plan 254: prove the bundles hold every row of every content once, by rebuilding each file from them."""
import csv, collections, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
study = Path(sys.argv[1]).resolve()
HEAD = re.compile(r"^##### FILE (.+) \| sha ([0-9a-f]{12}) \| from row (\d+) of (\d+) #####$")
rows = collections.defaultdict(dict)
total = {}
for f in sorted((study / "bundles").rglob("*.txt")):
    if f.parent.name.startswith("F"):
        continue
    cur = None
    body = f.read_text(encoding="utf-8").split("\n")
    assert body[-1] == ""
    for ln in body[:-1]:
        m = HEAD.match(ln)
        if m:
            cur, n = (m[1], m[2]), int(m[3])
            total[cur] = int(m[4])
            continue
        assert cur, f
        assert n not in rows[cur], (cur, n)
        rows[cur][n] = ln
        n += 1
bad = []
for (path, sha), got in rows.items():
    if sorted(got) != list(range(1, total[(path, sha)] + 1)):
        bad.append((path, "rows", len(got), total[(path, sha)])); continue
    text, carry = [], ""
    for i in range(1, total[(path, sha)] + 1):
        ln = got[i]
        if len(ln) == 1802 and ln.endswith(" ↵"):
            carry += ln[:-2]; continue
        text.append(carry + ln); carry = ""
    orig = (study / "src" / path).read_bytes().decode("utf-8", "replace").replace("\r\n", "\n").replace("\r", "\n")
    if "\n".join(text) != orig:
        bad.append((path, "text differs"))
led = list(csv.DictReader((HERE / "ledger.csv").open(encoding="utf-8")))
read = {p for p, _ in rows}
missing = [r["path"] for r in led if not r["read_as"] and r["lane"] not in ("image", "dump") and r["path"] not in read]
print("files rebuilt from bundles", len(rows), "bad", bad[:5], "missing", missing[:5])
print("paths", len(led), "read by a model", sum(1 for r in led if not r["read_as"] and r["lane"] not in ("image", "dump")),
      "images", sum(1 for r in led if r["lane"] == "image" and not r["read_as"]),
      "dumps", sum(1 for r in led if r["lane"] == "dump" and not r["read_as"]),
      "proven copies", sum(1 for r in led if r["read_as"]))
big = max((study / "bundles").rglob("*.txt"), key=lambda f: f.stat().st_size)
print("largest bundle", big.stat().st_size, big.relative_to(study))
