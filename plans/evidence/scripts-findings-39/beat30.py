"""Lab beat 30 (plan 163): fire what v5.7.0 changes against the recorded lab-tracker package,
in-process through the engine's tool functions (the same code path the MCP tools call).
Phase B runs FIRST, on a SCRATCH copy (never committed), with hard assertions: a failure stops
the beat before the fixture is touched. Phase A then writes the FIXTURE (committed) and its note
quotes what phase B observed. Every observation is printed as `OBS <key>: <value>`.
The operator's own trace variable is removed before the engine is imported; this beat runs no hook.

Run:  env -u TAMHEED_HOOK_LOG python plans/evidence/scripts-findings-39/beat30.py <scratch dir>
"""
import hashlib
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
import export_html as viewer  # noqa: E402
import tamheed_server as srv  # noqa: E402

FIX = REPO / "evals" / "sample-results" / "lab-tracker"
SCR = Path(sys.argv[1])
ACTOR = "agent:lab-beat-30"
RELEASE, PREVIOUS = "5.7.0", "5.6.1"
STAMP = f'<meta name="tamheed-version" content="{RELEASE}">'
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


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


def num(entity_id):
    return int(entity_id.split("-")[1])


def ids_of(result):
    assert result["ok"], result
    return [r["id"] for r in result["rows"]]


def count(family):
    return srv.entity_query(family, columns=["id"], limit=1)["total"]


def hashes(package: Path) -> dict:
    files = [package / "review.html", *sorted((package / "csv").glob("*.csv"))]
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files}


def page_date(text):
    return re.search(r"Evaluated as of (\d{4}-\d\d-\d\d)", text).group(1)


# ------------------------------------------------------------------ phase B: a scratch copy, FIRST
assert srv.server_info()["version"] == RELEASE, srv.server_info()["version"]
assert viewer._by_id is srv._by_id                   # one id order, the page's and the tool's
scr = SCR / "lab30"
shutil.rmtree(scr, ignore_errors=True)
shutil.copytree(FIX / "package", scr / "package")
shutil.copytree(FIX / "workspace", scr / "workspace")
srv.PACKAGE_ROOT = scr
PAGE = scr / "package" / "review.html"

# B1: before anything is opened - the page the PREVIOUS release exported, read by name
old_page = PAGE.read_text(encoding="utf-8")
before = keys("package")
assert before == {"review_current": True, "review_exported_by": PREVIOUS}, before
obs("B.before_first_export", before)

o = srv.package_open("package")
assert o["ok"], o
resume = o["resume"]
obs("B.open.resume", {"handoff": resume["handoff"]["id"], "behind": resume["handoff_behind"]})
(scr / "CLAUDE.md").write_text("# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n",
                               encoding="utf-8", newline="\n")
em = srv.handoff_emit(str(scr), refresh_stock=True)
assert em["ok"], em

# B2: the first export on this release, before any write - what the page's diff holds. The
# page held the id order already, so nothing but the stamp (and the date, on a later UTC date)
# may move.
digest0 = srv.package_verify()["digest"]
assert srv.export_html()["ok"]
page = PAGE.read_text(encoding="utf-8")
assert STAMP in page[:4096] and srv.package_verify()["digest"] == digest0
assert len(old_page.split("\n")) == len(page.split("\n"))
moved = [(a, b) for a, b in zip(old_page.split("\n"), page.split("\n")) if a != b]
same_day = page_date(old_page) == TODAY
assert len(moved) == (1 if same_day else 2), (len(moved), page_date(old_page), TODAY)
assert PREVIOUS in moved[0][0] and RELEASE in moved[0][1] and "tamheed-version" in moved[0][1]
if not same_day:
    # only WHERE THE PAGE STATES ITS DATE: the same line holds that date as data too, and
    # replacing every occurrence would move a stored timestamp with it
    stated = "Evaluated as of "
    assert moved[1][0].count(stated + page_date(old_page)) == 1
    assert moved[1][0].replace(stated + page_date(old_page), stated + TODAY) == moved[1][1]
