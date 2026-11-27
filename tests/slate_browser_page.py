"""Build two interview pages for the browser check (plan 257, R154).

    python tests/slate_browser_page.py <out dir>

The demo slate of plan 227c (every part of a page: rounds, blocks, decided topics, an operator
question, participants, recommendations, a round that is not ready), with three additions
from Jisr's FB-032, FB-034 and FB-033:

- the slate's intro and a round's intro run over two lines;
- a long word sits in every text field (the field's file path, and a sha256 digest that has no
  place to break): titles, the question, its detail, the labels and details of the options, the reason,
  the gap and a decided answer;
- `keyed.html` sets `show_recommendations`, and `plain.html` does not.

Both pages go to <out dir>. The temporary package is removed. It loads no field data.
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "plugins/tamheed/server"), str(REPO / "plugins/tamheed/db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

# The field's path wraps at its hyphens under the normal rules of line breaking, so on its own it
# did not overflow this page. A sha256 digest has no place to break, and such digests are common
# in the texts of a package, so every long text holds both.
PATH = "(raw/85-owasp-api2023-0xa8-security-misconfiguration.html):"
DIGEST = "e2e74be412af0c5cbf4763d3bd6c994bda917d6f579bcaba3aa3f8a359a4e13e"
LONG = PATH + " " + DIGEST
assert len(DIGEST) == 64 and " " not in PATH

ROWS = [
    {"type": "requirement", "id": "FR-001", "kind": "functional", "title": "Audit trail",
     "statement": "The service keeps every audit event for seven years.",
     "lifecycle_status": "Approved", "source_kind": "brief", "source_span": "section 4.2"},
    {"type": "requirement", "id": "FR-002", "kind": "functional", "title": "Export",
     "statement": "An auditor exports one year of events as CSV.", "lifecycle_status": "Approved",
     "source_kind": "brief", "source_span": "section 4.3"},
    {"type": "constraint", "id": "CON-001", "title": "All data stays in one region"},
    {"type": "constraint", "id": "CON-002", "title": "The budget holds one managed store"},
    {"type": "decision", "id": "DEC-001", "title": "Events are written on every request",
     "lifecycle_status": "Proposed"},
    {"type": "stakeholder", "id": "STK-001", "title": "Operator"},
    {"type": "stakeholder", "id": "STK-002", "title": "API Gateway team " + LONG},
    {"type": "stakeholder", "id": "STK-003", "title": "Security"},
    {"type": "stakeholder", "id": "STK-004", "title": "Operations"},
    {"type": "stakeholder", "id": "STK-005", "title": "Business owners"},
    {"type": "glossary-term", "id": "GT-001", "term": "audit trail",
     "definition": "The ordered list of who did what, and when.",
     "custom_attributes": json.dumps({"variants": ["audit log"]})},
]


def options(*labels):
    return [{"id": k, "label": v} for k, v in zip("ABCD", labels)]


SLATE = {
    "name": "browser-check", "title": "Storage and access workshops " + LONG,
    "intro": "One round for each topic.\nEach question shows what we already know.",
    "participants": ["STK-002", "STK-003", "STK-004",
                     {"id": "STK-001", "attends": False}, {"id": "STK-005", "attends": False}],
    "rounds": [
        {"id": "storage", "title": "Storage " + LONG,
         "intro": "1. Where the audit trail lives.\n2. How long an export may take " + LONG,
         "cites": ["CON-001"],
         "decided": [
             {"id": "T001", "title": "The region of the data", "cites": ["CON-001"],
              "answer": "One region, by CON-001.\nSee " + LONG}],
         "blocks": [
             {"title": "The audit trail " + LONG, "questions": [
                 {"id": "Q003", "question": "Which store keeps the audit trail? " + LONG,
                  "detail": "It is written on every request.\nThe file " + LONG + " holds it.",
                  "options": [
                      {"id": "A", "label": "Keep the managed store " + LONG},
                      {"id": "B", "label": "Move audit events to object storage",
                       "detail": "The archive " + LONG + " moves first."},
                      {"id": "C", "label": "A second managed store for audit only"},
                      {"id": "D", "label": "Decide after a load test"}],
                  "recommended": "A", "basis": "evidence",
                  "reason": "It meets the query time today.\nIt keeps one store " + LONG,
                  "owner": "room", "lead": "STK-002", "consulted": ["STK-003", "STK-005"],
                  "known": ["FR-001"], "decided": ["CON-002", "DEC-001"],
                  "depends_on": ["T001"], "settles": "FR-001",
                  "gap": "Nobody has measured a query over " + LONG},
                 {"id": "Q004", "question": "How long may an export take?",
                  "options": options("One minute", "Ten minutes", "In the background",
                                     "Requires a measurement first"),
                  "recommended": "C", "basis": "practice",
                  "reason": "A year of events is about 12 million rows.",
                  "lead": "STK-004", "consulted": ["STK-002"], "known": ["FR-002"],
                  "depends_on": ["Q003"]}]},
             {"title": "Sign-off", "questions": [
                 {"id": "Q006", "question": "Does the operator accept a second managed store?",
                  "options": options("Accepted", "Not accepted", "Accepted for one year",
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
              "options": options("Security only", "Security and Operations", "Anyone on call",
                                 "Nobody without a ticket"),
              "recommended": "D", "basis": "practice", "reason": "Every read leaves a ticket.",
              "lead": "STK-003", "consulted": ["STK-004"]}]},
        {"id": "migration", "title": "Migration waves", "ready": False}]}


def build(out_dir: Path) -> list[Path]:
    root = Path(tempfile.mkdtemp(prefix="slate-check-"))
    written = []
    try:
        srv.PACKAGE_ROOT = root
        assert srv.package_create("demo", "Browser check", "rnd")["ok"]
        up = srv.entity_upsert(ROWS)
        assert up["ok"], up
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, keyed in (("plain", False), ("keyed", True)):
            slate = copy.deepcopy(SLATE) | {"name": f"browser-check-{name}"}
            if keyed:
                slate["show_recommendations"] = True
            result = srv.slate_export(slate)
            assert result["ok"], result
            target = out_dir / f"{name}.html"
            shutil.copyfile(result["page"], target)
            written.append(target)
        srv.package_close()
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return written


if __name__ == "__main__":
    for path in build(Path(sys.argv[1])):
        print(path)
