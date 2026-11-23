"""Plan 254: an audit hook for the scratch venv. Copied into the venv's site-packages, never into a tree.

It writes one JSON line for every process start, file write, delete, move, URL request and socket use,
with the nearest graphify frame, to the file named by G254_AUDIT_LOG. With G254_BLOCK_NET=1 it raises on
a connection, a send or a name lookup that is not loopback. File reads are not logged (too many).
Limit: calls made inside native code (C extensions) raise no audit events.
"""
import json
import os
import sys
import time

_LOG = os.environ.get("G254_AUDIT_LOG")
_BLOCK = os.environ.get("G254_BLOCK_NET") == "1"
_LOCAL = {"localhost", "127.0.0.1", "::1", "", None}
_WRITE_FLAGS = getattr(os, "O_WRONLY", 1) | getattr(os, "O_RDWR", 2) | getattr(os, "O_CREAT", 64) \
    | getattr(os, "O_APPEND", 8) | getattr(os, "O_TRUNC", 512)
_EVENTS = {"subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.startfile",
           "os.remove", "os.rename", "os.rmdir", "os.mkdir", "os.truncate", "os.symlink", "os.link",
           "shutil.rmtree", "shutil.copyfile", "shutil.copytree", "shutil.move", "shutil.chown",
           "socket.connect", "socket.sendto", "socket.sendmsg", "socket.getaddrinfo", "socket.gethostbyname",
           "socket.bind", "urllib.Request", "webbrowser.open", "ctypes.dlopen", "winreg.SetValue",
           "winreg.CreateKey", "open"}


def _where() -> str:
    f = sys._getframe(2)
    while f is not None:
        name = f.f_code.co_filename
        if "graphify" in name and "sitecustomize" not in name:
            return f"{os.path.basename(name)}:{f.f_lineno}:{f.f_code.co_name}"
        f = f.f_back
    return "?"


def _host(args) -> object:
    if not args:
        return None
    first = args[0]
    if isinstance(first, str):
        return first
    addr = args[1] if len(args) > 1 else None
    if isinstance(addr, tuple) and addr:
        return addr[0]
    return addr


def _hook(event: str, args) -> None:
    if event not in _EVENTS:
        return
    if event == "open":
        path, mode, flags = (list(args) + [None, None, None])[:3]
        writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (isinstance(flags, int) and flags & _WRITE_FLAGS)
        if not writing or (_LOG and str(path).startswith(_LOG)):
            return
    if event.startswith("socket.") and _BLOCK:
        host = _host(args) if event != "socket.getaddrinfo" else (args[0] if args else None)
        if isinstance(host, bytes):
            host = host.decode("ascii", "replace")
        if host not in _LOCAL and not (isinstance(host, str) and host.startswith("127.")):
            _write(event, args, blocked=True)
            raise RuntimeError(f"plan 254: network blocked ({event} {host!r})")
    _write(event, args)


def _write(event: str, args, blocked: bool = False) -> None:
    if not _LOG:
        return
    try:
        row = {"t": round(time.time(), 3), "pid": os.getpid(), "event": event, "where": _where(),
               "args": [repr(a)[:300] for a in (args if event != "subprocess.Popen" else args[:3])]}
        if blocked:
            row["blocked"] = True
        # one file per process: worker processes appending to one file interleaved their lines (measured)
        with open(f"{_LOG}.{os.getpid()}", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    except Exception:  # an audit hook must never break the program it watches
        pass


sys.addaudithook(_hook)
