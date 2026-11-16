"""The standup page (plan 234): one self-contained HTML file per report, a pure function of its
row. The frame of review.html: one escape point, the same content policy, no script, and links
only to fragments of the page itself. The engine's part stays at or under 1,400 visible words
(SR15). The first report is exempt (SR12) and lists every item in closed folds (SR39).
"""
from __future__ import annotations

import html as _html
import re
from html.parser import HTMLParser
from pathlib import Path

CSS_PATH = Path(__file__).with_name("standup.css")
_CSP = "default-src 'none'; style-src 'unsafe-inline'"
ENGINE_BUDGET = 1400
VISIBLE = 8
SHRINK = (5, 3, 1, 0)
# Least important first; "Needs from you" shrinks last.
SHRINK_ORDER = ("did.edited", "did.commits", "did.journal_done", "next.due_soon",
                "challenges.blocked_work", "challenges.exceptions", "did.requirements_done",
                "did.slices_moved", "challenges.risks_moved", "challenges.risks_new",
                "challenges.defects_closed", "did.checks_passed", "did.tasks_claimed",
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
    "Not-met": "failed", "Go": "go", "Hold": "hold", "Redirect": "redirect", "Kill": "stop"}
FAMILY_WORDS = {
    "wbs_items": ("task", "tasks"), "slices": ("slice", "slices"),
    "phases": ("phase", "phases"), "milestones": ("milestone", "milestones"),
    "requirements": ("requirement", "requirements"),
    "acceptance_criteria": ("acceptance check", "acceptance checks"),
    "decisions": ("decision", "decisions"), "adrs": ("architecture decision",
                                                     "architecture decisions"),
    "risks": ("risk", "risks"), "defects": ("defect", "defects"),
    "open_questions": ("open question", "open questions"),
    "scope_changes": ("scope change", "scope changes"), "waivers": ("waiver", "waivers"),
    "deferred_work": ("postponed item", "postponed items"), "lessons": ("lesson", "lessons"),
    "feedback": ("feedback row", "feedback rows"), "tests": ("test", "tests")}
GLOSSARY = (
    ("task", "One piece of planned work."),
    ("slice", "A small part of the product that ships on its own."),
    ("phase", "A stage of the plan."),
    ("acceptance check", "A test of one requirement that a person or a machine runs."),
    ("check result", "The result of one acceptance check: passed, partly passed or failed."),
    ("claimed done", "The agent says the work is done, and no check confirmed it yet."),
    ("architecture decision", "A recorded choice about the structure of the system."),
    ("waiver", "The operator's permission to pass one readiness rule."),
    ("scope change", "An approved change to the plan."),
    ("blocker rule", "A readiness rule that must pass before the work counts as done."),
    ("journal", "The work log of the package."),
    ("checkpoint", "A report that keeps the full state, so later reports can be checked."),
)


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


# ----------------------------------------------------------------------------- lists

def _item(it: dict) -> str:
    parts = [f'<span class="t">{esc(it.get("title") or "(untitled)")}</span>']
    if it.get("id"):
        parts.append(f'<span class="ref">{esc(it["id"])}</span>')
    move = it.get("move")
    if move:
        was = "new" if move[0] is None else plain(move[0])
        parts.append(f'<span class="mv">{esc(was)} → {esc(plain(move[1]))}</span>')
    if it.get("note"):
        parts.append(f'<span class="note">{esc(plain(it["note"]))}</span>')
    return "<li>" + " ".join(parts) + "</li>"


def block(label: str, data: dict, cap: int, empty: str | None = None) -> str:
    """A labelled list: `cap` items visible, the rest in a closed fold."""
    items, total = data.get("items", []), data.get("total", 0)
    if not total:
        return f'<p class="none">{esc(empty)}</p>' if empty else ""
    head = f"<h4>{esc(label)} <span class=\"count\">{esc(total)}</span></h4>"
    shown = "".join(_item(it) for it in items[:cap])
    rest = items[cap:]
    out = head + (f"<ul>{shown}</ul>" if shown else "")
    if rest:
        out += (f"<details><summary>{esc(len(rest))} more</summary><ul>"
                + "".join(_item(it) for it in rest) + "</ul></details>")
    if total > len(items):
        out += (f'<p class="more">And {esc(total - len(items))} more in the record:'
                " see review.html.</p>")
    return out


def _text(value) -> str:
    paras = [p.strip() for p in re.split(r"\n\s*\n", str(value or "")) if p.strip()]
    return "".join(f"<p>{esc(' '.join(p.split()))}</p>" for p in paras)


# ----------------------------------------------------------------------------- sections

