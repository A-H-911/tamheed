"""Plan 227c: the documents follow the interview page's rounds, its views and its reader.

Run once from the repository root. Each replacement must find its text exactly once.

    python plans/evidence/scripts-227/docs_227c.py
"""
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def patch(path: str, pairs: list) -> None:
    file = ROOT / path
    text = io.open(file, encoding="utf-8").read()
    for old, new in pairs:
        assert text.count(old) == 1, (path, text.count(old), old[:70])
        text = text.replace(old, new)
    io.open(file, "w", encoding="utf-8", newline="\n").write(text)


def row(path: str, starts: str, new: str) -> None:
    """Replace the one table row that starts with `starts`."""
    file = ROOT / path
    text = io.open(file, encoding="utf-8").read()
    found = re.findall(r"^%s.*$" % re.escape(starts), text, re.M)
    assert len(found) == 1, (path, starts, len(found))
    io.open(file, "w", encoding="utf-8", newline="\n").write(text.replace(found[0], new))


patch("SECURITY.md", [
    ("  The script reads ids from data attributes, sets values and classes, and writes no markup. The\n"
     "  page holds no data block.",
     "  The script reads ids from data attributes, sets values and classes, and writes no markup. A\n"
     "  line of a round's points is copied from a template that the server rendered. The page\n"
     "  holds no data block."),
    ("  tag cannot set `frame-ancestors` or `sandbox`. The answers stay in the browser's storage under\n"
     "  the slate's digest until the operator clears them. So a shared browser profile shows them to\n"
     "  its next user.",
     "  tag cannot set `frame-ancestors` or `sandbox`. The answers stay in the browser's storage until\n"
     "  the operator clears them, under a key that is the page's own address. So a shared browser\n"
     "  profile shows them to its next user. Measured in Chrome: every local page shares one storage\n"
     "  area, so another local page that is opened in that profile can read them.\n"
     "- **A view of the interview page protects nothing** (v6.5, plan 227c). The page has a room view\n"
     "  and a presenter view. The room view hides the operator's questions, attendance, closure and\n"
     "  the recommendations, and it can show one round. All of that is the style's work, from a\n"
     "  switch on the page. The hidden text is in the file, and anyone who holds the file can read\n"
     "  it. Text that a reader must not see does not belong in a slate.\n"
     "- **The hand-outs hold the room's questions only.** `slate_export` writes two Markdown sheets\n"
     "  beside the page. They leave out every option, every recommendation, every question of the\n"
     "  operator and every decided topic."),
    ("- **An answers file is a record of a page, never the operator's word.** `slate_read` reads one\n"
     "  fixed file, `<package>/slates/<name>.answers.json`, and the caller names no path. It refuses a\n"
     "  file over its size cap, a key written twice and a head for another slate. It refuses an answer\n"
     "  that the slate does not offer. It computes the slate's digest from the record's content and trusts no\n"
     "  stored field.",
     "- **An answers file is a record of a page, never the operator's word.** `slate_read` reads\n"
     "  `<package>/slates/<name>.answers.json` and one `<name>.<round id>.answers.json` for each ready\n"
     "  round. It builds those names from the record, the caller names no path, and it opens no\n"
     "  other file. A file beside the page that it did not read is named, never opened. It refuses a\n"
     "  file over its size cap, a key written twice and a head for another slate. It refuses an\n"
     "  answer that the slate does not offer, and a person, a point kind or a closure field that the\n"
     "  slate did not declare. A round holds 200 points at most. Where two files disagree, the\n"
     "  answer is listed and neither file is picked. A file from an earlier export of the slate is\n"
     "  read, and each answer is compared with its question's digest: a changed question is listed\n"
     "  to be put again. Every digest is computed from content, and no stored field is trusted. A\n"
     "  question may be marked as needing the operator's approval. The page holds no approval input,\n"
     "  and the reader lists such answers for the session."),
])
patch("plugins/tamheed/skills/operator-interview/SKILL.md", [
    ("your one recommendation with its reason. Name the rows in `cites`: the tool quotes each row from\n"
     "the store, so you type no row text by hand. For a large round, write the slate to\n"
     "`<package>/slates/<name>.spec.json` by script and send `name` alone. Give the operator the page.\n"
     "They answer in a browser and save a file.\n"
     "- Read the file with `slate_read`. It returns a checked transcript, and it writes nothing.\n",
     "your one recommendation with its reason and its basis. Name the rows in `cites`: the tool quotes\n"
     "each row from the store, so you type no row text by hand. `references/slate.md` holds the whole\n"
     "grammar: participants, rounds and blocks, decided topics, an owner and a lead for each question.\n"
     "For a large round, write the slate to `<package>/slates/<name>.spec.json` by script and send\n"
     "`name` alone. Give the operator the page, and the two hand-outs for the people of the room.\n"
     "They answer in a browser. The page saves one file for each round, or one for the whole page.\n"
     "- Read the files with `slate_read`. It returns one checked transcript, and it writes nothing.\n"),
    ("- Put every question in `put_again` again. A row that it quotes, or that its round quotes, has\n"
     "  changed since the page was made.\n",
     "- Put every question in `put_again` again. Its own text has changed since it was answered, or a\n"
     "  row that it shows has changed.\n"
     "- Settle each entry of `conflicts` with the operator. Two files disagree there, and the tool\n"
     "  picked neither.\n"
     "- Ask the operator about each question in `approval_needed`. No file carries an approval, and\n"
     "  the page has no input for one.\n"
     "- A round is `complete`, or its `missing` names what it lacks: a person not recorded, a cover\n"
     "  with no name, an empty closure field. Tell the operator. The tool blocks nothing.\n"
     "- A point from the room is a candidate, with the name of who raised it. Propose a row for it\n"
     "  only on the operator's word.\n"),
    ("- The audience mode hides your recommendation and its reason. Use it when the people who answer\n"
     "  must not see your pick first. A page opened for the first time shows the pick, so tell the\n"
     "  operator to set the mode before the screen is shared.\n",
     "- The page opens in its room view. Your recommendation and its reason are hidden until the\n"
     "  presenter shows them. The operator's questions, attendance and closure are hidden too. The\n"
     "  slate's `opens` sets whether the room sees every round, or the one that the presenter opened.\n"
     "- A view protects nothing: the hidden text is in the file. Put no text in a slate that a\n"
     "  reader of the file must not see.\n"),
])
patch("CHANGELOG.md", [
    ("- `slate_export` and `slate_read` (plan 227): an interview page for the operator, and a reader\n"
     "  for the answers file that the page saves. The page runs one script, named by hash in a content\n"
     "  policy, and it loads and sends nothing. The reader writes nothing, and its result says that\n"
     "  nothing proves who wrote the file. The tools number 21.\n",
     "- `slate_export` and `slate_read` (plan 227): an interview page for the operator, and a reader\n"
     "  for the answers files that the page saves. The page runs one script, named by hash in a\n"
     "  content policy, and it loads and sends nothing. The reader writes nothing, and its result\n"
     "  says that nothing proves who wrote a file. The tools number 21.\n"
     "- The interview page runs a workshop (plan 227c): rounds with a navigator and blocks,\n"
     "  participants with attendance, an owner, a lead and consulted people for each question, a room\n"
     "  view and a presenter view, points from the room, a closure for each round, and topics\n"
     "  already decided. A question takes \"Unknown\" and \"Requires evidence\" as answers. The page\n"
     "  saves one file for each round. The reader names what a round lacks, what two files disagree\n"
     "  on, and which answers were made on an earlier version of their question. The export also\n"
     "  writes two hand-outs, matches glossary terms, and names the rows that a text cites.\n"
     "  `references/slate.md` holds the grammar.\n"),
])
patch("README.md", [
    ("questions. `slate_read` returns a checked transcript of the answers file that the operator saved. The\n"
     "page runs one script named by hash, and the transcript is never the operator's word.",
     "questions, with rounds, participants and a presenter view for a workshop. `slate_read` returns a\n"
     "checked transcript of the answers files that the page saved. The page runs one script named by\n"
     "hash, and the transcript is never the operator's word."),
])
patch("docs/architecture.md", [
    ("script, named by hash, and it loads and sends nothing. **`slate_read`** returns a checked\n"
     "transcript of the answers file that the operator saved, and it writes nothing. The transcript\n"
     "is a record of a file. An approval is still spoken in the session.",
     "script, named by hash, and it loads and sends nothing. A slate may hold rounds, participants,\n"
     "decided topics and an owner for each question, so one page runs a workshop. The page saves one\n"
     "file for each round. **`slate_read`** returns one checked transcript of those files, and it\n"
     "writes nothing. The transcript is a record of files. An approval is still spoken in the\n"
     "session. `references/slate.md` in the bundle holds the slate's grammar."),
])
patch("plugins/tamheed/references/generated-structure.md", [
    ("│   ├── <name>.spec.json           #   optional: a slate that a project script wrote for slate_export\n"
     "│   └── <name>.answers.json        #   the file the operator saved from the page, read by slate_read\n",
     "│   ├── <name>.spec.json           #   optional: a slate that a project script wrote for slate_export\n"
     "│   ├── <name>.orientation.md      #   a hand-out: the room's questions with their text\n"
     "│   ├── <name>.short.md            #   a hand-out: one line for each question of the room\n"
     "│   ├── <name>.answers.json        #   the answers of the whole page, saved by the operator\n"
     "│   └── <name>.<round>.answers.json #  the answers of one round. slate_read reads both kinds\n"),
])
patch("CLAUDE.md", [
    ("│                                     #   + slate.py, slate.js, slate.css (the interview page, v6.5)",
     "│                                     #   + slate*.py, slate.js, slate.css (the interview page, v6.5)"),
])
row("tests/README.md", "| `test_slate.py` |",
    "| `test_slate.py` | The interview page (plans 227, 227b): a slate's checks and their words, the "
    "page's one script named by hash (read from the script as it stands in the page), hostile text "
    "never unescaped, the same bytes twice, the slate file as the record with its digests computed "
    "from content, a bind that is no change to a quoted row, and a reader that judges an answers "
    "file and writes nothing. |\n"
    "| `test_slate_rounds.py` | The interview page's rounds (plan 227c): the slate's keys for "
    "participants, blocks and decided topics, what the export derives from the store, a digest for "
    "each question, files per round, a round that is complete, two files that disagree, answers of "
    "an earlier export, what the reader refuses, and the two hand-outs. |\n"
    "| `slate_browser_check.js` | Not a suite, and CI does not run it. It checks what the page's "
    "script does, from a browser's developer tools, against an exported demo page (plan 227c, R114). |")
