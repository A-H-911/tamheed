"""Lab beat 27 (plan 149): fire every v5.5 mechanism against the recorded lab-tracker package,
in-process through the engine's tool functions (the same code path the MCP tools call).
Phase B runs FIRST, on a SCRATCH copy (never committed), with hard assertions: a failure stops
the beat before the fixture is touched. Phase A then writes the FIXTURE (committed) and its note
quotes what phase B observed. Every observation is printed as `OBS <key>: <value>`.
The operator's own trace variable is removed before the engine is imported."""
import json
import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(r"C:\Users\ahammo\Repos\tamheed")
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "server"))
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

FIX = REPO / "evals" / "sample-results" / "lab-tracker"
SCR = Path(sys.argv[1])
ACTOR = "agent:lab-beat-27"
OPERATOR = "operator:lab (beat 27)"
RULE = "decide a boundary's inclusive or exclusive reading from the specification"
STORY = ("During the second slice the tracker's due-date filter dropped the last day of the month,"
         " and two sessions argued about what the operator had meant before anyone opened the"
         " specification; the defect was closed twice and reopened twice. What it taught: " + RULE
         + " before changing the comparison.")
RULE_FIRST = (RULE[0].upper() + RULE[1:] + " before changing the comparison. The tracker's due-date"
              " filter dropped the last day of the month in the second slice, and two sessions"
              " argued about the operator's intent before anyone opened the specification.")
HINT = "binds from this write and is RENDERED only once the always-loaded note is rebuilt"
CAP = "only if pinned or among the 10 newest unpinned Approved rows"
FOOTER = "more Approved lesson(s) bind too and are not rendered here"


def obs(key, value):
    print(f"OBS {key}: {json.dumps(value, ensure_ascii=False, default=str)[:900]}")


def rule(name):
    return next((r for r in srv.readiness_check("package")["rules"] if r["rule"] == name), None)


def pe(entry, **kw):
    out = srv.progress_update([{"entry": entry, "actor": ACTOR, **kw}])
    assert out["ok"], out
    return out


def lesson(n, statement, **kw):
    return {"type": "lesson", "id": f"LL-{n:03d}", "title": f"lab lesson {n}",
            "statement": statement, "kind": "improve", **kw}


def approved(row, **kw):
    return dict(row, lifecycle_status="Approved", operator_confirm=True, confirmed_by=OPERATOR,
                **kw)


def note_ids(path: Path) -> list[str]:
    return re.findall(r"^- \*\*(LL-\d+)\*\*", path.read_text(encoding="utf-8"), re.M)


def note_line(path: Path, lid: str) -> str:
    return next(ln for ln in path.read_text(encoding="utf-8").splitlines()
                if ln.startswith(f"- **{lid}**"))


def page_cells(name: str) -> tuple[dict, str]:
    out = srv.export_html(str(SCR / name))
    assert out["ok"], out
    page = (SCR / name).read_text(encoding="utf-8")
    fold = page.split('id="lessons-approved"', 1)[1].split("</details>", 1)[0]
    return dict(re.findall(r'<tr id="(LL-\d+)"><td>LL-\d+</td><td>[^<]*</td><td>[^<]*</td>'
                           r'<td>([^<]*)</td>', fold)), page


def changed(item: dict) -> list[str]:
    return sorted(c["column"] for c in item.get("changed_columns", []))


def marked(cells: dict) -> list[str]:
    return sorted(i for i, c in cells.items() if c == "rendered")


# ------------------------------------------------------------------ phase B: a scratch copy, FIRST
scr = SCR / "lab27"
shutil.rmtree(scr, ignore_errors=True)
shutil.copytree(FIX / "package", scr / "package")
shutil.copytree(FIX / "workspace", scr / "workspace")
srv.PACKAGE_ROOT = scr
o = srv.package_open("package")
assert o["ok"], o
obs("B.open.resume", {"handoff": o["resume"]["handoff"]["id"], "behind": o["resume"]["handoff_behind"]})
(scr / "CLAUDE.md").write_text("# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n",
                               encoding="utf-8", newline="\n")
NOTE = scr / "package" / "CLAUDE.md"
em = srv.handoff_emit(str(scr), refresh_stock=True)
assert em["ok"], em
assert note_ids(NOTE) == ["LL-004"], note_ids(NOTE)
assert FOOTER not in NOTE.read_text(encoding="utf-8")
obs("B.emit0", {"note_roster": note_ids(NOTE), "refreshed": em["prompt_library"]["refreshed"]})

# B2: two Proposed lessons, one opening with its story and one with its rule; then approved
born = srv.entity_upsert([lesson(6, STORY), lesson(7, RULE_FIRST)])
assert born["ok"], born
assert all("next" not in it for it in born["items"]), born          # Proposed: no hint
hints = []
for row in (lesson(6, STORY), lesson(7, RULE_FIRST)):
    out = srv.entity_upsert([approved(row)])
    assert out["ok"], out
    it = out["items"][0]
    # the row sends no confirmed_at, so two columns move (a row that sends it moves three)
    assert changed(it) == ["confirmed_by", "lifecycle_status"], it
    assert HINT in it["next"] and it["next"].endswith(
        "; it renders in the note only if pinned or among the 10 newest unpinned Approved rows"
        " - pin it to keep it visible"), it["next"]
    assert "BINDS only once" not in it["next"]
    hints.append(it["next"])
