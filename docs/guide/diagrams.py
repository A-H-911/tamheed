"""Inline-SVG diagrams for the guide, drawn from small layout models.

Each diagram is a model: nodes placed on a grid, edges between node anchors, and labels that
are content ids resolved per language. `svg()` renders the model twice at build time: once as
drawn and once mirrored (x -> W - x - w) for the right-to-left copy, so flow direction follows
the reading direction while text, numbers and marks stay upright. No scripts inside the SVG;
interactivity hangs off data-key / data-step attributes the page script reads.

Drawing rules (plan 175, the operator's bar): an edge leaves its source perpendicular to the
side it starts on and enters its target perpendicular to the side it ends on, so every
arrowhead sits on a box border; edges that would share a run are given their own anchors
(`offset`) or waypoints (`via`); labels sit beside the longest segment with a halo and never
over a box. `lint()` checks all of it on both copies and the build fails on a violation.
"""
from __future__ import annotations

import re
from html import escape as esc

# Every content id a diagram label uses (the build adds these to the required ids).
DIAGRAM_LABELS: list[str] = []


def _L(key: str) -> str:
    cid = f"dia.{key}"
    if cid not in DIAGRAM_LABELS:
        DIAGRAM_LABELS.append(cid)
    return cid


def node(key, x, y, w, h, label, cls="", mono=False, step=None, group="", links="", detail=None,
         line_keys=None, small=False, keyed=True):
    """A box (w,h > 0), a text-only label (cls contains 'bare') or a junction point (w = h = 0)."""
    return {"key": key, "x": x, "y": y, "w": w, "h": h, "label": label, "cls": cls, "mono": mono,
            "step": step, "group": group, "links": links, "detail": detail,
            "line_keys": line_keys, "small": small, "keyed": keyed}


def frame(key, x, y, w, h, label, members):
    """A region (plan 201, G17): a dashed box drawn behind the edges with a short title at its
    top-left. Never a click target. The lint checks it stays on the canvas and that every member
    node lies inside it; it is not an object edges must avoid."""
    return {"key": key, "x": x, "y": y, "w": w, "h": h, "label": label, "members": list(members)}


def edge(frm, to, label=None, cls="", key="", step=None, draw=True, side=None, bend=0, via=None,
         offset=(0, 0), arrow=True, label_at=None, bus=""):
    """`side` = (source side, target side) in l/r/t/b; `offset` shifts each anchor along its side;
    `via` lists absolute waypoints (pre-mirroring); `label_at` = (x, y, anchor) pre-mirroring;
    edges sharing a `bus` may run over each other (a trunk drawn as several arrows)."""
    return {"from": frm, "to": to, "label": label, "cls": cls, "key": key, "step": step,
            "draw": draw, "side": side, "bend": bend, "via": via or [], "offset": offset,
            "arrow": arrow, "label_at": label_at, "bus": bus}


# ----------------------------------------------------------------------------- geometry

def _mx(x, rtl, W):
    return W - x if rtl else x


def _rect(n, rtl, W):
    x = W - n["x"] - n["w"] if rtl else n["x"]
    return x, n["y"], n["w"], n["h"]


def _anchor(n, side, rtl, W, off=0):
    x, y, w, h = _rect(n, rtl, W)
    if rtl and side in ("l", "r"):
        side = "r" if side == "l" else "l"
    dx = -off if rtl else off
    return {"l": (x, y + h / 2 + off), "r": (x + w, y + h / 2 + off),
            "t": (x + w / 2 + dx, y), "b": (x + w / 2 + dx, y + h)}[side]


def _sides(a, b):
    """Pick the facing sides of two nodes from their relative position (pre-mirroring)."""
    ax, ay = a["x"] + a["w"] / 2, a["y"] + a["h"] / 2
    bx, by = b["x"] + b["w"] / 2, b["y"] + b["h"] / 2
    if abs(bx - ax) >= abs(by - ay):
        return ("r", "l") if bx > ax else ("l", "r")
    return ("b", "t") if by > ay else ("t", "b")


def _route(p1, sa, p2, sb, via):
    """Orthogonal polyline from p1 (leaving side sa) to p2 (entering side sb)."""
    x1, y1 = p1
    x2, y2 = p2
    if via:
        return [p1, *via, p2]
    horiz_a, horiz_b = sa in ("l", "r"), sb in ("l", "r")
    if horiz_a and horiz_b:
        if abs(y1 - y2) < 0.5:
            return [p1, p2]
        mx = (x1 + x2) / 2
        return [p1, (mx, y1), (mx, y2), p2]
    if not horiz_a and not horiz_b:
        if abs(x1 - x2) < 0.5:
            return [p1, p2]
        my = (y1 + y2) / 2
        return [p1, (x1, my), (x2, my), p2]
    if horiz_a:                        # leave horizontally, enter vertically
        return [p1, (x2, y1), p2]
    return [p1, (x1, y2), p2]          # leave vertically, enter horizontally


def _curve(p1, sa, p2, bend, rtl):
    x1, y1 = p1
    x2, y2 = p2
    if sa in ("t", "b"):
        c1, c2 = (x1, y1 + bend), (x2, y2 + bend)
    else:
        bx = -bend if rtl else bend
        c1, c2 = (x1 + bx, y1), (x2 + bx, y2)
    return c1, c2


def _bezier(p0, c1, c2, p3, t):
    u = 1 - t
    return (u * u * u * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * p3[0],
            u * u * u * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * p3[1])


