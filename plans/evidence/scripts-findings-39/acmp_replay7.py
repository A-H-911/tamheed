"""Replay the 5.7.0 engine over a read-only COPY of the field package and its control files,
taken by `git archive` at the field's pushed head (plan 164): the classes of the brief, what
5.7.0 changes, and the sweep for the sentences 5.7.0 falsifies.

The sweep is by WORD, and it reads every file a session reads before acting - the package's
prompts, the memory files, both CLAUDE.md, AGENTS.md, the project skills - beside the register
families. It prints every hit; the maintainer reads each one. A `git archive` copy holds
tracked files only: what the field keeps in ignored folders is NOT swept.

EVERY `after_id` call the field ever made (read from its transcripts) is run through the engine
over the copy and compared with an INDEPENDENT cut. What is under test is the order and the
cut, so the two read one snapshot and one filtered set: the engine's own read of the same
search and status WITHOUT the bound gives the set, and Python orders and cuts it with a key
that shares no code with the engine.

Run:  env -u TAMHEED_HOOK_LOG PYTHONIOENCODING=utf-8 python acmp_replay7.py <copy dir> <second, untouched copy> <transcripts root> <prefix>
"""
import difflib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "server"))
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

COPY, SECOND = Path(sys.argv[1]), Path(sys.argv[2])
ROOT, PREFIX = Path(sys.argv[3]), sys.argv[4]
PKG = COPY / "tamheed-package"
HOOK = REPO / "plugins" / "tamheed" / "server" / "resume_hook.py"
SID = "64b2af54-e22c-4e2e-9d13-8c7792eb2b78"
RELEASE, PREVIOUS = "5.7.0", "5.6.1"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def obs(k, v):
    print("OBS", k, json.dumps(v, ensure_ascii=False, default=str)[:1100])


def run_hook(event, where, trace=None):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(where))
    env.pop("TAMHEED_HOOK_LOG", None)
    if trace is not None:
        env["TAMHEED_HOOK_LOG"] = str(trace)
    return subprocess.run(["uv", "run", "--no-project", str(HOOK)], input=json.dumps(event),
                          capture_output=True, text=True, env=env, cwd=str(where), encoding="utf-8")


def changed_lines(before: str, after: str) -> list[str]:
    return [ln for ln in difflib.unified_diff(before.splitlines(), after.splitlines(), lineterm="",
                                              n=0)
            if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]


def note_ids(text: str) -> list[str]:
    return sorted(re.findall(r"^- \*\*(LL-\d+)\*\*", text, re.M))


def key(entity_id):
    """The page's rule, written a second time and in Python: prefix, first number, id."""
    prefix, sep, tail = entity_id.partition("-")
    digits = re.match(r"\d+", tail)
    return (prefix + sep, int(digits.group()) if digits else 0, entity_id)


def ids_of(result):
    assert result["ok"], result
    return [r["id"] for r in result["rows"]]


# ------------------------------------------------------------ the sweep, before any write
WORDS = {
    "text-order": re.compile(r"(?i)\btext order\b|\bbyte order\b|\bcompared as text\b"
                             r"|\bas text\b"),
    "after_id": re.compile(r"\bafter_id\b"),
    "journal-keys": re.compile(r"(?i)\bprogress_update\b[^.\n]{0,160}?\b(?:summary|subject\b|"
                               r"custom_attributes|occurred_at)"),
    "description": re.compile(r"(?i)\btool'?s description\b|\bdocstring\b"),
    "exports-by-position": re.compile(r"\brows\[\d+\]|\.rows\["),
}
live = (sorted((COPY / ".claude" / "memory").glob("*.md"))
        + sorted((COPY / ".claude" / "skills").rglob("*.md"))
        + sorted((PKG / "prompts").glob("*.md"))
        + [COPY / "CLAUDE.md", PKG / "CLAUDE.md", COPY / "AGENTS.md"]
        + sorted((COPY / "scripts").glob("gen-*.mjs")) + sorted((COPY / "scripts" / "lib").glob("*.mjs")))
