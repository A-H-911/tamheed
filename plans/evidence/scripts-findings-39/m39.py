"""Measurements of the findings_39 cycle (plans 160-164), read-only. Classes, counts and ids
only: no field text is printed (a search needle is used to filter and never shown).

Run:  PYTHONIOENCODING=utf-8 python plans/evidence/scripts-findings-39/m39.py <field repo> <transcripts root> <prefix>
      <field repo>        the field project's git repository (read through `git show HEAD:`)
      <transcripts root>  the folder that holds one folder of session transcripts per project
      <prefix>            the name the field project's transcript folders start with

HORIZON. The harness sweeps old session transcripts, so every count taken from them holds for
the day it was taken: a later run reads fewer old files and more new ones. The script prints the
oldest and the newest timestamp it read.
"""
import collections
import json
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FIELD, ROOT, PREFIX = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, str(REPO / "plugins" / "tamheed" / "server"))
import tamheed_server as srv  # noqa: E402

TAKES = {"progress_update": ("entries", {"entry", "event_type", "subject_id", "actor",
                                         "corrects", "phase_id", "slice_id"}),
         "audit_record": ("verdicts", {"ac_id", "verdict", "evidence", "verified_by",
                                       "verification_method", "against_commit"})}


def field_rows(family):
    raw = subprocess.run(["git", "-C", str(FIELD), "show",
                          f"HEAD:tamheed-package/data/{family}.jsonl"],
                         capture_output=True, check=True).stdout.decode("utf-8")
    return [json.loads(ln) for ln in raw.splitlines() if ln.strip()]


def key(entity_id):
    """An INDEPENDENT reading of the page's rule, in Python: prefix, first number, id. It is
    here to check the engine, so it shares no code with it. Good for ids a store can hold and
    for bounds of the same shape; the engine's own cut is proven on odd strings by its test."""
    prefix, sep, tail = entity_id.partition("-")
    digits = re.match(r"\d+", tail)
    return (prefix + sep, int(digits.group()) if digits else 0, entity_id)


# ---------------------------------------------------------------- the field package's ids
head = subprocess.run(["git", "-C", str(FIELD), "rev-parse", "--short=8", "HEAD"],
                      capture_output=True, check=True).stdout.decode().strip()
names = subprocess.run(["git", "-C", str(FIELD), "ls-tree", "--name-only", "HEAD",
                        "tamheed-package/data/"], capture_output=True,
                       check=True).stdout.decode().split()
families = sorted(Path(n).stem for n in names if n.endswith(".jsonl"))
moved, multi, walked = [], {}, 0
cut, binds = srv._after_id()
for fam in families:
    ids = [r["id"] for r in field_rows(fam) if isinstance(r.get("id"), str)]
    if not ids:
        continue
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (id TEXT PRIMARY KEY)")
    conn.executemany("INSERT INTO t VALUES (?)", [(i,) for i in ids])
    page = [r[0] for r in conn.execute(f"SELECT id FROM t ORDER BY {srv._by_id()}")]
    assert page == sorted(ids, key=key), fam          # the engine's order == the independent one
    seen, cursor = [], None
    while True:                                        # a walk at limit 7, through the cut
        rows = [r[0] for r in conn.execute(
            "SELECT id FROM t" + (f" WHERE {cut}" if cursor else "")
            + f" ORDER BY {srv._by_id()} LIMIT 8", [cursor] * binds if cursor else [])]
        seen += rows[:7]
        if len(rows) <= 7:
            break
        cursor = rows[6]
    assert seen == page, fam
    walked += 1
    if page != sorted(ids):
        moved.append(fam)
    many = [i for i in ids if len(re.findall(r"\d+", i)) > 1]
    if many:
        multi[fam] = (len(many), len(ids))
print(f"field head {head}: families with ids {walked}; each walks complete in the page's order"
      f" and equals the independent key")
print(f"M41: families where text order and the page's order differ: {moved}")
print(f"M59: families whose ids carry more than one number (count of rows): {multi}")

# ---------------------------------------------------------------- the transcripts
files = []
for folder in sorted(ROOT.glob(PREFIX + "*")):
    for dirpath, _dirs, fnames in os.walk(folder):
        if os.sep + "memory" in dirpath:
            continue
        files += [os.path.join(dirpath, n) for n in fnames if n.endswith(".jsonl")]
