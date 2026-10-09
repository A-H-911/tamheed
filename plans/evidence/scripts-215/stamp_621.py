"""Plan 215: stamp 6.2.1 on every version surface lint 8 reads, write the CHANGELOG entry, append
the stock guide's new body to stock-history.json, re-aim the two lab-tracker eval pins. Run from
the repository root, then `python docs/guide/build.py` (index.html carries the version) and the
fixture refresh (`refresh_lab_621.py`). The 213 pattern."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[3]
OLD, NEW, DATE = "6.2.0", "6.2.1", "2026-10-09"   # the UTC date of the release commit


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

# the two lab-tracker pins on the recorded fixture (refreshed by the engine in refresh_lab_621.py)
ev = R / "evals/evals.json"
sub_once(ev, '"tamheed v6.2.0"', '"tamheed v6.2.1"')
sub_once(ev, '"<meta name=\\"tamheed-version\\" content=\\"6.2.0\\">"', '"<meta name=\\"tamheed-version\\" content=\\"6.2.1\\">"')
sub_once(ev, "The guide followed the stamp: refresh_stock carried it to the 6.2.0 body that names nine discipline skills (plans 120, 127, 183, 189, 198, 210, 213).",
         "The guide followed the stamp: refresh_stock carried it to the 6.2.1 body that names nine discipline skills (plans 120, 127, 183, 189, 198, 210, 213, 215).")
sub_once(ev, "The guide followed the 6.2.0 stamp: refresh_stock carried it to the shipped body at the package root, whose history key landed with the stamp (plans 168, 173, 189, 198, 210, 213).",
         "The guide followed the 6.2.1 stamp: refresh_stock carried it to the shipped body at the package root, whose history key landed with the stamp (plans 168, 173, 189, 198, 210, 213, 215).")

# the CHANGELOG entry, above the newest heading
cl = R / "CHANGELOG.md"
t = cl.read_text(encoding="utf-8")
head = f"## [{OLD}] - 2026-10-08"
assert t.count(head) == 1
entry = f"""## [{NEW}] - {DATE}

**PATCH — one text for both G-COMPLETE scans (the field's FB-001, plans 214–215).** A planning
package on 6.2.0 journaled the `[NEEDS-CLARIFICATION]` marker it had just removed from a requirement,
and `gate_run` failed G-COMPLETE on that journal entry with no repair: the marker scan read every TEXT
column, the append-only journal included, while the placeholder scan had exempted the journal and the
verdict evidence since plan 038 and stripped code spans since plan 017. Both scans now read one source,
`_graded_text`: every entity table's TEXT columns minus `custom_attributes` and the report columns
(`progress_entries.entry`, `audit_verdicts.evidence`), live rows only (`Superseded` and `Obsolete`
rows are history), code spans stripped. A marker quoted in the journal, in verdict evidence or inside
backticks is a quotation. A bare marker on a live row still fails as before. The change only removes
matches: no package that passed fails after it. The repository's own demo sample
(`generated-samples/support-triage-agent-v2`), failing G-COMPLETE unseen on a backticked marker in
`PRT-002` since v6.0.0, passes and reads ready. No schema move: `schema_version` stays 8.

**For a live package (the migration note).** Nothing to run. A package failing G-COMPLETE on a
journal row, on verdict evidence or on a marker inside backticks passes at its next `gate_run` under
6.2.1. The field sets its feedback row `Resolved` with `resolved_in` 6.2.1 and the plan reference.

### Fixed
- G-COMPLETE's marker check skips the append-only report columns and strips code spans, as the
  placeholder scan always did. One text source (`_graded_text`) feeds both loops, so no third
  difference can grow between them (plan 046's rule).
- `clarifications-open` no longer counts a valid marker quoted in a journal entry, in verdict
  evidence or inside backticks (the line plan 046 deferred to a release note).
- The demo sample passes G-COMPLETE.

### Changed
- `quality-gates.md`, `governance.md`, the `package-writes` skill (the fact: the journal is a record,
  never graded; elsewhere quote a marker inside backticks), the server README and three docstrings,
  `docs/entities.md` and the repository's `CLAUDE.md` say both screens. The guide's gate sentence and
  FAQ answer, which already promised this, are now true as written.

"""
t = t.replace(head, entry + head)
cl.write_text(t, encoding="utf-8", newline="\n")
print("stamped", NEW)
