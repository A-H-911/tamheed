"""Tamheed interview page (plan 227): a slate of questions as one local page, and a reader
for the answers file that the page saves.

The page carries the questions. The session carries the word: an answers file is a record of
what was clicked on a page, never the operator's approval (operator-interview, step 7).

Security doctrine, as for the review page, with one difference: this page runs ONE script.
- Every text of the slate and of a quoted row passes `esc()` at render.
- The script is the static file `slate.js`, the same for every slate. The page names it by
  hash in a content policy, so no other script runs: not an inline handler, not a script
  that a row's text tries to add.
- The script reads ids from data attributes, sets values and classes, and writes no markup.
  The page holds no data block.
- The page loads nothing and sends nothing (`default-src 'none'`).

Determinism: the same slate over the same rows gives the same bytes. The page has no clock.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
from pathlib import Path

from export_html import esc, CSS_PATH
from tamheed_server import ENTITY_TABLES

HERE = Path(__file__).resolve().parent
SCRIPT_PATH = HERE / "slate.js"
STYLE_PATH = HERE / "slate.css"

ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,31}")      # used with fullmatch
OTHER = "other"                       # the reserved option id of a free answer
CAPS = {"title": 200, "intro": 8000, "question": 2000, "detail": 8000, "label": 500,
        "reason": 2000}
MAX_ROUNDS, MAX_QUESTIONS, MAX_OPTIONS, MAX_CITES = 50, 500, 12, 30
MAX_FILE_BYTES = 2_000_000            # a spec file and an answers file, each
MAX_RECORD_BYTES = 20_000_000         # the slate record, at export and at read
MAX_PAGE_CHARS = 20_000_000           # the quoted text of a page, every citation counted
EXPORTED_AT_RE = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?Z")
MAX_ANSWER_TEXT = 8000                # a note, an other answer, attendance, a closing note
ANSWERS_FORMAT, RECORD_FORMAT, VERSION = "tamheed-slate-answers", "tamheed-slate", 1
# `last_referenced` is stamped by work_bind: a bind is no change to what a row says
UNQUOTED_COLUMNS = frozenset({"id", "last_referenced"})

_SLATE_KEYS = {"name", "title", "intro", "rounds"}
_ROUND_KEYS = {"id", "title", "intro", "cites", "questions"}
_QUESTION_KEYS = {"id", "question", "detail", "cites", "allow_other", "options",
                  "recommended", "reason"}
_OPTION_KEYS = {"id", "label", "detail"}


# --------------------------------------------------------------------------- the slate

def _text(owner: str, obj: dict, key: str, required: bool = False) -> tuple[str, str | None]:
    value = obj.get(key)
    if value is None or value == "":
        return "", (f"{owner} needs `{key}`" if required else None)
    if not isinstance(value, str) or not encodable(value):
        return "", f"{owner}: `{key}` is text"
    if len(value) > CAPS[key]:
        return "", f"{owner}: `{key}` holds {len(value)} characters (the cap is {CAPS[key]})"
    return value, None


def encodable(value: str) -> bool:
    """False for text that UTF-8 cannot hold (a lone surrogate): it cannot be written."""
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def short(value) -> str:
    """A value of a file, as an error may echo it: 60 characters at most, never whole."""
    plain = isinstance(value, (str, int, float, bool, type(None)))
    text = repr(value) if plain else type(value).__name__
    return text if len(text) <= 60 else text[:57] + "..."


def _keys(owner: str, obj, allowed: set) -> str | None:
    if not isinstance(obj, dict):
        return f"{owner} is an object"
    if extra := sorted(str(k) for k in set(obj) - allowed):
        return f"{owner} has unknown key(s) {extra}. It takes {', '.join(sorted(allowed))}"
    return None


def _ident(owner: str, value) -> str | None:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        return (f"{owner} needs an `id` of 1 to 32 letters, digits, dots, dashes or underscores"
                f" (got {short(value)})")
    return None


def _cites(owner: str, obj: dict) -> tuple[list, str | None]:
    cites = [] if obj.get("cites") is None else obj["cites"]
    if not isinstance(cites, list) or not all(isinstance(c, str) and c for c in cites):
        return [], f"{owner}: `cites` is a list of row ids"
    if len(cites) > MAX_CITES:
        return [], f"{owner} cites {len(cites)} rows (the cap is {MAX_CITES})"
    return list(dict.fromkeys(cites)), None           # in order, each id once


def _check_question(owner: str, q) -> tuple[dict | None, str | None]:
    if err := _keys(owner, q, _QUESTION_KEYS) or _ident(owner, q.get("id")):
        return None, err
    owner = f"question {q['id']}"
    out = {"id": q["id"]}
    for key, required in (("question", True), ("detail", False), ("reason", False)):
        out[key], err = _text(owner, q, key, required)
        if err:
            return None, err
    out["cites"], err = _cites(owner, q)
    if err:
        return None, err
    if not isinstance(q.get("allow_other", True), bool):
        return None, f"{owner}: `allow_other` is true or false"
    out["allow_other"] = q.get("allow_other", True)
    options = q.get("options")
    if not isinstance(options, list) or len(options) < 2:
        return None, f"{owner} needs two or more options"
    if len(options) > MAX_OPTIONS:
        return None, f"{owner} has {len(options)} options (the cap is {MAX_OPTIONS})"
    out["options"], seen = [], set()
    for n, option in enumerate(options):
        where = f"{owner}, option {n + 1}"
        if err := _keys(where, option, _OPTION_KEYS) or _ident(where, option.get("id")):
            return None, err
        if option["id"] == OTHER or option["id"] in seen:
            return None, (f"{where}: the id {option['id']!r} is "
                          + ("reserved for the free answer" if option["id"] == OTHER
                             else "used twice in this question"))
        seen.add(option["id"])
        label, err = _text(where, option, "label", True)
        detail, err2 = _text(where, option, "detail")
        if err or err2:
            return None, err or err2
        out["options"].append({"id": option["id"], "label": label, "detail": detail})
    recommended = q.get("recommended")
    if recommended is None:
        if out["reason"]:
            return None, f"{owner} gives a `reason` and recommends no option"
    elif not isinstance(recommended, str) or recommended not in seen:
        return None, f"{owner} recommends {short(recommended)}, which is none of its options"
    elif not out["reason"]:
        return None, (f"{owner} recommends an option and gives no `reason`. A recommendation"
                      " carries its deciding reason")
    out["recommended"] = recommended
    return out, None


def check_slate(slate) -> tuple[dict | None, str | None]:
    """(the slate with every default filled, None), or (None, why it is refused). The answer
    holds known keys only, in one fixed shape, so the record's bytes follow from it."""
    if err := _keys("the slate", slate, _SLATE_KEYS):
        return None, err
    out = {"name": slate.get("name")}
    for key, required in (("title", True), ("intro", False)):
        out[key], err = _text("the slate", slate, key, required)
        if err:
            return None, err
    rounds = slate.get("rounds")
    if not isinstance(rounds, list) or not rounds:
        return None, "the slate needs one or more `rounds`"
    if len(rounds) > MAX_ROUNDS:
        return None, f"the slate has {len(rounds)} rounds (the cap is {MAX_ROUNDS})"
    out["rounds"], round_ids, question_ids = [], set(), set()
    for n, rnd in enumerate(rounds):
        owner = f"round {n + 1}"
        if err := _keys(owner, rnd, _ROUND_KEYS) or _ident(owner, rnd.get("id")):
            return None, err
        if rnd["id"] in round_ids:
            return None, f"the round id {rnd['id']!r} is used twice"
        round_ids.add(rnd["id"])
        owner = f"round {rnd['id']}"
        item = {"id": rnd["id"]}
        for key, required in (("title", True), ("intro", False)):
            item[key], err = _text(owner, rnd, key, required)
            if err:
                return None, err
        item["cites"], err = _cites(owner, rnd)
        if err:
            return None, err
        questions = rnd.get("questions")
        if not isinstance(questions, list) or not questions:
            return None, f"{owner} needs one or more `questions`"
        item["questions"] = []
        for m, question in enumerate(questions):
            checked, err = _check_question(f"{owner}, question {m + 1}", question)
            if err:
                return None, err
            if checked["id"] in question_ids:
                return None, f"the question id {checked['id']!r} is used twice in the slate"
            question_ids.add(checked["id"])
            item["questions"].append(checked)
        out["rounds"].append(item)
    if len(question_ids) > MAX_QUESTIONS:
        return None, f"the slate has {len(question_ids)} questions (the cap is {MAX_QUESTIONS})"
    return out, None


