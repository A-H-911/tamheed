"""Plan 248, seeding: copy the pass-0 workspace and give it a backlog, through the tools.

    env -u TAMHEED_HOOK_LOG python -I seed_248.py <scratch folder> A|B

The workspace is built first by `setup_248.py <scratch> run-A|run-B`.

A: DEC-003 -> SC-003 -> SL-004 (PH-1) with WBS-5..7 and AC-007..9, three small commands.
B: DEC-003 -> SC-003 -> PH-2 -> SL-005 with WBS-8 (recurring tasks, FR-006) and AC-010, which
   waits on the open OQ-001 (`WBS-8 blocked_by OQ-001`, the marker in the criterion). DEC-002
   keeps FR-006 out of the MVP, so the slice sits in a phase after it.
The scope change is Approved, its rows are written and re-read, then it is set Merged: the
note's own order. The scripted operator is `human:rehearsal-operator` (L1, scratch only).
The seeding commit is package-only, so it is unbound by rule.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(REPO / "plugins/tamheed/server"), str(REPO / "plugins/tamheed/db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402


def _rm(path) -> None:
    """rmtree that clears the read-only bit git sets on its object files (Windows)."""
    import stat

    def again(fn, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        fn(p)
    shutil.rmtree(path, onerror=again)

OP = "human:rehearsal-operator"
SRC = {"source_kind": "clarification", "source_span": "plan 248 rehearsal seeding"}


def edge(f, rel, t):
    return {"type": "trace-edge", "from_id": f, "relation": rel, "to_id": t}


def rows_a():
    dec = {"type": "decision", "id": "DEC-003", "title": "Harden three tick commands",
           "decision": "Add SL-004: add refuses a bad due date, list --overdue filters, and done"
                       " on an unknown id fails.",
           "rationale": "Each is a small, testable change to an existing command.",
           "lifecycle_status": "Approved", **SRC}
    plan = [
        {"type": "slice", "id": "SL-004", "title": "Command hardening", "phase_id": "PH-1",
         "objective": "Three small, testable changes to existing commands", "sort_order": 4,
         "lifecycle_status": "Approved", "introduced_in": 2},
        {"type": "wbs-item", "id": "WBS-5", "title": "add refuses a due date that is not"
         " YYYY-MM-DD", "slice_id": "SL-004", "lifecycle_status": "Approved", **SRC},
        {"type": "wbs-item", "id": "WBS-6", "title": "list --overdue shows only open overdue"
         " tasks", "slice_id": "SL-004", "lifecycle_status": "Approved", **SRC},
        {"type": "wbs-item", "id": "WBS-7", "title": "done on an unknown id exits 1",
         "slice_id": "SL-004", "lifecycle_status": "Approved", **SRC},
        {"type": "acceptance-criterion", "id": "AC-007", "title": "add refuses a bad due date",
         "statement": "Given a due date that is not YYYY-MM-DD, when `add` runs, then it prints"
                      " an error, exits 2, and stores no task.",
         "requirement_id": "FR-001", "slice_id": "SL-004", "lifecycle_status": "Approved",
         "introduced_in": 2},
        {"type": "acceptance-criterion", "id": "AC-008", "title": "list --overdue filters",
         "statement": "Given open tasks with past, today and future due dates and a done past"
                      " task, when `list --overdue` runs, then it shows only the open past-due"
                      " tasks.",
         "requirement_id": "FR-002", "slice_id": "SL-004", "lifecycle_status": "Approved",
         "introduced_in": 2},
        {"type": "acceptance-criterion", "id": "AC-009", "title": "done on an unknown id fails",
         "statement": "Given no task with the id, when `done <id>` runs, then it prints"
                      " `no task #<id>` and exits 1.",
         "requirement_id": "FR-003", "slice_id": "SL-004", "lifecycle_status": "Approved",
         "introduced_in": 2},
    ]
    edges = [edge("SL-004", "implements", f) for f in ("FR-001", "FR-002", "FR-003")]
    edges += [edge("WBS-5", "implements", "FR-001"), edge("WBS-6", "implements", "FR-002"),
              edge("WBS-7", "implements", "FR-003")]
    return dec, plan, edges


def rows_b():
    dec = {"type": "decision", "id": "DEC-003", "title": "Plan recurring tasks after the MVP",
           "decision": "Add PH-2 with SL-005 for FR-006. The work waits on OQ-001; DEC-002"
                       " keeps FR-006 out of the MVP.",
           "rationale": "The slice can be planned now. Its missed-repeat rule cannot be built"
                        " until OQ-001 is answered.",
           "lifecycle_status": "Approved", **SRC}
    plan = [
        {"type": "phase", "id": "PH-2", "title": "After the MVP", "objective": "Recurring"
         " tasks", "sort_order": 2, "lifecycle_status": "Approved", "introduced_in": 2, **SRC},
        {"type": "slice", "id": "SL-005", "title": "Recurring tasks", "phase_id": "PH-2",
         "objective": "Tasks that repeat on a schedule", "sort_order": 5,
         "lifecycle_status": "Approved", "introduced_in": 2},
        {"type": "wbs-item", "id": "WBS-8", "title": "Recurring tasks: add --every and the"
         " next repeat", "slice_id": "SL-005", "lifecycle_status": "Approved", **SRC},
        {"type": "acceptance-criterion", "id": "AC-010", "title": "a missed repeat behaves as"
         " decided",
         "statement": "Given a repeating task whose due date passed with no completion, when"
                      " the next repeat is computed, then the missed repeat behaves as OQ-001"
                      " decides. [NEEDS-CLARIFICATION: OQ-001]",
         "requirement_id": "FR-006", "slice_id": "SL-005", "lifecycle_status": "Approved",
         "introduced_in": 2},
    ]
    edges = [edge("SL-005", "implements", "FR-006"), edge("WBS-8", "implements", "FR-006"),
             edge("WBS-8", "blocked_by", "OQ-001")]
    return dec, plan, edges


def ok(res, what):
    if not res.get("ok"):
        raise SystemExit(f"SEED REFUSED at {what}: {json.dumps(res)[:1500]}")
    return res


def reading():
    g, r = srv.gate_run(), srv.readiness_check("package")
    return {"gate_ready": g["ready"], "ready": r["ready"],
            "rules": {x["rule"]: x["status"] for x in r["rules"]}}


def main():
    scratch, run = Path(sys.argv[1]).resolve(), sys.argv[2]
    ws = scratch / f"run-{run}"      # built by setup_248.py <scratch> run-<run>, seeded in place
    assert ws.is_dir() and not (ws / "package/data/.lock").exists(), ws
    srv.PACKAGE_ROOT = ws
    ok(srv.package_open("package"), "open")
    before = reading()
    dec, plan, edges = rows_b() if run == "B" else rows_a()
    sc = {"type": "scope-change", "id": "SC-003", "decision_ref": "DEC-003",
          "description": dec["decision"], "iteration": 2, "lifecycle_status": "Approved"}
    ok(srv.entity_upsert([dec, sc]), "decision + scope change")
    added = [r["id"] for r in plan]
    ok(srv.entity_upsert(plan + edges + [edge("SC-003", "scope_adds", i) for i in added]),
       "plan rows")
    # G-PROGRESS: once auditing has begun, every active AC carries a verdict. A criterion the
    # scope change adds starts at Pending (measured: without it gate_run reads ready false).
    ok(srv.audit_record([{"ac_id": r["id"], "verdict": "Pending", "verified_by": "human",
                          "verification_method": "inspection",
                          "evidence": "added by SC-003 (plan 248 seeding); not built yet"}
                         for r in plan if r["type"] == "acceptance-criterion"]), "pending")
    back ={i: srv.entity_query(t, id=i)["rows"][0]["lifecycle_status"]
            for t, i in [(r["type"], r["id"]) for r in plan]}
    print("OBS re-read:", back)
    ok(srv.entity_upsert([{**sc, "lifecycle_status": "Merged"}]), "merge")
    ok(srv.progress_update([{"entry": f"Rehearsal seeding (plan 248, run {run}): DEC-003 and"
                                      f" SC-003 add {', '.join(added)}. SC-003 merged after"
                                      " the re-read.", "event_type": "note", "actor": OP}]),
       "journal")
    after = reading()
    srv.package_close()
    changed = {k: (before["rules"].get(k), v) for k, v in after["rules"].items()
               if before["rules"].get(k) != v}
    print("OBS reading:", before["gate_ready"], before["ready"], "->", after["gate_ready"],
          after["ready"], "| rules changed:", changed or "none")
    git = lambda *a: subprocess.run(["git", *a], cwd=ws, capture_output=True, text=True,
                                    check=True).stdout.strip()
    git("add", "-A")
    git("commit", "-qm", f"plan: run {run} seeding (DEC-003, SC-003)")
    print("OBS commit files:", git("show", "--name-only", "--format=", "HEAD").splitlines())
    print("OBS status clean:", git("status", "--porcelain") == "")


if __name__ == "__main__":
    main()