def _path_d(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def _label_pos(pts, curve, rtl):
    """Default label spot: beside the longest segment (above a horizontal one, next to a
    vertical one) or above/below a curve's apex. Returns (x, y, anchor)."""
    if curve:
        p0, c1, c2, p3, bend = curve
        ax, ay = _bezier(p0, c1, c2, p3, 0.5)
        return ax, ay + (-12 if bend < 0 else 12), "middle"
    best, blen = None, -1
    for a, b in zip(pts, pts[1:]):
        length = abs(b[0] - a[0]) + abs(b[1] - a[1])
        if length > blen:
            best, blen = (a, b), length
    (ax, ay), (bx, by) = best
    if abs(ay - by) < 0.5:                       # horizontal
        return (ax + bx) / 2, ay - 10, "middle"
    x = ax + (-7 if rtl else 7)                  # vertical: beside it, reading-side
    return x, (ay + by) / 2, "start"            # RTL copies inherit direction:rtl, so start = the right edge


_LATIN_RUN = re.compile(r"[A-Za-z0-9_/:\-.=*@#'\"]+(?: [A-Za-z0-9_/:\-.=*@#'\"·]+)*")   # a middle-dot list stays one run


def _isolate_latin(line: str) -> str:
    """Plan 203: in a right-to-left copy a Latin token keeps its own order (a command, a flag, a
    tool name) by a left-to-right isolate around every Latin run; brackets stay outside it."""
    return _LATIN_RUN.sub(lambda m: "⁦" + m.group(0) + "⁩", line)


def _text(lines, x, y, rtl, cls, anchor="middle", lh=14, keys=None):
    out = []
    n = len(lines)
    y0 = y - (n - 1) * lh / 2
    if rtl:
        lines = [_isolate_latin(l) for l in lines]
    for i, line in enumerate(lines):
        extra = ' style="direction:ltr;unicode-bidi:isolate"' if cls and "num" in cls else ""
        key = f' data-key="{esc(keys[i])}"' if keys else ""
        out.append(f'<text class="lbl {cls}" x="{x:.1f}" y="{y0 + i * lh:.1f}" text-anchor="{anchor}"'
                   f' dominant-baseline="middle"{extra}{key}>{esc(line)}</text>')
    return "".join(out)


def _edge_geometry(model, e, rtl):
    """Resolved endpoints, sides, polyline (or curve) of one edge on one copy."""
    W = model["w"]
    nodes = {n["key"]: n for n in model["nodes"]}
    a, b = nodes[e["from"]], nodes[e["to"]]
    sa, sb = e["side"] or _sides(a, b)
    oa, ob = e["offset"]
    p1 = _anchor(a, sa, rtl, W, oa)
    p2 = _anchor(b, sb, rtl, W, ob)
    if e["bend"]:
        c1, c2 = _curve(p1, sa, p2, e["bend"], rtl)
        return p1, p2, sa, sb, None, (p1, c1, c2, p2, e["bend"])
    via = [(_mx(x, rtl, W), y) for x, y in e["via"]]
    return p1, p2, sa, sb, _route(p1, sa, p2, sb, via), None


def _flip(anchor, rtl):
    """The RTL copy inherits `direction: rtl`, under which text-anchor start/end already
    swap sides; mirroring the x alone mirrors the label, so the keyword is kept."""
    return anchor


# ----------------------------------------------------------------------------- rendering

def svg(model, rtl: bool, lang: str, resolve, title: str) -> str:
    """Render one copy. `resolve(cid) -> str` returns the label text in `lang`."""
    W, H = model["w"], model["h"]
    sfx = f"{model['id']}-{lang}"
    parts = [f'<svg class="dia" lang="{lang}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}" xmlns="http://www.w3.org/2000/svg">',
             f'<defs><marker id="ar-{sfx}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="arrow"/></marker>'
             f'<marker id="ara-{sfx}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="arrow acc"/></marker></defs>']
    for fr in model.get("frames", []):
        x, y, w, h = _rect(fr, rtl, W)
        tx = _mx(fr["x"] + 10, rtl, W)
        parts.append(f'<g class="frame"><rect class="box frame" x="{x:.1f}" y="{y}" width="{w}" height="{h}" rx="8"/>'
                     + _text([resolve(fr["label"])], tx, y + 13, rtl, "small", _flip("start", rtl)) + "</g>")
    for e in model.get("edges", []):
        p1, p2, sa, sb, pts, curve = _edge_geometry(model, e, rtl)
        marker = "ara" if "acc" in e["cls"] else "ar"
        attrs = [f'class="edge {e["cls"]}{" draw" if e["draw"] else ""}{" step" if e["step"] else ""}"']
        if e["arrow"]:
            attrs.append(f'marker-end="url(#{marker}-{sfx})"')
        if e["key"]:
            attrs.append(f'data-key="{esc(e["key"])}"')
        if e["step"]:
            attrs.append(f'data-step="{e["step"]}"')
        if curve:
            p0, c1, c2, p3, _bend = curve
            d = (f"M{p0[0]:.1f} {p0[1]:.1f} C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f}"
                 f" {p3[0]:.1f} {p3[1]:.1f}")
        else:
            d = _path_d(pts)
        parts.append(f'<path {" ".join(attrs)} d="{d}"/>')
        if e["label"]:
            if e["label_at"]:
                lx, ly, anchor = e["label_at"]
                lx, anchor = _mx(lx, rtl, W), _flip(anchor, rtl)
            else:
                lx, ly, anchor = _label_pos(pts, curve, rtl)
            parts.append(_text([resolve(e["label"])], lx, ly, rtl, "small", anchor))
    for n in model["nodes"]:
        x, y, w, h = _rect(n, rtl, W)
        if w == 0 and h == 0:
            continue                                   # a junction point
        attrs = []
        if n["key"] and n["keyed"]:          # a matrix cell is keyed by its text lines, not its box
            attrs.append(f'data-key="{esc(n["key"])}"')
        if n["group"]:
            attrs.append(f'data-group="{esc(n["group"])}"')
        if n["links"]:
            attrs.append(f'data-links="{esc(n["links"])}"')
        if n["step"]:
            attrs.append(f'class="step" data-step="{n["step"]}"')
        parts.append(f'<g {" ".join(attrs)}>')
        if "bare" not in n["cls"]:
            rx = h / 2 if "pill" in n["cls"] else 6
            parts.append(f'<rect class="box {n["cls"]}" x="{x:.1f}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')
        label = n["label"]
        lines = label if isinstance(label, list) else resolve(label).split("\n")
        cls = "num" if n["mono"] else ("strong" if "strong" in n["cls"] else "")
        if n["small"]:
            cls = (cls + " small").strip()
        lh = 12 if n["small"] else 14
        parts.append(_text(lines, x + w / 2, y + h / 2, rtl, cls, lh=lh, keys=n["line_keys"]))
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


# ----------------------------------------------------------------------------- the lint

def _text_width(s: str, px: float) -> float:
    return len(s) * px * 0.55 + 4


def _inside(p, r, tol=0.6):
    x, y, w, h = r
    return (x + tol) < p[0] < (x + w - tol) and (y + tol) < p[1] < (y + h - tol)


def _on_border(p, r, tol=0.6):
    x, y, w, h = r
    on_v = (abs(p[0] - x) <= tol or abs(p[0] - (x + w)) <= tol) and y - tol <= p[1] <= y + h + tol
    on_h = (abs(p[1] - y) <= tol or abs(p[1] - (y + h)) <= tol) and x - tol <= p[0] <= x + w + tol
    return on_v or on_h


def _samples(pts, curve, step=3.0):
    if curve:
        p0, c1, c2, p3, _b = curve
        return [_bezier(p0, c1, c2, p3, i / 60) for i in range(61)]
    out = []
    for a, b in zip(pts, pts[1:]):
        length = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
        n = max(1, int(length / step))
        for i in range(n + 1):
            t = i / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def _seg_cross(a, b, c, d):
    """True when segments ab and cd properly cross (interior intersection), or overlap
    collinearly for more than a point."""
    def orient(p, q, r):
        v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return 0 if abs(v) < 1e-6 else (1 if v > 0 else -1)
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    if o1 and o2 and o3 and o4 and o1 != o2 and o3 != o4:
        return True
    if o1 == o2 == o3 == o4 == 0:                   # collinear: overlapping length?
        if abs(a[0] - b[0]) >= abs(a[1] - b[1]):
            lo, hi = sorted((a[0], b[0])), sorted((c[0], d[0]))
        else:
            lo, hi = sorted((a[1], b[1])), sorted((c[1], d[1]))
        return min(lo[1], hi[1]) - max(lo[0], hi[0]) > 1.0
    return False


def _boxes_touch(a, b, pad=0.0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax - pad < bx + bw and bx - pad < ax + aw and ay - pad < by + bh and by - pad < ay + ah


def lint(model, rtl: bool, resolve) -> list[str]:
    """Every defect class the review found, as a mechanical check on one rendered copy."""
    W, H = model["w"], model["h"]
    problems = []
    nodes = {n["key"]: n for n in model["nodes"]}
    rects = {n["key"]: _rect(n, rtl, W) for n in model["nodes"] if n["w"] or n["h"]}
    label_boxes: list[tuple[str, tuple]] = []
    for n in model["nodes"]:
        x, y, w, h = _rect(n, rtl, W)
        if x < -0.1 or y < -0.1 or x + w > W + 0.1 or y + h > H + 0.1:
            problems.append(f"{model['id']}: node {n['key']} leaves the canvas")
    for fr in model.get("frames", []):
        fx, fy, fw, fh = _rect(fr, rtl, W)
        if fx < -0.1 or fy < -0.1 or fx + fw > W + 0.1 or fy + fh > H + 0.1:
            problems.append(f"{model['id']}: frame {fr['key']} leaves the canvas")
        for m in fr["members"]:
            if m not in rects:
                problems.append(f"{model['id']}: frame {fr['key']} names no node {m}")
                continue
            mx, my, mw, mh = rects[m]
            if mx < fx or my < fy or mx + mw > fx + fw or my + mh > fy + fh:
                problems.append(f"{model['id']}: node {m} lies outside its frame {fr['key']}")
    segs: list[tuple[str, tuple, tuple, str]] = []
    for e in model.get("edges", []):
        p1, p2, sa, sb, pts, curve = _edge_geometry(model, e, rtl)
        name = e["key"] or f"{e['from']}->{e['to']}"
        for p, k in ((p1, e["from"]), (p2, e["to"])):
            if k in rects and not _on_border(p, rects[k]):
                problems.append(f"{model['id']}: edge {name} does not meet the border of {k}")
        samples = _samples(pts, curve)
        for p in samples[2:-2]:
            for k, r in rects.items():
                if _inside(p, r, 1.0):
                    problems.append(f"{model['id']}: edge {name} crosses box {k}")
                    break
            if any(f"edge {name} crosses box" in s for s in problems[-1:]):
                break
        if curve:
            poly = samples
        else:
            poly = pts
        for a, b in zip(poly, poly[1:]):
            segs.append((name, a, b, e["bus"]))
        if e["label"]:
            if e["label_at"]:
                lx, ly, anchor = e["label_at"]
                lx, anchor = _mx(lx, rtl, W), _flip(anchor, rtl)
            else:
                lx, ly, anchor = _label_pos(pts, curve, rtl)
            tw = _text_width(resolve(e["label"]), 10.5)
            bx = _label_left(lx, tw, anchor, rtl)
            label_boxes.append((name, (bx, ly - 6, tw, 12)))
    for i, (n1, a1, b1, bus1) in enumerate(segs):
        for n2, a2, b2, bus2 in segs[i + 1:]:
            if n1 == n2 or (bus1 and bus1 == bus2):
                continue
            if _seg_cross(a1, b1, a2, b2):
                problems.append(f"{model['id']}: edges {n1} and {n2} cross")
    for name, box in label_boxes:
        bx, by, bw, bh = box
        if bx < 0 or by < 0 or bx + bw > W or by + bh > H:
            problems.append(f"{model['id']}: label of {name} leaves the canvas")
        for k, r in rects.items():
            if _boxes_touch(box, r, pad=1.0):
                problems.append(f"{model['id']}: label of {name} touches box {k}")
        for n2, a, b, _bus in segs:
            if n2 == name:
                continue
            if _box_hits_seg(box, a, b):
                problems.append(f"{model['id']}: label of {name} lies on edge {n2}")
    for i, (n1, b1) in enumerate(label_boxes):
        for n2, b2 in label_boxes[i + 1:]:
            if _boxes_touch(b1, b2):
                problems.append(f"{model['id']}: labels of {n1} and {n2} overlap")
    return sorted(set(problems))


def _label_left(lx, tw, anchor, rtl):
    """Left edge of a label's box: under direction:rtl, start is the RIGHT edge."""
    if anchor == "middle":
        return lx - tw / 2
    starts_at_x = (anchor == "start") != rtl
    return lx if starts_at_x else lx - tw


def _box_hits_seg(box, a, b):
    x, y, w, h = box
    for p in _samples([a, b], None, 2.0):
        if x < p[0] < x + w and y < p[1] < y + h:
            return True
    return False


# ----------------------------------------------------------------------------- models

def overview(f) -> dict:
    """D1 — one agent, two halves (G1): the operator on top; one frame, Claude Code + Tamheed,
    with the planning lane (stages 1-20) and the execution lane (stages 21-22) and the handoff
    between them; the MCP server and the package below, the one write path; the review page."""
    ns = [
        node("op", 270, 10, 360, 40, _L("overview.operator"), "acc strong pill"),
        node("plan", 40, 112, 360, 96, _L("overview.planning"), "strong"),
        node("exec", 500, 112, 360, 96, _L("overview.execution"), "strong"),
        node("server", 330, 272, 240, 44, _L("overview.server"), "acc"),
        node("pkg", 640, 268, 150, 52, _L("overview.package"), ""),
        node("review", 800, 272, 90, 44, _L("overview.review"), ""),
    ]
    frs = [frame("agent", 20, 78, 860, 150, _L("frame.agent"), ["plan", "exec"])]
    es = [
        edge("op", "plan", _L("overview.brief"), "", side=("b", "t"), offset=(-110, 0), label_at=(300, 70, "end")),
        edge("op", "exec", _L("overview.approvals"), "", side=("b", "t"), offset=(110, 0), label_at=(600, 70, "start")),
        edge("plan", "exec", _L("overview.handoff"), "acc", side=("r", "l"), label_at=(450, 150, "middle")),
        edge("plan", "server", _L("overview.writes"), "", side=("b", "t"), offset=(0, -70), label_at=(210, 232, "end")),
        edge("exec", "server", _L("overview.records"), "", side=("b", "t"), offset=(0, 70), label_at=(690, 232, "start")),
        edge("server", "pkg", _L("overview.path"), "acc", side=("r", "l"), label_at=(605, 334, "middle")),
        edge("pkg", "review", _L("overview.export"), "", side=("r", "l"), label_at=(845, 334, "middle")),
    ]
    return {"id": "d1", "w": 900, "h": 352, "nodes": ns, "edges": es, "frames": frs}


def actors(f) -> dict:
    """D2 — the operator and the agent's two halves (G1, G16), what each may do; click a party to
    isolate its part. The frame holds both lanes and their tool pills."""
    ns = [
        node("op", 270, 10, 220, 44, _L("actors.operator"), "acc strong", group="op"),
        node("op-does", 510, 12, 300, 40, _L("actors.operator.does"), "pill", group="op", links="op"),
        node("plan", 40, 118, 360, 46, _L("actors.planner"), "strong", group="plan"),
        node("exec", 500, 118, 360, 46, _L("actors.executor"), "strong", group="exec"),
        node("plan-does", 40, 190, 360, 70, _L("actors.planner.does"), "pill", group="plan", links="plan"),
        node("exec-does", 500, 190, 360, 70, _L("actors.executor.does"), "pill", group="exec", links="exec"),
        node("store", 330, 320, 240, 44, _L("actors.store"), "", group="store"),
    ]
    frs = [frame("agent", 20, 84, 860, 196, _L("frame.agent"), ["plan", "exec", "plan-does", "exec-does"])]
    es = [
        edge("op", "plan", _L("actors.brief"), side=("b", "t"), offset=(-60, 0), label_at=(300, 70, "end")),
        edge("op", "exec", _L("actors.approves"), side=("b", "t"), offset=(60, 0), label_at=(460, 70, "start")),
        edge("plan", "exec", _L("actors.handoff"), "acc", side=("r", "l"), label_at=(450, 131, "middle")),
        edge("plan-does", "store", None, "", side=("b", "l")),
        edge("exec-does", "store", None, "", side=("b", "r")),
    ]
    return {"id": "d2", "w": 900, "h": 390, "nodes": ns, "edges": es, "frames": frs}


def stage_track(f) -> dict:
    """D3 — the 22 stages in three lanes; human points and the loop-backs."""
    st = f["stages"]
    human = set(st["human"])
    loops = set(st["loops"])
    ns, es = [], []
    lane_y = {"A": 54, "B": 134, "C": 214}
    for p in st["phases"]:
        y = lane_y[p["letter"]]
        ns.append(node(f"phase-{p['letter']}", 10, y - 14, 92, 44, f"phase.{p['letter']}", "acc pill"))
        for i, n in enumerate(p["stages"]):
            x = 120 + i * 78
            cls = "good" if n in human else ""
            ns.append(node(f"s{n}", x, y, 56, 24, [str(n)], cls + " pill", mono=True,
                            detail=f"stage.{n:02d}"))
            if i:
                es.append(edge(f"s{p['stages'][i - 1]}", f"s{n}", side=("r", "l")))
    es.append(edge("s8", "s9", "", "", side=("b", "t"), via=[(694, 90), (134, 90)], offset=(0, -14)))
    es.append(edge("s15", "s16", "", "", side=("b", "t"), via=[(616, 170), (134, 170)], offset=(0, -14)))
    # plan 202 (G5): a loop-back is an orthogonal dashed return in a channel 18 px above its lane,
    # landing on the lane's first pill from the top. s9 and s16 already receive the phase-crossing
    # drop at centre - 14, so the return lands at centre + 14; s1 has no other arrival.
    lane_start = {n: p["stages"][0] for p in st["phases"] for n in p["stages"]}
    lane_of = {n: p["letter"] for p in st["phases"] for n in p["stages"]}
    idx = {n: i for p in st["phases"] for i, n in enumerate(p["stages"])}
    for n in sorted(loops):
        s0 = lane_start[n]
        ch = lane_y[lane_of[n]] - 18
        t_off = 0 if s0 == 1 else 14
        x_from = 120 + idx[n] * 78 + 28
        x_to = 120 + idx[s0] * 78 + 28 + t_off
        es.append(edge(f"s{n}", f"s{s0}", None, "loop", draw=False, side=("t", "t"),
                       via=[(x_from, ch), (x_to, ch)], offset=(0, t_off)))
    ns.append(node("legend-l", 360, 256, 190, 24, _L("stages.legend.loop"), "pill"))
    ns.append(node("legend-h", 560, 256, 190, 24, _L("stages.legend.human"), "good pill"))
    return {"id": "d3", "w": 760, "h": 294, "nodes": ns, "edges": es}


def package_tree(f) -> dict:
    """D4 — a package on disk, the one path that changes data/, and the target repo it wires."""
    ns = [
        node("tools", 240, 6, 190, 34, _L("package.tools"), "pill"),
        node("root", 10, 76, 150, 36, _L("package.root"), "acc strong"),
        node("data", 240, 70, 190, 48, _L("package.data"), "", links="write"),
        node("readme", 240, 132, 190, 48, _L("package.readme"), ""),
        node("review", 240, 194, 190, 48, _L("package.review"), ""),
        node("exports", 240, 256, 190, 48, _L("package.exports"), ""),
        node("csv", 240, 318, 190, 36, _L("package.csv"), ""),
        node("target", 480, 20, 150, 36, _L("package.target"), "strong"),
        node("mcp", 480, 80, 270, 40, _L("package.mcp"), ""),
        node("claude", 480, 134, 270, 48, _L("package.claude"), ""),
    ]
    es = [
        edge("root", "data", side=("r", "l"), bus="tree"), edge("root", "readme", side=("r", "l"), bus="tree"),
        edge("root", "review", side=("r", "l"), bus="tree"), edge("root", "exports", side=("r", "l"), bus="tree"),
        edge("root", "csv", side=("r", "l"), bus="tree"),
        edge("tools", "data", _L("package.flush"), "acc", side=("b", "t"), label_at=(327, 55, "end")),
        edge("target", "mcp", side=("l", "l"), via=[(460, 38), (460, 100)], bus="target"),
        edge("target", "claude", side=("l", "l"), via=[(460, 38), (460, 158)], bus="target"),
    ]
    return {"id": "d4", "w": 760, "h": 364, "nodes": ns, "edges": es}


BUCKETS = [
    ("needs", ("requirement", "constraint", "invariant", "assumption")),
    ("decisions", ("decision", "adr")),
    ("work", ("phase", "slice", "wbs-item", "execution-plan", "defect", "deferred-work")),
    ("verif", ("test", "acceptance-criterion", "experiment", "poc")),
    ("risk", ("risk", "hypothesis", "open-question")),
    ("scope", ("scope-change",)),
    ("lesson", ("lesson",)),
    ("other", ("stakeholder", "kpi", "dependency", "convention", "execution-gate", "progress-entry")),
]


def relation_matrix(f) -> dict[tuple[str, str], list[str]]:
    """(source bucket, target bucket) -> the typed relations the engine allows between them,
    derived from RELATION_RULES through BUCKETS. Every type a rule names must have a bucket."""
    where = {t: b for b, types in BUCKETS for t in types}
    cells: dict[tuple[str, str], list[str]] = {}
    for rel in f["relations"]:
        if rel.get("fallback"):
            continue                                   # relates_to: any pair; the caption says so
        if rel["same_type"]:
            for b, _types in BUCKETS:
                cells.setdefault((b, b), []).append(rel["relation"])
            continue
        missing = [t for t in rel["from"] + rel["to"] if t not in where]
        assert not missing, f"relation {rel['relation']} names types with no bucket: {missing}"
        pairs = sorted({(where[a], where[b]) for a in rel["from"] for b in rel["to"]})
        for pair in pairs:
            cells.setdefault(pair, []).append(rel["relation"])
    return {k: sorted(v) for k, v in cells.items()}


def relations_map(f) -> dict:
    """D5 — the bucket x bucket matrix of legal relation kinds (rows = source, columns = target)."""
    cells = relation_matrix(f)
    names = [b for b, _t in BUCKETS]
    hx, hy, cw, lh = 118, 30, 90, 11
    rows_h = []
    for a in names:
        lines = max([len(cells.get((a, b), [])) for b in names] + [1])
        rows_h.append(max(26, lines * lh + 10))
    ns = [node("corner", 10, 10, hx - 4, hy - 4, _L("relations.corner"), "bare", small=True, keyed=False)]
    x0, y0 = 10 + hx, 10 + hy
    for j, b in enumerate(names):
        ns.append(node(f"col-{b}", x0 + j * cw, 10, cw - 4, hy - 4, _L(f"relations.h.{b}"), "acc pill", keyed=False))
    y = y0
    for i, a in enumerate(names):
        h = rows_h[i]
        ns.append(node(f"row-{a}", 10, y, hx - 4, h - 4, _L(f"relations.h.{a}"), "acc", keyed=False))   # plan 202: a box, not a tall pill
        for j, b in enumerate(names):
            rels = cells.get((a, b), [])
            cls = "cell" if rels else "cell empty"
            ns.append(node(f"c-{a}-{b}", x0 + j * cw, y, cw - 4, h - 4, rels or [""], cls, mono=True,
                            small=True, line_keys=rels or None, keyed=False))
        y += h
    return {"id": "d5", "w": x0 + len(names) * cw + 6, "h": y + 6, "nodes": ns, "edges": []}


def status_machine(f) -> dict:
    """D6 — the standard lifecycle with the Review / Implemented branch."""
    ns = [
        node("Draft", 10, 90, 100, 36, ["Draft"], "pill", mono=True),
        node("Proposed", 150, 90, 100, 36, ["Proposed"], "pill", mono=True),
        node("Approved", 290, 90, 110, 36, ["Approved"], "acc pill", mono=True),
        node("Review", 440, 150, 100, 36, ["Review"], "warn pill", mono=True),
        node("Implemented", 600, 90, 130, 36, ["Implemented"], "good pill", mono=True),
        node("Rejected", 150, 20, 100, 32, ["Rejected"], "bad pill", mono=True),
        node("Deferred", 150, 160, 100, 32, ["Deferred"], "pill", mono=True),
        node("Superseded", 440, 20, 110, 32, ["Superseded"], "pill", mono=True),
        node("Obsolete", 620, 20, 110, 32, ["Obsolete"], "pill", mono=True),
        node("note", 150, 212, 580, 36, _L("status.note"), "pill"),
    ]
    es = [
        edge("Draft", "Proposed", side=("r", "l")), edge("Proposed", "Approved", side=("r", "l")),
        edge("Approved", "Implemented", _L("status.verified"), "acc", side=("r", "l")),
        edge("Approved", "Review", _L("status.claimed"), "", side=("b", "l"), label_at=(353, 140, "start")),
        edge("Review", "Implemented", _L("status.guard"), "acc", side=("r", "b"), label_at=(673, 150, "start")),
        edge("Proposed", "Rejected", side=("t", "b")), edge("Proposed", "Deferred", side=("b", "t")),
        edge("Deferred", "Proposed", side=("l", "l"), bend=-30),
        edge("Approved", "Superseded", side=("t", "b"), offset=(0, -22)),
        edge("Implemented", "Superseded", side=("t", "b"), offset=(0, 22)),
        edge("Superseded", "Obsolete", side=("r", "l")),
    ]
    return {"id": "d6", "w": 790, "h": 260, "nodes": ns, "edges": es}


def guard(f) -> dict:
    """D7 — the guarded transition to Implemented, step by step."""
    ns = [
        node("upsert", 10, 80, 200, 44, _L("guard.upsert"), "pill", step=1),
        node("rules", 240, 60, 170, 84, _L("guard.rules"), "", step=2),
        node("pass", 540, 20, 150, 44, _L("guard.pass"), "good", step=3),
        node("impl", 760, 20, 150, 44, ["Implemented"], "good pill", mono=True, step=3),
        node("fail", 540, 130, 150, 44, _L("guard.fail"), "bad", step=3),
        node("force", 760, 130, 150, 44, _L("guard.force"), "warn pill", step=4),
        node("journal", 760, 215, 160, 44, _L("guard.journal"), "warn", step=5),
    ]
    es = [
        edge("upsert", "rules", step=1, side=("r", "l")),
        edge("rules", "pass", _L("guard.nofail"), "", step=3, side=("r", "l"), label_at=(483, 80, "start"), bus="fork"),
        edge("rules", "fail", _L("guard.blocking"), "", step=3, side=("r", "l"), label_at=(483, 118, "start"), bus="fork"),
        edge("pass", "impl", step=3, side=("r", "l")),
        edge("fail", "force", _L("guard.operator"), "", step=4, side=("r", "l"), label_at=(725, 118, "middle")),
        edge("force", "journal", step=5, side=("b", "t")),
        edge("force", "impl", _L("guard.past"), "acc", step=5, side=("t", "b"), label_at=(827, 97, "end")),
    ]
    return {"id": "d7", "w": 930, "h": 270, "nodes": ns, "edges": es}


def session(f) -> dict:
    """D8 — one session on a package, from the hook to the handoff."""
    ns = [
        node("hook", 10, 30, 210, 48, _L("session.hook"), "acc", step=1),
        node("orient", 270, 30, 210, 48, _L("session.orient"), "", step=2),
        node("work", 530, 30, 210, 48, _L("session.work"), "", step=3),
        node("sync", 530, 130, 210, 48, _L("session.sync"), "", step=4),
        node("handoff", 270, 130, 210, 48, _L("session.handoff"), "acc", step=5),
        node("close", 10, 130, 210, 48, _L("session.close"), "", step=6),
        node("resume", 10, 222, 730, 36, _L("session.resume"), "pill", step=6),
    ]
    es = [
        edge("hook", "orient", step=2, side=("r", "l")), edge("orient", "work", step=3, side=("r", "l")),
        edge("work", "sync", step=4, side=("b", "t")),
        edge("sync", "handoff", _L("session.last"), "acc", step=5, side=("l", "r")),
        edge("handoff", "close", step=6, side=("l", "r")),
        edge("close", "resume", _L("session.next"), "", step=6, side=("b", "t"), offset=(0, -260)),
    ]
    return {"id": "d8", "w": 760, "h": 270, "nodes": ns, "edges": es}


# ----------------------------------------------------------------------------- the file figures

RECIPES = [
    ("new-project", ["tamheed", "entity_upsert", "gate_run", "readiness_check", "handoff_emit"], 6),
    ("intake-only", ["tamheed", "entity_upsert"], 4),
    ("resume", ["package_open", "orient-resume", "gate_run"], 4),
    ("update", ["tamheed", "entity_upsert", "progress_update", "audit_record"], 5),
    ("adopt", ["package_adopt", "gate_run", "readiness_check"], 5),
    ("migrate", ["package_migrate", "package_open", "gate_run"], 5),
    ("upgrade", ["package_close", "server_info", "package_migrate", "handoff_emit", "export_html"], 6),
    ("lock-recovery", ["package_open", "package_unlock"], 4),
    ("semi-auto", ["orient-resume", "slice-kickoff", "progress-sync", "slice-review", "phase-close"], 6),
    ("fully-auto", ["loop-guard", "loop-iteration"], 5),
    ("skill-promote", ["skill-promote", "entity_upsert", "handoff_emit"], 5),
    ("release", ["release-close-out", "readiness_check", "work_bind", "export_html", "package_verify"], 6),
]
LANES = ("operator", "agent", "engine")
LANE_Y = {"operator": 10, "agent": 104, "engine": 198}
# Plan 203 (G12): the party that acts at each step of a recipe, by one rule. An operator's command
# or word is the operator's lane; a tool the agent calls, or a skill it runs, is the agent's; the
# engine's own behaviour (a hook, a refusal, a verdict, a sync) is the engine's.
SWIMLANES = {
    "new-project": ['operator', 'operator', 'operator', 'agent', 'agent', 'operator'],
    "intake-only": ['operator', 'agent', 'agent', 'operator'],
    "resume": ['engine', 'agent', 'engine', 'operator'],
    "update": ['operator', 'agent', 'agent', 'agent', 'operator'],
    "adopt": ['agent', 'operator', 'operator', 'engine', 'operator'],
    "migrate": ['agent', 'operator', 'operator', 'engine', 'engine'],
    "upgrade": ['operator', 'operator', 'agent', 'agent', 'agent', 'agent'],
    "lock-recovery": ['engine', 'operator', 'operator', 'agent'],
    "semi-auto": ['agent', 'agent', 'agent', 'agent', 'operator', 'operator'],
    "fully-auto": ['operator', 'agent', 'engine', 'engine', 'operator'],
    "skill-promote": ['agent', 'operator', 'agent', 'agent', 'operator'],
    "release": ['agent', 'operator', 'engine', 'agent', 'agent', 'operator'],
}


def swimlane(f, slug) -> dict:
    """One recipe as three lanes (the frame primitive), one node per step in the lane of the party
    that acts, the steps linked in order: departures from the right side, arrivals at the top or
    the bottom centre, so no two edges share an anchor and no edge crosses a node."""
    steps = next(s for sl, _names, s in RECIPES if sl == slug)
    lanes = SWIMLANES[slug]
    assert len(lanes) == steps, (slug, len(lanes), steps)
    ns, es = [], []
    col = 860 // steps                       # the columns share the lanes' width: fewer steps, wider boxes
    w = min(col - 8, 200)
    for k, lane in enumerate(lanes, 1):
        cls = {"operator": "acc", "agent": "", "engine": "pill"}[lane]
        ns.append(node(f"s{k}", 30 + (k - 1) * col, LANE_Y[lane] + 30, w, 44, _L(f"wf.{slug}.s{k}"), cls))
    for k in range(1, steps):
        a, b = lanes[k - 1], lanes[k]
        side = ("r", "l") if a == b else (("r", "t") if LANE_Y[b] > LANE_Y[a] else ("r", "b"))
        es.append(edge(f"s{k}", f"s{k + 1}", side=side))
    frs = [frame(f"lane-{lane}", 10, LANE_Y[lane], 880, 86, _L(f"lane.{lane}"),
                 [f"s{k}" for k, ln in enumerate(lanes, 1) if ln == lane]) for lane in LANES]
    return {"id": f"wf-{slug}", "w": 900, "h": 294, "nodes": ns, "edges": es, "frames": frs}


FILE_MODELS = {f"wf-{slug}": (lambda f, s=slug: swimlane(f, s)) for slug in SWIMLANES}


def label_problems(model, resolve) -> list[str]:
    """A file figure renders in fallback fonts with no inline twin to compare against, so every
    node label line must fit its box by the width estimate (plan 203)."""
    out = []
    for n in model["nodes"]:
        if not (n["w"] and n["h"]):
            continue
        lines = n["label"] if isinstance(n["label"], list) else resolve(n["label"]).split("\n")
        px = 13 if "strong" in n["cls"] else (10.5 if n["small"] else 12)
        for line in lines:
            if _text_width(line, px) > n["w"] - 10:
                out.append(f"{model['id']}: label of {n['key']} is wider than its box: {line!r}")
    return out


_FILE_FONTS = {"en": 'Georgia, "Times New Roman", serif', "ar": '"Noto Naskh Arabic", "Segoe UI", Tahoma, serif'}
_FILE_MONO = 'Consolas, Menlo, monospace'


def _mix(a: str, b: str, pct: int) -> str:
    """pct % of colour a over colour b, both #rrggbb (the page uses color-mix, which an SVG
    loaded as an image may not resolve)."""
    ra, ga, ba = (int(a[i:i + 2], 16) for i in (1, 3, 5))
    rb, gb, bb = (int(b[i:i + 2], 16) for i in (1, 3, 5))
    m = lambda x, y: round(x * pct / 100 + y * (100 - pct) / 100)
    return f"#{m(ra, rb):02x}{m(ga, gb):02x}{m(ba, bb):02x}"


def file_style(tokens: dict, lang: str) -> str:
    """The embedded style of a standalone figure: the theme's tokens resolved, no web fonts, the
    direction of the language on the root (an SVG loaded as an image inherits nothing). Built
    from declarations, never written as one string."""
    t = tokens
    rtl = "rtl" if lang == "ar" else "ltr"
    rules = [
        ("svg", [f"font-family:{_FILE_FONTS[lang]}", f"color:{t['ink']}", f"direction:{rtl}"]),
        ("text", ["fill:currentColor"]),
        (".box", [f"fill:{t['panel-2']}", f"stroke:{t['line']}", "stroke-width:1.2"]),
        (".box.acc", [f"fill:{t['accent-soft']}", f"stroke:{t['accent']}"]),
        (".box.good", [f"fill:{_mix(t['good'], t['panel'], 14)}", f"stroke:{t['good']}"]),
        (".box.bad", [f"fill:{_mix(t['bad'], t['panel'], 12)}", f"stroke:{t['bad']}"]),
        (".box.warn", [f"fill:{_mix(t['warn'], t['panel'], 14)}", f"stroke:{t['warn']}"]),
        (".box.frame", ["fill:none", f"stroke:{t['line']}", "stroke-dasharray:5 4"]),
        (".frame .lbl", [f"fill:{t['ink-2']}"]),
        (".edge", ["fill:none", f"stroke:{t['ink-2']}", "stroke-width:1.4"]),
        (".edge.acc", [f"stroke:{t['accent']}", "stroke-width:1.8"]),
        (".edge.loop", ["stroke-dasharray:4 3"]),
        (".lbl", ["font-size:12px"]),
        (".lbl.small", ["font-size:10.5px", f"fill:{t['ink-2']}", "paint-order:stroke fill", f"stroke:{t['panel']}",
                        "stroke-width:4px", "stroke-linejoin:round"]),
        (".lbl.strong", ["font-weight:600", "font-size:13px"]),
        (".num", [f"font-family:{_FILE_MONO}", "font-size:11px", "direction:ltr", "unicode-bidi:isolate"]),
        (".arrow", [f"fill:{t['ink-2']}"]),
        (".arrow.acc", [f"fill:{t['accent']}"]),
    ]
    sep = chr(59)   # the declaration separator, kept out of every literal on purpose
    return "".join(f"{selector}{{{sep.join(decls)}}}" for selector, decls in rules)


def svg_file(model, rtl: bool, lang: str, resolve, title: str, tokens: dict) -> str:
    """One standalone copy: the inline markup with an intrinsic size and the resolved style."""
    body = svg(model, rtl, lang, resolve, title)
    W, H = model["w"], model["h"]
    head = f'<svg class="dia" lang="{lang}" viewBox="0 0 {W} {H}"'
    assert body.startswith(head), body[:80]
    body = head + f' width="{W}" height="{H}"' + body[len(head):]
    cut = body.index(">") + 1
    return body[:cut] + f"<style>{file_style(tokens, lang)}</style>" + body[cut:]


MODELS = {"d1": overview, "d2": actors, "d3": stage_track, "d4": package_tree, "d5": relations_map,
          "d6": status_machine, "d7": guard, "d8": session}
STEPS = {"d7": 5, "d8": 6}