def header(meta: dict, narrative: dict | None) -> str:
    rows = [f'<h1>Standup report {esc(meta["id"])}<span class="pkg">'
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
    n = f["needs"]
    body = (block("Decisions waiting for approval", n["approve_decisions"],
                  caps["needs.approve_decisions"])
            + block("Scope changes waiting for approval", n["approve_scope"],
                    caps["needs.approve_scope"])
            + block("Lessons and feedback to confirm", n["confirm_rows"],
                    caps["needs.confirm_rows"])
            + block("Open questions past their date", n["questions_overdue"],
                    caps["needs.questions_overdue"])
            + block("From the latest handoff", n["awaiting_operator"], VISIBLE))
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
    d = f["did"]
    added = ", ".join(family(t, n) for t, n in d.get("added", {}).items())
    return ('<section id="did"><h2>1. What we did</h2>' + _text((narrative or {}).get("did"))
            + block("Tasks done", d["tasks_done"], caps["did.tasks_done"])
            + block("Tasks claimed done", d["tasks_claimed"], caps["did.tasks_claimed"])
            + block("Slices and phases moved", d["slices_moved"], caps["did.slices_moved"])
            + block("Acceptance checks passed", d["checks_passed"], caps["did.checks_passed"])
            + block("Requirements done", d["requirements_done"],
                    caps["did.requirements_done"])
            + block("From the journal", d["journal_done"], caps["did.journal_done"])
            + block("Edited (status unchanged)", d["edited"], caps["did.edited"])
            + block("Commits", d["commits"], caps["did.commits"])
            + (f'<p class="added">New rows: {esc(added)}.</p>' if added else "")
            + "</section>")


def challenges(f: dict, narrative: dict | None, caps: dict) -> str:
    c, pending = f["challenges"], f["needs"]["approve_decisions"]["total"]
    return ('<section id="challenges"><h2>2. Challenges and decisions</h2>'
            + _text((narrative or {}).get("challenges"))
            + block("Decisions made", c["decided"], caps["challenges.decided"])
            + (f'<p class="pending">{esc(pending)} {"decision waits" if pending == 1 else "decisions wait"}'
               " for approval: see Needs from you.</p>" if pending else "")
            + block("Exceptions and scope changes", c["exceptions"],
                    caps["challenges.exceptions"])
            + block("Open defects", c["defects_open"], caps["challenges.defects_open"])
            + block("New defects", c["defects_new"], caps["challenges.defects_new"])
            + block("Defects closed", c["defects_closed"], caps["challenges.defects_closed"])
            + block("High risks", c["risks_high"], caps["challenges.risks_high"])
            + block("New risks", c["risks_new"], caps["challenges.risks_new"])
            + block("Risks that moved", c["risks_moved"], caps["challenges.risks_moved"])
            + block("Failed checks", c["checks_failed"], caps["challenges.checks_failed"])
            + block("Escalations", c["escalations"], caps["challenges.escalations"])
            + block("Blocker rules that fail", c["blocker_rules"], VISIBLE)
            + block("Blocked work", c["blocked_work"], caps["challenges.blocked_work"])
            + "</section>")


def upcoming(f: dict, narrative: dict | None, caps: dict) -> str:
    x, n = f["next"], narrative or {}
    plan = n.get("plan") or n.get("next")
    return ('<section id="next"><h2>3. What we expect to do next</h2>'
            + _text(n.get("next") if n.get("plan") else "")
            + (('<div class="plan"><p class="label">The agent\'s plan. A plan, not a record.'
                "</p>" + _text(plan) + "</div>") if plan else "")
            + block("Open work", x["open_work"], caps["next.open_work"])
            + block("Due in the next 7 days", x["due_soon"], caps["next.due_soon"])
            + block("Where the last session stopped", x["resume_at"], VISIBLE)
            + "</section>")


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

def render(meta: dict, facts: dict, narrative: dict | None, caps: dict) -> str:
    n = narrative or {}
    body = (header(meta, narrative) + glance(facts.get("glance", {}))
            + (f'<div class="headline">{_text(n.get("headline"))}</div>'
               if n.get("headline") else "")
            + needs(facts, caps) + stand(facts) + did(facts, narrative, caps)
            + challenges(facts, narrative, caps) + upcoming(facts, narrative, caps))
    body += glossary(visible_text(body)) + footer(meta)
    css = CSS_PATH.read_text(encoding="utf-8")
    title = f"Standup report {meta['id']} — {meta['package']}"
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta http-equiv="Content-Security-Policy" content="{_CSP}">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{esc(title)}</title>\n<style>\n{css}</style>\n</head>\n<body>\n<main>\n"
            f"{body}\n</main>\n</body>\n</html>\n")


def narrative_words(narrative: dict | None) -> int:
    n = narrative or {}
    return sum(len(str(n.get(k) or "").split()) for k in
               ("headline", "did", "challenges", "next", "plan", "colour_reason"))


def fit(meta: dict, facts: dict, narrative: dict | None, *, exempt: bool) -> tuple[str, int]:
    """(page, visible words). The engine's part shrinks to ENGINE_BUDGET, least important
    list first. The narrative never shrinks: an over-share narrative only warns (SR38)."""
    caps = {k: VISIBLE for k in SHRINK_ORDER}
    page = render(meta, facts, narrative, caps)
    if exempt:
        return page, visible_words(page)
    own = narrative_words(narrative)
    for level in SHRINK:
        for key in SHRINK_ORDER:
            if visible_words(page) - own <= ENGINE_BUDGET:
                return page, visible_words(page)
            caps[key] = min(caps[key], level)
            page = render(meta, facts, narrative, caps)
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
