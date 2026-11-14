"""The interview page's shell (plans 227, 227b, 227c). Import `slate` first.

One page, one static script, one static style. Every text of the slate and of a quoted row
passes `esc()`. The script reads ids and its fixed words from data attributes, sets values,
classes and a few fixed attributes, and copies markup only from a template that is rendered
here. The policy in the head names the script by hash, so nothing else runs.

The shell is: the bar, the presenter's controls, the round navigator, the head, the rounds
(`slate_round`), the pager, and the two folds at the end.

What is hidden is hidden by the style, from classes on the root: `presenter`, `recs`,
`session`. That is a way to show the page. It protects nothing: the text is in the file.
"""
from __future__ import annotations

import base64
import hashlib
from pathlib import Path

from export_html import esc
from slate_round import Page, bdi, round_html
from slate_rows import question_digests
from slate_words import WORDS

HERE = Path(__file__).resolve().parent
SCRIPT_PATH = HERE / "slate.js"
STYLE_PATH = HERE / "slate.css"


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


def _button(ident: str, label: str, extra: str = "") -> str:
    return f'<button type="button" id="{ident}"{extra}>{label}</button>\n'


def _bar_html(page: Page) -> str:
    words = page.words

    def both(long: str, short: str) -> str:
        return (f'<span class="long">{esc(words[long])}</span>'
                f'<span class="short">{esc(words[short])}</span>')

    rounds = "".join(
        f'<option value="{esc(rnd["id"])}"{"" if rnd["ready"] else " disabled"}>'
        f'{esc(words["round"])} {n} · {esc(rnd["title"])}</option>'
        for n, rnd in enumerate(page.slate["rounds"], 1))
    return (
        '<div class="bar">\n<span id="progress" class="progress"></span>\n'
        f'<select id="round-pick" aria-label="{esc(words["round_pick"])}">{rounds}</select>\n'
        + _button("view-all", both("all", "all_short"))
        + _button("view-one", both("one", "one_short"))
        + _button("theme", "&#9680;", f' title="{esc(words["theme"])}"'
                                      f' aria-label="{esc(words["theme"])}"')
        + _button("save", both("save", "save_short"), ' class="primary"')
        + f'<details class="more"><summary>{esc(words["more"])}</summary><div class="menu">\n'
        + _button("presenter", esc(words["presenter"]), ' aria-pressed="false"')
        + _button("load-button", esc(words["load"]))
        + '<input type="file" id="load" accept=".json,application/json" hidden>\n'
        + _button("print", esc(words["print"])) + _button("clear", esc(words["clear"]))
        + "</div></details>\n</div>\n")


def _controls_html(page: Page) -> str:
    """The presenter's controls. They show only in the presenter view."""
    words = page.words
    people = "".join(f'<option value="{esc(p["id"])}">{esc(page.name(p["id"]))}</option>'
                     for p in page.slate["participants"])
    return (
        f'<div class="controls" role="group" aria-label="{esc(words["controls"])}">\n'
        f'<span class="ctitle">{esc(words["controls"])}</span>\n'
        + _button("lock", esc(words["lock"]), ' aria-pressed="false"')
        + _button("recs", esc(words["recs"]), ' aria-pressed="false"')
        + f'<span class="seg" role="group" aria-label="{esc(words["filter"])}">\n'
        + _button("f-all", esc(words["f_all"]), ' aria-pressed="true"')
        + _button("f-operator", esc(words["f_operator"]), ' aria-pressed="false"')
        + _button("f-room", esc(words["f_room"]), ' aria-pressed="false"') + "</span>\n"
        + (f'<select id="group-pick" aria-label="{esc(words["group"])}">'
           f'<option value="">{esc(words["group_all"])}</option>{people}</select>\n'
           if people else '<select id="group-pick" hidden><option value=""></option></select>\n')
        + "</div>\n")


def _nav_html(page: Page) -> str:
    """The list of rounds. A round that is not ready is listed and cannot be opened."""
    words, items = page.words, []
    for n, rnd in enumerate(page.slate["rounds"], 1):
        count = (f'{len(rnd["questions"])} {esc(words["questions"])}' if rnd["ready"]
                 else esc(words["not_ready"]))
        items.append(
            f'<button type="button" class="jump" data-jump="{esc(rnd["id"])}"'
            f'{"" if rnd["ready"] else " disabled"}><span class="jnum">{esc(words["round"])} {n}'
            f'</span><span class="jtitle">{bdi(rnd["title"])}</span>'
            f'<span class="jcount">{count}</span><span class="jstate"></span></button>\n')
    return (f'<nav class="roundnav" aria-label="{esc(words["rounds"])}">\n'
            f'<p class="navtitle">{esc(words["rounds"])}</p>\n<p class="navready"></p>\n'
            + "".join(items) + "</nav>\n")


