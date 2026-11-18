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


def natural(i) -> tuple:
    """WBS-5.2 before WBS-5.10: every number of the id compares as a number (plan 251)."""
    return tuple(int(x) if x.isdigit() else x for x in re.split(r"(\d+)", str(i or "")))


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


# Plan 241 (the field's FB-020, R121, R129, R135): when a row no longer blocks the row that
# names it in a `blocked_by` edge. ONE definition: the standup list and the readiness advisory
# `blocks-lifted` read it. The two predicates are the readiness rules' own SQL text, so
# `open-questions-resolved` and `risks-discharged` and this rule cannot drift apart.
OQ_UNRESOLVED = ("(resolution IS NULL OR trim(resolution) = '') AND resolved_by IS NULL"
                 " AND lifecycle_status NOT IN ('Deferred','Rejected','Superseded','Obsolete')")
RISK_UNDISCHARGED = "risk_state IN ('open','materialized') AND discharged_by IS NULL"
_DONE = "lifecycle_status IN ('Implemented','Superseded','Obsolete','Rejected')"
SETTLED_WHERE = {
    "dependencies": _DONE, "assumptions": _DONE, "phases": _DONE, "slices": _DONE,
    "wbs_items": _DONE, "execution_plans": _DONE, "requirements": _DONE,
    "defects": "lifecycle_status IN ('Fixed','Won''t-fix','Duplicate')",
    "deferred_work": "lifecycle_status IN ('Done','Won''t-do')",
    "open_questions": f"NOT ({OQ_UNRESOLVED})",
    "decisions": "lifecycle_status IN ('Approved','Rejected','Superseded','Implemented')",
    "risks": f"NOT ({RISK_UNDISCHARGED})",
    "execution_gates": "outcome = 'Go'",     # the gate's latest decision, never the journal
}


def settled_ids(conn) -> set[str]:
    """The ids of every row that blocks nothing any more. A row that does not exist never
    settles, and a family outside the table above never settles either."""
    out: set[str] = set()
    for table, where in SETTLED_WHERE.items():
        out.update(r[0] for r in conn.execute(f"SELECT id FROM {table} WHERE {where}"))
    return out


def _blocked_by(conn) -> dict[str, list[str]]:
    edges: dict[str, list[str]] = {}
    for a, b in conn.execute("SELECT from_id, to_id FROM trace_edges"
                             " WHERE relation = 'blocked_by'"):
        edges.setdefault(a, []).append(b)
    return edges


def lifted(conn) -> dict[str, list[str]]:
    """Open rows whose every `blocked_by` far end is settled: work that is free to start
    (R130). The edges stay as history. A row is open while it is not settled itself."""
    done = settled_ids(conn)
    return {a: sorted(bs, key=_key) for a, bs in sorted(_blocked_by(conn).items(),
                                                        key=lambda kv: _key(kv[0]))
            if a not in done and all(b in done for b in bs)}


def blocked(conn) -> list[dict]:
    """Open slices and WBS items, each with a far end that is not settled (R121)."""
    done = settled_ids(conn)
    rows = [r for r in conn.execute(
        "SELECT e.from_id, e.to_id FROM trace_edges e WHERE e.relation = 'blocked_by'"
        " AND (e.from_id IN (SELECT id FROM wbs_items WHERE lifecycle_status NOT IN"
        " ('Implemented', 'Superseded', 'Obsolete', 'Rejected'))"
        " OR e.from_id IN (SELECT id FROM slices WHERE lifecycle_status NOT IN"
        " ('Implemented', 'Superseded', 'Obsolete', 'Rejected')))").fetchall()
        if r[1] not in done]
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


# ----------------------------------------------------------------------------- the plan tree

# Plan 251 (R3-R9, D2-D6): the whole plan as one tree, frozen at the draft. The page opens the
# branches with news. Tags from the window: "done" (moved to Implemented, or a Met verdict),
# "claimed" (moved to Review; claimed never counts as done), "blocked" (a blocker not settled).
OPEN = ("Draft", "Proposed", "Approved")
_GONE = ("Superseded", "Obsolete", "Rejected")
# Plan 251 v2 (U10, V1, V3): ONE state per row, in this order. Every count on the page reads it.
STATES = ("done-window", "claimed-window", "done-earlier", "blocked", "in-progress", "next",
          "not-started", "failed", "not-checked", "postponed")


