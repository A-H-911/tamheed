"""The standup facts (plan 233): what each section of the page lists, frozen at the draft.

Every list is {"items": [{"id", "title", "move"?, "note"?}], "total": n}. Items are ordered by
the id's prefix and number. A list keeps at most `cap` items (SR41); the first report is
uncapped (SR39). Text taken from the journal or a handoff passes the caller's `screen` first.
"""
from __future__ import annotations

import datetime as _dt
import json
import re

import standup as S

S_DECIDED = ("Approved", "Rejected", "Superseded")
_SEVERITY = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _key(i) -> tuple:
    m = re.match(r"^([A-Za-z]+)-(\d+)", str(i or ""))
    return (m.group(1), int(m.group(2)), str(i)) if m else ("~", 0, str(i))


def as_list(items: list[dict], cap: int | None) -> dict:
    ordered = sorted(items, key=lambda it: _key(it.get("id")))
    return {"items": ordered if cap is None else ordered[:cap], "total": len(ordered)}


def titles(conn, table: str, ids) -> dict:
    ids = sorted(set(ids))
    if not ids:
        return {}
    names = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
    col = next((c for c in ("title", "statement", "description", "question", "definition",
                            "rule") if c in names), "id")
    out = {}
    for k in range(0, len(ids), 500):
        part = ids[k:k + 500]
        for i, t in conn.execute(f"SELECT id, {col} FROM {table} WHERE id IN"
                                 f" ({', '.join('?' * len(part))})", part):
            out[str(i)] = " ".join(str(t or "").split())[:S.TITLE_CAP]
    return out


def _items(conn, table: str, rows: list[tuple]) -> list[dict]:
    """rows: (id, from_status, to_status) -> items with titles and the move."""
    names = titles(conn, table, [r[0] for r in rows])
    return [{"id": i, "title": names.get(i, ""), "move": [a or None, b]} for i, a, b in rows]


def moved_to(cls: dict, table: str, statuses, *, part: int = 0) -> list[tuple]:
    """Rows of `table` whose status moved INTO `statuses`. A new row moves from none."""
    def pick(status: str) -> str:
        return status.split("|")[part] if "|" in status else status
    out = [(i, a, b) for t, i, a, b in cls["moved"]
           if t == table and pick(b) in statuses and pick(a) not in statuses]
    out += [(i, None, s) for t, i, s in cls["new"] if t == table and pick(s) in statuses]
    return out


def _rows(conn, sql: str, params=()) -> list[dict]:
    cur = conn.execute(sql, params)
    keys = [d[0] for d in cur.description]
    return [dict(zip(keys, r)) for r in cur.fetchall()]


def _text_items(lines, screen, prefix: str) -> list[dict]:
    return [{"id": None, "title": (f"withheld: read the latest {prefix}" if screen(x) else x)}
            for x in lines[:10]]


# ----------------------------------------------------------------------------- sections

def needs(conn, handoff: dict, today: str, screen, cap) -> dict:
    dec = _rows(conn, "SELECT id, title FROM decisions WHERE lifecycle_status = 'Proposed'")
    dec += _rows(conn, "SELECT id, title FROM adrs WHERE lifecycle_status IN"
                       " ('Draft', 'Proposed')")
    scope = _rows(conn, "SELECT id, description AS title FROM scope_changes"
                        " WHERE lifecycle_status = 'Proposed'")
    confirm = _rows(conn, "SELECT id, title FROM lessons WHERE lifecycle_status = 'Proposed'")
    confirm += _rows(conn, "SELECT id, title FROM feedback WHERE lifecycle_status = 'Proposed'")
    overdue = _rows(conn, "SELECT id, title, due_by AS note FROM open_questions WHERE"
                          " resolved_by IS NULL AND resolution IS NULL AND due_by IS NOT NULL"
                          " AND due_by < ?", (today,))
    for row in dec + scope + confirm + overdue:
        row["title"] = " ".join(str(row["title"] or "").split())[:S.TITLE_CAP]
    return {"approve_decisions": as_list(dec, cap), "approve_scope": as_list(scope, cap),
            "confirm_rows": as_list(confirm, cap), "questions_overdue": as_list(overdue, cap),
            "awaiting_operator": as_list(_text_items(handoff.get("awaiting the operator", []),
                                                     screen, "handoff"), None)}


