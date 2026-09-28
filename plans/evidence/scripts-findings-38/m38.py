"""Measurements of the findings_38 cycle (plans 156-159), read-only. Counts and ids only: no
field text is printed.

Run:  PYTHONIOENCODING=utf-8 python plans/evidence/scripts-findings-38/m38.py <field repo> <transcripts root> <prefix>
      <field repo>        the field project's git repository (read through `git show HEAD:`)
      <transcripts root>  the folder that holds one folder of session transcripts per project
      <prefix>            the name the field project's transcript folders start with
"""
import collections
import glob
import json
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FIELD, ROOT, PREFIX = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]


def num(entity_id):
    return int(entity_id.split("-")[1])


def engine_order(ids):
    """The engine's own read: ORDER BY id (BINARY) LIMIT 10, over the real ids, in memory."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (id TEXT PRIMARY KEY)")
    conn.executemany("INSERT INTO t VALUES (?)", [(i,) for i in ids])
    return [r[0] for r in conn.execute("SELECT id FROM t ORDER BY id LIMIT 10")]


lab = glob.glob(str(REPO / "evals/sample-results/lab-tracker/**/data/progress_entries.jsonl"),
                recursive=True)[0]
lab_ids = [json.loads(ln)["id"] for ln in open(lab, encoding="utf-8") if ln.strip()]
raw = subprocess.run(["git", "-C", str(FIELD), "show", "HEAD:tamheed-package/data/progress_entries.jsonl"],
                     capture_output=True, check=True).stdout.decode("utf-8")
field_ids = [json.loads(ln)["id"] for ln in raw.splitlines() if ln.strip()]
for name, mark, ids in (("M24 lab", "M24", lab_ids), ("M25 field", "M25", field_ids)):
    first, newest = engine_order(ids), sorted(ids, key=num)[-3:]
    print(f"{name}: rows {len(ids)}; id widths {sorted({len(i) for i in ids})};"
          f" ORDER BY id LIMIT 10 -> {first[0]}..{first[-1]}; newest by number -> {newest};"
          f" shared ids {len(set(first) & set(newest))}")

# M26: the field's transcripts - every entity_query call, and the bare reads among them
files = []
folders = sorted(ROOT.glob(PREFIX + "*"))
for folder in folders:
    for dirpath, _dirs, names in os.walk(folder):
        files += [os.path.join(dirpath, n) for n in names if n.endswith(".jsonl")]
calls, bare, first_ts, last_ts = 0, collections.Counter(), "9", "0"
for path in files:
    with open(path, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            if "entity_query" not in ln:
                continue
            try:
                row = json.loads(ln)
            except ValueError:
                continue
            content = (row.get("message") or {}).get("content")
            for block in content if isinstance(content, list) else []:
                if not (isinstance(block, dict) and block.get("type") == "tool_use"
                        and "entity_query" in str(block.get("name", ""))):
                    continue
                args = block.get("input") or {}
                calls += 1
                ts = row.get("timestamp", "")
                if ts:
                    first_ts, last_ts = min(first_ts, ts), max(last_ts, ts)
                if not any(k in args for k in ("id", "ids", "search", "after_id", "status")):
                    bare[args.get("type")] += 1
print(f"M26: project folders {len(folders)}; transcript files"
      f" {len(files)}; entity_query calls {calls}; first {first_ts[:10]}; last {last_ts[:10]};"
      f" bare reads of progress-entry {bare.get('progress-entry', 0)},"
      f" of audit-verdict {bare.get('audit-verdict', 0)}")

# M29: the date on the lab's review page
page = Path(glob.glob(str(REPO / "evals/sample-results/lab-tracker/**/review.html"),
                      recursive=True)[0]).read_text(encoding="utf-8")
hits = [(i + 1, len(ln)) for i, ln in enumerate(page.split("\n")) if "Evaluated as of" in ln]
print(f"M29: page lines {len(page.split(chr(10)))}; 'Evaluated as of' occurs {page.count('Evaluated as of')}"
      f" time(s), on (line, chars) {hits}; dated {re.search(r'Evaluated as of ([0-9-]+)', page).group(1)}")

# M30: text-ordered reads in the engine, and whether any of them cuts rows
src = (REPO / "plugins/tamheed/server/tamheed_server.py").read_text(encoding="utf-8").split("\n")
text_order = [i + 1 for i, ln in enumerate(src) if re.search(r"ORDER BY (\w+\.)?id\b(?! DESC)", ln)
              and "CAST" not in ln]
cut = [n for n in text_order if "LIMIT" in src[n - 1]]
print(f"M30: lines with a text ORDER BY id: {len(text_order)} {text_order};"
      f" of them carrying LIMIT: {cut}")
