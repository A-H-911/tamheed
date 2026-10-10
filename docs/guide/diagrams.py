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
        label = n["label"]
        lines = label if isinstance(label, list) else resolve(label).split("\n")
        lines = lines + list(n.get("label_tail") or [])
        # plan 206: a node may be accented when its resolved text names a token (the strip's step)
        box_cls = n["cls"] + (" acc" if n.get("accent_if") and n["accent_if"] in " ".join(lines) else "")
        if "bare" not in n["cls"]:
            rx = h / 2 if "pill" in n["cls"] else 6
            parts.append(f'<rect class="box {box_cls}" x="{x:.1f}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')
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


def _wrap(items: list[str], width: float, px: float = 12) -> list[str]:
    """Greedy lines of space-joined items that fit `width` by the width estimate."""
    lines, cur = [], ""
    for it in items:
        cand = f"{cur} {it}".strip()
        if cur and _text_width(cand, px) > width:
            lines.append(cur)
            cur = it
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


def relation_partners(f, ftype: str) -> tuple[dict, dict, list[str]]:
    """(incoming kind -> source prefixes, outgoing kind -> target prefixes, same-family kinds) for
    one family, from RELATION_RULES. relates_to (the fallback) is never drawn."""
    fams = {x["type"]: x for x in f["families"]}
    prefix = lambda t: fams[t]["prefix"].rstrip("-") if t in fams else t
    incoming: dict[str, list[str]] = {}
    outgoing: dict[str, list[str]] = {}
    same: list[str] = []
    table = fams[ftype]["table"] if ftype in fams else None
    cols = {c["name"] for t in f["schema"]["tables"] if t["table"] == table for c in t["columns"]}
    for rel in f["relations"]:
        if rel.get("fallback"):
            continue
        if rel["same_type"]:
            if "superseded_by" in cols:
                same.append(rel["relation"])
            continue
        if ftype in rel["to"]:
            incoming[rel["relation"]] = [prefix(t) for t in rel["from"]]
        if ftype in rel["from"]:
            outgoing[rel["relation"]] = [prefix(t) for t in rel["to"]]
    return incoming, outgoing, same


def relations_figure(f, ftype: str) -> dict:
    """Plan 204 (G4): the family in the centre, one node per incoming relation kind on the left
    (the source families' prefixes), one per outgoing kind on the right (the targets'), the
    same-family kinds below. Arrivals spread along the centre's sides, so no two edges share an
    anchor."""
    fams = {x["type"]: x for x in f["families"]}
    incoming, outgoing, same = relation_partners(f, ftype)
    LW, CW, GAP = 270, 200, 12
    lx, cx, rx = 20, 350, 610

    def column(kinds: dict, x: float, key: str) -> list[dict]:
        out, y = [], 40
        for kind, prefixes in kinds.items():
            lines = [kind] + _wrap(prefixes, LW - 14)
            h = 16 + 14 * len(lines)
            out.append(node(f"{key}-{kind}", x, y, LW, h, lines, ""))
            y += h + GAP
        return out

    left = column(incoming, lx, "in")
    right = column(outgoing, rx, "out")
    col_h = lambda ns: (ns[-1]["y"] + ns[-1]["h"] + 20) if ns else 0
    ch = max(44, 12 + 10 * max(len(left), len(right)))   # 10 px per arrival, so the arrowheads spread
    same_h = (16 + 14 * len(same)) if same else 0
    H = max(col_h(left), col_h(right), 40 + ch + (GAP + same_h if same else 0) + 20, 120)
    cy = max(40, (H - ch - (GAP + same_h if same else 0)) / 2)
    ns = left + right + [node("fam", cx, cy, CW, ch, [ftype, fams[ftype]["prefix"]], "acc strong")]
    es = []

    def spread(k: int, i: int) -> float:
        step = min(14, (ch - 12) / (k - 1)) if k > 1 else 0
        return (i - (k - 1) / 2) * step

    def elbows(column: list[dict], arrivals: list[float], near_x: float, sign: int) -> list[float]:
        """One elbow x per edge: the edge farthest from its arrival hugs the centre, the nearest
        elbows first, so verticals never overlap and no horizontal meets another vertical."""
        dist = [abs((n["y"] + n["h"] / 2) - a) for n, a in zip(column, arrivals)]
        order = sorted(range(len(column)), key=lambda i: -dist[i])
        step = min(8.0, 48 / max(1, len(column)))   # every elbow stays inside the 60 px gap
        xs = [0.0] * len(column)
        for rank, i in enumerate(order):
            xs[i] = near_x + sign * step * rank
        return xs

    cy_mid = cy + ch / 2
    arr_l = [cy_mid + spread(len(left), i) for i in range(len(left))]
    for n, a, mx in zip(left, arr_l, elbows(left, arr_l, cx - 6, -1)):
        ys = n["y"] + n["h"] / 2
        es.append(edge(n["key"], "fam", side=("r", "l"), offset=(0, a - cy_mid), via=[(mx, ys), (mx, a)]))
    arr_r = [cy_mid + spread(len(right), j) for j in range(len(right))]
    for n, a, mx in zip(right, arr_r, elbows(right, arr_r, cx + CW + 6, 1)):
        ys = n["y"] + n["h"] / 2
        es.append(edge("fam", n["key"], side=("r", "l"), offset=(a - cy_mid, 0), via=[(mx, a), (mx, ys)]))
    if same:
        ns.append(node("same", cx, cy + ch + GAP, CW, same_h, _L("rel.same"), "pill", line_keys=None))
        ns[-1]["label_tail"] = same   # the kinds, appended by the renderer after the resolved first line
        es.append(edge("fam", "same", side=("b", "t")))
    frs = []
    if left:
        frs.append(frame("sources", lx - 10, 10, LW + 20, col_h(left) - 10, _L("rel.sources"), [n["key"] for n in left]))
    if right:
        frs.append(frame("targets", rx - 10, 10, LW + 20, col_h(right) - 10, _L("rel.targets"), [n["key"] for n in right]))
    return {"id": f"rel-{ftype}", "w": 900, "h": int(H), "nodes": ns, "edges": es, "frames": frs}


