"""Plan 254, step 5.1: dump the small fix commits for the two raters, who have no shell.

    python -I fixes_254.py <study folder> <tamheed repo>

A fix commit: since 2026-07-01, the subject has the word fix/fixes/fixed, and it touches 1 to 6 code or
text files (tests, fixtures, records and generated files do not count). Each entry holds the message,
the diff of those files, and for every removed or replaced line the commit that had written it.
"""
import re
import subprocess
import sys
from pathlib import Path

study, repo = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def kind(p: str) -> str:
    if p.startswith("plans/") or p == "CHANGELOG.md":
        return "record"
    if p.startswith(("tests/", "evals/", "lab/", "generated-samples/")):
        return "test"
    if p.startswith("docs/guide/figures") or p == "index.html":
        return "generated"
    return "code" if p.rsplit(".", 1)[-1] in ("py", "js", "mjs", "css", "sql", "yaml") else "text"


picked = []
for line in git("log", "--since=2026-07-01", "--format=%H%x09%s", "451ff94").splitlines():
    sha, subject = line.split("\t", 1)
    if not re.search(r"\bfix(es|ed)?\b", subject, re.I):
        continue
    files = [p for p in git("show", "--name-only", "--format=", sha).splitlines() if p]
    keep = [p for p in files if kind(p) in ("code", "text")]
    if 1 <= len(keep) <= 6:
        picked.append((sha, subject, files, keep))
out = study / "bundles" / "F"
out.mkdir(parents=True, exist_ok=True)
for old in out.glob("*.txt"):
    old.unlink()
entries = []
for n, (sha, subject, files, keep) in enumerate(picked, 1):
    text = [f"##### FIX {n:02d} of {len(picked)} | commit {sha[:10]} | {git('show', '-s', '--format=%ad', '--date=short', sha).strip()} #####",
            git("show", "-s", "--format=%B", sha).strip(), "--- all files of the commit: " + ", ".join(files)]
    for p in keep:
        diff = git("show", "--format=", "-U4", sha, "--", p)
        rows = [x[:1800] for x in diff.splitlines()]
        text.append("\n".join(rows[:420]) + (f"\n[... {len(rows) - 420} more diff rows of {p} not shown]" if len(rows) > 420 else ""))
        spans = re.findall(r"^@@ -(\d+)(?:,(\d+))? ", diff, re.M)
        blame = {}
        for start, count in spans[:8]:
            c = int(count or 1)
            if c:
                for b in git("blame", "-s", "-L", f"{start},+{c}", f"{sha}^", "--", p).splitlines():
                    blame[b.split()[0].lstrip("^")[:8]] = blame.get(b.split()[0].lstrip("^")[:8], 0) + 1
        names = [f"{k} x{v} ({git('show', '-s', '--format=%s', k).strip()[:90]})" for k, v in sorted(blame.items(), key=lambda kv: -kv[1])[:6]]
        text.append(f"--- who had written the surrounding lines of {p}: " + "; ".join(names))
    entries.append("\n".join(text) + "\n\n")
bundle, size, seq = [], 0, 0
for e in entries + [None]:
    if e is None or (bundle and size + len(e) > 42000):
        seq += 1
        (out / f"{seq:03d}.txt").write_text("".join(bundle), encoding="utf-8", newline="\n")
        bundle, size = [], 0
    if e is not None:
        while len(e) > 42000:
            seq += 1
            (out / f"{seq:03d}.txt").write_text("".join(bundle) + e[:42000], encoding="utf-8", newline="\n")
            bundle, size, e = [], 0, "[continued]\n" + e[42000:]
        bundle.append(e)
        size += len(e)
print("fix commits", len(picked), "bundles", seq, "chars", sum(len(e) for e in entries))
