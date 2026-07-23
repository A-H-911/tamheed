#!/usr/bin/env python3
"""Scratch-diff — the runbook §8 field-level regression diff (plan 024, C29).

Compares two canonical-JSONL package data dirs (live vs scratch) table by table,
keyed correctly, over the UNION of columns — JSON blobs (custom_attributes)
included. Stdlib only; the canonical files ARE the store, no sqlite needed.

    python scratch_diff.py <live-data-dir> <scratch-data-dir> [--json]

Exit codes (validator convention): 0 = no differences, 1 = differences found,
2 = usage/IO error. Exit 1 is NORMAL mid-life — post-migration v2 rows (the
REMAINED bucket) always differ; the §8 pass criterion is the OPERATOR's empty
UNEXPECTED bucket, not this tool's exit code. The tool reports raw truth and
never buckets (report-never-reconcile): field-evidence C29 — two mis-keyed
tables in a session scratchpad produced ~1,000 DUP-KEY noise lines; correct
keying is part of the method, so it ships with the store it reads.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Non-(id)-keyed tables — mirrors the server's _NON_ID_TABLES/CSV-order knowledge.
# These are exactly the keyings ad-hoc scripts get wrong (C29 §E1).
KEYS = {
    "trace_edges": ("from_id", "to_id", "relation"),
    "omissions": ("entity_type", "reason"),
    "entity_types": ("type_id",),
    "packages": ("name",),  # singleton in practice — see diff_table
}
_TRUNC = 160  # human-output value cap; --json carries full values


def load_dir(path: Path) -> dict[str, list[dict]]:
    tables: dict[str, list[dict]] = {}
    for p in sorted(path.glob("*.jsonl")):
        rows = []
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except ValueError as exc:
                raise SystemExit(f"error: {p.name}:{n}: unparseable JSON: {exc}")
        tables[p.stem] = rows
    return tables


def key_rows(table: str, rows: list[dict],
             problems: list[str]) -> dict[tuple, dict]:
    fields = KEYS.get(table, ("id",))
    buckets: dict[tuple, list[dict]] = {}
    for row in rows:
        if any(f not in row for f in fields):
            problems.append(f"{table}: row missing key field(s) {fields}: "
                            f"{json.dumps(row, ensure_ascii=False)[:_TRUNC]}")
            continue
        buckets.setdefault(tuple(str(row[f]) for f in fields), []).append(row)
    keyed = {}
    for k, group in buckets.items():
        if len(group) > 1:  # report, never silently clobber
            problems.append(f"{table}: duplicate key {k} x{len(group)} — "
                            "rows reported, not compared")
        else:
            keyed[k] = group[0]
    return keyed


def diff_rows(a: dict, b: dict) -> list[dict]:
    return [{"field": f, "live": a.get(f), "scratch": b.get(f)}
            for f in sorted(set(a) | set(b)) if a.get(f) != b.get(f)]


def diff_table(table: str, live: list[dict], scratch: list[dict],
               problems: list[str]) -> dict:
    # packages is a one-row table whose key (name) differs structurally between a
    # live package and its scratch — a field-level diff is the useful view there.
    if table == "packages" and len(live) == 1 == len(scratch):
        return {"only_live": [], "only_scratch": [],
                "changed": {"(package)": diff_rows(live[0], scratch[0])}
                if diff_rows(live[0], scratch[0]) else {}}
    lk = key_rows(table, live, problems)
    sk = key_rows(table, scratch, problems)
    return {
        "only_live": sorted(k for k in lk if k not in sk),
        "only_scratch": sorted(k for k in sk if k not in lk),
        "changed": {"/".join(k): d for k in sorted(set(lk) & set(sk))
                    if (d := diff_rows(lk[k], sk[k]))},
    }


def run(live_dir: str, scratch_dir: str) -> tuple[dict, list[str]]:
    live, scratch = (load_dir(Path(d)) for d in (live_dir, scratch_dir))
    problems: list[str] = []
    report = {}
    for table in sorted(set(live) | set(scratch)):
        if table not in scratch:
            report[table] = {"table_only_in": "live"}
        elif table not in live:
            report[table] = {"table_only_in": "scratch"}
        else:
            d = diff_table(table, live[table], scratch[table], problems)
            if d["only_live"] or d["only_scratch"] or d["changed"]:
                report[table] = d
    return report, problems


def _short(v: object) -> str:
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= _TRUNC else s[:_TRUNC] + "…"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Runbook §8 field-level scratch-vs-live package diff")
    ap.add_argument("live_dir")
    ap.add_argument("scratch_dir")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args(argv)
    for d in (args.live_dir, args.scratch_dir):
        if not Path(d).is_dir():
            print(f"error: {d} is not a directory", file=sys.stderr)
            return 2
    report, problems = run(args.live_dir, args.scratch_dir)
    if args.as_json:
        print(json.dumps({"tables": {t: ({"table_only_in": d["table_only_in"]}
                                         if "table_only_in" in d else
                                         {"only_live": ["/".join(k) for k in d["only_live"]],
                                          "only_scratch": ["/".join(k) for k in d["only_scratch"]],
                                          "changed": d["changed"]})
                                     for t, d in report.items()},
                          "problems": problems}, ensure_ascii=False, indent=2))
    else:
        for table, d in report.items():
            if "table_only_in" in d:
                print(f"== {table}: file only in {d['table_only_in']}")
                continue
            print(f"== {table}: +{len(d['only_scratch'])} scratch-only, "
                  f"-{len(d['only_live'])} live-only, {len(d['changed'])} changed")
            for k in d["only_live"]:
                print(f"   only live:    {'/'.join(k)}")
            for k in d["only_scratch"]:
                print(f"   only scratch: {'/'.join(k)}")
            for k, diffs in d["changed"].items():
                for f in diffs:
                    print(f"   {k} :: {f['field']}: live={_short(f['live'])} "
                          f"scratch={_short(f['scratch'])}")
        for p in problems:
            print(f"!! {p}")
        if not report and not problems:
            print("no differences")
    return 1 if report or problems else 0


if __name__ == "__main__":
    sys.exit(main())
