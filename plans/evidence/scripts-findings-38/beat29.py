"""Lab beat 29 (plan 158): fire what v5.6.1 teaches against the recorded lab-tracker package,
in-process through the engine's tool functions (the same code path the MCP tools call).
Phase B runs FIRST, on a SCRATCH copy (never committed), with hard assertions: a failure stops
the beat before the fixture is touched. Phase A then writes the FIXTURE (committed) and its note
quotes what phase B observed. Every observation is printed as `OBS <key>: <value>`.
The operator's own trace variable is removed before the engine is imported; this beat runs no hook.

Run:  env -u TAMHEED_HOOK_LOG python plans/evidence/scripts-findings-38/beat29.py <scratch dir>
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
ACTOR = "agent:lab-beat-29"
RELEASE, PREVIOUS = "5.6.1", "5.6.0"
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


def hashes(package: Path) -> dict:
    files = [package / "review.html", *sorted((package / "csv").glob("*.csv"))]
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files}


def page_date(text):
    return re.search(r"Evaluated as of (\d{4}-\d\d-\d\d)", text).group(1)


# ------------------------------------------------------------------ phase B: a scratch copy, FIRST
assert srv.server_info()["version"] == RELEASE, srv.server_info()["version"]
scr = SCR / "lab29"
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

# B2: the first export on this release, before any write - what the page's diff holds
digest0 = srv.package_verify()["digest"]
assert srv.export_html()["ok"]
page = PAGE.read_text(encoding="utf-8")
assert STAMP in page[:4096] and srv.package_verify()["digest"] == digest0
moved = [(a, b) for a, b in zip(old_page.split("\n"), page.split("\n")) if a != b]
assert len(old_page.split("\n")) == len(page.split("\n"))
same_day = page_date(old_page) == TODAY
assert len(moved) == (1 if same_day else 2), (len(moved), page_date(old_page), TODAY)
assert PREVIOUS in moved[0][0] and RELEASE in moved[0][1] and "tamheed-version" in moved[0][1]
after = keys()
assert after == {"review_current": True, "review_exported_by": RELEASE}, after
obs("B.first_export", {"lines_changed": len(moved), "same_utc_date": same_day,
                       "page_dated": page_date(old_page), "today": TODAY, "after": after,
                       "digest_moved": False})

# B3: a read cut by `limit` returns the LOWEST ids; the resume block names the newest
every = srv.entity_query("progress-entry", columns=["id"], limit=10000)
assert every["ok"] and every["count"] == every["total"], every
ids = [r["id"] for r in every["rows"]]
limited = [r["id"] for r in srv.entity_query("progress-entry", columns=["id"], limit=10)["rows"]]
newest = sorted(ids, key=num)[-3:]
last = [e["id"] for e in resume["last_entries"]]
assert limited == sorted(ids)[:10], limited
assert sorted(last, key=num) == newest, (last, newest)
assert not set(limited) & set(newest)
assert max(num(i) for i in limited) < min(num(i) for i in newest)
obs("B.limited_read", {"total": every["total"], "limit_10_returned": [limited[0], limited[-1]],
                       "resume_last_entries": last})

# B4: ONE work entry past the latest handoff - the count, the rule's list, and the read by ids
assert resume["handoff_behind"] == 0 and rule("handoff-current")["entities"] == []
w = pe("Beat 29 scratch entry: one unit of work after the latest handoff.",
       event_type="work-done")["ids"][0]
block = srv.server_info()["resume"]
named = rule("handoff-current")["entities"]
assert block["handoff_behind"] == 1 and named == [w], (block["handoff_behind"], named)
back = srv.entity_query("progress-entry", ids=named)
assert [r["id"] for r in back["rows"]] == [w] and "one unit of work" in back["rows"][0]["entry"]
obs("B.work_after_handoff", {"handoff_behind": 1, "handoff_current_names": named,
                             "read_back_by_ids": True})

# B5: one store, one fixed report, two dates - the date is the only input besides the store
conn = srv._CURRENT.conn
gates = srv.gate_run()["gates"]
fixed = {"report": srv._readiness_report(conn, "package", None),
         "resume": srv._resume_block(conn, srv._CURRENT_NAME, scr / "package" / "data"),
         "note_roster": {"ids": [r[0] for r in srv._note_lesson_rows(conn)],
                         "cap": srv._NOTE_LESSONS_CAP}}
day_a, day_b = "2999-01-01", "2999-01-02"
page_a, page_b = (viewer.render(conn, gates, False, {**fixed, "as_of": day}) for day in (day_a, day_b))
assert (page_a.count(day_a), page_b.count(day_b)) == (1, 1)
assert page_a != page_b and page_a.replace(day_a, day_b) == page_b
line = next(ln for ln in page_a.split("\n") if day_a in ln)
obs("B.two_dates", {"pages_differ": True, "equal_after_replacing_the_date": True,
                    "chars_of_the_line_that_holds_the_date": len(line)})

# B6: the read-only audit's export - outside the package; the package's page and csv/ untouched
held = hashes(scr / "package")
outside = SCR / "audit29" / "review.html"
shutil.rmtree(outside.parent, ignore_errors=True)
ex = srv.export_html(output=str(outside))
assert ex["ok"] and Path(ex["path"]) == outside and outside.exists(), ex
assert hashes(scr / "package") == held
fresh = re.search(r"Freshness: ([^<]+)<", outside.read_text(encoding="utf-8")).group(1)
assert keys()["review_current"] is False            # the package's own page still lacks B4's write
obs("B.export_outside", {"package_files_unchanged": len(held), "freshness_line": fresh})
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
target = SCR / "target29"
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

pe("Beat 29 (plan 158, the v5.6.1 continuation), opened at schema_version 7 (no migration in"
   " 5.6.1). WHAT A LIMITED READ RETURNS: a read limited to ten rows returned the ten lowest ids"
   f" of the journal ({limited[0]} to {limited[-1]} of {every['total']}), while the resume block"
   " named the three newest; rows come in the id's text order. One work entry written past the"
   " latest handoff on the scratch copy: handoff_behind read 1, handoff-current named that entry,"
   " and ids read it back. THE PAGE'S DATE: two dates over one store differed in the date and"
   " nowhere else - one page with its date replaced equalled the other byte for byte. THE FIRST"
   f" EXPORT on the release changed the stamp's line from {PREVIOUS} to {RELEASE}"
   f" ({len(moved)} line(s) changed, the scratch export being on "
   f"{'the same' if same_day else 'a later'} UTC date), the digest unchanged. THE AUDIT WRITES"
   " NOTHING: an export to a path outside the package left the page and csv/ untouched."
   f" THE EMISSION: refresh_stock carried the guide to tamheed v{RELEASE}, its title only, no"
   " finding.", event_type="note")
h = pe("Resume at: the next continuation beat (30). In flight: none - beat 29 closed. Awaiting"
       " the operator: nothing. Verified facts: handoff-current pass, read after this entry;"
       f" the guide reads the {RELEASE} stock. The export, gate_run and package_verify FOLLOW this"
       " entry, so their results are in the evidence report and not here. Do not carry: the"
       " scratch copy's work entry and its export outside the package - never written to this"
       " package.", event_type="handoff")
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
