"""Replay the 5.5.0 engine over a read-only COPY of the field package and its control files,
taken by `git archive` at the field's pushed head (plan 150): every 5.4 class again, the new
classes of 5.5.0, EVERY recipe the brief prescribes, and the sweep of four families for the
sentences 5.5.0 falsifies."""
import difflib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(r"C:\Users\ahammo\Repos\tamheed")
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "server"))
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

COPY = Path(sys.argv[1])
PKG = COPY / "tamheed-package"
HOOK = REPO / "plugins" / "tamheed" / "server" / "resume_hook.py"
SID = "d37475be-d853-424d-a4bc-996b1e7f5e42"


def obs(k, v):
    print("OBS", k, json.dumps(v, ensure_ascii=False, default=str)[:1100])


def run_hook(event, trace=None):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(COPY))
    env.pop("TAMHEED_HOOK_LOG", None)
    if trace is not None:
        env["TAMHEED_HOOK_LOG"] = str(trace)
    return subprocess.run(["uv", "run", "--no-project", str(HOOK)], input=json.dumps(event),
                          capture_output=True, text=True, env=env, cwd=str(COPY), encoding="utf-8")


def changed_lines(before: str, after: str) -> list[str]:
    return [ln for ln in difflib.unified_diff(before.splitlines(), after.splitlines(), lineterm="",
                                              n=0)
            if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]


def note_ids(text: str) -> list[str]:
    return sorted(re.findall(r"^- \*\*(LL-\d+)\*\*", text, re.M))


# ------------------------------------------------------------ the sweep, before any write
SWEEP = re.compile(
    r"no longer binds?|stops? binding|stopped binding|roster of what binds|binds nothing"
    r"|what binds|every session in every|every Claude Code session|no SessionStart hook at all"
    r"|ran no SessionStart|sdk-py", re.I)
hits = []
for f in sorted((COPY / ".claude" / "memory").glob("*.md")) + [COPY / "CLAUDE.md", PKG / "CLAUDE.md"]:
    for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        for m in SWEEP.finditer(line):
            hits.append((f.relative_to(COPY).as_posix() + f":{n}", m.group(0),
                         line.strip()[max(0, m.start() - 70):m.end() + 70]))
for fam in ("decisions", "lessons", "progress_entries"):
    rows = [json.loads(x) for x in (PKG / "data" / f"{fam}.jsonl").read_text(
        encoding="utf-8").splitlines() if x.strip()]
    for r in rows:
        if fam == "progress_entries" and int(r["id"].split("-")[1]) < 1500:
            continue
        if fam == "decisions" and int(r["id"].split("-")[1]) < 230:
            continue
        if fam == "lessons" and r["lifecycle_status"] not in ("Approved", "Proposed"):
            continue
        for col, val in r.items():
            if not isinstance(val, str):
                continue
            for m in SWEEP.finditer(val):
                hits.append((f"{r['id']}.{col}", m.group(0),
                             " ".join(val[max(0, m.start() - 90):m.end() + 90].split())))
print("SWEEP hits:", len(hits))
for where, what, ctx in hits:
    print("  HIT", where, "|", what, "|", ctx[:230])

# ------------------------------------------------------------ the classes
srv.PACKAGE_ROOT = COPY
info0 = srv.server_info()
obs("server_info.closed", {k: info0.get(k) for k in ("version", "migrations_head", "schema_version")})
o = srv.package_open("tamheed-package")
assert o["ok"], o
res = o["resume"]
HO = res["handoff"]["id"]
obs("open.resume", {"handoff": HO, "truncated": res["handoff"].get("truncated"),
                    "corrections": [c["id"] for c in (res["handoff"].get("corrections") or [])],
                    "behind": res["handoff_behind"], "skill": res["skill"],
                    "open_feedback": res["open_feedback"]})
obs("open.lock", {k: res["lock"].get(k) for k in ("observed", "evidence")})
v0 = srv.package_verify()
D0 = v0["digest"]
obs("verify.before_any_write", {k: v0.get(k) for k in ("verified", "dirty", "foreign",
                                                       "review_current", "digest")})
root_b = (COPY / "CLAUDE.md").read_text(encoding="utf-8")
pkg_b = (PKG / "CLAUDE.md").read_text(encoding="utf-8")
guide_b = (PKG / "prompts" / "README.md").read_text(encoding="utf-8")
page_b = (PKG / "review.html").read_bytes()
e = srv.handoff_emit(str(COPY))
assert e["ok"], e
obs("emit", {k: e.get(k) for k in ("written", "unchanged", "stale_references", "restated_content",
                                  "oversized_prompts", "stock_merged", "skill")})
