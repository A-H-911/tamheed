"""The steps of one round of the interview page (plan 227c). Import `slate` first.

A round is shown as steps, in this order: its context, attendance, its terms, each question,
the topics already decided, the points from the room, the closure. The view of one step at a
time turns these steps. Every text passes `esc()` here.

Classes that the style and the script read: `step` (one step), `oponly` (hidden in the room
view), `data-owner` on a question (the owner filter), `data-people` (the participant filter).
"""
from __future__ import annotations

import json

from export_html import esc
from slate import EVIDENCE, OTHER, UNKNOWN
from slate_rows import TITLE_COLUMNS, name_of, title_of

_LONG = 40                       # a text this long is shown as a paragraph of the quote
_AREA = ' rows="2" dir="auto" autocomplete="off" maxlength="8000"'


class Page:
    """What every part of one page reads: the record, its words, and what was derived."""

    def __init__(self, record: dict, words: dict, digests: dict):
        self.record, self.words, self.digests = record, words, digests
        self.slate, self.quotes, self.derived = record["slate"], record["rows"], record["derived"]
        self.titles = {}                       # question or decided-topic id -> (title, round)
        for rnd in self.slate["rounds"]:
            for q in rnd["questions"]:
                self.titles[q["id"]] = (q["question"], rnd["id"])
            for topic in rnd["decided"]:
                self.titles[topic["id"]] = (topic["title"], rnd["id"])

    def name(self, pid: str) -> str:
        return name_of(self.record, pid)

    def label(self, group: str, item: dict) -> str:
        """The label of a point kind or a closure field: the slate's own, or the page's word."""
        return item["label"] or self.words.get(f"{group}_{item['id']}", item["id"])


