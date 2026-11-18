"""Plan 253: stamp 6.8.0 on every version surface that lint 8 reads, turn the CHANGELOG's
`[Unreleased]` block into the 6.8.0 entry (the beats wrote its items; this adds the header), put
the stock guide's stamped body in stock-history.json under 6.8.0, and re-aim the lab-tracker
eval pins. Run once from the repository root, then `python docs/guide/build.py` and
`refresh_lab_680.py`. The pattern is plans/evidence/scripts-239/stamp_670.py.
"""
import datetime
import json
from pathlib import Path

R = Path(__file__).resolve().parents[3]
OLD, NEW = "6.7.0", "6.8.0"
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
sub_prefix(ev, "The guide followed the stamp: refresh_stock carried it to the", "231, 237, 247).", "231, 237, 247, 253).")
sub_prefix(ev, f"The guide followed the {OLD} stamp:", f"the {OLD} stamp", f"the {NEW} stamp")

HEAD = f"""## [{NEW}] - {DATE}

**MINOR — Jisr's FB-023 and FB-024, and the standup report as a delivery report (plans
249–253, ADR-0005).** The rulings U1–U20 and the defaults V1–V10 are in
`plans/249-field-round-6.8.0.md`.

**For a live package.** Update the plugin and start the client again. No migration is needed:
no table or column changed. Run `handoff_emit(<repository root>, refresh_stock=true)` (the stock
guide changed) and `export_html()`. A new standup report row is larger: it freezes the plan tree
and the full registers (about 100 KB to 800 KB a row on a large package). From 6.8.0 back to
6.7.0 the plugin goes back alone: 6.7.0 draws a 6.8.0 report in its old look.

"""
cl = R / "CHANGELOG.md"
t = cl.read_text(encoding="utf-8")
assert t.count("## [Unreleased]\n\n") == 1
cl.write_text(t.replace("## [Unreleased]\n\n", HEAD), encoding="utf-8", newline="\n")
print("stamped", NEW, DATE)
