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
import math
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


def _fold(title: str, count: int, inner: str, anchor: str | None = None,
          csv: str | None = None) -> str:
    """C21 (plan 019, maintainer decision): EVERY table folds closed — one consistent
    affordance instead of a size threshold. The summary keeps the count visible; browsers
    auto-expand closed <details> on find-in-page. Sole exception: the gap/screening warn
    cards, which exist to be SEEN and are never folded.
    C25: `anchor` gives the fold a jump target (graph aggregate nodes); `csv` renders a
    download link to the sibling csv/<name>.csv the server emits beside review.html."""
    unit = "row" if count == 1 else "rows"
    aid = f' id="{esc(anchor)}"' if anchor else ""
    dl = (f' <a class="csv" href="csv/{esc(csv)}.csv" download>CSV</a>' if csv else "")
    return (f"<details{aid}><summary>{esc(title)} ({count} {unit}){dl}</summary>"
            f"{inner}</details>")


def _table(headers, rows, row_ids: bool = False) -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join(
        # row_ids: column 0 is a globally unique entity id (entity_index PK) — the <tr>
        # anchor is the jump target for graph node links; same esc() as the hrefs, so
        # link and target match byte-for-byte even for pathological ids (C25).
        (f'<tr id="{esc(row[0])}">' if row_ids else "<tr>")
        + "".join(f"<td>{esc(cell)}</td>" for cell in row) + "</tr>" for row in rows
    )
    return (f'<div class="tablewrap"><table><thead><tr>{head}</tr></thead>'
            f"<tbody>{body}</tbody></table></div>")


def _freshness(conn: sqlite3.Connection) -> str:
    """C1: freshness from stored timestamps, never the wall clock (determinism)."""
    row = conn.execute("SELECT iteration, created_at FROM packages LIMIT 1").fetchone()
    iteration, created = (row[0], row[1]) if row else ("?", None)
    latest = None
    for table in sorted(set(ENTITY_TABLES.values())):
        for col in _TS_COLUMNS:
            if col in _cols(conn, table):
                (value,) = conn.execute(f"SELECT MAX({col}) FROM {table}").fetchone()
                if value is not None and (latest is None or value > latest):
                    latest = value
    if latest is None:
        # Field-evidence C18: right after migration the only date around is the package
        # record's own (often the v1 manifest's) — calling it "activity" reads as
        # staleness. Say what it actually is.
        return (f"iteration {iteration} · package record dated {created or 'unknown'}; "
                "no v2 activity recorded yet")
    return f"iteration {iteration} · latest recorded activity: {latest}"


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
    attrs = conn.execute("SELECT custom_attributes FROM packages LIMIT 1").fetchone()
    # C18: on migrated packages, mode/profile/created_at are v1-manifest passthrough
    # (ACMP read "mode: resume" as the report's own state) — label them for what they are.
    migrated = bool(attrs and attrs[0] and "v1_manifest" in attrs[0])
    identity_rows = [(c, f"{v} (v1-manifest-derived)"
                      if migrated and v is not None and c in ("mode", "profile", "created_at")
                      else v)
                     for c, v in zip(cols, row)] if row else []
    identity = (_fold("Package identity", len(identity_rows),
                      _table(["field", "value"], identity_rows)) if row
                else '<p class="empty">No package row.</p>')
    return (f'<p class="ready">Gate verdict: {"READY" if ready else "NOT READY"}</p>'
            f'<p>{"".join(chips)}</p>'
            f'<p>Audit evidence: {esc(evidence.get("evidenced", 0))} evidenced / '
            f'{esc(evidence.get("narrated", 0))} narrated'
            " (narrated = the graded party grading itself, C7)</p>" + identity)


# ------------------------------------------------------------------ relations graph
# C25 (maintainer req 4): every entity as a clickable node, every trace edge drawn —
# deterministic pure-Python geometry, inline SVG, zero JS, fragment links only.
_G_GAP = 3        # empty slots between adjacent families
_G_SPACING = 8.0  # px of arc per slot (node diameter 6 + padding)
_G_RMIN = 260.0
_G_LABELS = 140   # radial band outside the circle for family labels
_G_AGG_LIMIT = 4000  # ponytail: family-aggregate view above this; full graph proven ~2.3k


