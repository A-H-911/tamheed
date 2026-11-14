"""One action of the 6.5.0 field assurance, in its own process, under ONE version of the code.

Usage: python -I worker.py <bundle dir> <package root> <package name> <action>
Actions: probe | write | preview | confirm. It prints one JSON object: ids, statuses, counts.
"""
import json
import sys
from pathlib import Path

bundle, root, name, action = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
sys.path.insert(0, str(bundle / "server"))
sys.path.insert(0, str(bundle / "db"))
import tamheed_server as srv  # noqa: E402

srv.PACKAGE_ROOT = root
out = {"action": action}
try:
    info = srv.server_info()
    out["version"] = info.get("version")
    if action in ("preview", "confirm"):
        res = srv.package_migrate(name, confirm=(action == "confirm"))
        out["ok"] = res.get("ok")
        out["error"] = (res.get("error") or "")[:300]
        report = res.get("report") or {}
        out["report"] = {k: v for k, v in report.items() if k != "note"}
        out["backup"] = str(res.get("backup") or "")[:200]
        out["keys"] = sorted(res)
    else:
        opened = srv.package_open(name)
        out["open_ok"] = opened.get("ok")
        out["open_error"] = (opened.get("error") or "")[:400]
        if opened.get("ok"):
            if action == "write":
                res = srv.entity_upsert([{"type": "constraint", "id": "CON-9990",
                                          "title": "assurance probe"}])
                out["write_ok"] = res.get("ok")
                out["write_error"] = str(res.get("error") or res.get("items"))[:300]
            gates = srv.gate_run()
            out["gate_ready"] = gates.get("ready")
            out["gates"] = {k: v.get("status") for k, v in gates.get("gates", {}).items()
                            if isinstance(v, dict) and "status" in v}
            rep = srv.readiness_check("package")
            out["rules"] = len(rep.get("rules", []))
            out["blocking_fail"] = sorted(r["rule"] for r in rep.get("rules", [])
                                          if r.get("severity") == "blocking"
                                          and r.get("status") == "fail")
            out["advisory_fail"] = sorted(r["rule"] for r in rep.get("rules", [])
                                          if r.get("severity") != "blocking"
                                          and r.get("status") not in ("pass", "waived"))
            ver = srv.package_verify()
            out["verify"] = {k: ver.get(k) for k in ("verified", "dirty", "review_current")}
            conn = srv._CURRENT.conn
            out["counts"] = {t: conn.execute(f"select count(*) from {t}").fetchone()[0]
                             for t in sorted(set(srv.ENTITY_TABLES.values()))}
            out["edges"] = conn.execute("select count(*) from trace_edges").fetchone()[0]
            closed = srv.package_close()
            out["close_ok"] = closed.get("ok")
            out["close_error"] = (closed.get("error") or "")[:300]
except Exception as exc:                      # the matrix records a crash as a result
    out["raised"] = f"{type(exc).__name__}: {exc}"[:400]
print(json.dumps(out, sort_keys=True))