obs("B.hint.approved", hints[0])

# B3: an approval with NO emit after it - the page shows the NEXT emit, the note is the last one
cells, page = page_cells("page27-b3.html")
assert marked(cells) == ["LL-004", "LL-006", "LL-007"], cells
assert note_ids(NOTE) == ["LL-004"]
assert "it is what the next handoff_emit renders" in page
assert "note (rendered at the next emit)" in page
assert "the 10 highest-numbered unpinned ones" in page
assert "rendered into the CLAUDE.md note" not in page
obs("B.no_emit_yet", {"page_marks": marked(cells), "note_on_disk": note_ids(NOTE)})

# B4: the emit renders them; the cut keeps the story of one and the rule of the other
assert srv.handoff_emit(str(scr))["ok"]
assert sorted(note_ids(NOTE)) == ["LL-004", "LL-006", "LL-007"]
story_line, rule_line = note_line(NOTE, "LL-006"), note_line(NOTE, "LL-007")
flat = " ".join(STORY.split())
assert len(flat) > srv._NOTE_LINE_MAX
assert story_line == f"- **LL-006** [improve] {flat[:srv._NOTE_LINE_CUT]}..."
assert RULE not in story_line and RULE.lower() in rule_line.lower(), (story_line, rule_line)
obs("B.cut", {"story_first_line": story_line, "rule_first_line": rule_line,
              "rule_in_story_line": RULE in story_line,
              "rule_in_rule_line": RULE.lower() in rule_line.lower()})

# B5: eleven unpinned approvals - the eleventh pushes the oldest out of the roster
more = srv.entity_upsert([approved(lesson(n, f"Lab rule number {n}: keep the export header and"
                                             " its test in one change.")) for n in range(8, 16)])
assert more["ok"], more
assert srv.handoff_emit(str(scr))["ok"]
roster = note_ids(NOTE)
assert sorted(roster) == [f"LL-{n:03d}" for n in range(6, 16)], roster
text = NOTE.read_text(encoding="utf-8")
assert f"1 {FOOTER}: `entity_query(\"lesson\")`." in text, text[-600:]
cells, _ = page_cells("page27-b5.html")
assert marked(cells) == sorted(roster) and cells["LL-004"] == "not rendered", cells
binding = srv.entity_query("lesson", status="Approved", columns=["id"], limit=100)
assert binding["total"] == 11 and "LL-004" in [r["id"] for r in binding["rows"]], binding
obs("B.eleven", {"note_roster": sorted(roster), "pushed_out": "LL-004",
                 "footer": f"1 {FOOTER}", "page_marks": len(marked(cells)),
                 "approved_by_query": binding["total"]})

# B6: a pinned row is rendered whatever its number
row4 = srv.entity_query("lesson", id="LL-004")["rows"][0]
content = {k: row4[k] for k in ("title", "statement", "context", "recommendation", "rationale",
                                "kind", "category", "impact_if_followed", "impact_if_ignored",
                                 "recorded_at", "custom_attributes")
           if row4.get(k) is not None}
pin = srv.entity_upsert([dict({"type": "lesson", "id": "LL-004"}, **content,
                              lifecycle_status="Approved", pinned=1, operator_confirm=True)])
assert pin["ok"], pin
assert changed(pin["items"][0]) == ["pinned"], pin
assert pin["items"][0]["next"].endswith("; pinned rows always render"), pin
assert srv.handoff_emit(str(scr))["ok"]
assert note_ids(NOTE)[0] == "LL-004" and len(note_ids(NOTE)) == 11
assert "[improve, pinned]" in note_line(NOTE, "LL-004")
assert FOOTER not in NOTE.read_text(encoding="utf-8")
cells, _ = page_cells("page27-b6.html")
assert len(marked(cells)) == 11 and cells["LL-004"] == "rendered"
obs("B.pinned", {"first_in_note": note_ids(NOTE)[0], "rendered_lines": len(note_ids(NOTE)),
                 "footer_present": FOOTER in NOTE.read_text(encoding="utf-8")})

# B7: a low-numbered lesson approved late is never rendered - and it binds
row2 = srv.entity_query("lesson", id="LL-002")["rows"][0]
assert row2["lifecycle_status"] == "Proposed"
content2 = {k: row2[k] for k in ("title", "statement", "context", "recommendation", "rationale",
                                 "kind", "category", "impact_if_followed", "impact_if_ignored",
                                 "recorded_at", "custom_attributes")
            if row2.get(k) is not None}
late = srv.entity_upsert([dict({"type": "lesson", "id": "LL-002"}, **content2,
                               lifecycle_status="Approved", pinned=0, operator_confirm=True,
                               confirmed_by=OPERATOR)])
