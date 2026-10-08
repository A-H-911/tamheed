"""Plan 213: stamp 6.2.0 on every version surface lint 8 reads, write the CHANGELOG entry, append
the stock guide's new body to stock-history.json, re-aim the two lab-tracker eval pins. Run from
the repository root, then `python docs/guide/build.py` (index.html carries the version) and the
fixture refresh (`refresh_lab_620.py`). The 210 pattern."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[3]
OLD, NEW, DATE = "6.1.0", "6.2.0", "2026-10-08"   # the UTC date of the release commit


def sub_once(path: Path, old: str, new: str) -> None:
    t = path.read_text(encoding="utf-8")
    assert t.count(old) == 1, (path, t.count(old), old[:60])
    path.write_text(t.replace(old, new), encoding="utf-8", newline="\n")


# plugin.json
sub_once(R / "plugins/tamheed/.claude-plugin/plugin.json", f'"version": "{OLD}"', f'"version": "{NEW}"')

# the prose surfaces: the line that names the current version, never the history lines
sub_once(R / "README.md", f"Claude Code plugin + MCP-backed agent skill · v{OLD}", f"Claude Code plugin + MCP-backed agent skill · v{NEW}")
sub_once(R / "README.md", f"**v6.x** (currently v{OLD}).", f"**v6.x** (currently v{NEW}).")
sub_once(R / "plugins/tamheed/server/README.md", f"Documents the tool surface as of **tamheed v{OLD}**.", f"Documents the tool surface as of **tamheed v{NEW}**.")
sub_once(R / "plugins/tamheed/skills/tamheed/SKILL.md", f"This skill documents tamheed **v{OLD}**", f"This skill documents tamheed **v{NEW}**")
sub_once(R / "plugins/tamheed/references/artifact-catalog.md", f"(tamheed v{OLD})", f"(tamheed v{NEW})")

# the stock operator guide: its title line, and the body lands WITH its history key (lint 9)
guide = R / "plugins/tamheed/prompts/README.md"
sub_once(guide, f"operator guide (tamheed v{OLD})", f"operator guide (tamheed v{NEW})")
hist_path = R / "plugins/tamheed/prompts/stock-history.json"
hist = json.loads(hist_path.read_text(encoding="utf-8"))
assert NEW not in hist["README.md"]
hist["README.md"][NEW] = guide.read_text(encoding="utf-8")
hist_path.write_text(json.dumps(hist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

# the two lab-tracker pins on the recorded fixture (refreshed by the engine in refresh_lab_620.py)
ev = R / "evals/evals.json"
sub_once(ev, '"tamheed v6.1.0"', '"tamheed v6.2.0"')
sub_once(ev, '"<meta name=\\"tamheed-version\\" content=\\"6.1.0\\">"', '"<meta name=\\"tamheed-version\\" content=\\"6.2.0\\">"')
sub_once(ev, "The guide followed the stamp: refresh_stock carried it to the 6.1.0 body that names nine discipline skills (plans 120, 127, 183, 189, 198, 210).",
         "The guide followed the stamp: refresh_stock carried it to the 6.2.0 body that names nine discipline skills (plans 120, 127, 183, 189, 198, 210, 213).")
sub_once(ev, "The guide followed the 6.1.0 stamp: refresh_stock carried it to the shipped body at the package root, whose history key landed with the stamp (plans 168, 173, 189, 198, 210).",
         "The guide followed the 6.2.0 stamp: refresh_stock carried it to the shipped body at the package root, whose history key landed with the stamp (plans 168, 173, 189, 198, 210, 213).")

# the CHANGELOG entry, above the newest heading
cl = R / "CHANGELOG.md"
t = cl.read_text(encoding="utf-8")
head = f"## [{OLD}] - 2026-10-04"
assert t.count(head) == 1
entry = f"""## [{NEW}] - {DATE}

**MINOR — the repository is wired to its package at birth (plans 212–213).** Until 6.1 nothing
pointed a repository at its package before stage 20's `handoff_emit`: the SessionStart hook finds a
package through the note span in the root `CLAUDE.md` or one `@` import, so a planning half ran with
no resume block, and the first `CLAUDE.md` a new repository got was the Tamheed note alone. Now
`package_create`, `package_adopt` and `package_open` on an unwired root write the recognized pointer
pattern: the root `CLAUDE.md` gets a stub (the package title, the operator's comment, the `AGENTS.md`
import when that file exists, the heading, the `@<package>/CLAUDE.md` line) or three lines appended
when it exists without a Tamheed section, and the package's own `CLAUDE.md` gets a planning-era note
in the exact shape the emit later rebuilds. The emit replaces that note without the hand-edit warning
and reports a note-only root. The resume block names its `half`, and the planning `next` names
`/tamheed:tamheed`. Results carry `wiring`. Only a served process writes the root (`_WIRE_ROOT`):
in-process callers leave the tree as they found it. No schema migration: `schema_version` stays 8,
the store's bytes do not move. Beyond the release stamp's own lines, the bundle changes in the server
and the four teaching files 212 names.

**For a live package (the migration note).** Nothing to run. The first `package_open` under 6.2.0 in
a repository whose root `CLAUDE.md` has no Tamheed section writes the pointer section (a stub when the
file is absent) and the package's own `CLAUDE.md` with the planning note, once; the result's `wiring`
names what moved. A repository already carrying the pointer or an inline note reads
`present/present`, and nothing is written.

### Added
- `_wire_project` in the server: the root pointer stub or section and the package's planning note at
  `package_create`, `package_adopt` and `package_open`; `wiring` in their results; `half` in the
  resume block (`package_open`, `server_info`, the hook).
- `handoff_emit`: the planning-era note is replaced in silence ("the planning-era note ... was
  replaced by the operating note"); a root whose first non-blank line is the Tamheed heading is
  reported "note-only", never rewritten.

### Changed
- The descriptions of `package_create`, `package_open`, `package_adopt` and `handoff_emit` name the
  wiring. `handoff.md`, `workflow.md` stage 1 and the agent-control template say the pointer is the
  engine's at birth. The guide's effects canvases for the three tools gain the `CLAUDE.md` write.

"""
t = t.replace(head, entry + head)
cl.write_text(t, encoding="utf-8", newline="\n")
print("stamped", NEW)
