"""M72 (plans 165-169): the review page's added bytes per export, as shipped and with one row
per line simulated on the SHIPPED bytes (a regex split at the joins plan 166 changes). The
added side is a line set-difference - a FLOOR on `git diff`'s added side, not the diff itself.

Run:  python sim_lines.py <field repo> <rev1> <rev2> [<rev3> ...]   (consecutive page commits)
"""
import subprocess, sys, re, difflib
repo = sys.argv[1]
def page(rev):
    return subprocess.run(["git", "-C", repo, "show", f"{rev}:tamheed-package/review.html"], capture_output=True, check=True).stdout.decode("utf-8")
def split(t):
    for a, b in (("</tr><tr", "</tr>\n<tr"), ("<tbody><tr", "<tbody>\n<tr"), ("</path><path", "</path>\n<path"), ("/><path", "/>\n<path"),
                 ("</g><g", "</g>\n<g"), ("</a><path", "</a>\n<path"), ("</text><text", "</text>\n<text"), ("</p><details", "</p>\n<details"),
                 ("</details><details", "</details>\n<details"), ("</summary><div", "</summary>\n<div"), ("</tr></tbody>", "</tr>\n</tbody>")):
        t = t.replace(a, b)
    return t
def added(a, b):
    la, lb = a.split("\n"), b.split("\n")
    sa = set(la)
    add = [x for x in lb if x not in sa]      # a floor on a line diff's added side: lines of b absent from a
    return len(add), sum(len(x.encode()) for x in add), max((len(x) for x in add), default=0)
revs = sys.argv[2:]
for old, new in zip(revs, revs[1:]):
    a, b = page(old), page(new)
    print(old[:8], "->", new[:8], "as shipped: lines,bytes,max =", added(a, b), "| one row per line:", added(split(a), split(b)),
          "| page bytes", len(b.encode()), "->", len(split(b).encode()), "lines", b.count("\n"), "->", split(b).count("\n"))
