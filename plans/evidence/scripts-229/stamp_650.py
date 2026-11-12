"""Plan 229: stamp 6.5.0 on every version surface that lint 8 reads, REPLACE the CHANGELOG's
`[Unreleased]` block with the 6.5.0 entry, change the stock guide's body and add it to
stock-history.json under its key, and re-aim the lab-tracker eval pins. Run once from the
repository root, then `python docs/guide/build.py` and the fixture refresh
(`refresh_lab_650.py`). The 213/215/218/220 pattern.
"""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[3]
OLD, NEW, DATE = "6.4.0", "6.5.0", "2026-11-12"      # the UTC date of the release commit


def sub_once(path: Path, old: str, new: str) -> None:
    t = path.read_text(encoding="utf-8")
    assert t.count(old) == 1, (path, t.count(old), old[:60])
    path.write_text(t.replace(old, new), encoding="utf-8", newline="\n")


def sub_prefix(path: Path, start: str, old: str, new: str) -> None:
    """Replace `old` by `new` in the one line that starts with `start`."""
    lines = path.read_text(encoding="utf-8").split("\n")
    hits = [i for i, line in enumerate(lines) if start in line and old in line]
    assert len(hits) == 1, (path, start[:40], len(hits))
    lines[hits[0]] = lines[hits[0]].replace(old, new)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


# plugin.json
sub_once(R / "plugins/tamheed/.claude-plugin/plugin.json", f'"version": "{OLD}"', f'"version": "{NEW}"')

# the prose surfaces: the line that names the current version, never the history lines
sub_once(R / "README.md", f"Claude Code plugin + MCP-backed agent skill · v{OLD}",
         f"Claude Code plugin + MCP-backed agent skill · v{NEW}")
sub_once(R / "README.md", f"**v6.x** (currently v{OLD}).", f"**v6.x** (currently v{NEW}).")
sub_once(R / "plugins/tamheed/server/README.md", f"Documents the tool surface as of **tamheed v{OLD}**.",
         f"Documents the tool surface as of **tamheed v{NEW}**.")
sub_once(R / "plugins/tamheed/skills/tamheed/SKILL.md", f"This skill documents tamheed **v{OLD}**",
         f"This skill documents tamheed **v{NEW}**")
sub_once(R / "plugins/tamheed/references/artifact-catalog.md", f"(tamheed v{OLD})", f"(tamheed v{NEW})")

# the stock operator guide: its title line and two paragraphs, WITH its history key (lint 9)
guide = R / "plugins/tamheed/prompts/README.md"
sub_once(guide, f"operator guide (tamheed v{OLD})", f"operator guide (tamheed v{NEW})")
sub_once(guide,
         "`data/.lock` by hand stays the deliberate path for what this host cannot see.\n",
         "`data/.lock` by hand stays the deliberate path for what this host cannot see.\n"
         "Since v6.5 a host that was renamed is still recognised inside one boot, on Linux and\n"
         "macOS, for a lock that v6.5 or later wrote. It is not recognised after a restart, on\n"
         "Windows, or on another machine. `package_unlock` also refuses while staging files of a\n"
         "stopped migration remain.\n")
sub_once(guide,
         "(`tamheed:operator-interview` is the full procedure).\n",
         "(`tamheed:operator-interview` is the full procedure).\n"
         "\n"
         "For a long interview, `slate_export` writes a local page of questions under `slates/`.\n"
         "`slate_read` returns a checked transcript of the answers file that the operator saved.\n"
         "The transcript is a record of a file. It is never the operator's word: the agent reads\n"
         "it back and the operator confirms it in the session.\n")
