"""The two mechanical invariants of a rewrite wave (plans 184-188). Read-only.

For every file the wave touched (git diff against a base ref), compare the committed text with
the working tree:
1. The set of backticked tokens, numbers, `G-`/`FB-`/`WVR-`/`/tamheed:` tokens and ALLCAPS words
   must be identical. A deliberate difference is written in the beat's plan file with its reason.
2. The count of modal and limiting words (may, might, could, can, must, never, only, always,
   until, unless) must not fall: a drop is where a hedge got promoted.

Usage: python plans/evidence/scripts-ste/wave_invariants.py [base-ref]   (default HEAD)
"""
from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TOKENS = re.compile(r"`[^`\n]+`|\b(?:G|FB|WVR|DEF|DW|SC|OQ|LL|GT|ADR|DEC|PE)-[A-Z0-9-]+\b"
                    r"|/tamheed:[a-z-]+|\b\d[\d.,]*\b|\b[A-Z][A-Z_-]{2,}\b")
MODALS = re.compile(r"\b(may|might|could|can|must|never|only|always|until|unless)\b", re.I)


def tokens(text: str) -> set[str]:
    return set(TOKENS.findall(text))


def modals(text: str) -> Counter:
    return Counter(m.lower() for m in MODALS.findall(text))


def main(base: str = "HEAD") -> int:
    changed = subprocess.run(["git", "diff", "--name-only", base, "--"], capture_output=True,
                             text=True, cwd=REPO).stdout.split()
    changed = [c for c in changed if c.endswith((".md", ".py"))]
    bad = 0
    for rel in changed:
        before = subprocess.run(["git", "show", f"{base}:{rel}"], capture_output=True,
                                text=True, encoding="utf-8", cwd=REPO).stdout
        path = REPO / rel
        after = path.read_text(encoding="utf-8") if path.exists() else ""
        gone = sorted(tokens(before) - tokens(after))
        new = sorted(tokens(after) - tokens(before))
        mb, ma = modals(before), modals(after)
        drops = {w: (mb[w], ma[w]) for w in mb if ma[w] < mb[w]}
        if gone or new or drops:
            bad += 1
            print(f"## {rel}")
            if gone:
                print(f"- tokens gone ({len(gone)}): " + ", ".join(gone[:40]) + (" ..." if len(gone) > 40 else ""))
            if new:
                print(f"- tokens new ({len(new)}): " + ", ".join(new[:40]) + (" ..." if len(new) > 40 else ""))
            if drops:
                print("- modal words that FELL (review stop): " + ", ".join(f"{w} {b}->{a}" for w, (b, a) in sorted(drops.items())))
            print()
    print(f"{len(changed)} changed prose/code files, {bad} with a token or modal difference to review.")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:2]))
