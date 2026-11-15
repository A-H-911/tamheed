"""Plan 231: the documents follow the last fix of the round. `handoff_emit` named a local-tool
row among the confirmed rows that are not yet reported. A local tool never leaves the project.
Run once from the repository root. Each replacement must find its text exactly once.
"""
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def patch(rel: str, pairs: list) -> None:
    path = ROOT / rel
    text = io.open(path, encoding="utf-8").read()
    for old, new in pairs:
        assert text.count(old) == 1, (rel, text.count(old), old[:70])
        text = text.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


patch("CHANGELOG.md", [
    ("  A text that reads like an instruction is withheld now.\n",
     "  A text that reads like an instruction is withheld now.\n"
     "- `handoff_emit` leaves a local-tool row out of its warning about confirmed rows that are not\n"
     "  yet reported (plan 231, found in a rehearsal). A local tool never leaves the project, so\n"
     "  the warning named it at every emit. The review page already left it out.\n"),
])
patch("plans/briefs/acmp-6.5.1.md", [
    ("A patch on 6.5.0. No file of a package changes form, and no migration runs. It holds four fixes.",
     "A patch on 6.5.0. No file of a package changes form, and no migration runs. It holds five fixes."),
    ("| The hook's failure line withholds a text that reads like an instruction | the review of this patch |\n",
     "| The hook's failure line withholds a text that reads like an instruction | the review of this patch |\n"
     "| `handoff_emit` no longer names a local-tool row as \"not yet reported\" | a rehearsal of this brief |\n"),
])
patch("plans/briefs/jisr-6.5.1.md", [
    ("> with four fixes. The migration's journal row carries its time.",
     "> with five fixes. The migration's journal row carries its time."),
    ("> withholds a text that reads like an instruction. The upgrade,",
     "> withholds a text that reads like an instruction. `handoff_emit` no longer names your two\n"
     "> local-tool rows as \"not yet reported\". The upgrade,"),
])
patch("plans/231-release-6.5.1.md", [
    ("A local-tool row never leaves, so it is named at every emit. Older than this round |",
     "A local-tool row never leaves, so it was named at every emit. Older than this round. The operator ruled: fix it. Fixed with a test, after the rehearsals |"),
])
print("documents follow the warning fix")
