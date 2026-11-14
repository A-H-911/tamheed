"""The field assurance of 6.5.0 rewrote package_migrate's file swap, so the guide's citation
of the line that writes `data/*.jsonl` lost its line. This aims it at the new swap. Run it
after `scripts-221/shift_221.py` and `scripts-227/guide_227c.py`, then build the guide.

    python plans/evidence/scripts-229/guide_swap.py
"""
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
source = io.open(ROOT / "plugins/tamheed/server/tamheed_server.py", encoding="utf-8").read().split("\n")
start = next(n for n, line in enumerate(source) if line.startswith("def package_migrate("))
swap = next(n for n in range(start, len(source)) if "_replace_held(dst, final)" in source[n]) + 1
path = ROOT / "docs/guide/diagrams.py"
text = io.open(path, encoding="utf-8").read()
block = text[text.index('    "package_migrate": {'):]
block = block[:block.index("]},\n") + 4]
fixed = re.sub(r'\("data/\*\.jsonl", \d+\)', f'("data/*.jsonl", {swap})', block)
assert fixed.count(f'("data/*.jsonl", {swap})') == 1
io.open(path, "w", encoding="utf-8", newline="\n").write(text.replace(block, fixed))
print("package_migrate writes data/*.jsonl at line", swap)
