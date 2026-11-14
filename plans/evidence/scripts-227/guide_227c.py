"""Plan 227c: the guide follows the page's rounds, its files per round and the reader.

It sets the guide prose (EN + AR) of the two slate tools and their parameters in
docs/guide/content.py, and it aims the two tools' effects in docs/guide/diagrams.py at the
server's lines. Run it from the repository root after `scripts-221/shift_221.py`, then run
`python docs/guide/build.py`. A second run changes nothing.

    python plans/evidence/scripts-227/guide_227c.py
"""
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTENT = ROOT / "docs" / "guide" / "content.py"
DIAGRAMS = ROOT / "docs" / "guide" / "diagrams.py"
SERVER = ROOT / "plugins" / "tamheed" / "server" / "tamheed_server.py"

# (the id, the id it stands after when it is new, English, Arabic). 25 words a sentence at most.
PROSE = [
    ("tool.slate_export", "tool.export_html",
     "Writes an interview page for the operator at `<package>/slates/<name>.html`. The slate"
     " record and two hand-outs for the room stand beside it. No row is written. Every row"
     " that the slate names is read from the store and quoted on the page. Participant names"
     " and glossary terms are read from the store too. The page runs one script, named by"
     " hash, and it loads nothing and sends nothing. Its presenter view is a way to show the"
     " page, and it protects nothing.",
     "يكتب صفحة مقابلة للمشغّل في `<package>/slates/<name>.html`. بجوارها سجل القائمة وورقتان"
     " للحضور. لا يُكتب أي صف. يُقرأ من المخزن كل صف تذكره القائمة ويُقتبس في الصفحة. تُقرأ"
     " من المخزن أيضًا أسماء المشاركين ومصطلحات المسرد. تشغّل الصفحة سكربتًا واحدًا مسمًّى"
     " ببصمته، ولا تحمّل شيئًا ولا ترسل شيئًا. عرض المقدِّم طريقة لعرض الصفحة، ولا يحمي شيئًا."),
    ("tool.slate_read", "tool.slate_export",
     "Reads the answers files that the operator saved from the page: one for the whole page,"
     " and one for each round. It returns one checked transcript and writes nothing. The"
     " transcript is a record of files, never the operator's word. Each round is complete, or"
     " the transcript names what it lacks. `conflicts` lists what two files disagree on."
     " `put_again` names the answers whose question or whose quoted row has changed.",
     "يقرأ ملفات الإجابات التي حفظها المشغّل من الصفحة: ملف للصفحة كلها، وملف لكل جولة. يعيد"
     " محضرًا واحدًا مفحوصًا ولا يكتب شيئًا. المحضر سجل لملفات، وليس كلمة المشغّل أبدًا. كل"
     " جولة مكتملة، أو يذكر المحضر ما ينقصها. يسرد `conflicts` ما يختلف فيه ملفان. يذكر"
     " `put_again` الإجابات التي تغيّر سؤالها أو صفها المقتبس."),
    ("param.slate_export.slate", "param.export_html.output",
     "The slate, inline: a name, a title, and rounds of questions. Each question has two or"
     " more options. One option at most is recommended, and it carries its reason. A slate"
     " may also name participants, blocks, decided topics, an owner and a lead for each"
     " question, and the rows that a question rests on. The plugin's `references/slate.md`"
     " holds the whole grammar.",
     "القائمة، مضمَّنة: اسم وعنوان وجولات من الأسئلة. لكل سؤال خياران أو أكثر. يُوصى بخيار"
     " واحد على الأكثر، ويحمل سببه. قد تذكر القائمة أيضًا المشاركين والمجموعات والمواضيع"
     " المحسومة، ومالك كل سؤال ومسؤوله، والصفوف التي يستند إليها السؤال. القواعد كلها في"
     " `references/slate.md` ضمن الإضافة."),
    ("param.slate_read.name", "param.slate_export.replace",
     "The slate's name. The tool reads the answers files at the places that the name and the"
     " slate's round ids give, and no other file.",
     "اسم القائمة. تقرأ الأداة ملفات الإجابات من المواضع التي يحددها الاسم ومعرّفات جولات"
     " القائمة، ولا تقرأ ملفًا آخر."),
    ("param.slate_read.round", "param.slate_read.name",
     "One round's id. The tool then reads that round's file alone, and the transcript holds"
     " that round only.",
     "معرّف جولة واحدة. تقرأ الأداة عندئذ ملف تلك الجولة وحده، ويحتوي المحضر تلك الجولة فقط."),
    ("suite.test_slate_rounds.py", "suite.test_slate.py",
     "The interview page's rounds: the slate's keys for participants, blocks and decided"
     " topics. What the export derives from the store. The reader of files per round, a"
     " round that is complete, and answers of an earlier page. The two hand-outs.",
     "جولات صفحة المقابلة: مفاتيح القائمة للمشاركين والمجموعات والمواضيع المحسومة. ما يشتقه"
     " التصدير من المخزن. قارئ ملفات الجولات، والجولة المكتملة، وإجابات صفحة سابقة. الورقتان."),
]

