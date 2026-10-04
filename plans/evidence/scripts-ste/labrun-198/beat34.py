"""Lab beat 34 (plan 198): the v6.0.0 continuation against the recorded lab-tracker package,
in-process through the engine's tool functions. The scratch phase (a real agent driving the
migration through the headless harness, `run-34.md`) runs FIRST and writes nothing here; this
script then writes the FIXTURE (committed): the migration previewed and confirmed, the kickoff
row approved on the operator's words, the emit (the root guide, the v7 note), the rule, the
closing note, the handoff LAST, the export (the Prompts section), the gate, the verify, the
close. Every observation prints as `OBS <key>: <value>`.

Run:  env -u TAMHEED_HOOK_LOG python beat34.py <scratch dir> <scratch session id>
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

sys.stdout.reconfigure(encoding="utf-8")
FIX = REPO / "evals" / "sample-results" / "lab-tracker"
PKG = FIX / "package"
SCR = Path(sys.argv[1])
SESSION = sys.argv[2]
ACTOR = "agent:lab-beat-34"
RELEASE, PREVIOUS = "6.0.0", "5.9.0"
STAMP = f'<meta name="tamheed-version" content="{RELEASE}">'
REPORT = "plans/evidence/lab-continuation-report-198-2026-10-04.md"


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


# ------------------------------------------------------------------ the fixture before
assert srv.server_info()["version"] == RELEASE, srv.server_info()["version"]
srv.PACKAGE_ROOT = FIX
fixture_before = keys("package")
assert fixture_before == {"review_current": True, "review_exported_by": PREVIOUS}, fixture_before
obs("A.before", fixture_before)
o = srv.package_open("package")
assert o["ok"], o
info = srv.server_info()
assert info["version"] == RELEASE and info["schema_version"] == 8, info
obs("A.schema", {"schema_version": info["schema_version"], "migrations_head": info["migrations_head"],
                 "entry_point": info["package"]["entry_point"]})
obs("A.open.resume", {"handoff": o["resume"]["handoff"]["id"], "behind": o["resume"]["handoff_behind"]})
obs("A.gset.before", srv.gate_run()["gates"]["G-SET"])      # the registry has no `prompt` row yet
srv.package_close()

# A1: the preview
pre = srv.package_migrate("package")
assert pre["ok"] and pre["stage"] == "preview", pre
rep = pre["report"]
by_file = {f["file"]: f for f in rep["prompt_files"]}
assert by_file["prompts/project-kickoff.md"]["kind"] == "kickoff", by_file
assert by_file["prompts/README.md"]["action"].startswith("remove"), by_file
assert rep["prompt_rows"] == ["PRT-001"], rep["prompt_rows"]
assert rep["entry_point"] == {"from": "prompts/project-kickoff.md", "to": "PRT-001"}, rep["entry_point"]
assert rep["prompts_folder"] == "remove", rep["prompts_folder"]
assert "g_set" not in rep
obs("A.preview", {"files": [(f["file"], f["action"]) for f in rep["prompt_files"]],
                  "entry_point": rep["entry_point"], "folder": rep["prompts_folder"],
                  "registry": rep.get("entity_types_added")})
assert (PKG / "prompts" / "project-kickoff.md").exists()      # the preview wrote nothing

# A2: the confirm, on the operator's word
out = srv.package_migrate("package", confirm=True)
assert out["ok"], out
obs("A.confirm", out["report"]["prompt_files_applied"])
assert not (PKG / "prompts").exists()
backup = PKG / "prompts-v5-backup"
assert sorted(q.name for q in backup.iterdir()) == ["project-kickoff.md"], list(backup.iterdir())
shutil.rmtree(backup)                                          # git holds the file (the ledger says so)
obs("A.backup_removed", not backup.exists())

o = srv.package_open("package")
assert o["ok"], o
assert srv.server_info()["package"]["entry_point"] == "PRT-001"
row = srv.entity_query("prompt", ids=["PRT-001"])["rows"][0]
assert row["kind"] == "kickoff" and row["lifecycle_status"] == "Proposed", row
attrs = json.loads(row["custom_attributes"])
assert attrs["converted_from"] == "prompts/project-kickoff.md", attrs
obs("A.row", {"id": row["id"], "kind": row["kind"], "title": row["title"], "status": row["lifecycle_status"],
              "converted_from": attrs["converted_from"], "body_lines": row["body"].count("\n") + 1})
g = srv.gate_run()["gates"]["G-SET"]
assert g["status"] == "pass", g
obs("A.gset.after", g["status"])

# A3: the STOP, then the operator's words
target = SCR / "target34"
shutil.copytree(FIX / "workspace", target / "workspace")
(target / "CLAUDE.md").write_text("# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n",
                                  encoding="utf-8", newline="\n")
refused = srv.handoff_emit(str(target), refresh_stock=True)
assert not refused["ok"] and "PRT-001 is Proposed, not Approved" in refused["error"], refused
obs("A.stop", refused["error"][:200])
full = {c: row.get(c) for c in srv._PROMPT_COLUMNS}
full.update({"type": "prompt", "lifecycle_status": "Approved"})
ap = srv.entity_upsert([full])
assert ap["ok"], ap
obs("A.approved", ap["results"][0] if "results" in ap else ap)

# A4: the emission: the root guide, the v7 note with the prompt roster
em = srv.handoff_emit(str(target), refresh_stock=True)
assert em["ok"], em
lib = em["prompt_library"]
obs("A.library", lib)
assert (PKG / "README.md").exists(), lib
guide = (PKG / "README.md").read_text(encoding="utf-8")
assert f"tamheed v{RELEASE}" in guide and "nine **discipline skills**" in guide
note = (PKG / "CLAUDE.md").read_text(encoding="utf-8")
assert "<!-- tamheed:note v7 -->" in note and "tamheed:note v6" not in note
roster = next(l for l in note.splitlines() if "PRT-001" in l)
first = next(l for l in note.splitlines() if "Tamheed package for this project" in l)
obs("A.guide", {"library": {k: v for k, v in lib.items() if k in ("written", "refreshed", "unchanged", "leftovers")},
                "title": f"tamheed v{RELEASE}"})
obs("A.note", {"marker": "tamheed:note v7", "first_sentence": first[:90], "roster_line": roster[:160]})
obs("A.emit.stale", em.get("stale_references"))

# A5: the rule over the rows
pr = rule("prompt-ids-resolve")
assert pr and pr["status"] == "pass", pr
obs("A.rule", {"status": pr["status"], "population": pr["population"], "entities": pr["entities"]})

# A6: the closing note, then the handoff LAST
pe(f"Beat 34 (plan 198, the v{RELEASE} continuation) opened at schema_version 8 (migration 008)."
   " THE MIGRATION: package_migrate previewed one project file, prompts/project-kickoff.md, as the"
   " kickoff PRT-001, and the stock guide under prompts/ as a shipped body to remove. On the"
   " operator's word the confirm wrote PRT-001 Proposed with converted_from in its attributes,"
   " moved the file to prompts-v5-backup/, removed the folder, and set entry_point to PRT-001."
   " G-SET passed with the row present (the family is Always since 6.0.0). THE STOP: handoff_emit"
   " refused while PRT-001 was Proposed and named the row. The operator approved PRT-001 as the"
   " kickoff (2026-10-04, lab beat 34), set in place. THE EMISSION: the guide was written at the"
   f" package root (README.md, tamheed v{RELEASE}), and the note was rebuilt as tamheed:note v7"
   " with PRT-001 in its prompt roster. THE RULE: prompt-ids-resolve read pass over the rows."
   " THE SCRATCH PHASE ran first, on a copy, by a real agent through the headless harness"
   f" (session {SESSION}): the same preview, the STOP with nothing written, then the confirm, the"
   " approval, the emit and the export on the operator's words. No row of this record was written"
   " there. The evidence: " + REPORT + ".", event_type="note")
h = pe("Resume at: the next continuation beat (35). In flight: none. Beat 34 is closed. Awaiting the"
       " operator: nothing. Verified facts: the kickoff is PRT-001, Approved, the row entry_point"
       f" names. The guide is at the package root and reads tamheed v{RELEASE}. The note is v7."
       " prompt-ids-resolve read pass before this entry. The export, gate_run and package_verify"
       " FOLLOW this entry. Their results are in the evidence report and not here. Do not carry:"
       " the scratch copy's rows. They were never written to this package.", event_type="handoff")
obs("A.handoff", h["ids"][0])
assert rule("handoff-current")["status"] == "pass"
assert rule("handoff-repeated")["status"] == "pass"
assert keys()["review_current"] is False
page_before = (PKG / "review.html").read_text(encoding="utf-8")
ex = srv.export_html()
assert ex["ok"], ex
page = (PKG / "review.html").read_text(encoding="utf-8")
assert STAMP in page[:4096] and f"Latest handoff: {h['ids'][0]}" in page
assert '<section id="prompts">' in page
section = page.split('<section id="prompts">')[1].split("</section>")[0]
assert "Approved (the execution half" in section and "PRT-001" in section and "<td>yes</td>" in section
obs("A.page", {"date_before": page_date(page_before), "date_after": page_date(page),
               "lines_before": page_before.count("\n"), "lines_after": page.count("\n"),
               "prompts_section": True})
g = srv.gate_run()
assert g["ready"], g["gates"]
obs("A.gate_run.ready", g["ready"])
v = srv.package_verify()
assert v["verified"] and v["review_current"] and not v["dirty"] and not v["foreign"]
assert v["review_exported_by"] == RELEASE, v
obs("A.verify", {k: v.get(k) for k in ("verified", "dirty", "foreign", "review_current", "review_exported_by")})
srv.package_close()
obs("A.lock_gone", not (PKG / "data" / ".lock").exists())
print("PHASE-A-DONE")
