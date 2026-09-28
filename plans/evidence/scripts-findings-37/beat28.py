"""Lab beat 28 (plan 154): fire every v5.6 mechanism against the recorded lab-tracker package,
in-process through the engine's tool functions (the same code path the MCP tools call).
Phase B runs FIRST, on a SCRATCH copy (never committed), with hard assertions: a failure stops
the beat before the fixture is touched. Phase A then writes the FIXTURE (committed) and its note
quotes what phase B observed. Every observation is printed as `OBS <key>: <value>`.
The operator's own trace variable is removed before the engine is imported; the hook runs of
this beat write to a trace file inside the scratch folder only.

Run:  env -u TAMHEED_HOOK_LOG python plans/evidence/scripts-findings-37/beat28.py <scratch dir>
"""
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import resume_hook as hook  # noqa: E402
import tamheed_server as srv  # noqa: E402

FIX = REPO / "evals" / "sample-results" / "lab-tracker"
SCR = Path(sys.argv[1])
ACTOR = "agent:lab-beat-28"
RELEASE = "5.6.0"
STAMP = f'<meta name="tamheed-version" content="{RELEASE}">'
LINE = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00 version=(\S+) source=(\S+) lines=(\d+)"
                  r" chars=(\d+) status=(\S+) session=(\S+)$")
SID = "28282828-aaaa-4bbb-8ccc-282828282828"


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


def run_hook(project: Path, source: str, trace: Path) -> str:
    """The hook in-process, its trace aimed at a scratch file; the variable is removed after."""
    buf, old_stdin = io.StringIO(), sys.stdin
    os.environ["TAMHEED_HOOK_LOG"] = str(trace)
    sys.stdin = io.StringIO(json.dumps({"source": source, "session_id": SID}))
    try:
        with contextlib.redirect_stdout(buf):
            assert hook.main([str(project)]) == 0
    finally:
        sys.stdin = old_stdin
        os.environ.pop("TAMHEED_HOOK_LOG", None)
    return buf.getvalue()


# ------------------------------------------------------------------ phase B: a scratch copy, FIRST
assert srv.server_info()["version"] == RELEASE, srv.server_info()["version"]
scr = SCR / "lab28"
shutil.rmtree(scr, ignore_errors=True)
shutil.copytree(FIX / "package", scr / "package")
shutil.copytree(FIX / "workspace", scr / "workspace")
srv.PACKAGE_ROOT = scr
PAGE = scr / "package" / "review.html"

# B1: before anything is opened - the page the PREVIOUS release exported, read by name
old_page = PAGE.read_text(encoding="utf-8")
assert "tamheed-digest" in old_page[:4096] and "tamheed-version" not in old_page
before = keys("package")
assert before == {"review_current": True, "review_exported_by": None}, before
obs("B.before_first_export", before)

o = srv.package_open("package")
assert o["ok"], o
obs("B.open.resume", {"handoff": o["resume"]["handoff"]["id"], "behind": o["resume"]["handoff_behind"]})
(scr / "CLAUDE.md").write_text("# Lab\n\n## Tamheed progress tracking\n\n@package/CLAUDE.md\n",
                               encoding="utf-8", newline="\n")
em = srv.handoff_emit(str(scr), refresh_stock=True)
assert em["ok"], em

# B2: the hook - a printed run and a silent one; both lines name the release and keep the tail
trace = SCR / "hook28.log"
trace.write_text("", encoding="utf-8")
empty = SCR / "empty28"
shutil.rmtree(empty, ignore_errors=True)
empty.mkdir(parents=True)
block = run_hook(scr, "compact", trace)
assert block.startswith("tamheed resume"), block[:60]
assert RELEASE not in block.splitlines()[0]                  # the block's first line is unchanged
assert run_hook(empty, "startup", trace) == ""
printed, silent = trace.read_text(encoding="utf-8").splitlines()
mp, ms = LINE.match(printed), LINE.match(silent)
assert mp and ms, (printed, silent)
assert (mp.group(1), mp.group(2), mp.group(5), mp.group(6)) == (RELEASE, "compact", "printed", SID)
assert (ms.group(1), ms.group(2), ms.group(3), ms.group(5), ms.group(6)) == (
    RELEASE, "startup", "0", "silent", SID)
body = block.rstrip("\n").splitlines()
assert (int(mp.group(3)), int(mp.group(4))) == (len(body), len("\n".join(body)))
obs("B.hook.printed", printed.split(" ", 1)[1])
obs("B.hook.silent", silent.split(" ", 1)[1])

# B3: a copy of the bundle with NO manifest, run as its own process: the line keeps its shape
nomanifest = SCR / "bundle28"
shutil.rmtree(nomanifest, ignore_errors=True)
shutil.copytree(BUNDLE, nomanifest, ignore=shutil.ignore_patterns(".claude-plugin", "__pycache__"))
assert not (nomanifest / ".claude-plugin").exists()
env = dict(os.environ, TAMHEED_HOOK_LOG=str(trace), PYTHONIOENCODING="utf-8")
proc = subprocess.run([sys.executable, str(nomanifest / "server" / "resume_hook.py"), str(empty)],
                      input=json.dumps({"source": "resume", "session_id": SID}), text=True,
                      capture_output=True, env=env, timeout=60)
