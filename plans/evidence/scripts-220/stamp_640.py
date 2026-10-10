"""Plan 220: stamp 6.4.0 on every version surface lint 8 reads, write the CHANGELOG entry, append
the stock guide's new body to stock-history.json, re-aim the two lab-tracker eval pins. Run from
the repository root, then `python docs/guide/build.py` (index.html carries the version) and the
fixture refresh (`refresh_lab_640.py`). The 213/215/218 pattern."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[3]
OLD, NEW, DATE = "6.3.0", "6.4.0", "2026-10-10"   # the UTC date of the release commit (6.3.0's too)


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

# the two lab-tracker pins on the recorded fixture (refreshed by the engine in refresh_lab_640.py)
ev = R / "evals/evals.json"
sub_once(ev, '"tamheed v6.3.0"', '"tamheed v6.4.0"')
sub_once(ev, '"<meta name=\\"tamheed-version\\" content=\\"6.3.0\\">"', '"<meta name=\\"tamheed-version\\" content=\\"6.4.0\\">"')
sub_once(ev, "The guide followed the stamp: refresh_stock carried it to the 6.3.0 body that names nine discipline skills (plans 120, 127, 183, 189, 198, 210, 213, 215, 218).",
         "The guide followed the stamp: refresh_stock carried it to the 6.4.0 body that names nine discipline skills (plans 120, 127, 183, 189, 198, 210, 213, 215, 218, 220).")
sub_once(ev, "The guide followed the 6.3.0 stamp: refresh_stock carried it to the shipped body at the package root, whose history key landed with the stamp (plans 168, 173, 189, 198, 210, 213, 215, 218).",
         "The guide followed the 6.4.0 stamp: refresh_stock carried it to the shipped body at the package root, whose history key landed with the stamp (plans 168, 173, 189, 198, 210, 213, 215, 218, 220).")

# the CHANGELOG entry, above the newest heading (6.3.0 landed on the same UTC date)
cl = R / "CHANGELOG.md"
t = cl.read_text(encoding="utf-8")
head = f"## [{OLD}] - 2026-10-10"
assert t.count(head) == 1
entry = f"""## [{NEW}] - {DATE}

**MINOR — the review page reads (plans 219–220).** Every data table on `review.html` shared the
body's width, so a nine-column table showed its id column one character wide and every cell tall,
and the Resume handoff ran off the right edge. The exporter now emits a `<colgroup>` with one of three
constant classes per header, chosen by the header's kind (long prose, ids and enums, everything else
including dates, actors and titles) from code strings only. The stylesheet sizes the columns
(9/14/36rem) under a fixed table layout, lets a wide table scroll inside its fold under a header that
stays put (70vh), keeps text wrapping inside its column, lands a row link below the sticky navigation,
wraps the handoff in its panel, and lifts the height cap in print. R78 supersedes the C25 decision
("wrap in place, no horizontal scrolling") on the operator's word. No schema move: `schema_version`
stays 8, the store's bytes do not move. Beyond the release stamp's own lines, the bundle changes in
`server/export_html.py` and `server/viewer.css`. Two releases carry this UTC date: 6.3.0 earlier in
the day, this one after it.

**For a live package (the migration note).** Nothing to run. One `export_html()` under 6.4.0
re-renders the page; `package_verify` then reads `review_exported_by` 6.4.0. For the plugin's own
repository, `.claude/settings.json` is now committed with the marketplace declaration and the enable
(plan 219, R79): a clone that has no install record sees "enabled in project settings but isn't
installed here" in `/plugin` until `claude plugin install tamheed@tamheed --scope project` runs once.

### Added
- `export_html._col_class` and the `<colgroup>` in every table: one constant class per header by
  kind; a column-kind test and the C25 test re-aimed.
- `viewer.css`: `.tablewrap` scrolls on both axes inside its fold, `table-layout: fixed` with
  `col.w-s/w-m/w-l`, a sticky `thead th`, `tbody tr {{ scroll-margin-top }}`, `pre.handoff` wrapping,
  the print rule.

### Changed
- `README.md` and the guide's review-page sentence say a wide table scrolls inside its fold under a
  header that stays put, and long text wraps inside columns sized by kind.

"""
t = t.replace(head, entry + head)
cl.write_text(t, encoding="utf-8", newline="\n")
print("stamped", NEW)
