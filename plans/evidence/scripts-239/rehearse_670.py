"""Plan 247 (from scripts-238/rehearse_brief.py): rehearse a field brief with a headless agent, with a chosen plugin bundle.

    python rehearse_brief.py setup <field repo> <package dir> <brief> <scratch>
    python rehearse_brief.py run <scratch> <label> <bundle: old|new> <prompt file>

`setup` builds a scratch repository from the field's committed HEAD (`git archive`: the package,
CLAUDE.md, .gitignore, .claude/settings.json), with autocrlf off and the brief in briefs/.
`run` starts one `claude -p` session (a new process, as a restart is), with the 6.6.0 bundle from
the tag or the working-tree 6.7.0 bundle. Arguments go as a list: no shell quoting.
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
ALLOW = ["mcp__plugin_tamheed_tamheed__*", "Read", "Glob", "Grep", "Edit", "Write", "Skill",
         "ToolSearch", "Bash(git:*)", "PowerShell(git *)", "Bash(gh:*)", "Bash(curl:*)",
         "Bash(sha256sum:*)", "Bash(shasum:*)"]


def setup(field: Path, pkg: str, brief: str, scratch: Path) -> None:
    ws = scratch / "ws"
    assert not ws.exists(), "a fresh scratch folder each run"
    ws.mkdir(parents=True)
    listed = subprocess.run(["git", "-C", str(field), "ls-files", "CLAUDE.md", ".gitignore",
                             ".claude/settings.json"], capture_output=True, text=True).stdout.split()
    blob = subprocess.run(["git", "-C", str(field), "archive", "HEAD", pkg, *listed],
                          capture_output=True).stdout
    tarfile.open(fileobj=io.BytesIO(blob)).extractall(ws)
    (ws / "briefs").mkdir()
    shutil.copy(REPO / "plans" / "briefs" / brief, ws / "briefs" / brief)
    for args in (["init", "-q"], ["config", "core.autocrlf", "false"], ["add", "-A"],
                 ["-c", "user.name=field", "-c", "user.email=f@x.invalid", "commit", "-qm", "before"]):
        subprocess.run(["git", *args], cwd=ws, check=True)
    b651 = scratch / "bundle-660"
    tarfile.open(fileobj=io.BytesIO(subprocess.run(
        ["git", "-C", str(REPO), "archive", "v6.6.0", "plugins/tamheed"], capture_output=True).stdout)
    ).extractall(b651)
    print("WS", ws, "| listed:", listed)


def run(scratch: Path, label: str, bundle: str, prompt_file: Path) -> None:
    ws = scratch / "ws"
    plugin = (scratch / "bundle-660" / "plugins" / "tamheed") if bundle == "old" else (
        REPO / "plugins" / "tamheed")
    out = scratch / "runs" / label
    out.mkdir(parents=True, exist_ok=True)
    prompt = prompt_file.read_text(encoding="utf-8")
    # REH_WIDE=1: the fetch smoke, whose one command has a redirect that prefix rules do not match
    allow = ALLOW + (["Bash"] if os.environ.get("REH_WIDE") else [])
    cmd = [shutil.which("claude") or "claude", "-p", prompt, "--setting-sources", "",
           "--plugin-dir", str(plugin), "--permission-mode", "dontAsk", "--allowedTools", *allow,
           "--model", "opus", "--max-turns", "90", "--max-budget-usd", "8", "--output-format", "json"]
    env = dict(os.environ)
    env.pop("TAMHEED_HOOK_LOG", None)
    proc = subprocess.run(cmd, cwd=ws, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out / "result.json").write_bytes(proc.stdout)
    res = json.loads(proc.stdout.decode("utf-8", "replace"))
    print(f"SESSION {res.get('session_id')} turns={res.get('num_turns')} cost={res.get('total_cost_usd')}")
    print("DENIALS", json.dumps([d.get("tool_input", {}).get("command", d.get("tool_name"))
                                 for d in res.get("permission_denials") or []])[:500])
    print("REPORT:\n" + (res.get("result") or "")[:5000])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "setup":
        setup(Path(sys.argv[2]), sys.argv[3], sys.argv[4], Path(sys.argv[5]).resolve())
    else:
        run(Path(sys.argv[2]).resolve(), sys.argv[3], sys.argv[4], Path(sys.argv[5]))
