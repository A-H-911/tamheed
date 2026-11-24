"""Plan 255: the numbers behind the missed-places rule, re-run at pinned commits. Standard library only.

    python -I measure_255.py                  re-runs the review's numbers, writes results/measure.json,
                                              and exits 1 if any differs from what plan 255 states
    python -I measure_255.py --tally T0 END OUT
                                              the frozen tally (step 6): the picked fix commits after T0 up to
                                              END, one entry file each in OUT, and the no-change range

Run from the repository root. Read-only on git.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RATED_UP_TO = "451ff94"      # plan 254's picker ran up to this commit
REVIEW_HEAD = "ec5686a"      # HEAD during the plan 255 review
SINCE = "2026-07-01"
BASELINE = (16, 48)          # misses among picked fix commits (plan 254 raters)
EXPECTED = {"picked": 48, "unrated": 18, "firing": {"20/5": 44, "30/3": 42, "40/2": 40},
            "gaps_commits": {"01": 1, "03": 135, "21": 11, "24": 1, "25": 36, "26": 34, "39": 3, "48": 13}}

FIX = re.compile(r"\bfix(es|ed)?\b", re.I)
CORR = re.compile(r"\b(correct(s|ed|ion)?|stale|missed|follow-up|forgot|repair|wrong|drift|regress\w*|align(s|ed)?)\b", re.I)
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")


def git(*args: str, inp: str | None = None) -> str:
    return subprocess.run(["git", "-C", str(REPO), "-c", "core.quotePath=false", *args], input=inp,
                          capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def kind(p: str) -> str:
    """The file kinds of plan 254's picker (fixes_254.py)."""
    if p.startswith("plans/") or p == "CHANGELOG.md":
        return "record"
    if p.startswith(("tests/", "evals/", "lab/", "generated-samples/")):
        return "test"
    if p.startswith("docs/guide/figures") or p == "index.html":
        return "generated"
    return "code" if p.rsplit(".", 1)[-1] in ("py", "js", "mjs", "css", "sql", "yaml") else "text"


def code_text_files(sha: str) -> list:
    return [p for p in git("show", "--name-only", "--format=", sha).splitlines() if p and kind(p) in ("code", "text")]


def picked(rev_range: list) -> list:
    """Plan 254's picker: the word fix/fixes/fixed in the subject, 1 to 6 code or text files."""
    out = []
    for line in git("log", *rev_range, "--format=%H%x09%s").splitlines():
        sha, subject = line.split("\t", 1)
        if FIX.search(subject) and 1 <= len(code_text_files(sha)) <= 6:
            out.append((sha, subject))
    return out


def unrated() -> list:
    """Commits since July at REVIEW_HEAD that the 254 picker did not rate, named for a fix or a correction."""
    rated = {s for s, _ in picked([f"--since={SINCE}", RATED_UP_TO])}
    out = []
    for line in git("log", "--no-merges", f"--since={SINCE}", "--format=%H%x09%s", REVIEW_HEAD).splitlines():
        sha, subject = line.split("\t", 1)
        if sha in rated or subject.startswith("release"):
            continue
        if (FIX.search(subject) or CORR.search(subject)) and 1 <= len(code_text_files(sha)) <= 12:
            out.append(sha)
    return out


def kept(p: str) -> bool:
    return not (p.startswith(("plans/", "docs/guide/figures/", "generated-samples/", "evals/sample-results/", "tests/"))
                or p in ("CHANGELOG.md", "index.html"))


def old_text_fires(sha: str, minlen: int, maxcopies: int) -> bool:
    """The old-text signal: a removed line (at least minlen characters, 2 or more identifiers, not re-added) that
    still has 1 to maxcopies copies in kept files of the tree at the commit."""
    removed, added, cur = set(), set(), None
    for line in git("show", "--format=", "-U0", "--no-renames", sha).split("\n"):
        if line.startswith("diff "):
            cur = None
        elif line.startswith("+++ "):
            cur = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("--- "):
            continue
        elif cur is not None and kept(cur) and line.startswith("-"):
            removed.add(line[1:].strip())
        elif cur is not None and line.startswith("+"):
            added.add(line[1:].strip())
    pats = [x for x in removed if len(x) >= minlen and len(IDENT.findall(x)) >= 2 and x not in added]
    if not pats:
        return False
    hits: dict = {}
    for row in git("grep", "-F", "-n", "-f", "-", sha, "--", inp="\n".join(pats) + "\n").splitlines():
        parts = row.split(":", 3)
        if len(parts) == 4 and kept(parts[1]):
            for p in pats:
                if p in parts[3]:
                    hits[p] = hits.get(p, 0) + 1
    return any(1 <= n <= maxcopies for n in hits.values())


