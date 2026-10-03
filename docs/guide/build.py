"""Build index.html — the bilingual Tamheed user guide — from the live engine plus content.py.

    python docs/guide/build.py            # write <repo>/index.html (LF, UTF-8)
    python docs/guide/build.py --check    # exit 1 if index.html is not the fresh build
    python docs/guide/build.py --missing  # list content ids still lacking EN or AR prose

index.html is generated: edit docs/guide/content.py (prose) or the engine (structure), then rebuild.
tests/test_user_guide.py holds the byte-twin and the coverage checks; check.py runs it.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import content  # noqa: E402
import diagrams  # noqa: E402
import extract  # noqa: E402
import render  # noqa: E402

OUT = extract.REPO / "index.html"
CSS = (HERE / "guide.css").read_text(encoding="utf-8")
JS = (HERE / "guide.js").read_text(encoding="utf-8")

# Derived-id prefixes the page must render for every member (a family the renderer silently
# dropped would otherwise pass the coverage test).
MUST_RENDER = ("type.", "table.", "tool.", "param.", "gate.", "rule.", "rel.", "skill.", "stage.",
               "mode.", "profile.", "lint.", "suite.", "event.", "trigger.", "view.", "review.")


def build() -> tuple[str, list[str]]:
    """Returns (html, required content ids). Deterministic: no clock, no unsorted enumeration."""
    f = extract.facts()
    html = render.render_page(f, content.TEXT, CSS, JS)
    geometry = diagram_problems(f)
    assert not geometry, "diagram geometry: " + "; ".join(geometry[:12])
    required = list(render.USED_IDS)
    derived = extract.derived_ids(f)
    missing_render = [d for d in derived if d.startswith(MUST_RENDER) and d not in required]
    assert not missing_render, f"derived ids never rendered: {missing_render[:10]}"
    for s in f["stages"]["stages"]:  # the Arabic title rides beside the derived English one
        cid = f"stagetitle.{s['n']:02d}"
        if cid not in required:
            required.append(cid)
        en = content.TEXT.get(cid, {}).get("en")
        assert en in (None, s["title"]), f"{cid}: content says {en!r}, workflow.md says {s['title']!r}"
    return html, required


def diagram_problems(f: dict) -> list[str]:
    """Every diagram, both copies, through diagrams.lint (the operator's drawing bar)."""
    out: list[str] = []
    for did in sorted(diagrams.MODELS):
        model = diagrams.MODELS[did](f)
        for lg in ("en", "ar"):
            resolve = lambda cid, lg=lg: content.TEXT.get(cid, {}).get(lg) or cid
            out += [f"{lg}: {p}" for p in diagrams.lint(model, rtl=(lg == "ar"), resolve=resolve)]
    return out


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
    html, required = build()
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
        if current == data:
            print("index.html is the fresh build")
            return 0
        print("index.html is STALE — run: python docs/guide/build.py")
        return 1
    OUT.write_bytes(data)
    print(f"wrote {OUT} ({len(data):,} bytes, {len(required)} content ids, {len(missing(required))} strings missing)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