def row_state(item: dict, kind: str, ctx: dict) -> str:
    """The state of one task or acceptance check. `ctx` holds the row's slice, the current
    (`now`) and next slice, the ids worked on in the window (`touched`) and `first`."""
    st = item.get("status")
    if kind == "check":
        if item.get("tag") == "done":
            return "done-window"
        if item.get("result") == "Met":
            return "done-earlier"
        if item.get("result") in ("Not-met", "Partial"):
            return "failed"
        return "not-checked"
    if st == "Deferred":
        return "postponed"
    if item.get("tag") == "done":
        return "done-window"
    if item.get("tag") == "claimed":
        return "claimed-window"
    if st == "Implemented":
        return "done-earlier"
    if item.get("tag") == "blocked":
        return "blocked"
    here = ctx.get("slice")
    if st == "Review" or item["id"] in ctx.get("touched", ()):
        return "in-progress"
    if here and here == ctx.get("now") and st in OPEN:
        return "in-progress" if ctx.get("first") else "next"   # V3: a first report
    if here and ctx.get("next") and here == ctx.get("next"):
        return "next"
    return "not-started"


def touched(entries: list[dict], first: bool) -> list[str]:
    """The rows worked on in the window: the subjects of its work-done entries. A first report
    covers the whole history, so nothing counts as touched (V3)."""
    if first:
        return []
    return sorted({str(e["subject_id"]) for e in entries
                   if e["event_type"] == "work-done" and e.get("subject_id")}, key=_key)


def overall(conn) -> dict:
    """Section 7 "Overall" (U17) and section 4's requirement count: the counts per family and
    every row of the decision, defect, risk and question registers, frozen in each report."""
    def counts(sql):
        return {str(s): n for s, n in conn.execute(sql)}

    def rows(sql):
        return [[str(i), _clean(t), str(s or "")] for i, t, s in conn.execute(sql)]
    open_q = ("CASE WHEN resolution IS NULL AND resolved_by IS NULL THEN 'open' ELSE"
              " 'answered' END")
    return {
        "requirements": counts("SELECT lifecycle_status, COUNT(*) FROM requirements GROUP BY 1"),
        "families": {
            "decisions": counts("SELECT lifecycle_status, COUNT(*) FROM decisions GROUP BY 1"),
            "defects": counts("SELECT lifecycle_status, COUNT(*) FROM defects GROUP BY 1"),
            "risks": counts("SELECT risk_state, COUNT(*) FROM risks GROUP BY 1"),
            "open_questions": counts(f"SELECT {open_q}, COUNT(*) FROM open_questions GROUP BY 1")},
        "lists": {
            "decisions": rows("SELECT id, title, lifecycle_status FROM decisions"),
            "defects": rows("SELECT id, title, lifecycle_status || ' · ' || COALESCE(severity, '')"
                            " FROM defects"),
            "risks": rows("SELECT id, title, risk_state FROM risks"),
            "open_questions": rows(f"SELECT id, title, {open_q} FROM open_questions")}}


def _clean(text) -> str:
    return " ".join(str(text or "").split())[:S.TITLE_CAP]


def window_tags(cls: dict, verdicts: list[dict]) -> dict[str, str]:
    """{id: "done" | "claimed"} for what this window moved (D6). Checks come from the window's
    verdicts, because verdicts are not in the state."""
    tags: dict[str, str] = {}
    for table in ("wbs_items", "slices", "phases"):
        for i, _a, _b in moved_to(cls, table, ("Review",)):
            tags[i] = "claimed"
        for i, _a, _b in moved_to(cls, table, ("Implemented",)):
            tags[i] = "done"
    for v in verdicts:
        if v["verdict"] == "Met":
            tags[str(v["ac_id"])] = "done"
    return tags


def _counts(statuses: list[str]) -> dict:
    return {"done": statuses.count("Implemented"), "claimed": statuses.count("Review"),
            "open": sum(s in OPEN for s in statuses), "total": len(statuses)}


def _node(row: dict, tags: dict, blocked_ids: set) -> dict:
    out = {"id": row["id"], "title": _clean(row.get("title")), "status": row.get("status")}
    tag = tags.get(row["id"]) or ("blocked" if row["id"] in blocked_ids and
                                  row.get("status") in OPEN + ("Review",) else None)
    if tag:
        out["tag"] = tag
    return out


