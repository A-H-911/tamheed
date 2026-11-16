"""Plan 245 (the field's FB-015, R124): the texts that name a `supersedes` edge for a retired
section now say what to do when a register ENTRY replaces it. `supersedes` stays within one
family, so the section is retired with no edge and linked another way. Idempotent.

    python plans/evidence/scripts-239/docs_245.py
"""
from pathlib import Path

R = Path(__file__).resolve().parents[3]
EDITS = {
    "plugins/tamheed/skills/package-writes/SKILL.md": [(
        "  `Superseded` or `Obsolete`. In the same batch, write a `supersedes` edge from the section that\n"
        "  replaces it. A live section has no status,",
        "  `Superseded` or `Obsolete`. When another SECTION replaces it, write a `supersedes` edge from\n"
        "  that section in the same batch. When a register ENTRY replaces it, write no such edge: the\n"
        "  engine refuses `supersedes` across two families. Link the entry by a `relates_to` edge, or\n"
        "  by a declared reference field that names the old section. A live section has no status,")],
    "plugins/tamheed/references/governance.md": [(
        "  follows its document. To retire one, set `lifecycle_status` to `Superseded` or `Obsolete`. Name\n"
        "  the section that replaces it with a `supersedes` edge from the kept section.",
        "  follows its document. To retire one, set `lifecycle_status` to `Superseded` or `Obsolete`. Name\n"
        "  the section that replaces it with a `supersedes` edge from the kept section. A register entry\n"
        "  that replaces a section takes no such edge (v6.7): `supersedes` stays within one family. Link\n"
        "  it by a `relates_to` edge, or by a declared reference field that names the old section."), (
        "`relates_to` edge, or with a `refs` field. The review page shows one table per register, and",
        "`relates_to` edge, or with a `refs` field. When entries replace document sections, retire each\n"
        "section with no edge, and keep its id in a declared field of the entry. The review page shows\n"
        "one table per register, and")],
    "plugins/tamheed/templates/governance.template.md": [(
        "  A `supersedes` edge from the kept section names what replaces it. A live section carries no status.",
        "  A `supersedes` edge from the kept section names what replaces it. A register entry that replaces\n"
        "  a section takes no such edge: link it by `relates_to` or a declared field. A live section carries\n"
        "  no status.")],
    "docs/entities.md": [(
        "An entry links to other rows by a `refs` field, by a `relates_to` edge, or by `supersedes`\n"
        "to another entry.",
        "An entry links to other rows by a `refs` field, by a `relates_to` edge, or by `supersedes`\n"
        "to another entry. An entry that replaces a document section never takes `supersedes` to it\n"
        "(v6.7): name the section in a declared field, or by a `relates_to` edge."), (
        "binds an explicit NULL for a column that an older row lacks. The kept section is named by a\n"
        "`supersedes` edge.",
        "binds an explicit NULL for a column that an older row lacks. The kept section is named by a\n"
        "`supersedes` edge. A register entry that replaces a section takes no such edge, because\n"
        "supersession stays within one family (v6.7).")],
    "plugins/tamheed/references/artifact-catalog.md": [(
        "Link an entry to other rows with `relates_to` edges.",
        "Link an entry to other rows with `relates_to` edges. An entry that replaces a section never"
        " takes `supersedes`: name the section in a declared field.")],
}
ENTRY = (
    "- **A section that a register entry replaces (plan 245, the field's FB-015, R124).** Three\n"
    "  texts said to retire a section with a `supersedes` edge. When an entry replaced the section,\n"
    "  the engine refused that edge, because supersession stays within one family. The texts now\n"
    "  say: retire the section with no edge, and link the entry by `relates_to` or a declared\n"
    "  field that names the old section. The 6.5 field briefs stay as they were published.\n\n")
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
if "(plan 245," not in text:
    anchor = "### Fixed\n\n"
    assert text.index(anchor) < text.index("## [6.6.0]")
    text = text.replace(anchor, anchor + ENTRY, 1)
    log.write_text(text, encoding="utf-8", newline="\n")
print("docs 245 written")
