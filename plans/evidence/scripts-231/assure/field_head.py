"""The steps of the 6.5.1 brief for a field that is already on 6.5.0, on a scratch git working
tree of its current commit (plan 231). After each step it prints what git sees as moved.

Usage: python -I field_head.py <new bundle> <scratch working tree> <package name> <feedback id>
Prints file names, ids, column names and counts. No text of a row.
"""
import json
import subprocess
import sys
from pathlib import Path

bundle, root, name, row_id = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
sys.path.insert(0, str(bundle / "server"))
sys.path.insert(0, str(bundle / "db"))
import tamheed_server as srv  # noqa: E402

srv.PACKAGE_ROOT = root


def moved() -> list:
    out = subprocess.run(["git", "status", "--short"], cwd=root, capture_output=True, text=True).stdout
    return sorted(line[3:] for line in out.splitlines())


print("bundle:", srv.server_info()["version"], "| moved at the start:", moved())
opened = srv.package_open(name)
print("open:", opened.get("ok"), (opened.get("error") or "")[:120])
assert srv.package_close()["ok"]
print("after an idle open and close:", moved())

assert srv.package_open(name)["ok"]
print("export_html:", srv.export_html().get("ok"))
verify = srv.package_verify()
print("verify:", {k: verify.get(k) for k in ("verified", "dirty", "review_current", "review_exported_by")})
assert srv.package_close()["ok"]
after_export = moved()
print("after the export:", after_export)

assert srv.package_open(name)["ok"]
emit = srv.handoff_emit(str(root), refresh_stock=True)
print("handoff_emit:", emit.get("ok"), {k: emit.get(k) for k in ("emitted", "unchanged", "diverged")},
      (emit.get("prompt_library") or {}).get("refreshed"))
assert srv.package_close()["ok"]
print("after the stock refresh, more than after the export:", sorted(set(moved()) - set(after_export)))

assert srv.package_open(name)["ok"]
row = srv.entity_query("feedback", ids=[row_id])["rows"][0]
print("the row before:", {k: row.get(k) for k in ("id", "kind", "lifecycle_status", "resolved_in")})
sent = srv.entity_upsert([{"type": "feedback", "id": row_id, "kind": row["kind"], "title": row["title"],
                           "lifecycle_status": "Resolved", "resolved_in": "6.5.1",
                           "upstream_ref": "https://github.com/A-H-911/tamheed/blob/v6.5.1/plans/230-migration-row-time.md"}])
item = (sent.get("items") or [{}])[0]
print("the resolve row:", sent.get("ok"), (sent.get("error") or "")[:200],
      "| changed columns:", sorted(c.get("column") if isinstance(c, dict) else c
                                   for c in item.get("changed_columns") or []),
      "| outcome:", item.get("outcome") or item.get("status"))
gates = srv.gate_run()
print("gate_run ready:", gates.get("ready"), "| verify:", srv.package_verify().get("verified"))
assert srv.package_close()["ok"]
print("at the end:", moved())
print(json.dumps({"done": True}))
