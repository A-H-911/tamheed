"""Plan 253: the way back from 6.8.0 to 6.7.0, measured on the scratch copy that measure_253.py
left (`<scratch>/ws`, holding a 6.8.0 first-report draft). Run twice, one engine per process:

    env -u TAMHEED_HOOK_LOG python -I wayback_253.py record <6.8.0 bundle> <package dir> <scratch>
    env -u TAMHEED_HOOK_LOG python -I wayback_253.py back   <6.7.0 bundle> <package dir> <scratch>

`record` attaches plain words and records the draft, signed by the scripted operator
`human:wayback-operator` (scratch only). `back` opens the store under 6.7.0, verifies it, reads
the gates, regenerates the 6.8.0 report's page, and drafts the next report on top of it.
Prints counts and sizes only.
"""
import json
import os
import sys
from pathlib import Path

mode, bundle, pkg, scratch = (sys.argv[1], Path(sys.argv[2]).resolve(), sys.argv[3],
                              Path(sys.argv[4]).resolve())
sys.path[:0] = [str(bundle / "server"), str(bundle / "db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

ws = scratch / "ws"


def obs(key, value):
    print(f"OBS {key}: {json.dumps(value, default=str)[:600]}")


def ok(res, what):
    if not res.get("ok"):
        raise SystemExit(f"{what} refused: {json.dumps(res)[:600]}")
    return res


srv.PACKAGE_ROOT = ws
ok(srv.package_open(pkg), "open")
try:
    obs("engine", srv.server_info()["version"])
    c = srv._CURRENT.conn
    if mode == "record":
        d = ok(srv.standup_report(utc_offset="+03:00"), "draft")
        s = d["plan_summary"]["suggest"]
        words = {"headline": "The workshop slice is under way.", "did": "We planned the work.",
                 "challenges": "Nothing blocks the work.", "next": "We go on with the slice.",
                 "colour": "green", "slice_now": s["now"], "slice": "The slice is open."}
        if s.get("next"):
            words["slice_next"] = s["next"]
        ok(srv.standup_report(narrative=words), "words")
        confirm = {"operator_confirm": True, "by": "human:wayback-operator",
                   "words": "record it (way-back test)", "colour": "green", "slice_now": s["now"]}
        if s.get("next"):
            confirm["slice_next"] = s["next"]
        rec = ok(srv.standup_report(action="record", confirm=confirm), "record")
        obs("recorded", rec.get("report") or rec.get("id"))
    else:
        v = srv.package_verify()
        obs("verify", {k: v.get(k) for k in ("verified", "dirty")})
        obs("gate ready", srv.gate_run()["ready"])
        obs("reports", c.execute("SELECT id, lifecycle_status FROM standup_reports"
                                 " ORDER BY id").fetchall())
        rg = srv.standup_report(action="regenerate")
        obs("regenerate", {"ok": rg.get("ok"), "reports": rg.get("reports"),
                           "error": rg.get("error")})
        nd = srv.standup_report()
        obs("next draft", {"ok": nd.get("ok"), "kind": nd.get("kind"), "error": nd.get("error")})
        obs("rows", c.execute("SELECT id, lifecycle_status, LENGTH(facts) FROM standup_reports"
                              " ORDER BY id").fetchall())
finally:
    srv.package_close()
reports = ws / pkg / "reports"
obs("pages", sorted((p.name, p.stat().st_size, "<script" in p.read_text(encoding="utf-8"))
                    for p in reports.glob("*.html")) if reports.exists() else None)
