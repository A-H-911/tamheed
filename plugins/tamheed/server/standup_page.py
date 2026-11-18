"""The standup page (plan 234): one self-contained HTML file per report, a pure function of its
row, with one escape point and links only to fragments of the page itself. This module holds the
shared helpers and the layout of the rows of 6.7.0 (no plan tree, no script). A row whose facts
hold the plan tree renders through `standup_view` (plan 251 v2, ADR-0005: one hash-pinned
script). Nothing shrinks any more: a list shows 8 items, then a fold.
"""
from __future__ import annotations

import html as _html
import re
from html.parser import HTMLParser
from pathlib import Path

import standup_families

CSS_PATH = Path(__file__).with_name("standup.css")
_CSP = "default-src 'none'; style-src 'unsafe-inline'"
TITLE_WORDS = 8                 # an inline title's words (plan 251)
VISIBLE = 8                     # a list shows 8 items, then a fold. Nothing shrinks (U8).
LIST_KEYS = ("did.edited", "did.commits", "did.journal_done", "next.due_soon",
                "challenges.blocked_work", "challenges.exceptions", "did.requirements_done",
                "did.slices_moved", "challenges.risks_moved", "challenges.risks_new",
                "challenges.defects_closed", "plan.items", "did.checks_passed",
                "did.tasks_claimed",
                "challenges.escalations", "challenges.checks_failed", "challenges.defects_new",
                "next.open_work", "challenges.decided", "did.tasks_done",
                "challenges.risks_high", "challenges.defects_open", "needs.confirm_rows",
                "needs.approve_scope", "needs.questions_overdue", "needs.approve_decisions")
COLOUR_WORDS = {"green": "On track", "amber": "At risk", "red": "Off track"}
STATUS_WORDS = {
    "Draft": "draft", "Proposed": "waiting for approval", "Approved": "approved",
    "Rejected": "rejected", "Superseded": "replaced", "Deferred": "postponed",
    "Implemented": "done", "Review": "claimed done", "Obsolete": "no longer used",
    "Open": "open", "In-progress": "being fixed", "Fixed": "fixed",
    "Won't-fix": "will not fix", "Duplicate": "duplicate", "open": "open",
    "mitigated": "reduced", "materialized": "happened", "retired": "closed",
    "accepted": "accepted", "Met": "passed", "Partial": "partly passed",
    "Not-met": "failed", "Pending": "not graded yet", "Go": "go", "Hold": "hold", "Redirect": "redirect", "Kill": "stop"}
FAMILY_WORDS = {table: (one, many) for table, (_p, one, many, _d)
                in standup_families.FAMILIES.items()}
# Plan 251 (D10): the family words (task, slice, phase, waiver ...) are defined once, in the fold
# "What the record holds" (standup_families). The glossary keeps the other terms.
GLOSSARY = (
    ("claimed done", "The agent says the work is done, and nobody confirmed it yet."),
    ("ready to close", "Every release rule of the package passes. Until then, the page names"
                       " the rules that fail."),
    ("journal", "The work log of the package."),
    ("checkpoint", "A report that keeps the full state, so later reports can be checked."),
    ("this report", "The window of time this report covers, from its start to its end."),
)
_ID_RE = re.compile(r"\[?\b([A-Z]{1,5}-\d+(?:\.\d+)*)\b\]?")


def esc(value) -> str:
    """THE single escape point of this page. None renders empty."""
    return "" if value is None else _html.escape(str(value), quote=True)


def plain(status) -> str:
    return STATUS_WORDS.get(str(status), str(status or "none"))


def family(table: str, n: int) -> str:
    one, many = FAMILY_WORDS.get(table, (table.replace("_", " "), table.replace("_", " ")))
    return f"{n} {one if n == 1 else many}"