def cited_ids(slate: dict) -> list[str]:
    """Every row id that the slate cites, each once, in the order of first use."""
    ids: dict = {}
    for rnd in slate["rounds"]:
        for cid in rnd["cites"]:
            ids[cid] = True
        for question in rnd["questions"]:
            for cid in question["cites"]:
                ids[cid] = True
    return list(ids)


# --------------------------------------------------------------------------- quoted rows

def _canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def quote_rows(conn, ids: list[str]) -> tuple[dict, list[str]]:
    """({id: {type, columns, digest}}, the ids that name no row). A quote is the row as the
    store holds it: every column that has a value, in column order, except the id itself
    and `last_referenced`. `custom_attributes` is in, so a register entry shows its fields.
    The digest is of that same set, so it moves only when what the row says moves."""
    quotes, missing = {}, []
    for rid in ids:
        found = conn.execute("SELECT entity_type FROM entity_index WHERE id = ?",
                             (rid,)).fetchone()
        table = ENTITY_TABLES.get(found[0]) if found else None
        if table is None:
            missing.append(rid)
            continue
        names = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
        row = conn.execute(f"SELECT {', '.join(names)} FROM {table} WHERE id = ?",
                           (rid,)).fetchone()
        columns = [[name, value] for name, value in zip(names, row)
                   if name not in UNQUOTED_COLUMNS and value not in (None, "")]
        quote = {"type": found[0], "columns": columns}
        quotes[rid] = quote | {"digest": _sha(_canonical(quote))}
    return quotes, missing


