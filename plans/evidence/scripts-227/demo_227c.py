"""A demo slate of invented text, shaped like a real workshop page (plan 227c).

Usage: demo_227c.py <repo> <out root> [ar]
"""
import json
import shutil
import sys
from pathlib import Path

repo, root = Path(sys.argv[1]), Path(sys.argv[2])
arabic = len(sys.argv) > 3 and sys.argv[3] == "ar"
sys.path.insert(0, str(repo / "plugins" / "tamheed" / "server"))
sys.path.insert(0, str(repo / "plugins" / "tamheed" / "db"))
import tamheed_server as srv  # noqa: E402

if root.exists():
    shutil.rmtree(root)
root.mkdir(parents=True)
srv.PACKAGE_ROOT = root
assert srv.package_create("demo", "Demo", "rnd")["ok"]
rows = [
    {"type": "requirement", "id": "FR-001", "kind": "functional", "title": "Audit trail",
     "statement": ("The service keeps every audit event for seven years. An event holds the "
                   "actor, the action, the target and the time."),
     "lifecycle_status": "Approved", "source_kind": "brief", "source_span": "section 4.2"},
    {"type": "requirement", "id": "FR-002", "kind": "functional", "title": "Export",
     "statement": "An auditor exports one year of events as CSV.", "lifecycle_status": "Approved",
     "source_kind": "brief", "source_span": "section 4.3"},
    {"type": "constraint", "id": "CON-001", "title": "All data stays in one region"},
    {"type": "constraint", "id": "CON-002", "title": "The budget holds one managed store"},
    {"type": "decision", "id": "DEC-001", "title": "Events are written on every request",
     "lifecycle_status": "Proposed"},
    {"type": "stakeholder", "id": "STK-001", "title": "Operator"},
    {"type": "stakeholder", "id": "STK-002", "title": "API Gateway team"},
    {"type": "stakeholder", "id": "STK-003", "title": "Security"},
    {"type": "stakeholder", "id": "STK-004", "title": "Operations"},
    {"type": "stakeholder", "id": "STK-005", "title": "Business owners"},
    {"type": "glossary-term", "id": "GT-001", "term": "audit trail",
     "definition": "The ordered list of who did what, and when.",
     "custom_attributes": json.dumps({"variants": ["audit log"]})},
    {"type": "glossary-term", "id": "GT-002", "term": "managed store",
     "definition": "A database that the cloud provider runs and patches."},
    {"type": "glossary-term", "id": "GT-003", "term": "tenant",
     "definition": "One customer of the service."},
]
out = srv.entity_upsert(rows)
assert out["ok"], out

