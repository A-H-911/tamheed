"""Plan 241 (FB-020, R121, R127, R129, R130, R135): the texts of the settled rule, the standup
blocked list and the advisory `blocks-lifted`. Idempotent: a pair already applied is skipped.

    python plans/evidence/scripts-239/docs_241.py
"""
from pathlib import Path

R = Path(__file__).resolve().parents[3]
PRACTICE = (
    "- A `blocked_by` edge is history. It is never retired when the block lifts, because a\n"
    "  retire records a wrong edge. The far row lifts the block when it is settled (v6.7). A\n"
    "  dependency, an assumption or work is settled at Implemented, Superseded, Obsolete or\n"
    "  Rejected. A defect is settled at Fixed, Won't-fix or Duplicate, and deferred work at Done\n"
    "  or Won't-do. A decision is settled once it is decided. A question is settled when\n"
    "  `open-questions-resolved` no longer lists it, so a Deferred question lifts its block. A\n"
    "  risk is settled when `risks-discharged` no longer lists it, whatever its status. A retired\n"
    "  risk that is still `open` keeps blocking. A gate lifts its block only when its `outcome`\n"
    "  column is Go. A journal entry alone lifts nothing, and a later Hold, Redirect or Kill\n"
    "  blocks again. The standup list of blocked work and the advisory `blocks-lifted` read this\n"
    "  one rule.\n")