row("plugins/tamheed/server/README.md", "| `slate_export(slate?, name?, replace?)` |",
    "| `slate_export(slate?, name?, replace?)` | export | Write an interview page for the operator at "
    "`<package>/slates/<name>.html`, with the slate record `<name>.slate.json` and two hand-outs "
    "beside it (v6.5, plans 227 and 227c). No row is written. Send the slate inline, or send `name` "
    "alone to read it from `<name>.spec.json`. A slate may hold rounds, blocks, participants, decided "
    "topics, and an owner and a lead for each question: `references/slate.md` holds the grammar. "
    "Every row that the slate names is read from the store and quoted. The page runs one script, "
    "named by hash. Its presenter view is a way to show the page, and it protects nothing. |")
row("plugins/tamheed/server/README.md", "| `slate_read(name)` |",
    "| `slate_read(name, round?)` | read | Read the answers files that the operator saved from a "
    "slate's page: `<name>.answers.json` and one `<name>.<round id>.answers.json` for each round "
    "(v6.5, plans 227 and 227c). It returns one checked transcript and writes nothing. Each round is "
    "`complete`, or `missing` names what it lacks. `conflicts` lists what two files disagree on. "
    "`put_again` lists the answers whose question or whose shown row has changed. `approval_needed` "
    "lists the answers that need the operator's approval. Nothing proves who wrote a file. |")
print("documents follow plan 227c")
sys.exit(0)
