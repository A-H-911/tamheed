"""Replay the 5.8.0 engine over read-only COPIES of the field package, taken by `git archive`
at the field's pushed head (plan 169): the classes of the brief, the brief's two feedback moves
rehearsed, the first plain emit, the two exports measured in git, the hook over an untouched
copy, and the wire. Prints ids, counts and classes; never a line of the field's text.

Run:  env -u TAMHEED_HOOK_LOG PYTHONIOENCODING=utf-8 python acmp_replay8.py <field repo> <scratch dir> <5.7.0 bundle dir>
      Fresh folders are created under <scratch dir>; nothing is removed.
"""
import json
import os
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

FIELD, SCR, OLD_BUNDLE = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
HOOK = BUNDLE / "server" / "resume_hook.py"
SID = "64b2af54-e22c-4e2e-9d13-8c7792eb2b78"
RELEASE, PREVIOUS = "5.8.0", "5.7.0"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def obs(k, v):
    print("OBS", k, json.dumps(v, ensure_ascii=False, default=str)[:1100])


def archive(name):
    dest = SCR / name
    dest.mkdir()                                   # refuses an existing folder
    tar = SCR / f"{name}.tar"
    with tar.open("wb") as fh:
        subprocess.run(["git", "-C", str(FIELD), "archive", "HEAD", "tamheed-package"],
                       check=True, stdout=fh)
    subprocess.run(["tar", "-x", "-C", str(dest), "-f", str(tar)], check=True)
    return dest


def git(where, *a):
    return subprocess.run(["git", "-C", str(where), *a], capture_output=True,
                          check=True).stdout.decode("utf-8", "replace")


def run_hook(event, where, trace):
    env = dict(ENV, CLAUDE_PROJECT_DIR=str(where), TAMHEED_HOOK_LOG=str(trace))
    return subprocess.run(["uv", "run", "--no-project", str(HOOK)], input=json.dumps(event),
                          capture_output=True, text=True, env=env, cwd=str(where), encoding="utf-8")


head = git(FIELD, "rev-parse", "--short=8", "HEAD").strip()
obs("field.head", head)
copy = archive("acmp-replay8")
pkg = copy / "tamheed-package"
git(copy, "init", "-q"); git(copy, "add", "-A")
git(copy, "-c", "user.email=x@y", "-c", "user.name=x", "commit", "-q", "-m", "field head")

# ---- the 5.7.0 render of the copy's store, before anything is opened (its own process)
old_render = SCR / "replay8-renders" / "by-5.7.0.html"
old_render.parent.mkdir()
r = subprocess.run([sys.executable, str(HERE / "render_with.py"), str(OLD_BUNDLE), str(copy),
                    "tamheed-package", str(old_render)], capture_output=True, text=True, env=ENV)
assert r.returncode == 0, r.stderr[-600:]

# ---- classes 1 and 2
srv.PACKAGE_ROOT = copy
info = srv.server_info()
obs("server_info", {k: info[k] for k in ("version", "migrations_head", "schema_version")})
assert info["version"] == RELEASE and info["schema_version"] == 7
v0 = srv.package_verify("tamheed-package")
obs("verify.before", {k: v0.get(k) for k in ("verified", "review_current", "review_exported_by")})
assert v0["verified"] and v0["review_current"] and v0["review_exported_by"] == PREVIOUS
o = srv.package_open("tamheed-package")
assert o["ok"], o
obs("open.resume", {"handoff": o["resume"]["handoff"]["id"], "behind": o["resume"]["handoff_behind"]})

# ---- class 3: the rule on the field's own journal
rules = srv.readiness_check("package")["rules"]
hr = next(x for x in rules if x["rule"] == "handoff-repeated")
obs("handoff-repeated", {"status": hr["status"], "entities": hr["entities"],
                         "population": hr["population"]["rows"]})
obs("advisories", len([x for x in rules if x["severity"] == "advisory"]))

# ---- class 4: the first export, in git
x = srv.export_html()
assert x["ok"], x
git(copy, "add", "-A"); git(copy, "-c", "user.email=x@y", "-c", "user.name=x", "commit", "-q", "-m", "first")
page = pkg / "review.html"
text = page.read_text(encoding="utf-8")
assert f'<meta name="tamheed-version" content="{RELEASE}">' in text[:4096]
assert text.count('<tr id="') == text.count('\n<tr id="')
assert all(ln.count("</tr>") <= 1 and ln.count("<path ") <= 1 for ln in text.split("\n"))
v1 = srv.package_verify()
obs("export.first", {"numstat": git(copy, "diff", "--numstat", "HEAD~1", "HEAD", "--", "tamheed-package/review.html").split()[:2],
                     "patch_bytes": len(git(copy, "diff", "HEAD~1", "HEAD", "--", "tamheed-package/review.html").encode()),
                     "csv_changed": git(copy, "diff", "--stat", "HEAD~1", "HEAD", "--", "tamheed-package/csv").strip() or "none",
                     "review_current": v1["review_current"], "exported_by": v1["review_exported_by"],
                     "lines": text.count("\n")})
# the byte check against the 5.7.0 render of the same store, same date
new_render = SCR / "replay8-renders" / "by-5.8.0.html"
new_render.write_bytes(page.read_bytes())
r = subprocess.run([sys.executable, str(HERE / "bytecheck.py"), str(old_render), str(new_render)],
                   capture_output=True, text=True, env=ENV)
