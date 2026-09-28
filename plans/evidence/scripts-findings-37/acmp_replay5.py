"""Replay the 5.6.0 engine over a read-only COPY of the field package and its control files,
taken by `git archive` at the field's pushed head (plan 155): every 5.5 class again, the new
classes of 5.6.0, and the sweep for the sentences 5.6.0 falsifies.

The sweep is by WORD, not by phrasing (the 5.5.0 brief's sweep matched five phrasings and
missed a negated one), and it reads every file a session reads before acting - the package's
prompts, the memory files, both CLAUDE.md, AGENTS.md, the project skills - beside the register
families. It prints every hit; the maintainer reads each one.

Run:  env -u TAMHEED_HOOK_LOG PYTHONIOENCODING=utf-8 python acmp_replay5.py <copy dir>
"""
import difflib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "server"))
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

COPY = Path(sys.argv[1])
PKG = COPY / "tamheed-package"
HOOK = REPO / "plugins" / "tamheed" / "server" / "resume_hook.py"
SID = "64b2af54-e22c-4e2e-9d13-8c7792eb2b78"
RELEASE = "5.6.0"


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
WORDS = {
    "line-shape": re.compile(r"\bsource=|\bstatus=(?:printed|silent)|\blines=N\b|\bchars=N\b"),
    "review_current": re.compile(r"\breview_current\b"),
    "export-order": re.compile(r"\bexport_html\b"),
}
live = (sorted((COPY / ".claude" / "memory").glob("*.md"))
        + sorted((COPY / ".claude" / "skills").rglob("*.md"))
        + sorted((PKG / "prompts").glob("*.md"))
        + [COPY / "CLAUDE.md", PKG / "CLAUDE.md", COPY / "AGENTS.md"])
print("SWEEP live files:", len(live))
hits = {k: [] for k in WORDS}
for f in live:
    if not f.is_file():
        continue
    for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        for key, pat in WORDS.items():
            if m := pat.search(line):
                hits[key].append((f.relative_to(COPY).as_posix() + f":{n}",
                                  line.strip()[max(0, m.start() - 110):m.end() + 130]))
for fam, floor in (("decisions", 230), ("progress_entries", 1500), ("lessons", 0)):
    rows = [json.loads(x) for x in (PKG / "data" / f"{fam}.jsonl").read_text(
        encoding="utf-8").splitlines() if x.strip()]
    for r in rows:
        if int(r["id"].split("-")[1]) < floor:
            continue
        if fam == "lessons" and r["lifecycle_status"] not in ("Approved", "Proposed"):
            continue
        for col, val in r.items():
            if not isinstance(val, str):
                continue
            for key, pat in WORDS.items():
                for m in pat.finditer(val):
                    hits[key].append((f"{r['id']}.{col}",
                                      " ".join(val[max(0, m.start() - 110):m.end() + 130].split())))
for key, found in hits.items():
    print(f"SWEEP {key}: {len(found)} hit(s)")
    for where, ctx in found:
        print("  HIT", key, "|", where, "|", ctx[:240])

# ------------------------------------------------------------ the classes
srv.PACKAGE_ROOT = COPY
info0 = srv.server_info()
obs("server_info.closed", {k: info0.get(k) for k in ("version", "migrations_head", "schema_version")})
assert info0["version"] == RELEASE
vc = srv.package_verify("tamheed-package")
obs("verify.closed_before_open", {k: vc.get(k) for k in ("verified", "dirty", "review_current",
                                                        "review_exported_by")})
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
                                                       "review_current", "review_exported_by",
                                                       "digest")})
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
for name in ("handoff-current", "lessons-confirmed", "feedback-unanswered", "lessons-note-budget"):
    x = next((x for x in r["rules"] if x["rule"] == name), None)
    if x:
        obs("rule." + name, {"status": x["status"], "n": len(x.get("entities") or []),
                             "note": (x.get("note") or "")[:200]})
obs("readiness", {"ready": r.get("ready"),
                  "blocking": sorted(x["rule"] for x in r["rules"]
                                     if x["status"] == "fail" and x.get("severity") == "blocking")})
q = srv.entity_query("lesson", status="Proposed")
obs("entity_query.proposed", {"count": q.get("count"), "skill": q.get("skill")})
bad = srv.entity_query("no-such-type")
obs("entity_query.error", {"ok": bad.get("ok"), "skill_present": "skill" in bad})
v1 = srv.package_verify()
obs("verify.after_emits_before_export", {k: v1.get(k) for k in ("verified", "dirty",
                                                                "review_current",
                                                                "review_exported_by")}
    | {"digest_equals_D0": v1["digest"] == D0})
ex = srv.export_html()
assert ex["ok"], ex
page_a = (PKG / "review.html").read_bytes()
page = page_a.decode("utf-8")
obs("review.changed", {"bytes_before": len(page_b), "bytes_after": len(page_a),
                       "differs": page_a != page_b,
                       "changed_lines": len(changed_lines(page_b.decode("utf-8", "replace"), page)),
                       "stamp_in_head": f'<meta name="tamheed-version" content="{RELEASE}">'
                                        in page[:4096],
                       "old_page_had_stamp": b"tamheed-version" in page_b[:4096]})
fold = page.split('id="lessons-approved"', 1)[1].split("</details>", 1)[0]
cells = dict(re.findall(r'<tr id="(LL-\d+)"><td>LL-\d+</td><td>[^<]*</td><td>[^<]*</td>'
                        r'<td>([^<]*)</td>', fold))
marked = sorted(i for i, c in cells.items() if c == "rendered")
obs("review.roster", {"rows": len(cells), "marked": len(marked),
                      "equals_note": marked == note_ids(pkg_a)})
v2 = srv.package_verify()
obs("verify.after_export", {k: v2.get(k) for k in ("verified", "dirty", "review_current",
                                                   "review_exported_by")}
    | {"digest_equals_D0": v2["digest"] == D0})
ex2 = srv.export_html()
obs("export.second_identical", (PKG / "review.html").read_bytes() == page_a)

# ------------------------------------------------------------ the rule of plan 152, on the copy
c = srv.progress_update([{"entry": "Replay: a journal note written after the export.",
                          "event_type": "note", "actor": "agent:replay"}])
assert c["ok"], c
v3 = srv.package_verify()
obs("verify.after_a_write", {k: v3.get(k) for k in ("review_current", "review_exported_by")})
hb = srv.server_info()["resume"]["handoff_behind"]
obs("handoff_behind.after_a_note", hb)
srv.export_html()
v4 = srv.package_verify()
obs("verify.after_the_next_export", {k: v4.get(k) for k in ("review_current",
                                                            "review_exported_by")})
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
obs("hook.trace", {"line": tl[0].split(" ", 1)[1] if tl else None, "n": len(tl),
                   "counts_match": bool(tl) and f"lines={len(lines)} chars={len(chr(10).join(lines))}" in tl[0],
                   "opens_with_version": bool(tl) and tl[0].split(" ")[1] == f"version={RELEASE}",
                   "tail_is_session": bool(tl) and tl[0].endswith(f" session={SID}")})
print("DONE")
