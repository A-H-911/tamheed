"""findings_37 cycle: the maintainer's read-only measurements M3 to M8, as one file.

Run from anywhere:  python plans/evidence/scripts-findings-37/m37.py
Every count is true at its run: the installed tree, the field page and the bundle all move.
Reads only. Writes nothing.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
HOME = Path.home()
CACHE = HOME / ".claude" / "plugins" / "cache" / "tamheed" / "tamheed"
FIELD_PAGE = Path(r"C:\Users\ahammo\Repos\acmp\tamheed-package\review.html")
TEXT = {".md", ".py", ".json", ".sql", ".css", ".svg"}


def m3_line_endings(version: str) -> None:
    root = CACHE / version
    files = [p for p in sorted(root.rglob("*")) if p.is_file()
             and ".in_use" not in p.parts and "__pycache__" not in p.parts]
    text = [p for p in files if p.suffix in TEXT]
    all_crlf = 0
    for p in text:
        lines = p.read_bytes().split(b"\n")
        body = lines[:-1] if lines and lines[-1] == b"" else lines
        if body and all(ln.endswith(b"\r") for ln in body):
            all_crlf += 1
    print(f"M3 installed {version}: files={len(files)} text={len(text)}"
          f" every-line-CRLF={all_crlf}")


def m4_bind_survey() -> None:
    word = re.compile(r"\b(?:bind|binds|binding|bound|unbound)\b", re.I)
    hits = []
    for p in sorted(BUNDLE.rglob("*")):
        if not p.is_file() or p.suffix not in {".md", ".py", ".sql"}:
            continue
        if "__pycache__" in p.parts or p.name == "stock-history.json":
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if word.search(line):
                hits.append((p.relative_to(REPO).as_posix(), n, line.strip()))
    print(f"M4 bundle lines naming bind/binds/binding/bound: {len(hits)}")
    negated = re.compile(r"(?:not|n['’]t|never|NOT)\s+bind\b", re.I)
    for rel, n, line in hits:
        if negated.search(line):
            print(f"   negated: {rel}:{n}: {line[:150]}")


def m5_field_page() -> None:
    if not FIELD_PAGE.is_file():
        print("M5 field page: not on this machine")
        return
    raw = FIELD_PAGE.read_bytes()
    text = raw.decode("utf-8", "replace")
    marks = [(m.start(), m.group(1)) for m in re.finditer(r'<section[^>]*id="([^"]+)"', text)]
    print(f"M5 field page: bytes={len(raw)} sections={len(marks)}")
    for (start, name), (end, _) in zip(marks, marks[1:] + [(len(text), "")]):
        print(f"   {end - start:>10}  {name}")
    head = text[:4096]
    for meta in ("tamheed-digest", "tamheed-version"):
        print(f"   head carries {meta}: {meta in head}")


def m6_review_current() -> None:
    for rel in ("lab/scenario.md", "evals/evals.json"):
        n = sum("review_current" in ln
                for ln in (REPO / rel).read_text(encoding="utf-8").splitlines())
        print(f"M6 review_current lines in {rel}: {n}")
    n = sum("review_current" in ln for p in sorted((REPO / "tests").glob("*.py"))
            for ln in p.read_text(encoding="utf-8").splitlines())
    print(f"M6 review_current lines in tests/*.py: {n}")


NEGATED = re.compile(
    r"(?:(?:does|do|did|will|would|can)\s+(?:not|NOT)|(?:doesn|don|didn|won)['’]t|never)"
    r"\s+bind\b[^.;:]{0,80}?\b(?:emit|handoff_emit|note|roster|rendered|pinn)")
CONTROLS = [
    (True, "approving and pinning a lesson does NOT bind it - `handoff_emit` in the SAME round"),
    (True, "an approved lesson does not bind until the emit has run"),
    (True, "a lesson doesn't bind until the note lists it"),
    (False, "a lesson does not bind until the operator approves it"),
    (False, "a Proposed lesson binds nothing and may be rejected freely"),
    (False, "a lesson does not bind until the operator approves it; the note renders it at"
            " the next emit"),
    (False, "A lesson does not bind until the operator approves it. The note renders it later."),
]


def m7_negated_pattern() -> None:
    good = sum(bool(NEGATED.search(s)) == want for want, s in CONTROLS)
    files = sorted(p for p in list(BUNDLE.rglob("*.md")) + list(BUNDLE.rglob("*.py"))
                   + list((REPO / "docs").glob("*.md")) if "__pycache__" not in p.parts)
    hits = []
    for p in files:
        prose = " ".join(" ".join(
            ln for ln in p.read_text(encoding="utf-8").splitlines()
            if not ln.lstrip().startswith(">")).split())
        hits += [(p.relative_to(REPO).as_posix(), m.group(0)) for m in NEGATED.finditer(prose)]
    print(f"M7 negated pattern: controls {good} of {len(CONTROLS)} as wanted;"
          f" files={len(files)} hits={len(hits)}")
    for rel, what in hits:
        print(f"   hit: {rel}: {what!r}")


def m8_export_mentions() -> None:
    roots = [BUNDLE / "skills", BUNDLE / "references", BUNDLE / "templates"]
    files = [p for r in roots for p in sorted(r.rglob("*.md"))] + [BUNDLE / "prompts" / "README.md"]
    n = 0
    for p in files:
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if "export_html" in line:
                n += 1
                print(f"   {p.relative_to(REPO).as_posix()}:{i}: {line.strip()[:120]}")
    print(f"M8 export_html lines in the teaching text: {n}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    versions = sorted((p.name for p in CACHE.iterdir() if p.is_dir()),
                      key=lambda v: tuple(int(x) for x in v.split("."))) if CACHE.is_dir() else []
    if versions:
        m3_line_endings(versions[-1])
    else:
        print("M3 installed tree: not on this machine")
    m4_bind_survey()
    m5_field_page()
    m6_review_current()
    m7_negated_pattern()
    m8_export_mentions()
    return 0


if __name__ == "__main__":
    sys.exit(main())