def count(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


# ----------------------------------------------------------------------------- citing

def short(title) -> str:
    words = str(title or "").split()
    return " ".join(words[:TITLE_WORDS]) + (" …" if len(words) > TITLE_WORDS else "")


class Cite:
    """Plan 251 (R10, D9): a cited row prints its title before a small id, at its first
    mention in a section. The names come frozen from the row, so the page stays a pure
    function of it. Without names (a 6.7.0 row) the text prints as written."""

    def __init__(self, names: dict | None):
        self.names, self.seen = dict(names or {}), set()

    def section(self) -> "Cite":
        self.seen = set()
        return self

    def html(self, text) -> str:
        text, out, at = str(text or ""), [], 0
        for m in _ID_RE.finditer(text):
            rid = m.group(1)
            if rid not in self.names:
                continue
            out.append(esc(text[at:m.start()]))
            ref = f'<span class="ref">{esc(rid)}</span>'
            out.append(ref if rid in self.seen else f'“{self.hover(short(self.names[rid]))}” {ref}')
            self.seen.add(rid)
            at = m.end()
        return "".join(out) + esc(text[at:])

    def hover(self, text) -> str:
        """A row's own title, as written. Each id it holds that has a name shows that name on
        hover (the operator's choice of 2026-11-18): the text keeps its length."""
        text, out, at = str(text or ""), [], 0
        for m in _ID_RE.finditer(text):
            rid = m.group(1)
            if rid not in self.names:
                continue
            out.append(esc(text[at:m.start(1)]))
            out.append(f'<abbr title="{esc(self.names[rid])}">{esc(rid)}</abbr>')
            at = m.end(1)
        return "".join(out) + esc(text[at:])

    def words(self, text) -> int:
        """The words `html` shows for one text, with each title counted once."""
        seen, n = set(), len(str(text or "").split())
        for m in _ID_RE.finditer(str(text or "")):
            if m.group(1) in self.names and m.group(1) not in seen:
                seen.add(m.group(1))
                n += len(short(self.names[m.group(1)]).split())
        return n


_PLAIN = Cite(None)


# ----------------------------------------------------------------------------- lists

def _item(it: dict, cite: Cite = _PLAIN) -> str:
    title = it.get("title") or "(untitled)"
    free = not it.get("id") or str(it["id"]).startswith("PE-")   # a journal line is free text
    parts = [f'<span class="t">{cite.html(title) if free else cite.hover(title)}</span>']
    if it.get("id"):
        parts.append(f'<span class="ref">{esc(it["id"])}</span>')
    move = it.get("move")
    if move:
        was = "new" if move[0] is None else plain(move[0])
        parts.append(f'<span class="mv">{esc(was)} → {esc(plain(move[1]))}</span>')
    if it.get("note"):
        parts.append(f'<span class="note">{cite.html(plain(it["note"]))}</span>')
    return "<li>" + " ".join(parts) + "</li>"


def block(label: str, data: dict, cap: int, empty: str | None = None,
          cite: Cite = _PLAIN) -> str:
    """A labelled list: `cap` items visible, the rest in a closed fold."""
    items, total = data.get("items", []), data.get("total", 0)
    if not total:
        return f'<p class="none">{esc(empty)}</p>' if empty else ""
    head = f"<h4>{esc(label)} <span class=\"count\">{esc(total)}</span></h4>"
    shown = "".join(_item(it, cite) for it in items[:cap])
    rest = items[cap:]
    out = head + (f"<ul>{shown}</ul>" if shown else "")
    if rest:
        out += (f"<details><summary>{esc(len(rest))} more</summary><ul>"
                + "".join(_item(it, cite) for it in rest) + "</ul></details>")
    if total > len(items):
        out += (f'<p class="more">And {esc(total - len(items))} more in the record:'
                " see review.html.</p>")
    return out


def _text(value, cite: Cite = _PLAIN) -> str:
    paras = [p.strip() for p in re.split(r"\n\s*\n", str(value or "")) if p.strip()]
    return "".join(f"<p>{cite.html(' '.join(p.split()))}</p>" for p in paras)


# ----------------------------------------------------------------------------- sections

THEME = ('<div class="theme" role="radiogroup" aria-label="Colours">'
         '<label><input type="radio" name="theme" id="theme-auto" checked> Auto</label>'
         '<label><input type="radio" name="theme" id="theme-light"> Light</label>'
         '<label><input type="radio" name="theme" id="theme-dark"> Dark</label></div>')


def header(meta: dict, narrative: dict | None) -> str:
    rows = [THEME + f'<h1>Standup report {esc(meta["id"])}<span class="pkg">'
            f' · {esc(meta["package"])}</span></h1>']
    if meta.get("draft"):
        rows.append('<p class="banner">Draft: not recorded yet.</p>')
    else:
        rows.append(f'<p class="recorded">Recorded by {esc(meta.get("recorded_by"))} on'
                    f' {esc(meta.get("recorded_on"))}.</p>')
    rows.append(f'<p class="window">From {esc(meta["start_text"])} to'
                f' {esc(meta["end_text"])}.</p>')
    for note in meta.get("notes", []):
        rows.append(f'<p class="note-line">{esc(note)}</p>')
    rows.append(colour_line(meta, narrative))
    return '<header>' + "".join(rows) + "</header>"


def colour_line(meta: dict, narrative: dict | None) -> str:
    rule = meta.get("rule_colour") or "green"
    chosen = meta.get("colour") or (narrative or {}).get("colour") or rule
    reason = (narrative or {}).get("colour_reason") or ""
    word = "Proposed overall" if meta.get("draft") else "Overall"
    out = (f'<p class="colour {esc(_safe_colour(chosen))}"><strong>{word}:'
           f' {esc(COLOUR_WORDS[_safe_colour(chosen)])}.</strong> {esc(reason)}</p>')
    if _safe_colour(chosen) != _safe_colour(rule):
        why = ", ".join(meta.get("rule_reasons", []))
        out += (f'<p class="rule">The default rule says:'
                f' {esc(COLOUR_WORDS[_safe_colour(rule)].lower())}'
                f'{(" (" + esc(why) + ")") if why else ""}.</p>')
    return out


def _safe_colour(value) -> str:
    return value if isinstance(value, str) and value in COLOUR_WORDS else "green"


def glance(g: dict) -> str:
    bits = [count(g.get("tasks_done", 0), "task done", "tasks done"),
            count(g.get("checks_passed", 0), "check passed", "checks passed"),
            count(g.get("defects_open", 0), "defect open", "defects open"),
            count(g.get("needs_you", 0), "item needs you", "items need you")]
    out = '<p class="glance">' + " · ".join(esc(b) for b in bits) + "</p>"
    ph = g.get("phase")
    if ph:
        out += (f'<p class="glance">Phase {esc(ph["phase"])} ({esc(ph["title"])}):'
                f' {esc(ph["done"])} of {esc(ph["total"])} tasks done'
                f' ({esc(ph["claimed"])} claimed done).</p>')
    return out


def needs(f: dict, caps: dict) -> str:
    cite = _cite(f).section()
    b = (lambda *a, **k: block(*a, cite=cite, **k))
    n = f["needs"]
    body = (b("Decisions waiting for approval", n["approve_decisions"],
                  caps["needs.approve_decisions"])
            + b("Scope changes waiting for approval", n["approve_scope"],
                    caps["needs.approve_scope"])
            + b("Lessons and feedback to confirm", n["confirm_rows"],
                    caps["needs.confirm_rows"])
            + b("Open questions past their date", n["questions_overdue"],
                    caps["needs.questions_overdue"])
            + b("From the latest handoff", n["awaiting_operator"], VISIBLE))
    return ('<section id="needs" class="needs"><h2>Needs from you</h2>'
            + (body or '<p class="none">Nothing waits for you.</p>') + "</section>")


def stand(f: dict) -> str:
    rows = "".join(
        f"<tr><td>{esc(FAMILY_WORDS.get(table, (table.replace('_', ' '),) * 2)[1])}</td><td>"
        + esc(", ".join(f"{plain(s)} {n}" for s, n in sorted(counts.items()))) + "</td></tr>"
        for table, counts in sorted(f.get("where_we_stand", {}).items()))
    return ("<section id=\"stand\"><h2>Where we stand</h2><details><summary>Rows per family"
            "</summary><table>" + rows + "</table></details></section>") if rows else ""


def did(f: dict, narrative: dict | None, caps: dict) -> str:
    d, cite, old = f["did"], _cite(f, narrative).section(), "plan" not in f
    b = (lambda *a, **k: block(*a, cite=cite, **k))
    added = ", ".join(family(t, n) for t, n in d.get("added", {}).items())
    return ('<section id="did"><h2>1. What we did</h2>'
            + _text((narrative or {}).get("did"), cite)
            + (b("Tasks done", d["tasks_done"], caps["did.tasks_done"])
               + b("Tasks claimed done", d["tasks_claimed"], caps["did.tasks_claimed"])
               + b("Slices and phases moved", d["slices_moved"], caps["did.slices_moved"])
               + b("Acceptance checks passed", d["checks_passed"],
                       caps["did.checks_passed"]) if old else "")
            + b("Requirements done", d["requirements_done"],
                    caps["did.requirements_done"])
            + b("From the journal", d["journal_done"], caps["did.journal_done"])
            + b("Edited (status unchanged)", d["edited"], caps["did.edited"])
            + b("Commits", d["commits"], caps["did.commits"])
            + (f'<p class="added">New rows: {esc(added)}.</p>' if added else "")
            + "</section>")


def challenges(f: dict, narrative: dict | None, caps: dict) -> str:
    cite = _cite(f, narrative).section()
    b = (lambda *a, **k: block(*a, cite=cite, **k))
    c, pending = f["challenges"], f["needs"]["approve_decisions"]["total"]
    return ('<section id="challenges"><h2>2. Challenges and decisions</h2>'
            + _text((narrative or {}).get("challenges"), cite)
            + b("Decisions made", c["decided"], caps["challenges.decided"])
            + (f'<p class="pending">{esc(pending)} {"decision waits" if pending == 1 else "decisions wait"}'
               " for approval: see Needs from you.</p>" if pending else "")
            + b("Exceptions and scope changes", c["exceptions"],
                    caps["challenges.exceptions"])
            + b("Open defects", c["defects_open"], caps["challenges.defects_open"])
            + b("New defects", c["defects_new"], caps["challenges.defects_new"])
            + b("Defects closed", c["defects_closed"], caps["challenges.defects_closed"])
            + b("High risks", c["risks_high"], caps["challenges.risks_high"])
            + b("New risks", c["risks_new"], caps["challenges.risks_new"])
            + b("Risks that moved", c["risks_moved"], caps["challenges.risks_moved"])
            + b("Failed checks", c["checks_failed"], caps["challenges.checks_failed"])
            + b("Escalations", c["escalations"], caps["challenges.escalations"])
            + b("Not ready to close yet", c["blocker_rules"], VISIBLE)
            + b("Blocked work", c["blocked_work"], caps["challenges.blocked_work"])
            + "</section>")


def upcoming(f: dict, narrative: dict | None, caps: dict) -> str:
    cite = _cite(f, narrative).section()
    b = (lambda *a, **k: block(*a, cite=cite, **k))
    x, n = f["next"], narrative or {}
    plan = n.get("plan") or n.get("next")
    return ('<section id="next"><h2>3. What we expect to do next</h2>'
            + _text(n.get("next") if n.get("plan") else "", cite)
            + (('<div class="plan"><p class="label">The agent\'s plan. A plan, not a record.'
                "</p>" + _text(plan, cite) + "</div>") if plan else "")
            + (b("Open work", x["open_work"], caps["next.open_work"])
               if "plan" not in f else "")
            + b("Due in the next 7 days", x["due_soon"], caps["next.due_soon"])
            + b("Where the last session stopped", x["resume_at"], VISIBLE)
            + "</section>")


# ----------------------------------------------------------------------------- the plan tree

def _cite(f: dict, narrative: dict | None = None) -> Cite:
    """The frozen names: the draft's (handoff lines, notes) and the words' (attach)."""
    return Cite({**f.get("names", {}), **(narrative or {}).get("_names", {})})


def _frozen_ids(f: dict, narrative: dict | None) -> set[str]:
    """Every id the row holds for this page: the lists, the tree, and the cited names."""
    ids = set(f.get("names", {})) | set((narrative or {}).get("_names", {}))

    def walk(value):
        if isinstance(value, dict):
            if isinstance(value.get("id"), str):
                ids.add(value["id"])
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for v in value:
                walk(v)
    walk({k: v for k, v in f.items() if k not in ("view", "names", "kinds")})
    return ids


def families(f: dict, narrative: dict | None) -> str:
    """Plan 251 (R11, D10): the families that this page shows or cites, in plain words. They
    come from the ids the row holds, so a date offset or a hash in a title is never a kind."""
    seen = {i.rsplit("-", 1)[0] if "-" in i else i for i in _frozen_ids(f, narrative)}
    seen = {re.match(r"[A-Z]+", s).group(0) for s in seen if re.match(r"[A-Z]+", s)}
    table_of, kinds = standup_families.by_prefix(), f.get("kinds", {})
    seen = {s for s in seen if s in table_of or s in kinds}
    tables = [t for t in standup_families.FAMILIES if t in {table_of.get(x) for x in seen}]
    other = sorted(x for x in seen if x not in table_of)
    if not tables and not other:
        return ""
    rows = "".join(f"<dt>{esc(spec[1].capitalize())} <span class=\"ref\">{esc(spec[0])}</span>"
                   f"</dt><dd>{esc(spec[3])}</dd>"
                   for spec in (standup_families.FAMILIES[t] for t in tables))
    rows += "".join(f"<dt>{esc(kinds[x])} <span class=\"ref\">{esc(x)}-</span></dt>"
                    f"<dd>{esc(standup_families.OTHER)}</dd>" for x in other)
    return ('<section id="families"><h2>What the record holds</h2><details><summary>'
            f"{esc(count(len(tables) + len(other), 'kind of row', 'kinds of row'))}"
            " on this page</summary><dl>" + rows + "</dl></details></section>")


def glossary(visible_text: str) -> str:
    low = visible_text.lower()
    used = [(w, d) for w, d in GLOSSARY if re.search(rf"\b{re.escape(w)}", low)]
    if not used:
        return ""
    return ('<section id="terms"><h2>Terms used</h2><dl>'
            + "".join(f"<dt>{esc(w)}</dt><dd>{esc(d)}</dd>" for w, d in used)
            + "</dl></section>")


def footer(meta: dict) -> str:
    lines = [f"Journal rows PE-{meta['pe_from']} to PE-{meta['pe_to']}, check results"
             f" AV-{meta['av_from']} to AV-{meta['av_to']}.",
             f"Starts after {meta.get('base') or 'the start of the package'}.",
             f"State digest {meta['digest'][:16]}.",
             "The report sees new rows, status moves and content edits in the store. It never"
             " sees work that nobody recorded."]
    return ('<footer><details><summary>How this report was made</summary>'
            + "".join(f"<p>{esc(x)}</p>" for x in lines) + "</details></footer>")


# ----------------------------------------------------------------------------- the page

def render(meta: dict, facts: dict, narrative: dict | None, caps: dict | None = None) -> str:
    """A row whose facts hold the plan tree is the delivery report of plan 251 v2
    (`standup_view`). A row of 6.7.0 keeps this layout."""
    if "plan" in facts:
        import standup_view  # noqa: PLC0415 - it imports this module
        return standup_view.render(meta, facts, narrative)
    caps = caps or {k: VISIBLE for k in LIST_KEYS}
    n = narrative or {}
    body = (header(meta, narrative) + glance(facts.get("glance", {}))
            + (f'<div class="headline">{_text(n.get("headline"), _cite(facts, n))}</div>'
               if n.get("headline") else "")
            + needs(facts, caps) + stand(facts) + did(facts, narrative, caps)
            + challenges(facts, narrative, caps) + upcoming(facts, narrative, caps))
    body += families(facts, narrative) + glossary(visible_text(body)) + footer(meta)
    css = CSS_PATH.read_text(encoding="utf-8")
    title = f"Standup report {meta['id']} — {meta['package']}"
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta http-equiv="Content-Security-Policy" content="{_CSP}">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{esc(title)}</title>\n<style>\n{css}</style>\n</head>\n<body>\n<main>\n"
            f"{body}\n</main>\n</body>\n</html>\n")


