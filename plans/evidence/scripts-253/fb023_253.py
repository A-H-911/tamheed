"""Plan 253: FB-023 measured on a field copy. In the latest handoff, how many lines under
"Awaiting the operator" carry a "Rulings given" sentence, and how many of them the 6.8.0 page
still shows (`standup.handoff_sections`, the engine's own split). Counts only.

    env -u TAMHEED_HOOK_LOG python -I fb023_253.py <bundle dir> <package dir> <scratch>
"""
import os
import sys
from pathlib import Path

bundle, pkg, scratch = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3]).resolve()
sys.path[:0] = [str(bundle / "server"), str(bundle / "db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import standup  # noqa: E402
import tamheed_server as srv  # noqa: E402

srv.PACKAGE_ROOT = scratch / "ws"
srv.package_open(pkg)
try:
    conn = srv._CURRENT.conn
    raw: list[str] = []
    row = conn.execute("SELECT entry FROM progress_entries WHERE event_type = 'handoff'"
                       " ORDER BY CAST(SUBSTR(id, 4) AS INTEGER) DESC LIMIT 1").fetchone()
    current = None
    for line in str(row[0] if row else "").splitlines():
        head = standup._HANDOFF_HEAD.match(line)
        if head:
            current = head.group(1).lower()
            line = line[head.end():]
        if current == "awaiting the operator" and line.strip():
            raw.append(line.strip())
    shown = standup.handoff_sections(conn).get("awaiting the operator", [])
    given = [x for x in raw if standup._GIVEN.search(x)]
    print(f"OBS awaiting lines {len(raw)} | with 'Rulings given' {len(given)} | shown lines"
          f" {len(shown)} | shown still carrying it {sum(bool(standup._GIVEN.search(x)) for x in shown)}")
finally:
    srv.package_close()