def quoted_size(slate: dict, quotes: dict) -> int:
    """The characters of quoted text that the page will hold. A row is printed once per
    citation, so one large row cited by many questions makes a very large page."""
    size = {rid: sum(len(str(name)) + len(str(value)) for name, value in quote["columns"])
            for rid, quote in quotes.items()}
    return sum(size[cid] for rnd in slate["rounds"]
               for cid in rnd["cites"] + [c for q in rnd["questions"] for c in q["cites"]])


def build_record(slate: dict, quotes: dict) -> dict:
    return {"format": RECORD_FORMAT, "version": VERSION, "slate": slate, "rows": quotes}


def record_text(record: dict) -> str:
    """The slate file's bytes: sorted keys, one space of indent, a final newline."""
    return json.dumps(record, ensure_ascii=False, sort_keys=True, indent=1) + "\n"


def record_digest(record: dict) -> str:
    """The slate's name for one exact content. Computed from the content at every use, and
    never read from a stored field: a field can be edited, and this cannot."""
    return _sha(_canonical({k: record.get(k) for k in ("format", "version", "slate", "rows")}))


# --------------------------------------------------------------------------- the page

def script_text() -> str:
    """`slate.js` with LF line ends. A checkout can turn them into CRLF, and a browser hashes
    an inline script after it has read the line ends as LF (measured, plan 227)."""
    return SCRIPT_PATH.read_text(encoding="utf-8").replace("\r\n", "\n")


def script_hash(script: str) -> str:
    return base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode("ascii")


def _policy(script: str) -> str:
    # ste:allow semicolon: a content policy separates its directives with semicolons
    return ("default-src 'none'; style-src 'unsafe-inline'; "
            f"script-src 'sha256-{script_hash(script)}'; base-uri 'none'; form-action 'none'")


