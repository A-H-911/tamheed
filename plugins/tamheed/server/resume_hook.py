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
G-INJECT screen) withholds it when it is instruction-shaped. Capped: at most MAX_LINES lines. Traced (opt-in,
plan 136): TAMHEED_HOOK_LOG naming an EXISTING file gets one line of counts per run, never the entry;
the line ends `session=<id>` (plan 141, v5.4) - the event's own `session_id`, which is also the
transcript's file name, so a line names the session that wrote it. One rule for both event fields:
a value that is absent or not a plain token is written `-`. The line opens `<utc> version=<x>`
(plan 151, v5.6) - the bundle's own manifest, read before any note is looked for, so a silent
run names the hook that ran too: a running session keeps the hook it loaded, and only the line
can say which one that was.
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
MANIFEST = HERE.parent / ".claude-plugin" / "plugin.json"   # the version's single source

_NOTE_RE = re.compile(r"<!--\s*tamheed:note v(\d+)\s*-->(.*?)<!--\s*/tamheed:note\s*-->", re.S)
_PKG_RE = re.compile(r"(?:executes Tamheed package|Tamheed package for this project is) `([^`\n]+)`")
_IMPORT_RE = re.compile(r"^@(\S+)", re.M)
_TOKEN_RE = re.compile(r"[A-Za-z0-9._-]{1,64}")   # what an event field may put in the trace


def read_event() -> dict:
    """The event object from stdin - `source` (startup | resume | clear | compact | fork) and
    `session_id` are what the hook uses - guarded so a manual terminal run never blocks and a
    malformed event costs only the wording: {} on any failure."""
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return {}
        raw = sys.stdin.read().lstrip("\ufeff").strip()
        if not raw:
            return {}
        event = json.loads(raw)
        return event if isinstance(event, dict) else {}
    except (OSError, ValueError, AttributeError):
        return {}


def read_source() -> str:
    """The event's `source` alone - kept for a caller written against 5.1-5.3 (plan 141)."""
    return str(read_event().get("source", "") or "")


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
    # Plan 136 (v5.3): the block carries what the store observed about the holder — after a
    # process restart the pid is usually dead, and the field needed package_unlock to learn it.
    remedy = {"not-running": "package_unlock(confirm=true) on the operator's word",
              "reused": "package_unlock(confirm=true) on the operator's word",
              "alive": "the MCP server holds it while the package is open",
              }.get(str(lock.get("observed")) if lock else "",
                    "package_unlock reports the evidence")
    lock_s = (f"lock file present (pid {lock.get('pid')} on {lock.get('host')} since"
              f" {lock.get('taken_at')}, holder observed {lock.get('observed')} — {remedy})"
              if lock else "unlocked")
    lines.append(f"tamheed resume — package `{name}` (schema {schema}) — {lock_s}")
    if source == "compact":
        lines.append("Context was compacted mid-session: this is state re-injection, not a"
                     " session start — resume from the handoff below. Do not re-summarise it"
                     " to the operator.")
    ho, behind = block.get("handoff"), block.get("handoff_behind", 0)
    if not ho:
        lines.append(f"No handoff recorded. Work-done/transition entries uncovered: {behind}.")
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
    source, session, lines, status = "", None, [], "silent"
    try:
        project = Path(args[0] if args else os.environ.get("CLAUDE_PROJECT_DIR") or ".").resolve()
        event = read_event()
        source = str(event.get("source", "") or "")
        session = event.get("session_id")
        lines = build_lines(project, source)
        if lines:
            print("\n".join(lines))
            status = "printed"
    except Exception as exc:  # noqa: BLE001 — one line, never a failed session start
        print(f"tamheed: resume unavailable ({exc.__class__.__name__}: {str(exc)[:160]})")
        status = f"error:{exc.__class__.__name__}"
    _trace(source, lines, status, session)
    return 0


def _token(value) -> str:
    """An event field as the trace may carry it: a plain token, else `-`. The event arrives on
    stdin, so a value holding a newline or a space would otherwise forge a line."""
    return value if isinstance(value, str) and _TOKEN_RE.fullmatch(value) else "-"


def _version() -> str:
    """The bundle's version as the trace may carry it (plan 151, v5.6): the manifest beside
    this hook, through the token rule. Guarded on its own - a missing or malformed manifest
    costs the line its version, never the line and never the block."""
    try:
        return _token(json.loads(MANIFEST.read_text(encoding="utf-8")).get("version"))
    except Exception:  # noqa: BLE001
        return "-"


def _trace(source: str, lines: list[str], status: str, session=None) -> None:
    """Plan 136 (v5.3, findings_34 A2): the field could not tell "the hook did not fire" from
    "it fired and its output was not delivered". Opt-in: when TAMHEED_HOOK_LOG names a file
    that ALREADY EXISTS (the operator creates it — a project's settings `env` block could
    otherwise aim this at any writable path), append ONE line of counts. Never the entry:
    an always-loaded surface's text stays out of files the engine does not own.
    Plan 141 (v5.4, findings_35): a headless session another tool starts in the same folder
    prints the same block, so equal counts attribute nothing. The line ends `session=<id>`.
    Plan 151 (v5.6, findings_37): the hook did not change between two releases and the field
    could not tell their lines apart. The line opens `<utc> version=<x>`; the tail stays."""
    target = os.environ.get("TAMHEED_HOOK_LOG")
    if not target:
        return
    try:
        path = Path(target)
        if not path.is_file():
            return
        from datetime import datetime, timezone  # noqa: PLC0415
        text = "\n".join(lines)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')}"
                     f" version={_version()}"
                     f" source={_token(source)} lines={len(lines)} chars={len(text)}"
                     f" status={status} session={_token(session)}\n")
    except Exception:  # noqa: BLE001 — the trace must never cost the session either
        pass


if __name__ == "__main__":
    sys.exit(main())