def _head_html(page: Page) -> str:
    words, slate = page.words, page.slate
    return (
        '<header class="pagehead">\n'
        f'<h1>{bdi(slate["title"])}</h1>\n'
        + (f'<p class="intro">{bdi(slate["intro"])}</p>\n' if slate["intro"] else "")
        + f'<ol class="how"><li>{esc(words["how1"])}</li><li>{esc(words["how2"])}</li>'
        f'<li>{esc(words["how3"])}</li></ol>\n'
        f'<p class="legend"><span class="owner operator">{esc(words["owner_operator"])}</span>'
        f' {esc(words["legend_operator"])} <span class="owner room">'
        f'{esc(words["owner_room"])}</span> {esc(words["legend_room"])}</p>\n</header>\n')


def _tail_html(page: Page, digest: str) -> str:
    words, name = page.words, esc(page.slate["name"])
    return (
        f'<nav class="pager">{_button("prev", esc(words["prev"]))}'
        f'<span id="position"></span>{_button("next", esc(words["next"]))}</nav>\n'
        f'<details class="copy" id="trouble"><summary>{esc(words["trouble"])}</summary>\n'
        f'<p>{esc(words["trouble_text"])} <code id="answers-name">{name}.answers.json</code></p>\n'
        '<textarea id="answers-text" readonly rows="8"'
        f' aria-label="{esc(words["trouble"])}"></textarea>\n</details>\n'
        f'<details class="about"><summary>{esc(words["about"])}</summary>\n'
        f'<p>{esc(words["notice"])}</p>\n'
        f'<p class="meta">{esc(words["slate"])} <code>{name}</code>, {esc(words["digest"])}'
        f" <code>{esc(digest[:12])}</code></p>\n</details>\n"
        '<a id="download" hidden></a>\n<input type="file" id="load-round"'
        ' accept=".json,application/json" hidden>\n')


def render(record: dict, digest: str) -> str:
    """The page for one slate record. Every data text passes `esc()`. The script is the one
    static file, and the policy in the head names it by hash."""
    slate, script = record["slate"], script_text()
    words = WORDS[slate["language"]]
    page = Page(record, words, question_digests(record))
    css = STYLE_PATH.read_text(encoding="utf-8").replace("\r\n", "\n")
    total = sum(len(rnd["questions"]) for rnd in slate["rounds"])
    strings = "".join(f' data-w-{key[2:]}="{esc(text)}"' for key, text in words.items()
                      if key.startswith("s_"))
    head = (
        f'<!doctype html>\n<html lang="{esc(slate["language"])}" dir="{words["dir"]}">\n'
        '<head>\n<meta charset="utf-8">\n'
        f'<meta http-equiv="Content-Security-Policy" content="{esc(_policy(script))}">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{esc(slate['title'])}</title>\n<style>\n{css}</style>\n</head>\n"
        f'<body data-slate="{esc(slate["name"])}" data-digest="{esc(digest)}"'
        f' data-opens="{slate["opens"]}"{strings}>\n'
        f'<a class="skip" href="#rounds">{esc(words["skip"])}</a>\n')
    top = ('<div class="top">\n' + _bar_html(page) + _controls_html(page)
           + f'<p class="banner roombanner">{esc(words["room_banner"])}</p>\n'
           '<p class="banner stalebanner" hidden></p>\n'
           '<p class="banner storebanner" hidden></p>\n</div>\n'
           '<p id="status" role="status"></p>\n'
           '<div class="shell">\n' + _nav_html(page) + '<div class="column">\n'
           + _head_html(page) + '<main id="rounds">\n')
    rounds, start = [], 1
    for number, rnd in enumerate(slate["rounds"], 1):
        rounds.append(round_html(rnd, number, page, start, total))
        start += len(rnd["questions"])
    tail = ("</main>\n" + _tail_html(page, digest) + "</div>\n</div>\n"
            f"<script>{script}</script>\n</body>\n</html>\n")
    # one kind of line end in the file: a row can hold a carriage return, and the page is
    # stored and compared as LF text (a browser reads both the same)
    return (head + top + "".join(rounds) + tail).replace("\r\n", "\n").replace("\r", "\n")