def did(conn, cls: dict, entries: list[dict], verdicts: list[dict], screen, cap) -> dict:
    ac = titles(conn, "acceptance_criteria", [v["ac_id"] for v in verdicts])
    journal, commits = [], []
    for e in entries:
        if e["event_type"] == "work-done":
            text = S.first_sentence(e["entry"])
            journal.append({"id": e["id"], "title": f"withheld: read {e['id']}"
                            if screen(text) else text})
        if e["actor"] == "system:work-bind":
            attrs = _json(e["custom_attributes"])
            binds = attrs.get("binds")
            binds = [str(b) for b in binds] if isinstance(binds, list) else []
            commits.append({"id": e["id"], "title": str(attrs.get("ref", ""))[:12],
                            "note": ", ".join(binds)})
    edited = [{"id": i, "title": titles(conn, t, [i]).get(i, ""), "note": t}
              for t, i in cls["edited"]]
    added: dict[str, int] = {}
    for t, *_rest in cls["new"]:
        added[t] = added.get(t, 0) + 1
    slices = (_items(conn, "slices", moved_to(cls, "slices", ("Review", "Implemented")))
              + _items(conn, "phases", moved_to(cls, "phases", ("Review", "Implemented"))))
    return {
        "tasks_done": as_list(_items(conn, "wbs_items",
                                     moved_to(cls, "wbs_items", ("Implemented",))), cap),
        "tasks_claimed": as_list(_items(conn, "wbs_items",
                                        moved_to(cls, "wbs_items", ("Review",))), cap),
        "slices_moved": as_list(slices, cap),
        "checks_passed": as_list([{"id": v["ac_id"], "title": ac.get(v["ac_id"], ""),
                                   "note": v["id"]} for v in verdicts
                                  if v["verdict"] == "Met"], cap),
        "requirements_done": as_list(_items(conn, "requirements", moved_to(
            cls, "requirements", ("Implemented",))), cap),
        "journal_done": as_list(journal, cap),
        "commits": as_list(commits, cap),
        "edited": as_list(edited, cap),
        "added": dict(sorted(added.items())),
    }


def challenges(conn, cls: dict, entries: list[dict], verdicts: list[dict],
               blocker_rules: list[str], screen, cap) -> dict:
    decided = (_items(conn, "decisions", moved_to(cls, "decisions", S_DECIDED))
               + _items(conn, "adrs", moved_to(cls, "adrs", S_DECIDED))
               + _items(conn, "execution_gates", moved_to(
                   cls, "execution_gates", ("Go", "Hold", "Redirect", "Kill"))))
    decided += _entry_items(entries, ("gate-decision",), screen)
    exceptions = (_items(conn, "waivers", [(i, None, s) for t, i, s in cls["new"]
                                           if t == "waivers"])
                  + _items(conn, "scope_changes", [(i, a, b) for t, i, a, b in cls["moved"]
                                                   if t == "scope_changes"]))
    ac = titles(conn, "acceptance_criteria", [v["ac_id"] for v in verdicts])
    failed = [{"id": v["ac_id"], "title": ac.get(v["ac_id"], ""), "note": v["verdict"]}
              for v in verdicts if v["verdict"] in ("Not-met", "Partial")]
    return {
        "decided": as_list(decided, cap),
        "exceptions": as_list(exceptions, cap),
        **defects(conn, cls, cap),
        **risks(conn, cls, cap),
        "checks_failed": as_list(failed, cap),
        "escalations": as_list(_entry_items(entries, ("escalation", "forced-override"),
                                            screen), cap),
        "blocker_rules": as_list([{"id": None, "title": r} for r in blocker_rules], None),
        "blocked_work": as_list(blocked(conn), cap),
    }


def defects(conn, cls: dict, cap) -> dict:
    new = [(i, None, s) for t, i, s in cls["new"] if t == "defects"]
    closed = moved_to(cls, "defects", ("Fixed", "Won't-fix", "Duplicate"))
    sev = dict(conn.execute("SELECT id, severity FROM defects"))
    open_rows = _rows(conn, "SELECT id, title, severity AS note FROM defects WHERE"
                            " lifecycle_status IN ('Open', 'In-progress')")
    open_rows.sort(key=lambda r: (_SEVERITY.get(r["note"], 9), _key(r["id"])))
    for row in open_rows:
        row["title"] = " ".join(str(row["title"] or "").split())[:S.TITLE_CAP]
    new_items = [dict(it, note=sev.get(it["id"])) for it in _items(conn, "defects", new)]
    return {"defects_new": as_list(new_items, cap),
            "defects_open": {"items": open_rows if cap is None else open_rows[:cap],
                             "total": len(open_rows)},
            "defects_closed": as_list(_items(conn, "defects", closed), cap)}


