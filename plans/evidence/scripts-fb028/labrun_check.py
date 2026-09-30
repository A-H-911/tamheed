"""Plan 172: check a real-agent run's package BY PREDICATE (never by id), in-process through the
engine. Prints one `CHECK <name>: PASS|FAIL <detail>` line per scenario tick; exits 1 on any FAIL.

    env -u TAMHEED_HOOK_LOG python labrun_check.py a1 <plan ws> <exec ws>
    env -u TAMHEED_HOOK_LOG python labrun_check.py a2 <plan ws> <exec ws> <a2 transcript.jsonl>
    env -u TAMHEED_HOOK_LOG python labrun_check.py b  <run-B ws>
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server")); sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

FAILS = []


def check(name, ok, detail: object = ""):
    print(f"CHECK {name}: {'PASS' if ok else 'FAIL'} {json.dumps(detail, default=str)}"[:400])
    if not ok:
        FAILS.append(name)


def rows(table, where="1=1"):
    conn = srv._CURRENT.conn
    cur = conn.execute(f"SELECT * FROM {table} WHERE {where}")
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def rule(name):
    return next((r for r in srv.readiness_check("package")["rules"] if r["rule"] == name), None)


def gates():
    return {k: v for k, v in srv.gate_run()["gates"].items() if k.startswith("G-")}


def open_pkg(ws, name):
    srv.PACKAGE_ROOT = Path(ws).resolve()
    lock = srv.PACKAGE_ROOT / name / "data" / ".lock"
    check("closed-no-lock", not lock.exists(), f"lock present: {lock.exists()}")  # read on the FIRST run only
    if lock.exists():  # a crashed earlier check leaves this script's own lock; the first run's line is the record
        srv.package_unlock(name, confirm=True)
    o = srv.package_open(name)
    assert o["ok"], o
    return o


def tool_calls(transcript):
    out = []
    for line in Path(transcript).read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        m = r.get("message")
        if isinstance(m, dict) and isinstance(m.get("content"), list):
            for c in m["content"]:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    out.append((c["name"], c.get("input") or {}))
    return out


def a1(plan_ws, exec_ws):
    open_pkg(plan_ws, "lab-tracker")
    oq = [q for q in rows("open_questions") if q["owner"] and q["due_by"]]
    check("oq-owner-due", bool(oq), f"{len(oq)} OQ rows with owner+due_by")
    marked = [r for r in rows("requirements") if re.search(r"\[NEEDS-CLARIFICATION: OQ-\d+\]", r.get("statement") or "")]
    check("marker-in-requirement", bool(marked), [r["id"] for r in marked])
    g = gates()
    check("g-complete-with-marker", g["G-COMPLETE"]["status"] == "pass", g["G-COMPLETE"]["status"])
    promoted = [d for d in rows("decisions") if d["promoted_to"]]
    adrs = {a["id"]: a for a in rows("adrs")}
    check("dec-promoted-to-adr-confirmed",
          any(d["promoted_to"] in adrs and (adrs[d["promoted_to"]]["confirmation"] or "").strip() for d in promoted),
          [(d["id"], d["promoted_to"]) for d in promoted])
    dla = rule("decisions-look-architectural")
    check("decisions-look-architectural-clean", dla and dla["status"] == "pass", dla and dla["entities"])
    check("one-phase-two-slices", len(rows("phases")) == 1 and len(rows("slices")) == 2,
          f"{len(rows('phases'))} phases, {len(rows('slices'))} slices")
    acs = rows("acceptance_criteria")
    check("acs-bound-req-and-slice", bool(acs) and all(a["requirement_id"] and a["slice_id"] for a in acs), f"{len(acs)} ACs")
    check("tests-planned", bool(rows("tests")), f"{len(rows('tests'))} tests")
    eg = rows("execution_gates")
    kinds = sorted(x["gate_kind"] for x in eg)
    check("two-gates-ready-approval", kinds == ["approval", "ready"], kinds)
    check("g-trace-pass", g["G-TRACE"]["status"] == "pass", g["G-TRACE"]["status"])
    asb = rule("acs-slice-bound")
    check("acs-slice-bound-clean", asb and asb["status"] == "pass", asb and asb["entities"])
    check("gate-run-all-pass", all(x["status"] == "pass" for x in g.values()),
          {k: v["status"] for k, v in g.items() if v["status"] != "pass"})
    ready = srv.readiness_check("package")
    check("readiness-lists-blockers", not ready["ready"], f"ready={ready['ready']}")
    note = Path(exec_ws) / "CLAUDE.md"
    check("note-span-in-exec", note.exists() and "Tamheed" in note.read_text(encoding="utf-8"), str(note))
    srv.package_close()


def a2(plan_ws, exec_ws, transcript):
    open_pkg(plan_ws, "lab-tracker")
    defs = rows("defects")
    check("def-rows-with-severity", bool(defs) and all(d["severity"] for d in defs),
          [(d["id"], d["severity"], d["lifecycle_status"]) for d in defs])
    calls = tool_calls(transcript)
    first_def = next((i for i, (n, inp) in enumerate(calls) if n.endswith("entity_upsert")
                      and any((it.get("type") == "defect") for it in inp.get("items", []) if isinstance(it, dict))), None)
    first_edit = next((i for i, (n, inp) in enumerate(calls) if n in ("Edit", "Write")
                       and "tracker.py" in str(inp.get("file_path", ""))), None)
    # the DEF rows may predate the executor's session: the planner (A1) recorded them from reading
    # the seed. Then the commit that first carried defects.jsonl must precede the first commit that
    # changed tracker.py after the seed (git order in the executor repo).
    def first_commit(path, skip_seed=False):
        out = subprocess.run(["git", "-C", str(exec_ws), "log", "--reverse", "--format=%H", "--", path],
                             capture_output=True, text=True).stdout.split()
        return out[1] if skip_seed and len(out) > 1 else (out[0] if out else None)
    def_commit, edit_commit = first_commit("lab-tracker/data/defects.jsonl"), first_commit("tracker.py", skip_seed=True)
    order = subprocess.run(["git", "-C", str(exec_ws), "rev-list", "--reverse", "HEAD"], capture_output=True, text=True).stdout.split()
    by_git = def_commit in order and edit_commit in order and order.index(def_commit) < order.index(edit_commit)
    check("def-before-edit", (first_def is not None and (first_edit is None or first_def < first_edit)) or by_git,
          f"A2 transcript: first DEF upsert call #{first_def}, first tracker.py edit call #{first_edit}; "
          f"git: defects.jsonl first in {def_commit and def_commit[:7]}, tracker.py first changed after the seed in {edit_commit and edit_commit[:7]}")
    wd = [p for p in rows("progress_entries") if p["event_type"] == "work-done"]
    check("work-done-typed", bool(wd) and all(p["subject_id"] and p["actor"] for p in wd), f"{len(wd)} work-done")
    av = rows("audit_verdicts")
    sha_ok = []
    for v in av:
        sha = v["against_commit"] or ""
        r = subprocess.run(["git", "-C", str(exec_ws), "cat-file", "-t", sha], capture_output=True, text=True)
        sha_ok.append(bool(sha) and r.stdout.strip() == "commit")
    check("av-agent-method-commit", bool(av) and all(v["verified_by"] and v["verification_method"] for v in av) and all(sha_ok),
          [(v["id"], v["verdict"], v["verified_by"], v["verification_method"], (v["against_commit"] or "")[:8]) for v in av])
    check("flaky-test-file-kept", (Path(exec_ws) / "test_tracker.py").exists())
    sl = {s["id"]: s["lifecycle_status"] for s in rows("slices")}
    check("slices-review-or-implemented", sorted(sl.values()) in (["Implemented", "Implemented"], ["Implemented", "Review"]), sl)
    sc = rows("scope_changes")
    check("sc-merged", any(s["lifecycle_status"] == "Merged" for s in sc), [(s["id"], s["lifecycle_status"]) for s in sc])
    scm = rule("scope-changes-merged")
    check("scope-changes-merged-clean", scm and scm["status"] == "pass", scm and scm["entities"])
    wv = rows("waivers")
    dm = rule("defects-minor")
    check("waiver-and-defects-minor-waived", bool(wv) and dm and dm["status"] == "waived", (len(wv), dm and dm["status"]))
    fo = [p for p in rows("progress_entries") if p["event_type"] == "forced-override"
          and (p["subject_id"] or "").startswith("SL-")]  # the slice's, not a lock removal's
    check("forced-override-event", bool(fo), [(p["id"], p["subject_id"], p["actor"]) for p in fo])
    check("gate-outcomes", all(x["outcome"] for x in rows("execution_gates")), [(x["gate_kind"], x["outcome"]) for x in rows("execution_gates")])
    gd = [p for p in rows("progress_entries") if p["event_type"] == "gate-decision"]
    check("gate-decision-events", len(gd) >= 2, len(gd))
    page = srv.PACKAGE_ROOT / "lab-tracker" / "review.html"
    check("review-page", page.exists(), str(page))
    srv.package_close()


def b(ws):
    """Run B: the package after B1-B4, and the B4 conversation's transcript (its last turn's copy
    holds every turn) for what handoff-repeated said before and after the agent acted."""
    open_pkg(ws, "package")
    hs = [p for p in rows("progress_entries") if p["event_type"] == "handoff"]
    new_hs = [h for h in hs if int(h["id"][3:]) > 61]  # the fixture's last handoff is PE-061 (beat 31)
    check("four-plus-new-handoffs", len(new_hs) >= 4, [h["id"] for h in new_hs])
    check("handoff-last", rows("progress_entries")[-1]["event_type"] == "handoff", rows("progress_entries")[-1]["id"])
    fb = rows("feedback", "plugin_version = '5.8.1' AND kind = 'question'")
    check("feedback-row-confirmed", any(f["lifecycle_status"] == "Confirmed" and f["confirmed_by"] for f in fb),
          [(f["id"], f["lifecycle_status"], f["confirmed_by"]) for f in fb])
    planted = [q for q in rows("open_questions") if "BOM" in (q["question"] or "")]
    check("planted-oq-open-unanswered", bool(planted) and all(not q["resolution"] and q["lifecycle_status"] == "Proposed" for q in planted),
          [(q["id"], q["lifecycle_status"], q["resolution"]) for q in planted])
    pid = planted[0]["id"] if planted else "OQ-?"
    check("planted-question-in-every-handoff", bool(planted) and all(pid in h["entry"] for h in new_hs),
          {"by id": [(pid in h["entry"]) for h in new_hs], "word for word (BOM)": [("BOM" in h["entry"]) for h in new_hs]})
    ll = rows("lessons", "id NOT IN ('LL-001','LL-002','LL-003','LL-004','LL-005')")
    check("lesson-approved-on-word", any(x["lifecycle_status"] == "Approved" for x in ll), [(x["id"], x["lifecycle_status"]) for x in ll])
    tr = sorted(Path(ws).parent.glob("runs/b4-*/transcript.jsonl"))[-1]
    seen = []
    for line in tr.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        m = r.get("message")
        if isinstance(m, dict) and isinstance(m.get("content"), list):
            for c in m["content"]:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    body = c.get("content")
                    text = body if isinstance(body, str) else " ".join(y.get("text", "") for y in body if isinstance(y, dict))
                    for mm in re.finditer(r'"rule": "handoff-repeated",\s*"severity": "advisory",\s*"status": "(\w+)",\s*"entities": \[([^\]]*)\]', text):
                        seen.append((r.get("timestamp"), mm.group(1), mm.group(2).strip()))
    statuses = [s_ for _, s_, _ in seen]
    check("handoff-repeated-fired-then-cleared", "fail" in statuses and statuses[-1] == "pass" and statuses.index("fail") < len(statuses) - 1, seen)
    v = srv.package_verify()
    check("review-exported-by-5.8.1", v["ok"] and v["verified"] and v["review_exported_by"] == "5.8.1", (v.get("review_current"), v.get("review_exported_by")))
    srv.package_close()


if __name__ == "__main__":
    which = sys.argv[1]
    try:
        {"a1": lambda: a1(sys.argv[2], sys.argv[3]),
         "a2": lambda: a2(sys.argv[2], sys.argv[3], sys.argv[4]),
         "b": lambda: b(sys.argv[2])}[which]()
    finally:
        if srv._CURRENT is not None:  # a crash must not leave this script's lock on the agent's package
            srv.package_close()
    print("RESULT", "ALL PASS" if not FAILS else f"FAILS {FAILS}")
    sys.exit(1 if FAILS else 0)
