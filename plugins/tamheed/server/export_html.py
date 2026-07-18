"""Tamheed HTML review surface — the operator's human-facing view (plan 012/B6, D-REVIEW).

Reads the live SQLite connection (never re-parses text files) and renders ONE
self-contained static HTML file. Security doctrine (W-V2-6, non-negotiable):
every data-derived string passes esc(); no data-derived links, ever — URLs render
as plain text, so javascript: schemes are inert; no JavaScript at all; restrictive
CSP. Deterministic: same DB state => byte-identical HTML (every query is ordered;
no wall clock — the C1 freshness stamp derives from stored timestamps).

New entity families (plan 015) render automatically: the Registers section iterates
ENTITY_TABLES; a new section = one entry in SECTIONS at the bottom of this file.
"""
from __future__ import annotations

import html as _html
import json
import sqlite3
from pathlib import Path

from tamheed_server import ENTITY_TABLES

CSS_PATH = Path(__file__).with_name("viewer.css")
_CSP = "default-src 'none'; style-src 'unsafe-inline'"
_TS_COLUMNS = ("created_at", "occurred_at", "recorded_at", "last_referenced")
_TRACE_BUCKETS = {"decision": "Decisions / ADRs", "adr": "Decisions / ADRs",
                  "wbs-item": "Work items", "slice": "Work items",
                  "test": "Tests", "acceptance-criterion": "Acceptance criteria"}
_MATRIX_COLUMNS = ["Decisions / ADRs", "Work items", "Tests", "Acceptance criteria", "Other"]


def esc(value) -> str:
    """THE single escape point — attribute-safe (quote=True); None renders empty."""
    return "" if value is None else _html.escape(str(value), quote=True)


def _cols(conn: sqlite3.Connection, table: str) -> list[str]:
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


def _table(headers, rows) -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{esc(cell)}</td>" for cell in row) + "</tr>" for row in rows
    )
    return (f'<div class="tablewrap"><table><thead><tr>{head}</tr></thead>'
            f"<tbody>{body}</tbody></table></div>")


def _freshness(conn: sqlite3.Connection) -> str:
    """C1: freshness from stored timestamps, never the wall clock (determinism)."""
    row = conn.execute("SELECT iteration FROM packages LIMIT 1").fetchone()
    iteration = row[0] if row else "?"
    latest = None
    for table in ["packages", *sorted(set(ENTITY_TABLES.values()))]:
        for col in _TS_COLUMNS:
            if col in _cols(conn, table):
                (value,) = conn.execute(f"SELECT MAX({col}) FROM {table}").fetchone()
                if value is not None and (latest is None or value > latest):
                    latest = value
    return f"iteration {iteration} · latest recorded activity: {latest or 'none recorded'}"


# ------------------------------------------------------------------ sections

def _overview(conn, gates, ready):
    chips = []
    for gate, info in gates.items():
        if not gate.startswith("G-"):
            continue
        status = info.get("status", "?")
        failures = info.get("failures") or []
        label = f"{gate}: {status}" + (f" ({len(failures)})" if failures else "")
        chips.append(f'<span class="chip {esc(status)}">{esc(label)}</span>')
    evidence = gates.get("audit_evidence", {})
    cols = [c for c in _cols(conn, "packages") if c != "custom_attributes"]
    row = conn.execute(f"SELECT {', '.join(cols)} FROM packages LIMIT 1").fetchone()
    identity = (_table(["field", "value"], list(zip(cols, row))) if row
                else '<p class="empty">No package row.</p>')
    return (f'<p class="ready">Gate verdict: {"READY" if ready else "NOT READY"}</p>'
            f'<p>{"".join(chips)}</p>'
            f'<p>Audit evidence: {esc(evidence.get("evidenced", 0))} evidenced / '
            f'{esc(evidence.get("narrated", 0))} narrated'
            " (narrated = the graded party grading itself, C7)</p>" + identity)


def _design_ahead(conn) -> str:
    """C9: approved-but-unimplemented as an explicit, healthy state (Marid's PH-7)."""
    counts = []
    for label, table in (("requirements", "requirements"), ("decisions", "decisions"),
                         ("acceptance criteria", "acceptance_criteria")):
        (n,) = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE lifecycle_status = 'Approved'").fetchone()
        counts.append(f"{n} {label}")
    return ('<p class="lead">Design-ahead lead (Approved, not yet Implemented — '
            "an explicit, healthy state): " + esc("; ".join(counts)) + "</p>")


def _registers(conn, gates, ready):
    parts, empty = [_design_ahead(conn)], []
    for table in ENTITY_TABLES.values():
        if table == "trace_edges":
            continue  # rendered in Traceability
        cols = [c for c in _cols(conn, table) if c != "custom_attributes"]
        rows = conn.execute(
            f"SELECT {', '.join(cols)} FROM {table} ORDER BY {cols[0]}").fetchall()
        label = table.replace("_", " ").capitalize()
        if not rows:
            empty.append(label)
            continue
        parts.append(f"<h3>{esc(label)} ({len(rows)})</h3>" + _table(cols, rows))
    if empty:
        parts.append(f'<p class="empty">Empty families: {esc(", ".join(sorted(empty)))}</p>')
    return "".join(parts)


