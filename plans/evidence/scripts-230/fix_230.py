"""Plan 230: the three edits. Run once from the repository root, after `tests_230.py`.

    python plans/evidence/scripts-230/fix_230.py

Each replacement must find its text exactly once. The server keeps its line count, because the
guide pins server lines (`docs/guide/diagrams.py`, `TOOL_EFFECTS`).
"""
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def patch(rel: str, pairs: list, same_lines: bool = False) -> None:
    path = ROOT / rel
    text = io.open(path, encoding="utf-8").read()
    lines = text.count("\n")
    for old, new in pairs:
        assert text.count(old) == 1, (rel, text.count(old), old[:70])
        text = text.replace(old, new)
    assert not same_lines or text.count("\n") == lines, (rel, lines, text.count("\n"))
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


patch("plugins/tamheed/server/tamheed_server.py", [
    # 1) FB-033: the row says when the migration ran
    ('''            "id": f"PE-{nxt:03d}", "event_type": "note", "entry": entry,
            "actor": "system:migrate"})
''',
     '''            "id": f"PE-{nxt:03d}", "event_type": "note", "entry": entry,
            "actor": "system:migrate", "occurred_at": _now()})
'''),
    # 2) R119: the journal's file takes its place first
    ('''            # successor stands. So a failure anywhere leaves every table on disk. Plan 045
            # removed the old files in a loop first: one file that another program held
            # stopped that loop, and the tables already removed were lost (field assurance of
            # 6.5.0). A file whose bytes do not change is not written at all.
            new_files = sorted((tmp_pkg / "data").glob("*.jsonl"))
''',
     '''            # successor stands. So a failure anywhere leaves every table on disk. A file whose
            # bytes do not change is not written. The journal's file goes FIRST (R119, plan
            # 230): a run that stops later is then finished by a second run, with its own row.
            journal_first = lambda f: (f.name != "progress_entries.jsonl", f.name)  # noqa: E731
            new_files = sorted((tmp_pkg / "data").glob("*.jsonl"), key=journal_first)
'''),
], same_lines=True)

patch("plugins/tamheed/server/resume_hook.py", [
    ('''Failure posture: one line, exit 0 — a hook must never cost the session.
''',
     '''Behind (plan 230, v6.5.1): when a data file lacks a column of this engine, one line after the
header names the file, the column and `package_migrate`. It reads `_columns_behind`, the check
that `package_open` refuses by, so the two never disagree. The header's schema number is the
engine's own.
Failure posture: one line, exit 0 — a hook must never cost the session.
'''),
    ('''    lines.append(f"tamheed resume — package `{name}` (schema {schema}) — {lock_s}")
''',
     '''    lines.append(f"tamheed resume — package `{name}` (schema {schema}) — {lock_s}")
    behind = srv._columns_behind(pkg_dir)       # R115: the rule that package_open refuses by
    if behind:
        lines.append("BEHIND THIS ENGINE: " + ". ".join(
            f"{table}.jsonl lacks {', '.join(f'`{c}`' for c in cols)}"
            for table, cols in sorted(behind.items()))
            + ". package_open refuses this package until package_migrate runs: a preview"
              " first, then confirm=true on the operator's word.")
'''),
])
print("the three edits of plan 230 applied")
