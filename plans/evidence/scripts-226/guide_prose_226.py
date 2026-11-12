"""Plan 226: add the guide prose (EN + AR) for the two register families, one parameter and
one rule to docs/guide/content.py. Run once from the repository root. A second run adds
nothing: an id that content.py already holds is skipped.

    python plans/evidence/scripts-226/guide_prose_226.py
"""
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTENT = ROOT / "docs" / "guide" / "content.py"

# (anchor id, the id to add after it, English, Arabic). Each sentence holds 25 words at most.
ADD = [
    ("table.feedback", "type.register",
     "A project register: a record type that the plugin has no family for. It declares its"
     " fields under `custom_attributes.fields`, a list of `name`, `required`, `values` and"
     " `refs`. Declare a register. Never put such records into dependency, open-question or"
     " section rows.",
     "سجل المشروع: نوع سجلات ليس له عائلة في الإضافة. يصرّح بحقوله تحت"
     " `custom_attributes.fields`، وهي قائمة من `name` و`required` و`values` و`refs`."
     " صرّح بسجل. ولا تضع هذه السجلات أبدًا في صفوف التبعيات أو الأسئلة المفتوحة أو الأقسام."),
    ("type.register", "table.registers",
     "On request. The declaration is checked at write: every field has a name, and a value"
     " set and `refs` never go together. An empty list declares no field. The rule"
     " `register-entries-conform` reads the current declaration.",
     "عند الطلب. يُفحص التصريح عند الكتابة: لكل حقل اسم، ولا تجتمع مجموعة قيم مع `refs`."
     " والقائمة الفارغة لا تصرّح بأي حقل. وتقرأ القاعدة `register-entries-conform` التصريح"
     " الحالي."),
    ("table.registers", "type.register-entry",
     "One record of a project register. Its field values live in `custom_attributes`, and"
     " the write checks them against the declaration of its register. Born `Proposed`. Retire"
     " it with `Superseded` or `Obsolete`.",
     "سجل واحد في سجل المشروع. تُحفظ قيم حقوله في `custom_attributes`، وتفحصها الكتابة"
     " مقابل تصريح سجله. يولد `Proposed`. ويُحال إلى التقاعد بـ `Superseded` أو `Obsolete`."),
    ("type.register-entry", "table.register_entries",
     "On request. The write refuses an undeclared key, a missing required field, a value"
     " outside the set, and a reference that names no row. A reference is one id or a list"
     " of ids. A string of joined ids is never split.",
     "عند الطلب. ترفض الكتابة مفتاحًا غير مصرَّح به، وحقلًا مطلوبًا ناقصًا، وقيمة خارج"
     " المجموعة، ومرجعًا لا يسمّي صفًا. والمرجع معرّف واحد أو قائمة معرّفات. ولا تُقسَّم"
     " أبدًا سلسلة معرّفات موصولة."),
    ("col.feedback.title", "col.registers.id",
     "`REG-NNN`, caller, when the project keeps a record type that no family holds.",
     "`REG-NNN`، المستدعي، حين يحتفظ المشروع بنوع سجلات لا تحمله أي عائلة."),
    ("col.registers.id", "col.registers.title",
     "Required. The name of the register.",
     "مطلوب. اسم السجل."),
    ("col.registers.title", "col.registers.purpose",
     "What one entry records, and why the project keeps it.",
     "ما يسجّله الإدخال الواحد، ولماذا يحتفظ به المشروع."),
    ("col.registers.purpose", "col.register_entries.id",
     "`ENT-NNN`, caller, one per record.",
     "`ENT-NNN`، المستدعي، واحد لكل سجل."),
    ("col.register_entries.id", "col.register_entries.register_id",
     "Required. The register that this entry belongs to. `entity_query(register_id=...)`"
     " selects by it.",
     "مطلوب. السجل الذي ينتمي إليه هذا الإدخال. ويختار `entity_query(register_id=...)`"
     " بحسبه."),
    ("col.register_entries.register_id", "col.register_entries.title",
     "Required. A short name for the record.",
     "مطلوب. اسم قصير للسجل."),
    ("col.register_entries.title", "col.register_entries.body",
     "Free prose about the record. The values of the declared fields go in"
     " `custom_attributes`.",
     "نص حر عن السجل. أما قيم الحقول المصرَّح بها فتوضع في `custom_attributes`."),
    ("param.entity_query.plugin_skill", "param.entity_query.register_id",
     "For `register-entry` rows only: the entries of one project register, exact match."
     " Refused for any other family.",
     "لصفوف `register-entry` فقط: إدخالات سجل مشروع واحد، بمطابقة تامة. ويُرفض لأي عائلة"
     " أخرى."),
    ("rule.feedback-unanswered", "rule.register-entries-conform",
     "Live register entries that the current declaration of their register does not admit."
     " `problems` names the cause per entry (conditional: only when a register exists).",
     "إدخالات سجل حيّة لا يقبلها التصريح الحالي لسجلها. ويسمّي `problems` السبب لكل"
     " إدخال (شرطية: فقط عند وجود سجل)."),
]


def main() -> int:
    text = io.open(CONTENT, encoding="utf-8").read()
    added = 0
    for anchor, new_id, en, ar in ADD:
        if f'"{new_id}":' in text:
            continue
        at = text.index(f'    "{anchor}":')
        # an entry may run over several lines: it ends at the next line that opens an id
        end = text.index('\n    "', at + 1) + 1
        entry = (f'    "{new_id}": {{"en": {json.dumps(en, ensure_ascii=False)},\n'
                 f'{" " * (len(new_id) + 8)}"ar": {json.dumps(ar, ensure_ascii=False)}}},\n')
        text = text[:end] + entry + text[end:]
        added += 1
    io.open(CONTENT, "w", encoding="utf-8", newline="\n").write(text)
    print(f"added {added} of {len(ADD)} ids")
    return 0


if __name__ == "__main__":
    sys.exit(main())
