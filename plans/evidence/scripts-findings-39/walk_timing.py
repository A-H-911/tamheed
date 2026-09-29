"""Time a full walk of the journal at limit=100 through the REAL tool of a given bundle, over
a copy of a package (W118). Run it once per bundle, on the same copy, and compare.

Run:  env -u TAMHEED_HOOK_LOG python walk_timing.py <bundle dir: .../plugins/tamheed> <package root> <package name>

An idle open and close changes no file of the package; the script asserts the digest held.
"""
import os
import sys
import time
from pathlib import Path

BUNDLE, ROOT, NAME = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

srv.PACKAGE_ROOT = ROOT
before = srv.package_verify(NAME)["digest"]
assert srv.package_open(NAME)["ok"]
best, rows, pages = None, 0, 0
for _ in range(20):
    start, cursor, rows, pages = time.perf_counter(), None, 0, 0
    while True:
        out = srv.entity_query("progress-entry", columns=["id"], limit=100, after_id=cursor)
        rows += out["count"]
        pages += 1
        cursor = out["next_after"]
        if cursor is None:
            break
    took = (time.perf_counter() - start) * 1000
    best = took if best is None else min(best, took)
first = [r["id"] for r in srv.entity_query("progress-entry", columns=["id"], limit=3)["rows"]]
every = [r["id"] for r in srv.entity_query("progress-entry", columns=["id"],
                                           limit=100000)["rows"]]
srv.package_close()
assert srv.package_verify(NAME)["digest"] == before
print(f"bundle {srv.server_info()['version']}: {rows} rows in {pages} pages;"
      f" best of 20 walks {best:.1f} ms; the last three ids of an unlimited read {every[-3:]};"
      f" the first three {first}")