after = keys()
assert after == {"review_current": True, "review_exported_by": RELEASE}, after
obs("B.first_export", {"lines_changed": len(moved), "same_utc_date": same_day,
                       "page_dated": page_date(old_page), "today": TODAY, "after": after,
                       "digest_moved": False})

# B3: the order. The lab's ids are all of one width, so a check on them would pass under
# EITHER order and prove nothing: two risks of two widths are written first.
held_risks = ids_of(srv.entity_query("risk", columns=["id"], limit=10000))
assert all(len(i) == len(held_risks[0]) for i in held_risks), held_risks
up = srv.entity_upsert([{"type": "risk", "id": i, "title": f"beat 30 scratch risk {i}"}
                        for i in ("RISK-998", "RISK-1000")])
assert up["ok"], up
every = ids_of(srv.entity_query("risk", columns=["id"], limit=10000))
assert every == sorted(every, key=num) and every != sorted(every), every
typed = ids_of(srv.entity_query("risk", after_id="RISK-998", columns=["id"]))
as_text = sorted(i for i in every if i > "RISK-998")
assert typed == ["RISK-1000"] and as_text == [], (typed, as_text)
absent = ids_of(srv.entity_query("risk", after_id="RISK-999", columns=["id"]))
assert absent == ["RISK-1000"], absent
walked, cursor = [], None
while True:
    out = srv.entity_query("risk", columns=["id"], limit=2, after_id=cursor)
    walked += ids_of(out)
    cursor = out["next_after"]
    if cursor is None:
        break
assert walked == every, (walked, every)
journal = ids_of(srv.entity_query("progress-entry", columns=["id"], limit=10000))
limited = ids_of(srv.entity_query("progress-entry", columns=["id"], limit=10))
assert limited == sorted(journal, key=num)[:10], limited
assert not set(limited) & {e["id"] for e in resume["last_entries"]}
obs("B.order", {"risks_in_number_order": True, "after_RISK-998_returned": typed,
                "the_text_cut_would_return": as_text, "a_bound_that_names_no_row": absent,
                "a_walk_at_limit_2_is_complete": True,
                "limit_10_on_the_journal": [limited[0], limited[-1]]})

# B4: the two write tools refuse a key they do not take, by name, and write nothing
digest1 = srv.package_verify()["digest"]
journal_rows, verdict_rows = count("progress-entry"), count("audit-verdict")
ac = ids_of(srv.entity_query("acceptance-criterion", columns=["id"], limit=1))[0]
refusals = {}
for label, call in (
        ("progress_update, summary for entry",
         lambda: srv.progress_update([{"summary": "what happened", "actor": ACTOR}])),
        ("progress_update, custom_attributes",
         lambda: srv.progress_update([{"entry": "x", "actor": ACTOR,
                                       "custom_attributes": {"ref": "abc1234"}}])),
        ("progress_update, no entry",
         lambda: srv.progress_update([{"event_type": "note", "actor": ACTOR}])),
        ("progress_update, one bad item of two",
         lambda: srv.progress_update([{"entry": "good", "actor": ACTOR},
                                      {"entry": "bad", "note": "n"}])),
        ("progress_update, an item that is no object",
         lambda: srv.progress_update(["a sentence"])),
        ("audit_record, a key it does not take",
         lambda: srv.audit_record([{"ac_id": ac, "verdict": "Met", "notes": "n"}])),
        ("audit_record, no verdict",
         lambda: srv.audit_record([{"ac_id": ac}]))):
    out = call()
    assert out["ok"] is False, (label, out)
    assert "constraint failed" not in out["error"], (label, out)      # words, never the raw text
    refusals[label] = out["error"][:160]
assert "'summary'" in refusals["progress_update, summary for entry"]
assert all(k in refusals["progress_update, summary for entry"] for k in srv._PROGRESS_KEYS)
assert "'custom_attributes'" in refusals["progress_update, custom_attributes"]
assert "`entry`" in refusals["progress_update, no entry"]
assert "'notes'" in refusals["audit_record, a key it does not take"]
assert all(k in refusals["audit_record, a key it does not take"] for k in srv._VERDICT_KEYS)
assert "`verdict`" in refusals["audit_record, no verdict"]
assert (count("progress-entry"), count("audit-verdict")) == (journal_rows, verdict_rows)
assert srv.package_verify()["digest"] == digest1
for tool, takes in (("progress_update", srv._PROGRESS_KEYS), ("audit_record", srv._VERDICT_KEYS)):
    assert all(k in srv.TOOLS[tool][1] for k in takes), tool
    assert len(srv.TOOLS[tool][1]) <= srv._DESCRIPTION_CAP
