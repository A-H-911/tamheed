"""After a wave's rewrite: which phrases of the pin ledger no longer occur in the wave's files?
Each one is a pin to re-aim in the same commit (or a phrase to restore).

Usage: python plans/evidence/scripts-ste/pins_missing.py plans/evidence/scripts-ste/pins-184.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROW = re.compile(r"^\| `(?P<src>[^`]+)` \| (?P<line>\d+) \| `(?P<phrase>.*)` \| (?P<files>.+) \|$")


def main(ledger: str) -> int:
    missing = 0
    texts: dict[str, str] = {}
    for line in Path(ledger).read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if not m:
            continue
        phrase = m.group("phrase").replace("\\|", "|")
        for f in re.findall(r"`([^`]+)`", m.group("files")):
            if f not in texts:
                p = REPO / f
                texts[f] = p.read_text(encoding="utf-8") if p.exists() else ""
            if phrase not in texts[f]:
                missing += 1
                print(f"MISSING in {f}: `{phrase}`  (pinned by {m.group('src')}:{m.group('line')})")
    print(f"{missing} pinned phrase(s) no longer occur.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
