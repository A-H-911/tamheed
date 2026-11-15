"""Plan 231: both 6.5.1 briefs after their rehearsal by an agent. Run once from the repository
root, after `briefs_651.py`. Each replacement must find its text exactly once.
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


patch("plans/briefs/acmp-6.5.1.md", [
    ("3. No file `tamheed-package/data/.lock` exists, and the package is closed in every client.\n",
     "3. No file `tamheed-package/data/.lock` exists. Ask the operator whether another client has\n"
     "   this repository open: the agent cannot see that.\n"),
    ("`package_open(\"tamheed-package\")` opens. Do not run `package_migrate`. Measured on your commit:\n",
     "`package_open(\"tamheed-package\")` opens. Run no confirm of `package_migrate`. Its preview is\n"
     "a probe, and it writes nothing. Measured on your commit:\n"),
    ("| `gate_run`, `readiness_check(\"package\")` | the same gates, blocking rules, counts and edges as under 6.5.0 |\n",
     "| `gate_run`, `readiness_check(\"package\")` | `ready true` on both, and no blocking rule fails |\n"),
    ("If the open is refused, or the preview offers a migration, STOP and file a feedback row.\n",
     "6.5.0 and 6.5.1 gave the same gates, rules, counts and edges on that commit. Your counts have\n"
     "grown since an earlier handoff, so compare with a read of today and not with that handoff.\n\n"
     "If the open is refused, or the preview offers a migration, STOP and file a feedback row.\n"),
    ("Run `handoff_emit(\"<repository root>\", refresh_stock=true)`. On your commit it rewrote\n"
     "`tamheed-package/README.md`, the stock guide of 6.5.1, and one line of\n"
     "`tamheed-package/CLAUDE.md`. It left the root `CLAUDE.md` as it was.\n",
     "With the package open, run `handoff_emit(\"<repository root>\", refresh_stock=true)`. On your\n"
     "commit it moved two files. `tamheed-package/README.md` is the stock guide, now of 6.5.1. One\n"
     "line of `tamheed-package/CLAUDE.md` changed. It left the root `CLAUDE.md` as it was.\n\n"
     "It warns that FB-033 is confirmed and not yet reported. That is expected: the row reached the\n"
     "maintainer as a file, and section 3.4 resolves it.\n"),
    ("commit the export moved `tamheed-package/review.html` alone. Close the package, read\n"
     "`git status`, and commit what moved.\n",
     "commit the export moved `tamheed-package/review.html`. After the writes of section 3 it also\n"
     "moves the `csv/` file of each table that those writes changed. Close the package, read\n"
     "`git status`, and commit what moved. Push and bind by your own rules.\n"),
    ("- Say \"committed at\". The time is the commit's. The migration ran a little before it.\n",
     "- Say \"committed at\". The time is the commit's. The migration ran a little before it.\n"
     "- The note holds seven shas. Check first that each is on your remote, by your own rule for a\n"
     "  sha in a row.\n"
     "- Send an `actor`. The tool stores none when the entry has none.\n"),
    ("On your commit that write changed three columns. It moved `feedback.jsonl`, and the journal\n"
     "gained one row by `system:feedback-guard`.\n",
     "On your commit that write changed three columns. It moved `feedback.jsonl` and\n"
     "`progress_entries.jsonl`: the journal gained one row by `system:feedback-guard`. The engine\n"
     "asks for no confirmation on this write. This brief asks for the operator's word all the same.\n"),
])

patch("plans/briefs/jisr-6.5.1.md", [
    ("Open the package and read three results. Each must equal the copy's:\n",
     "Open the package and read these results. Each must equal the copy's:\n"),
    ("| `gate_run` | the same result as before the upgrade: `G-PROGRESS` fails, and no other gate does |\n",
     "| `gate_run` | `G-PROGRESS` fails, and no other gate does. 6.4.0 read the same on the copy before the upgrade |\n"),
    ("- **No-go:** do not commit. Go back by route A in 1b. It restores three files.\n",
     "- **No-go:** do not commit. Go back by route A in 1b. It restores three files. A root\n"
     "  `CLAUDE.md` that the open wrote stays, and `git status` names it.\n"),
    ("Then run `handoff_emit(\"<repository root>\", refresh_stock=true)`. On the copy it rewrote\n",
     "Open the package again. Then run `handoff_emit(\"<repository root>\", refresh_stock=true)`: it\n"
     "is refused while no package is open. On the copy it rewrote\n"),
    ("and `tamheed/CLAUDE.md`. Read `git status`, and commit\nwhat it moved.\n",
     "and `tamheed/CLAUDE.md`. Close the package, read `git status`, and commit\nwhat it moved.\n"
     "It warns that confirmed feedback rows are not yet reported. Section 4 answers those rows.\n"),
    ("no file outside the folder, so your code commits stay.\n",
     "no file outside the folder, so your code commits stay. A root `CLAUDE.md` that the first\n"
     "  open wrote stays too. It is outside the folder, and 6.4.0 reads it.\n"),
    ("FB-008 and FB-010 register local tools. They never resolve.",
     "The nine fixes shipped in 6.5.0. So each row names 6.5.0, although you install 6.5.1.\n\n"
     "FB-008 and FB-010 register local tools. They never resolve."),
])
print("briefs follow their rehearsals")
