"""One action of the 6.5.1 field assurance, in its own process, under ONE bundle of the code.

Usage: python -I worker.py <bundle dir> <package root> <package name> <action>
Actions: probe | write | preview | confirm | held:<file name> | hook.
`held:<file name>` is a confirm in which that data file cannot be replaced, as when another
program holds it. `hook` prints the first lines of the session-start hook for the folder.
It prints one JSON object: ids, statuses, counts, file names. No text of a row.
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
    out["version"] = srv.server_info().get("version")
    if action == "hook":
        import resume_hook as hook  # noqa: E402
        lines = hook.build_lines(root, "startup")
        out["lines"] = [line[:260] for line in lines[:2]]      # the header, and the line after it
        out["count"] = len(lines)
    elif action in ("preview", "confirm") or action.startswith("held:"):
        real = srv.os.replace
        if action.startswith("held:"):
            blocked = action.split(":", 1)[1]

            def held(src, dst, *args, **kwargs):
                if Path(dst).name == blocked:
                    raise PermissionError(13, "the file is held by another program")
                return real(src, dst, *args, **kwargs)

            srv.os.replace = held
        try:
            res = srv.package_migrate(name, confirm=(action != "preview"))
        finally:
            srv.os.replace = real
        out["ok"] = res.get("ok")
        out["error"] = (res.get("error") or "")[:330]
        out["report"] = {k: v for k, v in (res.get("report") or {}).items() if k != "note"}
    else:
        opened = srv.package_open(name)
        out["open_ok"] = opened.get("ok")
        out["open_error"] = (opened.get("error") or "")[:300]
        if opened.get("ok"):
            if action == "write":
                res = srv.entity_upsert([{"type": "constraint", "id": "CON-9990",
                                          "title": "assurance probe"}])
                out["write_ok"] = res.get("ok")
            gates = srv.gate_run()
            out["gate_ready"] = gates.get("ready")
            out["gates"] = {k: v.get("status") for k, v in gates.get("gates", {}).items()
                            if isinstance(v, dict) and "status" in v}
            rep = srv.readiness_check("package")
            out["rules"] = len(rep.get("rules", []))
            out["blocking_fail"] = sorted(r["rule"] for r in rep.get("rules", [])
                                          if r.get("severity") == "blocking"
                                          and r.get("status") == "fail")
            conn = srv._CURRENT.conn
            out["counts"] = {t: conn.execute(f"select count(*) from {t}").fetchone()[0]
                             for t in sorted(set(srv.ENTITY_TABLES.values()))}
            out["edges"] = conn.execute("select count(*) from trace_edges").fetchone()[0]
            out["close_ok"] = srv.package_close().get("ok")
except Exception as exc:                      # a crash is a result of the cell
    out["raised"] = f"{type(exc).__name__}: {exc}"[:300]
print(json.dumps(out, sort_keys=True))