def _grouped_nodes(nodes):
    order = {t: i for i, t in enumerate(ENTITY_TABLES)}
    nodes = sorted(nodes, key=lambda n: (order.get(n[1], 99), n[1], n[0]))
    fams: list[tuple[str, list[str]]] = []
    for nid, fam in nodes:
        if not fams or fams[-1][0] != fam:
            fams.append((fam, []))
        fams[-1][1].append(nid)
    return fams


def _degrees(edges) -> dict[str, int]:
    deg: dict[str, int] = {}
    for f, t, _rel in edges:
        deg[f] = deg.get(f, 0) + 1
        deg[t] = deg.get(t, 0) + 1
    return deg


def _rel_filter(prefix: str, relations) -> str:
    """CSS-only relation filter (plan 027): radio siblings of .graphwrap — the proven
    gz-zoom pattern. Labels double as the color legend (per-relation chip colors in
    viewer.css). Only relations present in the data get a radio (deterministic)."""
    parts = [f'<input type="radio" name="{prefix}" id="{prefix}-all" class="gz" checked>'
             f'<label for="{prefix}-all" class="gzl">all relations</label>']
    for rel in sorted(set(relations)):
        parts.append(
            f'<input type="radio" name="{prefix}" id="{prefix}-{esc(rel)}" class="gz">'
            f'<label for="{prefix}-{esc(rel)}" class="gzl rl-{esc(rel)}">'
            f"{esc(rel)}</label>")
    return "".join(parts)


def _marker(marker_id: str) -> str:
    # One neutral-ink arrowhead per svg (ids are document-unique). Per-relation marker
    # color needs `context-stroke` — unportable, deferred (plan 027).
    return (f'<defs><marker id="{marker_id}" viewBox="0 0 8 8" refX="7" refY="4" '
            'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
            '<path d="M0 0 L8 4 L0 8 z" class="arrowhead"/></marker></defs>')


def _graph_full(nodes, edges) -> str:
    """The circular overview. Plan 027: connected nodes only (74% of the golden's
    nodes were isolated dots), degree-scaled radii, arrowheads, per-relation edge
    classes; 12 hues + a ring stroke as the second-cycle family disambiguator.
    Plan 028 (C34 §5.1): hover-isolate — each node group carries hidden .hl copies of
    its incident edges; :has() dims the base layer on hover, pure CSS."""
    deg = _degrees(edges)
    fams = _grouped_nodes(nodes)
    S = len(nodes) + _G_GAP * len(fams)
    R = max(_G_RMIN, S * _G_SPACING / (2 * math.pi))
    half = R + _G_LABELS + 10
    pos: dict[str, tuple[float, float]] = {}
    meta: list[tuple[str, str, int, str]] = []   # (nid, fam, fi, ring)
    label_parts = []
    slot = 0
    for fi, (fam, ids) in enumerate(fams):
        start = slot
        ring = " ring" if fi >= 12 else ""
        for nid in ids:
            th = 2 * math.pi * slot / S - math.pi / 2
            x, y = R * math.cos(th), R * math.sin(th)
            pos[nid] = (x, y)  # 0.1px rounding absorbs cross-platform libm variation
            meta.append((nid, fam, fi, ring))
            slot += 1
        mid = 2 * math.pi * ((start + slot - 1) / 2) / S - math.pi / 2
        lx, ly = (R + 16) * math.cos(mid), (R + 16) * math.sin(mid)
        anchor = "start" if math.cos(mid) >= 0 else "end"
        label_parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}">'
            f"{esc(fam)} ({len(ids)})</text>")
        slot += _G_GAP
    edge_parts = []
    incident: dict[str, list[str]] = {}
    for f, t, rel in edges:
        if f not in pos or t not in pos:
            continue
        (x1, y1), (x2, y2) = pos[f], pos[t]
        # quadratic pull toward the center: short edges hug the rim, long ones sweep
        # through the middle — the chord-diagram trick that keeps 1,000 edges legible
        cx, cy = 0.35 * (x1 + x2) / 2, 0.35 * (y1 + y2) / 2
        d = f"M{x1:.1f} {y1:.1f} Q{cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}"
        edge_parts.append(
            f'<path d="{d}" class="e-{esc(rel)}" marker-end="url(#arrow)">'
            f"<title>{esc(f)} —{esc(rel)}→ {esc(t)}</title></path>")
        hl = f'<path d="{d}" class="hl e-{esc(rel)}" marker-end="url(#arrow)"/>'
        incident.setdefault(f, []).append(hl)
        if t != f:
            incident.setdefault(t, []).append(hl)
    node_parts = []
    for nid, fam, fi, ring in meta:
        x, y = pos[nid]
        r = min(7.0, 3.0 + 0.8 * math.sqrt(deg.get(nid, 0)))
        node_parts.append(
            f'<g class="nod"><a href="#{esc(nid)}">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" '
            f'class="g{fi % 12}{ring}"/><title>{esc(nid)} ({esc(fam)}, '
            f'{deg.get(nid, 0)} edge(s))</title></a>'
            f'{"".join(incident.get(nid, []))}</g>')
    return _graph_svg(half, edge_parts, node_parts, label_parts, "arrow")


