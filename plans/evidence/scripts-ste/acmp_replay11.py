"""Replay the 6.0.0 bundle over read-only COPIES of the field package, taken by `git archive` at
the field's HEAD (plan 199): the classes of the 6.0.0 brief. The state a 6.0 server meets before
the migration (G-SET vacuous, the rules blind to the prompt files), the migrate preview on a CLOSED
package, the confirm, the STOP (the emit refused on a Proposed kickoff), the approval in place, the
two bindings and the guard's refusal, the emit with refresh_stock (the v7 note, the roster, the
stale scan over AGENTS.md), the export (the Prompts section), readiness over rows, ste-clean on
the root guide, the hook over the v5 note and the v7 note, and the wire. Prints ids, counts and
classes; never a line of the field's text.

Run:  env -u TAMHEED_HOOK_LOG PYTHONIOENCODING=utf-8 python acmp_replay11.py <field repo> <scratch dir>
      Fresh folders are created under <scratch dir>; nothing is removed.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
HERE = Path(__file__).resolve().parent
OLD_SCRIPTS = HERE.parent / "scripts-fb026-fb027"
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

FIELD, SCR = Path(sys.argv[1]), Path(sys.argv[2])
HOOK = BUNDLE / "server" / "resume_hook.py"
SID = "64b2af54-e22c-4e2e-9d13-8c7792eb2b78"
RELEASE = "6.0.0"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
PKG = "tamheed-package"
sys.stdout.reconfigure(encoding="utf-8")


def obs(k, v):
    print("OBS", k, json.dumps(v, ensure_ascii=False, default=str)[:1400])


def archive(name):
    dest = SCR / name
    dest.mkdir()
    tar = SCR / f"{name}.tar"
    with tar.open("wb") as fh:
        subprocess.run(["git", "-C", str(FIELD), "archive", "HEAD", PKG], check=True, stdout=fh)
    subprocess.run(["tar", "-x", "-C", str(dest), "-f", str(tar)], check=True)
    for root_file in ("CLAUDE.md", "AGENTS.md"):
        (dest / root_file).write_text((FIELD / root_file).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    return dest


def git(where, *a):
    return subprocess.run(["git", "-C", str(where), *a], capture_output=True, check=True).stdout.decode("utf-8", "replace")


def commit(where, msg):
    git(where, "add", "-A"); git(where, "-c", "user.email=x@y", "-c", "user.name=x", "commit", "-q", "-m", msg)


def run_hook(event, where, trace):
    env = dict(ENV, CLAUDE_PROJECT_DIR=str(where), TAMHEED_HOOK_LOG=str(trace))
    return subprocess.run(["uv", "run", "--no-project", str(HOOK)], input=json.dumps(event),
                          capture_output=True, text=True, env=env, cwd=str(where), encoding="utf-8")


def ste_clean(pkg_dir):
    r = subprocess.run([sys.executable, str(REPO / "evals" / "pkg_check.py"), "ste-clean", str(pkg_dir)],
                       capture_output=True, text=True, env=ENV, encoding="utf-8")
    hard = [ln for ln in r.stdout.splitlines() if ln.startswith("  ")]
    return {"exit": r.returncode, "first_line": r.stdout.splitlines()[0][:200] if r.stdout else "", "hard": len(hard)}


def rule(name):
    return next((x for x in srv.readiness_check("package")["rules"] if x["rule"] == name), None)


head = git(FIELD, "rev-parse", "--short=8", "HEAD").strip()
dirty = [ln[3:] for ln in git(FIELD, "status", "--porcelain").splitlines()]
obs("field.head", {"head": head, "uncommitted_in_the_field_tree": dirty[:6]})
copy = archive("acmp-replay11")
pkg = copy / PKG
git(copy, "init", "-q"); commit(copy, "field head")

# ---- class 1: the server
srv.PACKAGE_ROOT = copy
info = srv.server_info()
obs("server_info", {k: info[k] for k in ("version", "migrations_head", "schema_version")})
assert info["version"] == RELEASE and info["schema_version"] == 8

# ---- class 2: what the 6.0 server meets BEFORE the migration
v0 = srv.package_verify(PKG)
obs("verify.before", {k: v0.get(k) for k in ("verified", "review_current", "review_exported_by", "dirty", "foreign")})
note_v5 = (pkg / "CLAUDE.md").read_text(encoding="utf-8")
obs("note.before", {"marker": re.search(r"tamheed:note v\d", note_v5).group(0)})
o = srv.package_open(PKG)
assert o["ok"], o
obs("open.resume", {"handoff": o["resume"]["handoff"]["id"], "behind": o["resume"]["handoff_behind"],
                    "entry_point": srv.server_info()["package"]["entry_point"]})
g0 = srv.gate_run()["gates"]["G-SET"]
reg = srv.entity_query("prompt", limit=1)
pr0 = rule("prose-plain-english")
pid0 = rule("prompt-ids-resolve")
obs("before.migrate", {"gset": g0, "prompt_rows": reg["total"],
                       "prose_plain_english": {"status": pr0["status"], "counts": pr0["counts"], "texts": pr0["population"]["rows"],
                                               "prompt_files_named": sum(1 for e in pr0["entities"] if e.startswith("prompts/"))},
                       "prompt_ids_resolve": {"status": pid0["status"], "population": pid0["population"]}})
files_before = sorted(q.name for q in (pkg / "prompts").glob("*.md"))
obs("prompt_files.before", files_before)
obs("ste-clean.before", ste_clean(pkg))
srv.package_close()

# ---- class 3: the preview, on a CLOSED package
refused_open = None
pre = srv.package_migrate(PKG)
assert pre["ok"] and pre["stage"] == "preview", pre
rep = pre["report"]
obs("preview", {"mode": rep.get("mode"), "registry_added": rep.get("entity_types_added"),
                "files": [(f["file"], f["action"].split(",")[0], f.get("kind"), (f.get("title") or "")[:40]) for f in rep["prompt_files"]],
                "rows": rep.get("prompt_rows"), "entry_point": rep.get("entry_point"), "folder": rep.get("prompts_folder"),
                "backup": rep.get("prompts_backup"), "g_set": rep.get("g_set")})
assert sorted(q.name for q in (pkg / "prompts").glob("*.md")) == files_before      # nothing written
assert git(copy, "status", "--porcelain").strip() == ""

# the preview is refused on an OPEN package (the lab agent met this)
srv.package_open(PKG)
refused_open = srv.package_migrate(PKG)
obs("preview.on_open_package", {"ok": refused_open.get("ok"), "error": str(refused_open.get("error"))[:120]})
srv.package_close()

# ---- class 4: the confirm, on the operator's word
out = srv.package_migrate(PKG, confirm=True)
assert out["ok"], out
obs("confirm", {"stage": out.get("stage"), "applied": out["report"].get("prompt_files_applied"),
                "entry_point": out["report"].get("entry_point"), "rows": out["report"].get("prompt_rows")})
obs("backup.files", sorted(q.name for q in (pkg / "prompts-v5-backup").iterdir()))
obs("prompts_folder_gone", not (pkg / "prompts").exists())
obs("root_readme", {"exists": (pkg / "README.md").exists(),
                    "title_release": f"tamheed v{RELEASE}" in (pkg / "README.md").read_text(encoding="utf-8").splitlines()[0]})
changed = git(copy, "status", "--porcelain", "-uall").splitlines()
obs("files_changed_by_the_migrate", sorted(ln[3:] for ln in changed))
commit(copy, "migrate")
o = srv.package_open(PKG)
assert o["ok"], o
rows = srv.entity_query("prompt", limit=20)["rows"]
obs("rows", [(r["id"], r["kind"], r["lifecycle_status"], json.loads(r["custom_attributes"])["converted_from"], len(r["body"])) for r in rows])
kick = srv.server_info()["package"]["entry_point"]
obs("entry_point.after", kick)
gates_after = srv.gate_run()["gates"]
obs("gates.after", {"G-SET": gates_after["G-SET"], "G-IDS": gates_after["G-IDS"]["status"], "G-REL": gates_after["G-REL"]["status"]})

# ---- class 5: the STOP
refused = srv.handoff_emit(str(copy), refresh_stock=True)
assert not refused["ok"], refused
obs("stop", refused["error"][:220])

# ---- class 6: the approval in place, the bindings, the guard
by_file = {json.loads(r["custom_attributes"])["converted_from"]: r for r in rows}


def full(r, **changes):
    d = {c: r.get(c) for c in srv._PROMPT_COLUMNS}
    d.update({"type": "prompt", **changes})
    return d


ap = srv.entity_upsert([full(by_file["prompts/prm-next.md"], lifecycle_status="Approved")])
assert ap["ok"], ap
obs("approve.kickoff", ap["items"][0]["changed_columns"])
bad = srv.entity_upsert([full(by_file["prompts/project-design-review.md"], plugin_skill="design-review")])
obs("bind.refused", {"ok": bad["ok"], "error": str(bad.get("error") or bad.get("items"))[:200]})
bound = srv.entity_upsert([
    full(by_file["prompts/project-invariant-audit.md"], plugin_skill="integrity-check", lifecycle_status="Approved"),
    full(by_file["prompts/project-deferred-work-cautions.md"], plugin_skill="replan-deferred", lifecycle_status="Approved"),
])
assert bound["ok"], bound
obs("bind.ok", [(i["id"], [c["column"] for c in i["changed_columns"]]) for i in bound["items"]])
obs("query.by_skill", [r["id"] for r in srv.entity_query("prompt", status="Approved", plugin_skill="integrity-check")["rows"]])

# ---- class 7: the emit with refresh_stock
em = srv.handoff_emit(str(copy), refresh_stock=True)
assert em["ok"], em
note_v7 = (pkg / "CLAUDE.md").read_text(encoding="utf-8")
roster = [ln for ln in note_v7.splitlines() if ln.startswith("- **PRT-")]
obs("emit", {"library": {k: v for k, v in em["prompt_library"].items() if v},
             "stale_references": em.get("stale_references"),
             "converted_hints": len(em.get("converted_prompts") or []),
             "note_marker": re.search(r"tamheed:note v\d", note_v7).group(0),
             "roster_lines": [ln[:90] for ln in roster],
             "note_lines_before_after": (note_v5.count("\n"), note_v7.count("\n")),
             "numstat": git(copy, "diff", "--numstat", "--", f"{PKG}/CLAUDE.md").split()[:2]})
commit(copy, "emit")
obs("ste-clean.after", ste_clean(pkg))

# ---- class 8: the export, the Prompts section
assert srv.export_html()["ok"]
text = (pkg / "review.html").read_text(encoding="utf-8")
assert f'<meta name="tamheed-version" content="{RELEASE}">' in text[:4096]
sec = text.split('<section id="prompts">')[1].split("</section>")[0]
v1 = srv.package_verify()
obs("export", {"numstat": git(copy, "diff", "--numstat", "--", f"{PKG}/review.html").split()[:2],
               "prompts_section": {"queue": "Awaiting the operator" in sec, "approved": "Approved (the execution half" in sec,
                                   "entry_marked": "<td>yes</td>" in sec},
               "csv_prompts": (pkg / "csv" / "prompts.csv").exists(),
               "review_current": v1["review_current"], "exported_by": v1["review_exported_by"]})
commit(copy, "export")

# ---- class 9: readiness over rows
rc = srv.readiness_check("package")
rules = rc["rules"]
pr = next(x for x in rules if x["rule"] == "prose-plain-english")
pid = next(x for x in rules if x["rule"] == "prompt-ids-resolve")
obs("readiness.after", {"ready": rc["ready"], "advisories": sum(1 for x in rules if x["severity"] == "advisory"),
                        "blocking_failing": [x["rule"] for x in rules if x["severity"] == "blocking" and x["status"] == "fail"],
                        "prompt_ids_resolve": {"status": pid["status"], "population": pid["population"], "entities": pid["entities"][:6]},
                        "prose_plain_english": {"status": pr["status"], "counts": pr["counts"], "texts": pr["population"]["rows"],
                                                "prompt_rows_named": sorted({e.split(".")[0] for e in pr["entities"] if e.startswith("PRT-")})}})
srv.package_close()
obs("lock_gone", not (pkg / "data" / ".lock").exists())

# ---- class 10: the hook over the v7 note (this copy) and the untouched v5 note (a second copy)
log = copy / "hook-trace.log"; log.write_text("", encoding="utf-8")
rr = run_hook({"source": "startup", "session_id": SID}, copy, log)
lines = rr.stdout.rstrip("\n").splitlines(); tl = log.read_text(encoding="utf-8").splitlines()
obs("hook.v7_note", {"exit": rr.returncode, "lines": len(lines), "chars": len("\n".join(lines)),
                     "trace_opens": " ".join(tl[0].split(" ")[1:3]) if tl else None})
assert tl and tl[0].split(" ")[1] == f"version={RELEASE}" and lines
second = archive("acmp-replay11-second")
log2 = second / "hook-trace.log"; log2.write_text("", encoding="utf-8")
rr2 = run_hook({"source": "startup", "session_id": SID}, second, log2)
lines2 = rr2.stdout.rstrip("\n").splitlines(); tl2 = log2.read_text(encoding="utf-8").splitlines()
obs("hook.v5_note_untouched", {"exit": rr2.returncode, "lines": len(lines2), "chars": len("\n".join(lines2)),
                               "trace_opens": " ".join(tl2[0].split(" ")[1:3]) if tl2 else None})
assert tl2 and tl2[0].split(" ")[1] == f"version={RELEASE}" and lines2

# ---- class 11: the wire
wire = subprocess.run([sys.executable, str(OLD_SCRIPTS / "wire_list.py"), str(BUNDLE), str(SCR / "wire11-empty")],
                      capture_output=True, text=True, env=ENV)
assert wire.returncode == 0, wire.stderr[-600:]
listed = json.loads(wire.stdout)
assert listed["handoff_emit"] == srv.TOOLS["handoff_emit"][1]
obs("wire", {"handoff_emit_len": len(listed["handoff_emit"]), "handoff_emit_opens": listed["handoff_emit"][:60],
             "descriptions": len(listed)})
print("DONE")
