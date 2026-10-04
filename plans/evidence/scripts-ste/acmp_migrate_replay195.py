"""Plan 195: replay `package_migrate` over a copy of the field package (ACMP) at its HEAD.

The copy is a `git archive HEAD tamheed-package` extracted under a scratch root; nothing in the
field repository is touched. The script prints the preview's prompt-file plan, confirms, reads the
rows back, and reports the files that left for the backup folder. Run from the tamheed repo root:

    python plans/evidence/scripts-ste/acmp_migrate_replay195.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FIELD = Path(r"C:/Users/ahammo/Repos/acmp")
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "server"))
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "db"))
import tamheed_server as srv  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="acmp195-") as td:
        root = Path(td)
        tar = root / "pkg.tar"
        with tar.open("wb") as fh:
            subprocess.run(["git", "-C", str(FIELD), "archive", "HEAD", "tamheed-package"],
                           check=True, stdout=fh)
        with tarfile.open(tar) as tf:
            if sys.version_info >= (3, 12):
                tf.extractall(root, filter="data")
            else:
                tf.extractall(root)
        srv.PACKAGE_ROOT = root
        name = "tamheed-package"
        files_before = sorted(p.name for p in (root / name / "prompts").glob("*.md"))
        print("prompt files before:", files_before)
        preview = srv.package_migrate(name)
        print("preview ok:", preview.get("ok"), "|", preview.get("error", ""))
        rep = preview.get("report", {})
        for f in rep.get("prompt_files", []):
            print("  ", f["file"], "->", f["action"])
        print("entry_point:", rep.get("entry_point"), "| folder:", rep.get("prompts_folder"))
        print("entity types added:", rep.get("entity_types_added"))
        out = srv.package_migrate(name, confirm=True)
        print("confirm ok:", out.get("ok"), "|", out.get("error", ""))
        print("applied:", out.get("report", {}).get("prompt_files_applied"))
        print("prompts/ exists after:", (root / name / "prompts").exists())
        print("backup:", sorted(p.name for p in (root / name / "prompts-v5-backup").iterdir()))
        opened = srv.package_open(name)
        print("open ok:", opened.get("ok"))
        print("entry_point now:", srv.server_info()["package"]["entry_point"])
        rows = srv.entity_query("prompt", limit=20)["rows"]
        for r in rows:
            attrs = json.loads(r["custom_attributes"] or "{}")
            print(f"  {r['id']} {r['kind']:<11} {r['lifecycle_status']:<9} {r['title'][:50]!r}"
                  f"  <- {attrs.get('converted_from')}  body={len(r['body'])}B")
        gates = srv.gate_run()["gates"]
        print("G-SET:", gates["G-SET"]["status"], gates["G-SET"].get("failures"))
        print("G-IDS:", gates["G-IDS"]["status"])
        with tempfile.TemporaryDirectory() as target:
            emit = srv.handoff_emit(target)
            print("emit before approval ok:", emit.get("ok"), "|", str(emit.get("error", ""))[:140])
        srv.package_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
