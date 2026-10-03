"""R11 check for a skills wave: the word multiset of every frontmatter description, HEAD vs the
working copy. Lowercased, punctuation stripped, code spans kept as words. The expected delta is
the vocabulary swaps and joiners; anything else is a ruling.

Usage: python plans/evidence/scripts-ste/desc_words.py [git-ref]   (default HEAD)
"""
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REF = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
ROOT = Path(__file__).resolve().parents[3]
# a word: letters, digits, the joiners inside identifiers; an inner dot stays (v5.8.1, data/x.jsonl),
# a trailing dot, colon or comma does not.
WORD = re.compile(r"[a-z0-9][a-z0-9'_/<>&-]*(?:[.:][a-z0-9][a-z0-9'_/<>&-]*)*")


def description(text: str) -> str:
    m = re.match(r"---\n(.*?)\n---", text.replace("\r\n", "\n"), re.S)
    if not m:
        return ""
    out, on = [], False
    for ln in m.group(1).split("\n"):
        if ln.startswith("description:"):
            on = True
            rest = ln[len("description:"):].strip()
            if rest and rest not in (">-", ">", "|"):
                out.append(rest)
            continue
        if on:
            if ln.startswith(" "):
                out.append(ln.strip())
            else:
                break
    return " ".join(out)


def words(s: str) -> Counter:
    return Counter(WORD.findall(s.lower()))


def fmt(c: Counter) -> str:
    return ", ".join(f"{w}x{n}" if n > 1 else w for w, n in sorted(c.items()))


changed = 0
for path in sorted((ROOT / "plugins/tamheed/skills").glob("*/SKILL.md")):
    rel = path.relative_to(ROOT).as_posix()
    before = subprocess.run(["git", "show", f"{REF}:{rel}"], cwd=ROOT, capture_output=True,
                            text=True, encoding="utf-8").stdout
    after = path.read_text(encoding="utf-8")
    wb, wa = words(description(before)), words(description(after))
    gone, new = wb - wa, wa - wb
    if not gone and not new:
        continue
    changed += 1
    print(f"## {rel.split('/')[-2]}")
    if gone:
        print("- gone: " + fmt(gone))
    if new:
        print("- new:  " + fmt(new))
print(f"\n{changed} of 27 descriptions differ in their word multiset.")
