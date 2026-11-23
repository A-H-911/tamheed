"""Plan 254 (critic X1): before the hash, a dry run of every non-Graphify tool on 3 real commits, and the
Graphify adapter on a hand-made fixture. No map of Tamheed is built.

    python -I dryrun_254.py <study>
"""
import io
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import places_254 as P  # noqa: E402
import replay_254 as R  # noqa: E402
from lsp_254 import Pyright  # noqa: E402

study = Path(sys.argv[1]).resolve()
repo = study / "hist"
tree = study / "dry" / "tree"

# 1. the adapter on a fixture: absolute, backslashed and relative paths; with and without a line; an outside path
fixture = "\n".join([
    "Affected nodes for gate_run()", "Relations: calls", "Depth: 2",
    f"- package_open() [calls] {tree.resolve()}\\plugins\\tamheed\\server\\tamheed_server.py:L1612",
    "- test_x() [calls] tests/test_mcp_contract.py:L27",
    "- store.py [imports_from] plugins/tamheed/db/store.py",
    "- elsewhere() [calls] Z:/other/repo/x.py:L3",
    "- nothing [calls] -",
    "- [NEEDS-CLARIFICATION] marker note [references] plugins/tamheed/db/store.py:L5",
])
rev = P.sha(str(repo), "451ff94")
got = R.parse_affected(fixture, tree, repo, rev)
assert got == ["plugins/tamheed/server/tamheed_server.py::package_open", "tests/test_mcp_contract.py::V4EngineTest"
               if P.spans(str(repo), rev, "tests/test_mcp_contract.py") else "tests/test_mcp_contract.py",
               "plugins/tamheed/db/store.py"] or len(got) == 3, got
assert got[0] == "plugins/tamheed/server/tamheed_server.py::package_open" and got[2] == "plugins/tamheed/db/store.py", got
print("adapter fixture:", got)
assert R.round_robin([["a", "b"], ["c"], ["d", "e", "f"]]) == ["a", "c", "d", "b", "e", "f"]
assert R.pipeline(["x.py", "CHANGELOG.md", "y.py", "x.py", "seed.py::f"], lambda p: p.startswith("seed.py")) == ["x.py", "y.py"]

# 2. the four other tools on the 3 newest eligible commits, pyright included
hist = P.history(repo, "451ff94")
idx = {c: i for i, (c, _) in enumerate(hist)}
eligible = [c for c, t in hist if 2 <= len(t) <= 20]
print("history", len(hist), "eligible", len(eligible))
co = P.CoChange(repo, hist)
for c in eligible[-3:]:
    parent = P.sha(str(repo), f"{c}^")
    shutil.rmtree(tree, ignore_errors=True)
    tree.mkdir(parents=True)
    tarfile.open(fileobj=io.BytesIO(subprocess.run([*P.GIT, "-C", str(repo), "archive", parent], capture_output=True,
                                                   check=True).stdout)).extractall(tree, filter="data")
    lsp = Pyright(tree)
    warm = lsp.warm()
    touched = hist[idx[c]][1]
    parent_places = set(P.all_places(str(repo), parent))
    print(f"== {c[:8]} {P.git(repo, 'show', '-s', '--format=%s', c).strip()[:70]} | seeds {len(touched)} | pyright warm {warm}")
    for seed, sp in list(touched.items())[:4]:
        truth = set().union(*(v for k, v in touched.items() if k != seed)) & parent_places
        names = P.seed_names(repo, c, seed, sp)
        defined = P.seed_names(repo, c, seed, sp, defined_only_at=parent) if seed.endswith(".py") else []

        def drop(p, s=seed):
            return p.split("::", 1)[0] == s
        res = {"search": R.pipeline(P.search(repo, parent, names, drop), drop),
               "pyright": R.pipeline(R.round_robin(R.pyright_lists(lsp, seed, defined, repo, parent)[0]), drop),
               "cochange": R.pipeline(co.rank(parent, sp, drop), drop),
               "most_changed": R.pipeline(P.most_changed(repo, hist, parent, drop), drop)}
        print(f"   {seed[:60]:60s} truth {len(truth):2d} names {len(names):2d} defined {len(defined)} | "
              + " ".join(f"{k} {sum(1 for t in truth if t in v)}/{len(v)}" for k, v in res.items()))
    lsp.close()
shutil.rmtree(study / "dry", ignore_errors=True)
print("dry run done")
