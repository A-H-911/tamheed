"""The brief's own git commands, run in a scratch git repository that holds a field package.

Usage: python -I gitdrill.py <v640 bundle> <v650 bundle> <scratch repo root> <package dir name>
The scratch repository is a clone or a fresh repository made from a copy. Prints file names,
commit counts, ids and counts. No text of a row.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

old, new, repo = (Path(a) for a in sys.argv[1:4])
name = sys.argv[4]
here = Path(__file__).parent
pkg = repo / name
KEYS = ("gates", "blocking_fail", "counts", "edges", "gate_ready", "rules")


def git(*args: str, check: bool = True) -> str:
    done = subprocess.run(["git", "-c", "user.name=assurance", "-c", "user.email=assurance@example.invalid",
                           "-c", "core.autocrlf=false", *args], cwd=repo, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    if check and done.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {done.stderr[-300:]}")
    return (done.stdout + (done.stderr if done.returncode else "")).strip()


def tree() -> dict:
    return {str(p.relative_to(repo)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(pkg.rglob("*")) if p.is_file() and not p.name.endswith(".lock")}


def run(script: str, bundle: Path, *more: str) -> str:
    done = subprocess.run([sys.executable, "-I", "-X", "utf8", str(here / script), str(bundle),
                           str(repo), name, *more], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    return (done.stdout + done.stderr).strip()


def probe(bundle: Path) -> dict:
    return json.loads(run("worker.py", bundle, "probe").splitlines()[-1])


def status() -> list:
    return [line for line in git("status", "--short", "--", name).splitlines() if line.strip()]


def same_as_before(label: str) -> None:
    back = probe(old)
    print(f"{label}: the folder equals PRE byte for byte: {tree() == base_tree} | 6.4.0 opens it:"
          f" {back.get('open_ok')} | same results: {all(back.get(k) == baseline.get(k) for k in KEYS)}"
          f" | git status lines: {len(status())}")


print("clean at the start:", status() == [])
PRE = git("rev-parse", "HEAD")
base_tree = tree()
baseline = probe(old)
print("6.4.0 baseline: opens", baseline.get("open_ok"), "| journal rows",
      (baseline.get("counts") or {}).get("progress_entries"), "| idle open left git status clean:",
      status() == [])

print("\n## The confirm, then route A before the commit")
confirm = json.loads(run("worker.py", new, "confirm").splitlines()[-1])
print("confirm:", confirm.get("ok"), "| git status:", status())
after = probe(new)
print("journal rows after:", (after.get("counts") or {}).get("progress_entries"),
      "| git status after an open and a close with 6.5.0:", status())
print(git("checkout", "--", f"{name}/data"))
same_as_before("after `git checkout -- <package>/data`")

print("\n## The migration commit, the review page, later work")
json.loads(run("worker.py", new, "confirm").splitlines()[-1])
moved = [line.split()[-1] for line in status()]
git("add", "--", *moved)
git("commit", "-q", "-m", "the migration")
text = run("exercise.py", new)
print("exercise:", [line for line in text.splitlines() if line.startswith(("FAIL", "exercise:"))])
print("git status kinds after the upgrade's steps and later writes:",
      sorted({line[:2].strip() + " " + "/".join(line.split()[-1].split("/")[1:2]) for line in status()}))
git("add", "-A", "--", name)
git("commit", "-q", "-m", "later work under 6.5.0")
count = int(git("rev-list", "--count", f"{PRE}..HEAD"))
print("commits after PRE:", count)
TOP = git("rev-parse", "HEAD")

print("\n## Route A after the commits, way 1: git revert of every commit after PRE")
out = git("revert", "--no-edit", f"{PRE}..HEAD", check=False)
print("revert said:", out.splitlines()[-1][:160] if out else "(nothing)")
same_as_before("after the revert")

print("\n## Route A, way 2: one restore of the folder as it was")
git("reset", "-q", "--hard", TOP)
git("restore", f"--source={PRE}", "--staged", "--worktree", "--", name)
print("git status kinds after the restore:",
      sorted({line[:2] for line in git("status", "--short", "--", name).splitlines()}))
left = git("status", "--short", "--", name)
same_as_before("after `git restore --source=PRE --staged --worktree -- <package>`")
git("commit", "-q", "-m", "back to the package as it was at PRE")
print("after the commit, git diff PRE -- <package> is empty:", git("diff", "--stat", PRE, "--", name) == "")

print("\n## Route A, way 3 (as the brief first said): git checkout PRE -- <package>")
git("reset", "-q", "--hard", TOP)
git("checkout", PRE, "--", name)
extra = sorted(set(tree()) - set(base_tree))
print("files that PRE does not have and that stay in the folder:", len(extra),
      sorted({"/".join(e.split("/")[1:2]) for e in extra}))
print("git status names them as untracked:", any(line.startswith("??") for line in status()),
      "| kinds:", sorted({line[:2] for line in git('status', '--short', '--', name).splitlines()}))
git("reset", "-q", "--hard", TOP)