# Plan 205 (G4): the gates that read one table. The three SQL gates from their views in schema.sql
# (g_trace_failures reads requirements through v_req_links over trace_edges; g_progress_failures
# reads acceptance_criteria and audit_verdicts; g_set_failures reads the registry and omissions, so
# it names every Always family and is added per family below); the Python gates from the server
# (G-DEC-STATUS over decisions, G-REQ-SRC over requirements, G-REL over trace_edges). G-IDS and
# G-COMPLETE read every table, so no family's figure draws them.
GATE_TABLES = {
    "G-TRACE": ("requirements", "trace_edges"),
    "G-PROGRESS": ("acceptance_criteria", "audit_verdicts"),
    "G-REL": ("trace_edges",),
    "G-DEC-STATUS": ("decisions",),
    "G-REQ-SRC": ("requirements",),
}
# the review page section that shows a table (export_html.SECTIONS); any other table is a register fold
REVIEW_SECTION = {"lessons": "lessons", "feedback": "feedback", "prompts": "prompts",
                  "progress_entries": "execution", "audit_verdicts": "execution", "trace_edges": "graph"}


def _hub(hub: str, column: list[dict], hub_x: float, hub_cy: float, hub_h: float, hub_is_source: bool, gap: float = 60):
    """Edges between one hub node and a column of nodes (the 204 routing): the hub's ports spread
    along its side, one elbow x per edge ranked by its distance, inside the gap next to the hub."""
    k = len(column)
    step = min(14.0, (hub_h - 12) / (k - 1)) if k > 1 else 0.0
    ports = [hub_cy + (i - (k - 1) / 2) * step for i in range(k)]
    dist = [abs(n["y"] + n["h"] / 2 - p) for n, p in zip(column, ports)]
    order = sorted(range(k), key=lambda i: -dist[i])
    gstep = min(8.0, (gap - 12) / max(1, k))   # every elbow stays inside the gap beside the hub
    xs = [0.0] * k
    for rank, i in enumerate(order):
        xs[i] = hub_x + (6 + gstep * rank) * (1 if hub_is_source else -1)
    out = []
    for n, p, mx in zip(column, ports, xs):
        ny = n["y"] + n["h"] / 2
        if hub_is_source:
            out.append(edge(hub, n["key"], side=("r", "l"), offset=(p - hub_cy, 0), via=[(mx, p), (mx, ny)]))
        else:
            out.append(edge(n["key"], hub, side=("r", "l"), offset=(0, p - hub_cy), via=[(mx, ny), (mx, p)]))
    return out