def _nest(tasks: list[dict], tags: dict, blocked_ids: set) -> list[dict]:
    """Tasks under their parent task. A parent outside the list, or a loop of parents, leaves
    the task at the top, so no task is lost."""
    parent = {t["id"]: t.get("parent_id") for t in tasks}

    def rooted(i: str) -> bool:
        seen = {i}
        up = parent.get(i)
        while up in parent:
            if up in seen:
                return False
            seen.add(up)
            up = parent.get(up)
        return True

    nodes = {t["id"]: _node(t, tags, blocked_ids) for t in tasks}
    top: list[dict] = []
    for t in sorted(tasks, key=lambda t: natural(t["id"])):
        p = t.get("parent_id")
        if p in nodes and p != t["id"] and rooted(t["id"]):
            nodes[p].setdefault("children", []).append(nodes[t["id"]])
        else:
            top.append(nodes[t["id"]])
    return top


def _lines(conn, open_slices: set, task_slice: dict, window: dict, marks: bool,
           screen) -> dict[str, list]:
    """Every work-done line tied to an open slice, newest first (R9, D6)."""
    out: dict[str, list] = {s: [] for s in open_slices}
    for pid, entry, subject, slice_id in conn.execute(
            "SELECT id, entry, subject_id, slice_id FROM progress_entries WHERE"
            " event_type = 'work-done' AND id GLOB ? ORDER BY CAST(SUBSTR(id, 4) AS INTEGER)"
            " DESC", (S._PE_RE,)):
        home = next((s for s in (slice_id, subject, task_slice.get(subject)) if s in out), None)
        if home is None:
            continue
        text = S.first_sentence(entry)
        line = {"id": pid, "title": f"withheld: read {pid}" if screen(text) else text}
        if marks and window["pe_from"] <= int(pid[3:]) <= window["pe_to"]:
            line["tag"] = "this report"
        out[home].append(line)
    return out


def plan_tree(conn, cls: dict, verdicts: list[dict], window: dict, *, marks: bool,
              screen) -> dict:
    """The whole plan, frozen at the draft (D2). `marks` is False on a first report and after
    a broken chain: no window tags then (D6)."""
    tags = window_tags(cls, verdicts) if marks else {}
    blocked_ids = {b["id"] for b in blocked(conn)}
    phases = sorted(_rows(conn, "SELECT id, title, lifecycle_status AS status, sort_order"
                                " FROM phases"), key=lambda r: (r["sort_order"] is None,
                                                                 r["sort_order"] or 0,
                                                                 _key(r["id"])))
    slices = sorted([r for r in _rows(conn, "SELECT id, title, phase_id, lifecycle_status AS"
                                            " status, sort_order FROM slices")
                     if r["status"] not in _GONE],
                    key=lambda r: (r["sort_order"] is None, r["sort_order"] or 0, _key(r["id"])))
    tasks = [r for r in _rows(conn, "SELECT id, title, parent_id, phase_id, slice_id,"
                                    " lifecycle_status AS status FROM wbs_items")
             if r["status"] not in _GONE]
    latest = dict(conn.execute("SELECT ac_id, verdict FROM v_latest_verdicts"))
    checks = [dict(r, result=latest.get(r["id"])) for r in _rows(
        conn, "SELECT id, title, slice_id, lifecycle_status AS status FROM acceptance_criteria")
        if r["status"] not in _GONE]
    stones = _rows(conn, "SELECT id, title, phase_id, due FROM milestones")
    slice_phase = {s["id"]: s["phase_id"] for s in slices}
    task_slice = {t["id"]: t["slice_id"] for t in tasks if t["slice_id"] in slice_phase}
    open_slices = {s["id"] for s in slices if s["status"] in OPEN + ("Review",)}
    lines = _lines(conn, open_slices, task_slice, window, marks, screen)

    def check_node(c: dict) -> dict:
        node = _node(c, tags, set())
        if c["result"]:
            node["result"] = c["result"]
        return node

    def slice_node(s: dict) -> dict:
        own = [t for t in tasks if t["slice_id"] == s["id"]]
        node = _node(s, tags, blocked_ids)
        node.update(counts=_counts([t["status"] for t in own]),
                    tasks=_nest(own, tags, blocked_ids),
                    checks=[check_node(c) for c in sorted(checks, key=lambda c: _key(c["id"]))
                            if c["slice_id"] == s["id"]])
        if s["id"] in lines:
            node["lines"] = lines[s["id"]]
        return node

    tree = []
    for ph in phases:
        mine = [t for t in tasks if (t["phase_id"] or slice_phase.get(t["slice_id"])) == ph["id"]]
        loose = [t for t in mine if t["slice_id"] not in slice_phase]
        node = _node(ph, tags, set())
        node.update(counts=_counts([t["status"] for t in mine]),
                    milestones=[{"id": m["id"], "title": _clean(m["title"]), "due": m["due"]}
                                for m in sorted(stones, key=lambda m: _key(m["id"]))
                                if m["phase_id"] == ph["id"]],
                    slices=[slice_node(s) for s in slices if s["phase_id"] == ph["id"]],
                    loose=_nest(loose, tags, blocked_ids))
        tree.append(node)
    placed = {ph["id"] for ph in phases}
    outside = [t for t in tasks if (t["phase_id"] or slice_phase.get(t["slice_id"]))
               not in placed]
    order = [s["id"] for ph in tree for s in ph["slices"] if s["status"] in OPEN + ("Review",)]
    return {"phases": tree, "marks": marks,
            "outside": {"tasks": _nest(outside, tags, blocked_ids),
                        "checks": [check_node(c) for c in sorted(checks, key=lambda c: _key(
                            c["id"])) if c["slice_id"] not in slice_phase]},
            "suggest": {"now": order[0] if order else None,
                        "next": order[1] if len(order) > 1 else None}}