def risks(conn, cls: dict, cap) -> dict:
    new = [(i, None, s) for t, i, s in cls["new"] if t == "risks"]
    moved = [(i, a, b) for t, i, a, b in cls["moved"] if t == "risks"]
    high = _rows(conn, "SELECT id, title, risk_state AS note FROM risks WHERE risk_state IN"
                       " ('open', 'materialized') AND (probability = 'high' OR"
                       " impact = 'high')")
    for row in high:
        row["title"] = " ".join(str(row["title"] or "").split())[:S.TITLE_CAP]
    return {"risks_new": as_list(_items(conn, "risks", new), cap),
            "risks_moved": as_list(_items(conn, "risks", moved), cap),
            "risks_high": as_list(high, cap)}


def blocked(conn) -> list[dict]:
    rows = conn.execute(
        "SELECT e.from_id, e.to_id FROM trace_edges e WHERE e.relation = 'blocked_by'"
        " AND (e.from_id IN (SELECT id FROM wbs_items WHERE lifecycle_status NOT IN"
        " ('Implemented', 'Superseded', 'Obsolete', 'Rejected'))"
        " OR e.from_id IN (SELECT id FROM slices WHERE lifecycle_status NOT IN"
        " ('Implemented', 'Superseded', 'Obsolete', 'Rejected')))").fetchall()
    names = {**titles(conn, "wbs_items", [r[0] for r in rows]),
             **titles(conn, "slices", [r[0] for r in rows])}
    return [{"id": a, "title": names.get(a, ""), "note": f"blocked by {b}"} for a, b in rows]


def _entry_items(entries, kinds, screen) -> list[dict]:
    out = []
    for e in entries:
        if e["event_type"] in kinds:
            text = S.first_sentence(e["entry"])
            out.append({"id": e["id"], "title": f"withheld: read {e['id']}"
                        if screen(text) else text, "note": e["event_type"]})
    return out


def _json(text) -> dict:
    try:
        value = json.loads(text) if isinstance(text, str) else (text or {})
    except ValueError:
        return {}
    return value if isinstance(value, dict) else {}


# ----------------------------------------------------------------------------- next

def active(conn) -> tuple[list[str], dict | None]:
    """(active slice ids, the active phase): slices in Approved or Review, else the first
    open phase by `sort_order`."""
    slices = _rows(conn, "SELECT id, phase_id FROM slices WHERE lifecycle_status IN"
                         " ('Approved', 'Review')")
    phase_id = next((s["phase_id"] for s in sorted(slices, key=lambda s: _key(s["id"]))
                     if s["phase_id"]), None)
    sql = "SELECT id, title FROM phases WHERE "
    phase = (_rows(conn, sql + "id = ?", (phase_id,)) if phase_id else _rows(
        conn, sql + "lifecycle_status NOT IN ('Implemented', 'Superseded', 'Obsolete',"
        " 'Rejected') ORDER BY sort_order, id LIMIT 1"))
    return sorted((s["id"] for s in slices), key=_key), (phase[0] if phase else None)


def upcoming(conn, handoff: dict, today: str, screen, cap) -> dict:
    slice_ids, phase = active(conn)
    if slice_ids:
        work = _rows(conn, "SELECT id, title, lifecycle_status AS note FROM v_backlog WHERE"
                           f" slice_id IN ({', '.join('?' * len(slice_ids))})", slice_ids)
    elif phase:
        work = _rows(conn, "SELECT id, title, lifecycle_status AS note FROM v_backlog"
                           " WHERE phase_id = ?", (phase["id"],))
    else:
        work = []
    until = (_dt.date.fromisoformat(today) + _dt.timedelta(days=S.DUE_DAYS)).isoformat()
    due = _rows(conn, "SELECT id, title, due AS note FROM milestones WHERE due >= ? AND"
                      " due <= ?", (today, until))
    due += _rows(conn, "SELECT id, title, due_by AS note FROM open_questions WHERE"
                       " resolved_by IS NULL AND resolution IS NULL AND due_by >= ? AND"
                       " due_by <= ?", (today, until))
    for row in work + due:
        row["title"] = " ".join(str(row["title"] or "").split())[:S.TITLE_CAP]
    return {"open_work": as_list(work, cap), "due_soon": as_list(due, cap),
            "resume_at": as_list(_text_items(handoff.get("resume at", []), screen,
                                             "handoff"), None)}


