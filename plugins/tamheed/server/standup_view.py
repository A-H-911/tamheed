"""The standup report as a delivery report (plan 251 v2, ADR-0005): the page of a report row
whose facts hold the plan tree. A pure function of the row: the facts frozen at the draft, the
agent's words and the page meta. Rows of 6.7.0 (no `plan` key) keep the layout of
`standup_page`.

Sections: the header, 1 Summary, 2 Needs your decision, 3 Plan overview (the one tree), 4 What
we did, 5 What we are working on now, 6 What we expect next, 7 Challenges and decisions,
8 Glossary, and the folded Record details. Every count reads `standup_facts.row_state`.
"""
from __future__ import annotations

import base64
import hashlib
import re
from pathlib import Path

import standup_facts as F
import standup_families as FAM
import standup_page as P

SCRIPT_PATH = Path(__file__).with_name("standup.js")
esc = P.esc
STATES = F.STATES
WORD = {"done-window": "done this window", "claimed-window": "claimed this window",
        "done-earlier": "done earlier", "blocked": "blocked", "in-progress": "in progress",
        "next": "next", "not-started": "not started", "failed": "failed",
        "not-checked": "not checked yet", "postponed": "postponed", "done": "done"}
DONE = ("done-window", "done-earlier")
GLOSS = {
    "done this window": "Finished inside this window: a task moved to done, or a check passed.",
    "claimed this window": "The agent said the task is finished inside this window. Nobody"
                           " confirmed it yet, so it does not count as done.",
    "done earlier": "Finished before this window started.",
    "blocked": "Waits on something that is not settled yet, such as an open question.",
    "in progress": "Work has started and is not finished: claimed earlier, or worked on in"
                   " this window.",
    "next": "Expected to start next: the open tasks of the current slice with no work yet, and"
            " the next slice.",
    "not started": "Planned, with no work yet, and not next.",
    "failed": "An acceptance check whose newest result is failed or partly passed.",
    "not checked yet": "An acceptance check with no result yet.",
    "postponed": "Moved to later on purpose. It is outside the counts.",
    "current slice": "The slice the team works on now. The agent names it, and the operator"
                     " confirms it.",
    "this window": "The stretch of time this report covers. Its dates are in the header.",
    "claimed done": "The agent says the work is finished, and nobody confirmed it yet.",
    "ready to close": "Every release rule of the package passes. Until then, the page names the"
                      " rules that fail.",
    "journal": "The work log of the package.",
    "checkpoint": "A report that keeps the full state, so later reports can be checked.",
}


def script() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def policy(source: str) -> str:
    """The page's content policy: the review page's, plus the one script named by its hash."""
    digest = base64.b64encode(hashlib.sha256(source.encode("utf-8")).digest()).decode()
    # ste:allow semicolon: a content policy separates its directives with semicolons
    return (f"default-src 'none'; style-src 'unsafe-inline'; script-src 'sha256-{digest}';"
            " base-uri 'none'; form-action 'none'")


def walk(nodes, depth=0):
    for n in nodes:
        yield n, depth
        yield from walk(n.get("children", []), depth + 1)


def bar(done: int, total: int, label: str = "tasks done") -> str:
    pct = 0 if not total else round(100 * done / total)
    return (f'<span class="bar" role="img" aria-label="{done} of {total} {label}">'
            f'<span style="width:{pct}%"></span></span><span class="frac">{done}/{total}</span>')


def chip(state: str) -> str:
    return f'<span class="state s-{state}">{esc(WORD.get(state, state))}</span>'


def text_of(n: dict) -> str:
    return esc(f"{n.get('title', '')} {n['id']}".lower())


