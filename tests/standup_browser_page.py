"""Build one standup page for the browser check (plan 251 v2, U4).

    python tests/standup_browser_page.py <out.html>

A temporary package with every kind of row: phases (one done, one current, one later), a
milestone, slices (done, current, next, later), task groups, tasks done, claimed, blocked and
open, an acceptance check, a task with no slice and one outside the plan. A first report is
recorded, work moves, and a second report is drafted, so the page holds every window state. The
page is copied to <out.html>; the package is removed. It loads no field data.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "plugins/tamheed/server"), str(REPO / "plugins/tamheed/db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

SRC = {"source_kind": "clarification", "source_span": "browser check"}
WORDS = {"headline": "The export moves. One task waits on a question.",
         "did": "We wrote the rows of the export (SL-002).",
         "challenges": "One open question blocks a task.", "next": "We finish SL-002.",
         "colour": "amber", "colour_reason": "One task is blocked.",
         "slice_now": "SL-002", "slice_next": "SL-003",
         "slice": "The export slice writes tasks to a CSV file. Two tasks are open."}


def up(*rows):
    out = srv.entity_upsert(list(rows))
    assert out["ok"], [it for it in out["items"] if not it.get("ok")]


def task(i, title, **kw):
    return dict({"type": "wbs-item", "id": i, "title": title, "lifecycle_status": "Approved"},
                **SRC, **kw)


def build(out: Path) -> None:
    root = Path(tempfile.mkdtemp(prefix="standup-check-"))
    try:
        srv.PACKAGE_ROOT = root
        srv.package_create("demo", "Browser check", "rnd")
        conn = srv._CURRENT.conn
        up(*[{"type": "phase", "id": f"PH-{k}", "title": t, "sort_order": k,
              "lifecycle_status": "Approved", **SRC}
             for k, t in ((1, "Groundwork"), (2, "First release"), (3, "Later work"))],
           {"type": "milestone", "id": "MS-1", "title": "Demo day", "phase_id": "PH-2",
            "due": "2026-12-01"})
        up(*[{"type": "slice", "id": i, "title": t, "phase_id": ph, "sort_order": k,
              "lifecycle_status": "Approved"} for i, t, ph, k in (
                 ("SL-001", "Setup", "PH-1", 1), ("SL-002", "Export", "PH-2", 1),
                 ("SL-003", "Import", "PH-2", 2), ("SL-004", "Reports", "PH-3", 1))])
        up({"type": "requirement", "id": "FR-001", "kind": "functional",
            "title": "Export to CSV", "statement": "The user exports tasks.", **SRC},
           {"type": "acceptance-criterion", "id": "AC-001", "title": "The CSV opens",
            "statement": "Given tasks, when exported, then the file opens.",
            "requirement_id": "FR-001", "slice_id": "SL-002", "lifecycle_status": "Approved"},
           {"type": "open-question", "id": "OQ-001", "title": "Which date format?",
            "question": "Which date format does the export use?", **SRC},
           task("WBS-1", "Export group", slice_id="SL-002", phase_id="PH-2"),
           *[task(f"WBS-1.{k}", f"Export step {k}", parent_id="WBS-1", slice_id="SL-002",
                  phase_id="PH-2") for k in range(1, 6)],
           task("WBS-2", "Set up the repository", slice_id="SL-001", phase_id="PH-1"),
           task("WBS-3", "A chore with no slice", phase_id="PH-2"),
           task("WBS-4", "An old task outside the plan"),
           *[task(f"WBS-5.{k}", f"Import step {k}", slice_id="SL-003", phase_id="PH-2")
             for k in range(1, 4)],
           {"type": "trace-edge", "from_id": "WBS-1.5", "relation": "blocked_by",
            "to_id": "OQ-001"})
        for table, i in (("wbs_items", "WBS-2"), ("slices", "SL-001"), ("phases", "PH-1")):
            conn.execute(f"UPDATE {table} SET lifecycle_status = 'Implemented' WHERE id = ?", (i,))
        assert srv.standup_report(utc_offset="+03:00")["ok"]
        assert srv.standup_report(narrative=WORDS)["ok"]
        confirm = {"operator_confirm": True, "by": "human:check", "words": "record it",
                   "colour": "amber", "slice_now": "SL-002", "slice_next": "SL-003"}
        assert srv.standup_report(action="record", confirm=confirm)["ok"]
        up({"type": "wbs-item", "id": "WBS-1.1",
            "substitute": {"lifecycle_status": ["Approved", "Review"]}},
           {"type": "wbs-item", "id": "WBS-1.2",
            "substitute": {"lifecycle_status": ["Approved", "Review"]}})
        conn.execute("UPDATE wbs_items SET lifecycle_status = 'Implemented' WHERE id IN"
                     " ('WBS-1.2', 'WBS-1.3')")
        assert srv.audit_record([{"ac_id": "AC-001", "verdict": "Met", "verified_by": "human",
                                  "verification_method": "manual", "evidence": "opened"}])["ok"]
        srv.progress_update([{"entry": "Wrote the rows of the export.", "event_type":
                              "work-done", "subject_id": "WBS-1.4", "actor": "agent:check"}])
        assert srv.standup_report()["ok"]
        page = srv.standup_report(narrative=WORDS)["page"]
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(page, out)
    finally:
        if srv._CURRENT is not None:
            srv.package_close()
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python tests/standup_browser_page.py <out.html>")
    build(Path(sys.argv[1]).resolve())
    print("wrote", sys.argv[1])
