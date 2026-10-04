"""Build index.html — the bilingual Tamheed user guide — from the live engine plus content.py.

    python docs/guide/build.py            # write <repo>/index.html (LF, UTF-8)
    python docs/guide/build.py --check    # exit 1 if index.html is not the fresh build
    python docs/guide/build.py --missing  # list content ids still lacking EN or AR prose

index.html is generated: edit docs/guide/content.py (prose) or the engine (structure), then rebuild.
tests/test_user_guide.py holds the byte-twin and the coverage checks; check.py runs it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import content  # noqa: E402
import diagrams  # noqa: E402
import extract  # noqa: E402
import render  # noqa: E402

OUT = extract.REPO / "index.html"
FIG_DIR = extract.REPO / "docs" / "guide" / "figures"   # plan 203: the per-item figures, sibling files
CSS = (HERE / "guide.css").read_text(encoding="utf-8")
JS = (HERE / "guide.js").read_text(encoding="utf-8")

# Derived-id prefixes the page must render for every member (a family the renderer silently
# dropped would otherwise pass the coverage test).
MUST_RENDER = ("type.", "table.", "tool.", "param.", "gate.", "rule.", "rel.", "skill.", "stage.",
               "mode.", "profile.", "lint.", "suite.", "event.", "trigger.", "view.", "review.", "vocab.")


def css_tokens(css: str) -> dict[str, dict[str, str]]:
    """The colour tokens of both themes, read from the stylesheet's :root blocks (one source)."""
    def block(start: str) -> dict[str, str]:
        i = css.index(start)
        j = css.index("}", i)
        return dict(re.findall(r"--([\w-]+):\s*([^;]+);", css[i:j]))
    return {"light": block(":root {"), "dark": block(':root[data-theme="dark"] {')}


def build() -> tuple[str, list[str], dict[str, bytes]]:
    """Returns (html, required content ids, the figure files). Deterministic: no clock, no
    unsorted enumeration."""
    f = extract.facts()
    html = render.render_page(f, content.TEXT, CSS, JS)
    geometry = diagram_problems(f)
    assert not geometry, "diagram geometry: " + "; ".join(geometry[:12])
    required = list(render.USED_IDS)
    tokens = css_tokens(CSS)
    figures: dict[str, bytes] = {}
    for fid, model, caption_cid in render.FIGURES:
        for lg in ("en", "ar"):
            resolve = lambda cid, lg=lg: content.TEXT.get(cid, {}).get(lg) or cid
            title = content.TEXT.get(caption_cid, {}).get(lg) or caption_cid
            for theme in ("light", "dark"):
                name = f"{fid}-{lg}{'-dark' if theme == 'dark' else ''}.svg"
                svg = diagrams.svg_file(model, rtl=(lg == "ar"), lang=lg, resolve=resolve, title=title,
                                        tokens=tokens[theme])
                figures[name] = (svg + "\n").encode("utf-8")
    derived = extract.derived_ids(f)
    missing_render = [d for d in derived if d.startswith(MUST_RENDER) and d not in required]
    assert not missing_render, f"derived ids never rendered: {missing_render[:10]}"
    for s in f["stages"]["stages"]:  # the Arabic title rides beside the derived English one
        cid = f"stagetitle.{s['n']:02d}"
        if cid not in required:
            required.append(cid)
        en = content.TEXT.get(cid, {}).get("en")
        assert en in (None, s["title"]), f"{cid}: content says {en!r}, workflow.md says {s['title']!r}"
    for cid, file_text in extract.vocabulary_cells(f["vocabulary"]):  # plan 188: the EN cell IS the file's
        en = content.TEXT.get(cid, {}).get("en")
        assert en in (None, file_text), f"{cid}: content says {en!r}, vocabulary.md says {file_text!r}"
    return html, required, figures


def diagram_problems(f: dict) -> list[str]:
    """Every diagram, both copies, through diagrams.lint (the operator's drawing bar); the file
    figures also through the label-width check (they render in fallback fonts)."""
    out: list[str] = []
    for did in sorted(diagrams.MODELS):
        model = diagrams.MODELS[did](f)
        for lg in ("en", "ar"):
            resolve = lambda cid, lg=lg: content.TEXT.get(cid, {}).get(lg) or cid
            out += [f"{lg}: {p}" for p in diagrams.lint(model, rtl=(lg == "ar"), resolve=resolve)]
    for fid in sorted(diagrams.FILE_MODELS):
        model = diagrams.FILE_MODELS[fid](f)
        for lg in ("en", "ar"):
            resolve = lambda cid, lg=lg: content.TEXT.get(cid, {}).get(lg) or cid
            out += [f"{lg}: {p}" for p in diagrams.lint(model, rtl=(lg == "ar"), resolve=resolve)]
            out += [f"{lg}: {p}" for p in diagrams.label_problems(model, resolve)]
    return out


def stale_figures(figures: dict[str, bytes]) -> list[str]:
    """Files in the folder that differ from the fresh build, are missing, or are strays."""
    on_disk = {p.name: p.read_bytes() for p in FIG_DIR.glob("*.svg")} if FIG_DIR.is_dir() else {}
    out = [n for n, data in figures.items() if on_disk.get(n) != data]
    out += [f"{n} (stray)" for n in on_disk if n not in figures]
    return sorted(out)


def missing(required: list[str]) -> list[tuple[str, str]]:
    out = []
    for cid in required:
        entry = content.TEXT.get(cid, {})
        for lg in ("en", "ar"):
            if not entry.get(lg):
                out.append((cid, lg))
    return out


def orphans(required: list[str]) -> list[str]:
    req = set(required)
    return sorted(k for k in content.TEXT if k not in req)


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    html, required, figures = build()
    if "--missing" in argv:
        miss = missing(required)
        by_prefix: dict[str, int] = {}
        for cid, _lg in miss:
            by_prefix[cid.split(".")[0]] = by_prefix.get(cid.split(".")[0], 0) + 1
        for cid, lg in miss:
            print(f"{cid}\t{lg}")
        print(f"-- {len(miss)} missing strings over {len({c for c, _ in miss})} ids, by prefix: {by_prefix}")
        orph = orphans(required)
        if orph:
            print(f"-- {len(orph)} orphan content ids: {orph[:20]}")
        print(f"-- required ids: {len(required)}, content ids: {len(content.TEXT)}")
        return 1 if miss or orph else 0
    data = html.encode("utf-8")
    if "--check" in argv:
        current = OUT.read_bytes() if OUT.exists() else b""
        stale = stale_figures(figures)
        if current == data and not stale:
            print(f"index.html and {len(figures)} figure files are the fresh build")
            return 0
        print("index.html or the figures folder is STALE — run: python docs/guide/build.py", stale[:6])
        return 1
    OUT.write_bytes(data)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for name, blob in figures.items():
        (FIG_DIR / name).write_bytes(blob)
    for p in FIG_DIR.glob("*.svg"):
        if p.name not in figures:
            p.unlink()   # a stray from an older build: the folder is exactly the generated set
    print(f"wrote {OUT} ({len(data):,} bytes, {len(required)} content ids, {len(missing(required))} strings missing)"
          f" and {len(figures)} figure files under {FIG_DIR.relative_to(extract.REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
