"""Plan 227: add the two slate tools to the user guide's engine files. Run it AFTER the
line re-aim (`plans/evidence/scripts-221/shift_221.py`), which first restores those files
from the last commit. A second run changes nothing.

    python plans/evidence/scripts-227/guide_227.py

It adds the effects entries of `slate_export` and `slate_read` to `docs/guide/diagrams.py`,
with the server line of each fact found by its text, and it moves the tool-count pin in
`tests/test_user_guide.py` from 19 to 21.
"""
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SERVER = ROOT / "plugins" / "tamheed" / "server" / "tamheed_server.py"
DIAGRAMS = ROOT / "docs" / "guide" / "diagrams.py"
GUIDE_TEST = ROOT / "tests" / "test_user_guide.py"


def line_of(source: list, needle: str, after: int = 0) -> int:
    """The 1-based number of the first line at or after `after` that holds `needle`."""
    for number, text in enumerate(source, 1):
        if number >= after and needle in text:
            return number
    raise SystemExit(f"the server no longer holds: {needle!r}")


def main() -> int:
    source = io.open(SERVER, encoding="utf-8").read().split("\n")
    export = line_of(source, "def slate_export(")
    read = line_of(source, "def slate_read(")
    entries = (
        '    "slate_export": {\n'
        f'        "needs": [("@need.open", {line_of(source, "if guard := _need_open():", export)})],\n'
        f'        "reads": [("slates/*.spec.json", {line_of(source, "files = _slate_files(name)", export)}),\n'
        f'                  ("@cited_rows", {line_of(source, "slates.quote_rows(", export)})],\n'
        f'        "writes": [("slates/*.slate.json", {line_of(source, "emitted = {", export)}),\n'
        f'                   ("slates/*.html", {line_of(source, "emitted = {", export)})]}},\n'
        '    "slate_read": {\n'
        f'        "needs": [("@need.open", {line_of(source, "if guard := _need_open():", read)})],\n'
        f'        "reads": [("slates/*.answers.json", {line_of(source, "files = _slate_files(name)", read)}),\n'
        f'                  ("slates/*.slate.json", {line_of(source, "files = _slate_files(name)", read)}),\n'
        f'                  ("@cited_rows", {line_of(source, "slates.quote_rows(", read)})],\n'
        f'        "writes": [("@nothing", {read})]}},\n')
    text = io.open(DIAGRAMS, encoding="utf-8").read()
    if '"slate_export": {' not in text:
        anchor = '    "entity_export": {\n'
        at = text.index(anchor)
        end = text.index("\n}\n", at) + 1          # the closing brace of TOOL_EFFECTS
        text = text[:end] + entries + text[end:]
        io.open(DIAGRAMS, "w", encoding="utf-8", newline="\n").write(text)
        print("changed   docs/guide/diagrams.py")
    else:
        print("unchanged docs/guide/diagrams.py")
    test = io.open(GUIDE_TEST, encoding="utf-8").read()
    old = 'self.assertEqual(len(f["tools"]), 19)'
    if old in test:
        io.open(GUIDE_TEST, "w", encoding="utf-8", newline="\n").write(
            test.replace(old, 'self.assertEqual(len(f["tools"]), 21)'))
        print("changed   tests/test_user_guide.py")
    else:
        print("unchanged tests/test_user_guide.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