def cell(value) -> str:
    """A stored value as text: text as it is, a list of text joined, anything else as
    compact JSON."""
    if isinstance(value, str):
        return value
    if isinstance(value, list) and value and all(isinstance(x, str) for x in value):
        return ", ".join(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def bdi(value) -> str:
    """A text that keeps its own direction and stands where the page's direction puts it."""
    return f"<bdi>{esc(value)}</bdi>"


def _pairs(items) -> str:
    return "".join(f'<dt>{esc(name)}</dt><dd>{bdi(cell(value))}</dd>\n' for name, value in items)


def _name_line(rid: str, quote: dict) -> str:
    title, status = title_of(quote), dict(quote["columns"]).get("lifecycle_status", "")
    return (f'<span class="rid">{esc(rid)}</span><span class="kind">{esc(quote["type"])}</span>'
            + (f'<span class="status">{esc(status)}</span>' if status else "")
            + (f'<span class="rtitle">{bdi(title)}</span>' if title else ""))


def quote_html(rid: str, page: Page) -> str:
    """One quoted row as a fold. The summary names the row: its id, its family, its status
    and its title. Open, it shows the long texts first, then the declared fields of a
    register entry, then every other column under a second fold. Nothing is left out."""
    quote = page.quotes[rid]
    title = title_of(quote)
    attributes, body, rest = None, [], []
    for name, value in quote["columns"]:
        if name in TITLE_COLUMNS and str(value) == title or name == "lifecycle_status":
            continue
        if name == "custom_attributes":
            try:
                parsed = json.loads(value) if isinstance(value, str) else value
            except (ValueError, RecursionError):
                parsed = None
            if isinstance(parsed, dict) and parsed:
                attributes = parsed
                continue
        (body if isinstance(value, str) and len(value) > _LONG else rest).append((name, value))
    if not (body or attributes is not None or rest):
        # a row that is only its title has nothing to open: it is one line, not a fold
        return f'<div class="quote plain">{_name_line(rid, quote)}</div>\n'
    parts = [f'<details class="quote"><summary>{_name_line(rid, quote)}</summary>\n'
             '<div class="qbody">\n']
    parts.extend(f'<p class="qtext"><span class="qname">{esc(name)}</span>{bdi(value)}</p>\n'
                 for name, value in body)
    if attributes is not None:
        parts.append(f'<dl class="attrs">\n{_pairs(attributes.items())}</dl>\n')
    if rest:
        parts.append(f'<details class="fields"><summary>{esc(page.words["fields"])}</summary>\n'
                     f'<dl>\n{_pairs(rest)}</dl></details>\n')
    parts.append("</div></details>\n")
    return "".join(parts)


def rests_html(cites: list, page: Page) -> str:
    if not cites:
        return ""
    return (f'<div class="rests"><span class="restslabel">{esc(page.words["rests"])}</span>\n'
            + "".join(quote_html(cid, page) for cid in cites) + "</div>\n")


def _fold(kind: str, label: str, count: int | None, body: str) -> str:
    counted = f' <span class="count">({count})</span>' if count is not None else ""
    return (f'<details class="ctx {kind}"><summary>{esc(label)}{counted}</summary>\n'
            f'<div class="ctxbody">\n{body}</div></details>\n')


def named_html(ident: str, page: Page) -> str:
    """R113: the rows that this item's text names by id, each with its family and title."""
    ids = page.derived["named"].get(ident, [])
    if not ids:
        return ""
    return (f'<div class="named"><span class="restslabel">{esc(page.words["named"])}</span>\n'
            + "".join(f'<div class="quote plain">{_name_line(rid, page.quotes[rid])}</div>\n'
                      for rid in ids) + "</div>\n")


def _context_html(question: dict, rnd: dict, page: Page) -> str:
    """The folds under a question's answers: what is known, what is decided, what it depends
    on, what is missing, its terms, and the rows that its text names."""
    words, parts = page.words, []
    for key in ("known", "decided"):
        if question[key]:
            parts.append(_fold(key, words[key], len(question[key]),
                               "".join(quote_html(rid, page) for rid in question[key])))
    if question["depends_on"]:
        lines = []
        for target in question["depends_on"]:
            title, home = page.titles[target]
            where = words["same_round"] if home == rnd["id"] else words["other_round"]
            lines.append(f'<div class="quote plain"><span class="rid">{esc(target)}</span>'
                         f'<span class="rtitle">{bdi(title)}</span>'
                         f'<span class="kind">{esc(where)}</span></div>\n')
        parts.append(_fold("depends", words["depends"], len(lines), "".join(lines)))
    if question["gap"]:
        parts.append(_fold("gap", words["gap"], None, f'<p>{bdi(question["gap"])}</p>\n'))
    if terms := page.derived["terms"].get(question["id"], []):
        parts.append(_fold("termfold", words["terms_card"], len(terms),
                           _terms_list(terms, page)))
    return "".join(parts) + named_html(question["id"], page)


def _terms_list(ids: list, page: Page) -> str:
    out = []
    for rid in ids:
        columns = dict(page.quotes[rid]["columns"])
        out.append(f'<dt>{bdi(columns.get("term", rid))}</dt>'
                   f'<dd>{bdi(columns.get("definition", ""))}</dd>\n')
    return f'<dl class="termlist">\n{"".join(out)}</dl>\n'


def _radio(qid: str, value: str, body: str, cls: str = "") -> str:
    return (f'<label class="option{cls}"><input type="radio" name="q:{qid}"'
            f' value="{esc(value)}"><span class="obody">{body}</span></label>\n')


def _option_html(qid: str, option: dict, question: dict, words: dict) -> str:
    recommended = option["id"] == question["recommended"]
    body = [f'<span class="ohead"><span class="oid">{esc(option["id"])}</span>'
            f'<span class="otext">{bdi(option["label"])}</span>']
    if recommended:
        body.append(f'<span class="recmark">{esc(words["rec"])}</span>')
    body.append("</span>")
    if option["detail"]:
        body.append(f'<span class="odetail">{bdi(option["detail"])}</span>')
    if recommended:
        if question["basis"]:
            body.append(f'<span class="recbasis">{esc(words["basis_" + question["basis"]])}'
                        "</span>")
        body.append(f'<span class="recreason"><strong>{esc(words["why"])}</strong> '
                    f'{bdi(question["reason"])}</span>')
    return _radio(qid, option["id"], "".join(body), " rec" if recommended else "")


def _people_select(name: str, label: str, page: Page, field: str) -> str:
    """A select over the slate's participants and the operator. Its values are ids."""
    words = page.words
    options = [f'<option value="">— {esc(words["choose"])} —</option>',
               f'<option value="operator">{esc(words["operator"])}</option>']
    options += [f'<option value="{esc(p["id"])}">{esc(page.name(p["id"]))}</option>'
                for p in page.slate["participants"]]
    return (f'<label class="who">{esc(label)} <select data-field="{field}" name="{esc(name)}">'
            + "".join(options) + "</select></label>\n")


def question_html(question: dict, rnd: dict, page: Page, place: int, total: int) -> str:
    words, qid = page.words, esc(question["id"])
    people = [p for p in [question["lead"], *question["consulted"]] if p]
    meta = [f'<span class="place">{place} / {total}</span><span class="qid">{qid}</span>'
            f'<span class="owner {question["owner"]}">{esc(words["owner_" + question["owner"]])}'
            "</span>"]
    if question["lead"]:
        meta.append(f'<span class="lead">{esc(words["lead"])}: {bdi(page.name(question["lead"]))}'
                    "</span>")
    if question["approval"]:
        meta.append(f'<span class="approval">{esc(words["approval"])}</span>')
    meta.append(f'<span class="state">{esc(words["answered"])}</span>')
    parts = [f'<fieldset class="question step" data-question="{qid}"'
             f' data-digest="{esc(page.digests[question["id"]])}"'
             f' data-owner="{question["owner"]}" data-people="{esc("|".join(people))}">\n'
             f'<legend><span class="qmeta">{"".join(meta)}</span>'
             f'<span class="qtitle">{bdi(question["question"])}</span></legend>\n'
             f'<p class="stale" hidden>{esc(words["stale"])}</p>\n']
    if question["block"]:
        parts.append(f'<p class="inblock">{bdi(question["block"])}</p>\n')
    if question["detail"]:
        parts.append(f'<p class="detail">{bdi(question["detail"])}</p>\n')
    if question["consulted"]:
        names = ", ".join(page.name(p) for p in question["consulted"])
        parts.append(f'<p class="consulted">{esc(words["consulted"])}: {bdi(names)}</p>\n')
    parts.append(rests_html(question["cites"], page))
    parts.append('<div class="options">\n')
    parts.extend(_option_html(qid, option, question, words) for option in question["options"])
    if question["allow_unsure"]:
        parts.append(f'<p class="unsure">{esc(words["unsure"])}</p>\n<div class="fallback">\n'
                     + "".join(_radio(qid, value, f'<span class="otext">{esc(words[value])}'
                                      "</span>", " small") for value in (UNKNOWN, EVIDENCE))
                     + "</div>\n")
    if question["allow_other"]:
        parts.append(_radio(
            qid, OTHER,
            f'<span class="ohead"><span class="otext">{esc(words["other"])}</span></span>'
            f'<textarea data-field="other" name="other:{qid}"{_AREA}'
            f' aria-label="{esc(words["other"])}"></textarea>', " other"))
    parts.append("</div>\n" + _people_select(f"by:{qid}", words["answered_by"], page,
                                             "answered_by"))
    parts.append(f'<details class="noteblock"><summary>{esc(words["note"])}</summary>'
                 f'<textarea data-field="note" name="note:{qid}"{_AREA}'
                 f' aria-label="{esc(words["note"])}"></textarea></details>\n')
    if question["settles"]:
        parts.append(f'<div class="settles"><span class="restslabel">{esc(words["settles"])}'
                     f'</span>\n{quote_html(question["settles"], page)}</div>\n')
    parts.append(_context_html(question, rnd, page) + "</fieldset>\n")
    return "".join(parts)


def _attendance_html(rnd: dict, page: Page) -> str:
    words, rid = page.words, esc(rnd["id"])
    people = [p for p in page.slate["participants"] if p["attends"]]
    if not people:
        return ""
    rows = []
    for person in people:
        pid = esc(person["id"])
        rows.append(
            f'<div class="attrow" data-person="{pid}"><label class="pname">'
            f'{bdi(page.name(person["id"]))}'
            f'<select data-field="state" name="att:{rid}:{pid}">'
            f'<option value="">{esc(words["not_recorded"])}</option>'
            f'<option value="present">{esc(words["present"])}</option>'
            f'<option value="covered">{esc(words["covered"])}</option></select></label>'
            f'<input type="text" data-field="covered_by" name="cover:{rid}:{pid}" dir="auto"'
            f' autocomplete="off" maxlength="8000" placeholder="{esc(words["covered_by"])}"'
            f' aria-label="{esc(words["covered_by"])}"></div>\n')
    return ('<div class="attendance step oponly">\n'
            f'<p class="stepname">{esc(words["attendance"])}</p>\n'
            f'<p class="hint">{esc(words["presenter_note"])}</p>\n'
            f'<div class="attgrid">\n{"".join(rows)}</div>\n'
            f'<label class="wide">{esc(words["guests"])} <input type="text" data-field="guests"'
            f' name="guests:{rid}" dir="auto" autocomplete="off" maxlength="8000"'
            f' placeholder="{esc(words["guests_hint"])}"></label>\n</div>\n')


def _terms_html(rnd: dict, page: Page) -> str:
    ids = sorted({rid for q in rnd["questions"]
                  for rid in page.derived["terms"].get(q["id"], [])})
    if not ids:
        return ""
    return ('<div class="terms step">\n'
            f'<p class="stepname">{esc(page.words["terms"])} ({len(ids)})</p>\n'
            f'<p class="hint">{esc(page.words["terms_note"])}</p>\n'
            + _terms_list(ids, page) + "</div>\n")


def _decided_html(rnd: dict, page: Page) -> str:
    if not rnd["decided"]:
        return ""
    words, lines = page.words, []
    for topic in rnd["decided"]:
        lines.append(
            f'<div class="topic"><p class="ttitle"><span class="rid">{esc(topic["id"])}</span>'
            f' {bdi(topic["title"])}</p>\n<p class="tanswer">{bdi(topic["answer"])}</p>\n'
            + "".join(quote_html(cid, page) for cid in topic["cites"])
            + named_html(topic["id"], page) + "</div>\n")
    return ('<div class="decidedstep step">\n'
            f'<p class="stepname">{esc(words["decided_title"])} ({len(lines)})</p>\n'
            f'<p class="hint">{esc(words["decided_note"])}</p>\n' + "".join(lines)
            + f'<label class="wide">{esc(words["reopen"])} <textarea data-field="reopen"'
            f' name="reopen:{esc(rnd["id"])}"{_AREA}></textarea></label>\n</div>\n')


def _points_html(rnd: dict, page: Page) -> str:
    """The points from the room. The script copies the template for each line that is
    added, and it writes no markup of its own."""
    words = page.words
    kinds = "".join(f'<option value="{esc(k["id"])}">{esc(page.label("kind", k))}</option>'
                    for k in page.slate["point_kinds"])
    return ('<div class="points step">\n'
            f'<p class="stepname">{esc(words["points"])}</p>\n'
            f'<p class="hint">{esc(words["points_note"])}</p>\n<div class="pointlist"></div>\n'
            '<template class="pointrow"><div class="point">\n'
            f'<label>{esc(words["kind"])} <select data-field="kind">{kinds}</select></label>\n'
            + _people_select("", words["raised_by"], page, "by")
            + f'<label class="wide">{esc(words["in_words"])} <textarea data-field="text"{_AREA}>'
            "</textarea></label>\n"
            f'<button type="button" data-action="remove-point">{esc(words["remove"])}</button>\n'
            "</div></template>\n"
            f'<button type="button" data-action="add-point">{esc(words["add_point"])}</button>\n'
            "</div>\n")


def _closure_html(rnd: dict, page: Page) -> str:
    words, rid = page.words, esc(rnd["id"])
    fields = "".join(
        f'<label>{esc(page.label("closure", f))} <textarea data-closure="{esc(f["id"])}"'
        f' name="closure:{rid}:{esc(f["id"])}"{_AREA}></textarea></label>\n'
        for f in page.slate["closure_fields"])
    return ('<div class="closure step oponly">\n'
            f'<p class="stepname">{esc(words["closure"])}</p>\n'
            f'<p class="hint">{esc(words["presenter_note"])}</p>\n'
            f'<div class="closuregrid">\n{fields}</div>\n'
            f'<label>{esc(words["closed_by"])} <input type="text" data-field="closed_by"'
            f' name="closed_by:{rid}" dir="auto" autocomplete="off" maxlength="8000"></label>\n'
            f'<label class="check"><input type="checkbox" data-field="closed" name="closed:{rid}">'
            f' {esc(words["closed"])}</label>\n'
            '<div class="roundactions">\n'
            f'<button type="button" class="primary" data-action="save-round">'
            f'{esc(words["save_round"])}</button>\n'
            f'<button type="button" data-action="load-round">{esc(words["load_round"])}</button>\n'
            f'<button type="button" data-action="clear-round">{esc(words["clear_round"])}'
            "</button>\n</div>\n</div>\n")


def round_html(rnd: dict, number: int, page: Page, start: int, total: int) -> str:
    """One round: its head, then its steps. A round that is not ready is only its head."""
    words, rid = page.words, esc(rnd["id"])
    parts = [f'<section class="round{"" if rnd["ready"] else " notready"}" data-round="{rid}">'
             '\n<div class="roundtop">\n'
             f'<h2><span class="rnum">{esc(words["round"])} {number}</span> {bdi(rnd["title"])}'
             "</h2>\n"
             + (f'<p class="roundcount"></p>\n<div class="meter"><span></span></div>\n'
                if rnd["ready"] else f'<p class="roundcount">{esc(words["not_ready"])}</p>\n')
             + "</div>\n"]
    if not rnd["ready"]:
        return "".join(parts) + "</section>\n"
    if rnd["intro"] or rnd["cites"]:
        parts.append('<div class="roundhead step">\n'
                     f'<p class="stepname">{esc(words["context"])}</p>\n'
                     + (f'<p class="lead">{bdi(rnd["intro"])}</p>\n' if rnd["intro"] else "")
                     + rests_html(rnd["cites"], page) + "</div>\n")
    parts.append(_attendance_html(rnd, page) + _terms_html(rnd, page))
    block = None
    for n, question in enumerate(rnd["questions"]):
        if question["block"] and question["block"] != block:
            parts.append(f'<h3 class="blockhead">{bdi(question["block"])}</h3>\n')
        block = question["block"]
        parts.append(question_html(question, rnd, page, start + n, total))
    parts.append(_decided_html(rnd, page) + _points_html(rnd, page) + _closure_html(rnd, page)
                 + "</section>\n")
    return "".join(parts)
