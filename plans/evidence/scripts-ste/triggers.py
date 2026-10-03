"""R11: every quoted trigger phrase and every "Use before ..." / "Invoke to ..." condition in the
skills' frontmatter descriptions. Run before and after wave 2; the two outputs must be identical.

Usage: python plans/evidence/scripts-ste/triggers.py > plans/evidence/scripts-ste/triggers-185.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "server"))
import ste_lint as sl  # noqa: E402


def main() -> None:
    print("# Trigger phrases in skill descriptions (R11)\n")
    for p in sorted((REPO / "plugins" / "tamheed" / "skills").glob("*/SKILL.md")):
        blocks = sl.extract_markdown_prose(p.read_text(encoding="utf-8"))
        desc = next((b["text"] for b in blocks if b["kind"] == "description"), "")
        quoted = re.findall(r'"([^"]+)"', desc)
        conditions = re.findall(r"\b(Use before [^.]+|Use when [^.]+|Invoke to [^.]+|Invoke when [^.]+|Trigger on [^.]+)", desc)
        print(f"## {p.parent.name}")
        for q in quoted:
            print(f'- quoted: "{q}"')
        for c in conditions:
            print(f"- condition: {c.strip()}")
        print()


if __name__ == "__main__":
    main()