class Page:
    """One report page. The facts are frozen at the draft; nothing here reads a store."""

    def __init__(self, meta: dict, facts: dict, narrative: dict | None):
        self.meta, self.f, self.n = meta, facts, dict(narrative or {})
        self.first = bool(facts.get("view", {}).get("first", meta.get("first")))
        self.cite = P.Cite({**facts.get("names", {}), **self.n.get("_names", {})})
        suggest = facts["plan"].get("suggest", {})
        self.now = self.n.get("slice_now") or suggest.get("now")
        self.next = self.n.get("slice_next") or suggest.get("next")
        self.touched = set(facts.get("touched", []))
        self.state: dict[str, str] = {}
        self.kind_of: dict[str, str] = {}
        self.phase_of: dict[str, str] = {}
        self.slice_of: dict[str, str] = {}
        self._classify()

    # ------------------------------------------------------------------ one state per row
    def _ctx(self, slice_id):
        return {"slice": slice_id, "now": self.now, "next": self.next, "touched": self.touched,
                "first": self.first}

    def _put(self, node, kind, phase, slice_id):
        self.state[node["id"]] = F.row_state(node, kind, self._ctx(slice_id))
        self.kind_of[node["id"]], self.phase_of[node["id"]] = kind, phase
        if slice_id:
            self.slice_of[node["id"]] = slice_id

    def _classify(self):
        plan = self.f["plan"]
        for ph in plan["phases"]:
            for s in ph["slices"]:
                for t, _d in walk(s["tasks"]):
                    self._put(t, "task", ph["id"], s["id"])
                for c in s["checks"]:
                    self._put(c, "check", ph["id"], s["id"])
            for t, _d in walk(ph.get("loose", [])):
                self._put(t, "task", ph["id"], None)
        for t, _d in walk(plan["outside"]["tasks"]):
            self._put(t, "task", "outside", None)
        for c in plan["outside"]["checks"]:
            self._put(c, "check", "outside", None)

    def count(self, states, kinds=("task",), where=None) -> int:
        return sum(1 for i, s in self.state.items() if s in states and self.kind_of[i] in kinds
                   and (where is None or where(i)))

    def delivery_word(self, node: dict, ids: list[str]) -> str:
        """U14: a phase or a slice in delivery words, never a record status."""
        if node.get("status") == "Implemented":
            return "done"
        if node["id"] == self.now or any(self.slice_of.get(i) == self.now for i in ids):
            return "in-progress"
        if any(self.state.get(i) in DONE + ("claimed-window", "in-progress") for i in ids):
            return "in-progress"
        if self.next and (node["id"] == self.next
                          or any(self.slice_of.get(i) == self.next for i in ids)):
            return "next"
        return "not-started"

    def window_badge(self, ids) -> str:
        if self.first:
            return ""
        d = sum(1 for i in ids if self.state.get(i) == "done-window")
        c = sum(1 for i in ids if self.state.get(i) == "claimed-window")
        return " ".join(([f'<span class="state s-done-window">✓ {d}</span>'] if d else [])
                        + ([f'<span class="state s-claimed-window">◐ {c}</span>'] if c else []))

    def rec(self, n: dict, st: str) -> str:
        """The record's own status, small, only when it says what the state word does not."""
        word = P.plain(n.get("status"))
        same = {"done-window": "done", "done-earlier": "done", "claimed-window": "claimed done",
                "in-progress": "claimed done"}
        if n.get("status") is None or word == same.get(st) or self.kind_of.get(n["id"]) == "check":
            return ""
        return f'<span class="rec">record: {esc(word)}</span>'

    # ------------------------------------------------------------------ tree rows
    def leaf(self, n: dict, kind: str, depth: int) -> str:
        st = self.state.get(n["id"], "not-started")
        win = ('<span class="muted">worked on</span>' if n["id"] in self.touched
               and st not in ("done-window", "claimed-window") else "")
        prog = (f'<span class="muted">{esc(P.plain(n["result"]) if n.get("result") else "no result yet")}</span>'
                if kind == "check" else "")
        mark = f'<span class="kindmark">{kind}</span>' if kind in ("check", "milestone") else ""
        return (f'<div class="row lvl-{depth}" data-row data-item data-kind="{kind}"'
                f' data-state="{st}" data-phase="{esc(self.phase_of.get(n["id"], ""))}"'
                f' data-text="{text_of(n)}"><div class="cells"><span class="item">'
                f'<span class="tw"></span>{mark}<span class="t">{self.cite.hover(n.get("title") or "")}'
                f'</span><span class="ref">{esc(n["id"])}</span></span><span class="c-status">'
                f'{chip(st)}{self.rec(n, st)}</span><span class="c-prog">{prog}</span>'
                f'<span class="c-win">{win}</span></div></div>')

    def task_rows(self, nodes, depth) -> str:
        out = []
        for n in nodes:
            kids = n.get("children", [])
            if not kids:
                out.append(self.leaf(n, "task", depth))
                continue
            st = self.state[n["id"]]
            ids = [c["id"] for c, _ in walk(kids)]
            done = sum(1 for i in ids if self.state[i] in DONE)
            opened = not self.first and any(
                self.state[i] in ("done-window", "claimed-window", "in-progress") for i in ids)
            out.append(f'<details class="row lvl-{depth}" data-row data-item data-kind="task"'
                       f' data-state="{st}" data-phase="{esc(self.phase_of.get(n["id"], ""))}"'
                       f' data-text="{text_of(n)}"{" open" if opened else ""}><summary>'
                       f'<div class="cells"><span class="item"><span class="tw"></span>'
                       f'<span class="t">{self.cite.hover(n.get("title") or "")}</span>'
                       f'<span class="ref">{esc(n["id"])}</span></span><span class="c-status">'
                       f'{chip(st)}{self.rec(n, st)}</span><span class="c-prog">'
                       f'{bar(done, len(ids))}</span><span class="c-win">{self.window_badge(ids)}'
                       '</span></div></summary>' + self.task_rows(kids, depth + 1) + "</details>")
        return "".join(out)

    def slice_row(self, s: dict, phase: str, depth: int, opened: bool | None = None) -> str:
        tasks = [t["id"] for t, _ in walk(s["tasks"])]
        ids = tasks + [c["id"] for c in s["checks"]]
        word = self.delivery_word(s, tasks)
        done = sum(1 for i in tasks if self.state[i] in DONE)
        mark = ('<span class="state s-now">now</span> ' if s["id"] == self.now else
                '<span class="state s-next">next</span> ' if s["id"] == self.next else "")
        shown_word = "" if (word == "next" and s["id"] == self.next) else chip(word)
        record = ("" if word == "done" else
                  f'<span class="rec">record: {esc(P.plain(s.get("status")))}</span>')
        news = any(self.state[i] in ("done-window", "claimed-window", "in-progress", "failed",
                                     "blocked") for i in ids)
        is_open = (s["id"] == self.now or news) if opened is None else opened
        body = (self.task_rows(s["tasks"], depth + 1)
                + "".join(self.leaf(c, "check", depth + 1) for c in s["checks"]))
        return (f'<details class="row lvl-{depth}" data-row data-kind="slice"'
                f' data-phase="{esc(phase)}"{" open" if is_open else ""}><summary>'
                f'<div class="cells"><span class="item"><span class="tw"></span>'
                f'<span class="kindmark">slice</span><span class="t">{self.cite.hover(s["title"])}'
                f'</span><span class="ref">{esc(s["id"])}</span></span><span class="c-status">'
                f'{mark}{shown_word}{record}</span><span class="c-prog">{bar(done, len(tasks))}'
                f'</span><span class="c-win">{self.window_badge(ids)}</span></div></summary>'
                + (body or '<p class="empty">No tasks yet.</p>') + "</details>")

    def phase_row(self, ph: dict) -> str:
        tasks = [i for i in self.state if self.phase_of.get(i) == ph["id"]
                 and self.kind_of[i] == "task"]
        live = [i for i in tasks if self.state[i] != "postponed"]
        done = sum(1 for i in live if self.state[i] in DONE)
        word = self.delivery_word(ph, tasks)
        left = sum(1 for i in live if self.state[i] not in DONE)
        extra = (f'<span class="rec">· {P.count(left, "task", "tasks")} still open</span>'
                 if ph.get("status") == "Implemented" and left else "")
        news = any(self.state[i] in ("done-window", "claimed-window", "in-progress", "failed")
                   for i in self.state if self.phase_of.get(i) == ph["id"])
        is_open = news or any(s["id"] in (self.now, self.next) for s in ph["slices"])
        stones = "".join(
            f'<div class="row lvl-1" data-row data-item data-kind="milestone"'
            f' data-state="milestone" data-phase="{esc(ph["id"])}" data-text="{text_of(m)}">'
            '<div class="cells"><span class="item"><span class="tw"></span>'
            f'<span class="kindmark">milestone</span><span class="t">{esc(m["title"])}</span>'
            f'<span class="ref">{esc(m["id"])}</span></span><span class="c-status">'
            f'<span class="muted">{("due " + esc(m["due"])) if m.get("due") else "no date"}'
            '</span></span><span class="c-prog"></span><span class="c-win"></span></div></div>'
            for m in ph.get("milestones", []))
        loose = ph.get("loose", [])
        loose_html = ""
        if loose:
            ids = [t["id"] for t, _ in walk(loose)]
            loose_html = (f'<details class="row lvl-1" data-row data-kind="group"'
                          f' data-phase="{esc(ph["id"])}"><summary><div class="cells">'
                          '<span class="item"><span class="tw"></span><span class="t">Not in a'
                          ' slice</span></span><span class="c-status"><span class="muted">'
                          f'{P.count(len(ids), "task", "tasks")}</span></span>'
                          f'<span class="c-prog"></span><span class="c-win">'
                          f'{self.window_badge(ids)}</span></div></summary>'
                          + self.task_rows(loose, 2) + "</details>")
        record = ("" if word == "done" else
                  f'<span class="rec">record: {esc(P.plain(ph.get("status")))}</span>')
        return (f'<details class="row lvl-0" data-row data-kind="phase"'
                f' data-phase="{esc(ph["id"])}"{" open" if is_open else ""}><summary>'
                '<div class="cells"><span class="item"><span class="tw"></span>'
                f'<span class="kindmark">phase</span><span class="t">{self.cite.hover(ph["title"])}'
                f'</span><span class="ref">{esc(ph["id"])}</span></span><span class="c-status">'
                f'{chip(word)}{record}{extra}</span><span class="c-prog">{bar(done, len(live))}'
                f'</span><span class="c-win">{self.window_badge(tasks)}</span></div></summary>'
                + stones + "".join(self.slice_row(s, ph["id"], 1) for s in ph["slices"])
                + loose_html + "</details>")

    def filtered_tree(self, keep: set[str]) -> str:
        """A static view: the rows in a state of `keep`, under their phase and slice."""
        out = []
        for ph in self.f["plan"]["phases"]:
            slices = []
            for s in ph["slices"]:
                rows = "".join(self.leaf(t, "task", 2) for t, _ in walk(s["tasks"])
                               if self.state[t["id"]] in keep)
                rows += "".join(self.leaf(c, "check", 2) for c in s["checks"]
                                if self.state[c["id"]] in keep)
                if rows:
                    slices.append(self._label(s, "slice", 1) + rows)
            if slices:
                out.append(self._label(ph, "phase", 0) + "".join(slices))
        return (f'<div class="tree compact">{"".join(out)}</div>' if out
                else '<p class="empty">Nothing.</p>')

    def _label(self, n, kind, depth) -> str:
        return (f'<div class="row lvl-{depth}"><div class="cells"><span class="item">'
                f'<span class="tw"></span><span class="kindmark">{kind}</span>'
                f'<span class="t">{self.cite.hover(n["title"])}</span><span class="ref">'
                f'{esc(n["id"])}</span></span><span class="c-status"></span>'
                '<span class="c-prog"></span><span class="c-win"></span></div></div>')

    # ------------------------------------------------------------------ sections
    def header(self) -> str:
        m, n = self.meta, self.n
        rule = P._safe_colour(m.get("rule_colour"))
        colour = P._safe_colour(m.get("colour") or n.get("colour") or rule)
        word = "Proposed overall" if m.get("draft") else "Overall"
        why = (f'<div class="rule">By the default rule it would be'
               f' {esc(P.COLOUR_WORDS[rule].lower())}'
               f'{(": " + esc(", ".join(m.get("rule_reasons", [])))) if m.get("rule_reasons") else ""}.</div>'
               if colour != rule else "")
        status = ('<p class="banner">Draft: not recorded yet.</p>' if m.get("draft") else
                  f'<p class="muted">Recorded by {esc(m.get("recorded_by"))} on'
                  f' {esc(m.get("recorded_on"))}.</p>')
        first = ('<p class="banner">This is the first report: everything below is since the'
                 ' start of the package, so it shows the overall picture only.</p>'
                 if self.first else "")
        notes = "".join(f'<p class="muted">{esc(x)}</p>' for x in m.get("notes", []))
        return (f'<header><div class="top"><div><h1>Standup report {esc(m["id"])}</h1>'
                f'<div class="pkg">{esc(m["package"])}</div></div>{P.THEME}</div>'
                f'<p class="window">This window: {esc(m["start_text"])} → {esc(m["end_text"])}</p>'
                + status + first + notes
                + f'<div class="verdict {esc(colour)}"><strong>{word}: {esc(P.COLOUR_WORDS[colour])}.'
                f'</strong> {self.cite.html(str(n.get("colour_reason") or ""))}{why}</div></header>')

    def summary(self) -> str:
        live = [i for i, s in self.state.items() if self.kind_of[i] == "task"
                and s != "postponed" and self.phase_of.get(i) != "outside"]
        done_all = sum(1 for i in live if self.state[i] in DONE)
        pct = round(100 * done_all / len(live)) if live else 0
        outside = [i for i in self.state if self.phase_of.get(i) == "outside"
                   and self.kind_of[i] == "task"]
        cur = [i for i in self.state if self.slice_of.get(i) == self.now
               and self.kind_of[i] == "task"]
        cur_open = sum(1 for i in cur if self.state[i] not in DONE + ("postponed",))
        cur_done = sum(1 for i in cur if self.state[i] in DONE)
        needs = sum(self.f["needs"][k]["total"] for k in
                    ("approve_decisions", "approve_scope", "confirm_rows", "questions_overdue"))
        risks = self.f["challenges"]["risks_high"]["total"]
        severe = sum(1 for it in self.f["challenges"]["defects_open"]["items"]
                     if it.get("note") in ("critical", "high"))
        cards = []
        if not self.first:
            cards.append(("Done this window", self.count({"done-window"}, ("task", "check")),
                          f'{self.count({"done-window"})} tasks · '
                          f'{self.count({"done-window"}, ("check",))} checks · '
                          f'{self.count({"claimed-window"})} claimed'))
        cards += [
            ("Done overall", f"{pct}%", f"{done_all} of {len(live)} tasks in the plan"
             + (f" · {len(outside)} outside it" if outside else "")),
            ("Working on now", self.now or "—",
             f"{cur_open} open of {len(cur)} tasks · {bar(cur_done, len(cur))}" if self.now
             else "no open slice"),
            ("Next", self.next or ("the rest of " + self.now if self.now else "—"),
             f'{self.count({"next"})} tasks expected to start'),
            ("Needs your decision", needs, "approvals and answers"),
            ("Risks and defects", f"{risks} · {severe}",
             "open high risks · critical or high defects")]
        html = "".join(f'<div class="kpi"><div class="label">{esc(a)}</div><div class="value">'
                       f'{esc(b)}</div><div class="sub">{c}</div></div>' for a, b, c in cards)
        head = (f'<div class="headline">{P._text(self.n.get("headline"), self.cite.section())}'
                '</div>' if self.n.get("headline") else "")
        return ('<section class="card" id="summary"><h2><span class="num">1</span>Summary</h2>'
                f'<div class="cards">{html}</div>{head}</section>')

    def needs(self) -> str:
        n, cite = self.f["needs"], self.cite.section()
        b = (lambda label, data: P.block(label, data, P.VISIBLE, cite=cite))  # noqa: E731
        body = (b("Decisions waiting for your approval", n["approve_decisions"])
                + b("Scope changes waiting for your approval", n["approve_scope"])
                + b("Lessons and feedback to confirm", n["confirm_rows"])
                + b("Open questions past their date", n["questions_overdue"])
                + b("Asked in the last session", n["awaiting_operator"]))
        return ('<section class="card" id="needs"><h2><span class="num">2</span>Needs your'
                ' decision</h2>' + (body or '<p class="empty">Nothing waits for you.</p>')
                + "</section>")

    def overview(self) -> str:
        plan = self.f["plan"]
        counts = {s: self.count({s}, ("task", "check")) for s in STATES}
        allowed = [s for s in STATES if counts[s]
                   and not (self.first and s in ("done-window", "claimed-window"))]
        chips = "".join(f'<button type="button" data-filter="state" data-value="{s}"'
                        f' aria-pressed="false">{esc(WORD[s])}<span class="n">{counts[s]}</span>'
                        "</button>" for s in allowed)
        kinds = "".join(f'<button type="button" data-filter="kind" data-value="{k}"'
                        f' aria-pressed="false">{w}</button>'
                        for k, w in (("task", "Tasks"), ("check", "Checks"),
                                     ("milestone", "Milestones")))
        phases = "".join(f'<option value="{esc(p["id"])}">{esc(p["id"])} · '
                         f'{esc(P.short(p["title"]))}</option>' for p in plan["phases"])
        controls = (
            '<div id="tree-controls" hidden><div class="toolbar"><div class="chips" role="group"'
            ' aria-label="State"><button type="button" data-filter="state" data-value="all"'
            f' aria-pressed="true">All states</button>{chips}</div></div><div class="toolbar">'
            '<div class="chips" role="group" aria-label="Kind"><button type="button"'
            ' data-filter="kind" data-value="all" aria-pressed="true">All kinds</button>'
            f'{kinds}</div><label>Phase <select id="tree-phase"><option value="all">All phases'
            f'</option>{phases}<option value="outside">Outside the plan</option></select></label>'
            '<label>Search <input id="tree-search" type="search" placeholder="words or an id">'
            '</label><button type="button" class="act" id="tree-open">Expand all</button>'
            '<button type="button" class="act" id="tree-close">Collapse all</button></div>'
            '<p id="tree-status" class="muted" role="status" aria-atomic="true"></p></div>')
        outside = plan["outside"]
        ids = ([t["id"] for t, _ in walk(outside["tasks"])]
               + [c["id"] for c in outside["checks"]])
        out_html = ("" if not ids else
                    '<details class="row lvl-0" data-row data-kind="group" data-phase="outside">'
                    '<summary><div class="cells"><span class="item"><span class="tw"></span>'
                    '<span class="t">Outside the plan</span></span><span class="c-status">'
                    f'<span class="muted">{P.count(len(ids), "item", "items")} with no phase'
                    f'</span></span><span class="c-prog"></span><span class="c-win">'
                    f'{self.window_badge(ids)}</span></div></summary>'
                    + self.task_rows(outside["tasks"], 1)
                    + "".join(self.leaf(c, "check", 1) for c in outside["checks"]) + "</details>")
        head = ('<div class="tree-head"><span>Item</span><span>Status</span><span>Progress</span>'
                '<span>This window</span></div>')
        return ('<section class="card" id="plan"><h2><span class="num">3</span>Plan overview</h2>'
                '<p class="muted">Every phase, slice, task, acceptance check and milestone. The'
                ' branches with work in this window, and the current and next slices, are'
                ' open.</p>' + controls + f'<div class="tree" id="tree">{head}'
                + "".join(self.phase_row(p) for p in plan["phases"]) + out_html
                + "</div></section>")

    def did(self) -> str:
        cite = self.cite.section()
        words = P._text(self.n.get("did"), cite)
        rows = []
        for ph in self.f["plan"]["phases"]:
            tasks = [i for i in self.state if self.phase_of.get(i) == ph["id"]
                     and self.kind_of[i] == "task" and self.state[i] != "postponed"]
            checks = [i for i in self.state if self.phase_of.get(i) == ph["id"]
                      and self.kind_of[i] == "check"]
            done = sum(1 for i in tasks if self.state[i] in DONE)
            passed = sum(1 for i in checks if self.state[i] in DONE)
            rows.append(f'<tr><td>{self.cite.hover(ph["title"])}<span class="ref">'
                        f'{esc(ph["id"])}</span></td><td>{chip(self.delivery_word(ph, tasks))}'
                        f'</td><td>{bar(done, len(tasks))}</td><td>{passed} of {len(checks)}'
                        ' passed</td></tr>')
        req = self.f.get("overall", {}).get("requirements", {})
        overall = ('<h3>Overall</h3><div class="scroll"><table class="prog"><thead><tr>'
                   '<th>Phase</th><th>State</th><th>Tasks done</th><th>Acceptance checks</th>'
                   f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
                   f'<p>Requirements done: {req.get("Implemented", 0)} of'
                   f' {sum(req.values())}.</p>')
        if self.first:
            body = words + overall
        else:
            body = ('<h3>In this window</h3>' + words
                    + self.filtered_tree({"done-window", "claimed-window"})
                    + P.block("Requirements done", self.f["did"]["requirements_done"], P.VISIBLE,
                              cite=cite) + overall)
        return ('<section class="card" id="did"><h2><span class="num">4</span>What we did</h2>'
                f'{body}</section>')

    def now_section(self) -> str:
        found = next(((ph["id"], s) for ph in self.f["plan"]["phases"] for s in ph["slices"]
                      if s["id"] == self.now), None)
        head = ('<section class="card" id="now"><h2><span class="num">5</span>What we are'
                ' working on now</h2>')
        if not found:
            return head + '<p class="empty">No slice is open.</p></section>'
        phase, s = found
        lines = s.get("lines", [])
        fresh = sum(1 for ln in lines if ln.get("tag"))
        fold = "".join(f'<li>{esc(ln["title"])}<span class="ref">{esc(ln["id"])}</span>'
                       + (' <span class="state s-done-window">this window</span>'
                          if ln.get("tag") else "") + "</li>" for ln in lines)
        others = [i for i, st in self.state.items() if st == "in-progress"
                  and self.slice_of.get(i) != self.now]
        return (head + P._text(self.n.get("slice"), self.cite.section())
                + f'<div class="tree">{self.slice_row(s, phase, 0, True)}</div>'
                + (f'<p class="muted">Also in progress elsewhere: {len(others)} items (filter'
                   ' "in progress" in the plan overview).</p>' if others else "")
                + (f'<details class="fold"><summary>Work done in this slice: '
                   f'{P.count(len(lines), "journal entry", "journal entries")}'
                   f'{f", {fresh} in this window" if fresh else ""}</summary>'
                   f'<ul class="list">{fold}</ul></details>' if lines else "")
                + "</section>")

    def next_section(self) -> str:
        cite, n = self.cite.section(), self.n
        plan = (('<p class="muted">The agent\'s plan, not a record:</p>'
                 + P._text(n.get("plan"), cite)) if n.get("plan") else "")
        return ('<section class="card" id="next"><h2><span class="num">6</span>What we expect'
                ' next</h2>' + P._text(n.get("next"), cite) + plan + self.filtered_tree({"next"})
                + P.block("Due in the next 7 days", self.f["next"]["due_soon"], P.VISIBLE,
                          cite=cite) + "</section>")

    def challenges(self) -> str:
        c, cite = self.f["challenges"], self.cite.section()
        b = (lambda label, data: P.block(label, data, P.VISIBLE, cite=cite))  # noqa: E731
        words = P._text(self.n.get("challenges"), cite)
        window = ('<h3>In this window</h3>' + words + b("Decisions made", c["decided"])
                  + b("Exceptions and scope changes", c["exceptions"])
                  + b("New defects", c["defects_new"]) + b("Defects closed", c["defects_closed"])
                  + b("New risks", c["risks_new"]) + b("Risks that moved", c["risks_moved"])
                  + b("Failed checks", c["checks_failed"]) + b("Escalations", c["escalations"]))
        overall_facts = self.f.get("overall", {})

        def line(label, counts):
            total = sum(counts.values())
            parts = ", ".join(f"{n} {esc(P.plain(s))}" for s, n in
                              sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
            return f"<li>{total} {label}: {parts}</li>" if total else ""
        fams = overall_facts.get("families", {})
        counts = ('<ul class="list">' + "".join(line(k.replace("_", " "), v)
                                                for k, v in fams.items()) + "</ul>")

        def full(label, rows):
            items = "".join(f'<li>{self.cite.hover(t)}<span class="ref">{esc(i)}</span>'
                            f'<span class="note">{esc(P.plain(s))}</span></li>'
                            for i, t, s in rows)
            return (f'<details class="fold"><summary>All {len(rows)} {label}</summary>'
                    f'<ul class="list">{items}</ul></details>' if rows else "")
        lists = "".join(full(k.replace("_", " "), v)
                        for k, v in overall_facts.get("lists", {}).items())
        overall = ('<h3>Overall</h3>' + (words if self.first else "")
                   + b("Open defects", c["defects_open"]) + b("Open high risks", c["risks_high"])
                   + b("Blocked work", c["blocked_work"])
                   + b("Release rules that do not pass yet", c["blocker_rules"]) + counts + lists)
        body = overall if self.first else window + overall
        return ('<section class="card" id="challenges"><h2><span class="num">7</span>Challenges'
                f' and decisions</h2>{body}</section>')

    def glossary(self, body: str) -> str:
        visible = re.sub(r"<[^>]+>", " ", body).lower()
        terms = {w: d for w, d in GLOSS.items() if w in visible}
        prefixes = {m.group(0) for i in list(self.state) + list(self.cite.names)
                    if (m := re.match(r"[A-Z]+", i))}
        table, kinds = FAM.by_prefix(), self.f.get("kinds", {})
        for p in sorted(prefixes):
            if p in table:
                _pre, one, _many, text = FAM.FAMILIES[table[p]]
                terms[f"{one} ({p}-)"] = text
            elif p in kinds:
                terms[f"{kinds[p]} ({p}-)"] = FAM.OTHER
        rows = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>"
                       for k, v in sorted(terms.items(), key=lambda kv: kv[0].lower()))
        return ('<section class="card" id="glossary"><h2><span class="num">8</span>Glossary</h2>'
                f'<dl class="gloss">{rows}</dl></section>')

    def record(self) -> str:
        d, x, m, cite = self.f["did"], self.f["next"], self.meta, self.cite.section()
        b = (lambda label, data: P.block(label, data, P.VISIBLE, cite=cite))  # noqa: E731
        made = (f"Journal rows PE-{m['pe_from']} to PE-{m['pe_to']}, check results"
                f" AV-{m['av_from']} to AV-{m['av_to']}. Starts after"
                f" {m.get('base') or 'the start of the package'}. State digest"
                f" {m['digest'][:16]}. The report sees new rows, status moves and content edits"
                " in the store. It never sees work that nobody recorded.")
        stand = P.stand(self.f)
        return ('<section class="card" id="record"><details class="fold"><summary>Record'
                ' details: the journal, commits, edits and the last session\'s notes</summary>'
                + b("From the journal", d["journal_done"]) + b("Commits", d["commits"])
                + b("Edited (status unchanged)", d["edited"])
                + b("Where the last session stopped", x["resume_at"])
                + (f'<p>New rows: {esc(", ".join(P.family(t, n) for t, n in d.get("added", {}).items()))}.</p>'
                   if d.get("added") else "")
                + stand + f'<h3>How this report was made</h3><p>{esc(made)}</p>'
                + "</details></section>")

    def body(self) -> str:
        body = (self.header() + self.summary() + self.needs() + self.overview() + self.did()
                + self.now_section() + self.next_section() + self.challenges())
        return body + self.glossary(body) + self.record()


def render(meta: dict, facts: dict, narrative: dict | None) -> str:
    source = script()
    css = P.CSS_PATH.read_text(encoding="utf-8")
    title = f"Standup report {meta['id']} — {meta['package']}"
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta http-equiv="Content-Security-Policy" content="{policy(source)}">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{esc(title)}</title>\n<style>\n{css}</style>\n</head>\n<body>\n<main>\n"
            f"{Page(meta, facts, narrative).body()}\n</main>\n<script>{source}</script>\n"
            "</body>\n</html>\n")