def _graph_svg(half: float, edge_parts, node_parts, label_parts,
               marker_id: str | None = None) -> str:
    # C26 (maintainer): NO fixed pixel width — the viewBox scales to the container, so
    # the default (Fit) shows ALL nodes; the CSS zoom radios scale width 100%..800%.
    d = f"{2 * half:.0f}"
    defs = _marker(marker_id) if marker_id else ""
    return (f'<svg class="graph" viewBox="{-half:.0f} {-half:.0f} {d} {d}" '
            f'xmlns="http://www.w3.org/2000/svg">{defs}'
            f'<g class="edges">{"".join(edge_parts)}</g>'
            f'<g class="nodes">{"".join(node_parts)}</g>'
            f'<g class="labels">{"".join(label_parts)}</g></svg>')


def _graph_agg(nodes, edges) -> str:
    """Above _G_AGG_LIMIT: one node per family, linked to its register fold."""
    fams = _grouped_nodes(nodes)
    fam_of = {nid: fam for nid, fam in nodes}
    pair_counts: dict[tuple[str, str], int] = {}
    for f, t, _rel in edges:
        fa, fb = fam_of.get(f), fam_of.get(t)
        if fa and fb:
            pair_counts[tuple(sorted((fa, fb)))] = \
                pair_counts.get(tuple(sorted((fa, fb))), 0) + 1
    S = max(len(fams), 8)
    R = max(200.0, S * 40.0 / (2 * math.pi))
    half = R + _G_LABELS + 10
    pos = {}
    node_parts, label_parts = [], []
    for i, (fam, ids) in enumerate(fams):
        th = 2 * math.pi * i / S - math.pi / 2
        x, y = R * math.cos(th), R * math.sin(th)
        pos[fam] = (x, y)
        r = 6 + round(2 * math.sqrt(len(ids)))
        table = ENTITY_TABLES.get(fam, fam)
        node_parts.append(
            f'<a href="#reg-{esc(table)}"><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" '
            f'class="g{i % 8}"/><title>{esc(fam)}: {len(ids)} entities</title></a>')
        anchor = "start" if math.cos(th) >= 0 else "end"
        lx, ly = (R + r + 10) * math.cos(th), (R + r + 10) * math.sin(th)
        label_parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}">'
                           f"{esc(fam)} ({len(ids)})</text>")
    edge_parts = []
    for (fa, fb), n in sorted(pair_counts.items()):
        if fa not in pos or fb not in pos or fa == fb:
            continue
        (x1, y1), (x2, y2) = pos[fa], pos[fb]
        w = min(6, 1 + n // 10)
        edge_parts.append(
            f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke-width="{w}">'
            f"<title>{esc(fa)} ↔ {esc(fb)}: {n} edge(s)</title></path>")
    return _graph_svg(half, edge_parts, node_parts, label_parts)


def _graph(conn, gates, ready):
    nodes = conn.execute(
        "SELECT id, entity_type FROM entity_index ORDER BY id").fetchall()
    edges = conn.execute("SELECT from_id, to_id, relation FROM trace_edges"
                         " ORDER BY from_id, to_id, relation").fetchall()
    if not nodes:
        return '<p class="empty">No entities recorded.</p>'
    # Plan 027: draw CONNECTED nodes only — on the golden 74% of nodes had zero edges
    # and buried the structure in dead dots. Isolated entities get their own fold.
    linked = {f for f, _t, _r in edges} | {t for _f, t, _r in edges}
    connected = [(nid, fam) for nid, fam in nodes if nid in linked]
    isolated = [(nid, fam) for nid, fam in nodes if nid not in linked]
    parts = []
    if connected:
        svg = _graph_agg(connected, edges) if len(connected) > _G_AGG_LIMIT \
            else _graph_full(connected, edges)
        hint = ("Hover a family for its size; click to jump to its register."
                if len(connected) > _G_AGG_LIMIT else
                "Hover a node for its id (radius = edge count); click to jump to its "
                "register row. Arrowheads show direction; pick a relation to isolate "
                "it.")
        # CSS-only zoom (C26): radio inputs + sibling selectors — zero JS. The inputs
        # must be direct siblings of .graphwrap for `:checked ~ .graphwrap` to apply.
        zoom = "".join(
            f'<input type="radio" name="gz" id="gz-{z}" class="gz"{chk}>'
            f'<label for="gz-{z}" class="gzl">{lbl}</label>'
            for z, lbl, chk in (("fit", "Fit all", " checked"), ("2", "2×", ""),
                                ("4", "4×", ""), ("8", "8×", "")))
        rels = _rel_filter("gr", (r for _f, _t, r in edges))
        parts.append(
            f"<details><summary>Relations graph ({len(connected)} connected, "
            f"{len(isolated)} isolated, {len(edges)} edges)</summary>"
            f'<p class="lead">{hint} Zoom: Fit shows every node; 2×–8× pan inside '
            f"the frame.</p>{zoom}<br>{rels}"
            f'<div class="graphwrap">{svg}</div></details>')
    else:
        parts.append('<p class="empty">No trace edges recorded — every entity is '
                     "isolated (see the fold below).</p>")
    if isolated:
        # Plan 028 (C34 §5.2): "1,699 isolated" is a number; the per-family breakdown
        # is information — and an isolated REQUIREMENT is a coverage hole, not noise:
        # it sorts first and gets the ⚠ prefix.
        order = {t: i for i, t in enumerate(ENTITY_TABLES)}
        counts: dict[str, int] = {}
        for _nid, fam in isolated:
            counts[fam] = counts.get(fam, 0) + 1
        breakdown = ", ".join(
            f"{fam} {n}" for fam, n in
            sorted(counts.items(), key=lambda kv: (order.get(kv[0], 99), kv[0])))
        req_n = counts.get("requirement", 0)
        warn = f"⚠ {req_n} requirement(s) — " if req_n else ""
        iso_sorted = sorted(isolated, key=lambda n: (n[1] != "requirement",
                                                     order.get(n[1], 99), n[1], n[0]))
        parts.append(_fold(
            f"Isolated entities (no trace edges) — {warn}{breakdown}",
            len(isolated), _table(["id", "family"], iso_sorted)))
    return "".join(parts)


# ------------------------------------------------------------------ traceability flow
# Plan 027 (maintainer decision: BOTH views — flow primary, circle overview): layered
# left-to-right lanes matching how a package is read. Same doctrine: deterministic
# geometry, esc() everywhere, zero JS, fragment links only.
_LANES = [
    ("Needs", ("requirement", "constraint", "invariant", "assumption")),
    ("Decisions", ("decision", "adr", "open-question")),
    ("Work", ("phase", "milestone", "slice", "wbs-item", "execution-plan",
              "defect", "deferred-work")),
    ("Verification", ("test", "acceptance-criterion", "experiment", "poc")),
    ("Risks & measures", ("risk", "kpi", "lesson", "skill")),
]
_LANE_W = 240   # px per lane
_ROW_H = 16    # px per node row


def _flow(conn, gates, ready):
    nodes = conn.execute(
        "SELECT id, entity_type FROM entity_index ORDER BY id").fetchall()
    edges = conn.execute("SELECT from_id, to_id, relation FROM trace_edges"
                         " ORDER BY from_id, to_id, relation").fetchall()
    linked = {f for f, _t, _r in edges} | {t for _f, t, _r in edges}
    connected = [(nid, fam) for nid, fam in nodes if nid in linked]
    if not connected:
        return '<p class="empty">No trace edges recorded — nothing flows yet.</p>'
    if len(connected) > _G_AGG_LIMIT:
        return (f'<p class="empty">{len(connected)} connected entities exceed the '
                "labeled-flow limit — use the aggregate relations graph below.</p>")
    lane_of = {fam: i for i, (_t, fams) in enumerate(_LANES) for fam in fams}
    order = {t: i for i, t in enumerate(ENTITY_TABLES)}
    lanes: list[list[tuple[str, str]]] = [[] for _ in range(len(_LANES) + 1)]
    for nid, fam in sorted(connected,
                           key=lambda n: (order.get(n[1], 99), n[1], n[0])):
        lanes[lane_of.get(fam, len(_LANES))].append((nid, fam))
    titles = [t for t, _f in _LANES] + ["Other"]
    live = [(titles[i], lane) for i, lane in enumerate(lanes) if lane]
    fam_index = {fam: fi for fi, (fam, _ids) in
                 enumerate(_grouped_nodes(connected))}
    pos: dict[str, tuple[float, float, int]] = {}
    header_parts = []
    placed: list[tuple[str, str]] = []
    for li, (title, lane) in enumerate(live):
        x = 40.0 + li * _LANE_W
        header_parts.append(f'<text x="{x:.1f}" y="14" class="lane">'
                            f"{esc(title)} ({len(lane)})</text>")
        for row, (nid, fam) in enumerate(lane):
            pos[nid] = (x, 34.0 + row * _ROW_H, li)
            placed.append((nid, fam))
    edge_parts = []
    incident: dict[str, list[str]] = {}
    for f, t, rel in edges:
        if f not in pos or t not in pos:
            continue
        x1, y1, l1 = pos[f]
        x2, y2, l2 = pos[t]
        if l1 == l2:  # same-lane: bow out to the left of the lane
            d = (f"M{x1 - 6:.1f} {y1:.1f} C{x1 - 40:.1f} {y1:.1f}, "
                 f"{x2 - 40:.1f} {y2:.1f}, {x2 - 6:.1f} {y2:.1f}")
        elif x2 > x1:  # rightward
            d = (f"M{x1 + 6:.1f} {y1:.1f} C{x1 + 90:.1f} {y1:.1f}, "
                 f"{x2 - 90:.1f} {y2:.1f}, {x2 - 6:.1f} {y2:.1f}")
        else:  # leftward
            d = (f"M{x1 - 6:.1f} {y1:.1f} C{x1 - 90:.1f} {y1:.1f}, "
                 f"{x2 + 90:.1f} {y2:.1f}, {x2 + 6:.1f} {y2:.1f}")
        edge_parts.append(f'<path d="{d}" class="e-{esc(rel)}" '
                          f'marker-end="url(#arrowf)">'
                          f"<title>{esc(f)} —{esc(rel)}→ {esc(t)}</title></path>")
        # Plan 028 (C34 §5.1): hidden incident copies power the CSS hover-isolate.
        hl = f'<path d="{d}" class="hl e-{esc(rel)}" marker-end="url(#arrowf)"/>'
        incident.setdefault(f, []).append(hl)
        if t != f:
            incident.setdefault(t, []).append(hl)
    node_parts = []
    for nid, fam in placed:
        x, y, _li = pos[nid]
        fi = fam_index.get(fam, 0)
        ring = " ring" if fi >= 12 else ""
        node_parts.append(
            f'<g class="nod"><a href="#{esc(nid)}">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" '
            f'class="g{fi % 12}{ring}"/><text x="{x + 8:.1f}" y="{y + 3:.1f}">'
            f"{esc(nid)}</text><title>{esc(nid)} ({esc(fam)})</title></a>"
            f'{"".join(incident.get(nid, []))}</g>')
    width = 40 + len(live) * _LANE_W
    height = 50 + max(len(lane) for _t, lane in live) * _ROW_H
    svg = (f'<svg class="graph flow" viewBox="0 0 {width} {height}" '
           f'xmlns="http://www.w3.org/2000/svg">{_marker("arrowf")}'
           f'<g class="edges">{"".join(edge_parts)}</g>'
           f'<g class="nodes">{"".join(node_parts)}</g>'
           f'<g class="labels">{"".join(header_parts)}</g></svg>')
    rels = _rel_filter("fr", (r for _f, _t, r in edges))
    # Plan 028 (C34 §5.2): unwired requirements are EXACTLY the ones this view cannot
    # draw — say so in the lead instead of letting the picture read rosier than reality.
    iso_reqs = sum(1 for nid, fam in nodes
                   if fam == "requirement" and nid not in linked)
    iso_line = (f' <strong>⚠ {iso_reqs} requirement(s) have no trace edges and are '
                "not drawn — see the isolated fold in the relations graph "
                "section.</strong>" if iso_reqs else "")
    return (f"<details><summary>Traceability flow ({len(connected)} connected, "
            f"{len(edges)} edges)</summary>"
            '<p class="lead">Needs → decisions → work → verification, left to right. '
            "Every node is labeled and clickable; hover a node to isolate its edges; "
            "arrowheads show direction; pick a relation to isolate it. The section "
            f"scrolls vertically.{iso_line}</p>"
            f"{rels}"
            f'<div class="graphwrap">{svg}</div></details>')


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


def _lessons(conn, gates, ready):
    """The lessons working surface (plan 035): the operator's confirmation queue
    first (Proposed rows await the interview), then the Approved register that
    binds sessions (pinned flagged, both impact columns), then closed rows folded
    as evidence. Numeric id ordering (CAST — never string-sort ids)."""
    order = "ORDER BY CAST(SUBSTR(id, 4) AS INTEGER)"
    parts = []
    queue = conn.execute(
        "SELECT id, kind, title, statement, context FROM lessons"
        f" WHERE lifecycle_status = 'Proposed' {order}").fetchall()
    if queue:
        parts.append(_fold("Awaiting operator confirmation (only Approved lessons"
                           " bind sessions)", len(queue),
                           _table(["id", "kind", "title", "statement", "context"],
                                  queue, row_ids=True), anchor="lessons-queue"))
    approved = conn.execute(
        "SELECT id, kind, pinned, title, statement, impact_if_followed,"
        " impact_if_ignored, confirmed_by, confirmed_at FROM lessons"
        f" WHERE lifecycle_status = 'Approved' {order}").fetchall()
    if approved:
        rows = [(lid, kind, "pinned" if pin else "", title, stmt, imf, imi,
                 by, at) for lid, kind, pin, title, stmt, imf, imi, by, at
                in approved]
        parts.append(_fold("Approved (rendered into the CLAUDE.md note — pinned"
                           " always, newest fill the cap)", len(rows),
                           _table(["id", "kind", "pinned", "title", "statement",
                                   "impact if followed", "impact if ignored",
                                   "confirmed by", "confirmed at"], rows,
                                  row_ids=True), anchor="lessons-approved"))
    promoted = conn.execute(
        "SELECT l.id, l.kind, l.title, l.promoted_to, s.name, s.level"
        " FROM lessons l LEFT JOIN skills s ON s.id = l.promoted_to"
        f" WHERE l.lifecycle_status = 'Promoted' {order.replace('id', 'l.id')}"
    ).fetchall()
    if promoted:
        parts.append(_fold("Promoted into skills (graduated from the note —"
                           " the skill file carries the content)", len(promoted),
                           _table(["id", "kind", "title", "skill", "name",
                                   "level"], promoted, row_ids=True),
                           anchor="lessons-promoted"))
    closed = conn.execute(
        "SELECT id, kind, lifecycle_status, title, superseded_by FROM lessons"
        f" WHERE lifecycle_status IN ('Rejected','Superseded','Obsolete') {order}"
    ).fetchall()
    if closed:
        parts.append(_fold("Closed (kept as evidence)", len(closed),
                           _table(["id", "kind", "status", "title",
                                   "superseded by"], closed, row_ids=True)))
    if not parts:
        return '<p class="empty">No lessons recorded yet — execution writes them'\
               ' (born Proposed); the operator confirms.</p>'
    return "".join(parts)


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
        parts.append(_fold(label, len(rows), _table(cols, rows, row_ids=True),
                           anchor=f"reg-{table}", csv=table))
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
    matrix = _fold("Requirement coverage matrix", len(rows),
                   _table(["requirement", "title", "mvp", *_MATRIX_COLUMNS], rows))
    if not edges:
        return matrix + '<p class="empty">No trace edges recorded.</p>'
    return matrix + _fold("All trace edges", len(edges),
                          _table(["from", "relation", "to"],
                                 [(f, r, t) for f, t, r in edges]),
                          csv="trace_edges")


def _execution(conn, gates, ready):
    # Plan 027: v_latest_verdicts (migration 004) orders NUMERICALLY — the old string
    # `ORDER BY av.id DESC` here silently showed a stale verdict as latest once a
    # package crossed 1000 verdict rows (AV-1000 < AV-999 as text).
    acs = conn.execute(
        "SELECT ac.id, ac.title, ac.lifecycle_status, lv.verdict, lv.evidence"
        " FROM acceptance_criteria ac"
        " LEFT JOIN v_latest_verdicts lv ON lv.ac_id = ac.id"
        " ORDER BY ac.id").fetchall()
    ac_rows = [[ac_id, title, lifecycle, verdict or "Pending",
                "evidenced" if evidence else ("narrated" if verdict else ""), evidence]
               for ac_id, title, lifecycle, verdict, evidence in acs]
    parts = [_fold("Acceptance criteria × audit verdicts", len(ac_rows),
                   _table(["ac", "title", "lifecycle", "verdict", "evidence class",
                           "evidence"], ac_rows))
             if ac_rows else
             '<h3>Acceptance criteria × audit verdicts</h3>'
             '<p class="empty">No acceptance criteria recorded.</p>']
    # C31 (threads-continued): gate_run counts verdict ROWS, this table shows one line
    # per CRITERION (latest verdict) — rows >= criteria because supersessions append.
    if ac_rows:
        n_verdicts = conn.execute("SELECT COUNT(*) FROM audit_verdicts").fetchone()[0]
        parts.append(f'<p class="freshness">{n_verdicts} verdict row(s) over '
                     f'{len(ac_rows)} criteria — verdict rows ≥ criteria because '
                     'corrections and re-verdicts APPEND (gate_run counts rows; this '
                     'table shows each criterion&#8217;s latest).</p>')
    entries = conn.execute(
        "SELECT id, occurred_at, event_type, entry, subject_id, actor, corrects,"
        " phase_id, slice_id FROM progress_entries ORDER BY id").fetchall()
    parts.append(_fold("Progress log (typed events)", len(entries),
                       _table(["id", "occurred at", "event", "entry", "subject",
                               "actor", "corrects", "phase", "slice"], entries))
                 if entries else
                 '<h3>Progress log</h3><p class="empty">No progress entries recorded.</p>')
    changes = conn.execute(
        "SELECT id, iteration, lifecycle_status, decision_ref, description"
        " FROM scope_changes ORDER BY id").fetchall()
    parts.append(_fold("Scope changes (Proposed → Approved → Merged)", len(changes),
                       _table(["id", "iteration", "lifecycle", "authorized by",
                               "description"], changes))
                 if changes else
                 '<h3>Scope changes</h3><p class="empty">No scope changes recorded.</p>')
    waivers = conn.execute(
        "SELECT id, rule, applies_to, justification, approver, expires FROM waivers"
        " ORDER BY id").fetchall()
    if waivers:
        parts.append(_fold("Readiness waivers (operator-approved; expiring)",
                           len(waivers),
                           _table(["waiver", "rule", "applies to", "justification",
                                   "approver", "expires"],
                                  [[w, r, a or "(whole rule)", j, ap, e or "(close-out)"]
                                   for w, r, a, j, ap, e in waivers])))
    # Plan 027: per-phase readiness panel — v_phase_exit (latest-verdict semantics) +
    # declared human gates. The full rule report is `readiness_check` (the tool).
    exits = conn.execute(
        "SELECT phase_id, title, acs_met, acs_total, open_defects FROM v_phase_exit"
        " ORDER BY phase_id").fetchall()
    if exits:
        rows = [[pid, title, f"{met}/{total}" if total else "—", defects,
                 "ready" if (total and met == total and not defects) else "not ready"]
                for pid, title, met, total, defects in exits]
        parts.append(_fold("Phase readiness (ACs latest-Met / open defects)",
                           len(rows),
                           _table(["phase", "title", "ACs met", "open defects",
                                   "exit"], rows)))
        parts.append('<p class="freshness">latest-verdict semantics — an old Met never '
                     'survives a newer Not-met; the full rule report (risks, decisions, '
                     'deferred work) is <code>readiness_check</code>.</p>')
    slice_exits = conn.execute(
        "SELECT slice_id, title, phase_id, acs_met, acs_total, wbs_open, open_defects"
        " FROM v_slice_exit ORDER BY slice_id").fetchall()
    if slice_exits:
        rows = [[sid, title, pid, f"{met}/{total}" if total else "—", wbs, defects,
                 "ready" if (total and met == total and not wbs and not defects)
                 else "not ready"]
                for sid, title, pid, met, total, wbs, defects in slice_exits]
        parts.append(_fold("Slice readiness (ACs latest-Met / open work incl. Review /"
                           " open defects)", len(rows),
                           _table(["slice", "title", "phase", "ACs met", "open work",
                                   "open defects", "exit"], rows)))
    # v4: all four gate kinds surface ('ready' was silently dropped through v3) plus
    # the latest Go/Hold/Redirect/Kill outcome.
    gates_h = conn.execute(
        "SELECT id, gate_kind, applies_to, definition, outcome FROM execution_gates"
        " ORDER BY id").fetchall()
    if gates_h:
        parts.append(_fold("Declared human gates (confirm + record via "
                           "progress_update)", len(gates_h),
                           _table(["gate", "kind", "applies to", "definition",
                                   "outcome"],
                                  [[g, k, a or "(package)", d, o or "—"]
                                   for g, k, a, d, o in gates_h])))
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
# Order (C25, maintainer decision): State → Relations → Data — related sections adjacent;
# raw registers last, warnings at the end.
SECTIONS = [
    ("overview", "Overview", _overview),
    ("flow", "Traceability flow", _flow),
    ("graph", "Relations graph", _graph),
    ("traceability", "Traceability", _traceability),
    ("execution", "Execution progress", _execution),
    ("lessons", "Lessons", _lessons),
    ("registers", "Registers", _registers),
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
    # C18: sticky in-page navigation. These are the ONLY anchors in the export — all
    # code-derived fragment links (W-V2-6 bans data-derived links, and the hostile-content
    # test pins "every href is a #fragment").
    toc = '<nav class="toc">' + "".join(
        f'<a href="#{anchor}">{esc(title)}</a>' for anchor, title, _fn in SECTIONS
    ) + "</nav>"
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta http-equiv="Content-Security-Policy" content="{_CSP}">\n'
            f"<title>{esc(name)} — Tamheed review</title>\n<style>\n{css}</style>\n"
            f"</head>\n<body>\n<h1>{esc(name)} — Tamheed review surface</h1>\n"
            f"{toc}\n{sections}\n</body>\n</html>\n")
