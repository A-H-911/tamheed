"""Plan 212: the guide's hand maps cite server line numbers; the engine patch inserted lines, so
every citation is re-aimed by a line map from HEAD's server text to the working copy (difflib equal
blocks), then the three new CLAUDE.md writes are added. Prints the map's coverage."""
import difflib
import re
import subprocess
from pathlib import Path

R = Path(r"C:\Users\ahammo\Repos\tamheed")
SRV = "plugins/tamheed/server/tamheed_server.py"
old = subprocess.run(["git", "show", f"HEAD:{SRV}"], cwd=R, capture_output=True, text=True,
                     encoding="utf-8").stdout.splitlines()
new = (R / SRV).read_text(encoding="utf-8").splitlines()
line_map: dict[int, int] = {}
sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        for k in range(i2 - i1):
            line_map[i1 + k + 1] = j1 + k + 1

D = R / "docs/guide/diagrams.py"
d = D.read_text(encoding="utf-8")
start = d.index("TOOL_EFFECTS = {")
end = d.index("_SEVERITY_KEY = {")
region = d[start:end]
unmapped = []


def remap(m):
    n = int(m.group(2))
    if n not in line_map:
        unmapped.append(n)
        return m.group(0)
    return f"{m.group(1)}{line_map[n]}{m.group(3)}"


# tuple citations ("item", 1234) and ("python", 1234); VACUOUS values "G-X": 1234; comment refs L1234
region = re.sub(r'(\(\s*"[^"]+",\s*)(\d{3,4})(\s*\))', remap, region)
region = re.sub(r'("G-[A-Z-]+":\s*)(\d{4})(\b)', remap, region)
region = re.sub(r"(\bL)(\d{4})(\b)", remap, region)
d = d[:start] + region + d[end:]

# the three new writes: the wiring call lines in the working copy
calls = {ln for ln, text in enumerate(new, 1) if "_wire_project(" in text and "def " not in text}
create_ln = min(ln for ln in calls if ln < 1200)
open_ln = min(ln for ln in calls if 1200 < ln < 2000)
adopt_ln = max(calls)
print("wiring calls:", sorted(calls), "->", create_ln, open_ln, adopt_ln)


def add_write(tool: str, ln: int):
    global d
    pat = re.compile(rf'("{tool}": \{{.*?"writes": \[)(.*?)(\]\}})', re.S)
    m = pat.search(d)
    assert m, tool
    assert "CLAUDE.md" not in m.group(2), tool
    d = d[:m.start()] + m.group(1) + m.group(2) + f', ("CLAUDE.md", {ln})' + m.group(3) + d[m.end():]


import sys  # noqa: E402

if "--remap-only" not in sys.argv:          # the first run adds the writes; later runs only re-aim
    add_write("package_create", create_ln)
    add_write("package_open", open_ln)
    add_write("package_adopt", adopt_ln)
D.write_text(d, encoding="utf-8", newline="\n")

# the guide test pins four server lines by number: re-aim them by the same map
T = R / "tests/test_user_guide.py"
tt = T.read_text(encoding="utf-8")
tt = re.sub(r"(lines\.append\()(\d{4})(\))", remap, tt)
tt = re.sub(r"(src\[)(\d{4})(\])", lambda m: (f"{m.group(1)}{line_map[int(m.group(2)) + 1] - 1}{m.group(3)}"
                                              if int(m.group(2)) + 1 in line_map else m.group(0)), tt)
T.write_text(tt, encoding="utf-8", newline="\n")
print("unmapped citations:", sorted(set(unmapped)))
print("shift applied")
