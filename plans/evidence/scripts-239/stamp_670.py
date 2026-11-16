"""Plan 247: stamp 6.7.0 on every version surface that lint 8 reads, turn the CHANGELOG's
`[Unreleased]` block into the 6.7.0 entry (the beats wrote its items; this adds the header), put
the stock guide's stamped body in stock-history.json under 6.7.0, and re-aim the lab-tracker
eval pins. Run once from the repository root, then `python docs/guide/build.py` and
`refresh_lab_670.py`. The pattern is plans/evidence/scripts-237/stamp_660.py.
"""
import datetime
import json
from pathlib import Path

R = Path(__file__).resolve().parents[3]
OLD, NEW = "6.6.0", "6.7.0"
DATE = datetime.datetime.now(datetime.timezone.utc).date().isoformat()   # the release commit's UTC date


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
hist["README.md"][NEW] = guide.read_text(encoding="utf-8")       # the key opens with the stamp
hist_path.write_text(json.dumps(hist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

ev = R / "evals/evals.json"
sub_once(ev, f'"tamheed v{OLD}"', f'"tamheed v{NEW}"')
sub_once(ev, f'"<meta name=\\"tamheed-version\\" content=\\"{OLD}\\">"',
         f'"<meta name=\\"tamheed-version\\" content=\\"{NEW}\\">"')
sub_prefix(ev, "The guide followed the stamp: refresh_stock carried it to the", f"the {OLD} body", f"the {NEW} body")
sub_prefix(ev, "The guide followed the stamp: refresh_stock carried it to the", "231, 237).", "231, 237, 247).")
sub_prefix(ev, f"The guide followed the {OLD} stamp:", f"the {OLD} stamp", f"the {NEW} stamp")

HEAD = f"""## [{NEW}] - {DATE}

**MINOR — the second field's round (plans 239–247: FB-015, FB-017 to FB-021) and two standup
actions (ADR-0004).** Rulings R121–R142 are in `plans/evidence/field-round-6.7.0-record.md`.

**For a live package.** Update the plugin and start the client again. No migration is needed:
migration `012_standup_withdraw.sql` replaces one trigger and changes no stored file. Run
`handoff_emit(<repository root>, refresh_stock=true)` and `export_html()`. From 6.7.0 back to
6.6.0 the plugin goes back alone. Before that, write a boolean `values` set as text, because
6.6.0 refuses every write to such a register. 6.6.0 would also use a withdrawn report id again.

"""
cl = R / "CHANGELOG.md"
t = cl.read_text(encoding="utf-8")
assert t.count("## [Unreleased]\n\n") == 1
cl.write_text(t.replace("## [Unreleased]\n\n", HEAD), encoding="utf-8", newline="\n")
print("stamped", NEW, DATE)