assert r.returncode == 0 and "EQUAL" in r.stdout, r.stdout + r.stderr
obs("export.bytecheck", r.stdout.strip().splitlines())

# ---- the brief's two feedback moves, rehearsed with the exact rows the brief prints
rows = {r["id"]: r for r in srv.entity_query("feedback", ids=["FB-026", "FB-027"])["rows"]}
before_j = srv.entity_query("progress-entry", columns=["id"], limit=1)["total"]
moves = []
for fid in ("FB-026", "FB-027"):
    base = {"type": "feedback", "id": fid, "kind": rows[fid]["kind"], "title": rows[fid]["title"]}
    a = srv.entity_upsert([{**base, "lifecycle_status": "Reported"}])
    b = srv.entity_upsert([{**base, "lifecycle_status": "Resolved", "resolved_in": RELEASE,
                            "upstream_ref": "tamheed plans 165-169"}])
    moves.append((fid, a["ok"], b["ok"], a["items"][0].get("error"), b["items"][0].get("error")))
after_j = srv.entity_query("progress-entry", columns=["id"], limit=1)["total"]
now = {r["id"]: (r["lifecycle_status"], r["resolved_in"], r["upstream_ref"])
       for r in srv.entity_query("feedback", ids=["FB-026", "FB-027"])["rows"]}
fu = next(x for x in srv.readiness_check("package")["rules"] if x["rule"] == "feedback-unanswered")
hc = next(x for x in srv.readiness_check("package")["rules"] if x["rule"] == "handoff-current")
obs("feedback.moves", {"results": moves, "rows_now": now, "transitions_journalled": after_j - before_j,
                       "feedback-unanswered_names": fu["entities"],
                       "handoff-current_counts": hc["entities"]})
assert all(m[1] and m[2] for m in moves), moves
assert after_j - before_j == 4 and not (set(fu["entities"]) & {"FB-026", "FB-027"})
assert all(now[f] == ("Resolved", RELEASE, "tamheed plans 165-169") for f in now)

# ---- class 5: the second export after a journal write (no node, no edge)
w = srv.progress_update([{"entry": "Replay: a note written after the first 5.8.0 export.",
                          "actor": "agent:replay"}])
assert w["ok"], w
assert srv.export_html()["ok"]
git(copy, "add", "-A"); git(copy, "-c", "user.email=x@y", "-c", "user.name=x", "commit", "-q", "-m", "second")
p2 = git(copy, "diff", "HEAD~1", "HEAD", "--", "tamheed-package/review.html")
added = [ln for ln in p2.split("\n") if ln.startswith("+") and not ln.startswith("+++")]
obs("export.second", {"numstat": git(copy, "diff", "--numstat", "HEAD~1", "HEAD", "--", "tamheed-package/review.html").split()[:2],
                      "patch_bytes": len(p2.encode()), "added_lines": len(added),
                      "added_bytes": sum(len(ln.encode()) for ln in added),
                      "longest_added_line": max(len(ln) for ln in added)})

# ---- the first plain emit: what it writes
(copy / "CLAUDE.md").write_text((FIELD / "CLAUDE.md").read_text(encoding="utf-8"),
                                encoding="utf-8", newline="\n")
git(copy, "add", "-A"); git(copy, "-c", "user.email=x@y", "-c", "user.name=x", "commit", "-q", "-m", "note")
em = srv.handoff_emit(str(copy))
assert em["ok"], em
changed = git(copy, "status", "--porcelain", "-uall").splitlines()
obs("emit.first_plain", {"written": em.get("written"), "unchanged": em.get("unchanged"),
                         "files_changed_in_the_copy": changed[:8],
                         "note_names_the_rule": "handoff-repeated" in (copy / "CLAUDE.md").read_text(encoding="utf-8")})
srv.package_close()

# ---- the hook over an untouched second copy, after a compaction
second = archive("acmp-replay8-second")
(second / "CLAUDE.md").write_text((FIELD / "CLAUDE.md").read_text(encoding="utf-8"),
                                  encoding="utf-8", newline="\n")
log = second / "hook-trace.log"
log.write_text("", encoding="utf-8")
rr = run_hook({"source": "compact", "session_id": SID}, second, log)
lines = rr.stdout.rstrip("\n").splitlines()
tl = log.read_text(encoding="utf-8").splitlines()
obs("hook.compact", {"exit": rr.returncode, "lines": len(lines), "chars": len("\n".join(lines)),
                     "trace_opens": " ".join(tl[0].split(" ")[1:3]) if tl else None,
                     "trace_tail_is_session": bool(tl) and tl[0].endswith(f" session={SID}")})

# ---- the wire: tools/list from the installed-shaped bundle, in its own process
wire = subprocess.run([sys.executable, str(HERE / "wire_list.py"), str(BUNDLE), str(SCR / "wire8-empty")],
                      capture_output=True, text=True, env=ENV)
assert wire.returncode == 0, wire.stderr[-600:]
listed = json.loads(wire.stdout)
for n in ("entity_query", "progress_update", "audit_record"):
    assert listed[n] == srv.TOOLS[n][1], n
obs("wire", {n: len(listed[n]) for n in listed})
print("DONE")
