"""Plan 253: the few field facts the briefs state, read on the scratch copies of measure_253.py
(statuses, stamps and settings keys only; no row text).

    env -u TAMHEED_HOOK_LOG python -I facts_253.py <bundle dir> <package dir> <scratch> [<scratch>...]
"""
import json
import os
import subprocess
import sys
from pathlib import Path

bundle, pkg = Path(sys.argv[1]).resolve(), sys.argv[2]
sys.path[:0] = [str(bundle / "server"), str(bundle / "db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

for scratch in sys.argv[3:]:
    ws = Path(scratch).resolve() / "ws"
    first = subprocess.run(["git", "show", f"HEAD:{pkg}/README.md"], cwd=ws, capture_output=True,
                           text=True, encoding="utf-8").stdout.splitlines()[:1]
    settings = ws / ".claude" / "settings.json"
    src = (json.loads(settings.read_text(encoding="utf-8")).get("extraKnownMarketplaces", {})
           .get("tamheed", {}).get("source", {})) if settings.exists() else None
    srv.PACKAGE_ROOT = ws
    srv.package_open(pkg)
    try:
        fb = srv._CURRENT.conn.execute(
            f"SELECT id, lifecycle_status FROM {srv.ENTITY_TABLES['feedback']}"
            " WHERE id IN ('FB-023', 'FB-024') ORDER BY id").fetchall()
    finally:
        srv.package_close()
    print(f"OBS {Path(scratch).name}: guide stamp at HEAD {first} | settings source keys "
          f"{sorted(src) if isinstance(src, dict) else src} | FB-023/024 {fb}")