def data_path(f, ftype: str) -> dict:
    """Plan 205 (G4): where a family's rows come from and go. The stages whose Writes clause names
    its table (workflow.md, parsed; a bare label when none does), the functions that insert into
    it (the census of the server source), data/<table>.jsonl with its CSV, then review.html and
    the section that shows it."""
    fam = next(x for x in f["families"] if x["type"] == ftype)
    table = fam["table"]
    stages = sorted(n for n, tabs in f["writes"].items() if tabs and table in tabs)
    # the writers, from the census of the server's INSERT statements: the public functions are drawn
    writers = f["inserters"].get(table) or f["inserters"]["{table}"]
    tail = [w for w in writers if not w.startswith("_")]
    section = REVIEW_SECTION.get(table, "registers")
    ns, y = [], 40
    for n in stages:
        ns.append(node(f"stage-{n}", 20, y, 260, 40, f"stagetitle.{n:02d}", "acc pill", small=True))
        ns[-1]["label_tail"] = [str(n)]
        y += 52
    th = max(16 + 14 * (1 + len(tail)), 12 + 10 * len(stages))   # 10 px per arrival, so the arrowheads spread
    H = max(y + 10 if stages else 0, th + 50, 120)
    ty = (H - th) / 2
    ns.append(node("tool", 320, ty, 180, th, _L("data.writers"), "strong"))
    ns[-1]["label_tail"] = tail
    if not stages:
        ns.append(node("nostage", 20, (H - 20) / 2, 260, 20, _L("data.nostage"), "bare"))
    ns.append(node("data", 530, (H - 44) / 2, 230, 44, [f"data/{table}.jsonl", f"csv/{table}.csv"], "", mono=True, small=True))
    ns.append(node("review", 790, (H - 44) / 2, 100, 44, ["review.html", f"#{section}"], "pill", mono=True, small=True))
    es = _hub("tool", ns[:len(stages)], 320, ty + th / 2, th, False, gap=40) if stages else []
    # ponytail: the bare label is appended after the tool node, so the stage slice above stays ns[:len(stages)]
    es.append(edge("tool", "data", side=("r", "l")))
    es.append(edge("data", "review", _L("data.export"), "", side=("r", "l"), label_at=(775, (H - 44) / 2 - 8, "middle")))
    frs = [frame("stages", 10, 10, 280, y - 2, _L("data.stages"), [n["key"] for n in ns[:len(stages)]])] if stages else []
    return {"id": f"data-{ftype}", "w": 900, "h": int(H), "nodes": ns, "edges": es, "frames": frs}


def life_std8(f) -> dict:
    """Plan 205 (G4): the STD8 lifecycle is D6 without the Review state (STD9's branch, slices and
    work items): Approved moves to Implemented when verified."""
    m = status_machine(f)
    m["id"] = "life-STD8"
    m["nodes"] = [n for n in m["nodes"] if n["key"] != "Review"]
    m["edges"] = [e for e in m["edges"] if "Review" not in (e["from"], e["to"])]
    return m


def lifecycle_of(f, ftype: str) -> str | None:
    """The lifecycle set a family's table belongs to (STD8, STD9 or the table's own domain set)."""
    fam = next(x for x in f["families"] if x["type"] == ftype)
    for name in ("STD8", "STD9"):
        if fam["table"] in f["lifecycles"][name]["tables"]:
            return name
    return fam["table"] if fam["table"] in f["lifecycles"]["domain"] else None


def trace_readers(f, ftype: str) -> tuple[list[str], list[str]]:
    """The gates (GATE_TABLES, plus G-SET for an Always family) and the readiness rules (the
    readiness run's population tables) that read a family's table."""
    fam = next(x for x in f["families"] if x["type"] == ftype)
    gates = [g for g, tabs in GATE_TABLES.items() if fam["table"] in tabs]
    if fam["cls"] == "Always":
        gates.append("G-SET")
    rules = [r for r, t in f["rule_tables"].items() if t == fam["table"]]
    return gates, rules


def trace_path(f, ftype: str) -> dict:
    """Plan 205 (G4): what reads a family at the gate and in readiness, as two framed columns."""
    fam = next(x for x in f["families"] if x["type"] == ftype)
    gates, rules = trace_readers(f, ftype)
    severity = {r["rule"]: r["severity"] for scope in f["rules"].values() for r in scope}
    ns, frs, y = [], [], 10
    if gates:
        frs.append(frame("gates", 310, y, 290, 48 * len(gates) + 22, _L("trace.gates"), [f"gate-{g}" for g in gates]))
        for g in gates:
            ns.append(node(f"gate-{g}", 330, y + 30, 250, 36, [g], "good pill", mono=True))
            y += 48
        y += 32
    if rules:
        frs.append(frame("rules", 310, y, 290, 48 * len(rules) + 22, _L("trace.rules"), [f"rule-{r}" for r in rules]))
        for r in rules:
            sev = severity.get(r, "advisory")
            ns.append(node(f"rule-{r}", 330, y + 30, 250, 36, [r, sev], "warn pill" if sev == "blocking" else "pill", mono=True))
            y += 48
        y += 32
    H = max(y, 100)
    hub = node("fam", 20, (H - 44) / 2, 200, 44, [ftype, fam["prefix"]], "acc strong")
    es = _hub("fam", ns, 220, H / 2, 44, True, gap=110)
    return {"id": f"trace-{ftype}", "w": 620, "h": int(H), "nodes": [hub] + ns, "edges": es, "frames": frs}


