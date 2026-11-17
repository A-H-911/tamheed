"""Plan 248: read one pass's transcript and debug log, not the agent's report.

    python -I inspect_248.py <runs/<run>/p<k> folder>

Prints: how the slash command reached the session (its expanded text, the argument, whether
${CLAUDE_PLUGIN_ROOT} was resolved), whether the loop-guard file was read, which CLAUDE.md files
the debug log names, and every tool call in order with a short input.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def texts(content):
    if isinstance(content, str):
        yield content
    else:
        for part in content or []:
            if part.get("type") == "text":
                yield part.get("text", "")


def main():
    d = Path(sys.argv[1])
    rows = [json.loads(x) for x in (d / "transcript.jsonl").read_text(encoding="utf-8")
            .splitlines() if x.strip()]
    users = [r for r in rows if r.get("type") == "user"]
    first = "\n".join(t for r in users[:3] for t in texts(r.get("message", {}).get("content")))
    print("EXPANDED skill body:", "Execute ONE iteration" in first)
    print("command tag:", re.findall(r"<command-name>[^<]*</command-name>", first)[:2],
          "| args tag:", re.findall(r"<command-args>[^<]*</command-args>", first)[:2])
    print("ARGUMENTS literal left:", "$ARGUMENTS" in first,
          "| plugin root literal left:", "${CLAUDE_PLUGIN_ROOT}" in first,
          "| resolved root path:", bool(re.search(r"plugins[\\/]+tamheed[\\/]+skills", first)))
    calls = []
    for r in rows:
        if r.get("type") != "assistant":
            continue
        for part in r.get("message", {}).get("content") or []:
            if isinstance(part, dict) and part.get("type") == "tool_use":
                calls.append((part["name"], part.get("input", {})))
    guard = [c for c in calls if "loop-guard" in json.dumps(c[1])]
    print("loop-guard read:", [(n, i.get("file_path") or i.get("skill")) for n, i in guard])
    dbg = (d / "debug.log").read_text(encoding="utf-8", errors="replace") if (
        d / "debug.log").exists() else ""
    mds = sorted(set(re.findall(r"[A-Za-z]:[\\/][^\s\"']*CLAUDE\.md", dbg)))
    print("CLAUDE.md in debug log:", mds[:8])
    print(f"TOOL CALLS ({len(calls)}):")
    for n, i in calls:
        short = n.replace("mcp__plugin_tamheed_tamheed__", "t:")
        arg = (i.get("command") or i.get("file_path") or i.get("skill") or i.get("pattern")
               or json.dumps(i, ensure_ascii=False))
        print(f"  {short}: {str(arg)[:170]}")


if __name__ == "__main__":
    main()
