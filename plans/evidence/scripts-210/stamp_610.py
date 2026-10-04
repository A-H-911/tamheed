"""Plan 210: stamp 6.1.0 on every version surface lint 8 reads, write the CHANGELOG entry, append
the stock guide's new body to stock-history.json, re-aim the two lab-tracker eval pins. Run from
the repository root, then `python docs/guide/build.py` (index.html carries the version) and the
fixture refresh (`refresh_lab_610.py`)."""
import json
import re
from pathlib import Path

R = Path(__file__).resolve().parents[3]
OLD, NEW, DATE = "6.0.0", "6.1.0", "2026-10-04"   # the UTC date of the release commit


def sub_once(path: Path, old: str, new: str) -> None:
    t = path.read_text(encoding="utf-8")
    assert t.count(old) == 1, (path, t.count(old), old[:60])
    path.write_text(t.replace(old, new), encoding="utf-8", newline="\n")


# plugin.json
pj = R / "plugins/tamheed/.claude-plugin/plugin.json"
sub_once(pj, f'"version": "{OLD}"', f'"version": "{NEW}"')

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

# the two lab-tracker pins on the recorded fixture (refreshed by the engine in refresh_lab_610.py)
ev = R / "evals/evals.json"
sub_once(ev, '"tamheed v6.0.0"', '"tamheed v6.1.0"')
sub_once(ev, '"<meta name=\\"tamheed-version\\" content=\\"6.0.0\\">"', '"<meta name=\\"tamheed-version\\" content=\\"6.1.0\\">"')
sub_once(ev, "The guide followed the stamp: refresh_stock carried it to the 6.0.0 body that names nine discipline skills (plans 120, 127, 183, 189, 198).",
         "The guide followed the stamp: refresh_stock carried it to the 6.1.0 body that names nine discipline skills (plans 120, 127, 183, 189, 198, 210).")
sub_once(ev, "The guide followed the 6.0.0 stamp: refresh_stock carried it to the shipped body at the package root, whose history key landed with the stamp (plans 168, 173, 189, 198).",
         "The guide followed the 6.1.0 stamp: refresh_stock carried it to the shipped body at the package root, whose history key landed with the stamp (plans 168, 173, 189, 198, 210).")

# the CHANGELOG entry, above the newest heading
cl = R / "CHANGELOG.md"
t = cl.read_text(encoding="utf-8")
head = f"## [{OLD}] - 2026-10-04"
assert t.count(head) == 1
entry = f"""## [{NEW}] - {DATE}

**MINOR — the user guide round 2 (plans 201–210).** The generated user guide (`index.html`) gains
its figures: twelve workflow swimlanes, a relations figure and a data path per family, a trace path
for every family a gate or rule reads, the standard lifecycle, an effects canvas and a call-sequence
strip per tool, the gates pipeline and one figure per gate, the skills' citation matrix and
lifecycle map and a strip per skill. The figures are sibling files under `docs/guide/figures/`
(two languages, light and dark, `<picture>` with a script swap on the explicit toggle), derived from
the engine's own facts and from the bundle's text (the `Writes` and `Check` clauses of workflow.md,
the gate definitions table, the skills' bodies, a census of the server's `INSERT` statements); a
figure that claims a server line carries it, and the tests read those lines. The chrome: a numbered
two-level section list, the two-halves framing on the overview figures, the README image. No schema
migration: `schema_version` stays 8, the store's bytes do not move. The bundle changes in one place:
the brand marks.

**For a live package (the migration note).** Nothing to run. A package created under 6.0.0 keeps its
stock guide until the next `handoff_emit(..., refresh_stock=true)`, which carries the 6.1.0 title
line; the body is otherwise the 6.0.0 one.

### Added
- `docs/guide/figures/`: 724 SVG files for 181 figure ids, byte-twins of the generator's output,
  LF-pinned. `build.py --check` covers the folder; stray files are removed on build.
- The guide's readers of the bundle: `writes()` (the stages that write a table), `checks()` (the
  gates a stage's Check clause cites), `gate_defs()` (the definitions table), `inserters()` (which
  server function inserts into which table), `rule_tables()` (each readiness rule's population,
  from a readiness run), `skill_text()` (citations, tools and ceremony STOPs per skill).
- The brand mark: two halves and a return arc (three ascending paving steps, a path slab, an arc
  back to the first step), on `assets/icon.svg` (a Keystone arch until now), the three lockups and
  the guide's favicon; drawn once by `plans/evidence/scripts-209/make_209_assets.py`.

### Changed
- The tagline reads "Plan the ground, keep the record" on the lockups, the README, the guide's
  hero line and footer, and the assets README.
- The guide's overview figures show one agent with two halves; the section list is numbered with a
  second level; the status machine is drawn once for STD8 and once (D6) for STD9.

"""
t = t.replace(head, entry + head)
cl.write_text(t, encoding="utf-8", newline="\n")
print("stamped", NEW)