# Plan 206 (G7): what each tool needs, reads and writes, hand-authored, every claim with the line of
# plugins/tamheed/server/tamheed_server.py that makes it true (the number after the item): the line
# in the tool or in the helper it calls; the def line only for a parameter of the signature or for
# "nothing". An item
# starting with "@" is a content id under dia.fx.*, resolved per language; any other item is an
# identifier drawn as written (a table, a file, a journal event type).
TOOL_EFFECTS = {
    "server_info": {
        "needs": [("@need.none", 5579)],
        "reads": [("plugin.json", 5553), ("packages", 5581), ("@resume", 5597)],
        "writes": [("@nothing", 5560)]},
    "package_create": {
        "needs": [("@need.closed", 974), ("@need.lockfree", 983)],
        "reads": [("@nothing", 971)],
        "writes": [("entity_types", 987), ("packages", 992), ("README.md", 1004), ("@lock_taken", 982), ("CLAUDE.md", 1006)]},
    "package_open": {
        "needs": [("@need.closed", 1403), ("@need.v4", 1410), ("@need.lockfree", 1422)],
        "reads": [("@canonical", 1421), ("@resume", 1430)],
        "writes": [("@lock_taken", 1421), ("CLAUDE.md", 1427)]},
    "package_close": {
        "needs": [("@need.open", 1453)],
        "reads": [("@nothing", 1450)],
        "writes": [("@canonical", 1458), ("@lock_released", 1474), ("data/*.unflushed", 1470)]},
    "package_unlock": {
        "needs": [("@need.name", 5247), ("@need.word", 5288)],
        "reads": [("@lock_file", 5284)],
        "writes": [("@lock_removed", 5321), ("progress_entries", 5338), ("forced-override", 5341)]},
    "entity_upsert": {
        "needs": [("@need.open", 1780)],
        "reads": [("@readiness", 1895), ("@skill_names", 2015)],
        "writes": [("@any_table", 2189), ("trace_edges", 1841), ("progress_entries", 1850), ("lessons", 2284),
                   ("@canonical", 2435)]},
    "entity_query": {
        "needs": [("@need.open", 2476)],
        "reads": [("@any_table", 2541)],
        "writes": [("@nothing", 2444)]},
    "trace_query": {
        "needs": [("@need.open", 2613)],
        "reads": [("trace_edges", 2622)],
        "writes": [("@nothing", 2611)]},
    "gate_run": {
        "needs": [("@need.open", 2637)],
        "reads": [("@all_tables", 2656)],
        "writes": [("@nothing", 2632)]},
    "readiness_check": {
        "needs": [("@need.open", 3402)],
        "reads": [("@all_tables", 3417)],
        "writes": [("@nothing", 3396)]},
    "progress_update": {
        "needs": [("@need.open", 3450)],
        "reads": [("@nothing", 3428)],
        "writes": [("progress_entries", 3467), ("@canonical", 3480)]},
    "audit_record": {
        "needs": [("@need.open", 3521)],
        "reads": [("@nothing", 3507)],
        "writes": [("audit_verdicts", 3535), ("@canonical", 3547)]},
    "work_bind": {
        "needs": [("@need.open", 3559)],
        "reads": [("entity_index", 3569)],
        "writes": [("@bound_rows", 3579), ("progress_entries", 3586), ("@canonical", 3594)]},
    "handoff_emit": {
        "needs": [("@need.open", 4214), ("@need.kickoff", 4231)],
        "reads": [("prompts", 4231), ("lessons", 4116), ("skills", 4122), ("feedback", 4370)],
        "writes": [("README.md", 4223), ("<target>/CLAUDE.md", 4643), ("<target>/.mcp.json", 4299),
                   ("<package>/CLAUDE.md", 4602)]},
    "package_migrate": {
        "needs": [("@need.name", 4876), ("@need.lockfree", 4916), ("@need.word", 4876)],
        "reads": [("@canonical", 4956)],
        "writes": [("data-v3-backup/", 4952), ("data/*.jsonl", 5171), ("progress_entries", 5100),
                   ("README.md", 5234)]},
    "package_adopt": {
        "needs": [("@need.source", 5364), ("@need.word", 5369)],
        "reads": [("@source_repo", 5369)],
        "writes": [("@new_package", 5380), ("README.md", 5373), ("CLAUDE.md", 5375)]},
    "export_html": {
        "needs": [("@need.open", 5424)],
        "reads": [("@all_tables", 5427), ("@readiness", 5430)],
        "writes": [("review.html", 5467), ("csv/*.csv", 5496)]},
    "package_verify": {
        "needs": [("@need.name", 1488)],
        "reads": [("data/*.jsonl", 1541), ("review.html", 1552)],
        "writes": [("progress_entries", 1603), ("integrity-verified", 1603)]},
    "entity_export": {
        "needs": [("@need.open", 1667), ("@need.path", 1638)],
        "reads": [("@tool_result", 1696)],
        "writes": [("@export_file", 1718)]},
}