# (tool, group, item) -> the text that the cited server line holds, inside that tool's function
EFFECTS = {
    "slate_export": {
        "needs": [("@need.open", "if guard := _need_open():")],
        "reads": [("slates/*.spec.json", '_read_capped(files["spec"]'),
                  ("@cited_rows", "slates.derive(_CURRENT.conn, checked)")],
        "writes": [("slates/*.slate.json", '"record": _managed_emit(files["record"]'),
                   ("slates/*.html", '"page": _managed_emit(files["page"]')]},
    "slate_read": {
        "needs": [("@need.open", "if guard := _need_open():")],
        "reads": [("slates/*.answers.json", "_read_capped(path, slates.MAX_FILE_BYTES)"),
                  ("slates/*.slate.json", '_read_capped(files["record"]'),
                  ("@cited_rows", "slates.quote_rows(_CURRENT.conn, list(rows))")],
        "writes": [("@nothing", "It WRITES NOTHING")]},
}


def entry(ident: str, en: str, ar: str) -> str:
    return (f'    "{ident}": {{"en": {json.dumps(en, ensure_ascii=False)},\n'
            f'{" " * (len(ident) + 8)}"ar": {json.dumps(ar, ensure_ascii=False)}}},\n')


def set_prose() -> None:
    text = io.open(CONTENT, encoding="utf-8").read()
    for ident, after, en, ar in PROSE:
        if f'    "{ident}":' in text:
            at = text.index(f'    "{ident}":')
        else:                                   # new: it stands after its anchor's entry
            at = text.index('\n    "', text.index(f'    "{after}":') + 1) + 1
            text = text[:at] + entry(ident, "", "") + text[at:]
        end = text.index('\n    "', at + 1) + 1    # an entry ends where the next id opens
        text = text[:at] + entry(ident, en, ar) + text[end:]
    io.open(CONTENT, "w", encoding="utf-8", newline="\n").write(text)


def aim_effects() -> None:
    source = io.open(SERVER, encoding="utf-8").read().split("\n")
    text = io.open(DIAGRAMS, encoding="utf-8").read()
    for tool, groups in EFFECTS.items():
        first = next(n for n, line in enumerate(source) if line.startswith(f"def {tool}("))
        last = next(n for n in range(first + 1, len(source)) if source[n].startswith("def ")
                    or source[n].startswith("_SLATE_"))
        block = "    " + json.dumps(tool) + ": {\n"
        parts = []
        for group, items in groups.items():
            cited = []
            for item, needle in items:
                line = next(n for n in range(first, last) if needle in source[n]) + 1
                cited.append(f'("{item}", {line})')
            joiner = ",\n" + " " * (len(group) + 14)
            parts.append(f'        "{group}": [{joiner.join(cited)}]')
        block += ",\n".join(parts) + "},\n"
        found = re.search(r'    "%s": \{\n.*?\]\},\n' % tool, text, re.S)
        assert found, tool
        text = text[:found.start()] + block + text[found.end():]
    io.open(DIAGRAMS, "w", encoding="utf-8", newline="\n").write(text)


if __name__ == "__main__":
    set_prose()
    aim_effects()
    print("guide prose set for", len(PROSE), "ids, and two tools' effects aimed")
    sys.exit(0)