def _quote_html(rid: str, quotes: dict) -> str:
    quote = quotes[rid]
    rows = "".join(f'<dt>{esc(name)}</dt><dd dir="auto">{esc(value)}</dd>\n'
                   for name, value in quote["columns"])
    return (f'<details class="quote"><summary>{esc(rid)} <span class="kind">'
            f'{esc(quote["type"])}</span></summary>\n<dl>\n{rows}</dl></details>\n')


def _question_html(question: dict, quotes: dict) -> str:
    qid, parts = esc(question["id"]), []
    parts.append(f'<fieldset class="question" data-question="{qid}">\n'
                 f'<legend dir="auto"><span class="qid">{qid}</span> '
                 f'{esc(question["question"])}</legend>\n')
    if question["detail"]:
        parts.append(f'<p class="detail" dir="auto">{esc(question["detail"])}</p>\n')
    parts.extend(_quote_html(cid, quotes) for cid in question["cites"])
    parts.append('<div class="options">\n')
    for option in question["options"]:
        recommended = option["id"] == question["recommended"]
        parts.append(
            f'<label class="option{" rec" if recommended else ""}">'
            f'<input type="radio" name="q:{qid}" value="{esc(option["id"])}"> '
            f'<span class="oid">{esc(option["id"])}</span> '
            f'<span dir="auto">{esc(option["label"])}</span>'
            + (' <span class="recmark">Recommended by the agent</span>' if recommended else "")
            + "</label>\n")
        if option["detail"]:
            parts.append(f'<p class="odetail" dir="auto">{esc(option["detail"])}</p>\n')
    if question["allow_other"]:
        parts.append(f'<label class="option"><input type="radio" name="q:{qid}"'
                     f' value="{OTHER}"> <span class="oid">Other</span></label>\n'
                     f'<textarea data-field="other" name="other:{qid}" rows="2" dir="auto"'
                     ' autocomplete="off" maxlength="8000" aria-label="Other answer"></textarea>\n')
    parts.append("</div>\n")
    if question["recommended"] is not None:
        parts.append('<p class="recreason" dir="auto"><strong>The reason of the agent:'
                     f'</strong> {esc(question["reason"])}</p>\n')
    parts.append(f'<label class="note">Note <textarea data-field="note" name="note:{qid}"'
                 ' rows="2" dir="auto" autocomplete="off" maxlength="8000"></textarea></label>\n</fieldset>\n')
    return "".join(parts)


def _round_html(rnd: dict, quotes: dict) -> str:
    rid = esc(rnd["id"])
    parts = [f'<section class="round" data-round="{rid}">\n'
             f'<h2 dir="auto">{esc(rnd["title"])}</h2>\n']
    if rnd["intro"]:
        parts.append(f'<p class="lead" dir="auto">{esc(rnd["intro"])}</p>\n')
    parts.extend(_quote_html(cid, quotes) for cid in rnd["cites"])
    parts.append('<label class="attendance">Attendance <textarea data-field="attendance"'
                 f' name="attendance:{rid}" rows="2" dir="auto" autocomplete="off" maxlength="8000">'
                 '</textarea></label>\n')
    parts.extend(_question_html(question, quotes) for question in rnd["questions"])
    parts.append('<div class="closure">\n<label><input type="checkbox" data-field="closed"'
                 f' name="closed:{rid}"> Round closed</label>\n'
                 '<label>Closed by <input type="text" data-field="closed_by"'
                 f' name="closed_by:{rid}" dir="auto" autocomplete="off" maxlength="8000"></label>\n'
                 '<label>Closing note <textarea data-field="closure_note"'
                 f' name="closure_note:{rid}" rows="2" dir="auto" autocomplete="off" maxlength="8000">'
                 '</textarea></label>\n</div>\n</section>\n')
    return "".join(parts)