def _pill_item(key, item, x, y, w):
    """A canvas item: "@x" is the phrase dia.fx.x; "#cid|tail" is a content id with a plain tail
    (a stage title with its number); anything else is an identifier drawn as written."""
    if item.startswith("@"):
        return node(key, x, y, w, 28, _L("fx." + item[1:]), "pill", small=True)
    if item.startswith("#"):
        cid, _, tail = item[1:].partition("|")
        n = node(key, x, y, w, 28, cid, "pill", small=True)
        if tail:
            n["label"], n["label_tail"] = cid, [tail]
            n["h"] = 40
        return n
    return node(key, x, y, w, 28, [item], "pill", mono=True, small=True)


def _canvas(fid: str, centre: list[str], centre_cls: str, left: list[str], right: list[str],
            below: list[str], labels: tuple[str, str, str]) -> dict:
    """Plan 206/207: one hub in the centre, a framed column on the left fanning in, a framed column
    on the right fanning out, a framed column beneath with no arrows. `labels` = the three frame
    titles (dia.* keys). A column holding only the "@nothing" phrase draws no arrow."""
    def column(items, x, key_prefix):
        ns, y = [], 40
        for i, it in enumerate(items):
            n = _pill_item(f"{key_prefix}{i}", it, x, y, 220)
            ns.append(n)
            y += n["h"] + 8
        return ns, y - 2
    ln, lh = column(left, 20, "l")
    rn, rh = column(right, 620, "r")
    for n in ln:
        n["w"] = 240
    for n in rn:
        n["w"] = 250
    ty = 24
    hub = node("hub", 330, ty, 210, 44, centre, centre_cls, mono=True)
    ny = ty + 44 + 14
    bn, bh = column(below, 330, "b")
    for n in bn:
        n["x"], n["w"], n["y"] = 330, 210, n["y"] + ny
    H = max(lh + 10, rh + 10, ny + bh + 10, 120) + 20
    frs = [frame("left", 10, 10, 260, lh, _L(labels[0]), [n["key"] for n in ln]),
           frame("right", 610, 10, 270, rh, _L(labels[1]), [n["key"] for n in rn]),
           frame("below", 320, ny, 230, bh, _L(labels[2]), [n["key"] for n in bn])]
    es = []
    if left != ["@nothing"]:
        es += _hub("hub", ln, 330, ty + 22, 44, False, gap=60)
    if right != ["@nothing"]:
        es += _hub("hub", rn, 540, ty + 22, 44, True, gap=70)
    return {"id": fid, "w": 900, "h": int(H), "nodes": ln + rn + [hub] + bn, "edges": es, "frames": frs}


def effects_figure(f, tool: str) -> dict:
    """Plan 206 (G7): the tool in the centre, what it reads on the left (arrows in), what it writes
    on the right (arrows out), what it needs beneath it."""
    fx = TOOL_EFFECTS[tool]
    return _canvas(f"fx-{tool}", [tool], "acc strong", [x for x, _ln in fx["reads"]],
                   [x for x, _ln in fx["writes"]], [x for x, _ln in fx["needs"]],
                   ("fx.reads", "fx.writes", "fx.needs"))


# Plan 207 (G8): how gate_run evaluates each mechanical gate, with the server line (Python) or the
# view in schema.sql, in the order the server builds its report (the views share one loop, L2680).
GATE_HOW = {
    "G-IDS": ("python", 2667), "G-DEC-STATUS": ("python", 2672), "G-REQ-SRC": ("python", 2675),
    "G-TRACE": ("view", "g_trace_failures"), "G-SET": ("view", "g_set_failures"),
    "G-PROGRESS": ("view", "g_progress_failures"),
    "G-COMPLETE": ("python", 2718), "G-REL": ("python", 2752),
}
PIPELINE = ["G-IDS", "G-DEC-STATUS", "G-REQ-SRC", "G-TRACE", "G-SET", "G-PROGRESS", "G-COMPLETE", "G-REL"]
# what each mechanical gate reads: the views' bodies (schema.sql L851-871) and the server's loops
# (G-IDS L2641-2656 over every table against entity_index; G-COMPLETE L2705 over every table
# through _graded_text;
# G-REL through _edge_rule_violations, trace_edges joined to entity_index twice)
GATE_READS = {**GATE_TABLES, "G-SET": ("entity_types", "entity_index", "omissions"),
              "G-REL": ("trace_edges", "entity_index"),
              "G-IDS": ("@all_tables", "entity_index"), "G-COMPLETE": ("@all_tables",)}
