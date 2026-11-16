"""Plan 246b (R144): a withdrawal takes the newest place in the chain whole, the newest report
with every report it corrects. The texts follow, and the round record gains R141-R144. Run after
docs_246.py and docs_246b.py. Idempotent.

    python plans/evidence/scripts-239/docs_246c.py
"""
from pathlib import Path

R = Path(__file__).resolve().parents[3]
EDITS = {
    "plugins/tamheed/server/tamheed_server.py": [(
        '" when nothing names it. The journal keeps a note without the words, and the id is never"',
        '" when nothing names it. It takes the reports it corrects with it. The journal keeps a"\n'
        '    " note without the words, and the id is never"')],
    "plugins/tamheed/server/README.md": [
        ("`withdraw` (v6.7) removes the newest daily report or an override report on the operator's word",
         "`withdraw` (v6.7) removes the newest daily report or an override report on the operator's"
         " word, with the reports it corrects"),
        ("standup_report(action?, narrative?, start?, utc_offset?, supersede?, confirm?)",
         "standup_report(action?, narrative?, start?, utc_offset?, supersede?, confirm?, report?)")],
    "docs/guide/content.py": [
        ("`withdraw` removes the newest daily report or an override report, on the operator's word.",
         "`withdraw` removes the newest daily report or an override report, on the operator's word,"
         " with the reports it corrects."),
        ("و`withdraw` يزيل أحدث تقرير يومي أو تقرير تجاوز بكلمة المشغّل.",
         "و`withdraw` يزيل أحدث تقرير يومي أو تقرير تجاوز بكلمة المشغّل، مع التقارير التي يصححها."),
        ("Aborts the removal of a recorded report that the chain needs: a correction, or a report"
         " that another report names or follows. A draft, the newest daily report and an override"
         " report can be removed (v6.7).",
         "Aborts the removal of a recorded report that another report names or follows. A draft,"
         " the newest place in the chain, whole, and an override report can be removed (v6.7)."),
        ("يُبطل إزالة تقرير مسجَّل تحتاجه السلسلة: تصحيح، أو تقرير يسمّيه تقرير آخر أو يليه. ويمكن"
         " إزالة المسودة وأحدث تقرير يومي وتقرير التجاوز (v6.7).",
         "يُبطل إزالة تقرير مسجَّل يسمّيه تقرير آخر أو يليه. ويمكن إزالة المسودة وأحدث موضع في"
         " السلسلة كاملًا وتقرير التجاوز (v6.7).")],
    "plugins/tamheed/skills/standup/SKILL.md": [
        ("The newest daily report, or an override report, can be withdrawn on the operator's word.\n"
         "A correction cannot, and neither can a report that another row names. Discard any draft\n"
         "first.",
         "The newest daily report, or an override report, can be withdrawn on the operator's word.\n"
         "When it is a correction, the reports it corrects go with it. A report that another row\n"
         "names stays. Discard any draft first."),
        ("fresh lists: withdraw it, then draft again. An older window cannot be counted again, because\n",
         "fresh lists: withdraw it, then draft again. To start the chain again, withdraw the newest\n"
         "report each time until none is left: the next draft is a first report, computed from\n"
         "today. An older window cannot be counted again, because\n")],
    "docs/adr/adr-0004-a-standup-report-can-be-withdrawn.md": [
        ("rulings R133, R134, R136, R139, R140 and R142 in",
         "rulings R133, R134, R136, R139, R140, R142 and R144 in"),
        ("- A recorded report that nothing depends on can be withdrawn: the newest daily report, or an\n"
         "  override report. A correction cannot, because its place in the chain would stay empty.",
         "- The newest place in the chain can be withdrawn whole (R144): the newest daily report\n"
         "  together with every report it corrects, or an override report. A report that another\n"
         "  report names stays. Withdrawn newest first down to none, the chain starts again with a\n"
         "  first report.")],
    "plugins/tamheed/references/governance.md": [(
        "A correction\n  and a report that another row names stay.",
        "A correction takes\n  the reports it corrects with it. A report that another row names stays.")],
    "CHANGELOG.md": [
        ("when nothing names it. A\n  correction is refused.",
         "when nothing names it. A\n  correction takes the reports it corrects with it."),
        ("(plan 246, ADR-0004; R133, R134, R136, R139,\n  R142).**",
         "(plan 246, ADR-0004; R133, R134, R136, R139,\n  R142, R144).**")],
    "docs/entities.md": [(
        "    Approved --> [*] : withdrawn on the operator's word, when nothing depends on it (v6.7)\n",
        "    Approved --> [*] : withdrawn on the operator's word, when nothing depends on it (v6.7)\n"
        "    Superseded --> [*] : withdrawn together with its newest correction (v6.7)\n")],
    "plans/evidence/field-round-6.7.0-record.md": [(
        "- **R140** The action is `withdraw`, and the vocabulary gains its row.\n",
        "- **R140** The action is `withdraw`, and the vocabulary gains its row.\n"
        "- **R141** (the security review of 243) An export refuses a target inside `slates/`, as it\n"
        "  refuses `data/`.\n"
        "- **R142** A correction and a regenerate keep a report's frozen facts. Fresh lists come only\n"
        "  from withdrawing the newest report and drafting again.\n"
        "- **R143** (2026-11-17, after the field's fresh export) The field's operator retired the two\n"
        "  DEP-002 edges by their own ruling. Their brief OFFERS writing the edges again as history and\n"
        "  moving the dependency to `Implemented`, and asks for a review of every dependency.\n"
        "- **R144** (2026-11-17) Supersedes R133 in part: a withdrawal takes the newest place in the\n"
        "  chain whole, the newest report with every report it corrects. An operator can withdraw\n"
        "  newest first down to none, and the next draft is a first report computed from today.\n")],
}
for rel, pairs in EDITS.items():
    path = R / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in text:
            continue
        assert text.count(old) == 1, (rel, text.count(old), old[:60])
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="\n")
print("docs 246c written")
