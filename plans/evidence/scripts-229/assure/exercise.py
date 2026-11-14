"""The 6.5.0 tools over the REAL rows of a migrated copy, in one process.

Usage: python -I exercise.py <bundle dir> <package root> <package name>
Prints one line per call: its name, ok or the refusal's first words, and counts. No row text.
"""
import json
import sys
from pathlib import Path

bundle, root, name = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, str(bundle / "server"))
sys.path.insert(0, str(bundle / "db"))
import tamheed_server as srv  # noqa: E402

srv.PACKAGE_ROOT = root
bad = 0


def say(label: str, ok, more="") -> None:
    global bad
    bad += 0 if ok else 1
    print(("ok   " if ok else "FAIL ") + label + (" | " + str(more)[:170] if more != "" else ""))


opened = srv.package_open(name)
say("package_open", opened.get("ok"), opened.get("error", ""))
families = sorted(srv.ENTITY_TABLES)
total = 0
for family in families:
    if family in ("trace-edge", "omission"):          # write-only families
        continue
    got = srv.entity_query(family, limit=100000)
    if not got.get("ok"):
        say(f"entity_query {family}", False, got.get("error"))
    total += got.get("total", 0)
say(f"entity_query over {len(families) - 1} families", True, f"{total} rows read")
links = srv.trace_query()
say("trace_query, every link", links.get("ok"),
    {k: links.get(k) for k in ("count", "total", "column_count", "column_total")})
exported = srv.entity_export(path="assurance-links.json", tool="trace_query", args={})
say("entity_export of the links", exported.get("ok"), exported.get("error", ""))
again = srv.entity_export(path="assurance-links.json", tool="trace_query", args={})
say("the same export twice gives one digest", exported.get("digest") == again.get("digest"))
first_req = srv.entity_query("requirement", limit=1)["rows"]
if first_req:
    one = srv.trace_query(first_req[0]["id"])
    say("trace_query of one requirement", one.get("ok"),
        f"{one.get('count')} edges, {one.get('column_count')} column links")
gates = srv.gate_run()
say("gate_run", gates.get("ok", True), {"ready": gates.get("ready")})
rep = srv.readiness_check("package")
say("readiness_check(package)", "rules" in rep, f"{len(rep.get('rules', []))} rules")
page = srv.export_html()
say("export_html over the real rows", page.get("ok"), page.get("error", ""))
verify = srv.package_verify()
say("package_verify after the export", verify.get("verified") and verify.get("review_current"),
    {k: verify.get(k) for k in ("verified", "dirty", "review_current", "review_exported_by")})

# the new families and the new status, written beside the real rows
reg = srv.entity_upsert([
    {"type": "register", "id": "REG-9990", "title": "Assurance register",
     "custom_attributes": {"fields": [{"name": "state", "required": True,
                                       "values": ["open", "closed"]},
                                      {"name": "about", "refs": True}]}}])
say("a register is declared", reg.get("ok"), reg.get("error") or reg.get("items"))
about = first_req[0]["id"] if first_req else None
entry = srv.entity_upsert([
    {"type": "register-entry", "id": "ENT-9990", "register_id": "REG-9990", "title": "One entry",
     "custom_attributes": {"state": "open", "about": about}}])
say("an entry that fits is admitted", entry.get("ok"), entry.get("error") or entry.get("items"))
wrong = srv.entity_upsert([
    {"type": "register-entry", "id": "ENT-9991", "register_id": "REG-9990", "title": "Bad",
     "custom_attributes": {"state": "maybe"}}])
say("an entry that does not fit is refused", not wrong.get("ok"))
section = srv.entity_query("document-section", limit=1)["rows"]
if section:
    retired = srv.entity_upsert([
        {"type": "document-section", "id": "SEC-9990", "document_id": section[0]["document_id"],
         "heading": "Assurance section", "body": "A section for the assurance run.",
         "sort_order": 99990, "lifecycle_status": "Obsolete"}])
    say("a section is written as retired", retired.get("ok"),
        retired.get("error") or retired.get("items"))
    only = srv.entity_query("document-section", status="Obsolete")
    say("the status filter returns it", "SEC-9990" in {r["id"] for r in only.get("rows", [])})
refused = srv.entity_upsert([{"type": "constraint", "title": "no id"}])
say("a write with no id is refused", not refused.get("ok"))
people = [r["id"] for r in srv.entity_query("stakeholder", limit=3).get("rows", [])]
slate = {"name": "assurance", "title": "Assurance", "participants": people[:2],
         "rounds": [{"id": "r1", "title": "One round",
                     "cites": [about] if about else [],
                     "questions": [{"id": "q1", "question": "Does the page hold?",
                                    "options": [{"id": "A", "label": "Yes"},
                                                {"id": "B", "label": "No"}],
                                    "known": ["ENT-9990"], "settles": about,
                                    "lead": people[0] if people else None,
                                    "recommended": "A", "reason": "It was measured.",
                                    "basis": "evidence"}]}]}
out = srv.slate_export(slate)
say("slate_export over real rows", out.get("ok"),
    out.get("error") or {k: out.get(k) for k in ("questions", "quoted_rows")})
if out.get("ok"):
    import slate as slates
    record = json.loads(Path(out["record"]).read_text(encoding="utf-8"))
    digest = slates.question_digests(record)["q1"]
    Path(out["round_answers"]["r1"]).write_text(json.dumps({
        "format": slates.ANSWERS_FORMAT, "version": slates.VERSION, "slate": "assurance",
        "round": "r1", "rounds": [], "answers": [{"question": "q1", "selected": "A",
                                                  "question_digest": digest}]}), encoding="utf-8")
    read = srv.slate_read("assurance")
    say("slate_read of one round file", read.get("ok") and read.get("put_again") == [],
        read.get("error") or {"answered": len(read["answers"]) - len(read["unanswered"])})
    again = srv.slate_export(slate)
    say("a second export moves no byte", set(again.get("files", {"x": "?"}).values()) == {"unchanged"})
gates2 = srv.gate_run()
say("the gates still give the same verdict after these writes",
    gates2.get("ready") == gates.get("ready"),
    {"before": gates.get("ready"), "after": gates2.get("ready"),
     "failing": [k for k, v in gates2.get("gates", {}).items()
                 if isinstance(v, dict) and v.get("status") == "fail"]})
closed = srv.package_close()
say("package_close", closed.get("ok"), closed.get("error", ""))
reopened = srv.package_open(name)
say("the package opens again", reopened.get("ok"), reopened.get("error", ""))
verify = srv.package_verify()
say("the store verifies after the reopen", verify.get("verified"), verify.get("dirty"))
srv.package_close()
print(f"exercise: {bad} failed")