def render(record: dict, digest: str) -> str:
    """The page for one slate record. Every data text passes `esc()`. The script is the one
    static file, and the policy in the head names it by hash."""
    slate, quotes, script = record["slate"], record["rows"], script_text()
    css = (CSS_PATH.read_text(encoding="utf-8") + "\n"
           + STYLE_PATH.read_text(encoding="utf-8")).replace("\r\n", "\n")
    name = esc(slate["name"])
    head = (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f'<meta http-equiv="Content-Security-Policy" content="{esc(_policy(script))}">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{esc(slate['title'])}</title>\n<style>\n{css}</style>\n</head>\n")
    intro = f'<p class="lead" dir="auto">{esc(slate["intro"])}</p>\n' if slate["intro"] else ""
    top = (
        f'<body data-slate="{name}" data-digest="{esc(digest)}">\n<header>\n'
        f'<h1 dir="auto">{esc(slate["title"])}</h1>\n'
        f'<p class="meta">Slate <code>{name}</code>, digest <code>{esc(digest[:12])}</code>.'
        ' <span id="progress"></span></p>\n' + intro +
        # the toolbar is a child of the body: inside the header it could not stay in view
        '</header>\n<div class="toolbar">\n'
        '<button type="button" id="view-all">All questions</button>\n'
        '<button type="button" id="view-one">One at a time</button>\n'
        '<button type="button" id="audience">Audience mode</button>\n'
        '<button type="button" id="save">Save answers</button>\n'
        '<label class="filebtn">Load answers <input type="file" id="load"'
        ' accept=".json,application/json"></label>\n'
        '<button type="button" id="print">Print</button>\n'
        '<button type="button" id="clear">Clear</button>\n</div>\n'
        '<p id="status" role="status"></p>\n'
        '<p class="notice">This page loads nothing and sends nothing. It keeps your answers in'
        " this browser. Save writes them to a file. The file is a record of this page. A"
        " decision is confirmed in the session, never by the file.</p>\n<main>\n")
    rounds = "".join(_round_html(rnd, quotes) for rnd in slate["rounds"])
    tail = (
        '</main>\n<nav class="pager"><button type="button" id="prev">Previous</button>'
        ' <span id="position"></span> <button type="button" id="next">Next</button></nav>\n'
        '<section class="copy">\n<h2>Answers as text</h2>\n'
        "<p>If the download does not start, copy this text into a file named "
        f"<code>{name}.answers.json</code>.</p>\n"
        '<textarea id="answers-text" readonly rows="8" aria-label="Answers as text">'
        "</textarea>\n</section>\n<a id=\"download\" hidden></a>\n"
        f"<script>{script}</script>\n</body>\n</html>\n")
    # one kind of line end in the file: a row can hold a carriage return, and the page is
    # stored and compared as LF text (a browser reads both the same)
    return (head + top + rounds + tail).replace("\r\n", "\n").replace("\r", "\n")


# --------------------------------------------------------------------------- the answers

def _unique_keys(pairs: list) -> dict:
    out = dict(pairs)
    if len(out) != len(pairs):
        raise ValueError("a key is written twice")
    return out


def _no_constant(name: str):
    raise ValueError(f"{name} is not a JSON value")


def parse_strict(text: str):
    """JSON with no key written twice and no non-finite number. Raises ValueError."""
    try:
        return json.loads(text, object_pairs_hook=_unique_keys, parse_constant=_no_constant)
    except RecursionError:
        raise ValueError("the text nests too deep") from None


def _answer_text(owner: str, obj: dict, key: str) -> tuple[str, str | None]:
    value = obj.get(key, "")
    if not isinstance(value, str) or not encodable(value):
        return "", f"{owner}: `{key}` is text"
    if len(value) > MAX_ANSWER_TEXT:
        return "", f"{owner}: `{key}` holds {len(value)} characters (the cap is {MAX_ANSWER_TEXT})"
    return value, None


def read_answers(record: dict, digest: str, answers, changed: dict) -> dict:
    """A checked transcript of one answers file against its slate record, or {"error": why}.
    `changed` maps a quoted row id to what happened to it since the page was made. This
    reads and judges. It decides nothing, and it writes nothing."""
    slate = record["slate"]
    if not isinstance(answers, dict):
        return {"error": "the answers file is not a JSON object"}
    head = (answers.get("format"), answers.get("version"), answers.get("slate"))
    if head != (ANSWERS_FORMAT, VERSION, slate["name"]):
        return {"error": "the file's head reads (" + ", ".join(short(h) for h in head)
                         + "). This slate's answers file starts"
                         f" with {(ANSWERS_FORMAT, VERSION, slate['name'])!r}"}
    if answers.get("slate_digest") != digest:
        return {"error": "the answers were saved from another version of this slate (the"
                         " digest differs). Export the page again and put the questions again,"
                         " or read the answers against the slate that made them"}
    given, rounds_given = {}, {}
    for kind, items, key, into in (("answer", answers.get("answers"), "question", given),
                                   ("round", answers.get("rounds"), "id", rounds_given)):
        if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
            return {"error": f"the file's `{kind}s` is a list of objects"}
        for item in items:
            ident = item.get(key)
            if not isinstance(ident, str) or ident in into:
                return {"error": f"the file names the {kind} {short(ident)} twice, or without"
                                 " an id"}
            into[ident] = item
    known_questions = {q["id"] for rnd in slate["rounds"] for q in rnd["questions"]}
    if unknown := sorted(set(given) - known_questions):
        return {"error": "the file answers question(s) that the slate does not ask: "
                         + ", ".join(short(u) for u in unknown[:5])}
    if unknown := sorted(set(rounds_given) - {rnd["id"] for rnd in slate["rounds"]}):
        return {"error": "the file names round(s) that the slate does not have: "
                         + ", ".join(short(u) for u in unknown[:5])}
    out = {"rounds": [], "answers": [], "unanswered": [], "put_again": []}
    for rnd in slate["rounds"]:
        got = rounds_given.get(rnd["id"], {})
        info = {"id": rnd["id"], "title": rnd["title"], "closed": got.get("closed") is True}
        for key in ("attendance", "closed_by", "closure_note"):
            info[key], err = _answer_text(f"round {rnd['id']}", got, key)
            if err:
                return {"error": err}
        out["rounds"].append(info)
        for question in rnd["questions"]:
            got = given.get(question["id"], {})
            owner = f"question {question['id']}"
            labels = {o["id"]: o["label"] for o in question["options"]}
            selected = got.get("selected")
            legal = set(labels) | ({OTHER} if question["allow_other"] else set())
            if selected is not None and (not isinstance(selected, str)
                                         or selected not in legal):
                return {"error": f"{owner}: the file selects {short(selected)}, which is none of"
                                 f" its options ({', '.join(sorted(legal))})"}
            other, err = _answer_text(owner, got, "other")
            note, err2 = _answer_text(owner, got, "note")
            if err or err2:
                return {"error": err or err2}
            moved = [cid for cid in dict.fromkeys(question["cites"] + rnd["cites"])
                     if cid in changed]
            answer = {"question": question["id"], "round": rnd["id"],
                      "text": question["question"], "selected": selected,
                      "selected_label": (labels.get(selected) if selected != OTHER
                                         else other) if selected is not None else None,
                      "recommended": question["recommended"],
                      "equals_recommendation": (selected == question["recommended"]
                                                if selected is not None
                                                and question["recommended"] is not None
                                                else None),
                      # the free text is returned whatever is selected: text that was typed
                      # and left unselected is still on the page, and it is screened
                      "other": other, "note": note,
                      "cites": question["cites"], "changed_rows": moved}
            out["answers"].append(answer)
            if selected is None or (selected == OTHER and not other.strip()):
                out["unanswered"].append(question["id"])
            if moved:
                out["put_again"].append(question["id"])
    stamp = answers.get("exported_at")           # a time in one fixed form, or nothing
    out["exported_at"] = (stamp if isinstance(stamp, str) and EXPORTED_AT_RE.fullmatch(stamp)
                          else None)
    return out
