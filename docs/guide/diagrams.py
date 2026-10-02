"""Inline-SVG diagrams for the guide, drawn from small layout models.

Each diagram is a model: nodes placed on a grid, edges between node anchors, and labels that
are content ids resolved per language. `svg()` renders the model twice at build time: once as
drawn and once mirrored (x -> W - x - w) for the right-to-left copy, so flow direction follows
the reading direction while text, numbers and marks stay upright. No scripts inside the SVG;
interactivity hangs off data-key / data-step attributes the page script reads.
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


def node(key, x, y, w, h, label, cls="", mono=False, step=None, group="", links="", detail=None):
    return {"key": key, "x": x, "y": y, "w": w, "h": h, "label": label, "cls": cls, "mono": mono,
            "step": step, "group": group, "links": links, "detail": detail}


def edge(frm, to, label=None, cls="", key="", step=None, draw=True, side=None, bend=0, label_side="after"):
    return {"from": frm, "to": to, "label": label, "cls": cls, "key": key, "step": step,
            "draw": draw, "side": side, "bend": bend, "label_side": label_side}


def _anchor(n, side, rtl, W):
    x = W - n["x"] - n["w"] if rtl else n["x"]
    y, w, h = n["y"], n["w"], n["h"]
    if rtl and side in ("l", "r"):
        side = "r" if side == "l" else "l"
    return {"l": (x, y + h / 2), "r": (x + w, y + h / 2), "t": (x + w / 2, y),
            "b": (x + w / 2, y + h)}[side]


def _sides(a, b):
    """Pick the facing sides of two nodes from their relative position (pre-mirroring)."""
    ax, ay = a["x"] + a["w"] / 2, a["y"] + a["h"] / 2
    bx, by = b["x"] + b["w"] / 2, b["y"] + b["h"] / 2
    if abs(bx - ax) >= abs(by - ay):
        return ("r", "l") if bx > ax else ("l", "r")
    return ("b", "t") if by > ay else ("t", "b")


def _text(lines, x, y, rtl, cls, anchor="middle", lh=14):
    out = []
    n = len(lines)
    y0 = y - (n - 1) * lh / 2
    for i, line in enumerate(lines):
        extra = ' style="direction:ltr;unicode-bidi:isolate"' if cls and "num" in cls else ""
        out.append(f'<text class="lbl {cls}" x="{x:.1f}" y="{y0 + i * lh:.1f}" text-anchor="{anchor}"'
                   f' dominant-baseline="middle"{extra}>{esc(line)}</text>')
    return "".join(out)


def svg(model, rtl: bool, lang: str, resolve, title: str) -> str:
    """Render one copy. `resolve(cid) -> str` returns the label text in `lang`."""
    W, H = model["w"], model["h"]
    sfx = f"{model['id']}-{lang}"
    nodes = {n['key']: n for n in model['nodes']}
    parts = [f'<svg class="dia" lang="{lang}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}" xmlns="http://www.w3.org/2000/svg">',
             f'<defs><marker id="ar-{sfx}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="arrow"/></marker>'
             f'<marker id="ara-{sfx}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="arrow acc"/></marker></defs>']
    for e in model["edges"]:
        a, b = nodes[e["from"]], nodes[e["to"]]
        sa, sb = e["side"] or _sides(a, b)
        x1, y1 = _anchor(a, sa, rtl, W)
        x2, y2 = _anchor(b, sb, rtl, W)
        marker = "ara" if "acc" in e["cls"] else "ar"
        attrs = [f'class="edge {e["cls"]}{" draw" if e["draw"] else ""}{" step" if e["step"] else ""}"',
                 f'marker-end="url(#{marker}-{sfx})"', 'pathLength="1"']
        if e["key"]:
            attrs.append(f'data-key="{esc(e["key"])}"')
        if e["step"]:
            attrs.append(f'data-step="{e["step"]}"')
        if e["bend"]:
            bend = e["bend"]
            if sa in ("t", "b"):
                cx1, cy1, cx2, cy2 = x1, y1 + bend, x2, y2 + bend
            else:
                bx = -bend if rtl else bend
                cx1, cy1, cx2, cy2 = x1 + bx, y1, x2 + bx, y2
            d = f"M{x1:.1f} {y1:.1f} C{cx1:.1f} {cy1:.1f} {cx2:.1f} {cy2:.1f} {x2:.1f} {y2:.1f}"
        elif sa in ("t", "b") and abs(x1 - x2) > 1:
            my = (y1 + y2) / 2
            d = f"M{x1:.1f} {y1:.1f} L{x1:.1f} {my:.1f} L{x2:.1f} {my:.1f} L{x2:.1f} {y2:.1f}"
        elif sa in ("l", "r") and abs(y1 - y2) > 1:
            mx = (x1 + x2) / 2
            d = f"M{x1:.1f} {y1:.1f} L{mx:.1f} {y1:.1f} L{mx:.1f} {y2:.1f} L{x2:.1f} {y2:.1f}"
        else:
            d = f"M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}"
        parts.append(f'<path {" ".join(attrs)} d="{d}"/>')
        if e["label"]:
            lx, ly, anchor = (x1 + x2) / 2, (y1 + y2) / 2, "middle"
            if sa in ("l", "r") and abs(y1 - y2) < 1:
                ly -= 30                       # above the boxes the edge joins
            elif sa in ("t", "b") and abs(x1 - x2) < 1:
                lx += -8 if rtl else 8         # beside a vertical edge
                anchor = "end" if rtl else "start"
                if e["bend"]:
                    ly += e["bend"] * 0.75
            elif e["bend"] and sa in ("t", "b"):
                ly = max(y1, y2) + e["bend"] * 0.75 + 12 if e["bend"] > 0 else min(y1, y2) + e["bend"] * 0.75 - 6
            elif sa in ("l", "r"):                 # a stepped edge: beside its vertical segment
                after = (e["label_side"] == "after") != rtl
                lx = (x1 + x2) / 2 + (6 if after else -6)
                anchor = "start" if after else "end"
                ly -= 6
            else:
                ly -= 8
            if anchor == "start" and lx > W - 130:
                lx -= 12
                anchor = "end"
            parts.append(_text([resolve(e["label"])], lx, ly, rtl, "small", anchor))
    for n in model["nodes"]:
        x = W - n["x"] - n["w"] if rtl else n["x"]
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
        if n["h"] > 0:
            rx = n["h"] / 2 if "pill" in n["cls"] else 6
            parts.append(f'<rect class="box {n["cls"]}" x="{x:.1f}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" rx="{rx}"/>')
        label = n["label"]
        lines = label if isinstance(label, list) else resolve(label).split("\n")
        cls = "num" if n["mono"] else ("strong" if "strong" in n["cls"] else "")
        parts.append(_text(lines, x + n["w"] / 2, n["y"] + n["h"] / 2, rtl, cls))
        parts.append("</g>")
    for extra in model.get("extras", []):
        parts.append(extra(rtl, W))
    parts.append("</svg>")
    return "".join(parts)


# ----------------------------------------------------------------------------- models

def overview(f) -> dict:
    """D1 — brief to package to execution; the MCP server is the only write path."""
    ns = [
        node("brief", 10, 70, 90, 44, _L("overview.brief"), "pill"),
        node("A", 130, 20, 120, 44, _L("overview.understand"), "acc"),
        node("B", 130, 70, 120, 44, _L("overview.explore"), "acc"),
        node("C", 130, 120, 120, 44, _L("overview.plan"), "acc"),
        node("server", 310, 70, 120, 44, _L("overview.server"), "strong"),
        node("pkg", 500, 48, 130, 88, _L("overview.package"), ""),
        node("exec", 700, 70, 120, 44, _L("overview.executor"), "pill"),
        node("review", 500, 200, 130, 36, _L("overview.review"), ""),
    ]
    es = [
        edge("brief", "A", side=("r", "l")), edge("brief", "B", side=("r", "l")), edge("brief", "C", side=("r", "l")),
        edge("A", "server", side=("r", "l")), edge("B", "server", side=("r", "l")), edge("C", "server", side=("r", "l")),
        edge("server", "pkg", _L("overview.writes"), "acc"),
        edge("pkg", "exec", _L("overview.handoff")),
        edge("exec", "server", _L("overview.records"), "acc", bend=-60, side=("t", "t")),
        edge("pkg", "review", _L("overview.export"), side=("b", "t")),
    ]
    return {"id": "d1", "w": 840, "h": 250, "nodes": ns, "edges": es}


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
        edge("op", "plan", _L("actors.brief"), side=("l", "t")),
        edge("op", "exec", _L("actors.approves"), side=("r", "t")),
        edge("plan", "exec", _L("actors.handoff"), "acc", side=("r", "l")),
        edge("plan-does", "store", None, "", side=("b", "l"), bend=0),
        edge("exec-does", "store", None, "", side=("b", "r"), bend=0),
    ]
    return {"id": "d2", "w": 760, "h": 340, "nodes": ns, "edges": es}


def stage_track(f) -> dict:
    """D3 — the 22 stages in three lanes; human points and the loop-backs."""
    st = f["stages"]
    human = set(st["human"])
    loops = set(st["loops"])
    ns, es, extras = [], [], []
    lane_y = {"A": 40, "B": 120, "C": 200}
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
            if n in human:
                extras.append(_halo(x + 28, y + 12))
    es.append(edge("s8", "s9", "", "", side=("b", "t"), bend=0))
    es.append(edge("s15", "s16", "", "", side=("b", "t"), bend=0))
    lane_start = {n: p['stages'][0] for p in st['phases'] for n in p['stages']}
    for n in sorted(loops):
        es.append(edge(f"s{n}", f"s{max(lane_start[n], n - 4)}", _L("stages.loop"), "loop", side=("t", "t"), bend=-26))
    ns.append(node("legend-h", 560, 240, 190, 24, _L("stages.legend.human"), "good pill"))
    ns.append(node("legend-l", 360, 240, 190, 24, _L("stages.legend.loop"), "pill"))
    return {"id": "d3", "w": 760, "h": 280, "nodes": ns, "edges": es, "extras": extras}


def _halo(cx, cy):
    def draw(rtl, W):
        x = W - cx if rtl else cx
        return f'<circle class="halo" cx="{x:.1f}" cy="{cy:.1f}" r="11"/>'
    return draw


def package_tree(f) -> dict:
    """D4 — a package on disk and the executor repo it wires."""
    ns = [
        node("root", 10, 20, 150, 36, _L("package.root"), "acc strong"),
        node("data", 200, 10, 190, 48, _L("package.data"), "", links="write"),
        node("prompts", 200, 72, 190, 48, _L("package.prompts"), ""),
        node("review", 200, 134, 190, 48, _L("package.review"), ""),
        node("exports", 200, 196, 190, 48, _L("package.exports"), ""),
        node("csv", 200, 258, 190, 36, _L("package.csv"), ""),
        node("target", 470, 20, 150, 36, _L("package.target"), "strong"),
        node("mcp", 470, 80, 270, 40, _L("package.mcp"), ""),
        node("claude", 470, 134, 270, 48, _L("package.claude"), ""),
        node("tools", 10, 258, 150, 36, _L("package.tools"), "pill"),
    ]
    es = [
        edge("root", "data", side=("r", "l")), edge("root", "prompts", side=("r", "l")),
        edge("root", "review", side=("r", "l")), edge("root", "exports", side=("r", "l")),
        edge("root", "csv", side=("r", "l")),
        edge("target", "mcp", side=("b", "l"), bend=0), edge("target", "claude", side=("b", "l"), bend=0),
        edge("tools", "data", _L("package.flush"), "acc", side=("r", "l"), bend=0, label_side="before"),
    ]
    return {"id": "d4", "w": 760, "h": 310, "nodes": ns, "edges": es}


def relations_map(f) -> dict:
    """D5 — the four buckets the typed relations connect."""
    ns = [
        node("needs", 10, 20, 225, 60, _L("relations.needs"), "strong", group="needs"),
        node("decisions", 525, 20, 225, 60, _L("relations.decisions"), "strong", group="decisions"),
        node("work", 10, 230, 225, 60, _L("relations.work"), "strong", group="work"),
        node("verif", 525, 230, 225, 60, _L("relations.verification"), "strong", group="verif"),
        node("risk", 280, 125, 200, 60, _L("relations.risk"), "strong", group="risk"),
        node("scope", 295, 20, 170, 40, _L("relations.scope"), "pill", group="scope"),
        node("lesson", 295, 250, 170, 40, _L("relations.lesson"), "pill", group="lesson"),
    ]
    rel = {
        "derives_from": ("needs", "decisions", ("r", "l")),
        "implements": ("work", "needs", ("t", "b")),
        "satisfies": ("work", "needs", ("r", "l")),
        "verifies": ("verif", "needs", ("l", "r")),
        "tests": ("verif", "work", ("l", "r")),
        "mitigates": ("work", "risk", ("r", "l")),
        "discharges": ("verif", "risk", ("t", "b")),
        "blocked_by": ("work", "decisions", ("t", "b")),
        "scope_adds": ("scope", "needs", ("l", "r")),
        "scope_modifies": ("scope", "work", ("b", "t")),
        "scope_removes": ("scope", "verif", ("b", "t")),
        "amends": ("scope", "decisions", ("r", "l")),
        "learned_from": ("lesson", "work", ("l", "r")),
        "carries": ("work", "work", ("b", "b")),
        "supersedes": ("decisions", "decisions", ("b", "b")),
    }
    es = []
    for r, (a, b, side) in rel.items():
        if a == b:
            continue
        es.append(edge(a, b, None, "", key=r, side=side, bend=0))
    return {"id": "d5", "w": 760, "h": 310, "nodes": ns, "edges": es, "self": ["carries", "supersedes"]}


def status_machine(f) -> dict:
    """D6 — the standard lifecycle with the Review / Implemented branch."""
    ns = [
        node("Draft", 10, 90, 100, 36, ["Draft"], "pill", mono=True),
        node("Proposed", 150, 90, 100, 36, ["Proposed"], "pill", mono=True),
        node("Approved", 290, 90, 110, 36, ["Approved"], "acc pill", mono=True),
        node("Review", 440, 150, 100, 36, ["Review"], "warn pill", mono=True),
        node("Implemented", 580, 90, 130, 36, ["Implemented"], "good pill", mono=True),
        node("Rejected", 150, 20, 100, 32, ["Rejected"], "bad pill", mono=True),
        node("Deferred", 150, 160, 100, 32, ["Deferred"], "pill", mono=True),
        node("Superseded", 440, 20, 110, 32, ["Superseded"], "pill", mono=True),
        node("Obsolete", 580, 20, 110, 32, ["Obsolete"], "pill", mono=True),
        node("note", 290, 200, 420, 44, _L("status.note"), "pill"),
    ]
    es = [
        edge("Draft", "Proposed"), edge("Proposed", "Approved"),
        edge("Approved", "Implemented", _L("status.verified"), "acc", side=("r", "l")),
        edge("Approved", "Review", _L("status.claimed"), "", side=("b", "l"), bend=0),
        edge("Review", "Implemented", _L("status.guard"), "acc", side=("r", "b"), bend=0),
        edge("Proposed", "Rejected", side=("t", "b")), edge("Proposed", "Deferred", side=("b", "t")),
        edge("Deferred", "Proposed", side=("l", "l"), bend=-30),
        edge("Approved", "Superseded", side=("t", "l")), edge("Implemented", "Superseded", side=("t", "r")),
        edge("Superseded", "Obsolete"),
    ]
    return {"id": "d6", "w": 760, "h": 260, "nodes": ns, "edges": es}


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
        edge("upsert", "rules", step=1), edge("rules", "pass", _L("guard.nofail"), "", step=3, side=("r", "l")),
        edge("rules", "fail", _L("guard.blocking"), "", step=3, side=("r", "l")),
        edge("pass", "impl", step=3), edge("fail", "force", _L("guard.operator"), "", step=4, side=("r", "l")),
        edge("force", "journal", step=5, side=("b", "t")), edge("force", "impl", _L("guard.past"), "acc", step=5, side=("t", "b")),
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
        node("resume", 10, 220, 730, 36, _L("session.resume"), "pill", step=6),
    ]
    es = [
        edge("hook", "orient", step=2), edge("orient", "work", step=3), edge("work", "sync", step=4),
        edge("sync", "handoff", _L("session.last"), "acc", step=5), edge("handoff", "close", step=6),
        edge("close", "resume", _L("session.next"), "", step=6, side=("b", "t")),
    ]
    return {"id": "d8", "w": 760, "h": 270, "nodes": ns, "edges": es}


MODELS = {"d1": overview, "d2": actors, "d3": stage_track, "d4": package_tree, "d5": relations_map,
          "d6": status_machine, "d7": guard, "d8": session}
STEPS = {"d7": 5, "d8": 6}
