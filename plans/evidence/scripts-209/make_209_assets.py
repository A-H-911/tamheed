"""Plan 209 (G11): the two-half paving mark with a return arc, drawn once and emitted as the plugin
icon, the three lockups, the user guide's favicon (the data URI in docs/guide/render.py) and the
proof page under plans/evidence/captures-209/. Run from the repository root:

    python plans/evidence/scripts-209/make_209_assets.py

The four SVGs and the favicon are byte-reproducible from this file; edit the mark here, never in
the emitted files."""
import re
from pathlib import Path
from urllib.parse import quote

R = Path(__file__).resolve().parents[3]
A = R / "plugins" / "tamheed" / "assets"
TAG = "PLAN THE GROUND, KEEP THE RECORD"


def mark(x, y, s, steps, slab, arc, arrow=None):
    """The mark at origin (x, y), unit s: three ascending steps (1.6 x 0.9), a thinner path slab
    after the top step (2.0 x 0.6), and an arc returning from the slab to above the first step with
    an arrowhead."""
    def r(ix, iy, w, h, fill):
        return (f'<rect x="{x + ix * s:.1f}" y="{y + iy * s:.1f}" width="{w * s:.1f}" height="{h * s:.1f}"'
                f' rx="{0.22 * s:.1f}" fill="{fill}"/>')
    parts = [
        r(0.0, 2.6, 1.6, 0.9, steps[0]),
        r(1.5, 1.3, 1.6, 0.9, steps[1]),
        r(3.0, 0.0, 1.6, 0.9, steps[2]),
        r(4.9, 0.15, 2.0, 0.6, slab),          # the paved path: thinner and longer than a step
    ]
    x0, y0 = x + 6.0 * s, y - 0.25 * s
    x1, y1 = x + 0.8 * s, y + 1.9 * s
    rad = 3.3 * s
    parts.append(f'<path d="M{x0:.1f} {y0:.1f} A{rad:.1f} {rad:.1f} 0 0 0 {x1:.1f} {y1:.1f}" fill="none"'
                 f' stroke="{arc}" stroke-width="{0.28 * s:.2f}" stroke-linecap="round"/>')
    ah = arrow or arc
    parts.append(f'<path d="M{x1 - 0.45 * s:.1f} {y1 - 0.15 * s:.1f} L{x1 + 0.45 * s:.1f} {y1 - 0.15 * s:.1f}'
                 f' L{x1:.1f} {y1 + 0.55 * s:.1f} Z" fill="{ah}"/>')
    return "\n  ".join(parts)


LIGHT = dict(steps=("#a5b4fc", "#818cf8", "#7c3aed"), slab="#a5b4fc", arc="#7c3aed")
DARK = dict(steps=("#4c1d95", "#7c3aed", "#a78bfa"), slab="#c4b5fd", arc="#a78bfa")
TILE = dict(steps=("#e0e7ff", "#c4b5fd", "#a78bfa"), slab="#ede9fe", arc="#ffffff")


def icon_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="Tamheed icon: the two-half paving mark with a return arc">
  <title>Tamheed icon</title>
  <desc>Three ascending paving steps (the planning half climbs), a flat slab continuing from the top step (the execution half walks the paved path), and an arc returning from the slab to the first step (the record flows back).</desc>
  {mark(4, 24, 8.0, **LIGHT)}