obs("B.refusals", {"refused": len(refusals), "rows_written": 0, "digest_moved": False,
                   "the_descriptions_name_every_key": True})

# B5: the read-only audit's export - outside the package. csv/ lands BESIDE the page at any
# `output`; the package's own page and csv/ are untouched.
assert srv.export_html()["ok"]                      # the package's page takes B3's two risks
held = hashes(scr / "package")
outside = SCR / "audit30" / "review.html"
shutil.rmtree(outside.parent, ignore_errors=True)
ex = srv.export_html(output=str(outside))
assert ex["ok"] and Path(ex["path"]) == outside and outside.exists(), ex
beside = sorted(p.name for p in (outside.parent / "csv").glob("*.csv"))
assert beside and beside == sorted(n for n in held if n.endswith(".csv")), beside
assert hashes(scr / "package") == held
assert outside.read_bytes() == PAGE.read_bytes()
obs("B.export_outside", {"package_files_unchanged": len(held), "csv_files_beside_the_output":
                         len(beside), "the_outside_page_equals_the_package_page": True})
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
target = SCR / "target30"
shutil.rmtree(target, ignore_errors=True)
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

pe("Beat 30 (plan 163, the v5.7.0 continuation), opened at schema_version 7 (no migration in"
   " 5.7.0). THE ORDER: entity_query orders and cuts by the review page's rule - prefix, the"
   " id's first number, the id. On the scratch copy, with risks of two widths written first,"
   f" a bound typed after RISK-998 returned {typed[0]}; compared as text the same read returned"
   " nothing. A bound that names no row returned the rows after it, a walk at limit 2 was"
   f" complete, and a read limited to ten rows still returned the ten lowest ids ({limited[0]}"
   f" to {limited[-1]}). THE REFUSALS: progress_update and audit_record were sent"
   f" {len(refusals)} items they do not take - a key the tool does not take was refused by name"
   " and nothing was written; a missing entry and a missing verdict were refused in words; the"
   " digest did not move. THE DESCRIPTIONS: the registered description of each of the two tools"
   " names every key it takes. THE FIRST EXPORT on the release changed the stamp's line from"
   f" {PREVIOUS} to {RELEASE} ({len(moved)} line(s) changed, the scratch export being on "
   f"{'the same' if same_day else 'a later'} UTC date), the digest unchanged: the page held this"
   " order already. THE AUDIT'S EXPORT: an export to a path outside the package wrote csv/ beside"
   f" it ({len(beside)} files) and left the package's page and csv/ untouched. THE EMISSION:"
   f" refresh_stock carried the guide to tamheed v{RELEASE}, its title only, no finding.",
   event_type="note")
h = pe("Resume at: the next continuation beat (31). In flight: none - beat 30 closed. Awaiting"
       " the operator: nothing. Verified facts: handoff-current pass, read after this entry;"
       f" the guide reads the {RELEASE} stock. The export, gate_run and package_verify FOLLOW this"
       " entry, so their results are in the evidence report and not here. Do not carry: the"
       " scratch copy's two risks, its refused writes and its export outside the package - never"
       " written to this package.", event_type="handoff")
obs("A.handoff", h["ids"][0])
obs("A.handoff-current.final", rule("handoff-current")["status"])
assert keys()["review_current"] is False                     # the handoff is itself a write
fixture_page_before = (FIX / "package" / "review.html").read_text(encoding="utf-8")
ex = srv.export_html()
assert ex["ok"], ex
page = (FIX / "package" / "review.html").read_text(encoding="utf-8")
assert STAMP in page[:4096] and f"Latest handoff: {h['ids'][0]}" in page
obs("A.page_date", {"before": page_date(fixture_page_before), "after": page_date(page)})
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
