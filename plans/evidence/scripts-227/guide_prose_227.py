"""Plan 227: add the guide prose (EN + AR) for the two slate tools, their parameters, one
figure phrase and the new suite to docs/guide/content.py. Run once from the repository
root. A second run adds nothing: an id that content.py already holds is skipped.

    python plans/evidence/scripts-227/guide_prose_227.py
"""
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTENT = ROOT / "docs" / "guide" / "content.py"

# (anchor id, the id to add after it, English, Arabic). Each sentence holds 25 words at most.
ADD = [
    ("tool.export_html", "tool.slate_export",
     "Writes an interview page for the operator at `<package>/slates/<name>.html`, with the"
     " slate record `<name>.slate.json` beside it. No row is written. Every cited row is read"
     " from the store and quoted on the page. The page runs one script, named by hash, and"
     " it loads nothing and sends nothing.",
     "يكتب صفحة مقابلة للمشغّل في `<package>/slates/<name>.html`، وبجوارها سجل القائمة"
     " `<name>.slate.json`. لا يُكتب أي صف. يُقرأ كل صف مستشهَد به من المخزن ويُقتبس في"
     " الصفحة. تشغّل الصفحة سكربتًا واحدًا مسمًّى ببصمته، ولا تحمّل شيئًا ولا ترسل شيئًا."),
    ("tool.slate_export", "tool.slate_read",
     "Reads the answers file that the operator saved from the page, at"
     " `<package>/slates/<name>.answers.json`. It returns a checked transcript and writes"
     " nothing. The transcript is a record of a file, never the operator's word. `put_again`"
     " names the questions whose quoted row has changed.",
     "يقرأ ملف الإجابات الذي حفظه المشغّل من الصفحة، في"
     " `<package>/slates/<name>.answers.json`. يعيد محضرًا مفحوصًا ولا يكتب شيئًا. المحضر"
     " سجل لملف، وليس كلمة المشغّل أبدًا. ويسمّي `put_again` الأسئلة التي تغيّر صفها"
     " المقتبَس."),
    ("param.export_html.output", "param.slate_export.slate",
     "The slate, inline: a name, a title, and rounds of questions. Each question has two or"
     " more options. One option at most is recommended, and it carries its reason. An"
     " optional `language`, `en` or `ar`, sets the page's direction and its fixed words.",
     "القائمة، مضمَّنة: اسم وعنوان وجولات من الأسئلة. لكل سؤال خياران أو أكثر. يُوصى بخيار"
     " واحد على الأكثر، ومعه سببه. والمفتاح الاختياري `language`، وقيمته `en` أو `ar`،"
     " يحدّد اتجاه الصفحة وكلماتها الثابتة."),
    ("param.slate_export.slate", "param.slate_export.name",
     "Sent alone, without `slate`: the tool reads the slate from"
     " `<package>/slates/<name>.spec.json`, which a project script writes. The caller names"
     " no path.",
     "يُرسَل وحده، بلا `slate`: تقرأ الأداة القائمة من `<package>/slates/<name>.spec.json`،"
     " وهو ملف يكتبه سكربت المشروع. ولا يسمّي المستدعي أي مسار."),
    ("param.slate_export.name", "param.slate_export.replace",
     "`true` replaces a record on disk that differs from this slate. On the operator's word:"
     " answers saved from the older page are then refused.",
     "`true` يستبدل سجلًا على القرص يختلف عن هذه القائمة. بكلمة المشغّل: تُرفض بعدها"
     " الإجابات المحفوظة من الصفحة الأقدم."),
    ("param.slate_export.replace", "param.slate_read.name",
     "The slate's name. The tool reads the answers file at the one place that the name"
     " gives.",
     "اسم القائمة. تقرأ الأداة ملف الإجابات من الموضع الوحيد الذي يحدّده الاسم."),
    ("dia.fx.export_file", "dia.fx.cited_rows",
     "the rows that the slate cites",
     "الصفوف التي تستشهد بها القائمة"),
    ("suite.test_export_html.py", "suite.test_slate.py",
     "The interview page: a slate is checked, and the page runs one script named by hash."
     " Hostile text never appears unescaped. The reader judges an answers file and writes"
     " nothing.",
     "صفحة المقابلة: تُفحص القائمة، وتشغّل الصفحة سكربتًا واحدًا مسمًّى ببصمته، والنص"
     " العدائي لا يظهر غير مُهرَّب أبدًا، ويحكم القارئ على ملف الإجابات ولا يكتب شيئًا."),
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