VACUOUS = {"G-TRACE": 2689, "G-PROGRESS": 2698}          # the warning the server attaches over zero rows
_SEVERITY_KEY = {"Critical": "@gate.sev.critical", "Warn": "@gate.sev.warn", "Critical at emission": "@gate.sev.emission"}


def _stage_items(f, gate: str) -> list[str]:
    return [f"#stagetitle.{n:02d}|{n}" for n, gs in f["checks"].items() if gs and gate in gs]


def gate_figure(f, gate: str) -> dict:
    """Plan 207 (G8): a mechanical gate reads its tables and is evaluated by a view or by Python in
    gate_run; a judgment or warn gate is the agent's judgment at the stages whose Check names it,
    helped by the mechanics its definition names, recorded as a gate-decision journal entry."""
    sev = _SEVERITY_KEY[f["gate_defs"][gate]["severity"]]
    if gate in GATE_HOW:
        kind, where = GATE_HOW[gate]
        how = [where, "@gate.view"] if kind == "view" else ["@gate.python", f"tamheed_server.py L{where}"]
        # a mechanical gate no Check clause names still runs at stage 19 (quality-gates.md, Running gates)
        stages = _stage_items(f, gate) or ["@gate.stage19"]
        below = [sev] + (["@gate.vacuous"] if gate in VACUOUS else [])
        return _canvas(f"gate-{gate}", [gate], "good strong", list(GATE_READS[gate]), how + stages, below,
                       ("gate.reads", "gate.how", "gate.sev"))
    stages = _stage_items(f, gate) or ["@gate.nostage"]
    mech = f["gate_defs"][gate]["mechanics"]
    cls = "warn strong" if gate in f["gates"]["warn"] else "acc strong"
    return _canvas(f"gate-{gate}", [gate], cls, stages, ["@gate.judgment"] + mech + ["@gate.recorded"], [sev],
                   ("gate.stages", "gate.how", "gate.sev"))


def pipeline_figure(f) -> dict:
    """Plan 207 (G8): gate_run's gates in evaluation order, and readiness_check's four parts above
    them as the semantic layer. No arrow joins the two: they are separate calls."""
    ns, es, frs = [], [], []
    parts = ["@pipe.blocking", "@pipe.waivers", "@pipe.liveness", "@pipe.human"]
    col = 860 // len(parts)
    for i, p in enumerate(parts):
        ns.append(_pill_item(f"p{i}", p, 30 + i * col, 36, col - 12))
    frs.append(frame("sem", 10, 10, 880, 66, _L("pipe.sem"), [n["key"] for n in ns]))
    col = 860 // len(PIPELINE)
    gn = []
    for i, g in enumerate(PIPELINE):
        gn.append(node(f"g{i}", 30 + i * col, 122, col - 12, 36, [g], "good pill", mono=True, small=True))
        if i:
            es.append(edge(f"g{i - 1}", f"g{i}", side=("r", "l")))
    frs.append(frame("mech", 10, 96, 880, 74, _L("pipe.mech"), [n["key"] for n in gn]))
    return {"id": "gates-pipeline", "w": 900, "h": 184, "nodes": ns + gn, "edges": es, "frames": frs}


def sequence_strip(f, tool: str) -> dict:
    """Plan 206 (G7): every recipe that names the tool, one row each, its steps as the swimlane's
    pills with the tool's step accented. Derived from RECIPES."""
    rows = [(slug, names, steps) for slug, names, steps in RECIPES if tool in names]
    ns, es, frs = [], [], []
    y = 10
    for slug, names, steps in rows:
        col = 860 // steps
        w = min(col - 8, 200)
        keys = []
        for k in range(1, steps + 1):
            ns.append(node(f"{slug}-s{k}", 30 + (k - 1) * col, y + 26, w, 40, _L(f"wf.{slug}.s{k}"), "pill", small=True))
            ns[-1]["accent_if"] = tool       # the step whose label names the tool is drawn accented
            keys.append(f"{slug}-s{k}")
            if k > 1:
                es.append(edge(f"{slug}-s{k - 1}", f"{slug}-s{k}", side=("r", "l")))
        frs.append(frame(f"row-{slug}", 10, y, 880, 76, f"workflow.{slug}.title", keys))
        y += 86
    return {"id": f"seq-{tool}", "w": 900, "h": y + 4, "nodes": ns, "edges": es, "frames": frs}


