"""Plan 230: the documents follow the three edits. Run once from the repository root, then
`python docs/guide/build.py`.

    python plans/evidence/scripts-230/docs_230.py

Each replacement must find its text exactly once.
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
    ("## [6.5.0] - 2026-11-15\n",
     "## [Unreleased]\n"
     "\n"
     "### Fixed\n"
     "- The journal row that `package_migrate` writes carries its time (plan 230, the first field's\n"
     "  FB-033). It had none from 4.0.0 to 6.5.0, in both modes. A row that an earlier release\n"
     "  wrote keeps its empty time: the engine has no record of when that migration ran.\n"
     "- A registry sync writes the journal's file first (plan 230). Before, a sync that could not\n"
     "  write that file had already written the others. A second run then answered \"Nothing to\n"
     "  migrate\", and the sync had no journal row. Now a second run always finishes the sync. A\n"
     "  sync that stopped at a later file leaves two rows, each with its time. Until the second\n"
     "  run, the first row reads ahead of the files.\n"
     "- The session-start hook names a package that is behind the engine (plan 230). It said\n"
     "  \"(schema 10) - unlocked\" for a package that `package_open` then refused. The number is\n"
     "  the engine's. One line now names the file, the column and `package_migrate`.\n"
     "\n"
     "## [6.5.0] - 2026-11-15\n"),
])

patch("docs/guide/content.py", [
    ('"col.progress_entries.occurred_at": {"en": "Stamped by the server.", "ar": "يختمه الخادم."},',
     '"col.progress_entries.occurred_at": {"en": "Stamped by the server. A migration\'s row from '
     'before v6.5.1 has none.", "ar": "يختمه الخادم. وصفّ الترحيل المكتوب قبل v6.5.1 لا يحمل وقتًا."},'),
    ("Then open feedback and slices, the lock holder and the next step. At most 40 lines,",
     "Then open feedback and slices, the lock holder and the next step. When a data file is behind "
     "the engine, a line after the header names the file, the column and `package_migrate` (v6.5.1). "
     "The header's schema number is the engine's. At most 40 lines,"),
    ("ثم الملاحظات والشرائح المفتوحة، وحامل القفل، والخطوة التالية. بحد 40 سطرًا،",
     "ثم الملاحظات والشرائح المفتوحة، وحامل القفل، والخطوة التالية. وحين يتأخر ملف بيانات عن "
     "المحرّك، يسمّي سطرٌ بعد الترويسة الملف والعمود و`package_migrate` (v6.5.1). ورقم المخطط في "
     "الترويسة هو رقم المحرّك. بحد 40 سطرًا،"),
    ("silence without a note, the injection screen, the trace line.\"",
     "silence without a note, the injection screen, the trace line, a package that is behind the engine.\""),
    ("والصمت بلا ملاحظة وفحص الحقن وسطر التتبّع.\"",
     "والصمت بلا ملاحظة وفحص الحقن وسطر التتبّع وحزمة متأخرة عن المحرّك.\""),
])

patch("plugins/tamheed/server/README.md", [
    ("a `system:migrate` audit event. Since v6 (plan 195)",
     "a `system:migrate` audit event that carries its time since v6.5.1. Since v6 (plan 195)"),
    ("It names the files that hold the new form, and a second run finishes it. |",
     "It names the files that hold the new form, and a second run finishes it. Since v6.5.1 the "
     "journal's file takes its place first, so that second run always has work to finish. A sync "
     "that stopped at a later file then leaves two journal rows, each with its time. |"),
])

patch("tests/README.md", [
    ("and **byte-determinism** (same input → byte-identical output). |",
     "and **byte-determinism** under one clock (same input and the same clock → byte-identical "
     "output). Since v6.5.1 the migration's journal row carries the time of the run, and a second "
     "test proves that this one value is the only difference between two runs. |"),
])
print("documents follow plan 230")
