"""Plan 263: stamp 6.9.0 on every version surface that lint 8 reads, turn the CHANGELOG's
`[Unreleased]` block into the 6.9.0 entry (the beats wrote its items; this adds the header), apply
D11 (the stock guide's line on `expect_unchanged`, which an insert cannot use), put the stock
guide's stamped body in stock-history.json under 6.9.0, and re-aim the lab-tracker eval pins. Run
once from the repository root, then `python docs/guide/build.py` and `refresh_lab_690.py`. The
pattern is plans/evidence/scripts-253/stamp_680.py.
"""
import datetime
import json
from pathlib import Path

R = Path(__file__).resolve().parents[3]
OLD, NEW = "6.8.0", "6.9.0"
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
# D11 (plan 259, ACMP's FB-037): expect_unchanged guards an update only. The stock line taught it
# for every long row, inserts included. The body changes here, with its history key.
sub_once(guide, "Apply `expect_unchanged` to every long row regardless of size.",
         "Apply `expect_unchanged` to every long row you update, regardless of size. For a new"
         " row, send `sha256: true` and compare each hash with your source.")
hist_path = R / "plugins/tamheed/prompts/stock-history.json"
hist = json.loads(hist_path.read_text(encoding="utf-8"))
hist["README.md"][NEW] = guide.read_text(encoding="utf-8")       # the key opens with the stamp
hist_path.write_text(json.dumps(hist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

ev = R / "evals/evals.json"
sub_once(ev, f'"tamheed v{OLD}"', f'"tamheed v{NEW}"')
sub_once(ev, f'"<meta name=\\"tamheed-version\\" content=\\"{OLD}\\">"',
         f'"<meta name=\\"tamheed-version\\" content=\\"{NEW}\\">"')
sub_prefix(ev, "The guide followed the stamp: refresh_stock carried it to the", f"the {OLD} body", f"the {NEW} body")
sub_prefix(ev, "The guide followed the stamp: refresh_stock carried it to the", "231, 237, 247, 253).",
           "231, 237, 247, 253, 263).")
sub_prefix(ev, f"The guide followed the {OLD} stamp:", f"the {OLD} stamp", f"the {NEW} stamp")

HEAD = f"""## [{NEW}] - {DATE}

**MINOR — the field round after 6.8.0: ACMP's FB-034 to FB-037, and Jisr's FB-025, FB-029,
FB-032, FB-033, FB-034, FB-043 and FB-044 (plans 256–263, ADR-0007).** The rulings R145–R170
are in `plans/256-field-round-6.9.0.md`.

**For a live package.** Update the plugin and start the client again. No migration is needed:
no table or column changed. Run `handoff_emit(<repository root>, refresh_stock=true)` (the stock
guide and the note's table of obligations changed) and `export_html()`. The way back to 6.8.0:
the plugin goes back alone, except that 6.8.0 refuses a slate spec or record that holds
`show_recommendations` or a text over 8000 characters. 6.8.0 ignores a family's declaration.

"""
cl = R / "CHANGELOG.md"
t = cl.read_text(encoding="utf-8")
assert t.count("## [Unreleased]\n\nThe 6.9.0 field round (plans 256-263). The rulings R145-R170 are in\n`plans/256-field-round-6.9.0.md`.\n\n") == 1
cl.write_text(t.replace("## [Unreleased]\n\nThe 6.9.0 field round (plans 256-263). The rulings R145-R170 are in\n`plans/256-field-round-6.9.0.md`.\n\n", HEAD),
              encoding="utf-8", newline="\n")
print("stamped", NEW, DATE)