def skills_matrix(f) -> dict:
    """Plan 208 (G9): rows the skills by group, columns the discipline skills, a mark where the
    row's SKILL.md cites the column. Derived from skill_text; nothing authored."""
    groups = [("front", "skillgroup.front"), ("scenario", "skillgroup.scenario"), ("discipline", "skillgroup.discipline")]
    cols = [s["name"] for s in f["skills"] if s["group"] == "discipline"]
    hx, hy, cw, rh = 150, 44, 90, 22      # 'measurement-' is 73 px at the small size; the rule wants w - 10
    x0, y0 = 10 + hx, 10 + hy
    ns = [node("corner", 10, 10, hx - 4, hy - 4, _L("skills.corner"), "bare", small=True, keyed=False)]
    for j, c in enumerate(cols):
        head, _, tail = c.partition("-")
        ns.append(node(f"col-{c}", x0 + j * cw, 10, cw - 4, hy - 4, [head + "-", tail] if tail else [c], "acc", small=True, keyed=False))   # a box: a pill's round ends eat its width
    frs, y = [], y0
    for g, label in groups:
        members = []
        gy = y
        y += 22                      # the frame's title band: the first row must not sit under the title
        for s in [x for x in f["skills"] if x["group"] == g]:
            rk = f"row-{s['name']}"
            ns.append(node(rk, 14, y, hx - 12, rh - 2, [s["name"]], "bare", mono=True, small=True, keyed=False))
            members.append(rk)
            for j, c in enumerate(cols):
                if c in f["skill_text"][s["name"]]["cites"]:
                    mk = f"m-{s['name']}-{c}"
                    ns.append(node(mk, x0 + j * cw + cw / 2 - 8, y + rh / 2 - 6, 12, 12, [], "acc pill", keyed=False))
                    members.append(mk)
            y += rh
        frs.append(frame(f"grp-{g}", 10, gy - 4, hx + len(cols) * cw, y - gy + 4, label, members))
        y += 14
    return {"id": "skills-matrix", "w": x0 + len(cols) * cw + 6, "h": y, "nodes": ns, "edges": [], "frames": frs}


def skills_lifecycle(f) -> dict:
    """Plan 208 (G9): the lesson and skill statuses as pills in CHECK order (G21: no arrow the
    engine does not state); between them the moves a line states: the two journal events the
    server writes on a lesson's status change (L1852-1853), skill-promote's interview that sets the
    lessons Promoted and writes the SKL- row on the operator's word (its steps 3 and 5), the two
    retirement columns, and the readiness rules that watch lessons."""
    lessons = f["lifecycles"]["domain"]["lessons"]
    skills = f["lifecycles"]["domain"]["skills"]
    ns, es, frs = [], [], []
    ly = {}
    for i, v in enumerate(lessons):
        ly[v] = 50 + 36 * i
        ns.append(node(f"l-{v}", 40, ly[v], 240, 28, [v], "acc pill" if v in ("Approved", "Promoted") else "pill", mono=True, small=True))
    # the retirement note sits under the pills; the retirement edges run in the frame's left channel
    ns.append(node("sup-note", 40, 50 + 36 * len(lessons), 240, 20, _L("skills.supersede"), "bare", small=True))
    frs.append(frame("lessons", 10, 10, 290, 36 * len(lessons) + 74, _L("skills.lessons"), [f"l-{v}" for v in lessons] + ["sup-note"]))
    ns.append(node("ev-c", 330, ly["Approved"], 220, 28, ["lesson-confirmed"], "pill", mono=True, small=True))
    ns.append(node("ev-p", 330, ly["Promoted"], 220, 28, ["lesson-promoted"], "pill", mono=True, small=True))
    frs.append(frame("events", 320, ly["Approved"] - 30, 240, 36 * 2 + 30, _L("skills.events"), ["ev-c", "ev-p"]))
    es.append(edge("l-Approved", "ev-c", side=("r", "l"), offset=(-5, 0)))
    es.append(edge("l-Promoted", "ev-p", side=("r", "l"), offset=(-5, 0)))
    # the third stated move (L2120-2135): a successor lesson approved on the operator's word retires
    # the old Approved and Promoted lessons to Superseded and writes a `transition` journal row
    sup = ly["Superseded"]
    # the farther source runs the outer channel and arrives lower, so the two never cross (the 204 ranking)
    es.append(edge("l-Approved", "l-Superseded", side=("l", "l"), offset=(0, 6), via=[(22, ly["Approved"] + 14), (22, sup + 20)]))
    es.append(edge("l-Promoted", "l-Superseded", side=("l", "l"), offset=(0, -6), via=[(31, ly["Promoted"] + 14), (31, sup + 8)]))
    py = ly["Promoted"] + 36 * 2 + 30
    ns.append(node("promote", 330, py, 220, 44, _L("skills.promote"), "acc strong"))
    es.append(edge("promote", "l-Promoted", side=("l", "r"), offset=(0, 6), via=[(305, py + 22), (305, ly["Promoted"] + 20)]))
    sy = {}
    for i, v in enumerate(skills):
        sy[v] = py + 36 * i
        ns.append(node(f"s-{v}", 610, sy[v], 260, 28, [v], "good pill" if v == "Approved" else "pill", mono=True, small=True))
    es.append(edge("promote", "s-Approved", side=("r", "l")))
    ry = py + 36 * len(skills) + 10
    ns.append(node("ret-s", 610, ry, 260, 28, ["superseded_by"], "pill", mono=True, small=True))
    ns.append(node("ret-u", 610, ry + 36, 260, 28, ["upstreamed_to"], "pill", mono=True, small=True))
    frs.append(frame("skills", 600, py - 30, 290, ry + 72 - (py - 30) + 6, _L("skills.skills"), [f"s-{v}" for v in skills] + ["ret-s", "ret-u"]))
    rules = sorted(r["rule"] for sc in f["rules"].values() for r in sc if r["rule"].startswith("lessons-"))
    rules = sorted(set(rules))
    by = max(ry + 72 + 6, 36 * len(lessons) + 84) + 20
    col = 860 // max(1, len(rules))
    rn = []
    for i, r in enumerate(rules):
        rn.append(node(f"rule-{r}", 30 + i * col, by + 30, col - 12, 28, [r], "warn pill", mono=True, small=True))
    ns += rn
    frs.append(frame("rules", 10, by, 880, 68, _L("skills.rules"), [n["key"] for n in rn]))
    return {"id": "skills-lifecycle", "w": 900, "h": by + 78, "nodes": ns, "edges": es, "frames": frs}


