"""The documents after the field assurance of 6.5.0 (2026-11-14): an open that refuses a
store that is behind (R115), a swap that removes no table, and the way back to an earlier
release. Run once from the repository root, then run the guide recipe and `python check.py`.

    python plans/evidence/scripts-229/docs_assure.py
"""
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def read(path: str) -> str:
    return io.open(ROOT / path, encoding="utf-8").read()


def write(path: str, text: str) -> None:
    io.open(ROOT / path, "w", encoding="utf-8", newline="\n").write(text)


def patch(path: str, pairs: list) -> None:
    text = read(path)
    for old, new in pairs:
        assert text.count(old) == 1, (path, text.count(old), old[:70])
        text = text.replace(old, new)
    write(path, text)


# 1. The stock operator guide, its history key, and the one fixture that holds a copy of it.
guide = "plugins/tamheed/prompts/README.md"
before = read(guide)
patch(guide, [
    ("`slate_read` returns a checked transcript of the answers file that the operator saved.\n"
     "The transcript is a record of a file. It is never the operator's word: the agent reads\n"
     "it back and the operator confirms it in the session.\n",
     "A slate may hold rounds, participants and decided topics, so one page runs a workshop.\n"
     "The page saves one answers file for each round. `slate_read` returns one checked\n"
     "transcript of those files. The transcript is a record of files. It is never the\n"
     "operator's word: the agent reads it back and the operator confirms it in the session.\n"
     "A view of the page hides text and protects nothing: the hidden text is in the file.\n"
     "\n"
     "After the plugin is upgraded, `package_open` may refuse a package that the earlier\n"
     "release wrote. It names `package_migrate`, and it moves no byte. Commit the package\n"
     "first: that migration takes no backup, and git is the way back.\n"),
])
after = read(guide)
history = json.loads(read("plugins/tamheed/prompts/stock-history.json"))
assert history["README.md"]["6.5.0"] == before, "the 6.5.0 key holds another body"
history["README.md"]["6.5.0"] = after
write("plugins/tamheed/prompts/stock-history.json",
      json.dumps(history, ensure_ascii=False, indent=2) + "\n")
fixture = "evals/sample-results/lab-tracker/package/README.md"
filled = lambda body: body.replace("{package}", "package")  # noqa: E731  the fixture's name
assert read(fixture) == filled(before), "the fixture does not hold the stock guide"
write(fixture, filled(after))

# 2. The CHANGELOG entry of 6.5.0.
patch("CHANGELOG.md", [
    ("**For a live package (the migration note).** Close the package, then run `package_migrate`: a\n"
     "preview first, then `confirm=true` on the operator's word.",
     "**For a live package (the migration note).** Commit the package first: the migration takes no\n"
     "backup, and git is the way back. `package_open` refuses the package until the migration has\n"
     "run, and it moves no byte. Run `package_migrate`: a preview first, then `confirm=true` on the\n"
     "operator's word."),
    ("that change alone. Then run `export_html()` and `package_verify()`.",
     "that change alone. Then run `export_html()` and `package_verify()`. To go back, restore the\n"
     "package's data from git and pin the plugin to the earlier tag: `docs/install.md` has both\n"
     "routes. 6.4.0 does not open a migrated package, and it moves no file when it stops."),
])
text = read("CHANGELOG.md")
entry = text[text.index("## [6.5.0]"):text.index("## [6.4.0]")]
CHANGED = (
     "- `package_open` refuses a package whose data file lacks a column of this engine, and it names\n"
     "  `package_migrate`. Before, the open succeeded and the first close wrote that file again in\n"
     "  full, outside any migration. An idle open now moves no byte on any package. `package_migrate`\n"
     "  runs a registry sync for a column alone. Before, it answered \"nothing to migrate\".\n"
     "- `package_open` refuses a file that holds a key this server does not know, in plain words: a\n"
     "  later tamheed wrote it. Before, that raised a bare error.\n")
assert entry.count("### Changed\n") == 1
entry_changed = entry.replace("### Changed\n", "### Changed\n" + CHANGED, 1)
FIXED = (
    "- **`package_migrate` could remove tables when its file swap failed** (present since 4.x, found\n"
    "  on a copy of a field package). The swap removed every old data file in a loop and then\n"
    "  renamed the new files in. One file that could not be removed stopped the loop, and the\n"
    "  handler then removed the staged copies too. The tables already removed were gone from disk,\n"
    "  and the tool said \"package UNCHANGED\". On Windows a program that holds one file open is\n"
    "  enough. Each new file now takes its place in one step, and no old file is removed first. A\n"
    "  file whose bytes do not change is not written. A stopped swap names the files that hold the\n"
    "  new form, and a second run finishes it. An earlier release keeps the fault: commit a package\n"
    "  before any `package_migrate` under 6.4.0 or older.\n")
if "### Fixed\n" in entry:
    new_entry = entry_changed.replace("### Fixed\n", "### Fixed\n" + FIXED, 1)
else:
    new_entry = entry_changed.rstrip("\n") + "\n\n### Fixed\n" + FIXED + "\n"
