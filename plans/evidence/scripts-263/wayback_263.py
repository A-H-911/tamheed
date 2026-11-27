"""Plan 263: the way back to 6.8.0, measured. Run twice: `write` under this checkout, then `read`
under a v6.8.0 bundle (`git archive v6.8.0 plugins/tamheed`), on the same scratch folder.

    env -u TAMHEED_HOOK_LOG python -I wayback_263.py <bundle dir> <scratch> write|read

write (6.9.0): a package with a family's declaration, a row changed by merge_attributes, a slate
with `show_recommendations`, and a slate with a detail of 17,114 characters, each answered.
read (6.8.0): open, gate, readiness, verify, a write of a declared family's row with a value
outside the set, a read of the merged row, slate_read and slate_export of both slates.
Prints outcomes only.
"""
import json
import os
import sys
from pathlib import Path

bundle, scratch, mode = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3]
sys.path[:0] = [str(bundle / "server"), str(bundle / "db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402
import slate as slates  # noqa: E402


def obs(key, value):
    print(f"OBS {key}: {json.dumps(value, default=str, ensure_ascii=False)[:500]}")


def spec(name, **extra):
    q = {"id": "q1", "question": "Which store?", "detail": "short",
         "options": [{"id": "A", "label": "Keep it"}, {"id": "B", "label": "Move it"}],
         "recommended": "A", "reason": "It is measured."}
    q |= extra.pop("question", {})
    return {"name": name, "title": "T", "rounds": [{"id": "r1", "title": "R", "questions": [q]}]} | extra


def answer(name):
    record = json.loads((scratch / "demo" / "slates" / f"{name}.slate.json").read_text(encoding="utf-8"))
    digests = slates.question_digests(record)
    content = {"format": "tamheed-slate-answers", "version": 2, "slate": name,
               "slate_digest": slates.record_digest(record), "exported_at": "2026-11-27T10:00:00.000Z",
               "rounds": [{"id": "r1", "guests": "", "closed": False, "closed_by": "", "closure": {}}],
               "answers": [{"question": "q1", "question_digest": digests["q1"], "selected": "B",
                            "other": "", "note": ""}]}
    (scratch / "demo" / "slates" / f"{name}.answers.json").write_text(json.dumps(content), encoding="utf-8")


srv.PACKAGE_ROOT = scratch
obs("engine", srv.server_info()["version"])
if mode == "write":
    assert srv.package_create("demo", "Demo", "rnd")["ok"]
    out = srv.entity_upsert([
        {"type": "decision", "id": "DEC-001", "title": "d", "lifecycle_status": "Proposed",
         "custom_attributes": {"layer": "product", "keep": "k"}},
        {"type": "entity-type", "type_id": "decision", "operator_confirm": True,
         "custom_attributes": {"fields": [{"name": "layer", "values": ["product", "migration"]}]}}])
    obs("declare", out["ok"])
    obs("merge", srv.entity_upsert([{"type": "decision", "id": "DEC-001",
                                      "merge_attributes": {"layer": "migration", "keep": None}}])["ok"])
    for name, s in (("keyed", spec("keyed", show_recommendations=True)),
                    ("long", spec("long", question={"detail": "line one\n" + "x" * 17_105}))):
        obs(f"export {name}", srv.slate_export(s)["ok"])
        answer(name)
        obs(f"read {name} under 6.9.0", srv.slate_read(name)["ok"])
    srv.package_close()
else:
    o = srv.package_open("demo")
    obs("open", {"ok": o["ok"], "error": o.get("error")})
    obs("gate ready", srv.gate_run()["ready"])
    obs("readiness ready", srv.readiness_check("package")["ready"])
    v = srv.package_verify()
    obs("verify", {k: v.get(k) for k in ("verified", "dirty")})
    row = srv.entity_query("decision", id="DEC-001")["rows"][0]
    obs("merged row read", row["custom_attributes"])
    w = srv.entity_upsert([{"type": "decision", "id": "DEC-001", "title": "d",
                            "lifecycle_status": "Proposed", "custom_attributes": {"layer": "nope"}}])
    obs("a value outside the set, written by 6.8.0", w["ok"])
    for name in ("keyed", "long"):
        r = srv.slate_read(name)
        obs(f"slate_read {name}", {"ok": r["ok"], "error": (r.get("error") or "")[:160]})
    spec_long = spec("long", question={"detail": "line one\n" + "x" * 17_105})
    e = srv.slate_export(spec_long, replace=True)
    obs("re-export long", {"ok": e["ok"], "error": (e.get("error") or "")[:160]})
    v = srv.package_verify()
    obs("verify after the 6.8.0 write", {k: v.get(k) for k in ("verified", "dirty")})
    srv.package_close()