assert late["ok"], late
assert HINT in late["items"][0]["next"] and CAP in late["items"][0]["next"]
assert srv.handoff_emit(str(scr))["ok"]
assert "LL-002" not in note_ids(NOTE)
assert f"1 {FOOTER}" in NOTE.read_text(encoding="utf-8")
cells, _ = page_cells("page27-b7.html")
assert cells["LL-002"] == "not rendered" and len(marked(cells)) == 11
assert "LL-002" in [r["id"] for r in srv.entity_query("lesson", status="Approved",
                                                       columns=["id"])["rows"]]
budget = rule("lessons-note-budget")
obs("B.late_low_number", {"in_note": "LL-002" in note_ids(NOTE), "page": cells["LL-002"],
                          "approved_by_query": True, "footer": f"1 {FOOTER}",
                          "note_budget": budget["status"]})
srv.package_close()
print("PHASE-B-DONE")

# ------------------------------------------------------------------ phase A: the fixture
srv.PACKAGE_ROOT = FIX
o = srv.package_open("package")
assert o["ok"], o
info = srv.server_info()
obs("A.schema", {"schema_version": info["schema_version"], "migrations_head": info["migrations_head"],
                 "version": info["version"]})
assert info["version"] == "5.5.0" and info["schema_version"] == 7
obs("A.open.resume", {"handoff": o["resume"]["handoff"]["id"], "behind": o["resume"]["handoff_behind"],
                      "skill": o["resume"]["skill"]})
target = SCR / "target27"
shutil.rmtree(target, ignore_errors=True)
shutil.copytree(FIX / "workspace", target / "workspace")
em = srv.handoff_emit(str(target), refresh_stock=True)
assert em["ok"], em
obs("A.emit.refreshed", em["prompt_library"]["refreshed"])
obs("A.emit.findings", {k: em[k] for k in ("stock_merged", "oversized_prompts", "stale_references",
                                           "restated_content")})
guide = (FIX / "package" / "prompts" / "README.md").read_text(encoding="utf-8")
assert "tamheed v5.5.0" in guide and "the 10 highest-numbered unpinned ones" in guide
obs("A.guide.5.5.0", True)
fixture_note = (target / "CLAUDE.md").read_text(encoding="utf-8")
assert note_ids(target / "CLAUDE.md") == ["LL-004"] and FOOTER not in fixture_note
obs("A.note", {"roster": ["LL-004"], "footer_present": False})
em2 = srv.handoff_emit(str(target))
obs("A.emit2.unchanged", "CLAUDE.md" in em2["unchanged"])
assert "CLAUDE.md" in em2["unchanged"]

pe("Beat 27 (plan 149, the v5.5.0 continuation), opened at schema_version 7 (no migration in"
   " 5.5.0). TWO WORDS: the status binds, the note's roster is what is rendered. On the scratch"
   " copy a lesson that opened with its story was cut to the story and one that opened with its"
   " rule kept the rule inside the cut. Eleven unpinned approvals: the eleventh pushed the oldest"
   " out of the roster, the footer read 1 more Approved lesson(s) bind too and are not rendered"
   " here, the review page marked ten rows rendered, and the row pushed out was still returned"
   " by the Approved query. A pinned row was rendered whatever its number. A low-numbered lesson"
   " approved late was never rendered. After an approval with no emit the page showed the next"
   " emit and the note on disk showed the last one, as the page's own sentence says. THE"
   " EMISSION: refresh_stock carried the guide to tamheed v5.5.0, no finding; this package has"
   " one Approved lesson, so its own note has no footer and did not change.", event_type="note")
h = pe("Resume at: the next continuation beat (28). In flight: none - beat 27 closed. Awaiting"
       " the operator: nothing. Verified facts: gate_run ready and package_verify verified after"
       " this entry (both re-run after it); handoff-current pass; the guide reads the 5.5.0"
       " stock; the review page marks the one Approved lesson rendered at the next emit. Do not"
       " carry: the scratch copy's eleven lessons, its pin and its late approval - never written"
       " to this package.",
       event_type="handoff")
obs("A.handoff", h["ids"][0])
obs("A.handoff-current.final", rule("handoff-current")["status"])
ex = srv.export_html()
assert ex["ok"], ex
page = (FIX / "package" / "review.html").read_text(encoding="utf-8")
fold = page.split('id="lessons-approved"', 1)[1].split("</details>", 1)[0]
assert "note (rendered at the next emit)" in fold and "<td>rendered</td>" in fold
assert f"Latest handoff: {h['ids'][0]}" in page
obs("A.review", {"column": True, "LL-004": "rendered", "latest_handoff": h["ids"][0]})
g = srv.gate_run()
obs("A.gate_run.ready", g["ready"])
assert g["ready"]
v = srv.package_verify()
obs("A.verify", {k: v.get(k) for k in ("verified", "dirty", "foreign", "review_current")})
assert v["verified"] and v["review_current"] and not v["dirty"]
srv.package_close()
obs("A.lock_gone", not (FIX / "package" / "data" / ".lock").exists())
print("DONE")
