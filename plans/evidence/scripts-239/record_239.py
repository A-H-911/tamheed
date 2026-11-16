"""Plan 239: copy the approved round plan into plans/, with no private path, and add the round's
section to the plan ledger above the standup section. Run once from the repository root.

    python plans/evidence/scripts-239/record_239.py <approved plan file>
"""
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[3]
src = Path(sys.argv[1]).read_text(encoding="utf-8")
src = src.replace("`C:\\Users\\ahammo\\Repos\\feedback.json`", "the field's export")
assert "C:\\Users" not in src, "a private path is left in the plan"
(R / "plans" / "239-field-round-6.7.0.md").write_text(src, encoding="utf-8", newline="\n")

ROWS = [
    ("239", "The round record and the rulings R121-R140", "238"),
    ("240", "FB-019: a closed set of true and false, compared by type", "239"),
    ("241", "FB-020: the settled rule, the blocked list, the advisory `blocks-lifted`", "239"),
    ("242", "FB-021: status claims scanned in kickoff prompts only; a labelled id-dense paragraph", "239"),
    ("243", "FB-017: `entity_export` runs `slate_read`", "239"),
    ("244", "FB-018: the browser check reads the page's shape first; one-round mode", "239"),
    ("245", "FB-015: the texts on a section that a register entry replaces", "239"),
    ("246", "Standup: `withdraw` and `regenerate`, migration 012, ADR-0004", "239"),
    ("247", "Acceptance, release 6.7.0, the two field briefs", "240-246"),
]
section = [
    "### Field round 6.7.0 -- plans 239-247 -> v6.7.0 (2026-11-16 ->; maintainer-executed)",
    "",
    "The second field handed up six rows on 6.6.0, and the operator asked for two standup actions:",
    "withdraw a recorded report, and regenerate a report. The record, with rulings R121-R140, is",
    "[field-round-6.7.0-record.md](evidence/field-round-6.7.0-record.md). Every plan row links to",
    "the one approved plan.",
    "",
    "| # | Plan | Depends on | Status |",
    "|---|---|---|---|",
]
for num, title, dep in ROWS:
    status = "in progress on `round/6.7.0`" if num == "239" else "planned"
    section.append(f"| {num} | [{title}](239-field-round-6.7.0.md) | {dep} | {status} |")
ledger = R / "plans" / "README.md"
text = ledger.read_text(encoding="utf-8")
anchor = "### Standup report -- plans 232-237"
assert text.count(anchor) == 1
ledger.write_text(text.replace(anchor, "\n".join(section) + "\n\n" + anchor), encoding="utf-8")
print("plan and ledger written")
