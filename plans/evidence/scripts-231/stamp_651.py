"""Plan 231: stamp 6.5.1 on every version surface that lint 8 reads, turn the CHANGELOG's
`[Unreleased]` block into the 6.5.1 entry, add the stock guide's body to stock-history.json
under its key (lint 9), and re-aim the lab-tracker eval pins. Run once from the repository
root, then `python docs/guide/build.py` and `refresh_lab_651.py`. After `stamp_650.py`.
"""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[3]
OLD, NEW, DATE = "6.5.0", "6.5.1", "2026-11-15"      # the UTC date of the release commit


def sub_once(path: Path, old: str, new: str) -> None:
    t = path.read_text(encoding="utf-8")
    assert t.count(old) == 1, (path, t.count(old), old[:60])
    path.write_text(t.replace(old, new), encoding="utf-8", newline="\n")


def sub_prefix(path: Path, start: str, old: str, new: str) -> None:
    """Replace `old` by `new` in the one line that holds `start`."""
    lines = path.read_text(encoding="utf-8").split("\n")
    hits = [i for i, line in enumerate(lines) if start in line and old in line]
    assert len(hits) == 1, (path, start[:40], len(hits))
    lines[hits[0]] = lines[hits[0]].replace(old, new)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


sub_once(R / "plugins/tamheed/.claude-plugin/plugin.json", f'"version": "{OLD}"', f'"version": "{NEW}"')

# the prose surfaces: the line that names the current version, never a history line
sub_once(R / "README.md", f"Claude Code plugin + MCP-backed agent skill · v{OLD}",
         f"Claude Code plugin + MCP-backed agent skill · v{NEW}")
sub_once(R / "README.md", f"**v6.x** (currently v{OLD}).", f"**v6.x** (currently v{NEW}).")
sub_once(R / "plugins/tamheed/server/README.md", f"Documents the tool surface as of **tamheed v{OLD}**.",
         f"Documents the tool surface as of **tamheed v{NEW}**.")
sub_once(R / "plugins/tamheed/skills/tamheed/SKILL.md", f"This skill documents tamheed **v{OLD}**",
         f"This skill documents tamheed **v{NEW}**")
sub_once(R / "plugins/tamheed/references/artifact-catalog.md", f"(tamheed v{OLD})", f"(tamheed v{NEW})")

# the stock operator guide: its title line alone, WITH its history key (lint 9)
guide = R / "plugins/tamheed/prompts/README.md"
sub_once(guide, f"operator guide (tamheed v{OLD})", f"operator guide (tamheed v{NEW})")
hist_path = R / "plugins/tamheed/prompts/stock-history.json"
hist = json.loads(hist_path.read_text(encoding="utf-8"))
assert NEW not in hist["README.md"]
hist["README.md"][NEW] = guide.read_text(encoding="utf-8")
hist_path.write_text(json.dumps(hist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

# the lab-tracker pins on the recorded fixture (the engine refreshes it in refresh_lab_651.py)
ev = R / "evals/evals.json"
sub_once(ev, f'"tamheed v{OLD}"', f'"tamheed v{NEW}"')
sub_once(ev, f'"<meta name=\\"tamheed-version\\" content=\\"{OLD}\\">"',
         f'"<meta name=\\"tamheed-version\\" content=\\"{NEW}\\">"')
sub_prefix(ev, "The guide followed the stamp: refresh_stock carried it to the", f"the {OLD} body", f"the {NEW} body")
sub_prefix(ev, "The guide followed the stamp: refresh_stock carried it to the", "220, 229).", "220, 229, 231).")
sub_prefix(ev, f"The guide followed the {OLD} stamp:", f"the {OLD} stamp", f"the {NEW} stamp")

# the CHANGELOG: the [Unreleased] block becomes the 6.5.1 entry, with its head
cl = R / "CHANGELOG.md"
t = cl.read_text(encoding="utf-8")
start, end = t.index("## [Unreleased]\n"), t.index(f"## [{OLD}] - ")
body = t[start + len("## [Unreleased]\n"):end]
assert body.count("### Fixed") == 1 and "plan 230" in body
head = f"""## [{NEW}] - {DATE}

**PATCH — one field row after the 6.5.0 upgrade (plans 230–231).** The first field handed up
one operator-confirmed row. Two more faults came from the rehearsals of the 6.5.0 briefs.

**For a live package.** No file changes form, and no migration runs. Update the plugin and
start the client again. Then run `handoff_emit(<repository root>, refresh_stock=true)` and
`export_html()`. A package that is still on 6.4.0 migrates as the 6.5.0 entry says, and its
journal row then carries a time. From 6.5.1 back to 6.5.0 the plugin goes back alone.
"""
cl.write_text(t[:start] + head + body + t[end:], encoding="utf-8", newline="\n")
print("stamped", NEW)
