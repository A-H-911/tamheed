"""Lab beat 32 (plan 173): the v5.8.1 continuation against the recorded lab-tracker package,
in-process through the engine's tool functions. 5.8.1 changes no engine surface: the beat records
what this cycle measured (the FB-028 correction; the real-agent runs) and carries the fixture to
the release. Phase B runs FIRST on a SCRATCH copy (never committed) with hard assertions; phase A
then writes the FIXTURE (committed). Every observation is printed as `OBS <key>: <value>`.
The operator's own trace variable is removed before the engine is imported; this beat runs no hook.

Run:  env -u TAMHEED_HOOK_LOG python plans/evidence/scripts-fb028/beat32.py <scratch dir>
"""
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

FIX = REPO / "evals" / "sample-results" / "lab-tracker"
SCR = Path(sys.argv[1])
ACTOR = "agent:lab-beat-32"
RELEASE, PREVIOUS = "5.8.1", "5.8.0"
STAMP = f'<meta name="tamheed-version" content="{RELEASE}">'
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
REPORT = "plans/evidence/lab-acceptance-report-2026-09-30.md"
CORRECTION = ("a reload restarts the server, not what the session lists: only a client process"
              " started after the update lists the new descriptions")


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


def page_date(text):
    return re.search(r"Evaluated as of (\d{4}-\d\d-\d\d)", text).group(1)


# ------------------------------------------------------------------ phase B: a scratch copy, FIRST
assert srv.server_info()["version"] == RELEASE, srv.server_info()["version"]
scr = SCR / "lab32"
assert not scr.exists(), "a fresh scratch folder each run"
shutil.copytree(FIX / "package", scr / "package")
shutil.copytree(FIX / "workspace", scr / "workspace")
srv.PACKAGE_ROOT = scr

# B1: the page the previous release exported, read by name before anything is opened
before = keys("package")
assert before == {"review_current": True, "review_exported_by": PREVIOUS}, before
obs("B.before", before)
o = srv.package_open("package")
assert o["ok"], o
obs("B.open.resume", {"handoff": o["resume"]["handoff"]["id"], "behind": o["resume"]["handoff_behind"]})

# B2: the guide refreshed to the 5.8.1 stock (its title only; lint 9's key landed with the stamp)
(scr / "CLAUDE.md").write_text("# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n",
                               encoding="utf-8", newline="\n")
em = srv.handoff_emit(str(scr), refresh_stock=True)
assert em["ok"], em
assert "prompts/README.md" in em["prompt_library"]["refreshed"], em["prompt_library"]
guide = (scr / "package" / "prompts" / "README.md").read_text(encoding="utf-8")
assert f"tamheed v{RELEASE}" in guide
obs("B.guide", {"refreshed": em["prompt_library"]["refreshed"], "title": f"tamheed v{RELEASE}"})

# B3: the rule under the real agents' pattern - a handoff whose line is re-measured and re-dated
# each time shares no line with the two before it; the rule stays silent (the lab run's B1-B3)
hr = rule("handoff-repeated")
assert hr["status"] == "pass" and hr["entities"] == [], hr
n0 = hr["population"]["rows"]
for i, day in enumerate(("09:00", "10:00", "11:00")):
    pe(f"RESUME AT: the scratch beat, step {i + 1}\nAWAITING THE OPERATOR:\n- the planted question,"
       f" re-read {TODAY} {day} against the register: Proposed, no ruling since\n"
       f"VERIFIED FACTS: gate_run read at {day}", event_type="handoff")
hr = rule("handoff-repeated")
assert hr["status"] == "pass" and hr["entities"] == [] and hr["population"]["rows"] == n0 + 3, hr
obs("B.rule.re-dated-lines", {"status": hr["status"], "handoffs": hr["population"]["rows"]})

# B4: the export on 5.8.1 - the stamp names the release, the store's digest does not move
digest0 = srv.package_verify()["digest"]
assert srv.export_html()["ok"]
page = (scr / "package" / "review.html").read_text(encoding="utf-8")
assert STAMP in page[:4096] and srv.package_verify()["digest"] == digest0
assert keys() == {"review_current": True, "review_exported_by": RELEASE}
obs("B.page", {"stamp": RELEASE, "date": page_date(page)})
srv.package_close()
assert not (scr / "package" / "data" / ".lock").exists()
print("PHASE-B-DONE")