def narrative_words(narrative: dict | None, facts: dict | None = None) -> int:
    """The agent's words on the page, with the titles they cite (plan 251, D9): those words
    are the agent's, so they never shrink a list."""
    n = narrative or {}
    cite = _cite(facts or {}, n)
    return sum(cite.words(n.get(k)) for k in
               ("headline", "did", "challenges", "next", "plan", "slice", "colour_reason"))


def fit(meta: dict, facts: dict, narrative: dict | None, *, exempt: bool = False
        ) -> tuple[str, int]:
    """(page, visible words). Plan 251 v2 (U8): nothing shrinks. Long lists show 8 items,
    then a fold. `exempt` is kept for the callers of 6.7.0 and changes nothing."""
    page = render(meta, facts, narrative)
    return page, visible_words(page)


# ----------------------------------------------------------------------------- the counter

class _Visible(HTMLParser):
    """Text a reader sees at rest: no head, style or title, and of a closed <details> only
    its <summary>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0           # inside head/style/title
        self.folds: list[bool] = []   # per open <details>: True when closed
        self.summary = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("head", "style", "title", "script"):
            self.hidden += 1
        elif tag == "details":
            self.folds.append("open" not in dict(attrs))
        elif tag == "summary":
            self.summary += 1

    def handle_endtag(self, tag):
        if tag in ("head", "style", "title", "script"):
            self.hidden = max(0, self.hidden - 1)
        elif tag == "details" and self.folds:
            self.folds.pop()
        elif tag == "summary":
            self.summary = max(0, self.summary - 1)

    def handle_data(self, data):
        if self.hidden:
            return
        closed = any(self.folds)
        if closed and not (self.summary and self.folds and not any(self.folds[:-1])):
            return
        self.parts.append(data)


def visible_text(page: str) -> str:
    v = _Visible()
    v.feed(page)
    return " ".join(v.parts)


def visible_words(page: str) -> int:
    return len(visible_text(page).split())


# ----------------------------------------------------------------------------- the meta

def meta(row: dict, *, package: str, base: dict | None, birth: str | None,
         window: dict, snapped: str | None = None, broken: str | None = None,
         rule_reasons: tuple | list = (), notes: tuple | list = ()) -> dict:
    """What the header and the footer print, from the row and its window. `birth` is the
    package's start date when one is known (a real `YYYY-MM-DD`), else None."""
    import standup as S
    offset = row["utc_offset"]
    if base:
        start = S.shown(base["ended_at"], offset)
    else:
        start = f"the start of the package ({birth})" if birth else "the start of the package"
    lines = []
    if row.get("kind") == "override":
        lines.append("An override report: it does not start the next window.")
    if snapped:
        lines.append(f"Started from {base['id'] if base else 'the start of the package'},"
                     f" the last daily report on or before {snapped}.")
    if row.get("supersedes"):
        lines.append(f"This report corrects {row['supersedes']}.")
    if broken:
        lines.append(f"The stored reports stopped matching at {broken}. Changes across that"
                     " point are unknown, so this report keeps the full state.")
    lines.extend(notes)
    recorded_on = S.shown(row["recorded_at"], offset) if row.get("recorded_at") else None
    return {"id": row["id"], "package": package, "kind": row.get("kind"),
            "draft": row.get("lifecycle_status", "Draft") == "Draft",
            "recorded_by": row.get("recorded_by"), "recorded_on": recorded_on,
            "start_text": start, "end_text": S.shown(row["ended_at"], offset),
            "notes": lines, "rule_colour": row.get("rule_colour"),
            "rule_reasons": list(rule_reasons), "colour": row.get("colour"),
            "pe_from": window["pe_from"], "pe_to": window["pe_to"],
            "av_from": window["av_from"], "av_to": window["av_to"],
            "base": (base or {}).get("id"), "digest": row["state_digest"]}
