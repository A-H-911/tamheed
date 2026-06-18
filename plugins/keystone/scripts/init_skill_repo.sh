#!/usr/bin/env bash
# Thin POSIX wrapper around init_skill_repo.py.
# All logic lives in the Python script; this only locates python3 and execs it,
# forwarding every argument unchanged.
set -euo pipefail

# Resolve the directory this script lives in (handles symlinks).
SOURCE="${BASH_SOURCE[0]:-$0}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ "$SOURCE" != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)"

# Ensure python3 is available.
if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required but was not found on PATH." >&2
  echo "       Install Python 3.9+ (https://www.python.org/downloads/) and retry." >&2
  exit 2
fi

exec python3 "$SCRIPT_DIR/init_skill_repo.py" "$@"