uses, seen_results = {}, set()
per_day = collections.defaultdict(lambda: [0, 0])
classes = collections.Counter()
writes = {n: collections.Counter() for n in TAKES}
dropped, bounds = [], []
first_ts, last_ts = "9", "0"
for path in files:
    with open(path, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            if "tamheed" not in ln and "tool_result" not in ln:
                continue
            try:
                row = json.loads(ln)
            except ValueError:
                continue
            ts = row.get("timestamp") or ""
            content = (row.get("message") or {}).get("content")
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict):
                    continue
                name = str(block.get("name") or "")
                if (block.get("type") == "tool_use" and "tamheed" in name
                        and block["id"] not in uses):
                    tool = name.split("__")[-1]
                    uses[block["id"]] = (tool, ts, block.get("input") or {})
                    per_day[ts[:10]][0] += 1
                    if ts:
                        first_ts, last_ts = min(first_ts, ts), max(last_ts, ts)
                if (block.get("type") == "tool_result" and block.get("tool_use_id") in uses
                        and block["tool_use_id"] not in seen_results):
                    seen_results.add(block["tool_use_id"])
                    body = block.get("content")
                    text = body if isinstance(body, str) else " ".join(
                        x.get("text", "") for x in (body or []) if isinstance(x, dict))
                    tool, uts, args = uses[block["tool_use_id"]]
                    refused = bool(block.get("is_error")
                                   or re.search(r'"ok":\s*false', text[:400]))
                    if refused:
                        per_day[uts[:10]][1] += 1
                        if tool == "entity_query" and "unknown columns" in text[:300]:
                            classes[("unknown columns", uts[:10])] += 1
                        if tool == "entity_upsert":
                            for _hit in re.findall(r"unknown columns for ", text):
                                classes[("unknown columns, a write", uts[:10])] += 1
                        if re.search(r"NOT NULL constraint failed: progress_entries.entry",
                                     text[:300]):
                            classes[("NOT NULL entry", uts[:10])] += 1
                    if tool in TAKES:
                        arg, takes = TAKES[tool]
                        items = args.get(arg)
                        if isinstance(items, str):
                            try:
                                items = json.loads(items)
                            except ValueError:
                                items = None
                        for item in items if isinstance(items, list) else []:
                            if not isinstance(item, dict):
                                continue
                            writes[tool]["refused" if refused else "written"] += 1
                            extra = sorted(set(item) - takes)
                            if extra and not refused:
                                dropped.append((uts[:10], tool, extra))
                    if (tool == "entity_query" and args.get("after_id") is not None
                            and not refused):
                        bounds.append((uts, args))
print(f"M38: transcript files {len(files)}; tamheed calls {len(uses)}; results paired"
      f" {len(seen_results)}; refusals or errors {sum(v[1] for v in per_day.values())};"
      f" first {first_ts[:19]}; last {last_ts[:19]}")
print("M39: per day, calls and refusals: "
      + "; ".join(f"{d} {c}/{r}" for d, (c, r) in sorted(per_day.items())))
cols = [k for k in classes if k[0] == "unknown columns"]
wcols = [k for k in classes if k[0] == "unknown columns, a write"]
print(f"M45: 'unknown columns' refusals of entity_query {sum(classes[k] for k in cols)},"
      f" last on {max((k[1] for k in cols), default='-')}; items of entity_upsert refused"
      f" for unknown columns {sum(classes[k] for k in wcols)},"
      f" last on {max((k[1] for k in wcols), default='-')}")
nn = [k for k in classes if k[0] == "NOT NULL entry"]
print(f"M42: journal items written {writes['progress_update']['written']}, refused"
      f" {writes['progress_update']['refused']}; verdict items written"
      f" {writes['audit_record']['written']}, refused {writes['audit_record']['refused']};"
      f" written with a key the tool dropped: {dropped};"
      f" 'NOT NULL ... entry' errors on {sorted(k[1] for k in nn)}")

# ---------------------------------------------------------------- the typed bounds (W113)
# A bound is TYPED when no earlier result handed it out as `next_after`. The transcripts
# cannot say that cheaply, so EVERY `after_id` call is replayed under both cuts, over the
# rows the field's head holds that are no younger than the call: where the two cuts agree the
# call was safe under either order, and only the calls where they part are listed. The
# independent cut is Python's (key() above), never the engine's.
cache, agree, per_family = {}, 0, collections.Counter()
print("the `after_id` calls where the text cut and the page's cut part, as classes:")
for uts, args in sorted(bounds, key=lambda b: b[0]):
    per_family[args.get("type")] += 1
    fam = srv.ENTITY_TABLES.get(args.get("type"))
    if fam not in families:
        continue
    rows = cache.setdefault(fam, field_rows(fam))
    rows = [r for r in rows if (r.get("occurred_at") or r.get("recorded_at") or "") <= uts
            or not (r.get("occurred_at") or r.get("recorded_at"))]
    if args.get("search") is not None:
        needle = str(args["search"]).lower()
        rows = [r for r in rows if any(isinstance(v, str) and needle in v.lower()
                                       for v in r.values())]
    if args.get("status") is not None:
        rows = [r for r in rows
                if (r.get("lifecycle_status") or r.get("status")) == args["status"]]
    bound, limit = str(args["after_id"]), int(args.get("limit", 100))
    text_cut = sorted(r["id"] for r in rows if r["id"] > bound)[:limit]
    page_cut = sorted((r["id"] for r in rows if key(r["id"]) > key(bound)), key=key)[:limit]
    if text_cut == page_cut:
        agree += 1
        continue
    print(f"  {uts[:10]} {args.get('type')} after {bound} limit {limit}"
          f" searched={args.get('search') is not None} status={args.get('status') is not None}"
          f" text={len(text_cut)} page={len(page_cut)}"
          f" dropped={sorted(set(page_cut) - set(text_cut), key=key)}"
          f" over-reached={len(set(text_cut) - set(page_cut))}")
print(f"`after_id` calls replayed {sum(per_family.values())}; the two cuts agree on {agree};"
      f" per family {dict(per_family)}")
