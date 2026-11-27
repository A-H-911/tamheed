"""Plan 263: what the 6.9.0 upgrade does to a field package, measured on a scratch git copy of
the field's committed tree, under a chosen bundle (the v6.8.0 tag or this checkout). From
scripts-253/measure_253.py, plus the probes of this round. Prints names, counts and sizes only:
no row text.

    env -u TAMHEED_HOOK_LOG python -I measure_263.py <bundle dir> <tree> <package dir> <scratch>

<tree> is a git repository (only read: `git archive HEAD`) or a GitHub tarball (.tar.gz) of a
commit. Its top folder is dropped, and only the package and the root files below are taken.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

bundle, tree, pkg, scratch = (Path(sys.argv[1]).resolve(), Path(sys.argv[2]), sys.argv[3],
                              Path(sys.argv[4]).resolve())
sys.path[:0] = [str(bundle / "server"), str(bundle / "db")]
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

def _inside(ws: Path, rel: str) -> Path | None:
    """The target of a member, or None when its name leaves the workspace (a tar slip)."""
    if not rel or Path(rel).is_absolute() or ".." in Path(rel).parts or "\\" in rel:
        return None
    target = (ws / rel).resolve()
    return target if target.is_relative_to(ws.resolve()) else None


ws = scratch / "ws"
if ws.exists():
    shutil.rmtree(ws)
ws.mkdir(parents=True)
KEEP = ("CLAUDE.md", ".gitignore", ".claude/settings.json")
if tree.name.endswith(".tar.gz"):
    with tarfile.open(tree) as tar:
        top = tar.getmembers()[0].name.split("/")[0]
        head = top.rsplit("-", 1)[-1][:8]
        for m in tar.getmembers():
            rel = m.name[len(top) + 1:]
            if not rel or not (rel.startswith(pkg + "/") or rel in KEEP) or not m.isfile():
                continue
            target = _inside(ws, rel)
            if target is None:
                raise SystemExit(f"a tarball member leaves the workspace: {m.name!r}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tar.extractfile(m).read())
else:
    listed = subprocess.run(["git", "-C", str(tree), "ls-files", *KEEP], capture_output=True,
                            text=True).stdout.split()
    blob = subprocess.run(["git", "-C", str(tree), "archive", "HEAD", pkg, *listed],
                          capture_output=True, check=True).stdout
    tarfile.open(fileobj=io.BytesIO(blob)).extractall(ws, filter="data")
    head = subprocess.run(["git", "-C", str(tree), "rev-parse", "--short=8", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
for args in (["init", "-q"], ["config", "core.autocrlf", "false"], ["add", "-A"],
             ["-c", "user.name=m", "-c", "user.email=m@x.invalid", "commit", "-qm", "PRE"]):
    subprocess.run(["git", *args], cwd=ws, check=True)


def moved():
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ws,
                         capture_output=True, text=True).stdout.splitlines()
    return [line[3:] for line in out]


def obs(key, value):
    print(f"OBS {key}: {json.dumps(value, default=str, ensure_ascii=False)[:700]}")


obs("field head", head)
obs("engine", {k: srv.server_info()[k] for k in ("version", "migrations_head", "schema_version")})
srv.PACKAGE_ROOT = ws
o = srv.package_open(pkg)
obs("open", {"ok": o["ok"], "error": o.get("error")})
g, r = srv.gate_run(), srv.readiness_check("package")
rules = {x["rule"]: x for x in r["rules"]}
obs("reading", {"gate_ready": g["ready"], "ready": r["ready"],
                "blocking_fail": sorted(x["rule"] for x in r["rules"]
                                        if x["severity"] == "blocking" and x["status"] == "fail")})
obs("package rules", len(r["rules"]))
rd = rules.get("risks-discharged", {})
obs("risks-discharged", {"status": rd.get("status"), "listed": len(rd.get("entities") or []),
                         "candidates": rd.get("note", "").split("operator's word: ")[1].split(". A")[0]
                         if "Candidates for" in rd.get("note", "") else None})
obs("declared-attributes present", "declared-attributes" in rules)
obs("moved by the open", moved())
slates = sorted(p.name[:-len(".slate.json")] for p in (ws / pkg / "slates").glob("*.slate.json")) \
    if (ws / pkg / "slates").is_dir() else []
reads = {}
for name in slates:
    out = srv.slate_read(name)
    reads[name] = ({"ok": True, "answers": len(out.get("answers") or []),
                    "question_changed": len(out.get("question_changed") or []),
                    "changed_rows": len(out.get("changed_rows") or [])}
                   if out.get("ok") else {"ok": False, "error": (out.get("error") or "")[:120]})
obs("slate reads", {"count": len(slates), "ok": sum(1 for v in reads.values() if v["ok"]),
                    "refused": {k: v["error"] for k, v in reads.items() if not v["ok"]}})
obs("slate answers read", {k: v for k, v in reads.items() if v["ok"] and v["answers"]})
em = srv.handoff_emit(str(ws), refresh_stock=True)
obs("emit", {"ok": em["ok"], "restated": len(em.get("restated_content") or []),
             "library": {k: v for k, v in (em.get("prompt_library") or {}).items()
                         if k in ("refreshed", "unchanged")}})
srv.export_html()
v = srv.package_verify()
obs("verify", {k: v.get(k) for k in ("verified", "dirty", "review_current", "review_exported_by")})
obs("moved by emit and export", moved())
srv.package_close()