print("SWEEP live files:", len(live))
hits = {k: [] for k in WORDS}
for f in live:
    if not f.is_file():
        continue
    for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        for name, pat in WORDS.items():
            if m := pat.search(line):
                hits[name].append((f.relative_to(COPY).as_posix() + f":{n}",
                                   line.strip()[max(0, m.start() - 110):m.end() + 130]))
for fam, floor in (("decisions", 230), ("progress_entries", 1500), ("lessons", 0)):
    rows = [json.loads(x) for x in (PKG / "data" / f"{fam}.jsonl").read_text(
        encoding="utf-8").splitlines() if x.strip()]
    for r in rows:
        if key(r["id"])[1] < floor:
            continue
        if fam == "lessons" and r["lifecycle_status"] not in ("Approved", "Proposed"):
            continue
        for col, val in r.items():
            if not isinstance(val, str):
                continue
            for name, pat in WORDS.items():
                for m in pat.finditer(val):
                    hits[name].append((f"{r['id']}.{col}",
                                       " ".join(val[max(0, m.start() - 110):m.end() + 130].split())))
for name, found in hits.items():
    print(f"SWEEP {name}: {len(found)} hit(s)")
    for where, ctx in found:
        print("  HIT", name, "|", where, "|", ctx[:240])

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
obs("open.resume", {"handoff": res["handoff"]["id"],
                    "corrections": [c["id"] for c in (res["handoff"].get("corrections") or [])],
                    "behind": res["handoff_behind"], "open_feedback": res["open_feedback"],
                    "last_entries": [e["id"] for e in res["last_entries"]]})
v0 = srv.package_verify()
D0 = v0["digest"]
obs("verify.before_any_write", {k: v0.get(k) for k in ("verified", "dirty", "foreign",
                                                       "review_current", "review_exported_by")})

# ---- the order, on the field's own families
journal = ids_of(srv.entity_query("progress-entry", columns=["id"], limit=100000))
limited = ids_of(srv.entity_query("progress-entry", columns=["id"], limit=10))
obs("limited_read", {"total": len(journal), "limit_10": [limited[0], limited[-1]],
                     "equals_ten_lowest_by_number": limited == sorted(journal, key=key)[:10],
                     "shared_with_last_entries": len(set(limited)
                                                     & {e["id"] for e in res["last_entries"]})})
families = {}
for etype, table in sorted(srv.ENTITY_TABLES.items()):
    if etype in ("trace-edge", "omission", "package"):
        continue
    got = srv.entity_query(etype, columns=["id"], limit=100000)
    if got.get("ok") and got["rows"]:
        families[etype] = ids_of(got)
wrong = [t for t, ids in families.items() if ids != sorted(ids, key=key)]
moved_fams = [t for t, ids in families.items() if ids != sorted(ids)]
obs("order.every_family", {"families": len(families), "not_in_the_independent_order": wrong,
                           "order_differs_from_text": moved_fams})
t0 = time.perf_counter()
walked, cursor, pages = [], None, 0
while True:
    out = srv.entity_query("progress-entry", columns=["id"], limit=100, after_id=cursor)
    walked += ids_of(out)
    pages += 1
    cursor = out["next_after"]
    if cursor is None:
        break
obs("walk.journal_at_limit_100", {"rows": len(walked), "pages": pages,
                                  "complete_and_in_order": walked == journal,
                                  "milliseconds": round((time.perf_counter() - t0) * 1000, 1)})

# ---- every `after_id` call the field made, through the engine, against the independent cut
files = []
for folder in sorted(ROOT.glob(PREFIX + "*")):
    for dirpath, _dirs, fnames in os.walk(folder):
        if os.sep + "memory" in dirpath:
            continue
        files += [os.path.join(dirpath, n) for n in fnames if n.endswith(".jsonl")]