ABCD = lambda a, b, c, d: [{"id": k, "label": v} for k, v in zip("ABCD", (a, b, c, d))]  # noqa: E731
slate = {
    "name": "workshop", "title": "Storage and access workshops",
    "intro": "One round for each topic. Each question shows what we already know.",
    "participants": ["STK-002", "STK-003", "STK-004",
                     {"id": "STK-001", "attends": False}, {"id": "STK-005", "attends": False}],
    "rounds": [
        {"id": "storage", "title": "Storage",
         "intro": "Where the audit trail lives, and how long an export may take.",
         "cites": ["CON-001"],
         "decided": [
             {"id": "T001", "title": "The region of the data", "cites": ["CON-001"],
              "answer": "One region, by CON-001. DEC-001 fixed when an event is written."},
             {"id": "T002", "title": "Who may read the gateway logs",
              "answer": "The two engineers named in the authorization."}],
         "blocks": [
             {"title": "The audit trail", "questions": [
                 {"id": "Q003", "question": "Which store keeps the audit trail?",
                  "detail": "It is written on every request and read by an auditor a few times a year.",
                  "options": ABCD("Keep the managed store that the service already has",
                                  "Move audit events to object storage",
                                  "A second managed store for audit only",
                                  "Decide after a load test"),
                  "recommended": "A", "basis": "evidence",
                  "reason": "It meets the two-second query today, and CON-002 holds one store.",
                  "owner": "room", "lead": "STK-002", "consulted": ["STK-003", "STK-005"],
                  "known": ["FR-001"], "decided": ["CON-002", "DEC-001"],
                  "depends_on": ["T001"], "settles": "FR-001",
                  "gap": "Nobody has measured a query over seven years of events."},
                 {"id": "Q004", "question": "How long may an export take?",
                  "options": ABCD("One minute", "Ten minutes",
                                  "It runs in the background, and the auditor is told",
                                  "Requires a measurement first"),
                  "recommended": "C", "basis": "practice",
                  "reason": "A year of events is about 12 million rows.",
                  "lead": "STK-004", "consulted": ["STK-002"], "known": ["FR-002"],
                  "depends_on": ["Q003"]}]},
             {"title": "Cost and sign-off", "questions": [
                 {"id": "Q005", "question": "Does each tenant pay for its own audit storage?",
                  "options": ABCD("Yes, by size", "Yes, a flat fee", "No, it is in the price",
                                  "Only above a quota"),
                  "lead": "STK-005", "consulted": ["STK-002"]},
                 {"id": "Q006", "question": "Does the operator accept a second managed store?",
                  "options": ABCD("Accepted", "Not accepted", "Accepted for one year",
                                  "Requires a cost figure first"),
                  "owner": "operator", "lead": "STK-001", "approval": True,
                  "recommended": "B", "basis": "ruling", "reason": "CON-002 holds one store.",
                  "decided": ["CON-002"], "depends_on": ["Q003"]}]}]},
        {"id": "access", "title": "Access and keys",
         "questions": [
             {"id": "Q007", "question": "Is each audit event encrypted with its own key?",
              "options": [{"id": "A", "label": "Yes"}, {"id": "B", "label": "No"}],
              "lead": "STK-003"},
             {"id": "Q008", "question": "Who may read the audit trail in production?",
              "options": ABCD("Security only", "Security and Operations", "Anyone on call",
                              "Nobody without a ticket"),
              "recommended": "D", "basis": "practice", "reason": "Every read leaves a ticket.",
              "lead": "STK-003", "consulted": ["STK-004"]}]},
        {"id": "migration", "title": "Migration waves", "ready": False}]}

if arabic:
    slate |= {"name": "workshop-ar", "language": "ar", "title": "ورش التخزين والوصول",
              "intro": "جولة لكل موضوع. كل سؤال يعرض ما نعرفه."}
    first = slate["rounds"][0]
    first["title"] = "التخزين"
    first["intro"] = "أين يُحفظ سجل التدقيق، وكم يستغرق التصدير."
    q = first["blocks"][0]["questions"][0]
    q["question"] = "أي مخزن يحفظ سجل التدقيق؟"
    q["detail"] = "يُكتب عند كل طلب، ويقرؤه المدقق مرات قليلة في السنة."
    q["reason"] = "يحقق استعلام الثانيتين اليوم، والميزانية تحتمل مخزنًا واحدًا."
    q["gap"] = "لم يقس أحد استعلامًا على سبع سنوات من الأحداث."
    for option, label in zip(q["options"], ("نبقي المخزن المُدار الحالي", "ننقل الأحداث إلى تخزين الكائنات",
                                            "مخزن مُدار ثانٍ للتدقيق فقط", "نقرر بعد اختبار الحمل")):
        option["label"] = label
    first["blocks"][0]["title"] = "سجل التدقيق"
    first["decided"][0]["title"] = "منطقة البيانات"
    first["decided"][0]["answer"] = "منطقة واحدة، بحسب CON-001."

result = srv.slate_export(slate)
assert result["ok"], result
srv.package_close()
print(json.dumps({"page": result["page"], "questions": result["questions"],
                  "rounds": result["rounds"], "rows": result["quoted_rows"]}))
