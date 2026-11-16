"""Plan 246 (R133, R134, R136, R139, R140, R142; ADR-0004): the texts of standup withdraw and
regenerate. Idempotent: a pair already applied is skipped, and a new file is written once.

    python plans/evidence/scripts-239/docs_246.py
"""
from pathlib import Path

R = Path(__file__).resolve().parents[3]
AR_CONFIRM_END = "وتبقى الكلمات في الصف ولا تبلغ صفحة أبدًا.\"}"
EDITS = {
    "plugins/tamheed/server/tamheed_server.py": [
        ('" words stay in the row and never reach a page. action=\'discard\' removes the draft. A"\n'
         '    " recorded report is immutable.")',
         '" words stay in the row and never reach a page. action=\'discard\' removes the draft. A"\n'
         '    " recorded report is never edited. action=\'withdraw\' with report=RPT-NNN and confirm"\n'
         '    " (operator_confirm, by, words) removes the newest daily report or an override report"\n'
         '    " when nothing names it. The journal keeps a note without the words, and the id is never"\n'
         '    " used again. action=\'regenerate\' rebuilds the pages of recorded reports from their"\n'
         '    " rows: one with report=RPT-NNN, or all. Neither changes the frozen facts.")'),
        ("# plan 232: a recorded standup report is immutable and engine-written",
         "# plan 232: a recorded standup report is never edited and is engine-written")],
    "docs/guide/content.py": [
        ("Aborts the removal of a recorded report. Only a draft can be discarded.",
         "Aborts the removal of a recorded report that the chain needs: a correction, or a report"
         " that another report names or follows. A draft, the newest daily report and an override"
         " report can be removed (v6.7)."),
        ("يُبطل إزالة تقرير مسجَّل. ولا يمكن تجاهل إلا المسودة.",
         "يُبطل إزالة تقرير مسجَّل تحتاجه السلسلة: تصحيح، أو تقرير يسمّيه تقرير آخر أو يليه. ويمكن"
         " إزالة المسودة وأحدث تقرير يومي وتقرير التجاوز (v6.7)."),
        ("A correction supersedes a recorded report over the same window.\", \"ar\":",
         "A correction supersedes a recorded report over the same window. The newest daily report"
         " or an override report can be withdrawn on the operator's word, and recorded pages can"
         " be rebuilt from their rows.\", \"ar\":"),
        ("والتصحيح يحل محل تقرير مسجَّل على النافذة نفسها.\"}",
         "والتصحيح يحل محل تقرير مسجَّل على النافذة نفسها. ويمكن سحب أحدث تقرير يومي أو تقرير"
         " تجاوز بكلمة المشغّل، وإعادة بناء صفحات التقارير المسجَّلة من صفوفها.\"}"),
        ("`discard` removes the draft.\", \"ar\":",
         "`discard` removes the draft. `withdraw` removes the newest daily report or an override"
         " report, on the operator's word. `regenerate` rebuilds recorded pages from their"
         " rows.\", \"ar\":"),
        ("و`discard` يزيل المسودة.\"}",
         "و`discard` يزيل المسودة. و`withdraw` يزيل أحدث تقرير يومي أو تقرير تجاوز بكلمة المشغّل."
         " و`regenerate` يعيد بناء الصفحات المسجَّلة من صفوفها.\"}"),
        ("The words stay in the row and never reach a page.\", \"ar\": \"كلمة المشغّل، لـ `record`",
         "The words stay in the row and never reach a page. For `withdraw` it takes"
         " `operator_confirm`, `by` and `words`, and the words are not stored.\", \"ar\":"
         " \"كلمة المشغّل، لـ `record`"),
        (AR_CONFIRM_END,
         "وتبقى الكلمات في الصف ولا تبلغ صفحة أبدًا. ولـ `withdraw` يأخذ `operator_confirm` و`by`"
         " و`words`، ولا تُخزَّن الكلمات.\"},\n"
         "    \"param.standup_report.report\": {\"en\": \"The report to withdraw or to regenerate,"
         " such as `RPT-002`. Without it, `regenerate` rebuilds every recorded page.\", \"ar\":"
         " \"التقرير المراد سحبه أو إعادة بنائه، مثل `RPT-002`. وبدونه يعيد `regenerate` بناء كل"
         " صفحة مسجَّلة.\"}"),
        ("then Superseded by a correction.\", \"ar\":",
         "then Superseded by a correction. The newest daily report or an override report can also"
         " be withdrawn.\", \"ar\":"),
        ("ثم Superseded بتصحيح.\"}",
         "ثم Superseded بتصحيح. ويمكن أيضًا سحب أحدث تقرير يومي أو تقرير تجاوز.\"}"),
        ("On request. A stored record by design (ADR-0003).",
         "On request. A stored record by design (ADR-0003). A report that nothing depends on can"
         " be withdrawn (ADR-0004)."),
        ("عند الطلب. سجل مخزَّن عن قصد (ADR-0003).",
         "عند الطلب. سجل مخزَّن عن قصد (ADR-0003). ويمكن سحب تقرير لا يعتمد عليه شيء (ADR-0004)."),
    ],
    "plugins/tamheed/skills/standup/SKILL.md": [(
        "A recorded report is immutable. To fix its words, call `standup_report(supersede=\"RPT-NNN\")`.",
        "A recorded report is never edited. To redo its words, call"
        " `standup_report(supersede=\"RPT-NNN\")`."), (
        "to 8. The old report moves to Superseded. A correction cannot change the facts.\n",
        "to 8. The old report moves to Superseded. A correction cannot change the facts.\n\n"
        "## Withdraw a report\n\n"
        "The newest daily report, or an override report, can be withdrawn on the operator's word.\n"
        "A correction cannot, and neither can a report that another row names. Discard any draft\n"
        "first. Call `standup_report(action=\"withdraw\", report=\"RPT-NNN\", confirm={\"operator_confirm\":\n"
        "true, \"by\": \"human:<name>\", \"words\": \"<what they said>\"})`. The row leaves the store, and\n"
        "its page is removed. A journal note names the report, who and when. The words are not stored.\n"
        "The id is never used again. Git history keeps the removed row, so this is no erasure. Export\n"
        "`review.html`, then commit on the operator's yes.\n\n"
        "## Fresh lists, and the page alone\n\n"
        "A correction and a regenerate keep the frozen facts. Only the newest daily report can take\n"
        "fresh lists: withdraw it, then draft again. An older window cannot be counted again, because\n"
        "the store keeps current state only. `standup_report(action=\"regenerate\")` rebuilds the\n"
        "pages of recorded reports from their rows, for a lost page or a page of an older release.\n"
        "It changes no row.\n")],
    "docs/entities.md": [(
        "    Approved --> Superseded : a correction over the same window replaces it\n",
        "    Approved --> Superseded : a correction over the same window replaces it\n"
        "    Approved --> [*] : withdrawn on the operator's word, when nothing depends on it (v6.7)\n")],
    "plugins/tamheed/references/artifact-catalog.md": [(
        "Approved and Superseded rows are immutable.",
        "Approved and Superseded rows are never edited. A report that nothing depends on can be"
        " withdrawn (ADR-0004).")],
    "plugins/tamheed/references/governance.md": [(
        "Approved and Superseded rows are immutable, by a trigger.",
        "Approved and Superseded rows are never edited, by a trigger. The newest daily report, or\n"
        "  an override report, can be withdrawn on the operator's word (v6.7, ADR-0004). A correction\n"
        "  and a report that another row names stay.")],
    "SECURITY.md": [(
        "  with a `human:` name. A recorded row is immutable by a trigger, and `entity_upsert`\n"
        "  refuses the family.",
        "  with a `human:` name. A recorded row is never edited, by a trigger, and `entity_upsert`\n"
        "  refuses the family. A withdrawal (v6.7) removes a row that nothing depends on, on the\n"
        "  operator's word. Git history keeps the row.")],
    "plugins/tamheed/server/README.md": [(
        "`discard` removes the draft.",
        "`discard` removes the draft. `withdraw` (v6.7) removes the newest daily report or an"
        " override report on the operator's word, and `regenerate` rebuilds recorded pages from"
        " their rows.")],
    "plugins/tamheed/references/vocabulary.md": [(
        "| take a row out of the record | retire | `delete`, `erase` |\n",
        "| take a row out of the record | retire | `delete`, `erase` |\n"
        "| take the newest standup report out of the record | withdraw | `delete`, `erase` |\n")],
    "docs/adr/adr-0003-standup-reports-are-stored-records.md": [(
        "superseded_by: none",
        "superseded_by: ADR-0004 (partially — a report that nothing depends on can be withdrawn)")],
}
ADR4 = """---
status: Approved
date: 2026-11-16
id: ADR-0004
supersedes: ADR-0003 (partially — the clause that a recorded report never leaves the store)
superseded_by: none
---

# ADR-0004 — A standup report can be withdrawn

## Status

Approved (operator, 2026-11-16 — rulings R133, R134, R136, R139, R140 and R142 in
`plans/evidence/field-round-6.7.0-record.md`; plan 246, release 6.7.0).

## Context

ADR-0003 made standup reports stored records. A trigger refused the removal of a recorded
report. The operator asked to delete a report and to regenerate one. The established pattern for
recorded events (Azure's Event Sourcing guidance, Fowler) never deletes an event: a compensating
record undoes it, and the original stays. A `Withdrawn` status would follow that pattern. But
6.6.0 loads every row under its own status CHECK, so it would refuse the whole store, and the way
back would break.

## Decision

- A recorded report that nothing depends on can be withdrawn: the newest daily report, or an
  override report. A correction cannot, because its place in the chain would stay empty.
- The tool checks every row that names the report, and it refuses while one is left. Migration
  012 replaces the trigger `trg_standup_reports_keep` under the same name, so a raw delete
  follows the same rule.
- The row leaves the store, and its page is removed. A journal note names the report, who and
  when. The operator's words are not stored (SR49): the row that held them is gone. Git history
  keeps the removed row, so a withdrawal is not erasure.
- A withdrawn id is never used again. The allocator also counts the ids that the journal notes
  name.
- Regenerate rebuilds the pages of recorded reports from their rows. No row changes.
- Neither a regenerate nor a correction changes the frozen facts. Fresh lists come only from
  withdrawing the newest daily report and drafting again, because the store keeps current state
  only (R142).
- A recorded report is still never edited: `trg_standup_reports_immutable` holds.

## Consequences

- Measured on 2026-11-16 (`plans/evidence/scripts-239/wayback_246.py`): after a withdrawal under
  6.7.0, the real 6.6.0 opens the store and verifies it clean. Its next draft takes the withdrawn
  id again, so the field briefs name that.
- The journal note is the compensating record. The store holds no row of the withdrawn report.

## Alternatives rejected

- **A `Withdrawn` status kept in the row:** 6.6.0 refuses the whole store on load.
- **Withdrawing any report:** later reports name it as their base, and the replay runs through it.
- **Keeping the operator's words in the note:** SR49 keeps words out of the journal.

## Confirmation

The four withdraw and regenerate tests of `StandupToolTest` in `tests/test_mcp_contract.py`, the
re-aimed trigger test of `StandupFamilyTest`, and the way-back measurement above.
"""
RECORD = """
## Later rulings (field round 6.7.0, 2026-11-16)

| # | Ruling |
|---|---|
| SR52 (R133, R139) | Supersedes SR23 in part: a recorded report is still never edited, and the newest daily report or an override report can be withdrawn on the operator's word (ADR-0004) |
| SR53 (R134) | Supersedes SR24's last clause in part: a discard removes a draft, and a withdrawal removes a recorded report that nothing depends on. A withdrawn id is never used again |
"""
ENTRY = (
    "- **Withdraw and regenerate a standup report (plan 246, ADR-0004; R133, R134, R136, R139,\n"
    "  R142).** `standup_report(action=\"withdraw\", report=..., confirm=...)` removes the newest\n"
    "  daily report or an override report, on the operator's word, when nothing names it. A\n"
    "  correction is refused. A journal note names the report, who and when, never the words, and\n"
    "  the id is never used again. Git history keeps the row. `action=\"regenerate\"` rebuilds the\n"
    "  pages of recorded reports from their rows. Neither changes the frozen facts. Migration\n"
    "  `012_standup_withdraw.sql` replaces one trigger: no table or column changes.\n")
for rel, pairs in EDITS.items():
    path = R / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in text:
            continue
        assert text.count(old) == 1, (rel, text.count(old), old[:60])
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="\n")
adr = R / "docs/adr/adr-0004-a-standup-report-can-be-withdrawn.md"
if not adr.exists():
    adr.write_text(ADR4, encoding="utf-8", newline="\n")
rec = R / "plans/evidence/standup-2026-11-record.md"
text = rec.read_text(encoding="utf-8")
if "SR52 (R133, R139)" not in text:
    rec.write_text(text.rstrip("\n") + "\n" + RECORD, encoding="utf-8", newline="\n")
log = R / "CHANGELOG.md"
text = log.read_text(encoding="utf-8")
if "(plan 246," not in text:
    anchor = "### Added\n\n"
    assert text.index(anchor) < text.index("## [6.6.0]")
    log.write_text(text.replace(anchor, anchor + ENTRY + "\n", 1), encoding="utf-8", newline="\n")
print("docs 246 written")
