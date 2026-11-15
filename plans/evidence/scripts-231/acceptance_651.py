"""Plan 231: one scratch scenario through every behaviour that the 6.5.1 patch changed, driven
through the real handlers on packages made for the run. It prints one OBS line per behaviour
and stops at the first one that does not hold. Run from the repository root:

    python plans/evidence/scripts-231/acceptance_651.py
"""
import json
import os
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import resume_hook as hook  # noqa: E402
import tamheed_server as srv  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
RELEASE = "6.5.1"
TIME = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
NOTE = ("# Project\n\n## Tamheed progress tracking\n<!-- tamheed:note v7 -->\n\n"
        "The Tamheed package for this project is `{name}` (under `{root}`).\n<!-- /tamheed:note -->\n")


def obs(key: str, holds: bool, value="") -> None:
    print(f"OBS {key}: {'holds' if holds else 'FAILS'} {json.dumps(value, ensure_ascii=False, default=str)[:200]}")
    if not holds:
        raise SystemExit(f"acceptance stopped at {key}")


def files(data: Path) -> dict:
    return {p.name: p.read_bytes() for p in data.iterdir() if p.name != ".lock"}


def behind(root: Path, name: str) -> tuple[Path, str]:
    """A package that lacks one baseline type and one column, as an earlier release wrote it."""
    srv.PACKAGE_ROOT = root
    assert srv.package_create(name, "Acceptance", "rnd")["ok"]
    assert srv.entity_upsert([{"type": "requirement", "id": "FR-001", "kind": "functional",
                               "title": "Store", "source_kind": "brief", "source_span": "p1"}])["ok"]
    assert srv.package_close()["ok"]
    data = root / name / "data"
    et = data / "entity_types.jsonl"
    rows = [json.loads(line) for line in et.read_text(encoding="utf-8").splitlines()]
    et.write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n"
                          for r in rows if r["type_id"] != "skill"), encoding="utf-8")
    fr = data / "requirements.jsonl"
    rows = [json.loads(line) for line in fr.read_text(encoding="utf-8").splitlines()]
    key = sorted(k for k in rows[0] if rows[0][k] is None)[0]
    fr.write_text("".join(json.dumps({k: v for k, v in r.items() if k != key}, ensure_ascii=False,
                                     separators=(",", ":")) + "\n" for r in rows), encoding="utf-8")
    (root / "CLAUDE.md").write_text(NOTE.format(name=name, root=root.as_posix()), encoding="utf-8")
    return data, key


def held(file_name: str, name: str) -> dict:
    """A confirm in which one data file cannot be replaced."""
    real = srv.os.replace

    def refuse(src, dst, *args, **kwargs):
        if Path(dst).name == file_name:
            raise PermissionError(13, "the file is held by another program")
        return real(src, dst, *args, **kwargs)

    srv.os.replace = refuse
    try:
        return srv.package_migrate(name, confirm=True)
    finally:
        srv.os.replace = real


def sync_rows(data: Path) -> list:
    path = data / "progress_entries.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []
    return [r for r in rows if r.get("actor") == "system:migrate"]


def main() -> int:
    obs("the bundle is the release", srv.server_info()["version"] == RELEASE, srv.server_info()["version"])

    # R118: the hook and the open say the same thing about a package that is behind
    one = tempfile.TemporaryDirectory()
    root = Path(one.name)
    data, key = behind(root, "accept")
    fact = f"requirements.jsonl lacks `{key}`"
    lines = hook.build_lines(root, "startup")
    obs("230 the hook names the file, the column and the migration",
        fact in lines[1] and "package_migrate" in lines[1] and "package_open refuses" in lines[1], lines[1])
    refused = srv.package_open("accept")
    obs("230 the open refuses with the same fact", not refused["ok"] and fact in refused["error"])
    preview = srv.package_migrate("accept")["report"]
    obs("230 the preview names the type and the column",
        preview["entity_types_added"] == ["skill"] and preview["columns_added"] == {"requirements": [key]},
        [preview.get("entity_types_added"), preview.get("columns_added")])

    # R119: the journal's file held. No file moves, and a second run does it all
    before = files(data)
    stopped = held("progress_entries.jsonl", "accept")
    obs("230 the journal's file held: no file moved, and the tool says UNCHANGED",
        not stopped["ok"] and files(data) == before and "UNCHANGED" in stopped["error"], stopped.get("error", "")[:80])
    done = srv.package_migrate("accept", confirm=True)
    rows = sync_rows(data)
    obs("230 the second run finishes the sync with one row", done["ok"] and len(rows) == 1, [r["id"] for r in rows])

    # FB-033: the row says when the migration ran, and the resume block shows it
    obs("230 the migration's row carries a time", bool(TIME.match(str(rows[0].get("occurred_at")))),
        rows[0].get("occurred_at"))
    obs("230 the hook has no such line for a current package",
        not any("BEHIND" in line for line in hook.build_lines(root, "startup")))
    opened = srv.package_open("accept")
    latest = opened["resume"]["last_entries"][0]
    obs("230 the resume block shows the row with its time",
        opened["ok"] and latest["id"] == rows[0]["id"] and latest["occurred_at"] == rows[0]["occurred_at"], latest)
    obs("the migrated package verifies", srv.package_verify()["verified"] and "gates" in srv.gate_run())
    assert srv.package_close()["ok"]
    obs("an idle open and close moves no byte",
        (lambda b: srv.package_open("accept")["ok"] and srv.package_close()["ok"] and files(data) == b)(files(data)))
    obs("a second migration has nothing to do", "Nothing to migrate" in srv.package_migrate("accept").get("error", ""))

    # R119: a later file held. The journal already holds a row, and the second run adds one
    two = tempfile.TemporaryDirectory()
    data, _ = behind(Path(two.name), "accept")
    stopped = held("entity_types.jsonl", "accept")
    obs("230 a later file held: the tool names what moved and says to run again",
        not stopped["ok"] and "UNCHANGED" not in stopped["error"] and "progress_entries.jsonl" in stopped["error"]
        and "package_migrate again" in stopped["error"], stopped.get("error", "")[:140])
    obs("230 no table left the disk and no staging file stays",
        not list(data.glob("*.tmp")) and (data / "entity_types.jsonl").exists())
    done = srv.package_migrate("accept", confirm=True)
    rows = sync_rows(data)
    obs("230 the second run finishes, and the journal holds two rows, each with its time",
        done["ok"] and len(rows) == 2 and all(TIME.match(str(r.get("occurred_at"))) for r in rows),
        [(r["id"], r.get("occurred_at")) for r in rows])
    obs("230 the package opens and verifies", srv.package_open("accept")["ok"] and srv.package_verify()["verified"])
    assert srv.package_close()["ok"]
    for tmp in (one, two):
        tmp.cleanup()
    print("ACCEPTANCE-651-DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