</svg>
'''


def lockup(kind, pal, word, word2, under, tagfill) -> str:
    desc = {"": "default", "-light": "for light backgrounds", "-dark": "for dark backgrounds"}[kind]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="24 52 842 200" width="842" height="200" role="img" aria-label="Tamheed">
  <title>Tamheed — تمهيد</title>
  <desc>The Tamheed logo ({desc}): the two-half paving mark (three ascending steps, a flat slab, an arc returning to the first step), the two-tone wordmark Tamheed beside the Arabic تمهيد on a shared baseline, a paved-path underline running into an arrow, and the tagline {TAG}.</desc>
  {mark(44, 75, 20, **pal)}
  <text x="196" y="142" font-family="'Segoe UI', system-ui, -apple-system, sans-serif" font-size="92" font-weight="800"><tspan fill="{word}">Tam</tspan><tspan fill="{word2}">heed</tspan></text>
  <text x="840" y="142" text-anchor="end" font-family="'Segoe UI', Tahoma, 'Noto Naskh Arabic', 'Geeza Pro', sans-serif" font-size="86" font-weight="700" fill="{word2}">تمهيد</text>
  <g fill="{under}">
    <rect x="44"  y="178" width="150" height="14" rx="7"/>
    <rect x="206" y="178" width="180" height="14" rx="7" opacity=".85"/>
    <rect x="398" y="178" width="180" height="14" rx="7" opacity=".7"/>
    <rect x="590" y="178" width="210" height="14" rx="7" opacity=".55"/>
    <path d="M808 170 L840 185 L808 200 Z" fill="{word2}"/>
  </g>
  <text x="442" y="232" text-anchor="middle" font-family="'Segoe UI', system-ui, -apple-system, sans-serif" font-size="24" font-weight="600" letter-spacing="5" fill="{tagfill}">{TAG}</text>
</svg>
'''


LOCKUPS = [
    ("", LIGHT, "#312e81", "#7c3aed", "#a5b4fc", "#6d28d9"),
    ("-light", LIGHT, "#312e81", "#7c3aed", "#a5b4fc", "#6d28d9"),
    ("-dark", DARK, "#e0e7ff", "#a78bfa", "#4c1d95", "#a78bfa"),
]


def favicon_href() -> str:
    fav = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
           '<rect width="32" height="32" rx="6" fill="#5b3fd6"/>'
           + mark(2.5, 12, 4.2, **TILE).replace("\n  ", "") + '</svg>')
    return "data:image/svg+xml," + quote(fav, safe="")


def proof_page(href: str) -> str:
    assets = "../../../plugins/tamheed/assets"
    return f'''<!doctype html><meta charset="utf-8"><title>Tamheed marks</title>
<style>body{{margin:0;font-family:system-ui}}.w{{background:#fff;padding:24px}}.d{{background:#15131f;padding:24px}}.i{{display:flex;gap:24px;align-items:center}}img{{display:block}}</style>
<div class="w" id="light"><img src="{assets}/logo-light.svg" width="842" alt="the light lockup"></div>
<div class="d" id="dark"><img src="{assets}/logo-dark.svg" width="842" alt="the dark lockup"></div>
<div class="w i" id="icons"><img src="{assets}/icon.svg" width="256" alt=""><img src="{assets}/icon.svg" width="64" alt=""><img src="{assets}/icon.svg" width="32" alt=""><img src="{assets}/icon.svg" width="16" alt=""></div>
<div class="w i" id="fav"><img src="{href}" width="64" alt="the favicon at 64"><img src="{href}" width="32" alt="at 32"><img src="{href}" width="16" alt="at 16"></div>
'''


def main() -> None:
    (A / "icon.svg").write_text(icon_svg(), encoding="utf-8", newline="\n")
    for kind, pal, word, word2, under, tagfill in LOCKUPS:
        (A / f"logo{kind}.svg").write_text(lockup(kind, pal, word, word2, under, tagfill), encoding="utf-8", newline="\n")
    href = favicon_href()
    rp = R / "docs" / "guide" / "render.py"
    text = rp.read_text(encoding="utf-8")
    m = re.search(r'<link rel="icon" href="data:image/svg\+xml,[^"]*">', text)
    assert m, "the favicon link in render.py"
    text = text[:m.start()] + f'<link rel="icon" href="{href}">' + text[m.end():]
    rp.write_text(text, encoding="utf-8", newline="\n")
    proof = R / "plans" / "evidence" / "captures-209" / "_logos.html"
    proof.parent.mkdir(parents=True, exist_ok=True)
    proof.write_text(proof_page(href), encoding="utf-8", newline="\n")
    print("wrote icon.svg, three lockups, the favicon in render.py and the proof page")


if __name__ == "__main__":
    main()
