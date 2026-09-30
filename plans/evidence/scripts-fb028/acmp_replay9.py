"""Replay the 5.8.1 bundle over read-only COPIES of the field package, taken by `git archive`
at the field's pushed head (plan 174): the classes of the 5.8.1 brief, FB-028's remaining
moves rehearsed by reading the row back FIRST (the field's PE-1584 says it sets Reported once the
row has left), the export after them, the first plain emit, the hook over an untouched copy
after a compaction, and the wire. Prints ids, counts and classes; never a line of the field's
text.

Run:  env -u TAMHEED_HOOK_LOG PYTHONIOENCODING=utf-8 python acmp_replay9.py <field repo> <scratch dir>
      Fresh folders are created under <scratch dir>; nothing is removed.
"""
import json
import os
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
RELEASE, PREVIOUS = "5.8.1", "5.8.0"
UPSTREAM = "tamheed plans 170-174"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def obs(k, v):
    print("OBS", k, json.dumps(v, ensure_ascii=False, default=str)[:1100])


def archive(name):
    dest = SCR / name
    dest.mkdir()
    tar = SCR / f"{name}.tar"
    with tar.open("wb") as fh:
        subprocess.run(["git", "-C", str(FIELD), "archive", "HEAD", "tamheed-package"], check=True, stdout=fh)
    subprocess.run(["tar", "-x", "-C", str(dest), "-f", str(tar)], check=True)
    return dest


def git(where, *a):
    return subprocess.run(["git", "-C", str(where), *a], capture_output=True, check=True).stdout.decode("utf-8", "replace")


def commit(where, msg):
    git(where, "add", "-A"); git(where, "-c", "user.email=x@y", "-c", "user.name=x", "commit", "-q", "-m", msg)


def run_hook(event, where, trace):
    env = dict(ENV, CLAUDE_PROJECT_DIR=str(where), TAMHEED_HOOK_LOG=str(trace))
    return subprocess.run(["uv", "run", "--no-project", str(HOOK)], input=json.dumps(event),
                          capture_output=True, text=True, env=env, cwd=str(where), encoding="utf-8")


head = git(FIELD, "rev-parse", "--short=8", "HEAD").strip()
obs("field.head", head)
copy = archive("acmp-replay9")
pkg = copy / "tamheed-package"
git(copy, "init", "-q"); commit(copy, "field head")

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

# ---- class 3: readiness on the field's journal (the rule passes on PE-1584)
rules = srv.readiness_check("package")["rules"]
hr = next(x for x in rules if x["rule"] == "handoff-repeated")
fu = next(x for x in rules if x["rule"] == "feedback-unanswered")
obs("handoff-repeated", {"status": hr["status"], "entities": hr["entities"], "population": hr["population"]["rows"]})
obs("feedback-unanswered.before", fu["entities"])
assert hr["status"] == "pass"

# ---- FB-028's moves: READ THE ROW BACK FIRST, then only the remaining transitions
row = srv.entity_query("feedback", ids=["FB-028"])["rows"][0]
obs("fb028.read_back", {"lifecycle_status": row["lifecycle_status"], "kind": row["kind"],
                        "resolved_in": row["resolved_in"], "upstream_ref": row["upstream_ref"]})
base = {"type": "feedback", "id": "FB-028", "kind": row["kind"], "title": row["title"]}
before_j = srv.entity_query("progress-entry", columns=["id"], limit=1)["total"]
moves = []
if row["lifecycle_status"] == "Confirmed":
    a = srv.entity_upsert([{**base, "lifecycle_status": "Reported"}])
    moves.append(("Reported", a["ok"], a["items"][0].get("error")))
if row["lifecycle_status"] in ("Confirmed", "Reported"):
    b = srv.entity_upsert([{**base, "lifecycle_status": "Resolved", "resolved_in": RELEASE, "upstream_ref": UPSTREAM}])
    moves.append(("Resolved", b["ok"], b["items"][0].get("error")))
