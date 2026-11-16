"""Plan 246, after its two reviews: what git keeps after a withdrawal, and an id that prose
cites. Run after docs_246.py. Idempotent.

    python plans/evidence/scripts-239/docs_246b.py
"""
from pathlib import Path

R = Path(__file__).resolve().parents[3]
EDITS = {
    "SECURITY.md": [(
        "  refuses the family. A withdrawal (v6.7) removes a row that nothing depends on, on the\n"
        "  operator's word. Git history keeps the row.",
        "  refuses the family. A withdrawal (v6.7) removes a row that nothing depends on, on the\n"
        "  operator's word. Git history keeps the row: the words, the facts and the pages that were\n"
        "  committed. Real erasure needs a rewrite of the git history.")],
    "plugins/tamheed/skills/standup/SKILL.md": [(
        "The id is never used again. Git history keeps the removed row, so this is no erasure. Export\n",
        "The id is never used again. Git history keeps the removed row, so this is no erasure. Prose\n"
        "that cites the id keeps it, and the advisory `prose-ids-resolve` then lists it. Export\n")],
}
for rel, pairs in EDITS.items():
    path = R / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in text:
            continue
        assert text.count(old) == 1, (rel, text.count(old), old[:60])
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="\n")
print("docs 246b written")
