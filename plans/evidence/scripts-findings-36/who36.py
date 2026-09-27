"""findings_36 orientation (read-only): who wrote the trace lines the field could not attribute,
and which hook this session's own compaction ran.

For each target time, list every transcript row within +-WINDOW s, in any project folder,
with its session, entrypoint, cwd, row type and (for tool calls) the command's first 200 chars.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path.home() / ".claude" / "projects"
TARGETS = [a for a in sys.argv[1:] if not a.startswith("-")]
WINDOW = 20


def ts(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


targets = [ts(t) for t in TARGETS]
lo = min(targets) - timedelta(seconds=WINDOW)
hi = max(targets) + timedelta(seconds=WINDOW)

for f in sorted(ROOT.glob("*/*.jsonl")):
    try:
        if datetime.fromtimestamp(f.stat().st_mtime, timezone.utc) < lo:
            continue
    except OSError:
        continue
    with f.open(encoding="utf-8", errors="replace") as fh:
        for n, line in enumerate(fh, 1):
            if '"timestamp"' not in line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            t = ts(str(row.get("timestamp", "")))
            if t is None or not any(abs((t - g).total_seconds()) <= WINDOW for g in targets):
                continue
            kind = row.get("type")
            detail = ""
            att = row.get("attachment") or {}
            if att:
                detail = f"att={att.get('type')} hook={att.get('hookName')} cmd={str(att.get('command'))[:90]!r} out={len(str(att.get('stdout') or att.get('content') or ''))}"
            msg = row.get("message") or {}
            content = msg.get("content") if isinstance(msg, dict) else None
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        inp = c.get("input") or {}
                        detail += f" TOOL {c.get('name')}: {str(inp.get('command') or inp.get('file_path') or '')[:260]!r}"
                    if isinstance(c, dict) and c.get("type") == "tool_result":
                        detail += f" RESULT {str(c.get('content'))[:160]!r}"
            print(f"{row.get('timestamp')} {f.parent.name[-28:]}/{f.stem[:8]} L{n} {kind} "
                  f"ep={row.get('entrypoint')} v={row.get('version')} cwd={str(row.get('cwd'))[-40:]} {detail}")
