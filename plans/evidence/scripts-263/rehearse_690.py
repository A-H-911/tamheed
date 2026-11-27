"""Plan 263 (from scripts-253/rehearse_680.py): rehearse a field brief with a headless agent.

    python -I rehearse_690.py setup <tree: git repo or .tar.gz> <package dir> <brief> <scratch> <branch>
    python -I rehearse_690.py run <scratch> <label> <old|new> <answers file>

`setup` builds a scratch repository from the field's committed tree (the package, CLAUDE.md,
.gitignore, .claude/settings.json), with the brief in briefs/ and the v6.8.0 bundle from the tag.
A .tar.gz is a GitHub tarball of a commit: its top folder is dropped. `run` starts one
`claude -p` session, a new process as a restart is, under the 6.8.0 bundle (`old`) or this
checkout (`new`). The operator's answers come from a file. Prints counts only. Three paths per
field (R161): old then new (the restart), and new alone in a fresh scratch (updated first).
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KEEP = ("CLAUDE.md", ".gitignore", ".claude/settings.json")
ALLOW = ["mcp__plugin_tamheed_tamheed__*", "Read", "Glob", "Grep", "Write", "Skill",
         "ToolSearch", "Bash(git:*)", "PowerShell(git *)", "Bash(claude plugin list:*)",
         "PowerShell(claude plugin list *)"]
BUDGET = "1.6"
APPEND = ("Harness note (plan 263 rehearsal): this run allows git commands and `claude plugin list"
          " --json` only, plus the tamheed, Read, Write, Glob, Grep, Skill and ToolSearch tools."
          " Run one plain command per shell call, with no `cd`, `echo`, `&&`, `;` or pipes. The"
          " working directory is already the repository root.")


def setup(tree: Path, pkg: str, brief: str, scratch: Path, branch: str) -> None:
    ws = scratch / "ws"
    assert not ws.exists(), "a fresh scratch folder each run"
    ws.mkdir(parents=True)
    if tree.name.endswith(".tar.gz"):
        with tarfile.open(tree) as tar:
            top = tar.getmembers()[0].name.split("/")[0]
            for m in tar.getmembers():
                rel = m.name[len(top) + 1:]
                if rel and m.isfile() and (rel.startswith(pkg + "/") or rel in KEEP):
                    (ws / rel).parent.mkdir(parents=True, exist_ok=True)
                    (ws / rel).write_bytes(tar.extractfile(m).read())
    else:
        listed = subprocess.run(["git", "-C", str(tree), "ls-files", *KEEP], capture_output=True,
                                text=True).stdout.split()
        blob = subprocess.run(["git", "-C", str(tree), "archive", "HEAD", pkg, *listed],
                              capture_output=True, check=True).stdout
        tarfile.open(fileobj=io.BytesIO(blob)).extractall(ws, filter="data")
    (ws / "briefs").mkdir()
    shutil.copy(REPO / "plans" / "briefs" / brief, ws / "briefs" / brief)
    for args in (["init", "-q", "-b", branch], ["config", "core.autocrlf", "false"], ["add", "-A"],
                 ["-c", "user.name=field", "-c", "user.email=f@x.invalid", "commit", "-qm",
                  "before"]):
        subprocess.run(["git", *args], cwd=ws, check=True)
    blob = subprocess.run(["git", "-C", str(REPO), "archive", "v6.8.0", "plugins/tamheed"],
                          capture_output=True, check=True).stdout
    tarfile.open(fileobj=io.BytesIO(blob)).extractall(scratch / "bundle-680", filter="data")
    print("WS", ws)


def run(scratch: Path, label: str, bundle: str, answers: Path) -> None:
    ws = scratch / "ws"
    plugin = (scratch / "bundle-680" / "plugins" / "tamheed") if bundle == "old" else (
        REPO / "plugins" / "tamheed")
    out = scratch / "runs" / label
    out.mkdir(parents=True, exist_ok=True)
    cmd = [shutil.which("claude") or "claude", "-p", answers.read_text(encoding="utf-8"),
           "--setting-sources", "", "--plugin-dir", str(plugin), "--permission-mode", "dontAsk",
           "--allowedTools", *ALLOW, "--append-system-prompt", APPEND, "--model", "opus",
           "--max-turns", "90", "--max-budget-usd", BUDGET, "--output-format", "json"]
    env = {k: v for k, v in os.environ.items() if k != "TAMHEED_HOOK_LOG"}
    proc = subprocess.run(cmd, cwd=ws, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out / "result.json").write_bytes(proc.stdout)
    res = json.loads(proc.stdout.decode("utf-8", "replace"))
    (out / "report.md").write_text(res.get("result") or "", encoding="utf-8")
    print(f"SESSION {label} subtype={res.get('subtype')} turns={res.get('num_turns')}"
          f" cost={round(res.get('total_cost_usd') or 0, 2)}")
    print("DENIALS", json.dumps([d.get("tool_input", {}).get("command", d.get("tool_name"))
                                 for d in res.get("permission_denials") or []])[:600])
    log = subprocess.run(["git", "log", "--oneline", "--name-only", "-8"], cwd=ws,
                         capture_output=True, text=True).stdout
    print("GIT LOG\n" + log)
    print("STATUS", subprocess.run(["git", "status", "--short"], cwd=ws, capture_output=True,
                                   text=True).stdout.strip() or "clean")
    pre = scratch / "tamheed-690-pre.txt"
    print("PRE FILE", pre.read_text(encoding="utf-8")[:400] if pre.exists() else "absent")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "setup":
        setup(Path(sys.argv[2]), sys.argv[3], sys.argv[4], Path(sys.argv[5]).resolve(), sys.argv[6])
    else:
        run(Path(sys.argv[2]).resolve(), sys.argv[3], sys.argv[4], Path(sys.argv[5]))