after_j = srv.entity_query("progress-entry", columns=["id"], limit=1)["total"]
now = srv.entity_query("feedback", ids=["FB-028"])["rows"][0]
rules = srv.readiness_check("package")["rules"]
fu = next(x for x in rules if x["rule"] == "feedback-unanswered")
hc = next(x for x in rules if x["rule"] == "handoff-current")
obs("fb028.moves", {"moves": moves, "transitions_journalled": after_j - before_j,
                    "row_now": (now["lifecycle_status"], now["resolved_in"], now["upstream_ref"]),
                    "feedback-unanswered_names": fu["entities"], "handoff-current_counts": hc["entities"]})
assert all(m[1] for m in moves), moves
assert now["lifecycle_status"] == "Resolved" and now["resolved_in"] == RELEASE and now["upstream_ref"] == UPSTREAM
assert "FB-028" not in fu["entities"]

# ---- class 4: the export after the moves, in git (small: no node, no edge)
assert srv.export_html()["ok"]
commit(copy, "export after the moves")
text = (pkg / "review.html").read_text(encoding="utf-8")
assert f'<meta name="tamheed-version" content="{RELEASE}">' in text[:4096]
p = git(copy, "diff", "HEAD~1", "HEAD", "--", "tamheed-package/review.html")
added = [ln for ln in p.split("\n") if ln.startswith("+") and not ln.startswith("+++")]
v1 = srv.package_verify()
obs("export.after_moves", {"numstat": git(copy, "diff", "--numstat", "HEAD~1", "HEAD", "--", "tamheed-package/review.html").split()[:2],
                           "patch_bytes": len(p.encode()), "longest_added_line": max(len(ln) for ln in added),
                           "csv_changed": git(copy, "diff", "--stat", "HEAD~1", "HEAD", "--", "tamheed-package/csv").strip().splitlines()[-1:] or "none",
                           "review_current": v1["review_current"], "exported_by": v1["review_exported_by"]})

# ---- the first plain emit: what it writes
(copy / "CLAUDE.md").write_text((FIELD / "CLAUDE.md").read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
commit(copy, "note")
em = srv.handoff_emit(str(copy))
assert em["ok"], em
changed = git(copy, "status", "--porcelain", "-uall").splitlines()
obs("emit.first_plain", {"written": em.get("written"), "unchanged": em.get("unchanged"),
                         "files_changed_in_the_copy": changed[:8]})
srv.package_close()
obs("lock_gone", not (pkg / "data" / ".lock").exists())

# ---- the hook over an untouched second copy, after a compaction
second = archive("acmp-replay9-second")
(second / "CLAUDE.md").write_text((FIELD / "CLAUDE.md").read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
log = second / "hook-trace.log"
log.write_text("", encoding="utf-8")
rr = run_hook({"source": "compact", "session_id": SID}, second, log)
lines = rr.stdout.rstrip("\n").splitlines()
tl = log.read_text(encoding="utf-8").splitlines()
obs("hook.compact", {"exit": rr.returncode, "lines": len(lines), "chars": len("\n".join(lines)),
                     "trace_opens": " ".join(tl[0].split(" ")[1:3]) if tl else None,
                     "trace_tail_is_session": bool(tl) and tl[0].endswith(f" session={SID}")})
assert tl and tl[0].split(" ")[1] == f"version={RELEASE}"

# ---- the wire: tools/list from the bundle, in its own process
wire = subprocess.run([sys.executable, str(OLD_SCRIPTS / "wire_list.py"), str(BUNDLE), str(SCR / "wire9-empty")],
                      capture_output=True, text=True, env=ENV)
assert wire.returncode == 0, wire.stderr[-600:]
listed = json.loads(wire.stdout)
for n in ("entity_query", "progress_update", "audit_record"):
    assert listed[n] == srv.TOOLS[n][1], n
obs("wire", {n: len(listed[n]) for n in ("entity_query", "progress_update", "audit_record")})
print("DONE")
