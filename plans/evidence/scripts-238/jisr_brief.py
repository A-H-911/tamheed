"""Plan 238: the Jisr brief, made from the ACMP brief line by line with Jisr's own measurements
(the fresh export of 2026-11-16, commit 7b1c85c). Run once from the repository root."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
text = (ROOT / "plans/briefs/acmp-6.6.0.md").read_text(encoding="utf-8")
PAIRS = [
    ("# Brief to ACMP: tamheed 6.6.0", "# Brief to Jisr: tamheed 6.6.0"),
    ("The ACMP prompt is one line.", "The Jisr prompt is one line."),
    ("Run them in Git Bash:", "Run them in a terminal:"),
    ("plans/briefs/acmp-6.6.0.md?ref=<commit>\" | sha256sum`.\n"
     "> PowerShell's `>` changes the bytes, so do not save the file through it. If the sum differs\n"
     "> from the prompt's, STOP.",
     "plans/briefs/jisr-6.6.0.md?ref=<commit>\" | shasum -a 256`.\n"
     "> Without `gh`: `curl -fsSL https://raw.githubusercontent.com/A-H-911/tamheed/<commit>/plans/briefs/jisr-6.6.0.md | shasum -a 256`.\n"
     "> If the sum differs from the prompt's, STOP."),
    ("> Every result below is the maintainer's own measurement of 2026-11-16, on a scratch export of\n"
     "> your commit `156398f8` (`git archive`, so your repository was only read).",
     "> Every result below is the maintainer's own measurement of 2026-11-16, on the export that the\n"
     "> operator made of your commit `7b1c85c` (branch `feature/sl-008-workshops`). Your repository was\n"
     "> only read. Every measurement ran on Windows. Nothing here ran on your Mac."),
    ("On `156398f8`: `ready true` on both, and no blocking rule failed.",
     "On `7b1c85c`: `ready false`, and three blocking rules failed: `acs-met`, `adrs-approved` and\n"
     "`risks-discharged`. They failed the same way after the sync, and under 6.5.1."),
    ("On `156398f8` it moved `tamheed-package/README.md` (the stock guide, now of 6.6.0) and\n"
     "`tamheed-package/CLAUDE.md`.",
     "On `7b1c85c` it moved `tamheed/README.md` (the stock guide, now of 6.6.0) and `tamheed/CLAUDE.md`.\n"
     "It also warns that FB-019 awaits the operator's word. That row is older than this upgrade."),
    ("that way. Measured on `156398f8` and on two earlier commits:", "that way. Measured on `7b1c85c`:"),
    ("- The facts call returns 58 to 84 KB. The page is about 463 KB. Its visible words depend on the\n"
     "  agent's words: 2,241 to 2,510 in three runs. The tool warns when a page passes 2,000 words. A\n"
     "  first report is exempt from that budget, so the warning is expected.",
     "- The facts call returns about 38 KB. The page is about 161 KB. Its visible words depend on the\n"
     "  agent's words: 1,924 in the measured run. The tool warns when a page passes 2,000 words. A\n"
     "  first report is exempt from that budget, so such a warning is expected."),
    ("- The narrative check refuses an id that names no row. In a rehearsal it refused two ids that the\n"
     "  agent had made up, and the agent wrote the sentence again.",
     "- The narrative check refuses an id that names no row."),
    ("- The rule colour read green: no open critical or high defect, no open high risk, no question\n"
     "  past its date.",
     "- The rule colour read amber: 10 open high risks. The three failing release rules show under\n"
     "  \"Not ready to close yet\", and they do not move the colour."),
    ("opened the package and\nread `ready true`, as before.",
     "opened the package and\nread the same three blocking rules as before."),
    ("Push and bind by your own\nrules.", "Push by your own rules."),
]
for old, new in PAIRS:
    assert text.count(old) == 1, (text.count(old), old[:60])
    text = text.replace(old, new)
text = text.replace("tamheed-package", "tamheed")
(ROOT / "plans/briefs/jisr-6.6.0.md").write_text(text, encoding="utf-8", newline="\n")
print("jisr brief written")
