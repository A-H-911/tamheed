"""Plan 238: measure the 6.6.0 upgrade route (fidelity: the field .gitignore, autocrlf off) on a scratch export of a field package's COMMITTED
tree (`git archive`, read-only on the field repository). Prints ids, file names and counts only,
never the text of a row.

    env -u TAMHEED_HOOK_LOG python measure_briefs_660.py <field repo> <package dir> <scratch>
"""
import json
import os
import subprocess
import sys
import tarfile
import io
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
field, pkg, scratch = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]).resolve()
ws = scratch / f"{field.name}-238"
assert not ws.exists(), "a fresh scratch folder each run"
ws.mkdir(parents=True)
head = subprocess.run(["git", "-C", str(field), "log", "-1", "--format=%h"], capture_output=True,
                      text=True).stdout.strip()
if (field / ".git").exists():
    blob = subprocess.run(["git", "-C", str(field), "archive", "HEAD", pkg, "CLAUDE.md", ".gitignore", ".claude/settings.json"],
                          capture_output=True).stdout
    tarfile.open(fileobj=io.BytesIO(blob)).extractall(ws)
else:                       # an exported folder (Jisr's of 2026-11-12): a plain copy
    import shutil
    shutil.copytree(field / pkg, ws / pkg, ignore=shutil.ignore_patterns(".lock"))
    head = "export folder"


def git(*args):
    return subprocess.run(["git", *args], cwd=ws, capture_output=True, text=True).stdout


def moved():
    out = sorted(x[3:] for x in git("status", "--porcelain").splitlines())
    git("add", "-A")
    git("-c", "user.name=m", "-c", "user.email=m@example.invalid", "commit", "-qm", "step")
    return out


def state():
    g = srv.gate_run()
    r = srv.readiness_check("package")
    return {"ready_gates": g.get("ready"), "ready": r.get("ready"),
            "blocking_fail": sorted(x["rule"] for x in r["rules"]
                                    if x["severity"] == "blocking" and x["status"] == "fail")}


def obs(k, v):
    print(f"OBS {k}: {json.dumps(v, ensure_ascii=False, default=str)[:700]}")


git("init", "-q"); git("config", "core.autocrlf", "false")
moved()
srv.PACKAGE_ROOT = ws
obs("field.head", head)
import resume_hook  # noqa: E402  the session-start lines a 6.6.0 client prints before the sync
hook_lines = resume_hook.build_lines(ws, source="startup")
obs("hook.before", {"lines": len(hook_lines), "behind": [x[:120] for x in hook_lines if "BEHIND" in x],
                    "standup": [x[:80] for x in hook_lines if "standup" in x.lower()]})
first = srv.package_open(pkg)
obs("open.before", {"ok": first["ok"], "error": (first.get("error") or "")[:240]})
if first["ok"]:
    obs("state.before", state())
    pre_sync = srv.standup_report(utc_offset="+03:00")       # before the sync: refused, nothing written
    obs("standup.before_sync", {"ok": pre_sync["ok"], "error": (pre_sync.get("error") or "")[:160]})
    srv.package_close()
pre = srv.package_migrate(pkg)
rep = pre.get("report", {})
obs("preview", {"ok": pre["ok"], "mode": rep.get("mode"), "added": rep.get("entity_types_added"),
                "columns_added": rep.get("columns_added"), "error": (pre.get("error") or "")[:200]})
conf = srv.package_migrate(pkg, confirm=True)
obs("confirm", {"ok": conf["ok"], "backup": conf.get("backup"), "moved": moved()})
o = srv.package_open(pkg)
obs("open.after", {"ok": o["ok"], "error": (o.get("error") or "")[:200]})
obs("state.after", state())
em = srv.handoff_emit(str(ws), refresh_stock=True)
obs("emit", {"ok": em["ok"], "library": {k: v for k, v in (em.get("prompt_library") or {}).items()
                                         if k in ("refreshed", "written", "unchanged")},
             "warnings": [w[:120] for w in em.get("warnings", [])], "error": em.get("error")})
srv.package_close()
obs("emit.moved", moved())
srv.package_open(pkg)
f = srv.standup_report(utc_offset="+03:00")
obs("standup.facts", {"ok": f["ok"], "report": f.get("report"), "first": f.get("first"),
                      "rule": f.get("rule_colour"), "reasons": f.get("rule_reasons"),
                      "result_kb": round(len(json.dumps(f)) / 1024, 1), "error": f.get("error")})
words = {"headline": "This first report covers the package from its start.",
         "did": "The lists below show the work recorded so far.",
         "challenges": "The open items are listed below.", "next": "The next report covers one day.",
         "colour": f.get("rule_colour", "green"),
         "colour_reason": "The default rule gives this colour."}
a = srv.standup_report(narrative=words)
obs("standup.narrative", {"ok": a["ok"], "words": a.get("visible_words"), "error": a.get("error")})
rec = srv.standup_report(action="record", confirm={"operator_confirm": True, "by": "human:m",
                                                   "words": "record it", "colour": words["colour"]})
obs("standup.record", {"ok": rec["ok"], "live_match": rec.get("live_match"), "error": rec.get("error")})
ex = srv.export_html()
obs("export", ex.get("ok"))
v = srv.package_verify()
obs("verify", {k: v.get(k) for k in ("verified", "dirty", "foreign", "review_current",
                                     "review_exported_by")})
srv.package_close()
page = ws / pkg / "reports" / "RPT-001.html"
row = ws / pkg / "data" / "standup_reports.jsonl"
obs("sizes_kb", {"page": round(page.stat().st_size / 1024, 1),
                 "row": round(row.stat().st_size / 1024, 1)})
obs("standup.moved", moved())
print("WS", ws)
