"""Plan 226: add the two register families to the bundle's teaching surfaces and to the
repository's own lists. Run once from the repository root. A second run changes nothing:
every insert is skipped when its marker text is already in the file.

    python plans/evidence/scripts-226/docs_226.py
"""
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

CATALOG = (
    "| register | `REG-` | On-request | A project register: a record type that the plugin has no"
    " family for, such as a source authorization or an evidence finding (v6.5, plan 226). It"
    " DECLARES its fields under `custom_attributes.fields`, a list of"
    " `{name, required?, values?, refs?}`. `required` means the key is present and not null."
    " `values` is a set of text values. `refs` marks a reference: one id or a list of ids, and"
    " each names a row. The write refuses a malformed declaration. Declare a register for such"
    " records. Never store them as dependency, open-question or section rows |\n"
    "| register-entry | `ENT-` | On-request | One record of a register (`register_id`). The"
    " values of the declared fields live in its `custom_attributes`. The write refuses an"
    " undeclared key, a missing required field, a value outside the set, and a reference that"
    " names no row. A string of joined ids is never split. Born Proposed. Retire it with"
    " Superseded or Obsolete. The advisory `register-entries-conform` lists the live entries"
    " that the current declaration does not admit. Link an entry to other rows with"
    " `relates_to` edges. Read one register with"
    " `entity_query(\"register-entry\", register_id=...)` |\n")

GOVERNANCE_ROWS = (
    "| Project register | `REG-NNN` | registers |\n"
    "| Register entry | `ENT-NNN` | register_entries |\n")

GOVERNANCE_SECTION = """## Project registers — declared fields (v6.5)

A project keeps record types that no family holds: a source authorization, an evidence
finding, an interview topic. Declare a `register` row (`REG-`) for each such type. Never put
those records into dependency, open-question or section rows: the rows then fill registers
that mean something else, and nothing checks their fields.

A register DECLARES its fields under `custom_attributes.fields`. Each field is an object:

| Key | Meaning |
|---|---|
| `name` | The key that an entry uses. Required, and unique in the register. |
| `required` | `true` when every entry must carry the key with a value that is not null. An empty list, `false` and `0` are values. |
| `values` | A list of text values. An entry's value must be one of them. |
| `refs` | `true` when the value is a reference: one id or a list of ids. Each id must name a row. |

A field takes `values` or `refs`, never both. A field never takes the name of an entry
column, such as `title` or `body`. A field with neither accepts any value: text,
a list, a mapping, a number or a boolean. A string of joined ids is never split, because it
cannot be told from prose that names an id. Keep such a value in a plain field, or send a list.

A `register-entry` row (`ENT-`) is one record. It names its register (`register_id`), and the
values of the declared fields live in its `custom_attributes`. The write refuses an undeclared
key, a missing required field, a value outside the set, and a reference that names no row.
One refusal names every cause. The guard reads the row as it would be stored, so a partial
write and a `substitute` are judged as a full row is.

A declaration changes on the operator's word. The advisory `register-entries-conform` then
lists the live entries that the new declaration does not admit, with the cause per entry.
Retire an entry with `Superseded` or `Obsolete`. A write that retires a stored entry as it is
is not judged, so an entry that no longer fits can still be retired. Every other write is
judged: one that keeps the entry live, one that changes a value while it retires, and a row
born retired. So correct the values of a live entry in the same write that edits its title or
body. A register with no entry reads `indeterminate`. Link an entry to other rows with a
`relates_to` edge, or with a `refs` field. The review page shows one table per register, and
its columns are the declared fields.

A package written before v6.5 does not know the two families. The write then names the route:
`package_migrate`, whose staged registry-sync teaches the package both.

"""

NAMING_ROWS = (
    "| Project register | `REG-NNN` | REG-001 |\n"
    "| Register entry | `ENT-NNN` | ENT-001 |\n")

RULES_LINE = (
    "- A record type that no family holds takes a declared `register` (`REG-`) and its entries"
    " (`ENT-`). Never overload dependency, open-question or section rows with it.\n")

WRITES_SECTION = """## 7c. A project record type takes a register, never a borrowed family

The project keeps a record type that no family holds. Do not store it as dependency,
open-question or section rows with the fields in `custom_attributes`. Nothing checks such
fields, and the rows fill a register that means something else.

1. Write one `register` row (`REG-`). Declare its fields under `custom_attributes.fields`, as
   `references/governance.md` (Project registers) defines them.
2. Write one `register-entry` row (`ENT-`) per record, with `register_id` and the field values
   in `custom_attributes`. Send a reference as one id or as a list of ids.
3. Read the refusal. It names every cause at once: an undeclared key, a missing required
   field, a value outside the set, a reference that names no row.
4. Change a declaration only on the operator's word. Then read the rule
   `register-entries-conform`, and correct every entry that it lists.

A package written before v6.5 refuses the first write and names `package_migrate`. Close the
package, run the preview, and confirm on the operator's word.

"""

LIVENESS_ITEM = """23. **Register entries that no longer fit** (`register-entries-conform`, v6.5): the live
    `ENT-` rows that the current declaration of their register does not admit. The rule is
    emitted only when the package has a register. `problems` names the cause per entry.
    Correct the values of the entry. Change a declaration only on the operator's word.
    A retired entry is never listed.
"""

