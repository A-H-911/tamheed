"""Plan 237: stamp 6.6.0 on every version surface that lint 8 reads, turn the CHANGELOG's
`[Unreleased]` block into the 6.6.0 entry, put the stock guide's stamped body in
stock-history.json under 6.6.0 (the key plan 236 opened), and re-aim the lab-tracker eval pins.
Run once from the repository root, then `python docs/guide/build.py` and `refresh_lab_660.py`.
"""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[3]
OLD, NEW, DATE = "6.5.1", "6.6.0", "2026-11-16"      # the UTC date of the release commit


def sub_once(path: Path, old: str, new: str) -> None:
    t = path.read_text(encoding="utf-8")
    assert t.count(old) == 1, (path, t.count(old), old[:60])
    path.write_text(t.replace(old, new), encoding="utf-8", newline="\n")


def sub_prefix(path: Path, start: str, old: str, new: str) -> None:
    lines = path.read_text(encoding="utf-8").split("\n")
    hits = [i for i, line in enumerate(lines) if start in line and old in line]
    assert len(hits) == 1, (path, start[:40], len(hits))
    lines[hits[0]] = lines[hits[0]].replace(old, new)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


sub_once(R / "plugins/tamheed/.claude-plugin/plugin.json", f'"version": "{OLD}"', f'"version": "{NEW}"')
sub_once(R / "README.md", f"Claude Code plugin + MCP-backed agent skill · v{OLD}",
         f"Claude Code plugin + MCP-backed agent skill · v{NEW}")
sub_once(R / "README.md", f"**v6.x** (currently v{OLD}).", f"**v6.x** (currently v{NEW}).")
sub_once(R / "plugins/tamheed/server/README.md", f"Documents the tool surface as of **tamheed v{OLD}**.",
         f"Documents the tool surface as of **tamheed v{NEW}**.")
sub_once(R / "plugins/tamheed/skills/tamheed/SKILL.md", f"This skill documents tamheed **v{OLD}**",
         f"This skill documents tamheed **v{NEW}**")
sub_once(R / "plugins/tamheed/references/artifact-catalog.md", f"(tamheed v{OLD})", f"(tamheed v{NEW})")

guide = R / "plugins/tamheed/prompts/README.md"
sub_once(guide, f"operator guide (tamheed v{OLD})", f"operator guide (tamheed v{NEW})")
hist_path = R / "plugins/tamheed/prompts/stock-history.json"
hist = json.loads(hist_path.read_text(encoding="utf-8"))
assert NEW in hist["README.md"], "plan 236 opened the 6.6.0 key with the new skill row"
hist["README.md"][NEW] = guide.read_text(encoding="utf-8")       # the stamped body replaces it
hist_path.write_text(json.dumps(hist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

ev = R / "evals/evals.json"
sub_once(ev, f'"tamheed v{OLD}"', f'"tamheed v{NEW}"')
sub_once(ev, f'"<meta name=\\"tamheed-version\\" content=\\"{OLD}\\">"',
         f'"<meta name=\\"tamheed-version\\" content=\\"{NEW}\\">"')
sub_prefix(ev, "The guide followed the stamp: refresh_stock carried it to the", f"the {OLD} body", f"the {NEW} body")
sub_prefix(ev, "The guide followed the stamp: refresh_stock carried it to the", "229, 231).", "229, 231, 237).")
sub_prefix(ev, f"The guide followed the {OLD} stamp:", f"the {OLD} stamp", f"the {NEW} stamp")

cl = R / "CHANGELOG.md"
t = cl.read_text(encoding="utf-8")
start, end = t.index("## [Unreleased]\n"), t.index(f"## [{OLD}] - ")
entry = f"""## [{NEW}] - {DATE}

**MINOR — the standup report (plans 232–237, ADR-0003).** The operator asked for a report on
demand that a team and a manager read in 5 to 10 minutes: what we did, the challenges and
decisions, and what we expect to do next, for the window since the last report.

**For a live package.** Update the plugin and start the client again. Commit the package. Run
`package_migrate(name)` for a preview, then `package_migrate(name, confirm=true)`: the staged
registry-sync teaches the package the `standup-report` family (a pure append, no backup). Then
run `handoff_emit(<repository root>, refresh_stock=true)` and `export_html()`. The first
`/tamheed:standup` asks for the operator's UTC offset. From 6.6.0 back to 6.5.1 the plugin goes
back alone, after `standup_reports.jsonl`, `reports/` and the registry row are removed.

### Added
- **The standup report** (`RPT-`, table `standup_reports`, migration `011_standup_reports.sql`).
  A stored record by design (ADR-0003 supersedes ADR-0001's "never stored snapshots" for this
  family). A report keeps the changes of its window: a status and a content fingerprint per
  row. The first report, and every 30th daily report, keeps the full state. A replay from the
  latest checkpoint rebuilds the state at any report, and each link is checked against its
  digest. Draft, then Approved on the operator's word, then Superseded by a correction.
  Recorded reports are immutable by a trigger.
- **The `standup_report` tool** (22 tools): draft the facts, attach the agent's words (refused
  for an id that names no row, a plain-English hard finding, or instruction-shaped text),
  record on the operator's word (`operator_confirm`, `by`, `words`, `colour`), discard. The
  page `reports/RPT-NNN.html` lists the facts in plain words, with a glossary, and keeps the
  engine's part within 1,400 visible words. The operator's words stay in the row: the journal
  note and every page leave them out. The rule colour is red for an open critical or high
  defect, amber for an open high risk or an overdue question. The release rules show as "Not
  ready to close yet" and do not move the colour.
- **The `/tamheed:standup` skill** (28 skills, 18 scenarios), and one line in the resume block
  and the session-start hook that names the last recorded report.

### Changed
- `entity_query` on standup reports leaves out `state_delta` and `facts` unless `columns`
  names them. `entity_upsert` refuses the family.
- `package_open` returns a refusal that names the file and line when the store refuses a row
  (a git merge of two drafts, for example). It raised before.

### Fixed
- A journal id like `PE-1x` (the GLOB admits it, and `entity_upsert` writes it) made
  `package_open` raise and leave the lock behind, and `readiness_check` and `package_migrate`
  raise. The three read the number by SQL now (plan 235).

"""
cl.write_text(t[:start] + entry + t[end:], encoding="utf-8", newline="\n")
print("stamped", NEW)