hist_path = R / "plugins/tamheed/prompts/stock-history.json"
hist = json.loads(hist_path.read_text(encoding="utf-8"))
assert NEW not in hist["README.md"]
hist["README.md"][NEW] = guide.read_text(encoding="utf-8")
hist_path.write_text(json.dumps(hist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

# the lab-tracker pins on the recorded fixture (refreshed by the engine in refresh_lab_650.py)
ev = R / "evals/evals.json"
sub_once(ev, f'"tamheed v{OLD}"', f'"tamheed v{NEW}"')
sub_once(ev, f'"<meta name=\\"tamheed-version\\" content=\\"{OLD}\\">"',
         f'"<meta name=\\"tamheed-version\\" content=\\"{NEW}\\">"')
sub_prefix(ev, "The guide followed the stamp: refresh_stock carried it to the", f"the {OLD} body", f"the {NEW} body")
sub_prefix(ev, "The guide followed the stamp: refresh_stock carried it to the", "218, 220).", "218, 220, 229).")
sub_prefix(ev, f"The guide followed the {OLD} stamp:", f"the {OLD} stamp", f"the {NEW} stamp")

# the CHANGELOG: the [Unreleased] block becomes the 6.5.0 entry
cl = R / "CHANGELOG.md"
t = cl.read_text(encoding="utf-8")
start, end = t.index("## [Unreleased]"), t.index(f"## [{OLD}] - ")
assert "010_registers.sql" in t[start:end] and "009_section_status.sql" in t[start:end]
entry = f"""## [{NEW}] - {DATE}

**MINOR — the field round of 2026-11 (plans 221–229).** Two field projects handed up fourteen
operator-confirmed feedback rows. Ten asked for a change, and each is answered here.

**For a live package (the migration note).** Close the package, then run `package_migrate`: a
preview first, then `confirm=true` on the operator's word. The registry-sync teaches the package
two families and one column. It moves three files: `entity_types.jsonl` and
`progress_entries.jsonl` gain rows, and `document_sections.jsonl` is written once in full. Commit
that change alone. Then run `export_html()` and `package_verify()`. One behaviour changes for
every family: a write with no `id` returned ok before and is refused now.

### Added
- `009_section_status.sql` (plan 225): a nullable `lifecycle_status` on `document_sections`, so a
  section can be retired with `Superseded` or `Obsolete`. A retired section leaves the scans.
- `010_registers.sql` (plan 226): two families, `registers` (`REG-`) and `register_entries`
  (`ENT-`). A register declares its fields, and an entry is checked against them at write. The
  advisory `register-entries-conform`, `entity_query(register_id=)`, one review-page fold per
  register.
- `slate_export` and `slate_read` (plan 227): an interview page for the operator, and a reader
  for the answers file that the page saves. The page runs one script, named by hash in a content
  policy, and it loads and sends nothing. The reader writes nothing, and its result says that
  nothing proves who wrote the file. The tools number 21.
- `trace_query` without an id (plan 221): every link, or one family's, in a fixed order with a
  total. `column_links` returns the links that a foreign-key column holds. `entity_query` and
  `trace_query` echo their arguments under `query`.
- The lock (plan 224): a host that was renamed is recognised inside one boot on Linux and macOS.
  macOS reads a process start time. The migrate lock names its holder.

### Changed
- `requirements-wired` (plan 222) reads the three legs of a requirement: a decision, work and a
  test. A requirement owes one leg, and an `Implemented` one owes all three. The result names the
  missing leg, and the review page shows it (plan 228).
- A refused value names the values that the column takes (plan 223). The four gate outcomes are
  defined: `Go`, `Hold`, `Redirect`, `Kill`.
- `package_unlock` refuses while staging files of a stopped migration remain (plan 224).
- `entity_upsert`, for every family (plan 226, found in its review): a row of an id-keyed family
  needs a text `id`, and a key is never a list. A `custom_attributes` value nests 32 levels at
  most. An exception that escapes the tool rolls its batch back. Before, a row with no `id` was
  stored with a NULL key, and a value 1,500 levels deep was stored as it was. After either,
  `readiness_check` and `export_html` raised. The earlier items of a batch that raised were
  committed by the next write.

"""
cl.write_text(t[:start] + entry + t[end:], encoding="utf-8", newline="\n")
print("stamped", NEW)