def skill_strip(f, name: str) -> dict:
    """Plan 208 (G9): the tools a skill's text names in the order of first mention, STOP where the
    text says so, chained left to right in rows of six; a skill naming no tool says so."""
    tokens = f["skill_text"][name]["tokens"]
    if not tokens:
        return {"id": f"skill-{name}", "w": 900, "h": 60,
                "nodes": [node("none", 20, 16, 860, 28, _L("skills.notool"), "bare", small=True)], "edges": [], "frames": []}
    ns, es = [], []
    per, col = 6, 143
    for i, tok in enumerate(tokens):
        r, c = divmod(i, per)
        cls = "warn pill" if tok == "STOP" else "pill"
        ns.append(node(f"t{i}", 30 + c * col, 12 + r * 52, col - 12, 36, [tok], cls, mono=True, small=True))
        if i:
            pr, pc = divmod(i - 1, per)
            es.append(edge(f"t{i - 1}", f"t{i}", side=("r", "l") if pr == r else ("b", "t")))
    rows = (len(tokens) + per - 1) // per
    return {"id": f"skill-{name}", "w": 900, "h": 12 + rows * 52 + 4, "nodes": ns, "edges": es, "frames": []}


def file_models(f) -> dict:
    """Every file figure the page may embed: the swimlanes; per family a relations figure (when a
    typed relation names it), a data path, a trace path (when a gate or rule reads it); STD8; per
    tool an effects canvas and, when a recipe names it, a call-sequence strip."""
    out = dict(FILE_MODELS)
    out["life-STD8"] = life_std8
    out["gates-pipeline"] = pipeline_figure
    out["skills-matrix"] = skills_matrix
    out["skills-lifecycle"] = skills_lifecycle
    for s in f["skills"]:
        out[f"skill-{s['name']}"] = (lambda ff, n=s["name"]: skill_strip(ff, n))
    for tier in f["gates"].values():
        for g in tier:
            out[f"gate-{g}"] = (lambda ff, gg=g: gate_figure(ff, gg))
    for t in f["tools"]:
        out[f"fx-{t['name']}"] = (lambda ff, n=t["name"]: effects_figure(ff, n))
        if any(t["name"] in names for _slug, names, _steps in RECIPES):
            out[f"seq-{t['name']}"] = (lambda ff, n=t["name"]: sequence_strip(ff, n))
    for x in f["families"]:
        incoming, outgoing, same = relation_partners(f, x["type"])
        if incoming or outgoing or same:
            out[f"rel-{x['type']}"] = (lambda ff, t=x["type"]: relations_figure(ff, t))
        out[f"data-{x['type']}"] = (lambda ff, t=x["type"]: data_path(ff, t))
        gates, rules = trace_readers(f, x["type"])
        if gates or rules:
            out[f"trace-{x['type']}"] = (lambda ff, t=x["type"]: trace_path(ff, t))
    return out


def label_problems(model, resolve) -> list[str]:
    """A file figure renders in fallback fonts with no inline twin to compare against, so every
    node label line must fit its box by the width estimate (plan 203)."""
    out = []
    for n in model["nodes"]:
        if not (n["w"] and n["h"]):
            continue
        lines = n["label"] if isinstance(n["label"], list) else resolve(n["label"]).split("\n")
        lines = list(lines) + list(n.get("label_tail") or [])
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
