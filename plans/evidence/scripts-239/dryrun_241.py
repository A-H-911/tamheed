"""Plan 241, step 0: does moving a met dependency, assumption and plan to `Implemented` move any
readiness rule or gate? Runs the CURRENT engine on a throwaway copy of a field package (scratch
only, never the original). Prints rule names and counts only.

    env -u TAMHEED_HOOK_LOG python -I dryrun_241.py <package parent folder> <package dir>
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

R = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(R / "plugins/tamheed/server"), str(R / "plugins/tamheed/db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

src, pkg = Path(sys.argv[1]).resolve(), sys.argv[2]
work = Path(tempfile.mkdtemp(prefix="dry241-"))
shutil.copytree(src / pkg, work / pkg, ignore=shutil.ignore_patterns(".lock"))
srv.PACKAGE_ROOT = work


def reading():
    g = srv.gate_run()
    r = srv.readiness_check("package")
    return ({k: (v.get("status", v.get("pass")) if isinstance(v, dict) else v)
             for k, v in g.get("gates", {}).items()},
            {x["rule"]: (x["severity"], x["status"], len(x.get("entities") or []))
             for x in r["rules"]})


assert srv.package_open(pkg)["ok"]
before = reading()
pick = {}
for etype, table in (("dependency", "dependencies"), ("assumption", "assumptions"),
                     ("execution-plan", "execution_plans")):
    row = srv._CURRENT.conn.execute(
        f"SELECT id FROM {table} WHERE lifecycle_status = 'Approved' ORDER BY id LIMIT 1").fetchone()
    if row:
        pick[etype] = row[0]
conn = srv._CURRENT.conn
items = []
for (t, i), table in zip(pick.items(), ("dependencies", "assumptions", "execution_plans")):
    cur = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (i,))
    row = dict(zip([d[0] for d in cur.description], cur.fetchone()))
    row.pop("last_referenced", None)
    items.append({"type": t, **{k: v for k, v in row.items() if v is not None},
                  "lifecycle_status": "Implemented"})
out = srv.entity_upsert(items)
print("OBS moved:", pick, "| ok:", out["ok"],
      "| errors:", [x.get("error", "")[:120] for x in out["items"] if not x.get("ok")])
after = reading()
srv.package_close()
gates = {k: (before[0].get(k), v) for k, v in after[0].items() if before[0].get(k) != v}
rules = {k: (before[1].get(k), v) for k, v in after[1].items() if before[1].get(k) != v}
print("OBS gates changed:", gates or "none")
print("OBS rules changed:", rules or "none")
print("OBS blocking rules changed:", [k for k, (b, a) in rules.items()
                                       if (a and a[0] == "blocking") or (b and b[0] == "blocking")]
      or "none")
shutil.rmtree(work, ignore_errors=True)
