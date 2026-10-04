"""Plan 198: the two planning-only recorded fixtures and the generated sample follow the 6.0.0
engine, through the engine's own tools (never a hand edit). The fixtures: `package_migrate`
syncs the registry (the `prompt` type), then an omission row records why no prompt row exists,
then the page is re-exported where one exists. The sample: `package_migrate` converts its three
prompt files to rows (the kickoff by the header's file name, P19), the backup folder is removed
(git holds the files), the root guide is seeded. Every observation prints as `OBS <key> <value>`.

    env -u TAMHEED_HOOK_LOG python fixtures_198.py
"""
import json
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
BUNDLE = REPO / "plugins" / "tamheed"
sys.path.insert(0, str(BUNDLE / "server"))
sys.path.insert(0, str(BUNDLE / "db"))
os.environ.pop("TAMHEED_HOOK_LOG", None)
import tamheed_server as srv  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def obs(key, value):
    print(f"OBS {key} {json.dumps(value, ensure_ascii=False, default=str)[:900]}")


assert srv.server_info()["version"] == "6.0.0", srv.server_info()["version"]

# ---------------------------------------------------------------- (a) the planning-only fixtures
FIXTURES = [
    ("minimal-brief", "this recorded planning run stopped before Stage 20, so no kickoff prompt was"
                      " written (plan 198, the prompt family is Always since 6.0.0)", True),
    ("execution-loop", "this recorded fixture never carried a prompt file and no handoff stage was run"
                       " (plan 198, the prompt family is Always since 6.0.0)", False),
]
for case, reason, has_page in FIXTURES:
    srv.PACKAGE_ROOT = REPO / "evals" / "sample-results" / case
    pre = srv.package_migrate("package")
    obs(f"{case}.preview", {"ok": pre.get("ok"), "stage": pre.get("stage"), "error": pre.get("error"),
                            "report_keys": sorted((pre.get("report") or {}).keys())})
    if pre.get("ok"):
        out = srv.package_migrate("package", confirm=True)
        assert out["ok"], out
        obs(f"{case}.confirm", {k: v for k, v in out["report"].items()
                                if k not in ("prompt_files",)})
    o = srv.package_open("package")
    assert o["ok"], o
    g0 = srv.gate_run()["gates"]["G-SET"]
    obs(f"{case}.gset.before", g0)
    w = srv.entity_upsert([{"type": "omission", "entity_type": "prompt", "reason": reason}])
    assert w["ok"], w
    g1 = srv.gate_run()["gates"]["G-SET"]
    obs(f"{case}.gset.after", g1["status"])
    if has_page:
        ex = srv.export_html()
        assert ex["ok"], ex
    v = srv.package_verify()
    obs(f"{case}.verify", {k: v.get(k) for k in ("verified", "dirty", "foreign", "review_current",
                                                   "review_exported_by")})
    srv.package_close()
    assert not (srv.PACKAGE_ROOT / "package" / "data" / ".lock").exists()

# ---------------------------------------------------------------- (b) the generated sample
srv.PACKAGE_ROOT = REPO / "generated-samples"
NAME = "support-triage-agent-v2"
pre = srv.package_migrate(NAME)
assert pre["ok"], pre
rep = pre["report"]
obs("sample.preview", {"files": rep.get("prompt_files"), "rows": rep.get("prompt_rows"),
                       "entry_point": rep.get("entry_point"), "folder": rep.get("prompts_folder"),
                       "g_set": rep.get("g_set")})
out = srv.package_migrate(NAME, confirm=True)
assert out["ok"], out
obs("sample.confirm", out["report"].get("prompt_files_applied"))
backup = REPO / "generated-samples" / NAME / "prompts-v5-backup"
obs("sample.backup_files", sorted(q.name for q in backup.iterdir()))
shutil.rmtree(backup)
obs("sample.prompts_folder_gone", not (REPO / "generated-samples" / NAME / "prompts").exists())
obs("sample.root_readme", (REPO / "generated-samples" / NAME / "README.md").exists())
o = srv.package_open(NAME)
assert o["ok"], o
obs("sample.rows", [(r["id"], r["kind"], r["title"], r["lifecycle_status"], r["plugin_skill"])
                    for r in srv.entity_query("prompt", limit=10)["rows"]])
obs("sample.entry_point", srv.server_info()["package"]["entry_point"])
obs("sample.gset", srv.gate_run()["gates"]["G-SET"]["status"])
v = srv.package_verify()
obs("sample.verify", {k: v.get(k) for k in ("verified", "dirty", "foreign")})
srv.package_close()
print("FIXTURES-198-DONE")
