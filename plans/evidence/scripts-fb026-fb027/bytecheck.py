"""Plan 166's byte check, the other half: two renders of the SAME store on the SAME date, one
by the 5.7.0 engine and one by the 5.8.0 engine, are equal once every newline that sits
between a `>` and a `<` is removed and the version stamp is replaced. Whitespace between
tags is the only thing plan 166 adds; anything else would show here as a difference.

Run:  python bytecheck.py <page by 5.7.0> <page by 5.8.0>
"""
import re
import sys
from pathlib import Path

a, b = (Path(p).read_text(encoding="utf-8") for p in sys.argv[1:3])
stamp = re.compile(r'<meta name="tamheed-version" content="[^"]*">')
# Plan 165 sits in the same release: the 5.8.0 page carries one more readiness row,
# `handoff-repeated`, on its own line. It is taken out here, with its count, so that what
# remains is plan 166's layout alone; the script says what it removed.
row = re.compile(r"\n<tr><td>handoff-repeated</td>.*?</tr>")
removed = len(row.findall(b))
b = row.sub("", b)
if removed:
    n = re.search(r"Rules \((\d+) rows\)", b).group(1)
    b = b.replace(f"Rules ({n} rows)", f"Rules ({int(n) - 1} rows)", 1)
    print(f"removed {removed} handoff-repeated row(s) from the 5.8.0 page (plan 165's), "
          f"Rules {n} -> {int(n) - 1}")
norm = [stamp.sub("", t).replace(">\n<", "><") for t in (a, b)]
print(f"5.7.0 page: {len(a):,} bytes, {a.count(chr(10)):,} lines; "
      f"5.8.0 page: {len(b):,} bytes, {b.count(chr(10)):,} lines")
if norm[0] == norm[1]:
    print("EQUAL after the newlines between tags are removed and the stamp replaced")
    sys.exit(0)
la, lb = norm[0].split("\n"), norm[1].split("\n")
for i, (x, y) in enumerate(zip(la, lb), 1):
    if x != y:
        j = next(k for k in range(min(len(x), len(y))) if x[k] != y[k]) if x[:1] == y[:1] else 0
        print(f"first difference at line {i}, column {j}: {x[j:j+80]!r} vs {y[j:j+80]!r}")
        break
else:
    print(f"line counts differ: {len(la)} vs {len(lb)}")
sys.exit(1)