write("CHANGELOG.md", text.replace(entry, new_entry))

# 3. The install guide: the shape of an upgrade, and the way back.
patch("docs/install.md", [
    ("names `package_migrate`, run the preview on the closed package, quote it, and convert on the operator's\n"
     "word.",
     "names `package_migrate`, run the preview on the closed package, quote it, and convert on the operator's\n"
     "word. Since 6.5.0 `package_open` refuses a package that the earlier release wrote until that\n"
     "migration has run. The refusal moves no byte, and it is the expected answer."),
])
text = read("docs/install.md")
marker = "### Moving a project to a newer release\n"
at = text.index(marker)
end = text.index("\n\n", text.index("stock guide carry the release", at)) + 2
BACK = '''### Going back to an earlier release

Measured for 6.5.0 to 6.4.0 on copies of two field packages, with the real 6.4.0 code. The data
and the plugin go back together. An earlier release does not open a package that a later release
migrated. It stops on a key that it does not know, and it moves no file.

**The data.** A registry sync takes no backup, so git is the way back. That is why an upgrade
starts with a commit of the package. Before the migration is committed, `git checkout --
<package>/data` restores the files. After it, revert the migration commit and every later
commit that touched the package. Every row that was written after the upgrade leaves the
working tree. Git history keeps it.

**The plugin.** Pin the repository's marketplace record to the earlier tag, then update:

```text
claude plugin marketplace add A-H-911/tamheed#v6.4.0 --scope project
claude plugin marketplace update tamheed
claude plugin update tamheed@tamheed --scope project
```

The last command answered "updated from 6.5.0 to 6.4.0" (Claude Code 2.1.323, Windows, a
separate configuration folder). Quit the client and start it again. `claude plugin list --json`
and `server_info()` then read the earlier version. The first command writes `"ref": "v6.4.0"`
into the repository's `.claude/settings.json`. One machine keeps one marketplace record named
`tamheed` for all its repositories, so the pin moves each of them at its next update. To follow
releases again, run `claude plugin marketplace add A-H-911/tamheed --scope project`, and update.

'''
write("docs/install.md", text[:end] + BACK + text[end:])

# 4. The server README: the two rows.
text = read("plugins/tamheed/server/README.md")
for starts, more in (
        ("| `package_open(name)` |",
         " Since v6.5 the open refuses a package whose data file lacks a column of this engine,"
         " and it names `package_migrate`: an idle open moves no byte. It also refuses, in plain"
         " words, a file that a later tamheed wrote."),
        ("| `package_migrate(name, confirm?)` |",
         " Since v6.5 a registry sync also runs for a column alone, and it takes no backup:"
         " commit the package first. Each new file takes its place in one step and no old file"
         " is removed first, so a swap that stops loses no table. It names the files that hold"
         " the new form, and a second run finishes it.")):
    rows = re.findall(r"^%s.*$" % re.escape(starts), text, re.M)
    assert len(rows) == 1, starts
    assert rows[0].endswith(" |")
    text = text.replace(rows[0], rows[0][:-2] + more + " |")
write("plugins/tamheed/server/README.md", text)

# 5. The guide's prose for the two tools, in both languages.
text = read("docs/guide/content.py")
for ident, en, ar in (
        ("tool.package_open",
         " A package whose data file lacks a column of this engine is refused too. The refusal"
         " points to `package_migrate`, and an idle open moves no byte.",
         " وتُرفض كذلك الحزمة التي ينقص ملف بياناتها عمودًا من أعمدة هذا المحرك، مع إشارة إلى"
         " `package_migrate`، فلا يحرّك الفتح الخامل أي بايت."),
        ("tool.package_migrate",
         " A registry sync takes no backup, so commit the package first. Each new file takes its"
         " place in one step, and a swap that stops loses no table.",
         " مزامنة السجل لا تأخذ نسخة احتياطية، فأودِع الحزمة في git أولًا. يأخذ كل ملف جديد"
         " مكانه في خطوة واحدة، والتبديل الذي يتوقف لا يفقد أي جدول.")):
    at = text.index(f'    "{ident}": {{"en": "')
    mid = text.index('", "ar": "', at)
    end = text.index('"},\n', mid)
    text = text[:mid] + en + text[mid:end] + ar + text[end:]
write("docs/guide/content.py", text)

# 6. The briefs: the last step of an upgrade carries the stock guide.
for field, pkg in (("acmp", "tamheed-package"), ("jisr", "tamheed")):
    patch(f"plans/briefs/{field}-6.5.0.md", [
        ("`review_exported_by \"6.5.0\"`. Commit the review page and its `csv/` as their own commit.\n",
         "`review_exported_by \"6.5.0\"`. Commit the review page and its `csv/` as their own commit.\n"
         "\n"
         "Then run `handoff_emit(\"<repository root>\", refresh_stock=true)`. On the copy it wrote\n"
         f"`{pkg}/README.md`, the stock guide of 6.5.0, and the root note. Read `git status`, and\n"
         "commit what it moved.\n"),
    ])
print("documents follow the field assurance")
