"""Plan 231: the Jisr brief for 6.5.1, made from the 6.5.0 brief line by line, and the
superseded note on the old one. Run once from the repository root.

Facts about the installed release move to 6.5.1. Two facts stay 6.5.0: `resolved_in`, and the
links to `blob/v6.5.0/plans/`. They name the release that carried each fix.
"""
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
old_path = ROOT / "plans/briefs/jisr-6.5.0.md"
text = io.open(old_path, encoding="utf-8").read()
source = text

PAIRS = [
    ("# Brief to Jisr: tamheed 6.5.0 (nine rows answered, one guarded migration, a way back)",
     "# Brief to Jisr: tamheed 6.5.1 (nine rows answered, one guarded migration, a way back)"),
    ("> Section 1 has four checks and several STOPs. Section 1b is the way back to 6.4.0.\n",
     "> Section 1 has four checks and several STOPs. Section 1b is the way back to 6.4.0.\n"
     ">\n"
     "> **This brief replaces `jisr-6.5.0.md`.** 6.5.0 was never installed at Jisr. 6.5.1 is 6.5.0\n"
     "> with four fixes. The migration's journal row carries its time. A sync writes the journal's\n"
     "> file first. The session-start line names a package that is behind. The hook's failure line\n"
     "> withholds a text that reads like an instruction. The upgrade, the stopped sync, the way\n"
     "> back to 6.4.0 and the session-start line were measured again under 6.5.1 on 2026-11-15, on\n"
     "> the same copies. A sentence that was measured under 6.5.0 alone says so.\n"),
    ("Each copy ran under the real 6.4.0 code and under the 6.5.0 code, each in its own\nprocess.",
     "Each copy ran under the real 6.4.0 code and under the 6.5.1 code, each in its own\nprocess."),
    ("Then **quit the client and start it again**. `claude plugin list --json` reads `6.5.0` for this\n"
     "repository. `server_info` in the new process reads `6.5.0`, `010_registers.sql`, schema `10`.\n",
     "Then **quit the client and start it again**. `claude plugin list --json` reads `6.5.1` for this\n"
     "repository. `server_info` in the new process reads `6.5.1`, `010_registers.sql`, schema `10`.\n"
     "\n"
     "The block at the start of the new session holds this line, after its header. It is the\n"
     "expected line, and its cure is the migration below:\n"
     "\n"
     "```text\n"
     "BEHIND THIS ENGINE: document_sections.jsonl lacks `lifecycle_status`. package_open refuses this package until package_migrate runs: ...\n"
     "```\n"
     "\n"
     "The header beside it still says \"(schema 10)\". That number is the engine's, not your package's.\n"),
    ("- \"registry sync failed, package UNCHANGED\": nothing moved. Read the cause, and run it again.\n"
     "- \"registry sync stopped during the file swap ... No table was removed\": some files hold the\n"
     "  new form, and the answer names them. Another program holds a file. Close it, and run the\n"
     "  confirm again: it finishes. Measured on the copy with one file made unwritable.\n",
     "- \"registry sync failed, package UNCHANGED\": nothing moved. Read the cause, and run it again.\n"
     "  The journal's file is written first, so this is also the answer when that file is held.\n"
     "- \"registry sync stopped during the file swap ... No table was removed\": some files hold the\n"
     "  new form, and the answer names them. The journal's file is among them, so the journal\n"
     "  already holds the migration's row. Another program holds a later file. Close it, and run\n"
     "  the confirm again: it finishes, and it adds a second row with its own time.\n"
     "  Measured on the copy twice: with the journal's file held, and with a later file held.\n"),
    ("| `readiness_check(\"package\")` | three blocking rules fail, as before: `acs-met`, `adrs-approved`, `risks-discharged` |\n",
     "| `readiness_check(\"package\")` | three blocking rules fail, as before: `acs-met`, `adrs-approved`, `risks-discharged` |\n"
     "| the `resume` block that `package_open` returned | the first row of `last_entries` is the migration's, and its `occurred_at` holds a time |\n"),
    ("Every count of rows and every trace edge was the same before and after on the copy. Only the\n"
     "journal grew, by the migration's own row.\n",
     "Every count of rows and every trace edge was the same before and after on the copy. Only the\n"
     "journal grew, by the migration's own row.\n"
     "\n"
     "**If that row's `occurred_at` is empty, STOP.** The session is not running 6.5.1. The time is\n"
     "the one difference between a migration under 6.5.0 and one under 6.5.1.\n"),
    ("`tamheed: migrate the package to 6.5.0 (registry-sync)`", "`tamheed: migrate the package to 6.5.1 (registry-sync)`"),
    ("`review_exported_by \"6.5.0\"`.", "`review_exported_by \"6.5.1\"`."),
    ("`tamheed/README.md`, the stock guide of 6.5.0, and `tamheed/CLAUDE.md`.",
     "`tamheed/README.md`, the stock guide of 6.5.1, and `tamheed/CLAUDE.md`."),
    ("Then run `handoff_emit(\"<repository root>\", refresh_stock=true)`.",
     "A first `package_open` in a repository with no root `CLAUDE.md` writes one. If `git status`\n"
     "shows that file as new, that is why. Whether to keep it is the operator's call.\n\n"
     "Then run `handoff_emit(\"<repository root>\", refresh_stock=true)`."),
    ("Your 35 export files were written again by both engines on the copies.",
     "Measured under 6.5.0, and 6.5.1 changes no line of the export code. Your 35 export files were written again by both engines on the copies."),
    ("6.5.0 adds the key `query` in each result,", "Since 6.5.0 each result carries the key `query`,"),
    ("\"unknown keys ['lifecycle_status']\" and moves no file. 6.5.0 does not open a package that was",
     "\"unknown keys ['lifecycle_status']\" and moves no file. 6.5.1 does not open a package that was"),
    ("git commit -m \"tamheed: back to the package as it was before 6.5.0\"",
     "git commit -m \"tamheed: back to the package as it was before 6.5.1\""),
    ("The last command answered \"updated from 6.5.0 to 6.4.0\" in the measurement. Then quit the client\n",
     "In the measurement of 2026-11-14 the last command answered \"updated from 6.5.0 to 6.4.0\". That\n"
     "measurement left 6.5.0. Leaving 6.5.1 is measured after the tag exists. Then quit the client\n"),
    ("It holds for a lock that 6.5.0 wrote,", "It holds for a lock that 6.5.0 or a later release wrote,"),
]
for old, new in PAIRS:
    assert text.count(old) == 1, (text.count(old), old[:70])
    text = text.replace(old, new)

kept = [line for line in text.split("\n") if "6.5.0" in line]
for needle in ('`resolved_in "6.5.0"`', "blob/v6.5.0/plans/"):
    assert any(needle in line for line in kept), needle
io.open(ROOT / "plans/briefs/jisr-6.5.1.md", "w", encoding="utf-8", newline="\n").write(text)

head = "# Brief to Jisr: tamheed 6.5.0 (nine rows answered, one guarded migration, a way back)\n"
assert source.startswith(head)
note = ("\n> **Superseded on 2026-11-15 by [jisr-6.5.1.md](jisr-6.5.1.md). Do not execute this file.**\n"
        "> 6.5.0 was never installed at Jisr, and the plugin's update now installs 6.5.1. This file\n"
        "> stays as the record of what was measured for 6.5.0.\n")
io.open(old_path, "w", encoding="utf-8", newline="\n").write(head + note + source[len(head):])
print("lines of the new brief that still name 6.5.0:", len(kept))
for line in kept:
    print("  ", line[:120])