calls, seen = [], set()
for path in files:
    with open(path, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            if "after_id" not in ln:
                continue
            try:
                row = json.loads(ln)
            except ValueError:
                continue
            content = (row.get("message") or {}).get("content")
            for block in content if isinstance(content, list) else []:
                if (isinstance(block, dict) and block.get("type") == "tool_use"
                        and str(block.get("name", "")).endswith("entity_query")
                        and block["id"] not in seen
                        and (block.get("input") or {}).get("after_id") is not None):
                    seen.add(block["id"])
                    calls.append((row.get("timestamp", ""), block["input"]))
agree, part, refused, journal_calls = 0, [], 0, 0
for ts, args in sorted(calls, key=lambda c: c[0]):
    etype = args.get("type")
    filt = {k: args[k] for k in ("search", "status") if args.get(k) is not None}
    bound, limit = str(args["after_id"]), int(args.get("limit", 100))
    engine = srv.entity_query(etype, columns=["id"], after_id=bound, limit=limit, **filt)
    whole = srv.entity_query(etype, columns=["id"], limit=100000, **filt)
    if not (engine.get("ok") and whole.get("ok")):
        refused += 1
        continue
    journal_calls += etype == "progress-entry"
    independent = sorted((i for i in ids_of(whole) if key(i) > key(bound)), key=key)[:limit]
    if ids_of(engine) == independent:
        agree += 1
    else:
        part.append((ts[:10], etype, bound, limit))
obs("after_id.every_field_call", {"calls": len(calls), "on_the_journal": journal_calls,
                                  "engine_equals_the_independent_cut": agree,
                                  "they_part": part, "refused_by_the_engine": refused})
the_read = ids_of(srv.entity_query("progress-entry", search="handoff_emit", after_id="PE-950",
                                   limit=3, columns=["id"]))
obs("the_read_of_2026-09-11", the_read)

# ---- the refusals
held = (srv.entity_query("progress-entry", limit=1)["total"],
        srv.entity_query("audit-verdict", limit=1)["total"])
r1 = srv.progress_update([{"summary": "what happened", "event_type": "work-done",
                           "actor": "agent:replay"}])
r2 = srv.audit_record([{"ac_id": "AC-001", "verdict": "Met", "notes": "n"}])
now = (srv.entity_query("progress-entry", limit=1)["total"],
       srv.entity_query("audit-verdict", limit=1)["total"])
obs("refusals", {"progress_update": [r1["ok"], r1["error"][:150]],
                 "audit_record": [r2["ok"], r2["error"][:150]],
                 "rows_written": [now[0] - held[0], now[1] - held[1]],
                 "digest_equals_D0": srv.package_verify()["digest"] == D0})
g = srv.gate_run()
obs("gate_run", {"ready": g.get("ready"),
                 "audit_evidence": {k: g["gates"]["audit_evidence"].get(k)
                                    for k in ("evidenced", "narrated", "ungraded")}})

root_b = (COPY / "CLAUDE.md").read_text(encoding="utf-8")
pkg_b = (PKG / "CLAUDE.md").read_text(encoding="utf-8")
guide_b = (PKG / "prompts" / "README.md").read_text(encoding="utf-8")
page_b = (PKG / "review.html").read_bytes()
e = srv.handoff_emit(str(COPY))
assert e["ok"], e
obs("emit", {k: e.get(k) for k in ("written", "unchanged", "stale_references", "restated_content",
                                  "oversized_prompts", "stock_merged")})
obs("emit.library", {k: v for k, v in e["prompt_library"].items() if v})
root_a = (COPY / "CLAUDE.md").read_text(encoding="utf-8")
pkg_a = (PKG / "CLAUDE.md").read_text(encoding="utf-8")
obs("root.changed_lines", len(changed_lines(root_b, root_a)))
obs("pkg_note.changed_lines", [ln[:160] for ln in changed_lines(pkg_b, pkg_a)])
obs("pkg_note.roster_equal", note_ids(pkg_b) == note_ids(pkg_a))
e1 = srv.handoff_emit(str(COPY))
obs("emit.second", {"written": e1["written"]})
e2 = srv.handoff_emit(str(COPY), refresh_stock=True)
obs("emit.refresh", {"refreshed": e2["prompt_library"].get("refreshed"), "written": e2["written"]})
guide_a = (PKG / "prompts" / "README.md").read_text(encoding="utf-8")
obs("guide.changed_lines", changed_lines(guide_b, guide_a))
r = srv.readiness_check("package")
obs("readiness", {"ready": r.get("ready"),
                  "blocking": sorted(x["rule"] for x in r["rules"]
                                     if x["status"] == "fail" and x.get("severity") == "blocking"),
                  "handoff-current": next(x["status"] for x in r["rules"]
                                          if x["rule"] == "handoff-current")})
v1 = srv.package_verify()
obs("verify.after_emits_before_export", {k: v1.get(k) for k in ("verified", "dirty",
                                                                "review_current",
                                                                "review_exported_by")}
    | {"digest_equals_D0": v1["digest"] == D0})
ex = srv.export_html()
assert ex["ok"], ex
page_a = (PKG / "review.html").read_bytes()
page, old = page_a.decode("utf-8"), page_b.decode("utf-8", "replace")
moved = changed_lines(old, page)
dated = re.search(r"Evaluated as of (\d{4}-\d\d-\d\d)", old).group(1)
gone = [m[1:] for m in moved if m[0] == "-"]
came = [m[1:] for m in moved if m[0] == "+"]
stated = "Evaluated as of "
only_the_date = [a.replace(stated + dated, stated + TODAY) == b
                 for a, b in zip(gone, came) if stated in a]
obs("review.changed", {"bytes_before": len(page_b), "bytes_after": len(page_a),
                       "numstat": [len(came), len(gone)],
                       "short_changed_lines": [m[:80] for m in moved if len(m) < 200],
                       "page_was_dated": dated, "today": TODAY,
                       "the_date_line_changed_in_its_stated_date_only": only_the_date,
                       "csv": {k: len(v) for k, v in ex["csv"].items() if isinstance(v, list)}})
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
srv.export_html()
obs("export.second_identical", (PKG / "review.html").read_bytes() == page_a)

# the audit's export, outside the package: csv/ lands beside it
held_page = (PKG / "review.html").read_bytes()
outside = COPY.parent / "audit-replay7" / "review.html"
xo = srv.export_html(output=str(outside))
beside = sorted(p.name for p in (outside.parent / "csv").glob("*.csv"))
obs("export.outside", {"ok": xo["ok"], "csv_files_beside_it": len(beside),
                       "same_names_as_the_package": beside == sorted(
                           p.name for p in (PKG / "csv").glob("*.csv")),
                       "package_page_unchanged": (PKG / "review.html").read_bytes() == held_page})

# ------------------------------------------------------------ a write after the export
c = srv.progress_update([{"entry": "Replay: a journal note written after the export.",
                          "event_type": "note", "actor": "agent:replay"}])
assert c["ok"], c
v3 = srv.package_verify()
obs("verify.after_a_write", {k: v3.get(k) for k in ("review_current", "review_exported_by")})
srv.export_html()
v4 = srv.package_verify()
obs("verify.after_the_next_export", {k: v4.get(k) for k in ("review_current",
                                                            "review_exported_by")})
srv.package_close()

# ------------------------------------------------------------ the hook over the SECOND copy
log = SECOND / "hook-trace.log"
log.write_text("", encoding="utf-8")
rr = run_hook({"source": "compact", "session_id": SID}, SECOND, log)
lines = rr.stdout.rstrip("\n").splitlines()
tl = log.read_text(encoding="utf-8").splitlines()
obs("hook.compact", {"exit": rr.returncode, "lines": len(lines), "chars": len("\n".join(lines)),
                     "has_corrections_line": any(ln.startswith("Corrections") for ln in lines)})
obs("hook.trace", {"line": tl[0].split(" ", 1)[1] if tl else None, "n": len(tl),
                   "counts_match": bool(tl) and f"lines={len(lines)} chars={len(chr(10).join(lines))}" in tl[0],
                   "opens_with_version": bool(tl) and tl[0].split(" ")[1] == f"version={RELEASE}",
                   "tail_is_session": bool(tl) and tl[0].endswith(f" session={SID}")})
print("DONE")
