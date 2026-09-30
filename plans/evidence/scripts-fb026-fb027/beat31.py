"""Lab beat 31 (plan 168): fire what v5.8.0 changes against the recorded lab-tracker package,
in-process through the engine's tool functions (the same code path the MCP tools call).
Phase B runs FIRST, on a SCRATCH copy (never committed), with hard assertions: a failure stops
the beat before the fixture is touched. Phase A then writes the FIXTURE (committed) and its note
quotes what phase B observed. Every observation is printed as `OBS <key>: <value>`.
The operator's own trace variable is removed before the engine is imported; this beat runs no hook.

Run:  env -u TAMHEED_HOOK_LOG python plans/evidence/scripts-fb026-fb027/beat31.py <scratch dir> <5.7.0 bundle dir>
      <5.7.0 bundle dir>  `git archive v5.7.0 plugins/tamheed`, extracted: the previous engine,
                          run in its own process by render_with.py for the byte check
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

FIX = REPO / "evals" / "sample-results" / "lab-tracker"
SCR, OLD_BUNDLE = Path(sys.argv[1]), Path(sys.argv[2])
ACTOR = "agent:lab-beat-31"
RELEASE, PREVIOUS = "5.8.0", "5.7.0"
STAMP = f'<meta name="tamheed-version" content="{RELEASE}">'
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
SHARED = "- the roster proof, put to the operator and not yet answered"


def obs(key, value):
    print(f"OBS {key}: {json.dumps(value, ensure_ascii=False, default=str)[:900]}")


def rule(name):
    return next((r for r in srv.readiness_check("package")["rules"] if r["rule"] == name), None)


def pe(entry, **kw):
    out = srv.progress_update([{"entry": entry, "actor": ACTOR, **kw}])
    assert out["ok"], out
    return out


def keys(name=None):
    v = srv.package_verify(name) if name else srv.package_verify()
    assert v["ok"] and v["verified"], v
    return {"review_current": v["review_current"], "review_exported_by": v["review_exported_by"]}


def hashes(package: Path) -> dict:
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
            for f in sorted((package / "csv").glob("*.csv"))}


def page_date(text):
    return re.search(r"Evaluated as of (\d{4}-\d\d-\d\d)", text).group(1)


def one_per_line(text):
    for ln in text.split("\n"):
        assert ln.count("</tr>") <= 1 and ln.count("<path ") <= 1, ln[:80]
    assert text.count('<tr id="') == text.count('\n<tr id="')


# ------------------------------------------------------------------ phase B: a scratch copy, FIRST
assert srv.server_info()["version"] == RELEASE, srv.server_info()["version"]
scr = SCR / "lab31"
assert not scr.exists(), "a fresh scratch folder each run"
shutil.copytree(FIX / "package", scr / "package")
shutil.copytree(FIX / "workspace", scr / "workspace")
srv.PACKAGE_ROOT = scr
PAGE = scr / "package" / "review.html"

# B1: before anything is opened - the page the PREVIOUS release exported, read by name
old_page = PAGE.read_text(encoding="utf-8")
before = keys("package")
assert before == {"review_current": True, "review_exported_by": PREVIOUS}, before
obs("B.before_first_export", before)

# B2: the byte check - the 5.7.0 engine renders the SAME store, in its own process, to a
# path outside the package; the 5.8.0 render follows below and the two are compared
old_render = SCR / "render31" / "by-5.7.0.html"
old_render.parent.mkdir()
r = subprocess.run([sys.executable, str(HERE / "render_with.py"), str(OLD_BUNDLE),
                    str(scr), "package", str(old_render)],
                   capture_output=True, text=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
assert r.returncode == 0 and old_render.exists(), r.stderr[-800:]
assert keys("package") == before                       # an outside export moves nothing inside

o = srv.package_open("package")
assert o["ok"], o
resume = o["resume"]
obs("B.open.resume", {"handoff": resume["handoff"]["id"], "behind": resume["handoff_behind"]})
(scr / "CLAUDE.md").write_text("# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n",
                               encoding="utf-8", newline="\n")
em = srv.handoff_emit(str(scr), refresh_stock=True)
assert em["ok"], em

# B3: the rule, on the fixture's own journal first: more than three handoffs, none repeating
hr = rule("handoff-repeated")
assert hr is not None and hr["status"] == "pass" and hr["entities"] == [], hr
assert hr["population"]["unit"] == "handoffs" and hr["population"]["rows"] >= 3
obs("B.rule.fixture", {"status": hr["status"], "handoffs": hr["population"]["rows"]})
# three handoffs sharing one line; a heading and a short line beside it
first = pe("RESUME AT: the scratch beat, step one\nAWAITING THE OPERATOR:\n" + SHARED
           + "\nshort line\nVERIFIED FACTS: gate_run read at 09:00", event_type="handoff")["ids"][0]
pe("RESUME AT: the scratch beat, step two\nAWAITING THE OPERATOR:\n" + SHARED
   + "\nshort line\nVERIFIED FACTS: gate_run read at 10:00", event_type="handoff")
third = pe("RESUME AT: the scratch beat, step three\nAWAITING THE OPERATOR:\n" + SHARED
           + "\nshort line\nVERIFIED FACTS: gate_run read at 11:00", event_type="handoff")["ids"][0]
hr = rule("handoff-repeated")
assert hr["status"] == "fail" and hr["entities"] == [first], hr
assert f"line 3 of {third} since {first} (3 handoffs)" in hr["note"], hr["note"]
assert "line 2" not in hr["note"] and "line 4" not in hr["note"]        # the heading, the short line
assert "roster proof" not in hr["note"] and "gate_run" not in hr["note"]  # no line text, ever
obs("B.rule.fail", {"entities": hr["entities"], "detail": hr["note"].split("; ")[-1]})
pe("RESUME AT: the scratch beat, step four\nAWAITING THE OPERATOR:\n- the roster proof:"
   f" re-measured {TODAY} against the decision register, still open, no ruling since\n"
   "short line\nVERIFIED FACTS: gate_run read at 12:00", event_type="handoff")
hr = rule("handoff-repeated")
assert hr["status"] == "pass" and hr["entities"] == [], hr
obs("B.rule.cleared", hr["status"])

# B4: the page - the first export on this release re-flows it once; the same page
csv_before = hashes(scr / "package")
digest0 = srv.package_verify()["digest"]
assert srv.export_html()["ok"]
page = PAGE.read_text(encoding="utf-8")
assert STAMP in page[:4096] and srv.package_verify()["digest"] == digest0   # an export moves no store byte
one_per_line(page)
assert hashes(scr / "package") != csv_before         # progress_entries.csv carries the handoffs
# the byte check proper: the 5.7.0 render of the store BEFORE the handoffs against a 5.8.0
# render of that same state - so the four handoffs are taken out by rendering a second copy
twin = SCR / "lab31-twin"
shutil.copytree(FIX / "package", twin / "package")
new_render = SCR / "render31" / "by-5.8.0.html"
r = subprocess.run([sys.executable, str(HERE / "render_with.py"), str(BUNDLE), str(twin),
                    "package", str(new_render)],
                   capture_output=True, text=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
assert r.returncode == 0 and new_render.exists(), r.stderr[-800:]
one_per_line(new_render.read_text(encoding="utf-8"))
r = subprocess.run([sys.executable, str(HERE / "bytecheck.py"), str(old_render), str(new_render)],
                   capture_output=True, text=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
assert r.returncode == 0, r.stdout + r.stderr
assert "EQUAL" in r.stdout, r.stdout
obs("B.page", {"bytecheck": r.stdout.strip().splitlines()[-1],
               "old_lines": old_render.read_text(encoding="utf-8").count("\n"),
               "new_lines": new_render.read_text(encoding="utf-8").count("\n"),
               "csv_of_the_twin_untouched": hashes(twin / "package") == hashes(FIX / "package")})
assert hashes(twin / "package") == hashes(FIX / "package")

# B5: the descriptions name their argument and every key, under the cap
for tool, arg, takes in (("progress_update", "`entries` is a list", srv._PROGRESS_KEYS),
                         ("audit_record", "`verdicts` is a list", srv._VERDICT_KEYS)):
    desc = srv.TOOLS[tool][1]
    assert arg in desc and all(k in desc for k in takes) and len(desc) <= srv._DESCRIPTION_CAP, tool
obs("B.descriptions", {t: len(srv.TOOLS[t][1]) for t in ("progress_update", "audit_record")})
srv.package_close()
print("PHASE-B-DONE")

# ------------------------------------------------------------------ phase A: the fixture
srv.PACKAGE_ROOT = FIX
fixture_before = keys("package")
assert fixture_before == {"review_current": True, "review_exported_by": PREVIOUS}, fixture_before
obs("A.before_first_export", fixture_before)
o = srv.package_open("package")
assert o["ok"], o
info = srv.server_info()
obs("A.schema", {"schema_version": info["schema_version"], "migrations_head": info["migrations_head"],
                 "version": info["version"]})
assert info["version"] == RELEASE and info["schema_version"] == 7
obs("A.open.resume", {"handoff": o["resume"]["handoff"]["id"], "behind": o["resume"]["handoff_behind"],
                      "skill": o["resume"]["skill"]})
target = SCR / "target31"
shutil.copytree(FIX / "workspace", target / "workspace")
em = srv.handoff_emit(str(target), refresh_stock=True)
assert em["ok"], em
obs("A.emit.refreshed", em["prompt_library"]["refreshed"])
obs("A.emit.findings", {k: em[k] for k in ("stock_merged", "oversized_prompts", "stale_references",
                                           "restated_content")})
guide = (FIX / "package" / "prompts" / "README.md").read_text(encoding="utf-8")
assert f"tamheed v{RELEASE}" in guide
obs("A.guide", f"tamheed v{RELEASE}")
em2 = srv.handoff_emit(str(target))
obs("A.emit2.unchanged", "CLAUDE.md" in em2["unchanged"])
assert "CLAUDE.md" in em2["unchanged"]

pe("Beat 31 (plan 168, the v5.8.0 continuation), opened at schema_version 7 (no migration in"
   " 5.8.0). THE RULE: readiness_check carries handoff-repeated; on this journal it passes. On"
   " the scratch copy three handoffs shared one line of twenty characters or more, beside a"
   " heading and a short line: a line carried word for word through three handoffs was named"
   f" by number - line 3 of the third, since the first of the three, 3 handoffs - and the"
   " heading and the short line were not; no line of any handoff appeared in the note. A"
   " fourth handoff that re-measured the line and wrote the date: a re-measured line cleared"
   " the rule. THE PAGE: the first export on the release re-flowed the page - every row, edge"
   " and node on its own line; the 5.7.0 engine's render of the same store, on the same date,"
   " equals it once the newlines between tags are removed and the stamp is replaced: the page"
   " puts each row on its own line and renders the same; the csv files kept their hashes."
   " THE DESCRIPTIONS: progress_update's and audit_record's registered descriptions name their"
   " argument (entries, verdicts) and every key, under the client's cap. THE EMISSION:"
   f" refresh_stock carried the guide to tamheed v{RELEASE}, its title only, no finding.",
   event_type="note")
h = pe("Resume at: the next continuation beat (32). In flight: none - beat 31 closed. Awaiting"
       " the operator: nothing. Verified facts: handoff-current pass and handoff-repeated pass,"
       f" both read after this entry; the guide reads the {RELEASE} stock. The export, gate_run"
       " and package_verify FOLLOW this entry, so their results are in the evidence report and"
       " not here. Do not carry: the scratch copy's four handoffs, its twin and its renders -"
       " never written to this package.", event_type="handoff")
obs("A.handoff", h["ids"][0])
obs("A.handoff-current.final", rule("handoff-current")["status"])
obs("A.handoff-repeated.final", rule("handoff-repeated")["status"])
assert rule("handoff-repeated")["status"] == "pass"
assert keys()["review_current"] is False                     # the handoff is itself a write
fixture_page_before = (FIX / "package" / "review.html").read_text(encoding="utf-8")
ex = srv.export_html()
assert ex["ok"], ex
page = (FIX / "package" / "review.html").read_text(encoding="utf-8")
assert STAMP in page[:4096] and f"Latest handoff: {h['ids'][0]}" in page
one_per_line(page)
obs("A.page", {"date_before": page_date(fixture_page_before), "date_after": page_date(page),
               "lines_before": fixture_page_before.count("\n"), "lines_after": page.count("\n")})
g = srv.gate_run()
obs("A.gate_run.ready", g["ready"])
assert g["ready"]
v = srv.package_verify()
obs("A.verify", {k: v.get(k) for k in ("verified", "dirty", "foreign", "review_current",
                                       "review_exported_by")})
assert v["verified"] and v["review_current"] and not v["dirty"]
assert v["review_exported_by"] == RELEASE
srv.package_close()
obs("A.lock_gone", not (FIX / "package" / "data" / ".lock").exists())
print("DONE")