obs("emit.library", {k: v for k, v in e["prompt_library"].items() if v})
obs("emit.warnings", [str(w)[:200] for w in e.get("warnings", [])])
root_a = (COPY / "CLAUDE.md").read_text(encoding="utf-8")
pkg_a = (PKG / "CLAUDE.md").read_text(encoding="utf-8")
obs("root.changed_lines", changed_lines(root_b, root_a))
obs("pkg_note.changed_lines", changed_lines(pkg_b, pkg_a))
obs("pkg_note.roster", {"before": note_ids(pkg_b), "after": note_ids(pkg_a)})
e1 = srv.handoff_emit(str(COPY))
obs("emit.second", {"written": e1["written"], "unchanged": e1["unchanged"]})
e2 = srv.handoff_emit(str(COPY), refresh_stock=True)
obs("emit.refresh", {"refreshed": e2["prompt_library"].get("refreshed"), "written": e2["written"]})
guide_a = (PKG / "prompts" / "README.md").read_text(encoding="utf-8")
obs("guide.changed_lines", changed_lines(guide_b, guide_a))
r = srv.readiness_check("package")
for name in ("handoff-current", "lessons-stranded", "lessons-confirmed", "feedback-unanswered",
             "lessons-note-budget"):
    x = next((x for x in r["rules"] if x["rule"] == name), None)
    if x:
        obs("rule." + name, {"status": x["status"], "n": len(x.get("entities") or []),
                             "note": (x.get("note") or "")[:200]})
obs("readiness", {"ready": r.get("ready"), "skill": r.get("skill"),
                  "blocking": sorted(x["rule"] for x in r["rules"]
                                     if x["status"] == "fail" and x.get("severity") == "blocking")})
q = srv.entity_query("lesson", status="Proposed")
obs("entity_query.proposed", {"count": q.get("count"), "skill": q.get("skill")})
qa = srv.entity_query("lesson", status="Approved", columns=["id", "pinned"], limit=100)
obs("entity_query.approved", {"total": qa.get("total"),
                              "pinned": sum(1 for x in qa["rows"] if x["pinned"])})
bad = srv.entity_query("no-such-type")
obs("entity_query.error", {"ok": bad.get("ok"), "skill_present": "skill" in bad})
v1 = srv.package_verify()
obs("verify.after_emits_before_export", {k: v1.get(k) for k in ("verified", "dirty",
                                                                "review_current")}
    | {"digest_equals_D0": v1["digest"] == D0})
ex = srv.export_html()
assert ex["ok"], ex
obs("export_html", {k: ex.get(k) for k in ("written", "unchanged", "path") if k in ex}
    | {"keys": sorted(ex.keys())})
page_a = (PKG / "review.html").read_bytes()
obs("review.changed", {"bytes_before": len(page_b), "bytes_after": len(page_a),
                       "differs": page_a != page_b})
page = page_a.decode("utf-8")
fold = page.split('id="lessons-approved"', 1)[1].split("</details>", 1)[0]
cells = dict(re.findall(r'<tr id="(LL-\d+)"><td>LL-\d+</td><td>[^<]*</td><td>[^<]*</td>'
                        r'<td>([^<]*)</td>', fold))
marked = sorted(i for i, c in cells.items() if c == "rendered")
obs("review.roster", {"rows": len(cells), "marked": marked, "equals_note": marked == note_ids(pkg_a)})
old_page = page_b.decode("utf-8", errors="replace")
obs("review.old_page_had_column", "note (rendered at the next emit)" in old_page)
v2 = srv.package_verify()
obs("verify.after_export", {k: v2.get(k) for k in ("verified", "dirty", "review_current")}
    | {"digest_equals_D0": v2["digest"] == D0})

# ------------------------------------------------------------ the brief's recipe, on the copy
ho_row = srv.entity_query("progress-entry", id=HO)["rows"][0]
sentence = re.search(r"[^.;]*no longer binds[^.;]*", ho_row["entry"])
obs("handoff.sentence", sentence.group(0).strip() if sentence else None)
c = srv.progress_update([{"entry": f"Corrects {HO}'s RULINGS GIVEN line, in tamheed 5.5.0's two"
                                   " words: the lesson pushed out of the note's roster is no longer"
                                   " RENDERED there; it stays Approved, so it still BINDS, and is"
                                   " read by query. The rest of the entry stands.",
                          "event_type": "correction", "corrects": HO, "actor": "agent:replay"}])
obs("recipe.correction_on_the_handoff", {"ok": c.get("ok"), "ids": c.get("ids")})
r2 = srv.readiness_check("package")
hc = next(x for x in r2["rules"] if x["rule"] == "handoff-current")
obs("rule.handoff-current.after_recipe", {"status": hc["status"], "entities": hc.get("entities")})
info = srv.server_info()
obs("server_info.open", {"version": info["version"], "handoff": info["resume"]["handoff"]["id"],
                         "corrections": [x["id"] for x in info["resume"]["handoff"].get("corrections") or []],
                         "behind": info["resume"]["handoff_behind"]})
srv.package_close()

# ------------------------------------------------------------ the hook over the copy
log = COPY / "hook-trace.log"
log.write_text("", encoding="utf-8")
rr = run_hook({"source": "compact", "session_id": SID}, log)
lines = rr.stdout.rstrip("\n").splitlines()
tl = log.read_text(encoding="utf-8").splitlines()
obs("hook.compact", {"exit": rr.returncode, "lines": len(lines), "chars": len("\n".join(lines)),
                     "first": lines[0][:120] if lines else None,
                     "corrections_line": next((ln for ln in lines if ln.startswith("Corrections")), None)})
obs("hook.trace", {"line": tl[0] if tl else None, "n": len(tl),
                   "counts_match": bool(tl) and f"lines={len(lines)} chars={len(chr(10).join(lines))}" in tl[0],
                   "tail_is_session": bool(tl) and tl[0].endswith(f" session={SID}")})
print("DONE")
