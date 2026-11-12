"""Plan 225: migration 009 adds one nullable column to `document_sections`, and every column
serialises (db/CANONICAL.md rule 4). So each recorded package rewrites that one file once.

This script does it through the engine, never by hand: an in-process open and a close of each
fixture. The close flushes only the files whose bytes changed. Run it from the repository root:

    python plans/evidence/scripts-225/rewrite_fixtures_225.py

Expected: `document_sections.jsonl` changes in the demo sample and in the three eval packages,
and no other file. The recorded pages, CSVs and exports of the fixtures then lag their data
(`package_verify` reads `review_current: false`). The release step refreshes them (plan 229).
"""
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R / "plugins" / "tamheed" / "server"))
import tamheed_server as srv  # noqa: E402

TARGETS = [(R / "generated-samples", "support-triage-agent-v2")] + [
    (case, "package") for case in sorted((R / "evals" / "sample-results").iterdir())
    if (case / "package" / "data").is_dir()]

for root, name in TARGETS:
    srv.PACKAGE_ROOT = root
    opened = srv.package_open(name)
    if not opened.get("ok"):
        raise SystemExit(f"{root.name}/{name}: open refused: {opened.get('error')}")
    closed = srv.package_close()
    print(f"{root.name}/{name}: closed {closed.get('ok')}")