# ------------------------------------------------------------------ phase A: the fixture
srv.PACKAGE_ROOT = FIX
fixture_before = keys("package")
assert fixture_before == {"review_current": True, "review_exported_by": PREVIOUS}, fixture_before
obs("A.before", fixture_before)
o = srv.package_open("package")
assert o["ok"], o
info = srv.server_info()
assert info["version"] == RELEASE and info["schema_version"] == 7
obs("A.schema", {"schema_version": info["schema_version"], "migrations_head": info["migrations_head"],
                 "version": info["version"]})
obs("A.open.resume", {"handoff": o["resume"]["handoff"]["id"], "behind": o["resume"]["handoff_behind"]})
target = SCR / "target32"
shutil.copytree(FIX / "workspace", target / "workspace")
em = srv.handoff_emit(str(target), refresh_stock=True)
assert em["ok"] and "prompts/README.md" in em["prompt_library"]["refreshed"], em
guide = (FIX / "package" / "prompts" / "README.md").read_text(encoding="utf-8")
assert f"tamheed v{RELEASE}" in guide
obs("A.guide", f"tamheed v{RELEASE}")

pe("Beat 32 (plan 173, the v5.8.1 continuation), opened at schema_version 7 (no migration, no"
   " engine change in 5.8.1). THE CORRECTION: the field's FB-028 read the 5.8.0 condition false -"
   f" {CORRECTION}; measured twice (the field's process at 2.1.284, the maintainer's at 2.1.285)"
   " and a control. THE RUNS: the lab was driven by a real agent, headless, through the plugin's"
   " own path against this release - a fresh run from the seed (items 1-9, one planning process"
   " and twelve execution processes) and four sessions on a copy of this package; 38 predicates"
   " pass, 17 engine refusals answered by re-reading, no engine defect; handoff-repeated fired"
   " on a line the agents had not re-measured and cleared once one rewrote it with the date,"
   " while the planted question, re-dated each session as the skill teaches, never tripped it."
   f" The evidence: {REPORT}. THE EMISSION: refresh_stock carried the guide to tamheed"
   f" v{RELEASE}, its title only, no finding.", event_type="note")
h = pe("Resume at: the next continuation beat (33). In flight: none - beat 32 closed. Awaiting"
       " the operator: nothing. Verified facts: handoff-current pass and handoff-repeated pass,"
       f" both read after this entry; the guide reads the {RELEASE} stock. The export, gate_run"
       " and package_verify FOLLOW this entry, so their results are in the evidence report and"
       " not here. Do not carry: the scratch copy's three handoffs - never written to this"
       " package.", event_type="handoff")
obs("A.handoff", h["ids"][0])
assert rule("handoff-current")["status"] == "pass"
assert rule("handoff-repeated")["status"] == "pass"
obs("A.handoffs", rule("handoff-repeated")["population"]["rows"])
assert keys()["review_current"] is False
fixture_page_before = (FIX / "package" / "review.html").read_text(encoding="utf-8")
ex = srv.export_html()
assert ex["ok"], ex
page = (FIX / "package" / "review.html").read_text(encoding="utf-8")
assert STAMP in page[:4096] and f"Latest handoff: {h['ids'][0]}" in page
obs("A.page", {"date_before": page_date(fixture_page_before), "date_after": page_date(page),
               "lines_before": fixture_page_before.count("\n"), "lines_after": page.count("\n")})
g = srv.gate_run()
assert g["ready"]
obs("A.gate_run.ready", g["ready"])
v = srv.package_verify()
assert v["verified"] and v["review_current"] and not v["dirty"] and v["review_exported_by"] == RELEASE
obs("A.verify", {k: v.get(k) for k in ("verified", "dirty", "foreign", "review_current", "review_exported_by")})
srv.package_close()
obs("A.lock_gone", not (FIX / "package" / "data" / ".lock").exists())
