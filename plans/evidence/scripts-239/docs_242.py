"""Plan 242 (FB-021, R122): the texts of the restated scan over prompt rows, and the CHANGELOG.
Idempotent: a pair already applied is skipped.

    python plans/evidence/scripts-239/docs_242.py
"""
from pathlib import Path

R = Path(__file__).resolve().parents[3]
EDITS = {
    "plugins/tamheed/references/handoff.md": [(
        "over EVERY Approved `prompt` row of the package (`PRT-NNN.body`). The tool-owned spans are\n",
        "over EVERY Approved `prompt` row of the package (`PRT-NNN.body`). Since v6.7 (plan 242, the\n"
        "field's FB-021) a `status-claim` is scanned in a kickoff prompt only. A phase or situational\n"
        "prompt states the conditions to enter or leave work, and a condition stays true as written.\n"
        "An `id-dense` paragraph with a label in it, or in the three lines before it, reads\n"
        "`labeled: true`. The tool-owned spans are\n")],
    "plugins/tamheed/references/prompt-templates.md": [(
        "engine/dependency upgrade + baseline regen, bug triage, release prep, deviation ADR, status report.",
        "engine/dependency upgrade + baseline regen, bug triage, release prep, deviation ADR, status report.\n"
        "A phase or situational prompt may state its conditions with ids and status words, such as\n"
        "\"Pass: `AC-004` Met\". `handoff_emit` reads status claims in a kickoff prompt only (v6.7).")],
}
ENTRY = (
    "### Changed\n\n"
    "- **Status claims in prompt rows are scanned in kickoff prompts only (plan 242, the field's\n"
    "  FB-021, R122).** A phase or situational prompt states the conditions to enter or leave\n"
    "  work, such as \"PH-1 is Implemented\" or \"Pass: AC-004 Met\". The `restated_content` scan\n"
    "  read 24 such lines in the field's prompts as status copies. The target's `CLAUDE.md` and\n"
    "  `AGENTS.md` keep the full scan. An `id-dense` paragraph that names its live form reads\n"
    "  `labeled: true`.\n\n")
for rel, pairs in EDITS.items():
    path = R / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in text:
            continue
        assert text.count(old) == 1, (rel, text.count(old), old[:60])
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="\n")
log = R / "CHANGELOG.md"
text = log.read_text(encoding="utf-8")
if "(plan 242," not in text:
    anchor = "### Fixed\n\n"
    assert text.index(anchor) < text.index("## [6.6.0]")
    text = text.replace(anchor, ENTRY + anchor, 1)
    log.write_text(text, encoding="utf-8", newline="\n")
print("docs 242 written")
