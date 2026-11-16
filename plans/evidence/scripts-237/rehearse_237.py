"""Plan 237: the standup rehearsal on a scratch copy of the lab fixture, driven by a real headless
agent (plans/evidence/scripts-fb028/labrun.py). This script prepares the workspace, adds work
between reports, and checks the result. It never touches a field package.

    python rehearse_237.py setup <scratch>     # copy the fixture, registry-sync, wire, git init
    python rehearse_237.py work  <scratch>     # work between reports, through the engine
    python rehearse_237.py check <scratch>     # the acceptance checker
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import standup  # noqa: E402
import standup_page  # noqa: E402
import tamheed_server as srv  # noqa: E402

FIX = REPO / "evals" / "sample-results" / "lab-tracker"


def ws_of(scratch: str) -> Path:
    return Path(scratch).resolve() / "standup-run" / "ws"


def git(ws: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=ws, capture_output=True, text=True).stdout


def setup(ws: Path) -> None:
    assert not ws.exists(), "a fresh scratch folder each run"
    shutil.copytree(FIX / "package", ws / "package", ignore=shutil.ignore_patterns(".lock"))
    shutil.copytree(FIX / "workspace", ws / "workspace")
    srv.PACKAGE_ROOT = ws
    sync = srv.package_migrate("package", confirm=True)          # the 6.6.0 registry-sync
    print("OBS sync:", sync["ok"], sync.get("report", {}).get("entity_types_added"))
    assert srv.package_open("package")["ok"]
    (ws / "CLAUDE.md").write_text("# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n",
                                  encoding="utf-8", newline="\n")
    em = srv.handoff_emit(str(ws))
    assert em["ok"], em
    (ws / ".mcp.json").unlink(missing_ok=True)                    # the bundle's server only
    assert srv.package_close()["ok"]
    git(ws, "init", "-q")
    git(ws, "add", "-A")
    git(ws, "-c", "user.name=lab", "-c", "user.email=lab@example.invalid", "commit", "-qm",
        "lab: start")
    print("WS", ws)


def work(ws: Path) -> None:
    """Work between reports: a journal entry, a task to Review, a Met and a Not-met verdict, a
    bind, a new defect, a reworded requirement (same status)."""
    srv.PACKAGE_ROOT = ws
    assert srv.package_open("package")["ok"]
    try:
        conn = srv._CURRENT.conn
        wbs = conn.execute("SELECT id, title FROM wbs_items WHERE lifecycle_status NOT IN"
                           " ('Implemented', 'Review') ORDER BY id LIMIT 1").fetchone()
        acs = [r[0] for r in conn.execute("SELECT id FROM acceptance_criteria WHERE"
                                          " retired_in IS NULL ORDER BY id LIMIT 2")]
        req = conn.execute("SELECT * FROM requirements ORDER BY id LIMIT 1")
        cols = [d[0] for d in req.description]
        req = dict(zip(cols, req.fetchone()))
        out = [srv.progress_update([{"entry": "Built the CSV import and its tests.",
                                     "event_type": "work-done", "actor": "agent:lab"}])]
        if wbs:
            row = srv.entity_query("wbs-item", id=wbs[0])["rows"][0]
            out.append(srv.entity_upsert([dict({k: v for k, v in row.items() if v is not None},
                                               type="wbs-item", lifecycle_status="Review")]))
        if acs:
            out.append(srv.audit_record([{"ac_id": acs[0], "verdict": "Met", "evidence":
                                          "tests/test_import.py passed", "verified_by": "ci"},
                                         {"ac_id": acs[-1], "verdict": "Not-met", "evidence":
                                          "the export drops the last row", "verified_by": "ci"}]))
            out.append(srv.work_bind("abc1234", [acs[0]]))
        out.append(srv.entity_upsert([{"type": "defect", "id": "DEF-090", "title":
                                       "Import drops the header row", "severity": "high"}]))
        out.append(srv.entity_upsert([dict({k: v for k, v in req.items() if v is not None},
                                           type="requirement",
                                           statement=str(req["statement"]) + " Reworded.")]))
        print("OBS work:", [o.get("ok") for o in out], "| wbs", wbs and wbs[0], "| acs", acs,
              "| req", req["id"])
    finally:
        srv.package_close()
    git(ws, "add", "-A")
    git(ws, "-c", "user.name=lab", "-c", "user.email=lab@example.invalid", "commit", "-qm",
        "lab: work")


def check(ws: Path) -> int:
    srv.PACKAGE_ROOT = ws
    lock = ws / "package" / "data" / ".lock"
    if lock.exists():
        print("OBS stray lock; unlock:", srv.package_unlock("package", confirm=True).get("ok"))
    assert srv.package_open("package")["ok"]
    failures = []
    try:
        conn = srv._CURRENT.conn
        rows = [dict(zip(srv._STANDUP_ROW, r)) for r in conn.execute(
            f"SELECT {', '.join(srv._STANDUP_ROW)} FROM standup_reports ORDER BY id")]
        print("OBS reports:", [(r["id"], r["kind"], r["seq"], r["lifecycle_status"],
                                r["supersedes"], r["base_report"]) for r in rows])
        chain = standup.chain(conn)
        st, _cols, broken = standup.replay(chain)
        if broken:
            failures.append(f"replay broke at {broken}")
        for r in rows:
            if r["lifecycle_status"] == "Draft":
                failures.append(f"{r['id']} left as a draft")
                continue
            ok, why = standup.verify(conn, r)
            if r["lifecycle_status"] == "Approved" and not ok:
                failures.append(f"{r['id']} does not verify: {why}")
            page = ws / "package" / "reports" / f"{r['id']}.html"
            if r["lifecycle_status"] != "Draft" and not page.exists():
                failures.append(f"{r['id']} has no page")
                continue
            html = page.read_text(encoding="utf-8")
            first = json.loads(r["facts"]).get("view", {}).get("first")
            words = standup_page.visible_words(html)
            if not first and words > 2000:
                failures.append(f"{r['id']}: {words} visible words")
            if "<script" in html.lower() or re.search(r'href="(?!#)', html):
                failures.append(f"{r['id']}: a script or an outward link")
            if r["operator_words"] and r["operator_words"] in html:
                failures.append(f"{r['id']}: the operator's words on the page")
            print(f"OBS {r['id']}: {r['kind']} {r['lifecycle_status']} words={words}"
                  f" first={first} colour={r['colour']} rule={r['rule_colour']}")
        transitions = conn.execute("SELECT COUNT(*) FROM progress_entries WHERE actor ="
                                   " 'system:standup-report' AND event_type <> 'note'"
                                   ).fetchone()[0]
        if transitions:
            failures.append("a standup journal row that is not a note")
        notes = [r[0] for r in conn.execute("SELECT entry FROM progress_entries WHERE actor ="
                                            " 'system:standup-report'")]
        for r in rows:
            if r["operator_words"] and any(r["operator_words"] in n for n in notes):
                failures.append(f"{r['id']}: the operator's words in the journal")
        edited = any("Reworded" in json.dumps(json.loads(r["facts"])) or
                     "requirements" in json.dumps(json.loads(r["facts"]).get("did", {})
                                                  .get("edited", {}))
                     for r in rows if r["kind"] == "default")
        print("OBS the reworded requirement listed as edited:", edited)
        verify = srv.package_verify()
        print("OBS package_verify ok:", verify.get("ok"), verify.get("verdict"))
    finally:
        srv.package_close()
    idle = git(ws, "status", "--porcelain", "--", "package/data")
    print("OBS data/ changes not committed by the run:", idle.strip() or "none")
    print("FAILURES:", failures or "none")
    return 1 if failures else 0


if __name__ == "__main__":
    cmd, scratch = sys.argv[1], sys.argv[2]
    ws = ws_of(scratch)
    sys.exit({"setup": setup, "work": work, "check": check}[cmd](ws) or 0)