def glance(conn, sections: dict) -> dict:
    """The at-a-glance counts and the active phase's progress (Review never counts as done)."""
    phase = active(conn)[1]
    progress = None
    if phase:
        rows = conn.execute("SELECT lifecycle_status FROM wbs_items WHERE phase_id = ? AND"
                            " lifecycle_status NOT IN ('Superseded', 'Obsolete', 'Rejected')",
                            (phase["id"],)).fetchall()
        statuses = [r[0] for r in rows]
        progress = {"phase": phase["id"], "title": " ".join(str(phase["title"] or "").split()),
                    "done": statuses.count("Implemented"), "claimed": statuses.count("Review"),
                    "total": len(statuses)}
    d, c, n = sections["did"], sections["challenges"], sections["needs"]
    return {"tasks_done": d["tasks_done"]["total"], "checks_passed": d["checks_passed"]["total"],
            "defects_open": c["defects_open"]["total"],
            "needs_you": sum(n[k]["total"] for k in ("approve_decisions", "approve_scope",
                                                     "confirm_rows", "questions_overdue")),
            "phase": progress}


def where_we_stand(live: dict) -> dict:
    """First report only: rows per family and status."""
    out: dict[str, dict] = {}
    for table, values in sorted(live.items()):
        for value in values.values():
            status = value.rpartition("|")[0] or "(no status)"
            out.setdefault(table, {})[status] = out.setdefault(table, {}).get(status, 0) + 1
    return out


def rule_colour(sections: dict) -> tuple[str, list[str]]:
    """Red: an open critical/high defect or a failing blocking rule. Amber: an open high risk
    or an overdue question. Green otherwise. Returns the colour and the reasons."""
    c, n = sections["challenges"], sections["needs"]
    severe = [it["id"] for it in c["defects_open"]["items"] if it.get("note") in
              ("critical", "high")]
    red = ([f"open {len(severe)} critical or high defect(s)"] if severe else []) + (
        [f"{c['blocker_rules']['total']} blocking rule(s) fail"]
        if c["blocker_rules"]["total"] else [])
    if red:
        return "red", red
    amber = ([f"{c['risks_high']['total']} open high risk(s)"] if c["risks_high"]["total"]
             else []) + ([f"{n['questions_overdue']['total']} overdue question(s)"]
                         if n["questions_overdue"]["total"] else [])
    return ("amber", amber) if amber else ("green", [])


def first_moves(live: dict) -> dict:
    """The first report lists the current state: every row counts as moved from none."""
    moved = [(t, i, "", v.rpartition("|")[0]) for t, m in live.items() for i, v in m.items()]
    return {"moved": moved, "edited": [], "new": [], "dropped": [], "first_counted": [],
            "paused": []}


def build(conn, *, cls: dict, live: dict, first: bool, window: dict, today: str,
          blocker_rules: list[str], screen) -> dict:
    """Every section's facts for one draft."""
    cap = None if first else S.LIST_CAP
    entries = S.window_entries(conn, window["pe_from"], window["pe_to"])
    verdicts = S.window_verdicts(conn, window["av_from"], window["av_to"])
    handoff = S.handoff_sections(conn)
    moves = first_moves(live) if first else cls
    sections = {"needs": needs(conn, handoff, today, screen, cap),
                "did": did(conn, moves, entries, verdicts, screen, cap),
                "challenges": challenges(conn, moves, entries, verdicts, blocker_rules,
                                         screen, cap),
                "next": upcoming(conn, handoff, today, screen, cap)}
    sections["glance"] = glance(conn, sections)
    if first:
        sections["where_we_stand"] = where_we_stand(live)
    sections["notes"] = {"first_counted": cls.get("first_counted", []),
                         "edits_paused": cls.get("paused", []),
                         "journal_rows": len(entries), "verdicts": len(verdicts)}
    return sections