def plan_summary(plan: dict) -> dict:
    """What the draft result carries instead of the tree (D1): counts, the open slices, the
    first 30 open tasks of the suggested slices, and the suggestion. The row keeps the tree."""
    named = {plan["suggest"].get("now"), plan["suggest"].get("next")}
    def flat(nodes):
        for n in nodes:
            yield n
            yield from flat(n.get("children", []))
    phases = [{"id": p["id"], "title": p["title"], "status": p["status"], "counts": p["counts"]}
              for p in plan["phases"]]
    open_slices = [{"id": s["id"], "title": s["title"], "status": s["status"],
                    "counts": s["counts"], "lines": len(s.get("lines", [])),
                    **({"open_tasks": [{"id": t["id"], "title": t["title"],
                                        "status": t["status"]} for t in flat(s["tasks"])
                                       if t["status"] in OPEN][:30]} if s["id"] in named else {})}
                   for p in plan["phases"] for s in p["slices"] if "lines" in s]
    return {"phases": phases, "open_slices": open_slices, "suggest": plan["suggest"]}


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
    """Red: an open critical/high defect. Amber: an open high risk or an overdue question.
    Green otherwise. Returns the colour and the reasons. The release rules (readiness's
    blocking rules) are not an input (SR51): they fail during normal work."""
    c, n = sections["challenges"], sections["needs"]
    severe = [it["id"] for it in c["defects_open"]["items"] if it.get("note") in
              ("critical", "high")]
    red = ([_n(len(severe), "open critical or high defect", "open critical or high defects")]
           if severe else [])
    if red:
        return "red", red
    amber = ([_n(c["risks_high"]["total"], "open high risk", "open high risks")]
             if c["risks_high"]["total"] else []) + (
        [_n(n["questions_overdue"]["total"], "overdue question", "overdue questions")]
        if n["questions_overdue"]["total"] else [])
    return ("amber", amber) if amber else ("green", [])


def _as_status(sections: dict) -> None:
    for part in sections.values():
        for value in (part.values() if isinstance(part, dict) else ()):
            for it in (value.get("items", []) if isinstance(value, dict) else ()):
                move = it.pop("move", None)
                if move and not it.get("note"):
                    it["note"] = move[1]


def _n(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def first_moves(live: dict) -> dict:
    """The first report lists the current state: every row counts as moved from none."""
    moved = [(t, i, "", v.rpartition("|")[0]) for t, m in live.items() for i, v in m.items()]
    return {"moved": moved, "edited": [], "new": [], "dropped": [], "first_counted": [],
            "paused": []}


def build(conn, *, cls: dict, live: dict, first: bool, window: dict, today: str,
          blocker_rules: list[str], screen) -> dict:
    """Every section's facts for one draft."""
    cap = None                         # plan 251 v2 (U8): every list keeps every item
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
    sections["touched"] = touched(entries, first)
    sections["overall"] = overall(conn)
    sections["plan"] = plan_tree(conn, cls, verdicts, window, screen=screen,
                                 marks=not first and not window.get("broken"))
    if first:
        sections["where_we_stand"] = where_we_stand(live)
        _as_status(sections)          # a catch-up lists states, not moves: nothing is "new"
    sections["notes"] = {"first_counted": cls.get("first_counted", []),
                         "edits_paused": cls.get("paused", []),
                         "journal_rows": len(entries), "verdicts": len(verdicts)}
    return sections
