"""Plan 237: a scratch repository for a brief rehearsal: the field package (a `git archive` of the
committed tree, or a copy of an exported folder), its root CLAUDE.md, the briefs, one commit.

    python brief_ws_660.py <field folder> <package dir> <scratch> <brief> [<brief> ...]
"""
import io
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
field, pkg, scratch = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]).resolve()
ws = scratch / f"brief-{field.name}" / "ws"
assert not ws.exists(), "a fresh scratch folder each run"
ws.mkdir(parents=True)
if (field / ".git").exists():
    blob = subprocess.run(["git", "-C", str(field), "archive", "HEAD", pkg, "CLAUDE.md"],
                          capture_output=True).stdout
    tarfile.open(fileobj=io.BytesIO(blob)).extractall(ws)
else:
    shutil.copytree(field / pkg, ws / pkg, ignore=shutil.ignore_patterns(".lock"))
    if (field / pkg / "CLAUDE.md").exists() and not (ws / "CLAUDE.md").exists():
        shutil.copy(field / pkg / "CLAUDE.md", ws / "CLAUDE.md")
(ws / "briefs").mkdir()
for name in sys.argv[4:]:
    shutil.copy(REPO / "plans" / "briefs" / name, ws / "briefs" / name)
for args in (["init", "-q"], ["add", "-A"],
             ["-c", "user.name=field", "-c", "user.email=field@example.invalid", "commit", "-qm",
              "field: before 6.6.0"]):
    subprocess.run(["git", *args], cwd=ws, check=True)
print("WS", ws)
