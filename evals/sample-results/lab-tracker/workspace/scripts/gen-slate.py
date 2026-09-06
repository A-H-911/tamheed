#!/usr/bin/env python3
"""gen-slate.py — render a review slate from an `entity_export` file.

usage: python gen-slate.py <export.json> <out.html>

The export is the ONLY read path: the tool wrote it (digest-stamped); this script
never opens <package>/data/. After writing it VERIFIES (every statement appears in
the HTML byte-for-byte, html-escaped) and then CALIBRATES the verifier (LL-013):
one character of one statement is corrupted in memory and the same comparison MUST
fail — an uncalibrated verifier proves nothing.

exit 0 all checks pass · 1 a real verify failure · 2 not a tamheed export · 3 the
corrupted comparison passed (the verifier is blind).
"""
import html
import json
import sys
from pathlib import Path


def load_export(path: Path) -> dict:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        doc = {}
    if not isinstance(doc, dict) or "tamheed_export" not in doc:
        print(f"REFUSED: {path} is not a tamheed export (no 'tamheed_export' envelope) "
              "— export it with entity_export() first")
        sys.exit(2)
    return doc


def render(doc: dict) -> str:
    env = doc["tamheed_export"]
    parts = ["<!doctype html><meta charset='utf-8'><title>Review slate</title>",
             f"<h1>Review slate — package {html.escape(env['package'])}</h1>",
             f"<p>export digest <code>{html.escape(env['digest'])}</code> "
             f"(tool {html.escape(env['tool'])}, tamheed {html.escape(env['version'])})</p>"]
    for row in doc["result"]["rows"]:
        parts.append(f"<section id='{html.escape(row['id'])}'>"
                     f"<h2>{html.escape(row['id'])} — {html.escape(row['title'])}</h2>"
                     f"<pre>{html.escape(row['statement'])}</pre></section>")
    return "\n".join(parts) + "\n"


def statements_present(rows: list, html_bytes: bytes) -> list:
    """ids whose html-escaped statement is NOT in the page, byte-for-byte."""
    return [r["id"] for r in rows
            if html.escape(r["statement"]).encode("utf-8") not in html_bytes]


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    export, out = Path(sys.argv[1]), Path(sys.argv[2])
    doc = load_export(export)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(doc))
    print(f"wrote {out} ({len(doc['result']['rows'])} rows, digest {doc['tamheed_export']['digest']})")

    # VERIFY — re-read both files from disk, compare bytes.
    rows = load_export(export)["result"]["rows"]
    page = out.read_bytes()
    missing = statements_present(rows, page)
    for r in rows:
        print(f"verify {r['id']}: {'FAIL' if r['id'] in missing else 'PASS'} (statement byte-exact in HTML)")
    if missing:
        return 1

    # CALIBRATE — corrupt one character in memory; the same comparison must fail.
    victim = dict(rows[0])
    s = victim["statement"]
    victim["statement"] = ("X" if s[0] != "X" else "Y") + s[1:]
    detected = bool(statements_present([victim], page))
    print(f"calibrate {victim['id']}: corrupted 1 char -> mismatch "
          f"{'DETECTED' if detected else 'NOT DETECTED'}")
    if not detected:
        print("UNCALIBRATED: the verifier passed a corrupted statement — it proves nothing")
        return 3
    print("all checks pass; verifier calibrated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
