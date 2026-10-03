"""Replay the 5.9.0 bundle over read-only COPIES of the field package, taken by `git archive` at
the field's HEAD (plan 190): the classes of the 5.9.0 brief. The readiness rule's counts, the
emit with refresh_stock (the guide to the 5.9.0 body, the note to v6), the export, ste-clean
before and after, the hook over the v5 note (untouched copy) and over the v6 note, and the wire.
Prints ids, counts and classes; never a line of the field's text.

Run:  env -u TAMHEED_HOOK_LOG PYTHONIOENCODING=utf-8 python acmp_replay10.py <field repo> <scratch dir>
      Fresh folders are created under <scratch dir>; nothing is removed.
"""
import collections
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
RELEASE, PREVIOUS = "5.9.0", "5.8.1"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
PKG = "tamheed-package"


def obs(k, v):
    print("OBS", k, json.dumps(v, ensure_ascii=False, default=str)[:1200])


def archive(name):
    dest = SCR / name
    dest.mkdir()
    tar = SCR / f"{name}.tar"
    with tar.open("wb") as fh:
        subprocess.run(["git", "-C", str(FIELD), "archive", "HEAD", PKG], check=True, stdout=fh)
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


def ste_clean(pkg_dir):
    r = subprocess.run([sys.executable, str(REPO / "evals" / "pkg_check.py"), "ste-clean", str(pkg_dir)],
                       capture_output=True, text=True, env=ENV, encoding="utf-8")
    hard = [ln for ln in r.stdout.splitlines() if ln.startswith("  ")]
    return {"exit": r.returncode, "first_line": r.stdout.splitlines()[0][:200], "hard": len(hard)}