assert proc.returncode == 0 and proc.stdout == "", (proc.returncode, proc.stdout, proc.stderr)
bare = trace.read_text(encoding="utf-8").splitlines()
assert len(bare) == 3, bare
mb = LINE.match(bare[-1])
assert mb and (mb.group(1), mb.group(2), mb.group(5), mb.group(6)) == ("-", "resume", "silent", SID)
obs("B.hook.no_manifest", bare[-1].split(" ", 1)[1])

# B4: the first export on this release - the page is rewritten with no data moved
digest0 = srv.package_verify()["digest"]
ex = srv.export_html()
assert ex["ok"], ex
page = PAGE.read_text(encoding="utf-8")
assert STAMP in page[:4096] and page.index("tamheed-version") < page.index("<title>")
assert page != old_page and srv.package_verify()["digest"] == digest0
after = keys()
assert after == {"review_current": True, "review_exported_by": RELEASE}, after
first = PAGE.read_bytes()
assert srv.export_html()["ok"] and PAGE.read_bytes() == first          # a constant, no clock
obs("B.first_export", {"before": before, "after": after, "digest_moved": False,
                       "second_export_identical": True})

# B5: the rule - any write stales the page, the export after it makes it current again
pe("Beat 28 scratch entry: a journal write after the export.", event_type="note")
stale = keys()
assert stale == {"review_current": False, "review_exported_by": RELEASE}, stale
assert srv.export_html()["ok"]
fresh = keys()
assert fresh == {"review_current": True, "review_exported_by": RELEASE}, fresh
obs("B.write_after_export", {"after_the_write": stale, "after_the_export": fresh})

# B6: a page another release exported, and a stamp that is not a plain token
good = PAGE.read_text(encoding="utf-8")
PAGE.write_text(good.replace(STAMP, '<meta name="tamheed-version" content="5.5.0">', 1),
                encoding="utf-8", newline="\n")
other = keys()
assert other == {"review_current": True, "review_exported_by": "5.5.0"}, other
PAGE.write_text(good.replace(STAMP, '<meta name="tamheed-version" content="5.6.0 and more">', 1),
                encoding="utf-8", newline="\n")
odd = keys()
assert odd == {"review_current": True, "review_exported_by": None}, odd
obs("B.other_release", {"stamped_5.5.0": other, "not_a_token": odd})
srv.package_close()
print("PHASE-B-DONE")

# ------------------------------------------------------------------ phase A: the fixture
srv.PACKAGE_ROOT = FIX
fixture_before = keys("package")
assert fixture_before == {"review_current": True, "review_exported_by": None}, fixture_before
obs("A.before_first_export", fixture_before)
o = srv.package_open("package")
assert o["ok"], o
info = srv.server_info()
obs("A.schema", {"schema_version": info["schema_version"], "migrations_head": info["migrations_head"],
                 "version": info["version"]})
assert info["version"] == RELEASE and info["schema_version"] == 7
obs("A.open.resume", {"handoff": o["resume"]["handoff"]["id"], "behind": o["resume"]["handoff_behind"],
                      "skill": o["resume"]["skill"]})
target = SCR / "target28"
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

pe("Beat 28 (plan 154, the v5.6.0 continuation), opened at schema_version 7 (no migration in"
   " 5.6.0). THE RELEASE IS NAMED ON TWO SURFACES. The hook's trace line opened with"
   f" version={RELEASE} on a printed run and on a silent one, and kept its session= tail; a copy"
   " of the bundle with no manifest wrote version=- and one line. Before the first export"
   " package_verify read review_current true and review_exported_by null over the page the"
   " previous release had exported; the export rewrote the page with no data moved, the digest"
   f" unchanged, and review_exported_by then read {RELEASE}; a second export was byte-identical."
   " THE EXPORT PRECEDES THE COMMIT: a journal write after the export turned review_current"
   " false and the next export turned it true again. A page stamped by another release kept"
   " review_current true and named that release. THE EMISSION: refresh_stock carried the guide"
   f" to tamheed v{RELEASE}, its title only, no finding.", event_type="note")
h = pe("Resume at: the next continuation beat (29). In flight: none - beat 28 closed. Awaiting"
       " the operator: nothing. Verified facts: handoff-current pass, read after this entry;"
       " the guide reads the 5.6.0 stock. The export, gate_run and package_verify run AFTER this"
       " entry, so their results are in the evidence report and not here. Do not carry: the"
       " scratch copy's journal entry and its two edited pages - never written to this package.",
       event_type="handoff")
obs("A.handoff", h["ids"][0])
obs("A.handoff-current.final", rule("handoff-current")["status"])
assert keys()["review_current"] is False                     # the handoff is itself a write
ex = srv.export_html()
assert ex["ok"], ex
page = (FIX / "package" / "review.html").read_text(encoding="utf-8")
assert STAMP in page[:4096] and f"Latest handoff: {h['ids'][0]}" in page
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