EDITS = {
    "docs/guide/content.py": [
        ('    "rule.register-entries-conform": {',
         '    "rule.blocks-lifted": {"en": "Open rows whose every `blocked_by` blocker is settled:'
         ' work that is free to start. The edge stays as history. `lifted` names the settled'
         ' blockers of each row (conditional: only when a `blocked_by` edge exists).",\n'
         '                          "ar": "صفوف مفتوحة استقر كل ما يعيقها عبر `blocked_by`: عمل'
         ' يمكن البدء به. وتبقى الحافة سجلًا للتاريخ. ويسمّي `lifted` المعيقات المستقرة لكل صف'
         ' (شرطية: فقط عند وجود حافة `blocked_by`)."},\n'
         '    "rule.register-entries-conform": {'),
        ("That row is work, a question, a dependency, a decision, a risk, an assumption or an"
         " execution gate.",
         "That row is work, a question, a dependency, a decision, a risk, an assumption or an"
         " execution gate. The block lifts when that row is settled, such as a met dependency at"
         " `Implemented`. The edge stays as history."),
        ("أو افتراض أو بوابة تنفيذ.\"",
         "أو افتراض أو بوابة تنفيذ. ويرتفع العائق متى استقر ذلك الصف، كتبعية مستوفاة في الحالة"
         " `Implemented`. وتبقى الحافة سجلًا للتاريخ.\""),
        ("A `blocked_by` edge can point work at a dependency.\"",
         "A `blocked_by` edge can point work at a dependency. A met dependency takes"
         " `Implemented`, and then it blocks nothing.\""),
        ("وتستطيع حافة `blocked_by` أن تشير بالعمل إلى تبعية.\"",
         "وتستطيع حافة `blocked_by` أن تشير بالعمل إلى تبعية. وتأخذ التبعية المستوفاة الحالة"
         " `Implemented`، وعندها لا تعيق شيئًا.\""),
    ],
    "plugins/tamheed/references/governance.md": [
        ("  rules. Phase/slice transitions to Implemented are guarded.",
         "  rules. For a dependency, an assumption or an execution plan, Implemented means met:\n"
         "  the row then blocks nothing. Phase/slice transitions to Implemented are guarded."),
        ("- A full-row update that only means to flip a status names the columns it did NOT mean to",
         PRACTICE + "- A full-row update that only means to flip a status names the columns it did"
         " NOT mean to"),
    ],
    "plugins/tamheed/references/quality-gates.md": [
        ("  The waivers: operator-approved `WVR-` rows reported `waived`, never silent, and expiring. The\n"
         "  advisory liveness rules, twenty-four at package scope (measured on the lab fixture at v5.8). Four\n"
         "  of them exist only when the package has waivers, feedback or skill rows, or three handoffs. And\n",
         "  The waivers: operator-approved `WVR-` rows reported `waived`, never silent, and expiring. The\n"
         "  advisory liveness rules at package scope. Six of them exist only when the package has\n"
         "  waivers, feedback rows, a register, skill rows, three handoffs or a `blocked_by` edge. And\n"),
        ("  the package has a register. Since v4.12",
         "  the package has a register. `blocks-lifted` (v6.7) lists open rows whose every\n"
         "  `blocked_by` blocker is settled: work that is free to start. It exists only when the\n"
         "  package has a `blocked_by` edge, and the edge stays as history. Since v4.12"),
    ],
    "plugins/tamheed/server/README.md": [
        ("register-entries-conform` (v6.5, only when the package has a register) lists the live"
         " register entries that the current declaration does not admit, with `problems` per"
         " entry.",
         "register-entries-conform` (v6.5, only when the package has a register) lists the live"
         " register entries that the current declaration does not admit, with `problems` per"
         " entry. `blocks-lifted` (v6.7, only when a `blocked_by` edge exists) lists open rows"
         " whose every blocker is settled, with `lifted` per row."),
    ],
    "docs/entities.md": [
        ("`owner` (RAID practice: an unowned dependency is a hope). Retire when delivered or\n"
         "designed around.",
         "`owner` (RAID practice: an unowned dependency is a hope). A met dependency takes\n"
         "`Implemented` (v6.7): it then blocks nothing, and its `blocked_by` edges stay as history.\n"
         "Retire it when it is designed around."),
    ],
    "plugins/tamheed/skills/standup/SKILL.md": [
        ("   The result holds the facts, the rule colour with its reasons, and the word shares. It also\n"
         "   writes `reports/draft.html`.\n",
         "   The result holds the facts, the rule colour with its reasons, and the word shares. It also\n"
         "   writes `reports/draft.html`. The list of blocked work names a slice or a WBS item only\n"
         "   while its blocker is not settled. A met dependency at `Implemented` blocks nothing.\n"),
    ],
    "plugins/tamheed/skills/register-liveness/SKILL.md": [
        ("    A retired entry is never listed.\n24. Close the sweep:",
         "    A retired entry is never listed.\n"
         "24. **Work that is free to start** (`blocks-lifted`, v6.7): open rows whose every\n"
         "    `blocked_by` blocker is settled. The rule is emitted only when the package has a\n"
         "    `blocked_by` edge. `lifted` names the settled blockers of each row. The edge stays as\n"
         "    history: never retire it. Start the work, or record what it now waits on as a new\n"
         "    edge. A deliberate wait is a `WVR-` row, on the operator's word.\n"
         "25. Close the sweep:"),
    ],
}
ENTRY = (
    "- **Work that is free to start (plan 241, the field's FB-020, R121, R127, R130).** The\n"
    "  standup list of blocked work read only the `blocked_by` edge, so a met dependency still\n"
    "  blocked its slice. A blocker now lifts the block when it is settled, by one rule per\n"
    "  family. A met dependency takes `Implemented`. The new advisory `blocks-lifted` lists open\n"
    "  rows whose every blocker is settled. It exists only when a `blocked_by` edge exists. The\n"
    "  edge stays as history, and nothing is retired.\n")
for rel, pairs in EDITS.items():
    path = R / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in text:
            continue
        assert text.count(old) == 1, (rel, text.count(old), old[:60])
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="\n")
log = R / "CHANGELOG.md"
text = log.read_text(encoding="utf-8")
if ENTRY not in text:
    anchor = "### Added\n\n"
    assert text.count(anchor) >= 1 and text.index(anchor) < text.index("## [6.6.0]")
    text = text.replace(anchor, anchor + ENTRY + "\n", 1)
    log.write_text(text, encoding="utf-8", newline="\n")
print("docs 241 written")
