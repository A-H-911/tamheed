"""M73 (plans 165-169): the `handoff-repeated` rule replayed over a field package's journal,
through the ENGINE's own helper, at every handoff in turn (the journal cut at that handoff).
Prints ids, line numbers and counts only - never a line of the field's text.

Run:  PYTHONIOENCODING=utf-8 python m73_repeated.py <path to progress_entries.jsonl>
"""
import json
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "server"))
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "db"))
import tamheed_server as srv  # noqa: E402

rows = [json.loads(ln) for ln in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if ln.strip()]
rows.sort(key=lambda r: int(r["id"][3:]))
handoffs = [r for r in rows if r.get("event_type") == "handoff"]
print(f"handoffs {len(handoffs)} ({handoffs[0]['id']} .. {handoffs[-1]['id']}) at "
      f"{srv._HANDOFF_REPEATED_AT} deep, {srv._HANDOFF_LINE_MIN} chars")
fired = 0
for h in handoffs:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE progress_entries (id TEXT PRIMARY KEY, event_type TEXT, entry TEXT)")
    conn.executemany("INSERT INTO progress_entries VALUES (?, ?, ?)",
                     [(r["id"], r["event_type"], r["entry"]) for r in rows
                      if int(r["id"][3:]) <= int(h["id"][3:])])
    found, n = srv._repeated_handoff_lines(conn)
    fired += bool(found)
    print(h["id"], str(h.get("occurred_at", ""))[:10], "handoffs", n,
          "named", [(f"line {ln}", since, depth) for ln, since, depth in found])
print(f"fired on {fired} of {len(handoffs)} handoffs")
