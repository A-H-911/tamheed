"""Plan 228: bring the repository's own documents up to the 6.5.0 round (plans 221-227). Run
once from the repository root. A second run changes nothing: every edit is skipped when its
marker text is already in the file.

    python plans/evidence/scripts-228/docs_228.py
"""
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

README_NEW = """**New in v6.5.** A record type that no family holds takes a declared **register** (`REG-`) and its
entries (`ENT-`). The register declares its fields, and the write checks each entry against them. A
document section can be retired, and it then leaves the scans. `trace_query` reads every link in one
call, in a fixed order with a total. It also returns the links that a foreign-key column holds, beside
the stored edges. `requirements-wired` reads the three legs of a requirement and names the missing
one. A refused value names the values that the column takes. The four gate outcomes are defined:
`Go`, `Hold`, `Redirect` and `Kill`. The lock survives a host rename inside one boot on Linux and
macOS. For a long interview, `slate_export` writes a local **interview page** from a slate of
questions. `slate_read` returns a checked transcript of the answers file that the operator saved. The
page runs one script named by hash, and the transcript is never the operator's word.

"""

README_PAIRS = [
    ("| `trace_query(entity_id, …)` | Typed traceability links |",
     "| `trace_query(entity_id?, …)` | The trace links of one entity, of one family, or all of them:"
     " the stored edges, and the links that a foreign-key column holds (v6.5) |"),
    ("| `handoff_emit / export_html` | Target-repository wiring + the HTML review surface |",
     "| `handoff_emit / export_html` | Target-repository wiring + the HTML review surface |\n"
     "| `slate_export / slate_read` | An interview page for the operator from a slate of questions,"
     " and a checked transcript of the answers file that the page saves (v6.5) |"),
    ("│   ├── server/                       # the Tamheed MCP server (the only write path into a package)",
     "│   ├── server/                       # the Tamheed MCP server (the only write path into a package),"
     " the review page, the interview page"),
]

ARCHITECTURE_PAIRS = [
    ("                  export_html · package_verify · entity_export — the ONLY write path into a",
     "                  export_html · slate_export · slate_read · package_verify · entity_export —\n"
     "                  the ONLY write path into a"),
]

CLAUDE_PAIRS = [
    ("├── server/                           # Tamheed MCP server + migrate_v3to4 + adopt + export_html + viewer.css",
     "├── server/                           # Tamheed MCP server + migrate_v3to4 + adopt + export_html + viewer.css\n"
     "│                                     #   + slate.py, slate.js, slate.css (the interview page, v6.5)"),
]


def pairs(replacements):
    def apply(text: str) -> str:
        for old, new in replacements:
            if new in text:
                continue
            if text.count(old) != 1:
                raise SystemExit(f"anchor not found once: {old[:70]!r}")
            text = text.replace(old, new)
        return text
    return apply


def readme(text: str) -> str:
    text = pairs(README_PAIRS)(text)
    if "**New in v6.5.**" not in text:
        anchor = "You follow along through the committed **`review.html`**"
        at = text.index(anchor)
        text = text[:at] + README_NEW + text[at:]
    return text


def edit(path: str, fn) -> None:
    p = ROOT / path
    old = io.open(p, encoding="utf-8").read()
    new = fn(old)
    if new != old:
        io.open(p, "w", encoding="utf-8", newline="\n").write(new)
    print(("changed  " if new != old else "unchanged"), path)


def main() -> int:
    edit("README.md", readme)
    edit("docs/architecture.md", pairs(ARCHITECTURE_PAIRS))
    edit("CLAUDE.md", pairs(CLAUDE_PAIRS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