def _traceability(conn, gates, ready):
    typemap = dict(conn.execute("SELECT id, entity_type FROM entity_index"))
    links: dict[str, dict[str, set]] = {}
    edges = conn.execute(
        "SELECT from_id, to_id, relation FROM trace_edges"
        " ORDER BY from_id, to_id, relation").fetchall()
    for from_id, to_id, _rel in edges:
        for req, other in ((from_id, to_id), (to_id, from_id)):
            if typemap.get(req) == "requirement" and other != req:
                bucket = _TRACE_BUCKETS.get(typemap.get(other, ""), "Other")
                links.setdefault(req, {}).setdefault(bucket, set()).add(other)
    for ac_id, req_id in conn.execute(
            "SELECT id, requirement_id FROM acceptance_criteria"
            " WHERE requirement_id IS NOT NULL ORDER BY id"):
        links.setdefault(req_id, {}).setdefault("Acceptance criteria", set()).add(ac_id)
    reqs = conn.execute("SELECT id, title, mvp FROM requirements ORDER BY id").fetchall()
    if not reqs and not edges:
        return '<p class="empty">No requirements or trace edges recorded.</p>'
    rows = [[rid, title, "MVP" if mvp else "",
             *(", ".join(sorted(links.get(rid, {}).get(b, ()))) for b in _MATRIX_COLUMNS)]
            for rid, title, mvp in reqs]
    matrix = _table(["requirement", "title", "mvp", *_MATRIX_COLUMNS], rows)
    edge_table = (_table(["from", "relation", "to"],
                         [(f, r, t) for f, t, r in edges])
                  if edges else '<p class="empty">No trace edges recorded.</p>')
    return matrix + f"<h3>All trace edges ({len(edges)})</h3>" + edge_table


def _execution(conn, gates, ready):
    acs = conn.execute(
        "SELECT ac.id, ac.title, ac.lifecycle_status,"
        " (SELECT verdict FROM audit_verdicts av WHERE av.ac_id = ac.id"
        "  ORDER BY av.id DESC LIMIT 1),"
        " (SELECT evidence FROM audit_verdicts av WHERE av.ac_id = ac.id"
        "  ORDER BY av.id DESC LIMIT 1)"
        " FROM acceptance_criteria ac ORDER BY ac.id").fetchall()
    ac_rows = [[ac_id, title, lifecycle, verdict or "Pending",
                "evidenced" if evidence else ("narrated" if verdict else ""), evidence]
               for ac_id, title, lifecycle, verdict, evidence in acs]
    parts = ["<h3>Acceptance criteria × audit verdicts</h3>",
             _table(["ac", "title", "lifecycle", "verdict", "evidence class", "evidence"],
                    ac_rows)
             if ac_rows else '<p class="empty">No acceptance criteria recorded.</p>']
    entries = conn.execute(
        "SELECT id, occurred_at, entry, phase_id, slice_id FROM progress_entries"
        " ORDER BY id").fetchall()
    parts.append("<h3>Progress log</h3>")
    parts.append(_table(["id", "occurred at", "entry", "phase", "slice"], entries)
                 if entries else '<p class="empty">No progress entries recorded.</p>')
    changes = conn.execute(
        "SELECT id, iteration, decision_ref, description FROM scope_changes"
        " ORDER BY id").fetchall()
    parts.append("<h3>Scope changes</h3>")
    parts.append(_table(["id", "iteration", "authorized by", "description"], changes)
                 if changes else '<p class="empty">No scope changes recorded.</p>')
    return "".join(parts)


def _gaps(conn, gates, ready):
    """Adopt-mode gap reports + injection-screen flags — these exist to be SEEN."""
    rows = conn.execute(
        "SELECT id, title, question, source_span, custom_attributes FROM open_questions"
        " WHERE source_span = 'adopt:gap-report'"
        " OR title LIKE 'Injection-shaped text found at%' ORDER BY id").fetchall()
    if not rows:
        return '<p class="empty">No gap-report or injection-screen notes recorded.</p>'
    cards = []
    for oq_id, title, question, span, attrs in rows:
        fenced = ""
        if attrs:
            try:
                payload = json.loads(attrs).get("fenced")
            except (ValueError, AttributeError):
                payload = None
            if payload:  # the captured hostile span, shown escaped-as-data
                fenced = f"<pre>{esc(payload)}</pre>"
        cards.append(f'<div class="warn"><strong>{esc(oq_id)}: {esc(title)}</strong>'
                     f"<p>{esc(question)}</p><p>Source: {esc(span)}</p>{fenced}</div>")
    return "".join(cards)


# One entry per section — plan 015 additions register here.
SECTIONS = [
    ("overview", "Overview", _overview),
    ("registers", "Registers", _registers),
    ("traceability", "Traceability", _traceability),
    ("execution", "Execution progress", _execution),
    ("gaps", "Gap & screening notes", _gaps),
]


def render(conn: sqlite3.Connection, gates: dict, ready: bool) -> str:
    """Render the full review surface from a loaded package connection."""
    row = conn.execute("SELECT name FROM packages LIMIT 1").fetchone()
    name = row[0] if row else "unnamed-package"
    freshness = _freshness(conn)
    sections = "\n".join(
        f'<section id="{anchor}"><h2>{esc(title)}</h2>'
        f'<p class="freshness">Freshness: {esc(freshness)}</p>{fn(conn, gates, ready)}</section>'
        for anchor, title, fn in SECTIONS)
    css = CSS_PATH.read_text(encoding="utf-8")
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta http-equiv="Content-Security-Policy" content="{_CSP}">\n'
            f"<title>{esc(name)} — Tamheed review</title>\n<style>\n{css}</style>\n"
            f"</head>\n<body>\n<h1>{esc(name)} — Tamheed review surface</h1>\n"
            f"{sections}\n</body>\n</html>\n")
