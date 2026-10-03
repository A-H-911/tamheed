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

from html import escape as esc

# Every content id a diagram label uses (the build adds these to the required ids).
DIAGRAM_LABELS: list[str] = []


def _L(key: str) -> str:
    cid = f"dia.{key}"
    if cid not in DIAGRAM_LABELS:
        DIAGRAM_LABELS.append(cid)
    return cid


def node(key, x, y, w, h, label, cls="", mono=False, step=None, group="", links="", detail=None,
         line_keys=None, small=False):
    """A box (w,h > 0), a text-only label (cls contains 'bare') or a junction point (w = h = 0)."""
    return {"key": key, "x": x, "y": y, "w": w, "h": h, "label": label, "cls": cls, "mono": mono,
            "step": step, "group": group, "links": links, "detail": detail,
            "line_keys": line_keys, "small": small}


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


def _text(lines, x, y, rtl, cls, anchor="middle", lh=14, keys=None):
    out = []
    n = len(lines)
    y0 = y - (n - 1) * lh / 2
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
        if n["key"]:
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
    """D1 — both halves: a brief becomes a package through the server; execution records back
    through the same server and ends at readiness and the go/no-go."""
    ns = [
        node("brief", 10, 92, 90, 44, _L("overview.brief"), "pill"),
        node("A", 150, 42, 120, 44, _L("overview.understand"), "acc"),
        node("B", 150, 92, 120, 44, _L("overview.explore"), "acc"),
        node("C", 150, 142, 120, 44, _L("overview.plan"), "acc"),
        node("j1", 124, 114, 0, 0, [""]), node("j2", 300, 114, 0, 0, [""]),
        node("server", 330, 92, 120, 44, _L("overview.server"), "strong"),
        node("pkg", 520, 70, 120, 88, _L("overview.package"), ""),
        node("exec", 740, 92, 130, 44, _L("overview.executor"), "pill"),
        node("review", 520, 230, 120, 36, _L("overview.review"), ""),
        node("ready", 730, 222, 150, 44, _L("overview.readiness"), "good"),
    ]
    es = [
        edge("brief", "j1", side=("r", "l"), arrow=False, bus="in"),
        edge("j1", "A", side=("t", "l")), edge("j1", "B", side=("r", "l")), edge("j1", "C", side=("b", "l")),
        edge("A", "j2", side=("r", "t"), arrow=False, bus="out"), edge("B", "j2", side=("r", "l"), arrow=False, bus="out"),
        edge("C", "j2", side=("r", "b"), arrow=False, bus="out"),
        edge("j2", "server", side=("r", "l")),
        edge("server", "pkg", _L("overview.writes"), "acc", side=("r", "l"), label_at=(485, 80, "middle")),
        edge("pkg", "exec", _L("overview.handoff"), "", side=("r", "l"), label_at=(690, 102, "middle")),
        edge("exec", "server", _L("overview.records"), "acc", bend=-62, side=("t", "t")),
        edge("pkg", "review", _L("overview.export"), side=("b", "t")),
        edge("exec", "ready", _L("overview.close"), "", side=("b", "t"), label_at=(797, 190, "end")),
    ]
    return {"id": "d1", "w": 890, "h": 280, "nodes": ns, "edges": es}


def actors(f) -> dict:
    """D2 — operator, planning agent, executing agent and what each may do."""
    ns = [
        node("op", 290, 10, 180, 46, _L("actors.operator"), "acc strong", group="op"),
        node("plan", 60, 150, 200, 46, _L("actors.planner"), "strong", group="plan"),
        node("exec", 500, 150, 200, 46, _L("actors.executor"), "strong", group="exec"),
        node("op-does", 490, 13, 260, 40, _L("actors.operator.does"), "pill", group="op", links="op"),
        node("plan-does", 20, 204, 280, 56, _L("actors.planner.does"), "pill", group="plan", links="plan"),
        node("exec-does", 460, 204, 280, 56, _L("actors.executor.does"), "pill", group="exec", links="exec"),
        node("store", 290, 290, 180, 40, _L("actors.store"), "", group="store"),
    ]
    es = [
        edge("op", "plan", _L("actors.brief"), side=("b", "t"), offset=(-50, 0)),
        edge("op", "exec", _L("actors.approves"), side=("b", "t"), offset=(50, 0)),
        edge("plan", "exec", _L("actors.handoff"), "acc", side=("r", "l")),
        edge("plan-does", "store", None, "", side=("b", "l")),
        edge("exec-does", "store", None, "", side=("b", "r")),
    ]
    return {"id": "d2", "w": 760, "h": 340, "nodes": ns, "edges": es}


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
    lane_start = {n: p["stages"][0] for p in st["phases"] for n in p["stages"]}
    for n in sorted(loops):
        es.append(edge(f"s{n}", f"s{lane_start[n]}", _L("stages.loop"), "loop", draw=False,
                       side=("t", "t"), bend=-28, offset=(0, 14)))
    ns.append(node("legend-l", 360, 256, 190, 24, _L("stages.legend.loop"), "pill"))
    ns.append(node("legend-h", 560, 256, 190, 24, _L("stages.legend.human"), "good pill"))
    return {"id": "d3", "w": 760, "h": 294, "nodes": ns, "edges": es}


def package_tree(f) -> dict:
    """D4 — a package on disk, the one path that changes data/, and the executor repo it wires."""
    ns = [
        node("tools", 240, 6, 190, 34, _L("package.tools"), "pill"),
        node("root", 10, 76, 150, 36, _L("package.root"), "acc strong"),
        node("data", 240, 70, 190, 48, _L("package.data"), "", links="write"),
        node("prompts", 240, 132, 190, 48, _L("package.prompts"), ""),
        node("review", 240, 194, 190, 48, _L("package.review"), ""),
        node("exports", 240, 256, 190, 48, _L("package.exports"), ""),
        node("csv", 240, 318, 190, 36, _L("package.csv"), ""),
        node("target", 480, 20, 150, 36, _L("package.target"), "strong"),
        node("mcp", 480, 80, 270, 40, _L("package.mcp"), ""),
        node("claude", 480, 134, 270, 48, _L("package.claude"), ""),
    ]
    es = [
        edge("root", "data", side=("r", "l"), bus="tree"), edge("root", "prompts", side=("r", "l"), bus="tree"),
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
    ns = [node("corner", 10, 10, hx - 4, hy - 4, _L("relations.corner"), "bare", small=True)]
    x0, y0 = 10 + hx, 10 + hy
    for j, b in enumerate(names):
        ns.append(node(f"col-{b}", x0 + j * cw, 10, cw - 4, hy - 4, _L(f"relations.h.{b}"), "acc pill"))
    y = y0
    for i, a in enumerate(names):
        h = rows_h[i]
        ns.append(node(f"row-{a}", 10, y, hx - 4, h - 4, _L(f"relations.h.{a}"), "acc pill"))
        for j, b in enumerate(names):
            rels = cells.get((a, b), [])
            cls = "cell" if rels else "cell empty"
            ns.append(node(f"c-{a}-{b}", x0 + j * cw, y, cw - 4, h - 4, rels or [""], cls, mono=True,
                            small=True, line_keys=rels or None))
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


MODELS = {"d1": overview, "d2": actors, "d3": stage_track, "d4": package_tree, "d5": relations_map,
          "d6": status_machine, "d7": guard, "d8": session}
STEPS = {"d7": 5, "d8": 6}
