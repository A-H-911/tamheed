"""Lab beat 33 (plan 189): the v5.9.0 continuation against the recorded lab-tracker package,
in-process through the engine's tool functions. The scratch phase (a real agent running
`/tamheed:ste-rewrite` through the headless harness, `run-33.md`) runs FIRST and writes nothing
here; this script then writes the FIXTURE (committed): the guide refreshed to the 5.9.0 body, the
note rebuilt as v6, the readiness rule's counts quoted, the closing note, the handoff LAST, the
export, the gate, the verify, the close. Every observation prints as `OBS <key>: <value>`.

Run:  env -u TAMHEED_HOOK_LOG python beat33.py <scratch dir> <scratch session id> <before counts> <after counts>
"""
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

FIX = REPO / "evals" / "sample-results" / "lab-tracker"
SCR = Path(sys.argv[1])
SESSION, BEFORE, AFTER = sys.argv[2], sys.argv[3], sys.argv[4]
ACTOR = "agent:lab-beat-33"
RELEASE, PREVIOUS = "5.9.0", "5.8.1"
STAMP = f'<meta name="tamheed-version" content="{RELEASE}">'
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
REPORT = "plans/evidence/lab-continuation-report-189-2026-10-04.md"


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


# ------------------------------------------------------------------ the fixture
assert srv.server_info()["version"] == RELEASE, srv.server_info()["version"]
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

# A1: the readiness rule the release adds, read before any write
pr = rule("prose-plain-english")
assert pr and pr["status"] == "fail", pr
obs("A.rule.before", {"status": pr["status"], "counts": pr["counts"], "texts": pr["population"]["rows"]})
assert pr["counts"] == json.loads(BEFORE), (pr["counts"], BEFORE)

# A2: the emission: the guide refreshed to the 5.9.0 body, the note rebuilt as v6
target = SCR / "target33"
shutil.copytree(FIX / "workspace", target / "workspace")
(target / "CLAUDE.md").write_text("# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n",
                                  encoding="utf-8", newline="\n")
em = srv.handoff_emit(str(target), refresh_stock=True)
assert em["ok"] and "prompts/README.md" in em["prompt_library"]["refreshed"], em
guide = (FIX / "package" / "prompts" / "README.md").read_text(encoding="utf-8")
assert f"tamheed v{RELEASE}" in guide and "nine **discipline skills**" in guide
note = (FIX / "package" / "CLAUDE.md").read_text(encoding="utf-8")
assert "<!-- tamheed:note v6 -->" in note and "tamheed:note v5" not in note
first = next(l for l in note.splitlines() if "Tamheed package for this project" in l)
obs("A.guide", {"refreshed": em["prompt_library"]["refreshed"], "title": f"tamheed v{RELEASE}"})
obs("A.note", {"marker": "tamheed:note v6", "first_sentence": first[:90]})
assert "tamheed:plain-english" in note

# A3: the closing note, then the handoff LAST
counts_before = json.dumps(pr["counts"], sort_keys=True)
counts_after = json.dumps(json.loads(AFTER), sort_keys=True)
texts = pr["population"]["rows"]
pe(f"Beat 33 (plan 189, the v{RELEASE} continuation) opened at schema_version 7. No migration."
   f" THE RULE: readiness_check reports prose-plain-english as an advisory. It read {counts_before}"
   f" over {texts} texts of this record. The value of ready did not move on it."
   f" THE SCRATCH PHASE ran first, on a copy, by a real agent through the headless harness"
   f" (session {SESSION}). The skill /tamheed:ste-rewrite named the same texts. It proposed batch 1"
   " and STOPPED. On the operator's words it rewrote one Approved assumption in place with"
   " expect_unchanged. It superseded one immutable row (ADR-0001 by ADR-0002), and the operator"
   f" approved the successor. The counts read {counts_after} after those two writes. No row of"
   " this record was written there. THE EMISSION: refresh_stock carried the guide to tamheed"
   f" v{RELEASE}. The guide names nine discipline skills. The note was rebuilt as tamheed:note v6,"
   " and its first sentence names the package. The evidence: " + REPORT + ".", event_type="note")
h = pe("Resume at: the next continuation beat (34). In flight: none. Beat 33 is closed. Awaiting"
       " the operator: whether this record's own prose is rewritten. The skill /tamheed:ste-rewrite"
       " is the operator's choice, and the rule only reports. Verified facts: handoff-current and"
       f" handoff-repeated both pass, read after this entry. The guide reads the {RELEASE} stock."
       f" The note is v6. The rule prose-plain-english read {counts_before} on this record before"
       " this entry. The export, gate_run and package_verify FOLLOW this entry. Their results are"
       " in the evidence report and not here. Do not carry: the scratch copy's rows. They were"
       " never written to this package.", event_type="handoff")
obs("A.handoff", h["ids"][0])
assert rule("handoff-current")["status"] == "pass"
assert rule("handoff-repeated")["status"] == "pass"
obs("A.handoffs", rule("handoff-repeated")["population"]["rows"])
pr_after = rule("prose-plain-english")
obs("A.rule.after", {"status": pr_after["status"], "counts": pr_after["counts"], "texts": pr_after["population"]["rows"]})
assert "PE-" not in " ".join(e for e in pr_after["entities"] if e.startswith("PE-")), pr_after["entities"]
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
print("PHASE-A-DONE")