def gaps() -> dict:
    rows = json.loads((REPO / "plans/evidence/scripts-254/rated_missed_places.json").read_text(encoding="utf-8"))
    out = {}
    for r in rows:
        if r["origin_agree"] and r["origin_F1"] != "none":
            o, f = r["origin_F1"], r["commit"]
            out[r["fix"]] = {"commits": int(git("rev-list", "--count", f"{o}..{f}").strip()),
                             "origin_date": git("show", "-s", "--format=%cs", o).strip(),
                             "fix_date": git("show", "-s", "--format=%cs", f).strip()}
    return out


def binomial_range(n: int, p: float) -> tuple:
    """The central 95% range of a binomial count: the smallest k with CDF >= 0.025 and with CDF >= 0.975."""
    cdf, lo, hi = 0.0, None, None
    for k in range(n + 1):
        cdf += math.comb(n, k) * p ** k * (1 - p) ** (n - k)
        if lo is None and cdf >= 0.025:
            lo = k
        if hi is None and cdf >= 0.975:
            hi = k
    return lo, hi


def measure() -> int:
    shas = git("log", "--no-merges", "-100", "--format=%H", RATED_UP_TO).split()
    got = {"picked": len(picked([f"--since={SINCE}", RATED_UP_TO])), "unrated": len(unrated()),
           "firing": {f"{a}/{b}": sum(old_text_fires(s, a, b) for s in shas) for a, b in ((20, 5), (30, 3), (40, 2))},
           "gaps": gaps()}
    got["gaps_commits"] = {k: v["commits"] for k, v in got["gaps"].items()}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "measure.json").write_text(json.dumps(got, indent=1, sort_keys=True) + "\n", encoding="utf-8",
                                                    newline="\n")
    bad = [k for k in EXPECTED if got[k] != EXPECTED[k]]
    print(json.dumps({k: got[k] for k in EXPECTED}, sort_keys=True))
    print("MISMATCH: " + ", ".join(bad) if bad else "all numbers match plan 255")
    return 1 if bad else 0


def tally(t0: str, end: str, out: Path) -> int:
    """Step 6, frozen in plan 255: one entry per picked fix commit after T0, and the reading rule."""
    rows = picked([f"{t0}..{end}"])
    out.mkdir(parents=True, exist_ok=True)
    for n, (sha, _subject) in enumerate(reversed(rows), 1):
        text = [f"##### FIX {n:02d} of {len(rows)} | commit {sha[:10]} | {git('show', '-s', '--format=%cs', sha).strip()}",
                git("show", "-s", "--format=%B", sha).strip()]
        blame: dict = {}
        for p in code_text_files(sha):
            diff = git("show", "--format=", "-U4", sha, "--", p)
            lines = [x[:1800] for x in diff.splitlines()]
            text.append("\n".join(lines[:420]) + (f"\n[... {len(lines) - 420} more rows]" if len(lines) > 420 else ""))
            for start, count in re.findall(r"^@@ -(\d+)(?:,(\d+))? ", diff, re.M)[:8]:
                if int(count or 1):
                    for b in git("blame", "-s", "-L", f"{start},+{int(count or 1)}", f"{sha}^", "--", p).splitlines():
                        key = b.split()[0].lstrip("^")[:8]
                        blame[key] = blame.get(key, 0) + 1
        top = sorted(blame.items(), key=lambda kv: -kv[1])[:6]
        text.append("--- who wrote the changed lines: " + "; ".join(
            f"{k} x{v} ({git('show', '-s', '--format=%s', k).strip()[:90]})" for k, v in top))
        text.append(f"--- suggested origin (a suggestion only): {top[0][0] if top else 'none'}")
        text.append("--- operator's mark: missed place yes / no")
        (out / f"{n:02d}-{sha[:10]}.txt").write_text("\n".join(text) + "\n", encoding="utf-8", newline="\n")
    n = len(rows)
    lo, hi = binomial_range(n, BASELINE[0] / BASELINE[1])
    print(f"{n} picked fix commits after {t0}; entries in {out}")
    print("reading: too few to read (fewer than 10)" if n < 10 else
          f"reading: {lo} to {hi} misses = no visible change; below {lo} = lower, not causal; above {hi} = higher")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) > 1 and sys.argv[1] == "--tally":
        sys.exit(tally(sys.argv[2], sys.argv[3], Path(sys.argv[4])))
    sys.exit(measure())
