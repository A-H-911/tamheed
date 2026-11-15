"""Plan 231, after the tag: the two briefs take the answers that could not be measured before
the tag existed, and the ledger closes. Run once from the repository root.
"""
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def patch(rel: str, pairs: list) -> None:
    path = ROOT / rel
    text = io.open(path, encoding="utf-8").read()
    for old, new in pairs:
        assert text.count(old) == 1, (rel, text.count(old), old[:70])
        text = text.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


patch("plans/briefs/acmp-6.5.1.md", [
    ("  installs 6.5.0. The measurement left 6.4.0, and the last command answered \"updated from 6.4.0\n"
     "  to 6.5.0\". Leaving 6.5.1 is measured after the tag exists.\n",
     "  installs 6.5.0. Measured again after the tag, leaving 6.5.1: the last command answered\n"
     "  \"updated from 6.5.1 to 6.5.0\".\n"),
])
patch("plans/briefs/jisr-6.5.1.md", [
    ("In the measurement of 2026-11-14 the last command answered \"updated from 6.5.0 to 6.4.0\". That\n"
     "measurement left 6.5.0. Leaving 6.5.1 is measured after the tag exists. Then quit the client\n",
     "Measured after the tag, leaving 6.5.1: the last command answered \"updated from 6.5.1 to\n"
     "6.4.0\". Then quit the client\n"),
    ("Route B was measured in a separate configuration folder, on Windows, with Claude Code 2.1.323.",
     "Route B was measured in a separate configuration folder, on Windows, with Claude Code 2.1.325."),
])
patch("plans/231-release-6.5.1.md", [
    ("> Status: PLANNED 2026-11-15.", "> Status: DONE 2026-11-15."),
    ("`acceptance_651.py` holds on 16 observations. Not measured before the tag: the plugin going\n"
     "back from 6.5.1 to 6.5.0. No brief quotes an answer for that direction.\n",
     "`acceptance_651.py` holds on 16 observations.\n"
     "\n"
     "Measured after the tag, in the separate configuration folder: \"updated from 6.5.0 to 6.5.1\",\n"
     "then \"updated from 6.5.1 to 6.5.0\" with the ref `v6.5.0`, then \"updated from 6.5.1 to 6.4.0\"\n"
     "with the ref `v6.4.0`. Both briefs quote the answer for their own direction.\n"),
])
patch("plans/230-migration-row-time.md", [
    ("> Status: IN PROGRESS 2026-11-15.", "> Status: DONE 2026-11-15 (`2c23dbf`, `a4a0e06`)."),
])

p = ROOT / "plans/README.md"
t = io.open(p, encoding="utf-8").read()
for number, status in (
    ("230", "DONE 2026-11-15 (`2c23dbf`, CI run 43676678644 green on eleven jobs). The hook's "
            "failure line, found in its review: `a4a0e06` (R120) |"),
    ("231", "DONE 2026-11-15. Released as `3f94b4d` on `main` (CI run 43680633082 green on eleven "
            "jobs), tag `v6.5.1`. Two rehearsals by an agent corrected the briefs |"),
):
    rows = re.findall(r"^\| %s \|.*$" % number, t, re.M)
    assert len(rows) == 1, number
    head = rows[0].rsplit("|", 2)[0]
    t = t.replace(rows[0], head + "| " + status)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("briefs and ledger follow the tag")
