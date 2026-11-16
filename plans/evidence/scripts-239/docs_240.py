"""Plan 240 (FB-019, R123): the texts that said a closed set holds text only, and the
[Unreleased] block of the CHANGELOG. Idempotent: a pair already applied is skipped.

    python plans/evidence/scripts-239/docs_240.py
"""
from pathlib import Path

R = Path(__file__).resolve().parents[3]
EDITS = {
    "plugins/tamheed/references/governance.md": [(
        "| `values` | A list of text values. An entry's value must be one of them. |",
        "| `values` | A list of text values, or of `true` and `false`. An entry's value must be"
        " one of them, with the same type: `1` is not `true`, and `\"true\"` is not `true`. |")],
    "plugins/tamheed/references/artifact-catalog.md": [(
        "`values` is a set of text values.",
        "`values` is a set of text values, or of `true` and `false`, matched by type.")],
    "docs/guide/content.py": [(
        "every field has a name, and a value set and `refs` never go together.",
        "every field has a name, and a value set and `refs` never go together. A value set"
        " holds text values, or `true` and `false`, and a value matches only by type."), (
        "لكل حقل اسم، ولا تجتمع مجموعة قيم مع `refs`.",
        "لكل حقل اسم، ولا تجتمع مجموعة قيم مع `refs`. وتضم مجموعة القيم نصوصًا، أو `true`"
        " و`false`، ولا تطابقها القيمة إلا من النوع نفسه.")],
}
UNRELEASED = """## [Unreleased]

### Added

- **A closed set of true and false (plan 240, the field's FB-019, R123).** A register field's
  `values` holds all text values, or `true` and `false`. A value is in the set only when its
  type matches too: `1` is not `true`, `0` is not `false`, and `"true"` is not `true`. A set of
  both kinds is refused. A boolean set reads `true / false` on the review page and in a refusal.

### Fixed

- **The retire door of a register entry compares by type (plan 240).** A write that retires a
  stored entry as it is passes unjudged. The door compared with `==`, so a value `1` passed as a
  stored `true`, and the changed value was stored with no check. It now compares the JSON text.

"""
for rel, pairs in EDITS.items():
    path = R / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in text:
            continue
        assert text.count(old) == 1, (rel, old[:50])
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="\n")
log = R / "CHANGELOG.md"
text = log.read_text(encoding="utf-8")
if "## [Unreleased]" not in text:
    assert text.count("## [6.6.0]") == 1
    text = text.replace("## [6.6.0]", UNRELEASED + "## [6.6.0]")
    log.write_text(text, encoding="utf-8", newline="\n")
print("docs 240 written")
