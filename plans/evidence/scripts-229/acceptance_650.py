"""Plan 229: one scratch scenario through every behaviour that the 6.5.0 round changed, driven
through the real handlers on a package made for the run. It prints one OBS line per behaviour
and stops at the first one that does not hold. Run from the repository root:

    python plans/evidence/scripts-229/acceptance_650.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import store  # noqa: E402
import tamheed_server as srv  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def obs(key: str, holds: bool, value="") -> None:
    print(f"OBS {key}: {'holds' if holds else 'FAILS'} {json.dumps(value, ensure_ascii=False, default=str)[:160]}")
    if not holds:
        raise SystemExit(f"acceptance stopped at {key}")


def up(*items) -> dict:
    return srv.entity_upsert(list(items))


def main() -> int:
    tmp = tempfile.TemporaryDirectory()
    srv.PACKAGE_ROOT = Path(tmp.name)
    assert srv.package_create("accept", "Acceptance", "rnd")["ok"]
    assert up(
        {"type": "requirement", "id": "FR-001", "kind": "functional", "title": "Store",
         "lifecycle_status": "Approved", "source_kind": "brief", "source_span": "p1"},
        {"type": "requirement", "id": "FR-002", "kind": "functional", "title": "Ship",
         "lifecycle_status": "Approved", "source_kind": "brief", "source_span": "p2"},
        {"type": "decision", "id": "DEC-001", "title": "Engine", "lifecycle_status": "Proposed"},
        {"type": "acceptance-criterion", "id": "AC-001", "title": "It stores",
         "requirement_id": "FR-001"},
        {"type": "trace-edge", "from_id": "FR-001", "to_id": "DEC-001", "relation": "derives_from"},
        {"type": "narrative-document", "id": "DOC-001", "title": "Notes", "doc_kind": "charter"},
        {"type": "document-section", "id": "SEC-001", "document_id": "DOC-001", "heading": "One",
         "body": "kept"},
        {"type": "document-section", "id": "SEC-002", "document_id": "DOC-001", "heading": "Two",
         "body": "TODO later"})["ok"], "the seed rows"

    # 221: the read names every link
    one = srv.trace_query("FR-001")
    obs("221 a column link is returned", one["column_links"] ==
        {"acceptance_criteria.requirement_id": [["AC-001", "FR-001"]]}, one["column_links"])
    every = srv.trace_query()
    obs("221 the bulk read has a total and an echo",
        every["total"] == 1 and every["query"] == {}, [every["total"], every["query"]])
    obs("221 an unknown relation carries a warning", "warning" in srv.trace_query(relation="nope"))

    # 222: requirements-wired reads the legs
    wired = srv.gate_run()["gates"]["requirements_unwired"]
    obs("222 the missing legs are named", wired["missing"] == {"FR-002": ["decision", "work", "test"]},
        wired["missing"])

    # 223: a refused value names what the column takes
    bad = up({"type": "decision", "id": "DEC-002", "title": "x", "lifecycle_status": "Done"})
    obs("223 the refusal lists the values", "is not one of:" in bad["items"][0]["error"],
        bad["items"][0]["error"][-90:])

    # 224: the lock records the boot session where the platform has one
    payload = store.lock_payload()
    obs("224 the lock payload carries a boot key", "boot" in payload, sorted(payload))

    # 225: a section can be retired
    assert up({"type": "document-section", "id": "SEC-002", "document_id": "DOC-001",
               "heading": "Two", "body": "TODO later", "lifecycle_status": "Obsolete"})["ok"]
    graded = {f["id"] for f in srv.gate_run()["gates"]["G-COMPLETE"]["failures"]}
    obs("225 a retired section leaves the content gate", "SEC-002" not in graded, sorted(graded))

    # 226: project registers, and the three older write-path defects
    assert up({"type": "register", "id": "REG-001", "title": "Sources", "custom_attributes": {
        "fields": [{"name": "status", "required": True, "values": ["approved", "refused"]},
                   {"name": "grants", "refs": True}]}},
        {"type": "register-entry", "id": "ENT-001", "register_id": "REG-001", "title": "One",
         "custom_attributes": {"status": "approved", "grants": ["FR-001"]}})["ok"]
    refused = up({"type": "register-entry", "id": "ENT-002", "register_id": "REG-001",
                  "title": "Two", "custom_attributes": {"status": "maybe", "grants": "FR-001, FR-002"}})
    obs("226 an entry outside its declaration is refused, every cause named",
        "is not one of" in refused["items"][0]["error"] and "names no row" in refused["items"][0]["error"])
    rule = {r["rule"]: r for r in srv.readiness_check("package")["rules"]}["register-entries-conform"]
    obs("226 the advisory reads the entries", rule["status"] == "pass", rule["population"])
    obs("226 a write with no id is refused",
        "needs a text `id`" in up({"type": "constraint", "title": "no id"})["items"][0]["error"])
    deep = "x"
    for _ in range(40):
        deep = [deep]
    obs("226 a value nested too deep is refused", "nests deeper than" in up(
        {"type": "constraint", "id": "CON-001", "title": "t", "custom_attributes": deep})["items"][0]["error"])
    half = up({"type": "constraint", "id": "CON-002", "title": "first"},
              {"type": "slice", "id": "SL-900", "title": "x", "phase_id": ["PH-1"]})
    obs("226 a refused batch leaves nothing behind", not half["ok"]
        and srv.entity_query("constraint", id="CON-002")["total"] == 0
        and not srv._CURRENT.conn.in_transaction)

    # 227: the interview page
    slate = {"name": "accept-round", "title": "A round", "rounds": [{"id": "r1", "title": "Access",
             "questions": [{"id": "q1", "question": "Which?", "cites": ["FR-001", "ENT-001"],
                            "options": [{"id": "A", "label": "Keep"}, {"id": "B", "label": "Move"}],
                            "recommended": "A", "reason": "It is measured."}]}]}
    exported = srv.slate_export(slate)
    obs("227 the page and its record are written", exported["ok"] and exported["quoted_rows"] == 2,
        exported.get("files"))
    obs("227 a second export moves no byte",
        set(srv.slate_export(slate)["files"].values()) == {"unchanged"})
    obs("227c the export writes two hand-outs",
        all(Path(sheet).is_file() for sheet in exported["handouts"].values()))
    page = Path(exported["page"]).read_text(encoding="utf-8")
    obs("227 the page holds one script", page.count("<script") == 1)
    import slate as slates
    digest_of_q1 = slates.question_digests(
        json.loads(Path(exported["record"]).read_text(encoding="utf-8")))["q1"]
    Path(exported["answers_path"]).write_text(json.dumps({
        "format": "tamheed-slate-answers", "version": 2, "slate": "accept-round",
        "slate_digest": exported["slate_digest"], "exported_at": "2026-11-12T10:00:00.000Z",
        "rounds": [{"id": "r1", "closed": False, "closed_by": "", "closure": {}}],
        "answers": [{"question": "q1", "selected": "B", "other": "", "note": "",
                     "question_digest": digest_of_q1}]}), encoding="utf-8")
    before = srv._CURRENT.conn.total_changes
    read = srv.slate_read("accept-round")
    obs("227 the reader returns a transcript and writes nothing", read["ok"]
        and read["answers"][0]["selected_label"] == "Move" and read["provenance"] == "unverified"
        and srv._CURRENT.conn.total_changes == before)
    obs("227c an unchanged question is not put again, and the round names what it lacks",
        read["put_again"] == [] and read["question_changed"] == []
        and read["rounds"][0]["complete"] is False and len(read["rounds"][0]["missing"]) == 1)
    Path(exported["round_answers"]["r1"]).write_text(json.dumps({
        "format": "tamheed-slate-answers", "version": 2, "slate": "accept-round", "round": "r1",
        "rounds": [], "answers": [{"question": "q1", "selected": "A"}]}), encoding="utf-8")
    both = srv.slate_read("accept-round")
    obs("227c two files that disagree are a conflict, and neither is picked",
        [c.get("question") for c in both["conflicts"]] == ["q1"]
        and both["answers"][0]["selected"] is None)
    Path(exported["round_answers"]["r1"]).unlink()
    assert up({"type": "register-entry", "id": "ENT-001", "register_id": "REG-001", "title": "One",
               "custom_attributes": {"status": "refused", "grants": ["FR-001"]}})["ok"]
    obs("227 a changed row puts its question again", srv.slate_read("accept-round")["put_again"] == ["q1"])

    # 228: the review page names the legs, and renders the register
    review = Path(srv.export_html()["path"]).read_text(encoding="utf-8")
    obs("228 the review page names the missing legs", "FR-002 (decision, work, test)" in review)
    obs("226 the review page renders the register", "<summary>REG-001 Sources (1 row)" in review)
    obs("the review page still runs no script", "<script" not in review)

    srv.package_close()
    assert srv.package_open("accept")["ok"]
    verify = srv.package_verify()
    obs("the store verifies after a close and a reopen", verify["verified"], verify.get("dirty"))
    srv.package_close()
    tmp.cleanup()
    print("ACCEPTANCE-650-DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
