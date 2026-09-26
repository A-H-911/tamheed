"""The plugin's SessionStart hook (plan 123, v5.1): print the package's resume block.

Runs on every session start, resume, clear, compaction and fork (`hooks/hooks.json`). Plain
text on stdout is what Claude Code adds to the model's context for SessionStart hooks — never
JSON (the plugin JSON `additionalContext` path has a bug history: anthropics/claude-code
#16538, #45438; plain stdout is measured working on 2.1.283).

Guarded: silent (nothing printed, exit 0) when the project carries no tamheed note; the note
is found in `<project>/CLAUDE.md` or behind ONE level of `@path` import (a project that keeps
the note in `<package>/CLAUDE.md` reaches it through `@<package>/CLAUDE.md`). Lockless: reads
the store through `store.load`, never takes the writer lock, writes nothing. Screened: the
handoff text is agent-authored prose entering an always-loaded surface, so `_INJECT_RE` (the
G-INJECT screen) withholds it when it is instruction-shaped. Capped: at most MAX_LINES lines.
Failure posture: one line, exit 0 — a hook must never cost the session.

stdlib only, NO inline script metadata: `uv run --no-project` runs it on the interpreter uv
already has without resolving the MCP SDK the server needs.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for p in (HERE, HERE.parent / "db"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

MAX_LINES = 40            # the whole block
ENTRY_LINES = 25          # of the handoff entry itself
ENTRY_CHARS = 4000        # plan 132 (v5.2): = the resume block's own cap; a 12-line field
                          # handoff was already 1,735 chars under the 2,000 of 5.1
TITLE_CHARS = 60

_NOTE_RE = re.compile(r"<!--\s*tamheed:note v(\d+)\s*-->(.*?)<!--\s*/tamheed:note\s*-->", re.S)
_PKG_RE = re.compile(r"executes Tamheed package `([^`\n]+)`")
_IMPORT_RE = re.compile(r"^@(\S+)", re.M)


def read_source() -> str:
    """The event's `source` (startup | resume | clear | compact | fork) from stdin, guarded
    so a manual terminal run never blocks and a malformed event costs only the wording."""
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return ""
        raw = sys.stdin.read().lstrip("﻿").strip()
        if not raw:
            return ""
        return str(json.loads(raw).get("source", "") or "")
    except (OSError, ValueError, AttributeError):
        return ""


def find_note(project: Path) -> tuple[Path, str] | None:
    """The note span: in the project's CLAUDE.md, else behind one level of `@path`."""
    root = project / "CLAUDE.md"
    if not root.is_file():
        return None
    text = root.read_text(encoding="utf-8", errors="replace")
    if m := _NOTE_RE.search(text):
        return root, m.group(2)
    for rel in _IMPORT_RE.findall(text):
        target = (root.parent / rel).resolve()
        if target.is_file():
            imported = target.read_text(encoding="utf-8", errors="replace")
            if m := _NOTE_RE.search(imported):
                return target, m.group(2)
    return None


def _short(text, n: int = TITLE_CHARS) -> str:
    s = " ".join(str(text or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def build_lines(project: Path, source: str = "") -> list[str]:
    found = find_note(project)
    if found is None:
        return []
    _, span = found
    m = _PKG_RE.search(span)
    if not m:
        return ["tamheed: a note span was found but names no package — re-run handoff_emit"]
    name = m.group(1).strip()
    pkg_dir = project / name
    data_dir = pkg_dir / "data"
    if not data_dir.is_dir():
        return [f"tamheed: the note names package `{name}` but {data_dir} does not exist"]
    import store  # noqa: PLC0415  (stdlib module of the bundle)
    import tamheed_server as srv  # noqa: PLC0415  (imports no MCP SDK at module level)
    stored = srv._stored_package_version(pkg_dir)
    if stored is not None and not stored.startswith("4."):
        return [f"tamheed: package `{name}` is a v{stored} store — run package_migrate first"]
    conn = store.load(data_dir)
    try:
        block = srv._resume_block(conn, name, data_dir)
        schema = store.schema_version()
    finally:
        conn.close()
    lines: list[str] = []
    lock = block.get("lock")
    lock_s = (f"lock file present (pid {lock.get('pid')} on {lock.get('host')} since"
              f" {lock.get('taken_at')}; the MCP server holds it while the package is open —"
              " package_unlock reports the holder)" if lock else "unlocked")
    lines.append(f"tamheed resume — package `{name}` (schema {schema}) — {lock_s}")
    if source == "compact":
        lines.append("Context was compacted mid-session: this is state re-injection, not a"
                     " session start — resume from the handoff below; do not re-summarise it"
                     " to the operator.")
    ho, behind = block.get("handoff"), block.get("handoff_behind", 0)
    if not ho:
        lines.append(f"No handoff recorded; work-done/transition entries uncovered: {behind}.")
    else:
        lines.append(f"Handoff {ho['id']} ({ho.get('occurred_at')}, {ho.get('actor')});"
                     f" {behind} work-done/transition entries since"
                     f"{' — BEHIND the journal' if behind else ''}.")
        entry = str(ho.get("entry") or "")
        if srv._INJECT_RE.search(entry):
            lines.append(f"  handoff {ho['id']} withheld (G-INJECT: instruction-shaped text) —"
                         " read it with entity_query and put its wording to the operator")
        else:
            body = entry[:ENTRY_CHARS].splitlines()
            for ln in body[:ENTRY_LINES]:
                lines.append("  " + ln)
            if len(body) > ENTRY_LINES or len(entry) > ENTRY_CHARS or ho.get("truncated"):
                lines.append(f'  … entity_query("progress-entry", ids=["{ho["id"]}"]) for the rest')
        corr = ho.get("corrections") or []
        if corr:
            lines.append("Corrections (read them WITH the handoff): "
                         + ", ".join(c["id"] for c in corr))
    fb = block.get("open_feedback") or []
    if fb:
        lines.append("Feedback awaiting upstream or the operator: " + ", ".join(fb))
    slices = block.get("slices_active") or []
    if slices:
        lines.append("Open slices: " + "; ".join(
            f"{s['id']} [{s['lifecycle_status']}] {_short(s.get('title'))}" for s in slices))
    last = block.get("last_entries") or []
    if last:
        lines.append("Latest journal: " + ", ".join(
            f"{e['id']} ({e['event_type']})" for e in last))
    lines.append(f"Next: {block.get('next')}")
    lines.append(f"Skill: {block.get('skill')} — invoke it by name before your first write.")
    return lines[:MAX_LINES]


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # UTF-8 output on legacy Windows code pages
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                pass
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        project = Path(args[0] if args else os.environ.get("CLAUDE_PROJECT_DIR") or ".").resolve()
        lines = build_lines(project, read_source())
        if lines:
            print("\n".join(lines))
    except Exception as exc:  # noqa: BLE001 — one line, never a failed session start
        print(f"tamheed: resume unavailable ({exc.__class__.__name__}: {str(exc)[:160]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