head = git(FIELD, "rev-parse", "--short=8", "HEAD").strip()
dirty = [ln[3:] for ln in git(FIELD, "status", "--porcelain").splitlines()]
obs("field.head", {"head": head, "uncommitted_in_the_field_tree": dirty[:6]})
copy = archive("acmp-replay10")
pkg = copy / PKG
(copy / "CLAUDE.md").write_text((FIELD / "CLAUDE.md").read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
git(copy, "init", "-q"); commit(copy, "field head")

# ---- classes 1 and 2
srv.PACKAGE_ROOT = copy
info = srv.server_info()
obs("server_info", {k: info[k] for k in ("version", "migrations_head", "schema_version")})
assert info["version"] == RELEASE and info["schema_version"] == 7
v0 = srv.package_verify(PKG)
obs("verify.before", {k: v0.get(k) for k in ("verified", "review_current", "review_exported_by", "dirty")})
o = srv.package_open(PKG)
assert o["ok"], o
obs("open.resume", {"handoff": o["resume"]["handoff"]["id"], "behind": o["resume"]["handoff_behind"]})

# ---- class 3: readiness, the new rule
rc = srv.readiness_check("package")
rules = rc["rules"]
adv = [x for x in rules if x["severity"] == "advisory"]
pr = next(x for x in rules if x["rule"] == "prose-plain-english")
fam = collections.Counter(re.match(r"([A-Z]+)-", e).group(1) for e in pr["entities"] if re.match(r"([A-Z]+)-", e))
files = sum(1 for e in pr["entities"] if e.startswith("prompts/"))
obs("readiness", {"ready": rc["ready"], "advisories": len(adv), "blocking_failing": [x["rule"] for x in rules if x["severity"] == "blocking" and x["status"] == "fail"]})
obs("prose-plain-english", {"status": pr["status"], "counts": pr["counts"], "texts": pr["population"]["rows"],
                            "entities": len(pr["entities"]), "by_family": dict(fam), "prompt_files_named": files,
                            "note_ends_with_skill": pr["note"].strip()[-60:]})

# ---- class 7a: ste-clean before the emit (the 5.8.1 guide)
obs("ste-clean.before", ste_clean(pkg))

# ---- class 4: the emit with refresh_stock: the guide to the 5.9.0 body, the note to v6
note_before = (pkg / "CLAUDE.md").read_text(encoding="utf-8")
em = srv.handoff_emit(str(copy), refresh_stock=True)
assert em["ok"], em
note_after = (pkg / "CLAUDE.md").read_text(encoding="utf-8")
changed = git(copy, "status", "--porcelain", "-uall").splitlines()
guide = (pkg / "prompts" / "README.md").read_text(encoding="utf-8")
obs("emit.refresh_stock", {"refreshed": em["prompt_library"].get("refreshed"), "retired": em["prompt_library"].get("retired"),
                           "customised": em["prompt_library"].get("customised"), "written": em.get("written"),
                           "files_changed_in_the_copy": changed[:8],
                           "guide_title_has_release": f"tamheed v{RELEASE}" in guide.splitlines()[0],
                           "guide_names_nine": "nine **discipline skills**" in guide})
obs("note", {"marker_before": re.search(r"tamheed:note v\d", note_before).group(0),
             "marker_after": re.search(r"tamheed:note v\d", note_after).group(0),
             "first_sentence_after": next((l for l in note_after.splitlines() if "Tamheed package for this project" in l), "")[:60],
             "names_plain_english": "tamheed:plain-english" in note_after,
             "lines_before_after": (note_before.count("\n"), note_after.count("\n")),
             "numstat": git(copy, "diff", "--numstat", "--", f"{PKG}/CLAUDE.md").split()[:2]})
commit(copy, "emit with refresh_stock")
obs("ste-clean.after", ste_clean(pkg))

# ---- class 5: the export
assert srv.export_html()["ok"]
commit(copy, "export")
text = (pkg / "review.html").read_text(encoding="utf-8")
assert f'<meta name="tamheed-version" content="{RELEASE}">' in text[:4096]
p = git(copy, "diff", "HEAD~1", "HEAD", "--", f"{PKG}/review.html")
added = [ln for ln in p.split("\n") if ln.startswith("+") and not ln.startswith("+++")]
v1 = srv.package_verify()
obs("export", {"numstat": git(copy, "diff", "--numstat", "HEAD~1", "HEAD", "--", f"{PKG}/review.html").split()[:2],
               "patch_bytes": len(p.encode()), "longest_added_line": max((len(ln) for ln in added), default=0),
               "csv_changed": git(copy, "diff", "--stat", "HEAD~1", "HEAD", "--", f"{PKG}/csv").strip().splitlines()[-1:] or "none",
               "review_current": v1["review_current"], "exported_by": v1["review_exported_by"]})
pr2 = next(x for x in srv.readiness_check("package")["rules"] if x["rule"] == "prose-plain-english")
obs("prose-plain-english.after_emit", {"counts": pr2["counts"], "texts": pr2["population"]["rows"]})
srv.package_close()
obs("lock_gone", not (pkg / "data" / ".lock").exists())

# ---- class 6: the hook over the v6 note (this copy) and over the untouched v5 note (a second copy)
log = copy / "hook-trace.log"
log.write_text("", encoding="utf-8")
rr = run_hook({"source": "compact", "session_id": SID}, copy, log)
lines = rr.stdout.rstrip("\n").splitlines()
tl = log.read_text(encoding="utf-8").splitlines()
obs("hook.v6_note", {"exit": rr.returncode, "lines": len(lines), "chars": len("\n".join(lines)),
                     "trace_opens": " ".join(tl[0].split(" ")[1:3]) if tl else None})
assert tl and tl[0].split(" ")[1] == f"version={RELEASE}"
second = archive("acmp-replay10-second")
(second / "CLAUDE.md").write_text((FIELD / "CLAUDE.md").read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
log2 = second / "hook-trace.log"
log2.write_text("", encoding="utf-8")
rr2 = run_hook({"source": "startup", "session_id": SID}, second, log2)
lines2 = rr2.stdout.rstrip("\n").splitlines()
tl2 = log2.read_text(encoding="utf-8").splitlines()
obs("hook.v5_note_untouched", {"exit": rr2.returncode, "lines": len(lines2), "chars": len("\n".join(lines2)),
                               "trace_opens": " ".join(tl2[0].split(" ")[1:3]) if tl2 else None,
                               "note_marker": re.search(r"tamheed:note v\d", (second / PKG / "CLAUDE.md").read_text(encoding="utf-8")).group(0)})
assert tl2 and tl2[0].split(" ")[1] == f"version={RELEASE}" and len(lines2) > 0

# ---- the wire: tools/list from the bundle, in its own process
wire = subprocess.run([sys.executable, str(OLD_SCRIPTS / "wire_list.py"), str(BUNDLE), str(SCR / "wire10-empty")],
                      capture_output=True, text=True, env=ENV)
assert wire.returncode == 0, wire.stderr[-600:]
listed = json.loads(wire.stdout)
for n in ("entity_query", "progress_update", "audit_record", "handoff_emit"):
    assert listed[n] == srv.TOOLS[n][1], n
obs("wire", {n: len(listed[n]) for n in ("entity_query", "progress_update", "audit_record", "handoff_emit")})
print("DONE")
