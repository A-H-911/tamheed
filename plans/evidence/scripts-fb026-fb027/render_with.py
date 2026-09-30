"""Plan 166's byte check, one half: render a package's review page with ONE bundle's engine
(the 5.7.0 tag's, or the working tree's) to a path outside the package. Run once per bundle
in its own process; `bytecheck.py` then compares the two pages.

Run:  python render_with.py <bundle dir (…/plugins/tamheed)> <package root> <package name> <out.html>
Every run: `env -u TAMHEED_HOOK_LOG`; the copy is a `git archive` of the field repo.
"""
import sys
from pathlib import Path

bundle, root, name, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
sys.path.insert(0, str(bundle / "server"))
sys.path.insert(0, str(bundle / "db"))
import tamheed_server as srv  # noqa: E402

srv.PACKAGE_ROOT = root
opened = srv.package_open(name)
assert opened["ok"], opened
try:
    res = srv.export_html(out)
    assert res["ok"], res
    print(srv.__version__ if hasattr(srv, "__version__") else srv.server_info()["version"],
          res["path"], Path(res["path"]).stat().st_size)
finally:
    srv.package_close()