GATES_SENTENCE = """ `register-entries-conform` (v6.5) lists the live register
  entries that the current declaration of their register does not admit. It exists only when
  the package has a register."""

FRONT_DOOR = """**A record type that no family holds takes a declared register (`REG-`) and
its entries (`ENT-`), never borrowed rows** (v6.5). The register declares its fields, and the
write checks each entry against them. """

ENTITIES = """#### register (`REG-`) and register-entry (`ENT-`) — On-request

A project keeps record types that the plugin has no family for (v6.5, migration
`010_registers.sql`). One field project stored three such types as dependency, open-question
and section rows, with the fields in `custom_attributes`. Nothing checked the fields, and the
rows filled registers that mean something else. A register DECLARES its fields, and the write
checks each entry against them. The plugin holds no rule of any one project.

The declaration is the list under the register's `custom_attributes.fields`, and the values of
an entry live in its own `custom_attributes`. No new JSON column was added. The content gate
grades every other text column, so an allowed value such as `TBD` would fail it there. A
reference is one id or a list of ids: a string of joined ids cannot be told from prose. A
project-defined rule over the fields was not built, because a rule language is a second engine.

Both families take the standard statuses, and no transition needs the operator's word. The
write guard reads the status all the same. A stored entry is retired as it is without a
check. A write that leaves an entry live is checked, and so is a return from retirement.
An entry links to other rows by a `refs` field, by a `relates_to` edge, or by `supersedes`
to another entry.

```mermaid
stateDiagram-v2
    [*] --> Proposed : the agent writes an entry - the write checks it against the declaration
    Proposed --> Approved : the record stands
    Proposed --> Rejected : it was only a draft
    Approved --> Superseded : another entry replaces it - a supersedes edge names the successor
    Approved --> Obsolete : the record no longer applies
    Approved --> Approved : register-entries-conform names it when the declaration no longer admits it
```

"""


def insert_after_line(text: str, starts: str, new: str, marker: str) -> str:
    if marker in text:
        return text
    at = text.index("\n" + starts) + 1
    end = text.index("\n", at) + 1
    return text[:end] + new + text[end:]


def insert_before(text: str, anchor: str, new: str, marker: str) -> str:
    if marker in text:
        return text
    at = text.index(anchor)
    return text[:at] + new + text[at:]


def liveness(text: str) -> str:
    if "`register-entries-conform`" in text:
        return text
    renumbered = text.replace("\n23. Close the sweep:", "\n24. Close the sweep:")
    at = renumbered.index("24. Close the sweep:")
    return renumbered[:at] + LIVENESS_ITEM + renumbered[at:]


def gates(text: str) -> str:
    if "`register-entries-conform`" in text:
        return text
    return text.replace("has rows of that family.", "has rows of that family." + GATES_SENTENCE, 1)


def scheme(text: str) -> str:
    if "`REG-`" in text:
        return text
    return (text.replace("`LL-`, `SKL-`, `FB-`, `PRT-`.", "`LL-`, `SKL-`, `FB-`, `PRT-`, `REG-`,\n"
                         "  `ENT-`.")
            .replace("is a list of 36 names", "is a list of 38 names"))


def edit(path: str, fn) -> None:
    p = ROOT / path
    old = io.open(p, encoding="utf-8").read()
    new = fn(old)
    if new != old:
        io.open(p, "w", encoding="utf-8", newline="\n").write(new)
    print(("changed  " if new != old else "unchanged"), path)


def main() -> int:
    edit("plugins/tamheed/references/artifact-catalog.md",
         lambda t: insert_after_line(t, "| feedback | `FB-`", CATALOG, "| register | `REG-`"))
    edit("plugins/tamheed/references/governance.md",
         lambda t: insert_before(
             insert_after_line(t, "| Feedback (upstream feedback / local tool) | `FB-NNN`",
                               GOVERNANCE_ROWS, "| Project register | `REG-NNN`"),
             "## Execution gate outcomes", GOVERNANCE_SECTION, "## Project registers"))
    edit("plugins/tamheed/templates/naming-conventions.template.md",
         lambda t: insert_after_line(t, "| Feedback (upstream feedback / local tool) | `FB-NNN`",
                                     NAMING_ROWS, "| Project register | `REG-NNN`"))
    edit("plugins/tamheed/references/artifact-rules.md",
         lambda t: insert_after_line(t, "- Prefer one well-populated register over several thin",
                                     RULES_LINE, "takes a declared `register`"))
    edit("plugins/tamheed/skills/package-writes/SKILL.md",
         lambda t: insert_before(t, "## 8. Set a scope change to `Merged` last",
                                 WRITES_SECTION, "## 7c. A project record type"))
    edit("plugins/tamheed/skills/register-liveness/SKILL.md", liveness)
    edit("plugins/tamheed/references/quality-gates.md", gates)
    edit("plugins/tamheed/skills/tamheed/SKILL.md",
         lambda t: insert_before(t, "**A function the tools lack is a `feedback` row",
                                 FRONT_DOOR, "takes a declared register (`REG-`)"))
    edit("docs/entities.md",
         lambda t: insert_before(t, "#### lesson (`LL-`)", ENTITIES, "#### register (`REG-`)"))
    edit("CLAUDE.md", scheme)
    return 0


if __name__ == "__main__":
    sys.exit(main())
